<p align="right"><a href="../orca-orchestration.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › Orca orchestration setup

# Orca orchestration setup

This guide sets up [Orca](https://orca.dev/docs/cli/orchestration) so run-ticket can run several tickets in parallel with workers and hand the cross review to a worker on another company's model. In the Orca mode, each brief gets one Orca Run, and each ticket gets a worker in a child worktree branched from the current branch. The coordinating session keeps the blocking order and does the merges, and Orca wakes it when a worker finishes or asks something. run-ticket uses Orca first and falls back to [Paseo](paseo-orchestration.md) when Orca is not available. This guide is based on Orca 1.4.265.

## Contents

- [Install](#install)
- [Tool order](#tool-order)
- [How Orca orchestration works](#how-orca-orchestration-works)
- [How the two modes differ](#how-the-two-modes-differ)
- [Check the setup](#check-the-setup)
- [Notes](#notes)

## Install

1. **Run Orca**: start the Orca app and open the coordinating session (the session that runs run-ticket or run-flow) in an Orca terminal or chat. Opened anywhere else, the session cannot receive worker news from Orca.
2. **Check the CLI**: the skills pick the Orca executable in this order: the value of the `ORCA_CLI_COMMAND` environment variable (Orca sets it in WSL sessions), `orca-ide` on Linux outside an Orca terminal, and `orca` otherwise. On Linux, a bare `orca` may be the GNOME screen reader, so do not run it directly.
3. **Install the skills**: install the `orchestration` and `orca-cli` skills bundled with Orca. They are linked into the skill folders of the agents Orca detects (Claude Code, Codex, omp, and so on). After updating Orca, run `skills update` to match the skills.

   ```bash
   <Orca CLI> skills install
   ```

4. **omp delegation rules**: implementation workers use the omp role `worker` for their model. Install `extras/omp/` as described in [omp multi-agent setup](omp-orchestration.md).
5. **Cross review workers (optional)**: for when the reviewer subagent is not available, install the Codex and Claude Code CLIs on the Orca host. Only agents listed by `<Orca CLI> agent installed` can be started as workers.

## Tool order

When running several tickets, run-ticket picks a worker tool in this order and uses the first one that works. If you name a tool, it uses that one, and a resumed run uses the tool whose identifiers are in the record.

1. Orca: the `orchestration` skill can be loaded, and `status` succeeds with the executable that skill picks
2. Paseo: the session has Paseo's workspace and agent management tools, or `paseo ls` succeeds
3. Neither: run the tickets one after another with subagents

The cross review goes, in order, to the agent set by the agent rules (the reviewer in the omp setup), an Orca worker on another company's model started in this worktree, then an agent started with Paseo. If none works, it is skipped.

## How Orca orchestration works

The coordinating session follows run-ticket's "parallel run" steps and handles workers with Orca commands. Command arguments follow the guide of the running Orca (`<Orca CLI> skills get orchestration`) and `--help`.

1. **Create a Run**: run `orchestration run-create` with the brief title as the objective and record the Run ID. In run-flow it goes into `- Orca Run:` in the state file.
2. **Start workers**: for each ticket whose blocking tickets are all merged, `orchestration worker-start` creates the Task and the worker together. The worker starts in a new worktree under the coordinator's worktree (`--worktree new-child`), based on the current branch's local ref (`--base-branch`). Implementation workers start as the same agent as the coordinator, with `--model @worker`. Workers due at the same time (up to 3 by default) start from one shell command.
3. **Wait**: after starting workers, the coordinator ends its turn and Orca wakes it with a message. It does not poll status.
   - `worker_done`: if the outcome is success and the reported commit is on the ticket branch, it moves on to the merge and integration checks. Anything else counts as a failure.
   - `question`: the worker asked with `ask`. If the brief and ticket answer it, it replies with `reply`; otherwise it asks you and passes your answer on.
   - `escalation`: the worker stopped without a report, disappeared, or asked for permission. It denies out-of-scope permission prompts with `deny` and asks you about in-scope ones.
4. **Rebase requests**: if the merge conflicts, it sends the request to the same worker with `orchestration send --to dispatch:<Dispatch ID>`. A finished worker gets it as a follow-up Task.
5. **Cleanup**: after the merge, it releases the worker with `orchestration worker-release` and removes the worktree and the merged branch with `worktree rm --delete-branch`. Workers and worktrees of failed tickets are kept so you can look at them.
6. **Resume**: if the session broke, it runs `orchestration run-use` with the recorded Run ID, checks each ticket's state and last report with `task-list`, `worker-list`, and `worker-read`, and continues.

When the cross review goes to a worker, it starts Codex if the implementing model is Claude, and Claude Code otherwise, in the coordinator's worktree (`--worktree current`), and tells it to report findings only without editing files. The model and effort come from the "워커" (Workers) section of `extras/omp/AGENTS.md`.

The detailed steps are in [run-ticket](skills/run-ticket.md#running-multiple-tickets).

## How the two modes differ

Merging, integration checks, completion records, the cross review, and the integration review are the same in both.

| Task | Orca | Paseo |
|---|---|---|
| Unit of execution | One Run per brief, one Task per ticket created when its worker starts | No matching concept. The coordinating session keeps the blocking order itself |
| Worker | An Orca worker in a child worktree branched from the current branch (local ref) | One worktree-isolated workspace branched from the current branch (local ref) and one agent inside it |
| Worker model | `--model @worker` from the agent rules | Picked by reading the descriptions of saved agent profiles. Without one, the agent rules; without those, the same provider and model as the coordinating session |
| Detecting completion | The coordinator ends its turn, and Orca wakes it with `worker_done`, `question`, or `escalation` messages | Waits for the completion notification. A session that Paseo did not start waits with `paseo wait` and reads the result with `paseo logs` |
| Questions, rebase requests | Answer with `reply`; `send` to the same Dispatch | A follow-up prompt to the same agent |
| Resuming | `run-use` and `worker-list` with the recorded Run ID | The recorded workspace ID, agent ID, and branch per ticket |
| Cleanup | `worker-release`, then `worktree rm --delete-branch` | Archive the workspace (Paseo removes the worktree), then delete the branch |

## Check the setup

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
- **Commands change with the Orca version.** The skills name only the commands and leave arguments to the running Orca's guide and `--help`.

---

[All docs](README.md) · [README](../../README.en.md)
