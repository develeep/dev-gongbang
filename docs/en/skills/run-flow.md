<p align="right"><a href="../../skills/run-flow.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › run-flow

# run-flow

Takes a planning document, a request, or a brief and runs the development stages in order, from organizing requirements to opening a PR. It loads the skill for each stage itself, so you do not run each stage's skill by hand. You only answer the confirmations and questions each skill asks.

> This skill is in progress. Install `gongbang-dev` to use it. Its behavior may change.

| Field | Value |
|---|---|
| Bucket | in-progress |
| Invocation | User-invoked |
| Command | `/gongbang:run-flow [planning doc path/link \| request \| brief path/issue number]` |
| Source | [SKILL.md](../../../skills/in-progress/run-flow/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

- You want to go from a planning document or a request to a PR, answering only confirmations and questions along the way.
- You want to finish a flow that stopped partway. Run it without an argument and it finds an unfinished state file, or failing that an unfinished brief, and continues.
- You want to see which stage a running flow is at. With `status`, it shows only the current stage, stop reason, and remaining ticket count of each unfinished flow, then ends.
- You run several features at once. Create one worktree per feature and run run-flow in each.

## Prerequisites

- The stage skills: analyzing-requirements, framing-problems, set-brief, set-ticket, run-ticket. Installing `gongbang` and `gongbang-dev` together provides all of them.
- By default, the session that runs run-flow implements the tickets itself, one after another. Parallel runs are optional. To run several tickets in parallel, you must name a worker tool procedure, or the repo or agent rules (CLAUDE.md, AGENTS.md) must name one. A worker tool procedure is a document that describes how to handle workers with one worker tool. If no usable procedure exists, fewer than two tickets can start together, or tickets share an integration branch, tickets run in order.
- Optional setup examples: [Orca orchestration setup](../orca-orchestration.md), [Paseo orchestration setup](../paseo-orchestration.md). Each guide explains how to install the tool and register its procedure in a rules file.
- To open a PR, you need a github.com remote and a logged-in `gh` CLI. Otherwise it shows the PR description and stops.
- If you use omp, install the [omp multi-agent setup](../omp-orchestration.md) for the cross-review and cold-read agents and the delegation rules. The repo does not pin a model; you choose it.

## How it works

0. It picks the starting stage from the argument and creates a state file. A state file starts at its current stage, a brief at stage 4 to 6 depending on its ticket status, a requirements document or a request sentence at stage 2, and a planning document at stage 1. State files and briefs are also Markdown documents, so they are checked before the planning-document rule. Without an argument it looks for unfinished state files, then unfinished briefs, and if there are several, lists them for you to choose. Given a folder, it looks inside it the same way. If you ask it to bring work done outside a flow into a flow, it judges each brief's current stage, creates state files, and asks whether to continue. If the repo rules or the state file define a completion status other than `done`, that value also counts as finished.
1. **Requirements**: analyzing-requirements turns the planning document into a requirements document. Answers you give to the skill's questions are written to the state file as soon as they arrive, so they are not asked again if the flow breaks before the document is saved.
2. **Framing**: if there are several development scopes, you pick one for this run, and the scopes you did not pick are written to the state file. Then framing-problems confirms a framing record. Each field is written to the state file as soon as it is confirmed, so if the flow breaks midway, answers you already gave are not asked again. If the flow breaks before the brief is written, it resumes from stage 3 with that record.
3. **Brief**: set-brief records the brief. The session running run-flow does every step itself: picking the storage location, drafting, the cold-read check, confirming the draft with you, and publishing. Only the three cold-read readers are started in fresh contexts that do not know the conversation. If the agent rules name an agent for the cold-read check, it uses that agent. The draft is written to a temporary file outside the repository. The draft file path and the cold-read result file path are written to the state file, so if the flow breaks before you confirm, the draft is not made again and the remaining mismatches are still shown. If you asked to split the work into tickets, it goes to stage 4 whatever the size. Otherwise, if the remaining work will not fit in one session, it goes to stage 4; otherwise to stage 5.
4. **Tickets**: set-ticket splits the brief into tickets and publishes them. When publishing ends, it asks whether to continue stage 5 in this session or in a new session with `/run-flow <state file>`. A new session does not reread the conversation so far, which lowers cost.
5. **Implementation and review**: if the current branch is the default branch, it first asks for a work branch name and creates it. It writes the starting HEAD to the state file, builds the protected list from the tests and judge cases at the starting HEAD, and asks whether to bundle the uncommitted flow documents (state file, protected list, requirements document, ADRs, brief, tickets) into one commit. Then run-ticket runs all remaining tickets. If a usable worker tool procedure exists, two or more tickets can start together, and no tickets share an integration branch, it starts one worker per ticket and runs them in parallel. Otherwise this session implements the tickets itself, one after another. Answers given to questions during implementation and newly made decisions are written to the state file as they happen and applied to later tickets. In a parallel run, worker identifiers are written to the state file too. If the repo rules name another skill for running tickets, it uses that skill only when it can confirm that the skill does not hand off implementation and does not skip the cross review; otherwise it uses run-ticket. If a ticket fails its done criteria, it stops, writes the attempt count and the cause of failure to the state file, and asks whether to split the ticket again. The integrated review result is written to the state file as soon as it arrives, with the reviewed HEAD and the code fingerprint. The review covers everything since the starting HEAD: commits, uncommitted changes, and new files. Before accepting each ticket it checks that no file on the protected list changed, and adds the new tests of the accepted ticket to the list.
6. **Merge and PR decision**: it first checks the protected list again, then compares the code fingerprint in the state file with the current one. If they differ, the code changed after the review, so it says so and reviews again first. Then it collects done criteria results, review findings, changed files, and commits, and asks you to choose: open a PR, fix something, or stop. If you choose to open a PR, it closes the protected list before committing. When it starts at stage 6 without a run-ticket report, it collects them from the state file's review record, the tickets' completion records, and the git history.
7. **Open the PR**: if needed, it creates a work branch and commits, checks that no changes are left, then writes the PR description, shows it to you for confirmation, pushes, and opens the PR. This session writes the PR description itself from the brief, the changed-file list, the completion records, and the review record instead of the full diff. If the cross review was substituted (for example by a model from the same company), the description carries that mark and the model that ran the review.

Every confirmation a stage skill asks (confirming the framing record, where to save the requirements document, the brief draft and where to publish it, the ticket split, the parallel run plan) is still asked. What run-flow asks itself is the work branch name, the flow-document commit, the session choice after stage 4, the choice at stage 6, and the PR description confirmation at stage 7. What run-flow removes is running the next skill yourself each time a stage ends.

### State file and ADRs

Each flow keeps a state file at `docs/context/run-flow/YYYY-MM-DD-<slug>.md`, updated at every stage change. It holds the current stage, stop reason, stage checklist, output locations (requirements document, brief, brief draft, brief cold-read result, ADRs, branch, starting HEAD, worker identifier filled only in parallel runs, PR), your decisions, requirements answers, the framing record, decisions made during implementation, and the review record. The code fingerprint, computed by `scripts/code_fingerprint.sh`, is the tree hash of the working tree without the flow documents: it includes uncommitted changes and new files, and stays the same when only flow documents change. From stage 5 until you choose to open a PR in stage 6, the protected list sits in the `.protected` file of the same name, and a resumed session keeps using it; see "Protected list" below. Even if the conversation breaks or is compacted, open this file or run `/run-flow status` to see where the flow is. Stage 5 progress follows ticket status; if the state file disagrees, it is corrected to match the tickets. But if all tickets are done and no integrated review is recorded, it resumes from the review in stage 5. The state file of a finished flow is not rewritten, so running a different development scope from the same requirements document creates a new state file.

You may also keep the state file elsewhere, for example next to the brief. Without an argument it finds state files by their `- 현재 단계:` (current stage) line, and when looking for briefs and state files it follows symlinked folders such as `.scratch`. When several reviews run together, each result is written to the state file as it arrives. If the requirements change mid-flow, it does not start a new flow: it goes back to stage 1 in the same state file, asks only about the framing fields that changed, and updates the brief and the remaining tickets.

At stages 2 and 6, only decisions that are hard to reverse, surprising without context, and chosen among real alternatives are offered as ADR candidates. Only the ones you pick are saved in the repo's ADR folder (or `docs/adr/NNNN-<slug>.md` if none) and linked from the state file.

### Protected list

It keeps the implementing session from passing by editing existing tests. At the start of stage 5, `scripts/protected_paths.py init` finds the test files at the starting HEAD (files under `tests/`, `test/`, `__tests__/`, `spec/`, and names such as `test_*.py`, `*_test.go`, `*.test.ts`, `*.spec.js`, `*Test.java`) and writes them to `docs/context/run-flow/<state file name>.protected`. Other tests or judge cases named by the repo rules (eval cases, grading criteria, expected outputs) are added with `--path`. A copy of the list is kept in the git common directory (`.git/gongbang-protected/`), so a shell edit of the list itself is caught too.

- **Blocking before the write**: with [gongbang-mods](../mods.md#run-flow-protected-path-blocking) (Claude Code) and the [omp extension](../omp-orchestration.md#protected-path-blocking) installed, a write tool such as Write or Edit is refused before it runs when it targets a file on the list, and gets the reason back. Subagents and workers are covered the same way. Relative paths, absolute paths, symlinked paths, and paths in git worktrees inside the repository are resolved to their real path before comparing. New files and files off the list are written as usual.
- **Check before acceptance**: writes through shell commands (`sed -i`, redirects) cannot be blocked. So before run-ticket accepts a ticket, and when stage 6 starts, `protected_paths.py verify` compares the working tree, the index (staged content), HEAD, and in a parallel run the worker's ticket branch with the starting content. If a file changed, was deleted, or a new file appeared in a protected folder, or the check itself fails, the ticket is not accepted and the flow stops. Changed files are shown, not reverted.
- **When it is on**: while the state file's `- 현재 단계:` (current stage) is not `완료` (done). Finished flows and work outside a flow are not blocked, and the write blocking does not run `python3` for them. A list whose state file is gone counts as on.
- **Closing**: the list is committed as a flow document, so if it is merged as is, it stays on in the default branch and blocks writes to existing tests there. So when you choose to open a PR in stage 6, `close` runs `verify` once more and, if it passes, deletes the list and its copy. The deletion goes into the PR commit.
- **Changing the list**: when stage 5 starts and the brief or a ticket asks to change an existing test on the list, it shows that file and removes only the files you choose with `remove`. Accepted tests are added with `add`. If a requirements change during implementation needs an existing test to change, the flow stops and, after you decide, the file is removed with `remove`. When a flow resumes in another clone without the copy, `init` stops; after you confirm the list, `--reseal` writes the copy again.
- Without the blocking installed, only the check before acceptance remains. Where you cannot tell whether blocking is on, such as an eval runner, do not judge blocking from the tool call log alone: refused calls are logged too. To confirm blocking, look at the refused tool result's reason and check that the file is unchanged.

## Output

- A state file, a requirements document, a brief, tickets, ADRs, the implemented code, and commits
- A GitHub PR. You do the merge.
- A final report: where each stage's output is, the PR URL, and review findings not fixed

## Customize

| What to change | Where to edit |
|---|---|
| Starting stage per argument | SKILL.md "0. 시작 단계 고르기" (0. Pick the starting stage); the decisions that docs files settle are in `scripts/start_stage.py` |
| State file location and rules | SKILL.md "상태 파일" (State file) |
| State file format | `assets/state-file.md` |
| ADR criteria and format | `references/adr.md` |
| How stage 3 handles the brief draft and the cold-read result | `references/brief-stage.md` |
| What to collect and offer at stage 6 | `references/merge-stage.md` |
| What to do when the requirements change | `references/requirement-change.md` |
| How tickets run | run-ticket's SKILL.md, or name a ticket execution skill in the repo rules (used only if it does not hand off implementation and runs the cross review) |
| PR description format, PR creation order | The repo's PR template, or `references/pr-stage.md` |
| How the code fingerprint is computed | `scripts/code_fingerprint.sh` |
| Test file name rules for the protected list, how the check works | `scripts/protected_paths.py` (keep `mods/gongbang-mods/hooks/protected_paths.py` identical) |

Behavior inside a stage is changed in that stage's skill. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **analyzing-requirements**, **framing-problems**, **set-brief**, **set-ticket**, **run-ticket**: the skills it loads at each stage. set-brief, set-ticket, and run-ticket are Model-invoked so that run-flow can load them, and they run only when you or another skill asks for them.

---

← Previous: [check-guidelines](check-guidelines.md) · [All docs](../README.md) · Next: [set-brief](set-brief.md) →
