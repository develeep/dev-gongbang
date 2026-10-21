#!/usr/bin/env python3
"""Check repo invariants from CLAUDE.md. Run after adding, moving, or renaming a skill. Needs PyYAML."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# ponytail: repo rules live only in skill-reviewer's validate.py. Update this path when skill-reviewer is promoted.
rules = subprocess.run([sys.executable, ROOT / "skills/in-progress/skill-reviewer/scripts/validate.py"], cwd=ROOT)
plugin = subprocess.run(["claude", "plugin", "validate", str(ROOT), "--strict"])
sys.exit(rules.returncode or plugin.returncode)
