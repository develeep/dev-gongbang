<p align="right"><a href="../../skills/run-ticket.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › run-ticket

# run-ticket

Implements and reviews one ticket made by set-ticket, then updates the ticket status and the brief checkboxes. When continued from run-flow, the conversation that made the brief may still be in the same session, but it still relies only on the brief, the ticket, and the completion records of earlier tickets. This session does the implementation, the done-criteria check, the code review, and the rule check itself; the only thing it hands to a new context is the cross review by another company's model. It does not commit. If you ask for several tickets, this session runs them itself, in order. The parallel run is an optional path used only when you choose it. If two or more tickets can start together, none of them share an integration branch, and you or the repo or agent rules name a usable worker tool procedure, it uses that procedure to run them in parallel with workers, one worktree per ticket, and only then commits to ticket branches and merges them. Without a usable procedure, it runs them in order.

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
- Run several tickets at once, as in "all remaining tickets". By default this session runs them itself, in order. It runs them in parallel only if you chose the parallel run (you named a worker tool procedure or registered one in the rules), that procedure is usable, two or more tickets can start together, and no tickets share an integration branch.

## Prerequisites

- A brief and tickets made with set-brief and set-ticket
- For GitHub tickets, the `gh` CLI must be logged in.
- If the working tree has changes outside the brief and tickets, it asks whether to commit them before continuing. If you continue as is, earlier changes get mixed into the review. Changes that are not in any finished ticket's changed-file list may be the unfinished work of an interrupted ticket, so it shows them separately and asks whether to revert them or keep building on them, even when this ticket does not touch those files.
- The parallel run is optional. Unless you choose it, this session runs the tickets itself, in order. To run several tickets in parallel, a worker tool procedure must be named. A worker tool procedure is a document that describes how to create, wait for, and clean up workers with one worker tool. It looks at procedures in the order below and uses the first one whose usage conditions are met. If no procedure is named, or none can be used, it runs the tickets in order.
  1. The procedure for the tool named by you or the caller
  2. The procedure named in the repo or agent rules (CLAUDE.md, AGENTS.md). If there are several, in the order the rules list them.
- Optional setup examples: [Orca orchestration setup](../orca-orchestration.md), [Paseo orchestration setup](../paseo-orchestration.md). Each guide explains how to install the tool and register its procedure in a rules file.
- The cross review is a read-only review by a model from a different company than the model that implemented the change. The implementing model is this session's model, or, in a parallel run, the model of the worker that implemented the ticket. To use another company's model, name it when you run the skill, write the agent or model for the cross review in the repo or agent rules, the harness settings, or a saved profile (for example, the [omp multi-agent setup](../omp-orchestration.md)), or name a worker tool procedure that defines a cross-review worker. If nothing is written down, it looks up the models this session can use and picks one. It does not skip the cross review when no other company's model is available. It substitutes a review in a new context on the same company's model, writes the substitution and the model that ran it in the completion record, and continues. The full order is in "Cross review" below.

## How it works

1. It picks a ticket. Without an argument, it takes the most recent brief that still has unfinished tickets, and picks the lowest-numbered ticket whose blocked-by relations are cleared.
2. It reads the ticket, the full brief, the completion records of finished tickets in the same brief, and the repo's CLAUDE.md and AGENTS.md.
3. This session implements "만들 것" (what to build) itself. It does not hand the implementation to a subagent or another agent. The only exception is the workers of a parallel run. It does not fix problems outside the ticket's scope and leaves them in the report.
4. It checks each done criterion with a command or observation. This session also checks criteria that must be seen on screen itself. If it has a way to drive a browser or capture the screen, it opens the screen and keeps the evidence; an item it could not check does not count as a pass and goes under "확인 못 한 것" (could not check) in the completion record. If a criterion fails, it works out the cause and fixes it in the same session, then checks again. It does not hand the ticket over again or move it up to another agent. If the criterion still fails on the third attempt, counting the first, it leaves the ticket status unchanged and stops, reports the failed criteria, the attempt count, and the causes, and asks whether to split the ticket again. When run-flow called it, it writes the same in the state file's `- 멈춘 이유:` (reason stopped) line. If a stronger model is needed, you can change the session model and run it again.
5. It reviews. This session runs the code review (the first method that applies in this order: the review skill named in the repo rules, the `code-review` skill, its own review) and the check-guidelines rule check itself, one after the other, fixes their findings, and then calls the cross review once. If a review skill tells it to start subagents for sub-reviews, it does not start them and does those sub-reviews itself, one by one. If a skill cannot run that way, it does not use the skill, reviews the change itself, and says so in the report. It does not call a separate security review; if the change touches authentication, authorization, payments, or personal data, it adds security to the cross review's criteria. It writes the completion record only after it has verified every cross-review finding. There is no path that finishes this step without a cross review.
6. If run-flow passed the protected path check, it first checks that the tests and judge cases from the starting HEAD were not changed or deleted, including changes made through the shell. If the check fails, it does not accept the ticket, shows the changed files, and stops; if it passes, it adds the new tests of this ticket to the protected list. Then it writes the completion record and runs the cross-review gate (`scripts/cross_review.py gate`). If the record has no cross-review line, or the line's code fingerprint differs from the current code, the gate refuses; the ticket status stays as it is and the review is done again. If the gate passes, it sets the ticket status to done or closes the issue and updates the brief checkboxes. If the repo rules or the run-flow state file define a different completion status, it writes that value instead of done. For the last ticket, it runs the brief's "확인 기준" (verification criteria) and closes the brief. In a multi-ticket run, the cross-review lines, the gate, and the last-ticket work happen once after the integrated review.

