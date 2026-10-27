#!/usr/bin/env python3
"""Check SKILL.md files against Claude Code rules (and repo rules when run inside a gongbang-style repo).

Usage: validate.py [SKILL_NAME_OR_PATH ...]
  No arguments: every skill under <repo>/skills/.
  Output: JSON on stdout. Exit code 1 if any error, 2 if it could not run (message on stderr), 0 otherwise. Needs PyYAML.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML이 없다. `pip install pyyaml` 후 다시 실행한다.", file=sys.stderr)
    sys.exit(2)

# Claude Code가 인식하는 frontmatter 키. 그 밖의 키는 CC가 경고 없이 무시하므로 오타로 본다.
SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
CC_KEYS = SPEC_KEYS | {"when_to_use", "argument-hint", "arguments", "disable-model-invocation", "user-invocable",
                       "disallowed-tools", "model", "effort", "context", "agent", "background", "hooks", "paths", "shell"}
BOOL_KEYS = ("disable-model-invocation", "user-invocable", "background")
ENUMS = {"effort": {"low", "medium", "high", "xhigh", "max"}, "context": {"fork"}, "shell": {"bash", "powershell"}}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
PROMOTED = ("engineering", "productivity")
TOC_LINES = 100  # 플랫폼 best practices 기준. skill-creator는 300을 쓴다.


def find_repo(start):
    for d in [start, *start.parents]:
        if (d / ".claude-plugin/plugin.json").is_file() and (d / "skills").is_dir():
            return d
    return None


def line_of(text, needle):
    i = text.find(needle)
    return text.count("\n", 0, i) + 1 if i >= 0 else 1


def split_frontmatter(text):
    """Return (frontmatter_text, body, body_start_line) or None if no frontmatter block."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for i, l in enumerate(lines[1:], 1):
        if l.strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:]), i + 2
    return None


def prose(t):
    """Blank out fenced blocks and inline code so examples are not checked as real links or wording. Keeps line count."""
    out, fence = [], False
    for l in t.split("\n"):
        if l.lstrip().startswith("```"):
            fence = not fence
            out.append("")
            continue
        out.append("" if fence else re.sub(r"`[^`]*`", "``", l))
    return "\n".join(out)


def is_user_invoked(fm):
    return str(fm.get("disable-model-invocation", "")).lower() in ("true", "yes", "on", "1")


