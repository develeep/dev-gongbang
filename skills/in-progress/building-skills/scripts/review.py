#!/usr/bin/env python3
"""Build a standalone review page (review.html) for one eval iteration.

Usage:
  python3 scripts/review.py <workspace>/iteration-N --skill-name NAME
                            [--previous <workspace>/iteration-<N-1>] [--output PATH]

Reads eval_metadata.json, each config's outputs/ and grading.json, and benchmark.json
if present. The page needs no server: the reviewer types feedback per case and clicks
"피드백 내보내기", which downloads feedback.json. Put that file at
<iteration>/feedback.json; the next iteration's page shows it as previous feedback.
Standard library only.
"""

import argparse
import base64
import html
import json
import mimetypes
import sys
from pathlib import Path

TEXT_EXT = {".md", ".txt", ".json", ".csv", ".tsv", ".py", ".js", ".ts", ".yaml", ".yml", ".sh",
            ".xml", ".sql", ".html", ".css", ".log", ".toml", ".ini", ".skill_md"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
MAX_TEXT = 200_000      # chars per file shown inline; larger files are cut so the page stays usable
MAX_IMG = 3_000_000     # bytes per image embedded as data: URI


def load_json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def collect_files(out_dir):
    files = []
    if not out_dir.is_dir():
        return files
    for p in sorted(out_dir.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(out_dir))
        ext = p.suffix.lower()
        size = p.stat().st_size
        item = {"name": rel, "size": size}
        if ext in IMG_EXT and size <= MAX_IMG:
            mime = mimetypes.guess_type(p.name)[0] or "image/png"
            item["image"] = f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()
        elif ext in TEXT_EXT or size < 50_000:
            try:
                text = p.read_text(encoding="utf-8")
                if len(text) > MAX_TEXT:
                    text = text[:MAX_TEXT] + f"\n\n… ({len(text) - MAX_TEXT:,} chars cut)"
                item["text"] = text
            except UnicodeDecodeError:
                pass
        files.append(item)
    # transcript last, it is long and secondary
    files.sort(key=lambda f: (f["name"] == "transcript.md", f["name"]))
    return files


def runs_of(config_dir):
    runs = sorted(p for p in config_dir.iterdir() if p.is_dir() and p.name.startswith("run-"))
    return runs or [config_dir]


def collect_case(case_dir):
    meta = load_json(case_dir / "eval_metadata.json") or {}
    configs = []
    for cdir in sorted(p for p in case_dir.iterdir() if p.is_dir()):
        for rd in runs_of(cdir):
            if not (rd / "outputs").exists() and not (rd / "grading.json").exists():
                continue
            label = cdir.name if rd == cdir else f"{cdir.name}/{rd.name}"
            grading = load_json(rd / "grading.json") or {}
            exps = grading.get("expectations") or grading.get("assertion_results") or []
            configs.append({"label": label, "files": collect_files(rd / "outputs"),
                            "expectations": exps, "notes": grading.get("assertion_notes", []),
                            "timing": load_json(rd / "timing.json") or {}})
    configs.sort(key=lambda c: (not c["label"].startswith("with_skill"), c["label"]))
    return {"name": case_dir.name, "prompt": meta.get("prompt", "(eval_metadata.json에 프롬프트 없음)"),
            "assertions": meta.get("assertions", []), "configs": configs}


def previous_feedback(prev_dir):
    fb = load_json(prev_dir / "feedback.json") if prev_dir else None
    out = {}
    if isinstance(fb, dict):
        for r in fb.get("reviews", []):
            out[r.get("case") or r.get("run_id", "")] = r.get("feedback", "")
    return out


PAGE = r"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#fafaf8;--panel:#fff;--ink:#1d1d1b;--muted:#6b6b66;--line:#e4e2dc;--pass:#1f7a4d;--passbg:#e6f4ec;--fail:#b3261e;--failbg:#fbe9e7;--accent:#3b5bdb;--code:#f3f2ee}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--panel:#1f1f1d;--ink:#ecebe6;--muted:#a09f99;--line:#34332f;--pass:#6fcf97;--passbg:#1d3326;--fail:#f28b82;--failbg:#3a1f1d;--accent:#8ea2ff;--code:#262623}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,"Segoe UI","Apple SD Gothic Neo","Malgun Gothic",sans-serif}
header{position:sticky;top:0;z-index:2;background:var(--panel);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
header h1{font-size:16px;margin:0 12px 0 0}button,select{font:inherit;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:6px;padding:5px 10px;cursor:pointer}
button.primary{background:var(--accent);border-color:var(--accent);color:#fff}button[aria-pressed=true]{border-color:var(--accent);color:var(--accent)}
main{max-width:1100px;margin:0 auto;padding:16px}section.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:14px}
h2{font-size:15px;margin:0 0 8px}h3{font-size:14px;margin:12px 0 6px}.muted{color:var(--muted);font-size:13px}
pre{background:var(--code);padding:10px;border-radius:6px;overflow:auto;white-space:pre-wrap;word-break:break-word;font:12.5px/1.5 ui-monospace,Menlo,Consolas,monospace;max-height:520px}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}
.exp{border-radius:6px;padding:6px 8px;margin:4px 0;font-size:13.5px}.exp.p{background:var(--passbg)}.exp.f{background:var(--failbg)}
.exp b{color:var(--pass)}.exp.f b{color:var(--fail)}details{margin:6px 0}summary{cursor:pointer;font-weight:600;font-size:13.5px}
textarea{width:100%;min-height:90px;font:inherit;border:1px solid var(--line);border-radius:6px;padding:8px;background:var(--panel);color:var(--ink)}
table{border-collapse:collapse;width:100%;font-size:13.5px}td,th{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
img{max-width:100%;border:1px solid var(--line);border-radius:6px}.hidden{display:none}.pill{display:inline-block;font-size:12px;padding:1px 8px;border-radius:99px;background:var(--code)}
</style></head><body>
<header><h1>__TITLE__</h1>
<button id="tab-out" aria-pressed="true">결과</button><button id="tab-bench" aria-pressed="false">Benchmark</button>
<select id="casesel" aria-label="케이스"></select><button id="prev">◀</button><button id="next">▶</button>
<span class="muted" id="pos"></span><span style="flex:1"></span><button class="primary" id="export">피드백 내보내기</button></header>
<main><div id="out"></div><div id="bench" class="hidden"></div></main>
<script id="data" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const KEY='review:'+D.title;let fb={};try{fb=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(fb))}catch(e){}};
let idx=0;const sel=document.getElementById('casesel');
D.cases.forEach((c,i)=>{const o=document.createElement('option');o.value=i;o.textContent=c.name;sel.appendChild(o)});
function files(fs){if(!fs.length)return '<p class="muted">출력 파일 없음</p>';return fs.map(f=>{
 const head=`${esc(f.name)} <span class="muted">${(f.size/1024).toFixed(1)} KB</span>`;
 const body=f.image?`<img src="${f.image}" alt="${esc(f.name)}">`:(f.text!=null?`<pre>${esc(f.text)}</pre>`:'<p class="muted">미리보기 없음</p>');
 return `<details ${f.name==='transcript.md'?'':'open'}><summary>${head}</summary>${body}</details>`}).join('')}
