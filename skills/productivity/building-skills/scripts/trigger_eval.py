#!/usr/bin/env python3
"""Measure how often a skill's description makes Claude invoke the skill.

Usage:
  python3 scripts/trigger_eval.py --skill <skill-folder> --queries queries.json
      [--description "text to test instead of the SKILL.md one"] [--runs 3]
      [--split 0.4] [--seed 42] [--model MODEL_ID] [--workers 4] [--timeout 90]
      [--out results.json]

queries.json: [{"query": "...", "should_trigger": true}, ...]

How it works: for every run, a throwaway project folder gets .claude/skills/<probe>/SKILL.md
holding only the name and description (under a unique probe name, so installed copies of
the same skill do not interfere). `claude -p <query>` runs there with stream-json output, and
the run counts as triggered when the first tool call is the Skill tool naming the probe.
Runs stop at the first tool call, so they are cheap, but each one is a real billed model call.

Requires the Claude Code CLI (`claude`) on PATH. Prints a JSON summary to stdout; full
per-query results go to --out. Exit 0 on success, 2 on bad input, 3 if `claude` is missing.
"""

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

THRESHOLD = 0.5  # a query "triggers" when at least half of its runs invoked the skill
# Tools a model may call before deciding on the real first action; they do not decide triggering.
BOOKKEEPING_TOOLS = {"ToolSearch", "TodoWrite", "TaskCreate", "TaskUpdate", "TaskList"}


def read_frontmatter(skill_md):
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("SKILL.md has no frontmatter")
    raw = text.split("---", 2)[1]
    try:
        import yaml  # type: ignore
        return yaml.safe_load(raw) or {}
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent))
        from check_skill import _mini_yaml  # same folder
        return _mini_yaml(raw)


def run_once(query, description, model, timeout):
    probe = f"probe-{uuid.uuid4().hex[:10]}"
    tmp = Path(tempfile.mkdtemp(prefix="trigger-eval-"))
    try:
        sd = tmp / ".claude" / "skills" / probe
        sd.mkdir(parents=True)
        desc = "\n  ".join(description.strip().splitlines())
        (sd / "SKILL.md").write_text(f"---\nname: {probe}\ndescription: |\n  {desc}\n---\n\n# {probe}\n\nFollow the user's request.\n",
                                     encoding="utf-8")
        cmd = ["claude", "-p", query, "--output-format", "stream-json", "--verbose"]
        if model:
            cmd += ["--model", model]
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}  # allow nesting inside a Claude Code session
        proc = subprocess.Popen(cmd, cwd=tmp, env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        deadline = time.time() + timeout
        result = {"triggered": False, "first_tool": None, "error": None}
        try:
            for line in proc.stdout:
                if time.time() > deadline:
                    result["error"] = "timeout"
                    break
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("type") == "assistant":
                    for item in ev.get("message", {}).get("content", []):
                        if item.get("type") == "tool_use":
                            name, inp = item.get("name"), item.get("input", {})
                            if name in BOOKKEEPING_TOOLS:
                                continue
                            result["first_tool"] = name
                            result["triggered"] = (name == "Skill" and probe in str(inp.get("skill", ""))) or \
                                                  (name == "Read" and probe in str(inp.get("file_path", "")))
                            return result
                if ev.get("type") == "result":
                    if ev.get("is_error"):
                        result["error"] = str(ev.get("result", "error"))[:200]
                    return result
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
        return result
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="Measure skill trigger rates for a query set.")
    ap.add_argument("--skill", required=True, help="skill folder (its description is tested unless --description is given)")
    ap.add_argument("--queries", required=True, help='JSON list of {"query", "should_trigger"}')
    ap.add_argument("--description", help="description text to test instead of the one in SKILL.md")
    ap.add_argument("--runs", type=int, default=3, help="runs per query (default 3)")
    ap.add_argument("--split", type=float, default=0.0, help="fraction held out as validation set, e.g. 0.4 (default 0: no split)")
    ap.add_argument("--seed", type=int, default=42, help="seed for the split; keep it fixed across iterations")
    ap.add_argument("--model", help="model ID to test with (use the deployment model)")
    ap.add_argument("--workers", type=int, default=4, help="parallel claude processes (default 4)")
    ap.add_argument("--timeout", type=int, default=90, help="seconds per run (default 90)")
    ap.add_argument("--out", help="write full results JSON here")
    args = ap.parse_args()

    if not shutil.which("claude"):
        print("Error: `claude` CLI not found on PATH. Install Claude Code or run this from a machine that has it.", file=sys.stderr)
        return 3
    skill_md = Path(args.skill).expanduser() / "SKILL.md"
    if not skill_md.is_file():
        print(f"Error: {skill_md} not found", file=sys.stderr)
        return 2
    try:
        queries = json.loads(Path(args.queries).read_text(encoding="utf-8"))
        assert isinstance(queries, list) and all("query" in q and "should_trigger" in q for q in queries)
    except Exception:
        print('Error: --queries must be a JSON list of {"query": str, "should_trigger": bool}', file=sys.stderr)
        return 2
    description = args.description or str(read_frontmatter(skill_md).get("description", ""))
    if not description.strip():
        print("Error: no description to test", file=sys.stderr)
        return 2

    # Stratified split so both sets keep the positive/negative mix.
    rng = random.Random(args.seed)
    for i, q in enumerate(queries):
        q["id"] = i
        q["set"] = "train"
    if args.split > 0:
        for label in (True, False):
            group = [q for q in queries if bool(q["should_trigger"]) == label]
            rng.shuffle(group)
            for q in group[: round(len(group) * args.split)]:
                q["set"] = "validation"

    total = len(queries) * args.runs
    print(f"running {total} claude calls ({len(queries)} queries x {args.runs})...", file=sys.stderr)
    hits = {q["id"]: [] for q in queries}
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_once, q["query"], description, args.model, args.timeout): q["id"]
                for q in queries for _ in range(args.runs)}
        done = 0
        for f in as_completed(futs):
            hits[futs[f]].append(f.result())
            done += 1
            if done % 10 == 0 or done == total:
                print(f"  {done}/{total}", file=sys.stderr)

    results = []
    for q in queries:
        rs = hits[q["id"]]
        valid = [r for r in rs if not r["error"]]
        rate = sum(r["triggered"] for r in valid) / len(valid) if valid else None
        passed = None if rate is None else ((rate >= THRESHOLD) == bool(q["should_trigger"]))
        results.append({"query": q["query"], "should_trigger": q["should_trigger"], "set": q["set"],
                        "trigger_rate": rate, "passed": passed,
                        "errors": [r["error"] for r in rs if r["error"]],
                        "first_tools": [r["first_tool"] for r in rs]})

    def score(subset):
        graded = [r for r in subset if r["passed"] is not None]
        return {"passed": sum(r["passed"] for r in graded), "total": len(graded),
                "pass_rate": round(sum(r["passed"] for r in graded) / len(graded), 3) if graded else None}

    summary = {"description": description, "model": args.model, "runs": args.runs,
               "train": score([r for r in results if r["set"] == "train"]),
               "validation": score([r for r in results if r["set"] == "validation"]) if args.split > 0 else None,
               "train_failures": [{"query": r["query"], "should_trigger": r["should_trigger"], "trigger_rate": r["trigger_rate"]}
                                  for r in results if r["set"] == "train" and r["passed"] is False],
               "errored_queries": sum(1 for r in results if r["passed"] is None)}
    if args.out:
        Path(args.out).write_text(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
        summary["out"] = args.out
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