def check_skill(skill_dir, repo):
    errs, warns = [], []
    E = lambda i, f, l, m: errs.append({"id": i, "file": str(f), "line": l, "msg": m})
    W = lambda i, f, l, m: warns.append({"id": i, "file": str(f), "line": l, "msg": m})
    rel = lambda p: p.relative_to(repo) if repo and p.is_relative_to(repo) else p
    md = skill_dir / "SKILL.md"
    text = md.read_text(encoding="utf-8")
    f = rel(md)

    parts = split_frontmatter(text)
    if parts is None:
        E("E1", f, 1, "첫 줄이 `---`가 아니거나 닫는 `---`가 없다. CC는 파일 전체를 본문으로 읽어 description이 사라진다")
        return {"name": skill_dir.name, "path": str(rel(skill_dir)), "errors": errs, "warnings": warns}, {}
    fm_text, body, body_line = parts
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as e:
        E("E2", f, 2, f"frontmatter YAML 파싱 실패: {str(e).splitlines()[0]}. CC는 필드 없이 로드한다")
        fm = None
    if fm is not None and not isinstance(fm, dict):
        E("E2", f, 2, "frontmatter가 key: value 매핑이 아니다")
        fm = None
    if fm is None:
        return {"name": skill_dir.name, "path": str(rel(skill_dir)), "errors": errs, "warnings": warns}, {}

    name = fm.get("name")
    if not isinstance(name, str) or not name:
        E("E3", f, 2, "`name`이 없다")
    else:
        nl = line_of(text, "name:")
        if len(name) > 64 or not NAME_RE.match(name):
            E("E3", f, nl, f"`name` '{name}'이 형식(소문자·숫자·하이픈, 하이픈으로 시작·끝·연속 금지, 64자 이하)에 맞지 않는다")
        if name != skill_dir.name:
            E("E3", f, nl, f"`name` '{name}'이 폴더 이름 '{skill_dir.name}'과 다르다")
        if "anthropic" in name.lower() or "claude" in name.lower():
            E("E4", f, nl, "`name`에 예약어 `anthropic`이나 `claude`가 들어 있다")

    desc = fm.get("description")
    dl = line_of(text, "description:")
    if not isinstance(desc, str) or not desc.strip():
        E("E5", f, dl, "`description`이 없거나 비어 있다")
        desc = ""
    else:
        if len(desc) > 1024:
            E("E5", f, dl, f"`description`이 {len(desc)}자다(1,024자 이하)")
        if re.search(r"<[^>]+>", desc):
            E("E5", f, dl, "`description`에 XML/HTML 태그가 있다")
        if re.search(r"\b(I can|I will|You can|you should)\b|도와드|당신", desc, re.I):
            W("W11", f, dl, "`description`에 1인칭·2인칭 표현이 있다. 3인칭으로 쓴다")
    if len(desc) + len(str(fm.get("when_to_use", ""))) > 1536:
        W("W2", f, dl, "`description` + `when_to_use`가 1,536자를 넘어 CC 목록에서 잘린다. 핵심 용도를 앞에 둔다")

    for k in fm:
        if k not in CC_KEYS:
            E("E6", f, line_of(text, f"{k}:"), f"알 수 없는 키 `{k}`. CC는 경고 없이 무시한다(오타 확인)")
    for k in BOOL_KEYS:
        if k in fm and not isinstance(fm[k], bool):
            E("E7", f, line_of(text, f"{k}:"), f"`{k}`는 true/false여야 한다(현재 {fm[k]!r})")
    for k, allowed in ENUMS.items():
        if k in fm and fm[k] not in allowed:
            E("E7", f, line_of(text, f"{k}:"), f"`{k}` 값 {fm[k]!r}은 {sorted(allowed)} 중 하나여야 한다")
    if "compatibility" in fm and (not isinstance(fm["compatibility"], str) or len(fm["compatibility"]) > 500):
        E("E7", f, line_of(text, "compatibility:"), "`compatibility`는 500자 이하 문자열이어야 한다")
    if "metadata" in fm and not isinstance(fm["metadata"], dict):
        E("E7", f, line_of(text, "metadata:"), "`metadata`는 매핑이어야 한다. CC는 매핑이 아니면 값을 버린다")
    if fm.get("user-invocable") is False:
        W("W9", f, line_of(text, "user-invocable:"), "`user-invocable: false`는 저장소의 두 호출 방식(User/Model-invoked) 밖이다")

    n_lines = body.count("\n") + 1
    # ponytail: 토큰은 글자 수/3으로 어림. 정확한 값이 필요하면 토큰 카운트 API로 바꾼다
    if n_lines >= 500 or len(body) / 3 > 5000:
        W("W1", f, body_line, f"본문이 {n_lines}줄, 약 {len(body) // 3}토큰이다(500줄·5,000토큰 미만 권장). 참조 파일로 나눈다")

    for m in re.finditer(r"!`([^`]+)`", text):
        if "|| true" not in m.group(1):
            W("W10", f, text.count("\n", 0, m.start()) + 1,"동적 주입 명령이 실패하면 스킬 호출 전체가 중단된다. `|| true`를 붙일지 검토한다")

    direct = {(md.parent / m.group(1).split("#")[0]).resolve() for m in LINK_RE.finditer(prose(text))}
    # 링크, 참조 깊이, 목차, 경로·시간 표현은 스킬 안의 모든 .md에 적용한다
    for p in sorted(skill_dir.rglob("*.md")):
        t = prose(p.read_text(encoding="utf-8"))
        pf = rel(p)
        for m in LINK_RE.finditer(t):
            target = m.group(1).split("#")[0]
            if not target or re.match(r"[a-z]+:", target):
                continue
            dest = (p.parent / target).resolve()
            ln = t.count("\n", 0, m.start()) + 1
            if not dest.is_relative_to(skill_dir.resolve()):
                E("E9", pf, ln, f"스킬 폴더 밖을 가리키는 링크 `{target}`. 다른 스킬은 'Skill 도구로 `<이름>`을 호출한다'고 쓴다")
            elif not dest.exists():
                E("E8", pf, ln, f"링크 `{target}`가 가리키는 파일이 없다")
            elif p != md and dest.suffix == ".md" and dest not in direct and dest != md.resolve():
                W("W3", pf, ln, f"`{target}`는 SKILL.md가 직접 링크하지 않고 참조 파일을 거쳐야 닿는다. SKILL.md에서 한 단계 깊이로 연결한다")
        if p != md and t.count("\n") + 1 > TOC_LINES and not re.search(r"목차|contents", "\n".join(t.split("\n")[:20]), re.I):
            W("W4", pf, 1, f"{TOC_LINES}줄이 넘는데 맨 위 20줄 안에 목차가 없다")
        old = False
        for i, l in enumerate(t.split("\n"), 1):
            if l.startswith("#"):
                old = bool(re.search(r"old patterns|이전 패턴", l, re.I))
            if re.search(r"\w\\\w+\.\w{1,4}\b", l) and "```" not in l:
                W("W5", pf, i, "백슬래시 경로가 있다. 경로는 `/`로 쓴다")
            if not old and re.search(r"20\d\d\s*년?\s*(\d+\s*월\s*)?(이후|이전|부터|까지)|(before|after|until)\s+(\w+\s+)?20\d\d", l, re.I):
                W("W6", pf, i, "시간에 따라 틀려질 표현이다. 'Old patterns' 절로 옮기거나 지운다")
        caps = re.findall(r"\b(MUST|ALWAYS|NEVER|CRITICAL)\b", t)
        if len(caps) > 3:
            W("W12", pf, 1, f"대문자 강조어가 {len(caps)}개다. 강조 대신 이유를 쓴다")

    return {"name": skill_dir.name, "path": str(rel(skill_dir)), "errors": errs, "warnings": warns}, fm