function grades(c){if(!c.expectations.length)return '<p class="muted">채점 없음</p>';
 const n=c.expectations.filter(e=>e.passed).length;
 return `<p><span class="pill">${n}/${c.expectations.length} 통과</span></p>`+c.expectations.map(e=>`<div class="exp ${e.passed?'p':'f'}"><b>${e.passed?'PASS':'FAIL'}</b> ${esc(e.text)}<div class="muted">${esc(e.evidence)}</div></div>`).join('')+(c.notes&&c.notes.length?`<p class="muted">채점 메모: ${c.notes.map(esc).join(' / ')}</p>`:'')}
function timing(t){if(!t||(!t.total_tokens&&!t.duration_ms&&!t.total_duration_seconds))return '';const s=t.total_duration_seconds??(t.duration_ms?t.duration_ms/1000:null);return `<span class="muted">${s!=null?s.toFixed(1)+'초':''} ${t.total_tokens?'· '+t.total_tokens.toLocaleString()+' 토큰':''}</span>`}
function render(){const c=D.cases[idx];sel.value=idx;document.getElementById('pos').textContent=`${idx+1} / ${D.cases.length}`;
 const prev=D.previous[c.name];const pfb=D.prevFeedback[c.name];
 document.getElementById('out').innerHTML=`
 <section class="card"><h2>${esc(c.name)}</h2><h3>프롬프트</h3><pre>${esc(c.prompt)}</pre>
 ${c.assertions.length?`<details><summary>assertion ${c.assertions.length}개</summary><ul>${c.assertions.map(a=>`<li>${esc(a)}</li>`).join('')}</ul></details>`:''}</section>
 <div class="cols">${c.configs.map(k=>`<section class="card"><h2>${esc(k.label)} ${timing(k.timing)}</h2>
  <details><summary>채점 결과</summary>${grades(k)}</details><h3>출력</h3>${files(k.files)}</section>`).join('')}</div>
 ${prev?`<section class="card"><details><summary>이전 반복의 출력 (${esc(prev.label)})</summary>${files(prev.files)}</details></section>`:''}
 <section class="card"><h2>피드백</h2>${pfb?`<p class="muted">이전 피드백: ${esc(pfb)}</p>`:''}
 <textarea id="fbt" placeholder="구체적으로 적어 주세요. 예: 표에 단위가 빠짐. 문제없으면 비워 두세요.">${esc(fb[c.name]||'')}</textarea></section>`;
 document.getElementById('fbt').addEventListener('input',e=>{fb[c.name]=e.target.value;save()})}
