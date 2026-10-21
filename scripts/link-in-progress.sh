#!/usr/bin/env bash
# Link skills/in-progress/* into a skills dir so edits apply immediately.
# Usage: scripts/link-in-progress.sh [--project] [--remove]
#   default    ~/.claude/skills (user scope)
#   --project  ./.claude/skills of the current directory (project scope)
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)/skills/in-progress"
DEST="$HOME/.claude/skills"
REMOVE=false
PROJECT=false
for arg in "$@"; do
  case "$arg" in
    --project) PROJECT=true; DEST="$PWD/.claude/skills" ;;
    --remove) REMOVE=true ;;
    *) echo "알 수 없는 옵션: $arg" >&2; exit 1 ;;
  esac
done
mkdir -p "$DEST"

# Project-scope links hold absolute local paths, so keep them out of that repo's commits.
EXCLUDE=""
if $PROJECT && git -C "$PWD" rev-parse --git-dir >/dev/null 2>&1; then
  EXCLUDE="$(git -C "$PWD" rev-parse --path-format=absolute --git-path info/exclude)"
  PREFIX="$(git -C "$PWD" rev-parse --show-prefix)"
  mkdir -p "$(dirname "$EXCLUDE")"
fi

for dir in "$SRC"/*/; do
  name="$(basename "$dir")"
  target="$DEST/$name"
  if $REMOVE; then
    # Only remove links that point back into this repo.
    if [[ -L "$target" && "$(readlink "$target")" == "$SRC/$name" ]]; then
      rm "$target" && echo "제거: $name"
    fi
  elif [[ -e "$target" && ! -L "$target" ]]; then
    echo "건너뜀: $target 이 이미 있음 (링크 아님)" >&2
  else
    ln -sfn "$SRC/$name" "$target" && echo "연결: $name"
    if [[ -n "$EXCLUDE" ]]; then
      entry="/${PREFIX}.claude/skills/$name"
      grep -qxF "$entry" "$EXCLUDE" 2>/dev/null || echo "$entry" >> "$EXCLUDE"
    fi
  fi
done
