#!/usr/bin/env python3
"""Check repo invariants from CLAUDE.md. Run after changing a skill or a mod. Needs PyYAML."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rules = subprocess.run([sys.executable, ROOT / "scripts/validate.py"], cwd=ROOT)
plugin = subprocess.run(["claude", "plugin", "validate", str(ROOT), "--strict"])
mods = [m for m in sorted((ROOT / "mods").glob("*")) if (m / ".claude-plugin/plugin.json").is_file()]
codes = [rules.returncode, plugin.returncode]
for m in mods:
    codes.append(subprocess.run(["claude", "plugin", "validate", str(m)]).returncode)
    if (m / "tests").is_dir():
        codes.append(subprocess.run(["claude", "plugin", "test", str(m)]).returncode)
sys.exit(next((c for c in codes if c), 0))