function bench(){const b=D.benchmark;const el=document.getElementById('bench');
 if(!b){el.innerHTML='<section class="card"><p class="muted">benchmark.json 없음. 검증 2단계 이상에서 scripts/aggregate.py를 실행하면 생깁니다.</p></section>';return}
 const pct=v=>v==null?'-':(v*100).toFixed(0)+'%';const num=(s,d=1)=>s.mean==null?'-':`${s.mean.toFixed(d)} ± ${s.stddev.toFixed(d)}`;
 let h=`<section class="card"><h2>설정별 요약</h2><table><tr><th>설정</th><th>실행</th><th>통과율</th><th>시간(초)</th><th>토큰</th></tr>`+
 b.configs.map(c=>{const s=b.run_summary[c];return `<tr><td>${esc(c)}</td><td>${s.runs}</td><td>${pct(s.pass_rate.mean)}</td><td>${num(s.time_seconds)}</td><td>${num(s.tokens,0)}</td></tr>`}).join('')+'</table>';
 const ds=Object.entries(b.delta||{});if(ds.length)h+='<h3>차이</h3><table>'+ds.map(([k,d])=>`<tr><td>${esc(k)}</td><td>통과율 ${d.pass_rate==null?'-':((d.pass_rate*100>=0?'+':'')+(d.pass_rate*100).toFixed(0)+'%p')}</td><td>시간 ${d.time_seconds==null?'-':d.time_seconds.toFixed(1)+'초'}</td><td>토큰 ${d.tokens==null?'-':Math.round(d.tokens).toLocaleString()}</td></tr>`).join('')+'</table>';
 h+='</section>';if(b.discrimination&&b.configs.length>1)h+=`<section class="card"><h2>assertion 판별력</h2><table><tr><th>케이스</th><th>assertion</th><th>판정</th></tr>`+b.discrimination.map(d=>`<tr><td>${esc(d.case)}</td><td>${esc(d.assertion)}</td><td>${esc(d.verdict)}${d.flaky?' · 흔들림':''}</td></tr>`).join('')+'</table></section>';
 if(D.analysis)h+=`<section class="card"><h2>분석 메모</h2><pre>${esc(D.analysis)}</pre></section>`;el.innerHTML=h}
