#!/usr/bin/env python3
"""Package a skill folder as <name>.skill (a zip with the folder at its root).

Usage:
  python3 scripts/package.py <skill-folder> [out-dir] [--no-evals]

Runs check_skill.py first and refuses to package while it reports an ERROR.
Skips __pycache__, .DS_Store, *-workspace folders and evals/results.
Prints the written path as JSON. Exit 0 ok, 1 check failed, 2 bad arguments.
Standard library only.
"""

import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path

SKIP_PARTS = {"__pycache__", ".git", "node_modules", ".DS_Store"}


def main():
    ap = argparse.ArgumentParser(description="Package a skill folder as a .skill file.")
    ap.add_argument("skill_folder")
    ap.add_argument("out_dir", nargs="?", default=".", help="where to write <name>.skill (default: current dir)")
    ap.add_argument("--no-evals", action="store_true", help="leave out the evals/ folder")
    args = ap.parse_args()

    folder = Path(args.skill_folder).expanduser().resolve()
    if not (folder / "SKILL.md").is_file():
        print(f"Error: {folder}/SKILL.md not found", file=sys.stderr)
        return 2
    check = subprocess.run([sys.executable, str(Path(__file__).with_name("check_skill.py")), str(folder)],
                           capture_output=True, text=True)
    if check.returncode != 0:
        print(check.stdout + check.stderr, file=sys.stderr)
        print("Error: fix the ERROR findings above before packaging.", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{folder.name}.skill"
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob("*")):
            rel = p.relative_to(folder)
            if not p.is_file() or SKIP_PARTS & set(rel.parts) or p.name == ".DS_Store":
                continue
            if rel.parts[0] == "evals" and (args.no_evals or (len(rel.parts) > 1 and rel.parts[1] == "results")):
                continue
            z.write(p, Path(folder.name) / rel)
            count += 1
    print(json.dumps({"package": str(out), "files": count}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
