<p align="right"><a href="../../skills/set-guidelines.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › set-guidelines

# set-guidelines

Pick coding guides that fit your repo's languages and frameworks from the [awesome-guidelines](https://github.com/Kristories/awesome-guidelines) list, and create the repo's rule files and configs from rules extracted from the guides' source text. It can create `.claude/rules/` rule files, CLAUDE.md/AGENTS.md, and linter and formatter configs, and you choose what to create and where. It writes files only after your final approval.

| Field | Value |
|---|---|
| Bucket | engineering |
| Invocation | User-invoked |
| Command | `/gongbang:set-guidelines` |
| Source | [SKILL.md](../../../skills/engineering/set-guidelines/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

- The repo has no coding rules or linter and formatter configs, and you want to create them.
- You want to fix or add to existing rules.
- You want to remove existing rules and set new ones.

## Prerequisites

- The skill must be able to read the guides' source text on the web. Guides with broken links or unreadable source text are skipped.
- When it creates a linter or formatter config, it runs that tool to check the config. If the tool is not installed, it asks whether to install it for the check.

## How it works

1. **Identify the repo and confirm**: It looks through the repo to identify the languages and frameworks, and asks you to confirm. It also looks for existing convention docs, CLAUDE.md/AGENTS.md, `.claude/rules/`, and linter and formatter configs.
2. **Decide how to handle existing rules**: You choose only if step 1 found existing rules.
   - **개선·추가** (Improve/extend): keep the existing rules. It recommends fixes and rules to add.
   - **초기화** (Reset): remove the existing rules and set new ones.
3. **Recommend and choose guides and tools**: It finds the sections in `reference/guides-index.md` for the languages, frameworks, platforms, and tools confirmed in step 1, recommends guides, linters, and formatters, and you choose. If the list has no linter or formatter for a language, it recommends a tool widely used for that language and marks it "awesome-guidelines 목록 밖" (outside the awesome-guidelines list).
4. **Read the source text and extract rules**: It reads the source text of the chosen guides and extracts the rules to apply to this repo.
   - If the chosen guides have conflicting rules, it shows them side by side and you pick one. Which one is right is a team preference, so it cannot be decided from the guides alone.
   - It extracts architecture rules only if a chosen guide covers architecture. API design rules are treated as area rules.
5. **Choose outputs and give final approval**: You choose the outputs to create and paths that fit the repo. You review the list of files to create, change, or delete with a summary of their content and the `paths` patterns for each rule file, and give final approval.
6. **Write**: It writes only the approved files. If it created a linter or formatter config, it runs the tool to check that the config loads without errors. If there is an error, it fixes the config and runs the tool again.

When a rule extracted from a guide differs from a team rule, the team rule wins. Guides are general advice, and team rules are decisions this repo has already agreed on. Team rules are the rules already in the repo (convention docs, CLAUDE.md/AGENTS.md, `.claude/rules/`, linter and formatter configs), plus rules you add to the "팀 규칙" (Team rules) section of CLAUDE.md/AGENTS.md after the outputs are created. If you choose reset in step 2, the existing rules no longer take precedence over guide rules.

## Output

It creates only the outputs you choose.

| Output | Template | Content |
|---|---|---|
| Per-area rule file `.claude/rules/<area>.md` | `templates/rule.md` | If `paths` lists file patterns, the file loads only when Claude works on matching files. Without `paths`, it loads every session, like CLAUDE.md. An area that applies only to certain files gets those file patterns in `paths` |
| CLAUDE.md / AGENTS.md | `templates/agent-instructions.md` | Split into a "팀 규칙" (Team rules) section and a "규칙" (Rules) section. Because it loads into context every session, it keeps only the core rules, moves details to rule files, and does not repeat rules that linters and formatters enforce |
| Linter and formatter configs | The chosen tool's documentation | It runs the tool to check that the config loads without errors |

If both CLAUDE.md and AGENTS.md are created, it adds an `@AGENTS.md` line to CLAUDE.md, because Claude Code reads only CLAUDE.md when both exist.

Output files contain no source attributions, no links, and no sections that are not in the template (such as reasons for departing from a guide or rules not applied).

## Customize

| What to change | File to edit |
|---|---|
| List of guides and tools to recommend | `reference/guides-index.md` (snapshot of the awesome-guidelines README, 2026-10-28) |
| Rule file format | `templates/rule.md` |
| CLAUDE.md / AGENTS.md format | `templates/agent-instructions.md` |

To add an in-house guide to the recommendation candidates, add its link to the section for that language or tool in `reference/guides-index.md`. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **check-guidelines**: checks code against the rules you created.

---

← Previous: [prompt-builder](prompt-builder.md) · [All docs](../README.md) · Next: [building-skills](building-skills.md) →
