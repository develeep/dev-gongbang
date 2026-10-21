#!/usr/bin/env bash
# Link skills/in-progress/* into ~/.claude/skills so edits apply immediately.
# Usage: scripts/link-in-progress.sh [--remove]
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)/skills/in-progress"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$DEST"

for dir in "$SRC"/*/; do
  name="$(basename "$dir")"
  target="$DEST/$name"
  if [[ "${1:-}" == "--remove" ]]; then
    # Only remove links that point back into this repo.
    if [[ -L "$target" && "$(readlink "$target")" == "$SRC/$name" ]]; then
      rm "$target" && echo "제거: $name"
    fi
  elif [[ -e "$target" && ! -L "$target" ]]; then
    echo "건너뜀: $target 이 이미 있음 (링크 아님)" >&2
  else
    ln -sfn "$SRC/$name" "$target" && echo "연결: $name"
  fi
done