def repo_checks(repo, results, fms):
    """CLAUDE.md 저장소 규칙. 결과는 해당 스킬 항목이나 repo_errors에 붙인다."""
    repo_errs = []
    by_name = {r["name"]: r for r in results}
    for stray in sorted((repo / "skills").glob("*/SKILL.md")):
        repo_errs.append({"id": "E11", "file": str(stray.relative_to(repo)), "line": 1,
                          "msg": "버킷 없이 skills/ 바로 아래 있는 스킬. 기본 skills/ 스캔으로 plugin.json과 상관없이 배포된다"})

    all_skills = sorted(p.parent for p in (repo / "skills").glob("*/*/SKILL.md"))
    manifest = json.loads((repo / ".claude-plugin/plugin.json").read_text(encoding="utf-8")).get("skills", [])
    manifest = {manifest} if isinstance(manifest, str) else set(manifest)
    promoted = {f"./{s.relative_to(repo)}" for s in all_skills if s.parent.name in PROMOTED}
    for p in sorted(promoted - manifest):
        repo_errs.append({"id": "E10", "file": ".claude-plugin/plugin.json", "line": 1, "msg": f"`skills` 배열에 없다: {p}"})
    for p in sorted(manifest - promoted):
        repo_errs.append({"id": "E10", "file": ".claude-plugin/plugin.json", "line": 1, "msg": f"승격 버킷의 스킬이 아닌데 `skills`에 있다: {p}"})

    user_invoked = {}
    for s in all_skills:
        parts = split_frontmatter(s.joinpath("SKILL.md").read_text(encoding="utf-8"))
        try:
            fm = yaml.safe_load(parts[0]) if parts else {}
        except yaml.YAMLError:
            fm = {}
        user_invoked[s.name] = is_user_invoked(fm or {})

    top_readme = (repo / "README.md").read_text(encoding="utf-8") if (repo / "README.md").exists() else ""
    for s in all_skills:
        r = by_name.get(s.name)
        if r is None or s.name not in fms:
            continue
        add = lambda i, f, l, m, kind="errors": r[kind].append({"id": i, "file": f, "line": l, "msg": m})
        bucket_readme = s.parent / "README.md"
        rf = str(bucket_readme.relative_to(repo))
        expect = "User-invoked" if user_invoked[s.name] else "Model-invoked"
        if not bucket_readme.exists():
            add("E12", rf, 1, "버킷 README.md가 없다")
        else:
            section = None
            for i, l in enumerate(bucket_readme.read_text(encoding="utf-8").split("\n"), 1):
                if l.startswith("## "):
                    section = l[3:].strip()
                if f"./{s.name}/SKILL.md" in l:
                    if section != expect:
                        add("E12", rf, i, f"'{section}' 절에 있지만 frontmatter 기준으로는 {expect}다")
                    break
            else:
                add("E12", rf, 1, f"버킷 README에 `./{s.name}/SKILL.md` 링크가 없다")
        if s.parent.name in PROMOTED:
            link = f"{s.relative_to(repo)}/SKILL.md"
            if link not in top_readme:
                add("E12", "README.md", 1, f"최상위 README에 `{link}` 링크가 없다")
            else:
                section = None
                for l in top_readme.split("\n"):
                    if l.startswith("#"):
                        section = l.lstrip("#").strip()
                    if link in l:
                        if section != expect:
                            add("E12", "README.md", line_of(top_readme, link), f"최상위 README의 '{section}' 절에 있지만 {expect}다")
                        break
        if not (repo / "evals" / s.name).is_dir():
            add("W7", f"evals/{s.name}", 0, "동작 eval 폴더가 없다", "warnings")
        if not user_invoked[s.name] and not (repo / "evals-trigger" / s.name).is_dir():
            add("W7", f"evals-trigger/{s.name}", 0, "Model-invoked인데 트리거 eval 폴더가 없다", "warnings")
        for md in sorted(s.rglob("*.md")):
            t = md.read_text(encoding="utf-8")
            for m in re.finditer(r"Skill 도구로 `([\w:-]+)`", t):
                target = m.group(1).split(":")[-1]
                if user_invoked.get(target):
                    add("E13", str(md.relative_to(repo)), line_of(t, m.group(0)),
                        f"`{target}`는 User-invoked라 Skill 도구로 호출할 수 없다. 사용자에게 실행을 안내한다")

    # W8: 승격 버킷 스킬이 바뀌었는데 plugin.json version이 그대로인지 (커밋 안 된 변경 기준)
    try:
        changed = subprocess.run(["git", "-C", str(repo), "diff", "HEAD", "--name-only"],
                                 capture_output=True, text=True, check=True).stdout.split()
        diff = subprocess.run(["git", "-C", str(repo), "diff", "HEAD", "--", ".claude-plugin/plugin.json"],
                              capture_output=True, text=True, check=True).stdout
        touched = sorted({c for c in changed if any(c.startswith(f"skills/{b}/") for b in PROMOTED)})
        if touched and '"version"' not in diff:
            repo_errs.append({"id": "W8", "file": ".claude-plugin/plugin.json", "line": 1,
                              "msg": f"승격 스킬이 바뀌었는데 version이 그대로다: {', '.join(touched[:3])}"})
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return repo_errs


