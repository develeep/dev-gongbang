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

2. Copy the whole skill folder you want to edit. Skills have bundled folders such as `reference/` or `references/`, `templates/`, `assets/`, `scripts/`, and `agents/`, and these must come along too. The command below copies write-docs as a user skill.

   ```bash
   cp -r dev-gongbang/skills/productivity/write-docs ~/.claude/skills/
   ```

3. To rename the skill, change the folder name and the `name` in the `SKILL.md` frontmatter to the same value. If they differ, the check reports an error.
4. Edit the files. The files commonly edited for each skill are listed in [Files to edit per skill](#files-to-edit-per-skill).
5. [Check the edited skill](#check-a-modified-skill) and start a new session.

## Files to edit per skill

Paths are relative to the skill folder. Skills are in the same order as in the [README](../../README.en.md#skills). Details are in the "Customize" section of each skill page.

| Skill | File to edit | What changes |
|---|---|---|
| [prompt-builder](skills/prompt-builder.md) | `reference/models/<model>.md` | Per-model guide. If you add a new model, also add a row to the "모델 ID 패턴" (Model ID pattern) table in SKILL.md |
| | `reference/interview.md` | Interview items and quick mode defaults |
| [set-guidelines](skills/set-guidelines.md) | `reference/guides-index.md` | List of guides and tools to recommend |
| | `templates/rule.md`, `templates/agent-instructions.md` | Rule file and CLAUDE.md/AGENTS.md templates |
| [building-skills](skills/building-skills.md) | `references/authoring-rules.md` | Skill authoring rules and the human review checklist |
| | `scripts/check_skill.py` | Rules checked by machine |
| [write-docs](skills/write-docs.md) | `reference/tech-writing.md` | Technical document types, recommended structure, sentence principles. The default is the Toss technical writing guide |
| | `reference/clear-writing.md` | Principles applied to every field |
| [framing-problems](skills/framing-problems.md) | `SKILL.md` | Items to fill (R1–R6) and question format |
| [check-guidelines](skills/check-guidelines.md) | `templates/report.md` | Report template |
| [run-flow](skills/run-flow.md) | `SKILL.md` | Starting stage per argument, state file rules, protected list rules, links between stages |
| | `assets/state-file.md` | State file format |
| | `references/adr.md` | Conditions for proposing an ADR, where it is saved, the ADR template |
| | `references/brief-stage.md`, `references/merge-stage.md`, `references/pr-stage.md` | Procedures for stage 3 (brief), stage 6 (merge/PR decision), and stage 7 (opening the PR) |
| | `references/requirement-change.md` | Procedure for going back to stage 1 when requirements change during a flow |
| | `scripts/code_fingerprint.sh` | Fingerprint used to compare the reviewed code with the current code |
| | `scripts/start_stage.py` | Rules for deciding the starting stage from docs files in stage 0 |
| | `scripts/protected_paths.py` | Test file rules for the protected list, the pre-write decision, the check before acceptance. If you edit it in the repository, make the same edit to `mods/gongbang-mods/hooks/protected_paths.py`, the copy gongbang-mods uses for its decision |
| [set-brief](skills/set-brief.md) | `SKILL.md` | Brief template, save path |
| [set-ticket](skills/set-ticket.md) | `SKILL.md` | Ticket template, splitting criteria |
| [run-ticket](skills/run-ticket.md) | `SKILL.md` | Ticket selection rules, review order, completion record |
| | `scripts/cross_review.py` | Cross-review code fingerprint, the format of the completion record's `- 교차 리뷰:` (Cross-review) line, and the gate that refuses completion without it |
| | `references/multi-ticket.md` | Running multiple tickets: choosing the method, parallel run, items a worker tool procedure fills in, sequential run. The parallel run is an optional path used only when you name or register a worker tool procedure, and worker models follow your settings. Registering a procedure is covered in the [Orca](orca-orchestration.md) and [Paseo](paseo-orchestration.md) setup docs |
| [analyzing-requirements](skills/analyzing-requirements.md) | `SKILL.md` | Document template |

set-brief, set-ticket, run-ticket, and run-flow exchange the same format. If you change the brief section names, the `- 작성일:` (Date written) line, or the ticket's `- 상태:` (Status) line, edit all four skills together. In run-flow, edit `SKILL.md`, the documents in `references/`, and `scripts/start_stage.py`, which uses these lines to find briefs and finished tickets.

## Change the invocation type

The invocation type is set in the `SKILL.md` frontmatter.

- **Change to User-invoked**: Add `disable-model-invocation: true`. The skill runs only when the user types its name.
- **Change to Model-invoked**: Delete that line. Claude picks skills by reading `description`, so state specifically in `description` when to use the skill.

To get the same invocation type in Codex, also update `agents/openai.yaml` in the skill folder. When you change to User-invoked, add `policy.allow_implicit_invocation: false` so Codex does not invoke the skill on its own. When you change to Model-invoked, remove that setting. Inside this repository, `scripts/check.py` reports an error when the two settings disagree.

Another skill cannot load a User-invoked skill. That is why analyzing-requirements, framing-problems, set-brief, set-ticket, and run-ticket, which run-flow loads stage by stage, are all Model-invoked. Of these, framing-problems, set-brief, set-ticket, and run-ticket say in `description` that they run only when the user or another skill asks, so Claude does not pick them for ordinary requests.

## Check a modified skill

Pass a skill folder path to the repository's `scripts/validate.py` to check rules such as frontmatter keys, `name` versus folder name, and broken links. It requires PyYAML.

```bash
pip install pyyaml
python3 dev-gongbang/scripts/validate.py ~/.claude/skills/write-docs
```

The result is JSON. If the `errors` of each skill entry are empty and the exit code is 0, the check passes. For `warnings`, decide whether to fix each one or confirm a reason to leave it.

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

To make your edits available to everyone, fork the repository and send a PR. Rules to follow when adding or moving a skill are in [AGENTS.md](../../AGENTS.md). After making changes, run `scripts/check.py` and make it pass. It requires PyYAML and the Claude Code CLI.

---

[All docs](README.md) · [README](../../README.en.md)
