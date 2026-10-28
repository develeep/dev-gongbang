#!/usr/bin/env python3
"""Aggregate grading.json / timing.json of one iteration into benchmark.json and benchmark.md.

Usage:
  python3 scripts/aggregate.py <workspace>/iteration-N [--primary with_skill]

Expected layout (a run dir holds grading.json and optionally timing.json):
  iteration-N/<case>/<config>/grading.json
  iteration-N/<case>/<config>/run-1/grading.json   (several runs of one config)

The primary config (default: the one whose name starts with "with_skill") is compared
against every other config. Prints a short JSON summary to stdout.
Standard library only.
"""

import argparse
import json
import statistics
import sys
from pathlib import Path


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"warning: cannot read {path}: {e}", file=sys.stderr)
        return None


def run_dirs(config_dir):
    runs = sorted(p for p in config_dir.iterdir() if p.is_dir() and p.name.startswith("run-"))
    return runs or [config_dir]


def stats(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return {"mean": None, "stddev": None, "n": 0}
    return {"mean": round(statistics.mean(vals), 4),
            "stddev": round(statistics.stdev(vals), 4) if len(vals) > 1 else 0.0,
            "n": len(vals)}


def expectations(grading):
    return grading.get("expectations") or grading.get("assertion_results") or []


def main():
    ap = argparse.ArgumentParser(description="Aggregate eval results of one iteration.")
    ap.add_argument("iteration_dir")
    ap.add_argument("--primary", help="config treated as 'with skill' (default: first config starting with with_skill)")
    args = ap.parse_args()

    it = Path(args.iteration_dir).expanduser()
    if not it.is_dir():
        print(f"Error: {it} is not a directory", file=sys.stderr)
        return 2

    runs = []  # one row per run
    case_dirs = [p for p in it.iterdir() if p.is_dir() and (any(p.glob("*/grading.json")) or any(p.glob("*/run-*/grading.json")))]
    for case in sorted(case_dirs):
        for config in sorted(c for c in case.iterdir() if c.is_dir()):
            for rd in run_dirs(config):
                g = rd / "grading.json"
                if not g.exists():
                    continue
                grading = load(g) or {}
                exps = expectations(grading)
                passed = sum(1 for e in exps if e.get("passed"))
                timing = load(rd / "timing.json") if (rd / "timing.json").exists() else {}
                timing = timing or {}
                secs = timing.get("total_duration_seconds")
                if secs is None and timing.get("duration_ms") is not None:
                    secs = timing["duration_ms"] / 1000
                runs.append({
                    "case": case.name, "config": config.name, "run": rd.name if rd != config else "run-1",
                    "passed": passed, "total": len(exps),
                    "pass_rate": passed / len(exps) if exps else None,
                    "seconds": secs, "tokens": timing.get("total_tokens"),
                    "expectations": [{"text": e.get("text", ""), "passed": bool(e.get("passed"))} for e in exps],
                })

    if not runs:
        print(f"Error: no grading.json found under {it}. Grade the runs first.", file=sys.stderr)
        return 1

    configs = sorted({r["config"] for r in runs})
    primary = args.primary or next((c for c in configs if c.startswith("with_skill")), configs[0])
    configs = [primary] + [c for c in configs if c != primary]

    summary = {}
    for c in configs:
        rs = [r for r in runs if r["config"] == c]
        summary[c] = {"pass_rate": stats([r["pass_rate"] for r in rs]),
                      "time_seconds": stats([r["seconds"] for r in rs]),
                      "tokens": stats([r["tokens"] for r in rs]),
                      "runs": len(rs)}

    deltas = {}
    for c in configs[1:]:
        d = {}
        for k in ("pass_rate", "time_seconds", "tokens"):
            a, b = summary[primary][k]["mean"], summary[c][k]["mean"]
            d[k] = round(a - b, 4) if a is not None and b is not None else None
        deltas[f"{primary} - {c}"] = d

    # Assertion discrimination: per (case, assertion text), pass rate per config.
    disc = {}
    for r in runs:
        for e in r["expectations"]:
            key = (r["case"], e["text"])
            disc.setdefault(key, {}).setdefault(r["config"], []).append(e["passed"])
    discrimination = []
    for (case, text), per in sorted(disc.items()):
        rates = {c: sum(v) / len(v) for c, v in per.items()}
        p = rates.get(primary)
        others = [rates[c] for c in rates if c != primary]
        if p is None or not others:
            verdict = "no-baseline"
        elif p >= 0.5 and all(o >= 0.5 for o in others):
            verdict = "always-pass (not discriminating)"
        elif p < 0.5 and all(o < 0.5 for o in others):
            verdict = "always-fail (check assertion/case)"
        elif p >= 0.5:
            verdict = "skill-only pass (skill adds value)"
        else:
            verdict = "baseline-only pass (skill hurts?)"
        flaky = any(0 < v < 1 for v in rates.values())
        discrimination.append({"case": case, "assertion": text, "rates": rates,
                               "verdict": verdict, "flaky": flaky})

    per_case = {}
    for r in runs:
        per_case.setdefault(r["case"], {}).setdefault(r["config"], []).append(r)

    bench = {"iteration": it.name, "primary": primary, "configs": configs,
             "run_summary": summary, "delta": deltas, "runs": runs,
             "discrimination": discrimination}
    (it / "benchmark.json").write_text(json.dumps(bench, ensure_ascii=False, indent=2), encoding="utf-8")

    def fmt(s, pct=False, digits=1):
        if s["mean"] is None:
            return "-"
        m, sd = s["mean"], s["stddev"]
        if pct:
            return f"{m*100:.0f}% ± {sd*100:.0f}"
        return f"{m:,.{digits}f} ± {sd:,.{digits}f}"

    md = [f"# Benchmark: {it.name}", "", "## 설정별 요약", "",
          "| 설정 | 실행 수 | 통과율 | 시간(초) | 토큰 |", "|---|---|---|---|---|"]
    for c in configs:
        s = summary[c]
        md.append(f"| {c} | {s['runs']} | {fmt(s['pass_rate'], True)} | {fmt(s['time_seconds'])} | {fmt(s['tokens'], digits=0)} |")
    if deltas:
        md += ["", "## 차이", "", "| 비교 | 통과율 | 시간(초) | 토큰 |", "|---|---|---|---|"]
        for k, d in deltas.items():
            pr = f"{d['pass_rate']*100:+.0f}%p" if d["pass_rate"] is not None else "-"
            ts = f"{d['time_seconds']:+.1f}" if d["time_seconds"] is not None else "-"
            tk = f"{d['tokens']:+,.0f}" if d["tokens"] is not None else "-"
            md.append(f"| {k} | {pr} | {ts} | {tk} |")
    md += ["", "## 케이스별 통과", "", "| 케이스 | " + " | ".join(configs) + " |", "|---|" + "---|" * len(configs)]
    for case, per in sorted(per_case.items()):
        cells = []
        for c in configs:
            rs = per.get(c, [])
            cells.append(", ".join(f"{r['passed']}/{r['total']}" for r in rs) or "-")
        md.append(f"| {case} | " + " | ".join(cells) + " |")
    if len(configs) > 1:
        md += ["", "## assertion 판별력", "", "| 케이스 | assertion | 판정 | 흔들림 |", "|---|---|---|---|"]
        for d in discrimination:
            md.append(f"| {d['case']} | {d['assertion'][:80]} | {d['verdict']} | {'예' if d['flaky'] else ''} |")
    (it / "benchmark.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps({"benchmark_json": str(it / "benchmark.json"), "benchmark_md": str(it / "benchmark.md"),
                      "pass_rate": {c: summary[c]["pass_rate"]["mean"] for c in configs},
                      "delta": deltas}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
