#!/usr/bin/env python3
"""Check repo invariants from AGENTS.md. Run after changing a skill or a mod. Needs PyYAML."""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rules = subprocess.run([sys.executable, ROOT / "scripts/validate.py"], cwd=ROOT)
protected = subprocess.run([sys.executable, ROOT / "scripts/test_protected_paths.py"], cwd=ROOT)
plugin = subprocess.run(["claude", "plugin", "validate", str(ROOT), "--strict"])
codes = [rules.returncode, protected.returncode, plugin.returncode]
# omp extension 테스트는 bun이 있어야 돈다. CI는 bun을 설치해 늘 돌린다.
if shutil.which("bun"):
    codes.append(subprocess.run(["bun", "test", "extras/omp/extensions"], cwd=ROOT).returncode)
else:
    print("bun이 없어 extras/omp/extensions 테스트를 건너뛰었다", file=sys.stderr)
# mod 매니페스트는 marketplace.json 항목에만 둔다. 루트 플러그인 안에 plugin.json이 중첩되면
# claude.ai 동기화가 gongbang을 거부하므로, 검사할 때만 임시 복사본에 plugin.json을 만든다.
entries = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))["plugins"]
for e in entries:
    if not e["source"].startswith("./mods/"):
        continue
    with tempfile.TemporaryDirectory() as tmp:
        m = Path(tmp) / e["name"]
        shutil.copytree(ROOT / e["source"], m, ignore=shutil.ignore_patterns(".claude-plugin"))
        (m / ".claude-plugin").mkdir()
        manifest = {k: v for k, v in e.items() if k not in ("source", "category", "strict")}
        (m / ".claude-plugin/plugin.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        codes.append(subprocess.run(["claude", "plugin", "validate", str(m)]).returncode)
        if (m / "tests").is_dir():
            codes.append(subprocess.run(["claude", "plugin", "test", str(m)]).returncode)
sys.exit(next((c for c in codes if c), 0))
