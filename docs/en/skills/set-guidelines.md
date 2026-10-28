<p align="right"><a href="../../skills/set-guidelines.md">한국어</a> · <b>English</b></p>

# set-guidelines

Picks coding guides that fit the repo's languages and frameworks from the [awesome-guidelines](https://github.com/Kristories/awesome-guidelines) list and extracts rules from the source text. From those rules it creates what you choose: `.claude/rules/` rule files, CLAUDE.md/AGENTS.md, and linter and formatter configs. It writes files only after final approval.

| Field | Value |
|---|---|
| Bucket | engineering |
| Invocation | User-invoked |
| Command | `/gongbang:set-guidelines` |
| Source | [SKILL.md](../../../skills/engineering/set-guidelines/SKILL.md) |

## When to use

- The repo has no coding rules or linter and formatter configs, and you want to create them.
- You want to fix or add to existing rules.
- You want to remove existing rules and set new ones.

## Prerequisites

- Web access, to read the guide source texts. Guides with broken or unreadable links are skipped.
- When it creates a linter or formatter config, it checks the config with that tool. If the tool is not installed, it asks whether to install it for the check.

## How it works

1. It identifies the repo's languages and frameworks and asks you to confirm. It also looks for existing convention docs, CLAUDE.md/AGENTS.md, `.claude/rules/`, and linter and formatter configs.
2. If rules already exist, you choose how to handle them.
   - **Improve/extend**: keep the existing rules. It recommends fixes and rules to add.
   - **Reset**: remove the existing rules and set new ones.
3. It recommends guides, linters, and formatters, and you choose. A recommended tool that is not in the list is marked "awesome-guidelines 목록 밖" (outside the awesome-guidelines list).
4. It reads the source text of the chosen guides and extracts rules. When guides have conflicting rules, it shows them side by side and you pick one.
5. You choose the output artifacts and paths. You review the list of files to create, change, or delete, and give final approval.
6. It writes only the approved files. For linter and formatter configs, it runs the tool to check that the config loads without errors.

Team rules take precedence over rules extracted from guides. Team rules are the rules already in the repo, plus rules you add to the "팀 규칙" (team rules) section of CLAUDE.md/AGENTS.md after the output artifacts are created.

## Output

It creates only what you choose.

- **Per-area rule files** `.claude/rules/<area>.md`: if `paths` lists file patterns, the file loads only when Claude works on matching files. Without `paths`, it loads every session, like CLAUDE.md.
- **CLAUDE.md / AGENTS.md**: keeps only the core rules and moves details to rule files. If both are created, it adds an `@AGENTS.md` line to CLAUDE.md, because Claude Code reads only CLAUDE.md when both exist.
- **Linter and formatter configs**: follow the chosen tool's documentation.

## Customize

| What to change | File to edit |
|---|---|
| List of guides and tools to recommend | `reference/guides-index.md` (snapshot of the awesome-guidelines README, 2026-10-28) |
| Rule file format | `templates/rule.md` |
| CLAUDE.md / AGENTS.md format | `templates/agent-instructions.md` |

To add an in-house guide to the recommendation candidates, add its link to the section for that language or tool in `reference/guides-index.md`. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **check-guidelines**: checks code against the rules you created.
