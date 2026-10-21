#!/usr/bin/env python3
"""Check repo invariants from CLAUDE.md. Run after adding, moving, or renaming a skill."""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMOTED = ("engineering", "productivity")
errors = []

skills = sorted(p.parent for p in (ROOT / "skills").glob("*/*/SKILL.md"))
promoted = {f"./{s.relative_to(ROOT)}" for s in skills if s.parent.name in PROMOTED}
manifest = set(json.loads((ROOT / ".claude-plugin/plugin.json").read_text())["skills"])
readme = (ROOT / "README.md").read_text()

for path in sorted(promoted - manifest):
    errors.append(f"plugin.json skills 배열에 없음: {path}")
for path in sorted(manifest - promoted):
    errors.append(f"plugin.json에 있지만 승격 버킷의 스킬이 아님: {path}")

for s in skills:
    rel = s.relative_to(ROOT)
    m = re.search(r"^name:\s*(\S+)", (s / "SKILL.md").read_text(), re.M)
    if not m or m.group(1) != s.name:
        errors.append(f"frontmatter name이 폴더 이름과 다름: {rel}")
    if f"./{s.name}/SKILL.md" not in (ROOT / "skills" / s.parent.name / "README.md").read_text():
        errors.append(f"버킷 README에 링크 없음: {rel}")
    if s.parent.name in PROMOTED and f"{rel}/SKILL.md" not in readme:
        errors.append(f"최상위 README에 링크 없음: {rel}")

if subprocess.run(["claude", "plugin", "validate", str(ROOT), "--strict"]).returncode:
    errors.append("claude plugin validate --strict 실패")

print("\n".join(errors) or f"OK: 스킬 {len(skills)}개, 승격 {len(promoted)}개")
sys.exit(1 if errors else 0)
