<p align="right"><a href="../../skills/run-ticket.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › run-ticket

# run-ticket

This session implements one ticket left by set-brief and set-ticket, checks its done criteria, reviews it, and then updates the ticket status and the brief checkboxes. The review always includes a cross review by a model from a different company than the implementing model, and a gate checks that the reviewed code is the current code. It does not commit. If you ask for several tickets, it runs them in order, and if you name a worker tool procedure, it can run them in parallel with workers.

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
- Run a small brief that was not split into tickets. The whole brief is treated as one ticket: its "남은 일" (remaining work) is what to build and its "확인 기준" (verification criteria) are the done criteria.
- Run several tickets at once, as in "all remaining tickets" or a number range. See [Running multiple tickets](#running-multiple-tickets).

run-flow uses this skill in its stage 5 to run the remaining tickets. It does not start by itself for general implementation requests that have no brief or ticket documents.

## Prerequisites

- A brief and tickets made with set-brief and set-ticket. Docs briefs are found by their `- 작성일: YYYY-MM-DD` (date written) line, including folders ignored by `.gitignore` (such as `.scratch/`). GitHub briefs are found among open issues labeled `context`.
- For briefs and tickets that are GitHub issues, a github.com remote and a logged-in `gh` CLI
- `python3`. The cross review's code fingerprint and completion gate are `scripts/cross_review.py`.
- A model from another company for the cross review. Name it when you run the skill, or write it in the repo or agent rules, the harness settings, or a saved agent profile (for example, the [omp multi-agent setup](../omp-orchestration.md)). Without one, it picks from the models it can use, and substitutes if no other company's model is available. The order is in [Cross review](#cross-review).
- Optional: a worker tool procedure for parallel runs. See [Running multiple tickets](#running-multiple-tickets) and the [Orca](../orca-orchestration.md) and [Paseo](../paseo-orchestration.md) orchestration guides.

## How it works

At the start it shows a checklist of steps 1 to 6 and updates it as each step ends.

1. **Pick a ticket**: if the argument is a ticket, it takes that ticket; if it is a brief, it picks within that brief. Without an argument, it takes the brief with the latest date among those that still have unfinished tickets, and picks the lowest-numbered ticket whose blocked-by relations are cleared. If the reference points to no document or to several, it shows the candidates and asks; if the chosen ticket is already done or still blocked, it says so and asks whether to go on. If there is no brief to pick, it says so and stops. Then it checks the working tree. If there are changes outside the brief and ticket documents, it asks whether to commit them before continuing; continuing as is mixes earlier changes into the review. Changes that are in no finished ticket's "바꾼 파일" (changed files) may be the unfinished work of an interrupted ticket, so it shows them separately and asks whether to revert them or keep building on them.
2. **Read the context**: it reads the ticket and the full brief, the completion records and output artifacts of finished tickets in the same brief, and the repo rules (CLAUDE.md, AGENTS.md, the documents they point to, `.claude/skills/`), and checks the verification commands and commit rules. Even when continued from run-flow with the conversation that made the brief still in the session, it relies only on the brief, the ticket, and the completion records of earlier tickets. If an earlier ticket's output artifact that the done criteria refer to cannot be found, it stops instead of making it again.
3. **Implement**: this session implements "만들 것" (what to build) itself. It does not hand the implementation to a subagent or another agent; the only exception is the workers of a parallel run. It writes tests when the repo rules require them or when the changed behavior already has tests. It does not fix problems outside the ticket's scope and leaves them in the report. If run-flow passed the protected path check, files on the [protected list](run-flow.md#protected-list) are not edited even through the shell; if a criterion can pass only by editing one, it stops and asks.
4. **Check done criteria**: it checks each done criterion with a command or observation, and runs the full test suite once at the end if there is one. Tickets marked `(통합 브랜치 공유)` (shared integration branch) in their blocked-by relations do not run the full suite; only the last "통합 및 검증" (integration and verification) ticket checks that everything passes. This session also checks criteria that must be seen on screen. If it has a way to drive a browser or capture the screen, it opens the screen and keeps the evidence (URL opened, actions taken, capture path); an item it could not check does not count as a pass and goes under "확인 못 한 것" (could not check).

   If a criterion fails, it works out the cause in the same session, fixes it, and checks again. It notes what changed and why each attempt failed, so it does not repeat the same approach. If the criterion still fails on the third attempt, counting the first, it leaves the ticket status unchanged and stops. It reports the failed criteria, the attempt count, and the causes (and, when run-flow called it, writes them on the state file's `- 멈춘 이유:` (stop reason) line), then asks whether to split the ticket again. If a stronger model is needed, you can switch the session model and run again.
5. **Review**: this session runs the code review and the rule check itself, one after the other, fixes findings within the ticket's scope, checks step 4 again, and then hands the [cross review](#cross-review) out once. The cross review is the only review handed to a new context.
   - **Code review**: it uses the first method that applies: the review skill named in the repo rules, the `code-review` (or `<plugin>:code-review`) skill, or its own review. If a review skill tells it to start subagents for sub-reviews, this session does them itself, one by one; if the skill cannot run that way, it does not use the skill, reviews the change itself, and says so in the report.
   - **Rule check**: check-guidelines checks the changed files. If the skill is not available, it skips the check and says so in the report.

   The review covers the uncommitted changes and new files since the HEAD at work start (or the base commit the caller passed). In a parallel run it covers the commits from the HEAD at work start, and when there are both commits and uncommitted changes, it covers both.
6. **Completion record**: done only after every cross-review result is verified.
   1. If run-flow passed the protected path check, it first runs `verify`. If that fails, it does not accept the ticket; it shows the output without reverting the changed files and stops. If it passes, the tests this ticket created are added to the list.
   2. It writes the [completion record](#output). A docs ticket gets it at the end of the ticket file (or the brief, for a brief without `## 티켓` (tickets)); a GitHub ticket gets it in a temporary file.
   3. It runs the cross-review gate (`scripts/cross_review.py gate`) on that record. The gate refuses if the record has no `- 교차 리뷰:` (cross review) line or the line's code fingerprint differs from the current code; then the status stays as it is and the review is done again.
   4. If the gate passes, a docs ticket is set to `- 상태: done` (status: done) and its passed criteria to `- [x]`; a GitHub ticket gets the record as a comment and is closed. The ticket is checked off in the brief's `## 티켓` (tickets), or in "남은 일" (remaining work) if there is no such section.
   5. For the last ticket, it runs the brief's "확인 기준" (verification criteria), reports the results, and closes the brief. A docs brief shows it is done by having every checkbox checked.

   If the repo rules or the run-flow state file's `## 결정` (decisions) define a completion value other than `done`, it uses that value both when reading and when writing. When running multiple tickets, the cross-review line, the gate, and the last-ticket work happen once, after the integrated review.

Even if the repo rules require commits, it does not commit and leaves that to you; the only exception is the parallel run. If the ticket and the repo rules conflict, it asks before continuing. The priority is the ticket's "하면 안 되는 것" (what not to do) and "작업 경계" (work boundaries), then the repo rules, then the skill's default behavior.

### Cross review

Models from the same company tend to miss the same mistakes, so a read-only review goes to a model from a different company than the implementing model. The implementing model is this session's model, or, in a parallel run, the model of the worker that implemented the ticket. The reviewer does not talk to you and does not decide the next step. There is no way to finish step 5 without a cross review.

- **What it passes**: the diff range to review (the HEAD at work start and the commands that read the change), the full brief (and the full ticket when one ticket is reviewed), the criteria, and the checks to run. The criteria are bugs, violations of the ticket's "하면 안 되는 것" (what not to do) and "작업 경계" (work boundaries), and violations of the repo rules; if the change touches authentication, authorization, payments, or personal data, security is added. The checks are the ticket's done criteria, plus the brief's "확인 기준" (verification criteria) for the last ticket or the integrated review. The reviewer runs the commands itself, so acceptance does not rest on the implementing session's own check. Secrets and raw logs are not passed.
- **Permissions**: the reviewer does not edit files, commit, or write outside the repository. A check command that changes repository files (snapshot updates, a formatter's write mode, and so on) is not run and is reported as `확인 못 함` (could not check). This session compares the code fingerprint right before the call and right after the result; if it changed, it does not use that result, shows you what changed, and hands the review to the next means.
- **What it gets back**: only the name of the model that ran the review, the findings (criterion, severity, file and line, evidence, how to fix), and for each check `met`, `unmet`, or `확인 못 함` (could not check) with the command run and a short result. No summary, overall verdict, or fix diff.
- **Verifying the result**: this session reproduces each finding or checks it against the source and records it as `수용` (accepted), `기각(사유)` (rejected, with reason), or `범위 밖` (out of scope). For an `unmet` check it runs the command again and fixes the cause if it reproduces. If the reviewer's verdict differs from the step 4 result, the difference goes in the completion record. After fixing accepted findings, it checks step 4 again. A report with no findings is not enough to accept.

**Model and means**: no model name is fixed. Each time, it uses the first that works in this order. Not having another company's model is no reason to stop.

1. The model or means you or the caller named for this run
2. A cross-review agent or model set in the repo or agent rules files, the harness settings, or a saved agent profile, or the "교차 리뷰 워커" (cross-review worker) of a named or registered worker tool procedure
3. Another company's model chosen from the providers, models, and agents this session can use. It tells you what it picked.
4. A substitute review in a new context on the same company's model. What it passes and how the result is verified are the same.

The review is started as one read-only subagent in a new context, and if the model can be set, it is set even for number 4. With a worker tool procedure, it starts in the current working tree as the procedure's "교차 리뷰 워커" (cross-review worker) says. If there is no response or the result cannot be read, it moves to the next means. Independence is judged by the model that actually ran the review, confirmed from the calling tool's run information or the means' settings, not from the name the reviewer wrote. If that model is from the same company, it moves to the next means; if only number 4 is left, that review counts as the substitute. If it cannot start any new context, this session substitutes a self review: it reads the diff again from the start and reruns the checks.

**Code fingerprint and gate**: `scripts/cross_review.py` produces them.

- `fingerprint` prints the code fingerprint of the working tree. It includes uncommitted changes and new files, and since it is a tree hash, committing alone does not change it. It leaves out `docs/context/run-flow/` (state files and protected lists), the brief given with `--brief` and its ticket folder, and paths given with `--exclude`, so editing completion records does not change it. If the tree hash cannot be computed, it falls back to a fingerprint built from HEAD, status, and diff.
- `record` builds the completion record's `- 교차 리뷰:` (cross review) line from the fingerprint taken after verification and fixes. If the model that ran the review cannot be confirmed, the model slot says `수행 모델 확인 불가: <means used>` (model could not be confirmed).
- `gate` passes only if, for each record, the last `- 교차 리뷰:` line is done or substituted and its fingerprint equals the current one.

The `- 교차 리뷰:` line is one of three. A substitute review is not an independent check, so the report carries the substitution mark for you to judge, and when run-flow called it, the state file's `- 교차 리뷰 모델:` (cross review model) line gets it too.

- Another company's model: `- 교차 리뷰: 완료 (<model that ran it>, 코드 지문 <fingerprint>)` (done)
- Substituted with the same company's model: `- 교차 리뷰: 대체 (같은 회사 모델 <model that ran it>, 코드 지문 <fingerprint>)` (substituted, same company's model)
- Substituted with a self review: `- 교차 리뷰: 대체 (새 컨텍스트 없음, 메인 세션 자기 리뷰, 코드 지문 <fingerprint>)` (substituted, no new context, main session self review)

### Running multiple tickets

If you ask for a number range or "all remaining tickets", it follows `references/multi-ticket.md`. The default is the **sequential run**, where this session implements the tickets itself, one at a time. The **parallel run** can be chosen only when you or the caller named a worker tool procedure for this run, or one is registered in the repo or agent rules, and all of the following must hold. If any does not, it runs sequentially.

- At some point two or more tickets can start together by their blocked-by relations. If the relations form a single chain, parallel runs add only worktree and merge costs.
- No target ticket has `(통합 브랜치 공유)` (shared integration branch) in its blocked-by relations.
- A usable worker tool procedure exists. It uses the first one whose "사용 조건" (usage conditions) are met, looking first at the procedure for the tool you or the caller named, then at procedures named in the rules (in the order the rules list them). A resumed run uses the procedure of the tool named in the recorded worker identifier.

A worker tool procedure is a document that describes how to create, wait for, and clean up workers with one worker tool. Answers to questions, new design decisions, attempt records of failed tickets, and worker identifiers are recorded as they happen: in the record file the caller passed (the state file, for run-flow), or else told to you in one line and repeated in the final report.

**Sequential run**: it checks the working tree once, shows the order set by blocked-by relations and numbers, and runs steps 2, 3, 4, and 6 for each ticket. It writes one ticket's completion record before starting the next, and since the tickets edit the same working tree, it never works on two at once. If a ticket fails its done criteria, it stops by the step 4 rule and does not start later tickets. When all are done, it runs the integrated review below.

**Parallel run**: for each ticket, a worker implements and commits on a new branch in a worktree branched from the current branch. A new worktree sees only committed content, so this is the only path that creates commits. This session acts as the coordinator: it keeps the blocked-by order, merges finished branches, writes completion records, and calls the cross review.

1. **Prepare**: the working tree must be clean. If the only uncommitted files are brief and ticket documents, it asks whether to commit them; if there are other changes, it asks you to clean them up and run again, and stops.
2. **Plan approval**: it shows the execution groups, the tool to start workers with and where its procedure was named, the branch to merge into, the number of concurrent workers (3 by default), and the HEAD at work start, and asks for approval. If the current branch is the default branch, it also asks whether to create a work branch.
3. **Resume**: if workers from an earlier run remain, it takes them over instead of starting new ones, since starting again would implement the same ticket twice. A ticket that finished but was not merged is merged first, and an interrupted merge is undone with `git merge --abort` before handling. If a done ticket that blocks others has no `- 교차 리뷰: 완료 (...)` (done) or `- 교차 리뷰: 대체 (...)` (substituted) line, it runs that cross review before starting the blocked tickets. A `- 교차 리뷰: 건너뜀 (...)` (skipped) line left by an earlier run counts as not reviewed.
4. **Start workers**: it starts workers, up to the concurrent limit, for tickets whose blockers are all merged and cross-reviewed. A worker does only run-ticket's steps 2, 3, and 4; if they pass, it commits to the ticket branch and reports the done criteria results, changed files, output artifacts, branch, and commit hash. It does not edit files on the protected list, even through the shell. Earlier decisions and answers to worker questions go into the instructions of workers started later.
5. **When a worker finishes**, it handles the result.
   - **Pass**: it merges with `git merge --no-ff --no-commit` and runs the repo's verification commands (type check, lint, tests) before creating the merge commit. Changes that conflict with earlier merged tickets show up here. It then runs the protected path check (`verify --rev <ticket branch>`), adds the new tests to the list, and creates the merge commit with the completion record. The record's commit line is ``- 커밋: 티켓 브랜치 `<branch>`의 `<hash>`를 머지`` (merged commit `<hash>` of ticket branch `<branch>`). A GitHub ticket is closed after the merge commit exists, and the worker and its worktree are cleaned up as the procedure's "정리" (cleanup) says.
   - **Verification or protected path check fails**: it undoes the merge, starts no new worker, and stops, keeping that ticket's worktree. If the integration verification failed, before stopping this session reads the failure output and both sides' changes and shows which side's change the failure seems to come from, with the evidence.
   - **Cross review of a blocking ticket**: if the merged ticket blocks other tickets, it runs only the cross review on that merge commit's diff (`HEAD^..HEAD`) before starting the blocked tickets, because later tickets built on a defect widen what has to be fixed. It fixes accepted findings and commits them together with the `- 교차 리뷰:` (cross review) line added to that ticket's completion record.
   - **Merge conflict**: it undoes the merge and asks that worker to rebase onto the current branch and check again. If it conflicts again, it stops that ticket and tells you.
   - **Failure**: that ticket and the tickets it blocks are not started. Running workers are waited for and merged.
   - **Question**: it answers from the brief and tickets if it can; otherwise it asks you and passes the answer to the same worker.
6. When all workers are done, it runs the integrated review below and reports the per-ticket results and the commits it made. You decide on push, PR, and merging into the default branch.

**Integrated review**: when all tickets are done, it runs the step 5 review once on the whole change since the HEAD at work start (commits, uncommitted changes, new files) and checks again the done criteria of tickets the fixes touched. In a parallel run it commits the fixes. If it received the protected path check, it runs `verify` again. A cross-review line is added to the completion record of each ticket in the reviewed change (in a sequential run, a review done again replaces the line). In a parallel run it is added even to tickets that already have a line from a blocking-ticket review, because later merges made that line's fingerprint stale and the gate reads the last line. It runs the gate once on all those tickets; if it refuses, it reviews again the changes of tickets with no line or a different fingerprint. If it passes, it runs the brief's "확인 기준" (verification criteria) on the combined result of all tickets and closes the brief.

**What a worker tool procedure defines**: commands and notifications differ by tool, so it follows the chosen procedure. The procedure fills in the items below with that tool's methods. The conditions for each item are in "워커 도구 절차" (Worker tool procedure) in `references/multi-ticket.md`, and examples are [`extras/orca/worker-procedure.md`](../../../extras/orca/worker-procedure.md) and [`extras/paseo/worker-procedure.md`](../../../extras/paseo/worker-procedure.md).

- **Usage conditions**: how to check that this session can start workers with the tool
- **Creating workers**: how to create a new worktree and branch from the current branch's local ref when the worker starts, and the order for choosing the worker's model and effort
- **Waiting**: how to be notified when a worker finishes, asks, stops, or requests a permission. It does not poll status.
- **Judging the end**: how to sort notifications and the last report into pass, question, and failure. It is a pass only if the reported commit is on the ticket branch.
- **Sending to the same worker**, **Resuming**, **Cleanup**, **Worker identifier**: how to send answers and rebase requests to that worker, how to find remaining workers from the recorded identifier, how to clean up the worker and worktree after the merge (keeping those of failed tickets), and the tool name and ID to record
- **Cross-review worker**: how to start a worker on another company's model in the current working tree as read-only and hand it the cross review. The procedure does not fix the model, and starts no worker if no other company's model can be chosen.

## Output

- The implemented code changes. Not committed; a parallel run creates one merge commit per ticket.
- A completion record attached to the ticket in the format below (a comment for GitHub tickets). Lines that do not apply are removed. `## 산출물` (output artifacts) holds results that "만들 것" (what to build) or the done criteria ask to keep and results other tickets refer to as "NN 티켓의 산출물" (ticket NN's output), as text or as a repository path; the section is removed if there are none.

  ```markdown
  ## 완료 기록
  - 완료일: YYYY-MM-DD
  - 커밋: 안 함 (작업 시작 HEAD `<해시>`)
  - 바꾼 파일: `<경로>`, `<경로>`
  - 확인한 것: `<명령>` → <결과> (확인한 HEAD `<해시>`, 커밋 전이면 "작업 트리")
  - 확인 못 한 것: <기준>: <이유>
  - 교차 리뷰: 완료 (<수행한 모델>, 코드 지문 <지문>)
  - 교차 리뷰 지적: <지적>: <수용 / 기각(사유) / 범위 밖>
  - 교차 리뷰 기준 판정: <기준>: <met / unmet / 확인 못 함> (4단계 결과와 다르면 그 차이)
  - 고치지 않은 지적: <지적>: <이유>

  ## 산출물
  <내용 또는 저장소 경로>
  ```

  The lines are, in order: completion date; commit (not committed, with the HEAD at work start); changed files; what was checked (command, result, and the HEAD checked, or "작업 트리" (working tree) before commit); what could not be checked and why; the cross-review line; the verdict on each cross-review finding; the reviewer's verdict on each check (and how it differs from step 4); findings not fixed and why.
- A report: finished ticket, done criteria results, changed files, output artifact location, the model that ran the cross review and the substitution mark, the cross-review findings and check verdicts, the gate result, review findings not fixed, skipped reviews and why (a rule check that could not run, or a review skill that was not used), the next ticket, and a note that you do the commit

## Customize

| What to change | Where to edit |
|---|---|
| Ticket selection rules | SKILL.md "1. 티켓 고르기" (1. Pick a ticket) |
| Retry limit for done criteria (3 attempts) | SKILL.md "4. 완료 기준 확인" (4. Check done criteria) |
| Priority of review methods, what the cross review gets and returns | SKILL.md "5. 리뷰" (5. Review) |
| Model or means for the cross review | Name it when you run the skill, or write it in the repo or agent rules (CLAUDE.md, AGENTS.md), the harness settings, or a saved agent profile. The order is in SKILL.md "5. 리뷰" (5. Review) |
| Code fingerprint, `- 교차 리뷰:` line, completion gate | `scripts/cross_review.py` |
| Completion record format | SKILL.md "6. 완료 기록" (6. Completion record) |
| Ticket completion value (instead of `done`) | The repo rules or the run-flow state file's `## 결정` (decisions) |
| Conditions for choosing the method, number of concurrent workers, merge method, items a worker tool procedure defines, sequential run | `references/multi-ticket.md` |
| Worker tool for the parallel run | Register a worker tool procedure in the repo or agent rules (CLAUDE.md, AGENTS.md) |
| Model and effort of implementation and cross-review workers | Wherever the chosen worker tool procedure looks. Orca and Paseo use the worker model lines of the registration text pasted into the rules file, and Paseo also looks at saved agent profiles ([Orca](../../../extras/orca/register.md), [Paseo](../../../extras/paseo/register.md)) |

To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **set-brief**, **set-ticket**: create the brief and tickets to run.
- **run-flow**: uses this skill in its stage 5 to run the brief's remaining tickets, and passes the state file and the protected path check commands.
- If the **code-review** skill is installed, it is used for the code review in step 5.
- **check-guidelines**: used for the rule check in step 5.

---

← Previous: [set-ticket](set-ticket.md) · [All docs](../README.md) · Next: [analyzing-requirements](analyzing-requirements.md) →