def resolve(arg, repo):
    p = Path(arg).expanduser()
    if p.name == "SKILL.md":
        p = p.parent
    if (p / "SKILL.md").is_file():
        return p.resolve()
    if repo:
        hits = sorted((repo / "skills").glob(f"*/{arg}/SKILL.md")) + sorted((repo / "skills").glob(f"{arg}/SKILL.md"))
        if hits:
            return hits[0].parent
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="*", help="스킬 이름 또는 스킬 폴더/SKILL.md 경로")
    args = ap.parse_args()

    first = resolve(args.targets[0], None) if args.targets else None
    repo = find_repo(first or Path.cwd())
    if args.targets:
        dirs, missing = [], []
        for t in args.targets:
            d = resolve(t, repo)
            (dirs if d else missing).append(d or t)
    else:
        if not repo:
            print("인자가 없고 skills/와 .claude-plugin/plugin.json이 있는 저장소도 찾지 못했다. 스킬 경로를 넘긴다.", file=sys.stderr)
            sys.exit(2)
        dirs, missing = sorted(p.parent for p in (repo / "skills").glob("**/SKILL.md")), []

    results, fms = [], {}
    for d in dirs:
        r, fm = check_skill(d, repo)
        results.append(r)
        if fm:
            fms[r["name"]] = fm
    repo_level = repo_checks(repo, results, fms) if repo else []
    out = {"repo": str(repo) if repo else None, "skills": results,
           "repo_findings": repo_level, "not_found": [str(m) for m in missing]}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    has_err = missing or any(r["errors"] for r in results) or any(x["id"].startswith("E") for x in repo_level)
    sys.exit(1 if has_err else 0)


if __name__ == "__main__":
    main()