function tab(b){document.getElementById('out').classList.toggle('hidden',b);document.getElementById('bench').classList.toggle('hidden',!b);
 document.getElementById('tab-out').setAttribute('aria-pressed',!b);document.getElementById('tab-bench').setAttribute('aria-pressed',b);if(b)bench()}
document.getElementById('tab-out').onclick=()=>tab(false);document.getElementById('tab-bench').onclick=()=>tab(true);
sel.onchange=()=>{idx=+sel.value;render()};document.getElementById('prev').onclick=()=>{idx=(idx-1+D.cases.length)%D.cases.length;render()};
document.getElementById('next').onclick=()=>{idx=(idx+1)%D.cases.length;render()};
document.addEventListener('keydown',e=>{if(e.target.tagName==='TEXTAREA')return;if(e.key==='ArrowRight')document.getElementById('next').click();if(e.key==='ArrowLeft')document.getElementById('prev').click()});
document.getElementById('export').onclick=()=>{const now=new Date().toISOString();
 const out={skill:D.skill,iteration:D.iteration,status:'complete',reviews:D.cases.map(c=>({case:c.name,run_id:c.name+'-'+(c.configs[0]?c.configs[0].label:''),feedback:(fb[c.name]||'').trim(),timestamp:now}))};
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(out,null,2)],{type:'application/json'}));a.download='feedback.json';a.click()};
if(D.cases.length)render();else document.getElementById('out').innerHTML='<section class="card">케이스가 없습니다.</section>';
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser(description="Build a standalone review page for one eval iteration.")
    ap.add_argument("iteration_dir")
    ap.add_argument("--skill-name", required=True)
    ap.add_argument("--previous", help="previous iteration dir, to show its outputs and feedback")
    ap.add_argument("--analysis", help="optional text/markdown file with analyst notes shown on the Benchmark tab")
    ap.add_argument("--output", help="output path (default: <iteration_dir>/review.html)")
    args = ap.parse_args()

    it = Path(args.iteration_dir).expanduser()
    if not it.is_dir():
        print(f"Error: {it} is not a directory", file=sys.stderr)
        return 2
    case_dirs = sorted(p for p in it.iterdir() if p.is_dir() and
                       ((p / "eval_metadata.json").exists() or any(p.glob("*/outputs"))))
    if not case_dirs:
        print(f"Error: no case folders with eval_metadata.json or */outputs under {it}", file=sys.stderr)
        return 1
    cases = [collect_case(p) for p in case_dirs]

    prev_dir = Path(args.previous).expanduser() if args.previous else None
    previous = {}
    if prev_dir and prev_dir.is_dir():
        for c in cases:
            pc = prev_dir / c["name"]
            if pc.is_dir():
                pcase = collect_case(pc)
                if pcase["configs"]:
                    previous[c["name"]] = pcase["configs"][0]
    analysis = Path(args.analysis).read_text(encoding="utf-8") if args.analysis else None

    title = f"{args.skill_name} · {it.name} 리뷰"
    data = {"title": title, "skill": args.skill_name, "iteration": it.name, "cases": cases,
            "previous": previous, "prevFeedback": previous_feedback(prev_dir),
            "benchmark": load_json(it / "benchmark.json"), "analysis": analysis}
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = PAGE.replace("__TITLE__", html.escape(title)).replace("__DATA__", blob)
    out = Path(args.output).expanduser() if args.output else it / "review.html"
    out.write_text(page, encoding="utf-8")
    print(json.dumps({"review_html": str(out), "cases": len(cases),
                      "configs": sorted({k["label"] for c in cases for k in c["configs"]})}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
