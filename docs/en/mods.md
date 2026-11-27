<p align="right"><a href="../mods.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › Mods

# Mods

With `gongbang-mods` installed, the Claude Code terminal folds each tool call to one line, splits your messages and replies into cards, and shows the session goal and context usage in a side pane. During a run-flow flow it stops write tools from editing files on the protected list. A mod is a plugin that hooks into Claude Code's screen and behavior. After reading this page, you can install, check, and turn off `gongbang-mods`, install the outside mods that pair well with it and the status line script, and set up the same environment on another computer with `extras/setup.sh`.

## Contents

- [Installation](#installation)
- [Check the setup](#check-the-setup)
- [What changes on screen](#what-changes-on-screen)
- [run-flow protected path blocking](#run-flow-protected-path-blocking)
- [Good to know](#good-to-know)
- [Turning it off and updating](#turning-it-off-and-updating)
- [Outside mods that pair well](#outside-mods-that-pair-well)
- [Status line](#status-line)
- [Same setup on another computer](#same-setup-on-another-computer)
- [Credits](#credits)

## Installation

Add the marketplace, install `gongbang-mods`, and restart Claude Code.

```bash
claude plugin marketplace add develeep/dev-gongbang
claude plugin install gongbang-mods@dev-gongbang
```

It installs and turns off separately from the `gongbang` skills plugin. To set up the outside mods and the status line in the same go, run `extras/setup.sh` as described in [Same setup on another computer](#same-setup-on-another-computer).

## Check the setup

- `claude plugin list` shows `gongbang-mods@dev-gongbang`
- In a new session, tool calls show as one line, such as `✓ Bash git status`
- Typing `/session-pane` opens the Session pane

## What changes on screen

### Tool calls folded to one line

Each tool call and its result fold into one line, such as `✓ Bash git status`. The line shows the status mark, the tool name, and the first line of the input (a command, file path, search pattern, and so on).

| Mark | Meaning |
|---|---|
| `…` (yellow) | running |
| `✓` (green) | succeeded |
| `✗` (red) | errored |
| `⏹` (yellow) | interrupted |

The result block is hidden. `ctrl+o` or `--verbose` unfolds everything as before. Lines where the engine already groups several calls, such as `Read 3 files`, are left alone.

### Card-style messages and Markdown

Messages you send from the prompt go in a rounded card titled `● You`, and Claude's replies in a card titled `◆ Claude`. When a tool call comes in the middle of a reply, the reply splits into several cards and only the first carries the title. The colors follow the theme's `suggestion` (yours) and `claude` (replies) keys, so they adapt to light and dark themes.

Inside a reply card, some Markdown is drawn by hand:

- Headings: bold, marked by level with `█` (underlined), `▌` or `▸`.
- Code blocks: in a light bordered box with the language name on top.
- Quotes: italic, with a `┃` bar on the left.
- Rules: a thin line as wide as the card.

Tables, lists, checkboxes and plain paragraphs are drawn by the engine as before. Background task notifications and messages from other agents keep their usual look.

### Session pane

One side pane shows the session goal and context usage together.

- **Goal**: the session goal, what is happening now (`now`), what comes next (`next`), and what waits on you (`waiting on you`). Haiku rewrites it at the end of each turn. While a turn runs, `now` shows the tool Claude is calling, such as `editing hooks/register.tsx`.
- **Context**: percent used, tokens in use and the auto-compaction point, a stacked bar by category, and tokens and share per category. The percent badge turns yellow when tokens in use reach 70% of the auto-compaction point (of the context window if auto-compaction is off) and red at 90%. If `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` is set, the compaction point shown takes it into account.

The Goal fills in after the first turn. The Context is read again at session start, at the end of each turn, and after `/compact` and `/clear`.

| Command | What it does |
|---|---|
| `/session-pane` | Opens the Session pane |
| `/where` | Recaps the session so far from the recent conversation, in at most six bullets |

At session start the pane opens by itself when the terminal is at least 144 columns wide, or 110 if you opened it before and have not closed it by hand since. In a narrower terminal it waits until you widen the window. `/session-pane` opens the pane at any width: beside the transcript in the fullscreen layout from 110 columns, otherwise above the prompt. Close the pane with its close mark or `ctrl+x x`.

## run-flow protected path blocking

In a repository with an active run-flow flow, when Write, Edit, or NotebookEdit targets a file on the protected list, the call is refused before the tool runs and the reason goes back to the model. The protected list holds the tests at the HEAD where stage 5 started, judge cases, accepted tests, and the list file itself. Subagent calls are covered the same way. The list and when it is on are described in [run-flow's protected list](skills/run-flow.md#protected-list).

- If the repository the target lands in has no active list, it does nothing and does not run `python3`. An active list is a `docs/context/run-flow/*.protected` whose state file's `- 현재 단계:` (current stage) is not `완료` (done). A missing state file also counts as active. Work outside a flow, finished flows, and repositories that do not use run-flow are not affected.
- If an active list exists, it runs the bundled `hooks/protected_paths.py` with `python3` to decide. That file is a copy of run-flow's `scripts/protected_paths.py`. Relative paths, absolute paths, symlinks, and paths in git worktrees inside the repository are resolved to their real path before comparing. New files and files off the list are written as usual.
- If it cannot decide (no `python3`, or the list cannot be read), it refuses the write.
- Writes through shell commands such as Bash are not blocked. run-flow catches them with `protected_paths.py verify` before it accepts a ticket.

In a clone of the repository, `claude plugin test mods/gongbang-mods` and `python3 scripts/test_protected_paths.py` check this behavior.

## Good to know

- **Uses Claude usage**: the Goal is written by one Haiku call at the end of each turn. `/where` also calls Haiku.
- **Overlaps with other mods that redraw the screen**: with another mod that redraws messages or tool rows, only one of the two looks may show.
- **Shows in the Claude Code terminal only**: in a `claude -p` run, or where another app runs Claude Code through the SDK, the hooks run but nothing is drawn.

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
| `⎇ master*` | git branch. `*` means uncommitted changes in tracked files. Clicking it opens the branch page of the `origin` remote |
| `5h`, `7d` | plan usage for the 5-hour and weekly limits, and time until each resets. Clicking it opens the claude.ai usage page. Shows on a subscription after the first reply |
| `cache 39m` | time left before the prompt cache expires. A longer pause rebuilds the cache on the next request |
| `$5.79` | session cost |

Usage turns yellow at 70% and red at 90%.

### Installation

Needs Python 3. Without git, or in a folder that is not a git repository, the branch item is left out. From your clone of the repository, link the script and add `statusLine` to `~/.claude/settings.json`.

```bash
ln -s "$PWD/extras/statusline/statusline.py" ~/.claude/statusline.py
```

```json
{
  "statusLine": { "type": "command", "command": "python3 ~/.claude/statusline.py" }
}
```

You can copy it (`cp`) instead of linking. A link follows the repository on `git pull`; a copy keeps your own edits. After you restart Claude Code, the status line shows under the prompt.

### Good to know

- The branch and usage links are clickable only in terminals that support OSC 8. If the status line shows text like `]8;;https://…`, set `LINKS = True` to `False` in the script.
- The status line redraws when Claude Code updates its state. The times left are computed at that moment.

## Same setup on another computer

`extras/setup.sh` sets up the mod environment on this page in one go. It needs the Claude Code CLI (`claude`) and Python 3. Run it from a clone of the repository, then restart Claude Code.

```bash
git clone https://github.com/develeep/dev-gongbang && cd dev-gongbang
extras/setup.sh
```

The script does the following, in order:

1. Adds three marketplaces (`develeep/dev-gongbang`, `hamzafer/claude-code-mods`, `YeonwooSung/my-claude-code-mods`) and installs `gongbang-mods` and the six [outside mods](#outside-mods-that-pair-well).
2. Sets `next-steps` to suggest in Korean.
3. Links the status line script to `~/.claude/statusline.py`.
4. Puts `"tui": "fullscreen"` and `statusLine` in `~/.claude/settings.json`. The Session pane docks beside the transcript only in the fullscreen layout.

It skips marketplaces already added and plugins already installed, and changes `settings.json` only when the two values differ, so it is safe to run again. Before changing `settings.json`, it keeps the previous file as `settings.json.bak`.

To try it first without touching your current setup, point `CLAUDE_CONFIG_DIR` at an empty folder. The plugins, the status line link, and `settings.json` all go into that folder. Check the result with `CLAUDE_CONFIG_DIR=<folder> claude plugin list`.

```bash
CLAUDE_CONFIG_DIR="$HOME/.cache/claude-test" extras/setup.sh
```

The script doesn't set up what differs per computer, such as the terminal app, fonts or Chrome.

## Credits

The Session pane is adapted from `context-bar` and `where-am-i` in [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods): what they drew above the prompt moved into one side pane. The originals are MIT licensed; the full license text is in `mods/gongbang-mods/hooks/session/LICENSE`.

---

[All docs](README.md) · [README](../../README.en.md)
