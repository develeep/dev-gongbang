<p align="right"><a href="../../skills/check-guidelines.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › check-guidelines

# check-guidelines

Check code against the rules already in your repo and get a report of violations grouped by rule. The skill collects rules from `.claude/rules/` rule files, CLAUDE.md/AGENTS.md, and linter and formatter configs. Pick the numbers of the violations to fix in the report, and it fixes only those, then checks again with the same rules to confirm.

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

To create or change rules, use set-guidelines. Do not use this skill for general code review of bugs or performance.

## Prerequisites

- The repo needs at least one of: rule files (`.claude/rules/`), CLAUDE.md/AGENTS.md, linter and formatter configs. If there are none, the skill does not check and tells you to create rules with set-guidelines first.
- It runs only the linters and formatters that are installed. It does not install missing tools. It skips them and lists them under "검사 못 함" (not checked) in the report summary.

## How it works

1. **Set the check scope**: It takes the scope as an argument. If you give none, you choose one of these four.

   | Scope | Files to check |
   |---|---|
   | `all` | The whole repo |
   | `diff` | All uncommitted changes: staged, unstaged, and new (untracked) files |
   | `branch` | Files changed since branching from the origin default branch. If it cannot find the default branch, it asks for the base branch |
   | path | The given file or directory |

2. **Collect rules**: It finds and reads rule files, CLAUDE.md/AGENTS.md, and linter and formatter configs. A rule file with `paths` applies only to files that match those patterns. Rule files without `paths` and CLAUDE.md/AGENTS.md apply to every file in scope.
3. **Check**: It judges the rules in rule files and CLAUDE.md/AGENTS.md by reading the files. It runs linters and formatters on the files in scope and adds their results to the violations.

   If there are more than 100 files to check, it warns you that the check takes long and uses a lot of context. It shows the file count and zones split by top-level directory. After you approve, it checks the zones one after another and records each zone's results in the report right away.
4. **Report**: It shows the report and asks whether to fix anything. To fix, pick the violations by number.
5. **Fix and recheck**: It fixes only the chosen violations and checks the fixed files again with the same rules. If a chosen violation remains, it fixes and checks again. When done, it tells you which violations it fixed and the recheck results.

## Output

A rule check report in the `templates/report.md` format, written in Korean polite style (합니다체).

The top of the report summarizes the scope, the number of files checked, and the counts of violations, ambiguous cases, and rule conflicts in at most two sentences. A table lists the scope, the rules applied, and "검사 못 함" (not checked). The "검사 못 함" row appears only when a tool was skipped. Three sections follow, and a section with zero items is not created.

- **위반** (Violations): grouped by rule with the rule's location, and for each violation its location, current code, and how to fix it. Numbers run across the whole report.
- **애매함** (Ambiguous): places where it is hard to tell whether there is a violation, with the reason. These are not counted as violations, so that you do not end up changing code that is fine.
- **규칙 충돌** (Rule conflicts): rules that clash, where each one is, and a proposal for fixing the rules. The team decides which rule is right.

## Customize

| What to change | File to edit |
|---|---|
| Report format and writing style | `templates/report.md` |
| Check scope options | "1. 검사 범위 정하기" (Set the check scope) in SKILL.md |
| Threshold for checking in zones (100 files to check) | "3. 검사" (Check) in SKILL.md |

The check criteria come from the repo's rule files, CLAUDE.md/AGENTS.md, and linter and formatter configs. To change the criteria, edit those files. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **set-guidelines**: run it first to create rules when there are none.
- **run-ticket**: calls this skill in its step 5 review to check the changed file paths and only report. run-ticket fixes the findings that fall within the ticket's scope.

---

← Previous: [framing-problems](framing-problems.md) · [All docs](../README.md) · Next: [run-flow](run-flow.md) →
