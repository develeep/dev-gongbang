<p align="right"><a href="../../skills/building-skills.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › building-skills

# building-skills

Pass a SKILL.md draft or your work material, and finish a skill that meets the Agent Skills spec and, when actually run, does better than working without the skill. Based on Claude's official skill best practices and the Agent Skills spec, it repeats static checks, test runs, human review, and fixes. The procedures, rules, decision criteria, and examples in the skill come only from your material, your answers, and proposals you approved.

| Field | Value |
|---|---|
| Bucket | productivity |
| Invocation | Model-invoked (when you ask to build a skill or to check or improve one) |
| Command | `/gongbang:building-skills [skill folder path, SKILL.md draft, or description of the skill to build]` |
| Source | [SKILL.md](../../../skills/productivity/building-skills/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

It runs in one of three modes depending on the input. If the input leaves the mode unclear, it asks.

| Mode | When | Input to pass |
|---|---|---|
| A. Continue from prompt-builder | You want to test and refine a SKILL.md draft built with prompt-builder | prompt-builder output (design summary, SKILL.md code block, next steps) |
| B. Improve existing skill | You want to fix an existing skill and confirm it got better than before | A skill folder or SKILL.md |
| C. Standalone new | You want to build a new skill from material | Material such as a description of the skill to build, conversation logs, runbooks, code, or review comments |

This skill handles only SKILL.md. To write a CLAUDE.md, use prompt-builder.

## Prerequisites

- Python 3.9 or later. Bundled scripts use only the standard library.
- Three representative requests. For a Model-invoked skill, also prepare two near-miss requests: similar, but the skill should not be used. If you have no representative requests, it asks rather than inventing them. If you leave it to the skill, it shows three drafts and uses only the ones you approve.
- For mode C, pass whatever you have of these: conversation logs where the task was actually done, runbooks or internal docs, API specs, config files or code, review comments or issues. If the request has no material, the skill asks for it. With no material at all, it proceeds with questions alone, but quality drops.
- Test runs use subagents. In an environment that cannot start subagents, it performs the cases one by one itself, tells you this is not rigorous, and skips the baseline runs.
- Validation level 3 (description measurement) needs the `claude` CLI (Claude Code) to measure. Without it, the skill builds only the query set and skips the measurement.

## How it works

1. **Read the input and choose the mode**: It chooses the mode from the input. A skill received only as code blocks is moved into files in a new `<name>/` folder in the working folder. In mode B, it copies the original to `<name>-workspace/skill-snapshot/` before editing, as a baseline for comparison.
2. **Confirm the spec**: It fills in the spec table (K1–K10), shows it as a `항목 | 값 | 출처 | 상태` (Field | Value | Source | Status) table, and asks only about items whose status is ambiguous or missing. In mode A, it does not ask again about values prompt-builder already confirmed with you.
3. **Write or improve**: It writes or edits SKILL.md and bundled files following the authoring rules in `references/authoring-rules.md`. Format changes such as polishing wording, reordering, or splitting out reference files are made right away, and it tells you what changed. For content such as procedures, rules, decision criteria, gotchas, and examples, it proposes the exact sentences to add and gets them approved.
4. **Static check**: It checks with `scripts/check_skill.py` and fixes until no ERROR remains. For each WARN, it either fixes it or tells you in one line why not. Items the script cannot check are reviewed with the human review checklist, and the results are shown as a `항목 | 결과 | 근거` (Item | Result | Evidence) table.
5. **Choose the validation level**: You choose one of these levels. Levels are cumulative.

   | Level | What it does | Cost |
   |---|---|---|
   | 1. Check (recommended, default) | Runs the representative requests only with the skill, then grades and reviews | About 3 subagents |
   | 2. Compare | Level 1, plus baseline runs (without the skill for modes A and C, the snapshot for mode B) for comparison. If there are several target models (K7), it runs each model | 6 or more subagents |
   | 3. description | Level 2, plus measuring and refining whether the description makes the skill run | Dozens or more of `claude -p` runs |

   User-invoked skills are called by name, so level 3 is removed from the options. If you choose to finish without tests, it goes to step 9 and notes in the wrap-up report that no run validation was done.
6. **Write, run, and grade tests**: For each representative request, it creates a test case in the skill folder's `evals/<case-name>/` in the format `claude plugin eval` reads. If the CLAUDE.md of the repo you are working in sets an eval location, it uses that location. It starts all runs at once, writes assertions while they run, and grades when they finish. At level 2 or above, it aggregates the results with `scripts/aggregate.py`. Run results accumulate in `<name>-workspace/iteration-N/` next to the skill folder.

   If the skill under test asks the user questions, a subagent has no one to answer, so it sets an expected answer for each case and passes it with the run. You confirm these answers.
7. **User review**: Before analyzing the results, it delivers the review page built with `scripts/review.py` (`iteration-N/review.html`). Write feedback for each case and click "피드백 내보내기" (Export feedback) to download `feedback.json`. Attach that file in the chat or put it in a connected folder. A case with empty feedback is taken as fine.
8. **Diagnose and fix**: It finds causes from failed assertions, feedback, and run logs, and shows proposed fixes as a `번호 | 근거 | 바꿀 문장 전/후 | 형식/내용` (No. | Evidence | Sentence before/after | Format/Content) table. Format fixes are applied right away, and you approve, edit, or drop each content fix by number. After fixing, it runs the static check again and repeats from step 6 in `iteration-<N+1>/`. It stops when you are satisfied, all feedback is empty, or results stop improving.

   If you chose validation level 3, it refines the description after the iterations end. It builds about 20 queries (8–10 that should trigger the skill and 8–10 that should not), gets them confirmed, measures with `scripts/trigger_eval.py`, and revises up to 5 times. Each measurement makes real billed runs equal to the number of queries × runs per query (`--runs`), so it tells you the count before starting.
9. **Wrap up and deliver**: It runs the static check one last time to confirm there is no ERROR, then delivers.

## Output

- The finished skill folder and its test cases (`evals/<case-name>/`)
- `<name>-workspace/` next to the skill folder: run results, grading, and the review page for each iteration, plus aggregates (`benchmark.json`, `benchmark.md`) at level 2 or above
- How it delivers depends on the skill's contents.
  - Only a SKILL.md with no extra frontmatter: in an environment with the `propose_skills` tool, it shows a save card.
  - Otherwise: it builds a `<name>.skill` package with `scripts/package.py` and delivers it. It also tells you how to copy the skill to your agent's skill folder (for example `~/.claude/skills/<name>/` or `.claude/skills/<name>/` in Claude Code, `~/.agents/skills/<name>/` or `.agents/skills/<name>/` in Codex and OMP).
- Wrap-up report: final pass rate and number of iterations (at level 2 or above, the difference from the baseline runs), fixes applied (format and content separated), and remaining WARNs, failures, and unapproved fix proposals. If run validation was skipped or only some models were tested, it says so.

The `propose_skills` save card in claude.ai and Cowork keeps only `name`, `description`, and the body. It drops other frontmatter keys such as `disable-model-invocation` and cannot carry bundled files. That is why a skill with bundled files or extra frontmatter is delivered as a package.

## Customize

| What to change | File to edit |
|---|---|
| Skill authoring rules and the human review checklist | `references/authoring-rules.md` |
| Spec table items, input handling per mode | `references/intake.md` |
| How to write and grade tests, diagnosis table | `references/evaluation.md` |
| Procedure for measuring and refining the description | `references/description-tuning.md` |
| Rules checked by machine | `scripts/check_skill.py` |

To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **prompt-builder**: Build a SKILL.md draft with prompt-builder and pass its output, and building-skills continues in mode A. It does not ask again about values prompt-builder already confirmed. The warnings left in prompt-builder's "다음 단계" (Next steps), such as unapproved proposals, skipped or defaulted items, and failed review items, are the first candidates it checks when looking for causes of failure.
- After editing a skill in this repository, you can test it in mode B. See the [customization guide](../customization.md#test-a-modified-skill).

---

← Previous: [set-guidelines](set-guidelines.md) · [All docs](../README.md) · Next: [write-docs](write-docs.md) →
