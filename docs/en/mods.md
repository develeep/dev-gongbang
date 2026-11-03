<p align="right"><a href="../mods.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › Mods

# Mods

`gongbang-mods` is a bundle of mods that restyle the Claude Code terminal. A mod is a plugin that hooks into Claude Code's screen and behavior. This page covers how `gongbang-mods` changes the screen, how to install and turn it off, and which outside mods pair well with it.

## Contents

- [Installation](#installation)
- [What changes on screen](#what-changes-on-screen)
- [Good to know](#good-to-know)
- [Turning it off and updating](#turning-it-off-and-updating)
- [Outside mods that pair well](#outside-mods-that-pair-well)
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

## Credits

The Session pane is adapted from `context-bar` and `where-am-i` in [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods): what they drew above the prompt moved into one side pane. The originals are MIT licensed; the full license text is in `mods/gongbang-mods/hooks/session/LICENSE`.

---

[← All docs](README.md)
