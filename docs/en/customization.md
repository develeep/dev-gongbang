<p align="right"><a href="../customization.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › Customizing skills

# Customizing skills

This page explains how to copy dev-gongbang skills and edit them to fit your team rules, the models you use, and your document formats. After reading it, you will know where to copy a skill, which files to edit, and how to check and test the edited skill.

## Contents

- [Choose where to edit](#choose-where-to-edit)
- [Copy and edit a skill](#copy-and-edit-a-skill)
- [Files to edit per skill](#files-to-edit-per-skill)
- [Change the invocation type](#change-the-invocation-type)
- [Check a modified skill](#check-a-modified-skill)
- [Test a modified skill](#test-a-modified-skill)
- [Use in-progress skills via links](#use-in-progress-skills-via-links)
- [Contributing](#contributing)

## Choose where to edit

Do not edit the skill files installed by the plugin. The plugin is installed in a per-version folder such as `~/.claude/plugins/cache/dev-gongbang/gongbang/<version>/`, so when you update to a new version, your edits do not carry over to the new folder.

To edit a skill, copy its folder to one of the two locations below.

| Location | Scope | Name to run |
|---|---|---|
| `~/.claude/skills/<skill-name>/` | All projects | `/<skill-name>` |
| `<project>/.claude/skills/<skill-name>/` | That project. Commit it and your team shares it | `/<skill-name>` |

Run a copy without the `gongbang:` prefix. If the plugin is also installed, the same skill is registered twice: `/gongbang:<skill-name>` and `/<skill-name>`. For a Model-invoked skill, both become candidates for Claude to pick, so to use only the copy, uninstall the plugin or rename the copy.

## Copy and edit a skill

1. Clone the repository.

   ```bash
   git clone https://github.com/develeep/dev-gongbang.git
   ```

2. Copy the whole skill folder you want to edit. Bundled files (`reference/`, `templates/`, `scripts/`) must come along too. The command below copies write-docs as a user skill.

   ```bash
   cp -r dev-gongbang/skills/productivity/write-docs ~/.claude/skills/
   ```

3. To rename the skill, change the folder name and the `name` in the `SKILL.md` frontmatter to the same value. If they differ, the check reports an error.
4. Edit the files. The files commonly edited for each skill are listed in [Files to edit per skill](#files-to-edit-per-skill).
5. [Check the edited skill](#check-a-modified-skill) and start a new session.

## Files to edit per skill

Paths are relative to the skill folder. Details are in the "Customize" section of each skill page.

| Skill | File to edit | What changes |
|---|---|---|
| [prompt-builder](skills/prompt-builder.md) | `reference/models/<model>.md` | Per-model guide. If you add a new model, also add a row to the "모델 ID 패턴" (Model ID pattern) table in SKILL.md |
| | `reference/interview.md` | Interview items and quick mode defaults |
| [building-skills](skills/building-skills.md) | `references/authoring-rules.md` | Skill authoring rules and the human review checklist |
| | `scripts/check_skill.py` | Rules checked by machine |
| [write-docs](skills/write-docs.md) | `reference/tech-writing.md` | Technical document types, recommended structure, sentence principles. The default is the Toss technical writing guide |
| | `reference/clear-writing.md` | Principles applied to every field |
| [set-guidelines](skills/set-guidelines.md) | `reference/guides-index.md` | List of guides and tools to recommend |
| | `templates/rule.md`, `templates/agent-instructions.md` | Rule file and CLAUDE.md/AGENTS.md templates |
| [check-guidelines](skills/check-guidelines.md) | `templates/report.md` | Report template |
| [framing-problems](skills/framing-problems.md) | `SKILL.md` | Items to fill (R1–R6) and question format |
| [analyzing-requirements](skills/analyzing-requirements.md) | `SKILL.md` | Document template |
| [set-brief](skills/set-brief.md) | `SKILL.md` | Brief template, save path |
| [set-ticket](skills/set-ticket.md) | `SKILL.md` | Ticket template, splitting criteria |
| [run-ticket](skills/run-ticket.md) | `SKILL.md` | Ticket selection rules, review order, completion record |

set-brief, set-ticket, and run-ticket exchange the same format. If you change the brief section names, the `- 작성일:` (Date written) line, or the ticket's `- 상태:` (Status) line, edit all three skills together.

## Change the invocation type

The invocation type is set in the `SKILL.md` frontmatter.

- **Change to User-invoked**: Add `disable-model-invocation: true`. The skill runs only when the user types its name.
- **Change to Model-invoked**: Delete that line. Claude picks skills by reading `description`, so state specifically in `description` when to use the skill.

Another skill cannot call a User-invoked skill with the Skill tool. For example, set-brief does not call set-ticket. It tells the user to run it.

## Check a modified skill

Pass a skill folder path to the repository's `scripts/validate.py` to check rules such as frontmatter keys, `name` versus folder name, and broken links. It requires PyYAML.

```bash
pip install pyyaml
python3 dev-gongbang/scripts/validate.py ~/.claude/skills/write-docs
```

The result is JSON. If `errors` is empty, the check passes. For `warnings`, decide whether to fix each one or confirm a reason to leave it.

## Test a modified skill

To see whether an edited skill actually works well, use building-skills. Pass the skill folder path and it runs in the "기존 스킬 개선" (Improve existing skill) mode.

```
/gongbang:building-skills ~/.claude/skills/write-docs
```

It keeps the original as a snapshot before editing, runs tests with representative requests, and builds a review page. If you choose "비교" (Compare) as the validation level, it compares the results of the original and the edited skill side by side. The full process is in the [building-skills page](skills/building-skills.md).

## Use in-progress skills via links

You can connect `in-progress/` skills with symbolic links instead of copying them. Edits in the repository take effect from the next session, and you do not need to bump a version as with the plugin.

```bash
dev-gongbang/scripts/link-in-progress.sh
```

This creates a link for each skill in `~/.claude/skills/`. To link only some skills, list their names after the command. To use them only in a specific project, run it from that project folder with `--project`. To remove links, add `--remove`. All options are in the [in-progress README](../../skills/in-progress/README.md).

## Contributing

To make your edits available to everyone, fork the repository and send a PR. Rules to follow when adding or moving a skill are in [.claude/CLAUDE.md](../../.claude/CLAUDE.md). After making changes, run `scripts/check.py` and make it pass.

---

[All docs](README.md) · [README](../../README.en.md)
