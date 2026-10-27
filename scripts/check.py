#!/usr/bin/env python3
"""Check repo invariants from CLAUDE.md. Run after adding, moving, or renaming a skill. Needs PyYAML."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rules = subprocess.run([sys.executable, ROOT / "scripts/validate.py"], cwd=ROOT)
plugin = subprocess.run(["claude", "plugin", "validate", str(ROOT), "--strict"])
sys.exit(rules.returncode or plugin.returncode)
