<p align="right"><a href="../../skills/run-ticket.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › run-ticket

# run-ticket

Implements and reviews one ticket made by set-ticket in a new session, then updates the ticket status and the brief checkboxes. It works without the conversation that made the brief, using only the brief, the ticket, and the completion records of earlier tickets. It does not commit. If you ask for several tickets and two or more of them can start together, it runs them in parallel with Orca workers, one worktree per ticket, and only then commits to ticket branches and merges them.

> This skill is in progress. Install `gongbang-dev` to use it. Its behavior may change.

| Field | Value |
|---|---|
| Bucket | in-progress |
| Invocation | Model-invoked (only when you ask or run-flow tells it to) |
| Command | `/gongbang:run-ticket [ticket/brief path, issue number/URL] [range for multiple tickets]` |
| Source | [SKILL.md](../../../skills/in-progress/run-ticket/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

- Run the tickets split with set-ticket one at a time.
- Run a small brief that was not split into tickets. The whole brief is treated as one ticket.
- Run several tickets at once, as in "all remaining tickets". If Orca is available and two or more tickets can start together, it runs them in parallel; otherwise, in order.

## Prerequisites

- A brief and tickets made with set-brief and set-ticket
- For GitHub tickets, the `gh` CLI must be logged in.
- If the working tree has changes outside the brief and tickets, it asks whether to commit them before continuing. If you continue as is, earlier changes get mixed into the review. Changes that are not in any finished ticket's changed-file list may be the unfinished work of an interrupted ticket, so it shows them separately and asks whether to revert them or keep building on them.
- To run several tickets in parallel, Orca must be running and the `orchestration` skill installed. Otherwise it runs them in order.
- The cross review needs a review agent on another company's model (for example, the reviewer in the [omp multi-agent setup](../omp-orchestration.md)) or Orca. If neither is available, it skips the cross review and says so in the report. If the review agent turns out to run on the same company's model as this session, it hands the review to Orca instead.

## How it works

1. It picks a ticket. Without an argument, it takes the most recent brief that still has unfinished tickets, and picks the lowest-numbered ticket whose blocked-by relations are cleared.
2. It reads the ticket, the full brief, the completion records of finished tickets in the same brief, and the repo's CLAUDE.md and AGENTS.md.
3. It implements "만들 것" (what to build). If the agent rules name an agent for implementing tickets, it hands over the brief, the ticket, the repo rules path, the verification commands, and earlier tickets' output artifacts. It does not fix problems outside the ticket's scope and leaves them in the report.
4. It checks each done criterion with a command or observation. If the agent rules name a UI-check agent, criteria that must be seen on screen go to it. If one fails, it fixes it. If it cannot fix it, it first follows the failure handling in the agent rules (handing it over again, moving it up to another agent); if it still fails, it reports the agents tried and the attempt count, and stops.
5. It reviews. It runs the code review (the first method that applies in this order: the review skill named in the repo rules, the `code-review` skill, its own review), a check-guidelines rule check, and a cross review by another company's model together, and writes the completion record only after it has all the results. If the model that actually ran the cross review is from the same company as this session, it hands the review to the next method (an Orca worker), and reports it as skipped only when no method is left. If the change touches authentication, authorization, payments, or personal data and the agent rules name a security review agent, it also hands the change to a security review.
6. It sets the ticket status to done or closes the issue, updates the brief checkboxes, and leaves a completion record. If the repo rules or the run-flow state file define a different completion status, it writes that value instead of done. For the last ticket, it runs the brief's "확인 기준" (verification criteria) and closes the brief. In a multi-ticket run, it does this once after the integrated review.

If the ticket and the repo rules conflict, it asks before continuing. The priority is: the ticket's "하면 안 되는 것" (what not to do) and "작업 경계" (work boundaries), then the repo rules, then the skill's default behavior.

### Running multiple tickets

If you ask for a number range or "all remaining tickets", the method differs. If Orca is available, two or more tickets can start together, and no ticket shares an integration branch, it runs the Orca parallel run; if any of these is not true, it runs sequentially.

**Orca parallel run**: it starts one Orca worker per ticket, each in a child worktree branched from the current branch.

1. The working tree must be clean. Workers cannot read uncommitted brief and ticket documents, so it asks whether to commit them. On a resumed run, it recovers an interrupted merge (step 3) before this check.
2. It shows the execution groups, the branch to merge into, the number of concurrent workers (3 by default), and the starting HEAD, and asks for approval. If the current branch is the default branch, it also asks whether to create a work branch.
3. It creates one Orca Run for the brief and one Task per ticket, with the blocked-by relations as Task deps. If a resumed Run has a Task that finished but was not merged, it merges it first instead of starting it again. A Task that is still running is not started again; it checks the worker's status and waits. If a blocking ticket is done but its completion record has no cross-review line, it runs the cross review first. It reports the Run ID as soon as the Run is created, and writes it to the record file if the caller passed one.
4. It starts workers for tickets whose blockers are all merged. If the agent rules set the model and effort for implementation workers, it starts them with those. Each worker implements its ticket, commits to the ticket branch, and reports. Answers given to worker questions and earlier decisions go into the instructions of workers started later.
5. After merging each finished branch into the current branch and before creating the merge commit, it runs the repo's verification commands (type check, lint, tests). If they pass, it puts the completion record in the merge commit and removes the worktree. A GitHub ticket is closed after the merge commit is created. If they fail, it undoes the merge, starts no new worker, and stops. If the agent rules name a debugging agent, it gets a cause report from that agent before stopping and shows it too. If a merged ticket blocks other tickets, it runs only the cross review on that merge before starting the blocked tickets, and adds a line to the completion record saying so. On a conflict it asks the worker to rebase; if it conflicts again, it stops and tells you. A failed ticket and the tickets it blocks are not run.
6. When all are done, it reviews everything from the starting HEAD once, runs the brief's "확인 기준" (verification criteria), and reports the results and the list of commits. You decide on push, PR, and merging into the default branch.

**Sequential run**: it starts one subagent per ticket, one after another. If the agent rules name an implementation agent, it starts that agent. They edit the same working tree, so it does not run them in parallel and does not commit. If the repo rules require your approval before code changes, the subagent only prepares a proposed diff, and this session applies it after you approve. If a ticket fails its done criteria, it follows the failure handling in the agent rules, and stops if the ticket still fails. When all are done, it reviews the whole change once and then runs the brief's "확인 기준". If commits were made midway because of the repo rules or your decision, the review covers them too.

## Output

- The implemented code changes. Not committed, except in an Orca parallel run, which creates one merge commit per ticket.
- A completion record attached to the ticket: completion date, commit info (a not-committed note with the HEAD at work start, or the merged ticket branch and commit in an Orca parallel run), changed files, the commands run and their results, criteria that could not be checked, and findings not fixed. Results other tickets will use go under `## 산출물` (output artifact).
- A report: finished ticket, done criteria results, changed files, output artifact location, review findings not fixed, skipped reviews, next ticket

## Customize

| What to change | Where to edit |
|---|---|
| Ticket selection rules | SKILL.md "1. 티켓 고르기" (1. Pick a ticket) |
| Priority of review methods | SKILL.md "5. 리뷰" (5. Review) |
| Completion record format | SKILL.md "6. 완료 기록" (6. Completion record) |
| Agents for implementation, UI check, cross review, security review, and code-review sub-reviews | Name them in the repo or agent rules (CLAUDE.md, AGENTS.md) or edit SKILL.md "3. 구현" through "5. 리뷰" (3. Implementation through 5. Review) |
| Conditions for choosing the method, number of concurrent workers, merge method, sequential run | `references/multi-ticket.md` |
| Model and effort of implementation and cross review workers | The repo or agent rules (CLAUDE.md, AGENTS.md) |

Not committing is a core rule. Even if the repo rules require commits, it leaves that to the user. The only exception is the Orca parallel run. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **set-brief**, **set-ticket**: create the brief and tickets to run.
- **run-flow**: uses this skill in its stage 5 to run the brief's remaining tickets.
- If the **code-review** skill is installed, it is used for the code review in step 5.
- **check-guidelines**: used for the rule check in step 5.
- **orchestration** (Orca): used for running several tickets in parallel and for cross-review workers.

---

← Previous: [set-ticket](set-ticket.md) · [All docs](../README.md) · Next: [analyzing-requirements](analyzing-requirements.md) →
