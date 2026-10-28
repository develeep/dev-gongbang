#!/usr/bin/env python3
"""Static checks for an Agent Skill folder (spec + Claude best practices).

Usage:
  python3 scripts/check_skill.py <skill-folder> [--json]

Levels:
  ERROR  breaks the Agent Skills spec or a hard limit. Fix before shipping.
  WARN   likely violates a best practice. Fix, or tell the user why not.
  INFO   heuristic hint. Look at it, ignore if it does not apply.

Exit codes: 0 = no ERROR, 1 = at least one ERROR, 2 = bad arguments / no SKILL.md.
Standard library only (Python 3.9+).
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Limits from https://agentskills.io/specification and the Claude best-practices page.
NAME_MAX = 64
DESC_MAX = 1024
COMPAT_MAX = 500
BODY_MAX_LINES = 500
BODY_MAX_TOKENS = 5000          # spec recommends < 5000 tokens for the SKILL.md body
REF_TOC_LINES = 100             # reference files longer than this need a table of contents
SHOUT_LIMIT = 3                 # a few strong words are fine; many cause over-triggering

SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
CLAUDE_CODE_KEYS = {
    "disable-model-invocation", "argument-hint", "user-invocable", "model",
    "context", "agent", "hooks", "when_to_use", "version",
}
RESERVED = ("anthropic", "claude")
VAGUE_NAMES = {"helper", "helpers", "utils", "util", "tools", "tool", "documents", "data", "files", "misc", "stuff"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
XML_RE = re.compile(r"<\s*/?\s*[A-Za-z][\w:-]*(\s[^<>]*)?>")
FIRST_SECOND_PERSON = re.compile(
    r"\b(I can|I will|I'll|I help|you can|you should|your )\b|도와\s?드|드립니다|해\s?드려|당신|여러분",
    re.IGNORECASE,
)
WHEN_RE = re.compile(r"\b(use (this|it)? ?when|use for|when the user|whenever|use this skill)\b|할 때|하는 경우|경우에|때 사용|요청할 때|상황", re.IGNORECASE)
TIME_RE = re.compile(
    r"\b(before|after|until|as of|since)\s+(January|February|March|April|May|June|July|August|September|October|November|December|20\d\d)"
    r"|20\d\d년\s*\d{1,2}월\s*(이전|이후|부터|까지)",
    re.IGNORECASE,
)
SHOUT_RE = re.compile(r"\b(MUST|CRITICAL|ALWAYS|NEVER|IMPORTANT)\b")
BACKSLASH_PATH_RE = re.compile(r"(?<![\\\w])[\w.-]+\\[\w.-]+\.(md|py|sh|js|ts|json|yaml|yml|txt)\b")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
CODE_PATH_RE = re.compile(r"`((?:scripts|references|reference|assets|templates|examples)/[^`\s]+)`")
# A link sentence that only says "see X" gives the agent no cue for when to open X.
GENERIC_POINTER_RE = re.compile(r"참고(하라|한다|하세요|\s*$|\.)|자세한|자세히는|\bsee\b|\bfor (more )?details\b|\bmore info", re.IGNORECASE)
CONDITION_RE = re.compile(r"\b(when|if|before|after|only|unless|while)\b|면\b|때|경우|전에|후에|단계", re.IGNORECASE)
TOC_RE = re.compile(r"^#{1,3}\s*(목차|contents|table of contents|toc)\b", re.IGNORECASE | re.MULTILINE)

findings = []


def add(level, rule, msg, where=""):
    findings.append({"level": level, "rule": rule, "message": msg, "where": where})


def estimate_tokens(text):
    # Rough: ASCII ~4 chars/token, Hangul/CJK ~1 char/token. Good enough for a 5k budget check.
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    other = len(text) - ascii_chars
    return int(ascii_chars / 4 + other * 1.0)


def parse_frontmatter(text):
    """Return (dict, body, error). Uses PyYAML when available, else a small fallback parser."""
    if not text.startswith("---"):
        return None, text, "SKILL.md does not start with a '---' frontmatter block"
    m = re.match(r"^---\s*\n(.*?)\n---\s*(\n|$)", text, re.DOTALL)
    if not m:
        return None, text, "frontmatter is not closed with '---'"
    raw, body = m.group(1), text[m.end():]
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(raw) or {}
        if not isinstance(data, dict):
            return None, body, "frontmatter is not a YAML mapping"
        return data, body, None
    except ImportError:
        pass
    except Exception as e:  # yaml error
        return None, body, f"frontmatter YAML error: {e}"
    return _mini_yaml(raw), body, None


def _scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    return v


def _mini_yaml(raw):
    """Tiny YAML subset: `key: value`, `key: |` / `key: >` blocks, and one-level nested mappings."""
    data, lines, i = {}, raw.splitlines(), 0
    while i < len(lines):
        m = re.match(r"^([A-Za-z][\w-]*)\s*:\s*(.*)$", lines[i])
        i += 1
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        indented = []
        while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
            indented.append(lines[i])
            i += 1
        if val[:1] in ("|", ">"):
            parts = [l.strip() for l in indented]
            data[key] = ("\n" if val[0] == "|" else " ").join(parts).strip()
        elif val == "" and indented:
            sub = {}
            for l in indented:
                sm = re.match(r"^\s+([\w.-]+)\s*:\s*(.*)$", l)
                if sm:
                    sub[sm.group(1)] = _scalar(sm.group(2))
            data[key] = sub
        else:
            data[key] = _scalar(" ".join([val] + [l.strip() for l in indented]))
    return data


def check_yaml_comments(text):
    """In plain (unquoted, non-block) YAML scalars, ' #' starts a comment and silently cuts the value."""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return
    for i, line in enumerate(m.group(1).splitlines(), 2):
        km = re.match(r"^([A-Za-z][\w-]*)\s*:\s*(.+)$", line)
        if not km:
            continue
        val = km.group(2).strip()
        if val[:1] in ("'", '"', "|", ">"):
            continue
        if re.search(r"\s#", val):
            add("ERROR", "frontmatter.comment", f"'{km.group(1)}' is cut at ' #' (YAML comment). Quote the value or remove the '#'", f"SKILL.md:{i}")


def check_frontmatter(fm, folder):
    name = fm.get("name")
    if not name or not isinstance(name, str):
        add("ERROR", "name.required", "frontmatter has no 'name'")
    else:
        if len(name) > NAME_MAX:
            add("ERROR", "name.length", f"name is {len(name)} chars (max {NAME_MAX})")
        if not NAME_RE.match(name):
            add("ERROR", "name.format", f"'{name}': use lowercase letters, digits and single hyphens; no leading/trailing hyphen")
        if name != folder.name:
            add("ERROR", "name.folder", f"name '{name}' differs from folder name '{folder.name}'")
        for word in RESERVED:
            if word in name:
                add("ERROR", "name.reserved", f"name contains reserved word '{word}'")
        if XML_RE.search(name):
            add("ERROR", "name.xml", "name contains an XML tag")
        if set(name.split("-")) & VAGUE_NAMES and len(name.split("-")) <= 2:
            add("WARN", "name.vague", f"'{name}' is vague; name the activity (gerund form like 'processing-pdfs')")
        elif not name.split("-")[0].endswith("ing"):
            add("INFO", "name.gerund", f"gerund form is preferred (e.g. 'processing-pdfs'); '{name}' is fine if it reads clearly")

    desc = fm.get("description")
    if not desc or not isinstance(desc, str) or not desc.strip():
        add("ERROR", "description.required", "frontmatter has no non-empty 'description'")
    else:
        desc = desc.strip()
        if len(desc) > DESC_MAX:
            add("ERROR", "description.length", f"description is {len(desc)} chars (max {DESC_MAX})")
        elif len(desc) > DESC_MAX * 0.9:
            add("INFO", "description.length", f"description is {len(desc)}/{DESC_MAX} chars; little room left")
        if XML_RE.search(desc):
            add("ERROR", "description.xml", "description contains an XML tag")
        m = FIRST_SECOND_PERSON.search(desc)
        if m:
            add("WARN", "description.person", f"write in third person; found '{m.group(0).strip()}'")
        user_invoked = fm.get("disable-model-invocation") is True
        if not user_invoked and not WHEN_RE.search(desc):
            add("WARN", "description.when", "model-invoked skill: say when to use it (e.g. '...할 때 사용한다' / 'Use when ...')")
        if len(desc) < 40:
            add("WARN", "description.short", "description is very short; say concretely what it does and when")

    compat = fm.get("compatibility")
    if compat is not None and (not isinstance(compat, str) or not (1 <= len(compat) <= COMPAT_MAX)):
        add("ERROR", "compatibility.length", f"compatibility must be 1-{COMPAT_MAX} chars")
    meta = fm.get("metadata")
    if meta is not None:
        if not isinstance(meta, dict):
            add("ERROR", "metadata.type", "metadata must be a mapping of string keys to string values")
        else:
            bad = [k for k, v in meta.items() if not isinstance(v, str)]
            if bad:
                add("WARN", "metadata.values", f"metadata values should be strings (quote them): {', '.join(map(str, bad))}")
    at = fm.get("allowed-tools")
    if at is not None and not isinstance(at, str):
        add("WARN", "allowed-tools.type", "allowed-tools is a space-separated string in the spec")

    for k in fm:
        if k in SPEC_KEYS:
            continue
        if k in CLAUDE_CODE_KEYS:
            add("INFO", "frontmatter.extension", f"'{k}' is a Claude Code extension; other clients and propose_skills may drop it")
        else:
            add("WARN", "frontmatter.unknown", f"unknown frontmatter key '{k}'")


def strip_fences(text):
    # Blank out fences instead of deleting them so line numbers still match the file.
    return re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.DOTALL)


def strip_code(text):
    return re.sub(r"`[^`\n]*`", "", strip_fences(text))


def local_links(text):
    """Relative file links: markdown links + backticked bundle paths. Code fences are ignored for both."""
    out = []
    for i, line in enumerate(strip_code(text).splitlines(), 1):
        for m in MD_LINK_RE.finditer(line):
            target = m.group(1).split("#")[0]
            if target and not re.match(r"^[a-z]+:", target) and not target.startswith("/"):
                out.append((target, line, i))
    for i, line in enumerate(strip_fences(text).splitlines(), 1):
        for m in CODE_PATH_RE.finditer(line):
            target = m.group(1).rstrip(".,:;)")
            if "<" in target or "*" in target:
                continue
            out.append((target, line, i))
    return out


def check_body(body, folder, offset=0):
    """offset = number of SKILL.md lines before the body, so reported line numbers match the file."""
    lines = body.splitlines()
    if len(lines) > BODY_MAX_LINES:
        add("WARN", "body.lines", f"SKILL.md body is {len(lines)} lines (keep under {BODY_MAX_LINES}; move detail to references/)")
    tokens = estimate_tokens(body)
    if tokens > BODY_MAX_TOKENS:
        add("WARN", "body.tokens", f"SKILL.md body is ~{tokens} tokens (spec recommends < {BODY_MAX_TOKENS})")
    if not body.strip():
        add("ERROR", "body.empty", "SKILL.md has no instructions after the frontmatter")

    prose = strip_code(body)
    shouts = SHOUT_RE.findall(prose)
    if len(shouts) > SHOUT_LIMIT:
        add("WARN", "style.shouting", f"{len(shouts)} all-caps MUST/ALWAYS/NEVER/CRITICAL; explain the reason instead")
    in_code = False
    for i, line in enumerate(body.splitlines(), 1 + offset):
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if not in_code and TIME_RE.search(line):
            add("INFO", "content.time-sensitive", "date-bound instruction; move old behaviour to an 'old patterns' section", f"SKILL.md:{i}")
        if BACKSLASH_PATH_RE.search(line):
            add("WARN", "paths.backslash", "use forward slashes in paths", f"SKILL.md:{i}")


def check_references(skill_md_text, folder):
    referenced = set()
    for target, line, lineno in local_links(skill_md_text):
        path = (folder / target).resolve()
        rel = target
        try:
            rel = str(path.relative_to(folder.resolve()))
        except ValueError:
            add("WARN", "refs.outside", f"link points outside the skill folder: {target}", f"SKILL.md:{lineno}")
            continue
        if not path.exists():
            add("ERROR", "refs.missing", f"referenced file does not exist: {target}", f"SKILL.md:{lineno}")
            continue
        referenced.add(rel)
        rest = line.replace(target, "")
        if rel.endswith(".md") and GENERIC_POINTER_RE.search(rest) and not CONDITION_RE.search(rest):
            add("INFO", "refs.when", f"say when to read {target} (e.g. 'API가 200이 아니면 읽는다')", f"SKILL.md:{lineno}")

    md_files = [p for p in folder.rglob("*.md") if p.name != "SKILL.md" and "evals" not in p.relative_to(folder).parts]
    for p in md_files:
        rel = str(p.relative_to(folder))
        text = p.read_text(encoding="utf-8", errors="replace")
        n = len(text.splitlines())
        if n > REF_TOC_LINES and not TOC_RE.search("\n".join(text.splitlines()[:40])):
            add("WARN", "refs.toc", f"{rel} has {n} lines but no table of contents near the top")
        if rel in referenced:
            for target, line, lineno in local_links(text):
                cand = (p.parent / target).resolve()
                if cand.exists() and cand.suffix == ".md" and cand.name != "SKILL.md":
                    try:
                        crel = str(cand.relative_to(folder.resolve()))
                    except ValueError:
                        continue
                    if crel not in referenced and crel != rel:
                        add("WARN", "refs.depth", f"{rel} links to {crel}, which SKILL.md does not link; keep references one level deep", f"{rel}:{lineno}")

    ignore_parts = {"evals", "__pycache__", ".git", "node_modules"}
    for p in folder.rglob("*"):
        if not p.is_file() or p.name in ("SKILL.md", "LICENSE", "LICENSE.txt", "LICENSE.md", "README.md", ".DS_Store"):
            continue
        rel_parts = p.relative_to(folder).parts
        if ignore_parts & set(rel_parts):
            continue
        rel = str(p.relative_to(folder))
        mentioned = rel in referenced or rel in skill_md_text or p.name in skill_md_text
        if not mentioned:
            add("WARN", "files.unreferenced", f"{rel} is never mentioned in SKILL.md, so the agent will not know to use it")


def check_scripts(folder):
    for p in folder.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        rel = str(p.relative_to(folder))
        src = p.read_text(encoding="utf-8", errors="replace")
        try:
            compile(src, rel, "exec")  # syntax check without writing .pyc files
        except SyntaxError as e:
            add("ERROR", "scripts.syntax", f"{rel} line {e.lineno}: {e.msg}")
            continue
        import ast
        calls_input = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "input"
                          for n in ast.walk(ast.parse(src)))
        if calls_input:
            add("WARN", "scripts.interactive", f"{rel} calls input(); agents cannot answer prompts. Take flags/stdin instead")
        if p.parent.name == "scripts" and "argparse" not in src and "sys.argv" not in src and "__main__" in src:
            add("INFO", "scripts.help", f"{rel}: give it a --help (argparse) so the agent can learn its interface")


def main():
    ap = argparse.ArgumentParser(description="Static checks for an Agent Skill folder.")
    ap.add_argument("skill_folder")
    ap.add_argument("--json", action="store_true", help="print findings as JSON")
    args = ap.parse_args()

    folder = Path(args.skill_folder).expanduser()
    skill_md = folder / "SKILL.md"
    if not skill_md.is_file():
        print(f"Error: {skill_md} not found. Pass the folder that contains SKILL.md.", file=sys.stderr)
        return 2
    folder = folder.resolve()
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    fm, body, err = parse_frontmatter(text)
    if err:
        add("ERROR", "frontmatter.parse", err)
        fm = {}
    check_frontmatter(fm, folder)
    check_yaml_comments(text)
    check_body(body, folder, offset=len(text.splitlines()) - len(body.splitlines()))
    check_references(text, folder)
    check_scripts(folder)

    counts = {lvl: sum(1 for f in findings if f["level"] == lvl) for lvl in ("ERROR", "WARN", "INFO")}
    stats = {"body_lines": len(body.splitlines()), "body_tokens_est": estimate_tokens(body),
             "description_chars": len((fm.get("description") or "").strip()) if isinstance(fm.get("description"), str) else 0}
    if args.json:
        print(json.dumps({"skill": str(folder), "counts": counts, "stats": stats, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        print(f"{folder.name}: {counts['ERROR']} ERROR, {counts['WARN']} WARN, {counts['INFO']} INFO "
              f"(body {stats['body_lines']} lines, ~{stats['body_tokens_est']} tokens, description {stats['description_chars']} chars)")
        order = {"ERROR": 0, "WARN": 1, "INFO": 2}
        for f in sorted(findings, key=lambda f: order[f["level"]]):
            where = f" [{f['where']}]" if f["where"] else ""
            print(f"{f['level']:5} {f['rule']}: {f['message']}{where}")
    return 1 if counts["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main())
