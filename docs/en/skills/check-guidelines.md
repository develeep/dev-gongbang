<p align="right"><a href="../../skills/check-guidelines.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › check-guidelines

# check-guidelines

Checks code against the rules in the repo. It collects rules from `.claude/rules/` rule files, CLAUDE.md/AGENTS.md, and linter and formatter configs, and reports violations by rule. Tell it the numbers of the violations you choose, and it fixes only those, then checks again to confirm.

| Field | Value |
|---|---|
| Bucket | engineering |
| Invocation | Model-invoked |
| Command | `/gongbang:check-guidelines [all \| diff \| branch \| path]` |
| Source | [SKILL.md](../../../skills/engineering/check-guidelines/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

- Check whether code follows the conventions or team rules.
- Find rule violations in your changes before a commit or PR.

If you ask something like "check whether the code follows our rules" or "look for convention violations before I open a PR", Claude can choose this skill without you typing its name.

Creating or changing rules is set-guidelines' job. Do not use this skill for general code review of bugs or performance.

## Prerequisites

- At least one of: rule files, CLAUDE.md/AGENTS.md, linter and formatter configs. If there are none, it does not check and tells you to run set-guidelines first.
- It runs only installed linters and formatters. Tools that are not installed are skipped and listed under "검사 못 함" (not checked) in the report.

## How it works

1. It sets the check scope. If you give no argument, you choose.
   - `all`: the whole repo
   - `diff`: all uncommitted changes (staged, unstaged, untracked)
   - `branch`: files changed since branching from the origin default branch
   - path: the given file or directory
2. It collects rules. A rule file with `paths` applies only to files that match those patterns.
3. It checks. If there are more than 100 target files, it warns you and shows zones by top-level directory. After you approve, it splits the check across subagents, one per zone.
4. It reports, and you choose violations to fix by number.
5. It fixes only the chosen violations and checks again with the same rules.

## Output

A rule check report. Sections with zero items are not created.

- **Violations**: grouped by rule, with location, current code, and how to fix. Numbers run across the whole report.
- **Ambiguous**: places where it is hard to tell whether there is a violation. These are not counted as violations.
- **Rule conflicts**: rules that clash, where they clash, and a proposal for fixing the rules. The team decides which rule is right.

## Customize

| What to change | File to edit |
|---|---|
| Report format and writing style | `templates/report.md` |
| Check scope options, threshold for splitting across subagents (100) | Steps 1 and 3 of SKILL.md |

The check criteria themselves come from the repo's rule files, CLAUDE.md/AGENTS.md, and linter and formatter configs, not from the skill. To change the criteria, edit those files. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **set-guidelines**: run it first to create rules when there are none.

---

← Previous: [framing-problems](framing-problems.md) · [All docs](../README.md) · Next: [set-brief](set-brief.md) →
