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
- To run several tickets in parallel, the repo or agent rules (CLAUDE.md, AGENTS.md) must name a worker tool procedure. A worker tool procedure is a document that describes how to handle workers with one worker tool. If no usable procedure exists, or fewer than two tickets can start together, tickets run in order.
- Optional setup examples: [Orca orchestration setup](../orca-orchestration.md), [Paseo orchestration setup](../paseo-orchestration.md). Each guide explains how to install the tool and register its procedure in a rules file.
- To open a PR, you need a github.com remote and a logged-in `gh` CLI. Otherwise it shows the PR description and stops.
- To use a different model at each stage, install the [omp multi-agent setup](../omp-orchestration.md).

## How it works

0. It picks the starting stage from the argument and creates a state file. A state file starts at its current stage, a brief at stage 4 to 6 depending on its ticket status, a requirements document or a request sentence at stage 2, and a planning document at stage 1. State files and briefs are also Markdown documents, so they are checked before the planning-document rule. Without an argument it looks for unfinished state files, then unfinished briefs, and if there are several, lists them for you to choose. Given a folder, it looks inside it the same way. If you ask it to bring work done outside a flow into a flow, it judges each brief's current stage, creates state files, and asks whether to continue. If the repo rules or the state file define a completion status other than `done`, that value also counts as finished.
1. **Requirements**: analyzing-requirements turns the planning document into a requirements document. Answers you give to the skill's questions are written to the state file as soon as they arrive, so they are not asked again if the flow breaks before the document is saved.
2. **Framing**: if there are several development scopes, you pick one for this run, and the scopes you did not pick are written to the state file. Then framing-problems confirms a framing record. Each field is written to the state file as soon as it is confirmed, so if the flow breaks midway, answers you already gave are not asked again. If the flow breaks before the brief is written, it resumes from stage 3 with that record.
3. **Brief**: set-brief records the brief. A subagent given the framing record from the state file drafts and cold-reads it; run-flow itself picks the storage location, confirms the draft with you, and publishes it. If the agent rules name an agent for the draft and the cold-read check, it uses that agent. The draft file path and the cold-read result file path are written to the state file, so if the flow breaks before you confirm, the draft is not made again and the remaining mismatches are still shown. If the remaining work will not fit in one session, it goes to stage 4; otherwise to stage 5.
4. **Tickets**: set-ticket splits the brief into tickets and publishes them. When publishing ends, it asks whether to continue stage 5 in this session or in a new session with `/run-flow <state file>`. A new session does not reread the conversation so far, which lowers cost.
5. **Implementation and review**: if the current branch is the default branch, it first asks for a work branch name and creates it. It writes the starting HEAD to the state file and asks whether to bundle the uncommitted flow documents (state file, requirements document, ADRs, brief, tickets) into one commit. Then run-ticket runs all remaining tickets. If a usable worker tool procedure exists and two or more tickets can start together, it starts one worker per ticket and runs them in parallel. Even a single ticket goes to a worker or subagent with a fresh context, so the implementer works from the brief and ticket alone, without this conversation. Answers given to worker questions and decisions made during implementation are written to the state file as they happen and passed to workers started later. If a ticket fails its done criteria, it stops, writes the agents tried and the attempt count to the state file, and asks whether to split the ticket again. The integrated review result is written to the state file as soon as it arrives, with the reviewed HEAD and the code fingerprint. The review covers everything since the starting HEAD: commits, uncommitted changes, and new files.
6. **Merge and PR decision**: it first compares the code fingerprint in the state file with the current one. If they differ, the code changed after the review, so it says so and reviews again first. Then it collects done criteria results, review findings, changed files, and commits, and asks you to choose: open a PR, fix something, or stop. When it starts at stage 6 without a run-ticket report, it collects them from the state file's review record, the tickets' completion records, and the git history.
7. **Open the PR**: if needed, it creates a work branch and commits, checks that no changes are left, then writes the PR description, shows it to you for confirmation, pushes, and opens the PR. When an agent writes the PR description, it gets the brief, the changed-file list, the completion records, and the review record instead of the full diff.

Every confirmation a stage skill asks (confirming the framing record, where to save the requirements document, the brief draft and where to publish it, the ticket split, the parallel run plan) is still asked. What run-flow asks itself is the work branch name, the flow-document commit, the session choice after stage 4, the choice at stage 6, and the PR description confirmation at stage 7. What run-flow removes is running the next skill yourself each time a stage ends.

### State file and ADRs

Each flow keeps a state file at `docs/context/run-flow/YYYY-MM-DD-<slug>.md`, updated at every stage change. It holds the current stage, stop reason, stage checklist, output locations (requirements document, brief, brief draft, brief cold-read result, ADRs, branch, starting HEAD, worker identifier, PR), your decisions, requirements answers, the framing record, decisions made during implementation, and the review record. The code fingerprint, computed by `scripts/code_fingerprint.sh`, is the tree hash of the working tree without the flow documents: it includes uncommitted changes and new files, and stays the same when only flow documents change. Even if the conversation breaks or is compacted, open this file or run `/run-flow status` to see where the flow is. Stage 5 progress follows ticket status; if the state file disagrees, it is corrected to match the tickets. But if all tickets are done and no integrated review is recorded, it resumes from the review in stage 5. The state file of a finished flow is not rewritten, so running a different development scope from the same requirements document creates a new state file.

You may also keep the state file elsewhere, for example next to the brief. Without an argument it finds state files by their `- 현재 단계:` (current stage) line, and when looking for briefs and state files it follows symlinked folders such as `.scratch`. When several reviews run together, each result is written to the state file as it arrives. If the requirements change mid-flow, it does not start a new flow: it goes back to stage 1 in the same state file, asks only about the framing fields that changed, and updates the brief and the remaining tickets.

At stages 2 and 6, only decisions that are hard to reverse, surprising without context, and chosen among real alternatives are offered as ADR candidates. Only the ones you pick are saved in the repo's ADR folder (or `docs/adr/NNNN-<slug>.md` if none) and linked from the state file.

## Output

- A state file, a requirements document, a brief, tickets, ADRs, the implemented code, and commits
- A GitHub PR. You do the merge.
- A final report: where each stage's output is, the PR URL, and review findings not fixed

## Customize

| What to change | Where to edit |
|---|---|
| Starting stage per argument | SKILL.md "0. 시작 단계 고르기" (0. Pick the starting stage) |
| State file location and rules | SKILL.md "상태 파일" (State file) |
| State file format | `assets/state-file.md` |
| ADR criteria and format | `references/adr.md` |
| How the brief draft is handed to a subagent | `references/brief-stage.md` |
| What to collect and offer at stage 6 | `references/merge-stage.md` |
| What to do when the requirements change | `references/requirement-change.md` |
| How tickets run | run-ticket's SKILL.md, or name a ticket execution skill in the repo rules |
| PR description format, PR creation order | The repo's PR template, or `references/pr-stage.md` |
| How the code fingerprint is computed | `scripts/code_fingerprint.sh` |

Behavior inside a stage is changed in that stage's skill. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **analyzing-requirements**, **framing-problems**, **set-brief**, **set-ticket**, **run-ticket**: the skills it loads at each stage. set-brief, set-ticket, and run-ticket are Model-invoked so that run-flow can load them, and they run only when you or another skill asks for them.

---

← Previous: [check-guidelines](check-guidelines.md) · [All docs](../README.md) · Next: [set-brief](set-brief.md) →
