<p align="right"><a href="../mods.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › Mods

# Mods

`gongbang-mods` is a bundle of mods that restyle the Claude Code terminal. A mod is a plugin that hooks into Claude Code's screen and behavior. This page covers how `gongbang-mods` changes the screen, how to install and turn it off, which outside mods pair well with it, and the status line script installed separately.

## Contents

- [Installation](#installation)
- [What changes on screen](#what-changes-on-screen)
- [Good to know](#good-to-know)
- [Turning it off and updating](#turning-it-off-and-updating)
- [Outside mods that pair well](#outside-mods-that-pair-well)
- [Status line](#status-line)
- [Same setup on another computer](#same-setup-on-another-computer)
- [Credits](#credits)

## Installation

Needs Claude Code 2.1.287 or later. Add the marketplace, install `gongbang-mods`, and restart Claude Code.

```bash
claude plugin marketplace add develeep/dev-gongbang
claude plugin install gongbang-mods@dev-gongbang
```

It installs and turns off separately from the `gongbang` skills plugin.

## What changes on screen

### Tool calls folded to one line

Each tool call and its result fold into one line, such as `✓ Bash git status`. The leading mark is the status.

| Mark | Meaning |
|---|---|
| `…` (yellow) | running |
| `✓` (green) | succeeded |
| `✗` (red) | errored |
| `⏹` (yellow) | interrupted |

The result block is hidden. `ctrl+o` or `--verbose` shows everything as before. Lines the engine already groups, such as `Read 3 files`, are left alone.

### Card-style messages and Markdown

Your messages go in a rounded card titled `● You`, and Claude's replies in a card titled `◆ Claude`. The colors follow the theme's `suggestion` (yours) and `claude` (replies) keys, so they adapt to light and dark themes.

Inside a reply card, some Markdown is drawn by hand:

- Headings: bold, marked by level with `█` (underlined), `▌` or `▸`.
- Code blocks: in a light bordered box with the language name on top.
- Quotes: italic, with a `┃` bar on the left.
- Rules: a thin line as wide as the card.

Tables, lists, checkboxes and plain paragraphs are drawn by the engine as before. Background task notifications and messages from other agents keep their usual look.

### Session pane

One side pane shows the session goal and context usage together.

- **Goal**: the session goal, what is happening now (`now`), what comes next (`next`), and what waits on you (`waiting on you`)
- **Context**: percent used, tokens in use and the auto-compaction point, a stacked bar by category, and tokens per category

Both fill in after the first turn.

With the [pokemon mod](https://github.com/dgokcin/claude-pokemon-mod), the same session view is also drawn at the top of the pane `/pokemon pane` opens. Only one pane shows at a time (the others become tabs), so this keeps the session and the mon in view together. The mon is drawn in the room left under the session view, and the separate `Session` tab can be closed.

If the mon is cut off at the bottom, shrink it to half size with `/pokemon size small`. That size is recommended alongside the session view.

| Command | What it does |
|---|---|
| `/session-pane` | Opens the Session pane |
| `/where` | Recaps the session so far in a few lines |

## Good to know

- **Uses Claude usage**: the Goal is written by one Haiku call at the end of each turn. `/where` also calls Haiku.
- **Pane placement**: the pane opens on the right at session start when the terminal is wide enough. If it is too narrow, widen the window and type `/session-pane`. Docking on the right works in the fullscreen layout only.
- **Overlaps with other mods that redraw the screen**: with another mod that redraws messages or tool rows, only one of the two looks may show.
- **Shows in Claude Code's own screens only**: where another app runs Claude Code through the SDK, the hooks run but nothing they draw shows.

## Turning it off and updating

```bash
claude plugin disable gongbang-mods@dev-gongbang   # turn off
claude plugin enable gongbang-mods@dev-gongbang    # turn back on
claude plugin marketplace update dev-gongbang
claude plugin update gongbang-mods@dev-gongbang    # update
```

After turning it off or updating, restart Claude Code or type `/reload-plugins`.

## Outside mods that pair well

These mods are made by other people and are not part of this repository. Install them from their own repositories, and read the code before you do.

[hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods):

- **mission-control**: a live pane of subagents, tool calls and the files being edited. Open it with `/mission`. Calls Haiku once per turn.
- **next-steps**: after each turn, suggests 2 or 3 prompts you might send next. Pick one with a number key in an empty prompt. To get suggestions in Korean, set its `language` option to `Korean`.
- **blast-radius**: holds risky Bash commands such as `rm -r`, shows the files they would delete, and asks before running. By default it cancels the command after 60 seconds without an answer.
- **agent-radar**: one live line per running subagent or background shell.

```bash
claude plugin marketplace add hamzafer/claude-code-mods
claude plugin install mission-control@claude-code-mods
claude plugin install next-steps@claude-code-mods
claude plugin install blast-radius@claude-code-mods
claude plugin install agent-radar@claude-code-mods
echo '{"language":"Korean"}' | claude plugin configure next-steps@claude-code-mods --values-stdin
```

While `next-steps` shows its list, the Session pane hides its own `next` item so the same thing does not show twice.

[YeonwooSung/my-claude-code-mods](https://github.com/YeonwooSung/my-claude-code-mods):

- **loop-detective**: flags and records a Bash command that keeps failing the same way. See it with `/loop-report` or `/loop-pane`.
- **context-inspector**: finds waste in the context window, such as files read again and near-duplicate outputs. See it with `/context-inspect` or `/context-pane`.

```bash
claude plugin marketplace add YeonwooSung/my-claude-code-mods
claude plugin install loop-detective@my-claude-code-mods
claude plugin install context-inspector@my-claude-code-mods
```

[dgokcin/claude-pokemon-mod](https://github.com/dgokcin/claude-pokemon-mod):

- **pokemon**: a pixel Pokémon above the prompt that reacts to what Claude does. Moved to the side pane with `/pokemon pane`, it shares the pane with the session view. The repository has no license, so none of its code is included here.

```bash
claude plugin marketplace add dgokcin/claude-pokemon-mod
claude plugin install pokemon@claude-pokemon
```

Don't install `context-bar` or `where-am-i` from the hamzafer repository: they show the same information as the Session pane again above the prompt.

## Status line

`extras/statusline/statusline.py` is a script that restyles the status line under the prompt. A plugin can't change a person's `statusLine` setting, so it lives apart from `gongbang-mods`.

```
~/dev-gongbang │ ◆ Opus 5.5 medium │ ⎇ master* │ 5h ▱▱▱▱▱ 5% ↻3h11m  7d ▰▰▰▰▱ 72% ↻2d7h │ cache 39m │ $5.79
```

| Item | Meaning |
|---|---|
| `~/dev-gongbang` | working folder |
| `◆ Opus 5.5 medium` | model and effort. Effort is left out on models without it |
| `⎇ master*` | git branch. `*` means uncommitted changes. Clicking it opens the branch on GitHub |
| `5h`, `7d` | plan usage for the 5-hour and weekly limits, and time until each resets. Clicking it opens the claude.ai usage page. Shows on a subscription after the first reply |
| `cache 39m` | time left before the prompt cache expires. A longer pause rebuilds the cache on the next request |
| `$5.79` | session cost |

Usage turns yellow at 70% and red at 90%.

### Installation

Needs Python 3 and git. From your clone of the repository, link the script and add `statusLine` to `~/.claude/settings.json`.

```bash
ln -s "$PWD/extras/statusline/statusline.py" ~/.claude/statusline.py
```

```json
{
  "statusLine": { "type": "command", "command": "python3 ~/.claude/statusline.py" }
}
```

You can copy it (`cp`) instead of linking. A link follows the repository on `git pull`; a copy keeps your own edits.

### Good to know

- The branch and usage links are clickable only in terminals that support OSC 8. If the status line shows text like `]8;;https://…`, set `LINKS = True` to `False` in the script.
- The status line redraws when Claude Code updates its state. The times left are computed at that moment.

## Same setup on another computer

`extras/setup.sh` sets up the mod environment on this page in one go. Run it from a clone of the repository, then restart Claude Code.

```bash
git clone https://github.com/develeep/dev-gongbang && cd dev-gongbang
extras/setup.sh
```

What the script does, skipping any step already done, so it is safe to run again:

- Adds four marketplaces and installs `gongbang-mods` and the seven [outside mods](#outside-mods-that-pair-well).
- Sets `next-steps` to suggest in Korean.
- Links the status line script to `~/.claude/statusline.py`.
- Puts `"tui": "fullscreen"` and `statusLine` in `~/.claude/settings.json`, keeping the previous file as `settings.json.bak`. Side panes dock on the right only in the fullscreen layout.

pokemon keeps its settings inside the plugin, so the script can't set them. After restarting Claude Code, type these once:

```
/pokemon charmander     pick a starter (Bulbasaur, Charmander, Squirtle, Pikachu)
/pokemon pane           move it into the side pane
/pokemon size small     so it fits under the session view
/pokemon images on      only in a terminal that draws images (kitty, Ghostty, WezTerm, Orca)
```

To try it first without touching your current setup, point the config folder at an empty one. Check the result with `CLAUDE_CONFIG_DIR=<folder> claude plugin list`.

```bash
CLAUDE_CONFIG_DIR="$HOME/.cache/claude-test" extras/setup.sh
```

The script doesn't set up what differs per computer, such as the terminal app, fonts or Chrome.

## Credits

The Session pane is adapted from `context-bar` and `where-am-i` in [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods): what they drew above the prompt moved into one side pane. The originals are MIT licensed; the full license text is in `mods/gongbang-mods/hooks/session/LICENSE`.

---

[← All docs](README.md)
