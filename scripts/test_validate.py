#!/usr/bin/env python3
"""Self-check for validate.py: builds a throwaway repo with known defects and asserts each rule ID fires.

Run: python3 test_validate.py
"""
import json, subprocess, sys, tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("validate.py")

FILES = {
    ".claude-plugin/plugin.json": '{"name": "t", "skills": ["./skills/engineering/good"]}',
    "README.md": "## User-invoked\n- [good](docs/skills/good.md) [SKILL.md](skills/engineering/good/SKILL.md)\n",
    "README.en.md": "- [good](docs/en/skills/good.md)\n",
    "docs/README.md": "- [good](skills/good.md)\n",
    "docs/en/README.md": "- [good](skills/good.md)\n",
    "docs/skills/good.md": "# good\n",
    "docs/en/skills/good.md": "# good\n",
    "skills/engineering/README.md": "## User-invoked\n- [good](./good/SKILL.md)\n- [bad](./bad/SKILL.md)\n",
    "skills/engineering/good/SKILL.md": "---\nname: good\ndescription: 좋은 스킬을 요약한다.\ndisable-model-invocation: true\n---\n\n본문. [ref](ref.md)\n",
    "skills/engineering/good/ref.md": "참조.\n",
    "evals/good/case.yaml": "x: 1\n",
    "skills/engineering/bad/SKILL.md": (
        "---\nname: Bad_Claude\ndescription: <b>You can</b> use this\ndisable-model-invokation: true\n"
        "effort: huge\n---\n\n[x](missing.md) [y](../good/SKILL.md) [z](a.md)\nC:\\dir\\file.txt\n2025년 8월 이후에는 다르게 한다.\n"
        "Skill 도구로 `good`을 호출한다.\nMUST MUST MUST MUST\n"
    ),
    "skills/engineering/bad/a.md": "[b](b.md)\n",
    "skills/engineering/bad/b.md": "\n" * 120,
    "skills/engineering/broken/SKILL.md": "---\nname: broken\ndescription: [unclosed\n---\n",
    "skills/engineering/nofm/SKILL.md": "frontmatter 없음\n",
    "skills/stray/SKILL.md": "---\nname: stray\ndescription: x\n---\n",
}


def ids(out, skill):
    r = next(s for s in out["skills"] if s["name"] == skill)
    return {x["id"] for x in r["errors"] + r["warnings"]}


with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    for rel, body in FILES.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(body, encoding="utf-8")
    run = subprocess.run([sys.executable, str(SCRIPT)], cwd=root, capture_output=True, text=True)
    out = json.loads(run.stdout)

    assert run.returncode == 1
    assert ids(out, "good") == set(), ids(out, "good")
    bad = ids(out, "bad")
    for rule in ("E3", "E4", "E5", "E6", "E7", "E8", "E9", "E12", "E13", "E14", "W3", "W4", "W5", "W6", "W7", "W11", "W12"):
        assert rule in bad, (rule, bad)
    assert ids(out, "broken") == {"E2"}, ids(out, "broken")
    assert "E1" in ids(out, "nofm")
    repo_ids = {x["id"] for x in out["repo_findings"]}
    assert "E11" in repo_ids, repo_ids

    one = json.loads(subprocess.run([sys.executable, str(SCRIPT), "good"], cwd=root, capture_output=True, text=True).stdout)
    assert [s["name"] for s in one["skills"]] == ["good"]
    print("OK")
