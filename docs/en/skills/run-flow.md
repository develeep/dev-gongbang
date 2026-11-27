<p align="right"><a href="../../skills/run-flow.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › run-flow

# run-flow

Give it a planning document, a request, or a brief, and it runs the development stages in order, from organizing requirements to opening a PR. It loads each stage's skill for you, so you only answer the confirmations and questions those skills ask. Progress is kept in a state file, so if the conversation breaks, running run-flow again picks up at the stage where it stopped.

> This skill is in progress. Install `gongbang-dev` to use it. Its behavior may change.

| Field | Value |
|---|---|
| Bucket | in-progress |
| Invocation | User-invoked |
| Command | `/gongbang:run-flow [planning doc path/link \| request \| brief path/issue number \| state file \| status]`. Without an argument it continues the flow in progress |
| Source | [SKILL.md](../../../skills/in-progress/run-flow/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

- You want to go from a planning document or a request to a PR, answering only confirmations and questions along the way.
- You want to finish a flow that stopped. Run it without an argument and it finds an unfinished flow and continues.
- You want to see which stage a flow is at. With `status`, it shows the title, current stage, stop reason, and remaining ticket count of each unfinished flow, then ends.
- You want to continue a brief and tickets made outside run-flow. Pass the brief and it picks the starting stage from the ticket status.

## Prerequisites

- The stage skills analyzing-requirements, framing-problems, set-brief, set-ticket, and run-ticket. Installing `gongbang` and `gongbang-dev` together provides all of them.
- A git repository and `python3`. Picking the starting stage, the protected list, and the cross-review gate are `python3` scripts.
- To use briefs and tickets that are GitHub issues, or to open a PR, a github.com remote and a logged-in `gh` CLI. Without them, stage 7 shows the PR description and stops.
- A model from another company for the cross review. How to set it is in [run-ticket's cross review](run-ticket.md#cross-review). If you use omp, the [omp multi-agent setup](../omp-orchestration.md) installs the cross-review and cold-read agents and the delegation rules; you choose the models.
- Optional: write blocking for the protected list. Install [gongbang-mods](../mods.md#run-flow-protected-path-blocking) (Claude Code) or the [omp extension](../omp-orchestration.md#protected-path-blocking). What it does is in [Protected list](#protected-list).
- Optional: parallel runs. By default the session that runs run-flow implements the tickets itself, one after another. To run them in parallel with workers, name a worker tool procedure or register one in the rules. The conditions are in [run-ticket's running multiple tickets](run-ticket.md#running-multiple-tickets), and setup examples are the [Orca](../orca-orchestration.md) and [Paseo](../paseo-orchestration.md) orchestration guides.

## How it works

At the start it shows a checklist of stages 0 to 7 and updates it as each stage ends. When a stage ends, it says in one line that the next stage is starting and goes straight on. Between stages it passes outputs, such as the requirements document path or the brief path or issue number, instead of the conversation.

0. **Pick the starting stage**: it decides the [starting stage](#starting-stage) from the argument and the repository's documents, states the stage and the reason in one line, and creates a [state file](#state-file) or continues an existing one.
1. **Requirements**: analyzing-requirements turns the planning document into a requirements document. Answers you give to the skill's questions are written to the state file as soon as they arrive, so they are not asked again if the flow breaks before the document is saved.
2. **Framing**: if the requirements document has several development scopes, you pick one for this flow, because one brief holds one final goal. The scopes you did not pick stay in the state file; after this flow ends, run run-flow again with the requirements document to take them on. Then framing-problems confirms the framing record. Each confirmed field is written to the state file at once, so answers are not asked again if the flow breaks midway.
3. **Brief**: set-brief writes and publishes the brief. This session does every set-brief step itself and starts only the three cold-read readers in fresh contexts that do not know the conversation. If the agent rules name an agent for the cold-read check, it uses that agent. The draft goes to a temporary file outside the repository and the cold-read result to `<draft file name>.review.md` next to it, and both paths are written to the state file, so the draft is not made again if the flow breaks before you confirm it. After publishing, the next stage is decided this way: if you asked to split the work into tickets, stage 4 whatever the size; otherwise stage 4 if the "남은 일" (remaining work) will not fit in one fresh context window, and stage 5 if it will. The stage and the reason go into the state file's `## 결정` (decisions).
4. **Tickets**: set-ticket splits the brief into tickets and publishes them. Then it asks whether to continue stage 5 in this session or in a new session with `/gongbang:run-flow <state file>`. A new session does not reread the conversation so far, which lowers cost, and everything stage 5 needs is in the brief, the tickets, and the state file.
5. **Implementation and review**: if the current branch is the default branch, it asks for a work branch name and creates it. It writes the starting HEAD to the state file, builds the [protected list](#protected-list) from that HEAD and shows it, then asks whether to bundle the uncommitted flow documents (state file, protected list, requirements document, ADRs, brief, tickets, index `README.md`) into one commit. Then it runs all unfinished tickets with run-ticket's [running multiple tickets](run-ticket.md#running-multiple-tickets). The same holds for one ticket or a brief without `## 티켓` (tickets); if no ticket is left, it runs only the integrated review. By default this session implements the tickets itself, one after another; the parallel run is used only when you named a worker tool procedure or registered one in the rules.
   - Answers to questions during implementation and new design decisions are written to the state file's `## 구현 중 결정` (decisions during implementation) as they happen and applied to later tickets as they are.
   - If a ticket fails its done criteria, the flow stops. It writes the ticket, the attempt count, and the causes on `- 멈춘 이유:` (stop reason) and asks whether to split the ticket again (back to stage 4). If a stronger model is needed, switch the session model and run again with the state file.
   - The integrated review result is written to `## 리뷰` (review) as soon as it arrives, with the reviewed HEAD and the [code fingerprint](#state-file). If the run-ticket report does not show the cross-review gate passing, it is not recorded as done and the review is handed back to run-ticket.
6. **Merge and PR decision**: it first checks the protected list again and compares the code fingerprint in `## 리뷰` (review) with the current one. If they differ, the code changed after the review, so it says so and reviews again first. Then it collects done criteria results, unfixed review findings, skipped reviews, cross-review substitution marks, and changed files and commits, and asks you to choose. When it starts at stage 6 without a run-ticket report, it collects these from the state file, the tickets' completion records, and the git history.
   - **Open a PR**: you settle the commit message and, on the default branch, a new work branch name; then it goes to stage 7. It [closes the protected list](#protected-list) before committing.
   - **Fix**: after the fix, run-ticket redoes only the review step, the new result and code fingerprint are written, and it comes back to stage 6.
   - **Stop**: it reports the current state and the remaining work and ends.
7. **Open the PR**: it creates the work branch and commits as settled in stage 6, then checks that no changes are left. This session writes the PR description itself from the brief, the changed-file list (`git diff --stat`), the completion records, and the review record instead of the full diff. It writes the reason for the change, the change, and how it was verified, in that order, and follows the repo's PR template if there is one. If the cross review was substituted, the mark and the model that ran it go into the verification part. Only after you confirm the description does it push and open the PR with `gh pr create`.

Every confirmation a stage skill asks (where to save the requirements document, confirming the framing record, the brief draft and where to publish it, the ticket split, the parallel run plan) is asked as is, without trimming or answering for you. What run-flow asks itself is the development scope, which decisions to record as ADRs, the work branch name, which files to remove from the protected list, the flow-document commit, the session choice after stage 4, the choice at stage 6, and the PR description confirmation. Push and PR leave remote history and notifications even if reverted, so they happen only after your choice at stage 6.

### Starting stage

`scripts/start_stage.py` looks at the repository's docs documents and decides by the table below. What the script cannot decide, such as a request sentence, a link, a GitHub issue, or the size of a brief without `## 티켓` (tickets), this session decides by the same table.

| Argument | Starting stage |
|---|---|
| `status` | No stage starts. It only lists the unfinished flows and does not change any state file |
| State file | Its `- 현재 단계:` (current stage) |
| Brief without `## 티켓` (tickets) | 4 if the "남은 일" (remaining work) will not fit in one fresh context window, otherwise 5 |
| Brief with unfinished tickets, or one of its tickets | 5 |
| Brief whose tickets are all done | 5 if the integrated review has not run yet (`- 통합 리뷰: 안 함`, integrated review: not run), otherwise 6 |
| A request to bring work done outside a flow into a flow | It judges the current stage of each unfinished brief, creates state files, and asks whether to continue |
| Requirements document (Markdown with `## 개발 범위` and `## 요구사항`, development scope and requirements), request sentence | 2 |
| Planning document: a PDF, PPT, or MD file that fits none of the rows above, a SharePoint or OneDrive link | 1 |
| Folder | Searches inside it as in "None" |
| None | Looks for unfinished state files, then unfinished briefs. If there are several, it lists them for you to choose; if there is none, it asks what to work on |

- A brief is a document with a `- 작성일: YYYY-MM-DD` (date written) line, and a ticket is a document linked from the brief's `## 티켓` (tickets). A docs ticket is done when it says `- 상태: done` (status: done), and a GitHub ticket when it is closed. If the repo rules or the state file's `## 결정` (decisions) define a different completion value, that value also counts as done.
- If an unfinished state file lists the brief or requirements document you passed, it continues that file. It never writes to a finished state file; it creates a new one.
- A flow with a framing record but no brief continues from stage 3 if the record is confirmed, and from stage 2 if it is not.
- State files are found by their `- 현재 단계:` (current stage) line even outside `docs/context/run-flow/` (for example next to the brief), and symlinked folders such as `.scratch` are followed. GitHub briefs are found among open issues labeled `context`.

### State file

Each flow keeps a state file at `docs/context/run-flow/YYYY-MM-DD-<slug>.md`, updated at every stage change. If the conversation breaks or is compacted, open this file or run `/gongbang:run-flow status` to see which stage it is at and what is left. At the top are the current stage and the stop reason (with how to continue); below them are the stage checklist, output locations (requirements document, development scope, brief, brief draft, brief cold-read result, ADRs, branch, starting HEAD, protected list, worker identifier filled only in parallel runs, PR), your decisions, requirements answers, the framing record, decisions during implementation, and the review record. The format is `assets/state-file.md`.

- Answers, decisions, and review results are written as they happen, without waiting for the stage to end. When several reviews run together, each result is written as it arrives.
- If the state file disagrees with the brief and ticket status, it is corrected to match them. Tickets become done before the integrated review, so even when all tickets are done, the flow resumes at the stage 5 review if no integrated review is recorded.
- After stage 7 the current stage becomes `완료` (done), and a finished state file is never written to again. Running another development scope from the same requirements document creates a new state file.

Reviews and reports cover the commits since the starting HEAD, uncommitted changes, and new files. The code fingerprint is the tree hash of the working tree without the flow documents, computed by `scripts/code_fingerprint.sh`. It includes uncommitted changes and new files and stays the same when only flow documents change, so stage 6 uses it to tell whether the reviewed code is the current code.

### Protected list

It keeps the implementing session from passing by editing existing tests. The protected list holds the tests and judge cases (eval cases, grading criteria, expected outputs) at the HEAD where stage 5 started, plus the tests accepted in this flow. This session, subagents, and workers do not edit files on the list, but they can create new test files. The list is on while the state file's `- 현재 단계:` (current stage) is not `완료` (done), and a list whose state file is gone counts as on.

`scripts/protected_paths.py` creates and changes the list.

- **Create (`init`)**: at the start of stage 5 it finds the test files at the starting HEAD and writes them to `docs/context/run-flow/<state file name>.protected`. It takes files under `test`, `tests`, `__tests__`, and `spec` folders, and names such as `test_*.py`, `*_test.go`, `*.test.ts`, `*.spec.js`, `*Test.java`, and `*_spec.rb`. Other tests or judge cases named by the repo rules are added with `--path`. An existing list is left unchanged. A copy of the list is kept in the git common directory (usually `.git/gongbang-protected/`), so a shell edit of the list file itself is caught too.
- **Change (`add`, `remove`)**: when a ticket is accepted, the tests it created are added. If the brief or a ticket asks to change an existing test on the list, it shows that file at the start of stage 5 and removes only the files you choose.
- **Blocking before the write** (optional): with gongbang-mods or the omp extension installed, a write tool that targets a file on the list is refused before it runs and gets the reason back. Writes through shell commands (`sed -i`, redirects) are not blocked.
- **Check before acceptance (`verify`)**: before a ticket is accepted and when stage 6 starts, it compares the working tree, the index, HEAD, and in a parallel run the worker's ticket branch with the starting content. If a file changed, was deleted, or a new file appeared in a folder added with `--path`, or the check itself fails, the ticket is not accepted; the changed files are shown, not reverted, and the flow stops. If a requirements change means an existing test must change, the file is removed after you decide and the flow continues.
- **Close (`close`)**: the list is committed as a flow document, so if it is merged as is, it stays on in the default branch and blocks writes to existing tests there. So when you choose to open a PR in stage 6, it runs `verify` once more and, if it passes, deletes the list and its copy. The deletion goes into the PR commit.
- **Missing copy (`--reseal`)**: when a flow resumes in another clone without the copy, `init` stops, because it cannot tell whether the list was edited through the shell. It shows the list, and if you confirm it, `--reseal` writes the copy again.

### ADRs

At stages 2 and 6, only decisions that are hard to reverse, surprising without context, and chosen among real alternatives are offered as ADR candidates. Only the ones you pick are saved in the repo's ADR folder (or `docs/adr/NNNN-<slug>.md` if there is none) and linked from the state file. set-ticket reads the ADRs saved at stage 2 and reflects them in the tickets.

### When requirements change

If you say the requirements changed mid-flow, it does not start a new flow; it goes back to stage 1 in the same state file. The previous requirements document is moved to `<name>-<previous date>.md`, and only the framing fields that changed are asked. It asks whether to edit the brief or write a new one, keeps finished tickets as they are, and splits only the remaining work again.

## Output

- A state file, a requirements document, a brief, tickets, ADRs
- The implemented code and commits. The protected list is deleted in the PR commit.
- A GitHub PR. You do the merge.
- A final report: each stage's output, the PR URL, and review findings not fixed

## Customize

| What to change | Where to edit |
|---|---|
| Starting stage per argument | SKILL.md "0. 시작 단계 고르기" (0. Pick the starting stage). Decisions settled by docs documents are in `scripts/start_stage.py` |
| When to split into tickets after stage 3 | SKILL.md "3. 작업 지시서" (3. Brief) |
| Ticket completion value (instead of `done`) | Write it in the repo rules or the state file's `## 결정` (decisions). run-flow and run-ticket read and write that value |
| State file location and rules | SKILL.md "상태 파일" (State file) |
| State file format | `assets/state-file.md` |
| ADR criteria and format | `references/adr.md` |
| How stage 3 handles the brief draft and the cold-read result | `references/brief-stage.md` |
| What to collect and offer at stage 6 | `references/merge-stage.md` |
| What to do when the requirements change | `references/requirement-change.md` |
| How tickets run | run-ticket's SKILL.md, or name a ticket execution skill in the repo rules. It is used only if its SKILL.md shows that it does not hand off implementation and does not skip the cross review; otherwise run-ticket is used |
| PR description format, PR creation order | The repo's PR template, or `references/pr-stage.md` |
| How the code fingerprint is computed | `scripts/code_fingerprint.sh` |
| Repo tests and judge cases to add to the protected list | Write their location in the repo rules (CLAUDE.md, AGENTS.md); stage 5 adds them with `--path` |
| Test file rules for the protected list, how the check works | `scripts/protected_paths.py`. If you change it, make `mods/gongbang-mods/hooks/protected_paths.py` identical |

Behavior inside a stage is changed in that stage's skill. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **analyzing-requirements**, **framing-problems**, **set-brief**, **set-ticket**, **run-ticket**: the skills it loads at each stage. set-brief, set-ticket, and run-ticket are Model-invoked so that run-flow can load them, and they run only when you or another skill asks for them.

---

← Previous: [check-guidelines](check-guidelines.md) · [All docs](../README.md) · Next: [set-brief](set-brief.md) →