If the ticket and the repo rules conflict, it asks before continuing. The priority is: the ticket's "하면 안 되는 것" (what not to do) and "작업 경계" (work boundaries), then the repo rules, then the skill's default behavior.

### Cross review

This session calls it once in step 5, takes the result, and continues in the same conversation. The reviewer does not talk to you and does not decide the next step.

- **What it passes**: the diff range to review (from the HEAD at work start), the full brief (and the full ticket when one ticket is reviewed), the list of criteria, and the checks to run. The criteria are bugs, and violations of the ticket's "하면 안 되는 것" (what not to do) and "작업 경계" (work boundaries) and of the repo rules; if the change touches authentication, authorization, payments, or personal data, security is added. The checks to run are the ticket's done criteria, plus the brief's "확인 기준" (verification criteria) for the last ticket or the integrated review. It does not pass secrets or raw logs.
- **Permissions**: read-only. The reviewer does not edit files, commit, or write outside the repository. It runs the check commands, but a command that changes repository files is not run and is reported as `확인 못 함` (could not check). This session compares the code fingerprint from `scripts/cross_review.py fingerprint`, taken right before the call and right after the result. The fingerprint covers uncommitted changes and new files and leaves out the brief, ticket, and run-flow flow documents. If the tree hash cannot be computed, the script falls back to a fingerprint built from the status and diff. If it changed, this session does not use that review result, shows you what changed, and hands the review to the next means.
- **What it gets back**: only the name of the model that ran the review, the list of findings, and a verdict per check. Each finding has the criterion it belongs to, a severity, the file and line, the evidence (a command that reproduces it, or the code or rule text), and how to fix it. Each check has `met`, `unmet`, or `확인 못 함` (could not check), with the command run and a short result. It does not take a summary, an overall verdict, or a fix diff.
- **Verifying the result**: this session reproduces each finding or checks it against the code or rule text, and records it as accepted, rejected (with the reason), or out of scope. For an `unmet` check, it runs the command again and fixes the cause if it reproduces. If the reviewer's verdict differs from this session's own check, the difference goes in the completion record. It fixes accepted findings and then checks the done criteria and verification commands again. A report with no findings is one input, not grounds for acceptance.
- **Model and means**: no model is fixed. The only condition is a company different from the implementing model's, and each time it uses the first that works in this order.
  1. The model or means you or the caller named for this run
  2. The cross-review means written in your settings: an agent or model set in the repo or agent rules files, the harness settings, or a saved agent profile, and the "cross-review worker" of a named or registered worker tool procedure
  3. Environment lookup: it picks another company's model from the providers, models, and agents this session can use, and tells you what it picked
  4. If no other company's model can be used, it substitutes a review in a new context on the same company's model. What it passes, the permissions, what it gets back, and the verification are the same. If the model can be set when starting it, it sets one, so the record can name the model that ran the review

  If there is no response or the result cannot be read, it hands the review to the next means. Independence is judged by the model that actually ran the review, not the planned one. If that model is from the same company as the implementing model, it hands the review to the next means; if only number 4 is left, it counts that review as the number 4 substitution. If it cannot start any new context at all, it substitutes this session's own review. A self review is weaker than a new-context review on the same company's model, so it is marked differently.
