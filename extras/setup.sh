#!/usr/bin/env bash
# Sets up the dev-gongbang terminal environment on this machine:
# gongbang-mods, the recommended outside mods, the status line and the fullscreen layout.
# Safe to run again: steps already done are skipped. Uses CLAUDE_CONFIG_DIR when set.
#
#   extras/setup.sh
#   CLAUDE_CONFIG_DIR=/path/to/test-config extras/setup.sh   # try it without touching ~/.claude
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
mkdir -p "$CONFIG"

MARKETPLACES=(
  develeep/dev-gongbang
  hamzafer/claude-code-mods
  YeonwooSung/my-claude-code-mods
)
PLUGINS=(
  gongbang-mods@dev-gongbang
  mission-control@claude-code-mods
  next-steps@claude-code-mods
  blast-radius@claude-code-mods
  agent-radar@claude-code-mods
  loop-detective@my-claude-code-mods
  context-inspector@my-claude-code-mods
)

step() { printf '\n== %s\n' "$1"; }

step "Marketplaces"
known="$(claude plugin marketplace list 2>&1)"
for m in "${MARKETPLACES[@]}"; do
  if grep -qF "($m)" <<<"$known"; then echo "already added: $m"; else claude plugin marketplace add "$m"; fi
done

step "Plugins"
installed="$(claude plugin list 2>&1)"
for p in "${PLUGINS[@]}"; do
  if grep -qF "❯ $p" <<<"$installed"; then echo "already installed: $p"; else claude plugin install "$p"; fi
done

step "next-steps in Korean"
echo '{"language":"Korean"}' | claude plugin configure next-steps@claude-code-mods --values-stdin

step "Status line"
ln -sfn "$REPO/extras/statusline/statusline.py" "$CONFIG/statusline.py"
echo "linked $CONFIG/statusline.py -> $REPO/extras/statusline/statusline.py"

step "settings.json: fullscreen layout and status line"
python3 - "$CONFIG/settings.json" "$CONFIG/statusline.py" <<'PY'
import json, os, shutil, sys
path, script = sys.argv[1], sys.argv[2]
settings = json.load(open(path)) if os.path.exists(path) else {}
wanted = {
    "tui": "fullscreen",  # side panes dock beside the transcript only in this layout
    "statusLine": {"type": "command", "command": f"python3 {script}"},
}
changed = {k: v for k, v in wanted.items() if settings.get(k) != v}
if not changed:
    print("already set")
    sys.exit(0)
if os.path.exists(path):
    shutil.copy(path, path + ".bak")
    print(f"backed up {path}.bak")
settings.update(changed)
with open(path, "w") as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
    f.write("\n")
for k in changed:
    print(f"set {k}")
PY

step "Done"
echo "Restart Claude Code."
