<p align="right"><a href="../../skills/building-skills.md">한국어</a> · <b>English</b></p>

# building-skills

Brings a skill in line with the spec and refines it until, when actually run, it does better than working without the skill. It repeats static checks, test runs, human review, and fixes, based on Claude's official skill best practices and the Agent Skills spec.

| Field | Value |
|---|---|
| Bucket | productivity |
| Invocation | User-invoked |
| Command | `/gongbang:building-skills [skill folder path, SKILL.md draft, or description of the skill to build]` |
| Source | [SKILL.md](../../../skills/productivity/building-skills/SKILL.md) |

## When to use

It runs in one of three modes depending on the input.

| Mode | Input |
|---|---|
| A. Continue from prompt-builder | prompt-builder output (design summary, SKILL.md code block, next steps) |
| B. Improve existing skill | A skill folder or SKILL.md |
| C. Standalone new | Material such as a description of the skill to build, conversation logs, runbooks, code, or review comments |

## Prerequisites

- Python 3.9 or later. Bundled scripts use only the standard library.
- Three representative requests. For a Model-invoked skill, also prepare two near-miss requests: similar, but the skill should not be used. If you have none, the skill shows three drafts and gets your approval.
- If you choose validation level 3 (description measurement), you need the `claude` CLI.

## How it works

1. Decides the mode from the input. In mode B, it copies the original to `<name>-workspace/skill-snapshot/` before editing, as a baseline for comparison.
2. Shows the spec table (K1–K10) as a `항목 | 값 | 출처 | 상태` (Field | Value | Source | Status) table, and asks only about items that are ambiguous or missing.
3. Writes or edits SKILL.md and bundled files according to the authoring rules. It fixes format issues right away, and for content it proposes the exact sentences to add and gets them approved.
4. Runs static checks with `scripts/check_skill.py` and fixes until no ERROR remains.
5. Choose the validation level. Levels are cumulative.

   | Level | What it does | Cost |
   |---|---|---|
   | 1. Check (default) | Runs the representative requests only with the skill, then grades and reviews | About 3 subagents |
   | 2. Compare | Level 1, plus comparison with a baseline run (without the skill, or the snapshot) | 6 or more subagents |
   | 3. description | Level 2, plus measuring and refining whether the description triggers the skill | Dozens or more of `claude -p` runs |

   User-invoked skills are run by name, so level 3 does not apply to them.
6. Creates tests, runs them, and grades them. Test results accumulate in `<name>-workspace/` next to the skill folder.
7. Delivers the review page (`review.html`) before analyzing the results. Write feedback for each case and click "피드백 내보내기" (Export feedback) to download `feedback.json`. Send that file back.
8. Finds causes from failed assertions, feedback, and run logs, and shows proposed fixes in a table. After fixing, it repeats from step 6.
9. Runs a final static check and delivers.

## Output

- The finished skill folder
- A `<name>.skill` package if there are bundled files or extra frontmatter. In Claude Code, you can also copy it to `~/.claude/skills/<name>/` (user) or `.claude/skills/<name>/` (project).
- Wrap-up report: final pass rate and number of iterations, fixes applied, and remaining WARNs, failures, and unapproved fix proposals

## Customize

| What to change | File to edit |
|---|---|
| Skill authoring rules and the human review checklist | `references/authoring-rules.md` |
| Spec table items, input handling per mode | `references/intake.md` |
| How to write and grade tests, diagnosis table | `references/evaluation.md` |
| Procedure for refining the description | `references/description-tuning.md` |
| Rules checked by machine | `scripts/check_skill.py` |

For how to copy and edit a skill, see the [customization guide](../customization.md).

## Related skills

- **prompt-builder**: Build a SKILL.md draft with prompt-builder and pass its output, and building-skills continues in mode A. It does not ask again about values prompt-builder already confirmed.
- After editing a skill in this repository, you can test it in mode B. See the [customization guide](../customization.md#test-a-modified-skill).