- **Record**: after verifying the result, it takes the code fingerprint and builds the completion record's `- 교차 리뷰:` (cross review) line with `scripts/cross_review.py record`. The line ends with the code fingerprint, so the gate in step 6 can tell whether the code changed after the review. A substituted review is not an independent check, so the report also says "교차 리뷰 대체(같은 회사 모델 <model name>)" (cross review substituted, same company's model) or "교차 리뷰 대체(새 컨텍스트 없음, 메인 세션 자기 리뷰)" (cross review substituted, no new context, main session self review) for you to see and judge. When run-flow called it, it also writes this on the state file's `- 교차 리뷰 모델:` (cross review model) line.
  - Another company's model ran it: `- 교차 리뷰: 완료 (<model that ran it>, 코드 지문 <fingerprint>)`
  - Substituted with a new context on the same company's model: `- 교차 리뷰: 대체 (같은 회사 모델 <model that ran it>, 코드 지문 <fingerprint>)`
  - Substituted with a self review: `- 교차 리뷰: 대체 (새 컨텍스트 없음, 메인 세션 자기 리뷰, 코드 지문 <fingerprint>)`

### Running multiple tickets

If you ask for a number range or "all remaining tickets", the method differs. The default is the sequential run, where this session implements the tickets itself, one at a time. The parallel run is used only when you chose it (you named a worker tool procedure or registered one in the repo or agent rules). If two or more tickets can start together, no ticket shares an integration branch, and a usable worker tool procedure exists, it runs the parallel run; if any of these is not true, it runs sequentially.

**Parallel run**: an optional path used only when you chose it. It starts one worker per ticket, each in a worktree branched from the current branch. This session acts as the coordinator: it keeps the blocked-by order, merges finished branches, writes completion records, and calls the cross review.

1. The working tree must be clean. Workers cannot read uncommitted brief and ticket documents, so it asks whether to commit them. On a resumed run, it recovers an interrupted merge (step 3) before this check.
2. It shows the execution groups, the tool to start workers with, the branch to merge into, the number of concurrent workers (3 by default), and the starting HEAD, and asks for approval. If the current branch is the default branch, it also asks whether to create a work branch.
3. If workers from an earlier run remain, it resumes them instead of creating new ones. If a ticket finished but was not merged, it merges it first instead of starting it again. A worker that is still running is not started again; it checks the worker's status and waits. If a blocking ticket is done but its completion record has no `- 교차 리뷰: 완료 (...)` (done) or `- 교차 리뷰: 대체 (...)` (substituted) line, it runs the cross review before starting the blocked tickets. A `- 교차 리뷰: 건너뜀 (...)` (skipped) line left by an earlier run counts as not reviewed. If the blocked tickets have not been started yet, it runs the cross review again; if they were already started or merged, it notes in the completion record that the integrated review covers that range. It reports worker identifiers as soon as they exist, and writes them to the record file if the caller passed one.
4. It starts workers for tickets whose blockers are all merged and cross-reviewed. Each worker implements its ticket, commits to the ticket branch, and reports. Answers given to worker questions and earlier decisions go into the instructions of workers started later.
5. After merging each finished branch into the current branch and before creating the merge commit, it runs the repo's verification commands (type check, lint, tests). If run-flow passed the protected path check, it also checks that no file on the protected list changed in the merged result or in the worker's ticket branch; if one did, it aborts the merge and stops. If they pass, it puts the completion record in the merge commit and cleans up the worker and its worktree. A GitHub ticket is closed after the merge commit is created. If they fail, it undoes the merge, starts no new worker, and stops. Before stopping, this session looks for the cause itself and shows which side's change the failure seems to come from, with the evidence. If a merged ticket blocks other tickets, it runs only the cross review on that merge before starting the blocked tickets. It does not start the blocked tickets without this review, and if no other company's model can be used, it substitutes a review in a new context on the same company's model. When the review is done, it adds ``- 교차 리뷰: 완료 (`<merge commit hash>`, <model that ran it>)`` or ``- 교차 리뷰: 대체 (`<merge commit hash>`, 같은 회사 모델 <model that ran it>)`` to the completion record. On a conflict it asks the worker to rebase; if it conflicts again, it stops and tells you. A failed ticket and the tickets it blocks are not run.
6. When all are done, it reviews everything from the starting HEAD once, adds the result to the completion records of tickets that have no cross-review line, runs the brief's "확인 기준" (verification criteria), and reports the results and the list of commits. You decide on push, PR, and merging into the default branch.

