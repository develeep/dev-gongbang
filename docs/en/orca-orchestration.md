<p align="right"><a href="../orca-orchestration.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › Orca orchestration setup

# Orca orchestration setup

This guide sets up [Orca](https://orca.dev/docs/cli/orchestration) so run-ticket can run several tickets in parallel with workers and hand the cross review to a worker on another company's model. In the Orca mode, each brief gets one Orca Run, and each ticket gets a worker in a child worktree branched from the current branch. The coordinating session keeps the blocking order and does the merges, and Orca wakes it when a worker finishes or asks something. This guide is based on Orca 1.4.265.

The Orca procedure is optional setup outside the skills. The run-ticket skill does not handle any particular worker tool itself; it runs several tickets in parallel only when the repo or agent rules (CLAUDE.md, AGENTS.md) name a worker tool procedure. Without one, it runs them one after another with subagents. So after installing Orca, register the Orca procedure document [`extras/orca/worker-procedure.md`](../../extras/orca/worker-procedure.md) in a rules file. You can register it together with the [Paseo](paseo-orchestration.md) procedure.

## Contents

- [Files](#files)
- [Install](#install)
- [Register the procedure](#register-the-procedure)
- [Tool order](#tool-order)
- [How Orca orchestration works](#how-orca-orchestration-works)
- [How the two modes differ](#how-the-two-modes-differ)
- [Check the setup](#check-the-setup)
- [Notes](#notes)

## Files

| File | Used by | Role |
|---|---|---|
| [`extras/orca/worker-procedure.md`](../../extras/orca/worker-procedure.md) | Read by the coordinating session. Its path goes in a rules file | How to create, wait for, judge, resume, and clean up workers with Orca, and how to start a cross-review worker. Its section names match the "워커 도구 절차" (Worker tool procedure) items in run-ticket's `references/multi-ticket.md` |
| [`extras/orca/register.md`](../../extras/orca/register.md) | Read and followed by you | The registration text to paste into a rules file, worker model lines with the omp setup values, and the text for naming it together with the Paseo procedure |

## Install

1. **Run Orca**: start the Orca app and open the coordinating session (the session that runs run-ticket or run-flow) in an Orca terminal or chat. Opened anywhere else, the session cannot receive worker news from Orca.
2. **Check the CLI**: the `orchestration` skill picks the Orca executable in this order: the value of the `ORCA_CLI_COMMAND` environment variable (Orca sets it in WSL sessions), `orca-ide` on Linux outside an Orca terminal, and `orca` otherwise. On Linux, a bare `orca` may be the GNOME screen reader, so do not run it directly.
3. **Install the skills**: install the `orchestration` and `orca-cli` skills bundled with Orca. They are linked into the skill folders of the agents Orca detects (Claude Code, Codex, omp, and so on). After updating Orca, run `skills update` to match the skills.

   ```bash
   <Orca CLI> skills install
   ```

4. **omp setup (optional)**: to use the omp role `worker` as the implementation workers' model, install `extras/omp/` as described in [omp multi-agent setup](omp-orchestration.md), and write `--model @worker` in the worker model line when you register the procedure.
5. **Cross review workers (optional)**: for when the reviewer subagent is not available, install the Codex and Claude Code CLIs on the Orca host. Only agents listed by `<Orca CLI> agent installed` can be started as workers.
6. **Register the procedure**: name the Orca procedure in a rules file as described in [Register the procedure](#register-the-procedure) below.

## Register the procedure

The full steps are in [`extras/orca/register.md`](../../extras/orca/register.md).

1. **Decide the path of the procedure document.** If you cloned this repository, use the absolute path of `<path to dev-gongbang>/extras/orca/worker-procedure.md`. For a repo your team shares, copy `worker-procedure.md` into that repo, commit it, and use the repo-relative path.
2. **Paste the registration text into a rules file.** To use it in every project, put it in your user-level rules file (`~/.claude/CLAUDE.md` for Claude Code, `~/.omp/agent/AGENTS.md` for omp, and so on); to use it in one repo, put it in that repo's `CLAUDE.md` or `AGENTS.md`. Write the path as plain text; do not import it with `@<path>`.

   ```markdown
   ## 워커 도구 절차

   run-ticket의 워커 도구 절차는 Orca 절차입니다. 여러 티켓을 병렬로 실행하거나 교차 리뷰를 워커에 맡길 때 `<worker-procedure.md 경로>`를 읽고 따릅니다.
   ```

3. **Set the worker models (optional).** Write the `--model` and `--effort` of implementation workers and cross-review workers below the registration text. The lines and the omp setup values are in "워커 모델 정하기" (Setting worker models) in register.md. Without them, implementation workers start as the same agent as the coordinating session with no model argument.
4. **Check.** In a new session, ask "what is run-ticket's worker tool procedure?" and see that the path from step 1 comes back.

If `~/.omp/agent/AGENTS.md` is a link to this repository's `extras/omp/AGENTS.md`, putting the text in that file edits the file in your clone. Keep a copy instead of the link and edit the copy, or put the text in the repo's `AGENTS.md`.

## Tool order

When running several tickets, run-ticket looks at worker tool procedures in this order and uses the first one whose usage conditions are met. A resumed run uses the procedure of the tool named in the recorded worker identifier.

1. The procedure for the tool named by you or the caller. If your request names a tool, as in "with Orca", that procedure is used.
2. The procedure named in the repo or agent rules. If there are several, in the order the rules list them.
3. If no procedure can be used, run the tickets one after another with subagents

The Orca procedure's usage condition is that the `orchestration` skill can be loaded and `status` succeeds with the executable that skill picks. When you register it together with the Paseo procedure, the order in the registration text decides which is used first. That text is in "Paseo 절차와 함께 지정할 때" (Naming it together with the Paseo procedure) in register.md.

The cross review goes, in order, to the agent set by the agent rules (the reviewer in the omp setup), then a worker on another company's model started in this worktree as the worker tool procedure's "cross-review worker" describes. With several procedures, they are tried in the order above. If none works, it is skipped.

## How Orca orchestration works

The coordinating session follows run-ticket's "parallel run" steps and handles workers with Orca commands as the registered Orca procedure ([`worker-procedure.md`](../../extras/orca/worker-procedure.md)) describes. Command arguments follow the guide of the running Orca (`<Orca CLI> skills get orchestration`) and `--help`.

1. **Create a Run**: run `orchestration run-create` with the brief title as the objective and record the Run ID. In run-flow it goes into `- 워커 식별자:` (worker identifier) in the state file as `Orca Run <Run ID>`.
2. **Start workers**: for each ticket whose blocking tickets are all merged, `orchestration worker-start` creates the Task and the worker together. The worker starts in a new worktree under the coordinator's worktree (`--worktree new-child`), based on the current branch's local ref (`--base-branch`). Implementation workers start as the same agent as the coordinator, with the value from the worker model line of the registration text if there is one (`--model @worker` with the omp setup). Workers due at the same time (up to 3 by default) start from one shell command.
3. **Wait**: after starting workers, the coordinator ends its turn and Orca wakes it with a message. It does not poll status.
   - `worker_done`: if the outcome is success and the reported commit is on the ticket branch, it moves on to the merge and integration checks. Anything else counts as a failure.
   - `question`: the worker asked with `ask`. If the brief and ticket answer it, it replies with `reply`; otherwise it asks you and passes your answer on.
   - `escalation`: the worker stopped without a report, disappeared, or asked for permission. It denies out-of-scope permission prompts with `deny` and asks you about in-scope ones.
4. **Rebase requests**: if the merge conflicts, it sends the request to the same worker with `orchestration send --to dispatch:<Dispatch ID>`. A finished worker gets it as a follow-up Task.
5. **Cleanup**: after the merge, it releases the worker with `orchestration worker-release` and removes the worktree and the merged branch with `worktree rm --delete-branch`. Workers and worktrees of failed tickets are kept so you can look at them.
6. **Resume**: if the session broke, it runs `orchestration run-use` with the recorded Run ID, checks each ticket's state and last report with `task-list`, `worker-list`, and `worker-read`, and continues.

When the cross review goes to a worker, it starts Codex if the implementing model is Claude, and Claude Code otherwise, in the coordinator's worktree (`--worktree current`), and tells it to report findings only without editing files. The model and effort come from the worker model lines of the registration text.

The full commands and judgment rules are in [`extras/orca/worker-procedure.md`](../../extras/orca/worker-procedure.md), and the parallel-run flow the coordinator follows is in [run-ticket](skills/run-ticket.md#running-multiple-tickets).

## How the two modes differ

Merging, integration checks, completion records, the cross review, and the integration review are the same in both.

| Task | Orca | Paseo |
|---|---|---|
| Unit of execution | One Run per brief, one Task per ticket created when its worker starts | No matching concept. The coordinating session keeps the blocking order itself |
| Worker | An Orca worker in a child worktree branched from the current branch (local ref) | One worktree-isolated workspace branched from the current branch (local ref) and one agent inside it |
| Worker model | The worker model line of the registration text (`--model @worker` with the omp setup) | Picked by reading the descriptions of saved agent profiles. Without one, the agent rules; without those, the same provider and model as the coordinating session |
| Detecting completion | The coordinator ends its turn, and Orca wakes it with `worker_done`, `question`, or `escalation` messages | Waits for the completion notification. A session that Paseo did not start waits with `paseo wait` and reads the result with `paseo logs` |
| Questions, rebase requests | Answer with `reply`; `send` to the same Dispatch | A follow-up prompt to the same agent |
| Resuming | `run-use` and `worker-list` with the recorded Run ID | The recorded workspace ID, agent ID, and branch per ticket |
| Cleanup | `worker-release`, then `worktree rm --delete-branch` | Archive the workspace (Paseo removes the worktree), then delete the branch |

## Check the setup

- In a new session, ask "what is run-ticket's worker tool procedure?" and see that the registered `worker-procedure.md` path comes back
- `<Orca CLI> status` shows `runtimeState: ready`
- `<Orca CLI> skills get orchestration` prints the guide. If it says the command is unknown, update Orca.
- `<Orca CLI> orchestration worker-start --help` lists `--base-branch` and `--model`
- `<Orca CLI> orchestration run-current` finishes without an error in the coordinating session. Without a Run, it prints `runId=none`.

## Notes

- **Worker worktrees see only committed content.** If you start without committing the brief and tickets, workers cannot read them, so run-ticket first checks that the working tree is clean.
- **Worktrees are based on the local ref.** Leaving the base out or giving a remote ref drops unpushed commits (flow documents, tickets merged earlier).
- **Silence is not completion.** No response or a timeout does not mean the worker finished, and the worker is not started again. That would implement the same ticket twice.
- **Start retries are limited.** After three failed starts of the same Task, Orca blocks that Task. run-ticket does not route around it with a new Run or Task; it reports the ticket as failed.
- **Workers in new worktrees stay open after they finish.** Release them with `worker-release` after the merge. To keep talking to a worker, start it with `--keep-open`.
- **Commands change with the Orca version.** The Orca procedure names only the commands and leaves arguments to the running Orca's guide and `--help`.
- **Worktrees other than ticket workers get the same value for name and branch.** The `--name` and `--branch` rule for creating such worktrees with Orca, for example for a work branch, is in "worktree와 브랜치 이름" (Worktree and branch names) in the procedure document.

---

[All docs](README.md) · [README](../../README.en.md)