How workers are created, waited for, and cleaned up is set by the chosen worker tool procedure. A procedure fills in the items below with that tool's methods. The conditions for each item are in "워커 도구 절차" (Worker tool procedure) in `references/multi-ticket.md`.

| Item | What the procedure defines |
|---|---|
| Usage conditions | How to check that this session can start workers with the tool |
| Creating workers | How to create a new worktree and a new branch from the current branch's local ref when the worker starts, how to pass the worker spec, and the order for choosing the worker's model and effort |
| Waiting | How this session is notified when a worker finishes, asks, stops, or requests a permission. It does not poll status. |
| Judging the end | How to sort notifications and the last report into pass, question, and failure. It is a pass only if the reported commit is on the ticket branch. |
| Sending to the same worker | How to send answers to questions and rebase requests to that worker instead of a new one |
| Resuming | How to find remaining workers from the recorded worker identifier and read their state and last report |
| Cleanup | How to close the worker after the merge and remove the worktree and the merged ticket branch. Those of failed tickets are kept. |
| Worker identifier | The value and format to record. It holds the tool name and the IDs needed to find the workers. |
| Cross-review worker | How to start a worker on another company's model in the current working tree as read-only and pass it the diff range, the full brief, the criteria, and the checks to run; the order for choosing its model and effort; and how to receive its findings, its verdict per check, and the name of the model that ran it. The procedure does not fix the model, and no worker is started if no other company's model can be chosen. |

**Sequential run**: the default. This session implements the tickets itself, one at a time, and does not start a subagent per ticket. It writes one ticket's completion record before starting the next. The tickets edit the same working tree, so it does not work on two at once and does not commit. If a ticket fails its done criteria, it tries up to three times in the same session, counting the first attempt; if the ticket still fails, it stops without starting the later tickets. When all are done, it reviews the whole change once, adds the cross-review result to each ticket's completion record, and then runs the brief's "확인 기준". If commits were made midway because of the repo rules or your decision, the review covers them too.

## Output

- The implemented code changes. Not committed, except in a parallel run, which creates one merge commit per ticket.
- A completion record attached to the ticket: completion date, commit info (a not-committed note with the HEAD at work start, or the merged ticket branch and commit in a parallel run), changed files, the commands run and their results, criteria that could not be checked, the model that ran the cross review (with the substitution mark if it was substituted), the verdict on each cross-review finding, and findings not fixed. Results other tickets will use go under `## 산출물` (output artifact).
- A report: finished ticket, done criteria results, changed files, output artifact location, the model that ran the cross review and the substitution mark, the verdict on each cross-review finding, review findings not fixed, skipped reviews (a rule check that could not run, or a review skill that was not used), next ticket

## Customize

| What to change | Where to edit |
|---|---|
| Ticket selection rules | SKILL.md "1. 티켓 고르기" (1. Pick a ticket) |
| Priority of review methods | SKILL.md "5. 리뷰" (5. Review) |
| Completion record format | SKILL.md "6. 완료 기록" (6. Completion record) |
| Cross-review code fingerprint, record line, completion gate | `scripts/cross_review.py` |
| Model or means for the cross review | Name it when you run the skill, or write it in the repo or agent rules (CLAUDE.md, AGENTS.md), the harness settings, or a saved profile. The order is in SKILL.md "5. 리뷰" (5. Review) |
| Retry limit for done criteria (3 attempts) | SKILL.md "4. 완료 기준 확인" (4. Check done criteria) |
| Conditions for choosing the method, number of concurrent workers, merge method, items a worker tool procedure fills in, sequential run | `references/multi-ticket.md` |
| Worker tool for the parallel run | Name a worker tool procedure in the repo or agent rules (CLAUDE.md, AGENTS.md) |
| Model and effort of implementation and cross review workers | The repo or agent rules (CLAUDE.md, AGENTS.md), or wherever the chosen worker tool procedure says |

Not committing is a core rule. Even if the repo rules require commits, it leaves that to the user. The only exception is the parallel run. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **set-brief**, **set-ticket**: create the brief and tickets to run.
- **run-flow**: uses this skill in its stage 5 to run the brief's remaining tickets.
- If the **code-review** skill is installed, it is used for the code review in step 5.
- **check-guidelines**: used for the rule check in step 5.

---

← Previous: [set-ticket](set-ticket.md) · [All docs](../README.md) · Next: [analyzing-requirements](analyzing-requirements.md) →
