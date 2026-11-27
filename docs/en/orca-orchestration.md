<p align="right"><a href="../orca-orchestration.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › Orca orchestration setup

# Orca orchestration setup

Once you install [Orca](https://orca.dev/docs/cli/orchestration) and register the Orca worker procedure in a rules file, run-ticket can run several tickets in parallel with Orca workers and hand the cross review to a worker on another company's model. Each brief gets one Orca Run, and each ticket gets a worker in a child worktree branched from the current branch. The coordinating session (the session that runs run-ticket or run-flow) keeps the blocking order and does the merges, and Orca wakes it when a worker finishes or asks something. After reading this guide, you can install, register, and check the Orca procedure, and you know how the Orca mode works. This guide is based on Orca 1.4.265.

Running in parallel is an optional path you choose. run-ticket runs tickets in parallel only when you name a worker tool procedure for this run or one is registered in the repo or agent rules (CLAUDE.md, AGENTS.md), and that procedure's usage conditions are met. Without either, the main session runs the tickets one after another itself. This repository does not set the models of workers or of the cross review; they follow your rules and environment. You can also register the Orca procedure together with the [Paseo procedure](paseo-orchestration.md).

## Contents

- [Files](#files)
- [Install](#install)
- [Register the procedure](#register-the-procedure)
- [Check the setup](#check-the-setup)
- [Tool order](#tool-order)
- [How Orca orchestration works](#how-orca-orchestration-works)
- [How the two modes differ](#how-the-two-modes-differ)
- [Notes](#notes)
- [Moving from the earlier setup](#moving-from-the-earlier-setup)

## Files

| File | Used by | Role |
|---|---|---|
| [`extras/orca/worker-procedure.md`](../../extras/orca/worker-procedure.md) | Read by the coordinating session. Its path goes in a rules file | How to create, wait for, judge, resume, and clean up workers with Orca, and how to start a cross-review worker. Its section names match the "워커 도구 절차" (Worker tool procedure) items in run-ticket's `references/multi-ticket.md` |
| [`extras/orca/register.md`](../../extras/orca/register.md) | Read and followed by you | The registration text to paste into a rules file, worker model lines with placeholder values, and the text for naming it together with the Paseo procedure |

## Install

1. **Run Orca**: start the Orca app and open the coordinating session in an Orca terminal or chat. Opened anywhere else, the session cannot receive worker news from Orca.
2. **Check the CLI**: the `orchestration` skill picks the Orca executable in this order: the value of the `ORCA_CLI_COMMAND` environment variable if set (Orca sets it in WSL sessions), `orca-ide` on Linux outside an Orca terminal, and `orca` otherwise. On Linux, a bare `orca` may be the GNOME screen reader, so do not run it directly. Below, `<Orca CLI>` is the executable picked this way.
3. **Install the skills**: install the `orchestration` and `orca-cli` skills bundled with Orca with the command below. They are linked into the skill folders of the agents Orca detects (Claude Code, Codex, omp, and so on). After updating Orca, run `<Orca CLI> skills update` to match the skills.

   ```bash
   <Orca CLI> skills install
   ```

4. **omp setup (optional)**: to use the omp role `worker` as the implementation workers' model, install `extras/omp/` as described in [omp multi-agent setup](omp-orchestration.md) and put a model from your environment in that role. When you register the procedure, write `--model @worker` in the worker model line.
5. **Cross-review workers (optional)**: to hand the cross review to an Orca worker, install on the Orca host at least one agent CLI that uses a model from a different company than the one you implement with. Only agents listed by `<Orca CLI> agent installed` can be started as workers.
6. **Register the procedure**: name the Orca procedure in a rules file as described in [Register the procedure](#register-the-procedure) below.

## Register the procedure

The full steps are in [`extras/orca/register.md`](../../extras/orca/register.md).

1. **Decide the path of the procedure document.** If you cloned this repository, use the absolute path of `<path to dev-gongbang>/extras/orca/worker-procedure.md`; updating the repository updates the procedure too. For a repo your team shares, copy `worker-procedure.md` into that repo, commit it, and use the repo-relative path.
2. **Paste the registration text into a rules file.** To use it in every project, put it in your user-level rules file (`~/.claude/CLAUDE.md` for Claude Code, `~/.codex/AGENTS.md` for Codex, `~/.omp/agent/AGENTS.md` for omp); to use it in one repo, put it in that repo's `CLAUDE.md` or `AGENTS.md`. Write the path as plain text; do not import it with `@<path>`. An import makes sessions that use no workers read the whole procedure too.

   ```markdown
   ## 워커 도구 절차

   run-ticket의 워커 도구 절차는 Orca 절차입니다. 여러 티켓을 병렬로 실행하거나 교차 리뷰를 워커에 맡길 때 `<worker-procedure.md 경로>`를 읽고 따릅니다.
   ```

3. **Set the worker models (optional).** Write the agent, `--model`, and `--effort` of implementation workers and cross-review workers below the registration text. The lines are in "워커 모델 정하기" (Setting worker models) in register.md; their values are placeholders, so fill in your own. Without them, implementation workers start as the same agent as the coordinating session with no model argument, and cross-review workers start as an installed agent that uses a model from a different company than the implementing model.

If `~/.omp/agent/AGENTS.md` is a link to this repository's `extras/omp/AGENTS.md`, putting the text in that file edits the file in your clone. Keep a copy instead of the link and edit the copy, or put the text in the repo's `AGENTS.md`.

## Check the setup

- In a new session, ask "what is run-ticket's worker tool procedure?" and see that the registered `worker-procedure.md` path comes back
- `<Orca CLI> status` shows `runtimeState: ready`
- `<Orca CLI> skills get orchestration` prints the guide. If it says the command is unknown, update Orca.
- `<Orca CLI> orchestration worker-start --help` lists `--base-branch` and `--model`
- `<Orca CLI> orchestration run-current` finishes without an error in the coordinating session. Without a Run, it prints `runId=none`.

When the parallel-run conditions are met and this procedure is picked, run-ticket shows Orca as the tool for starting workers when it asks you to approve the plan.

## Tool order

When running several tickets, run-ticket looks at worker tool procedures in this order and uses the first one whose usage conditions are met.

1. The procedure for the tool named by you or the caller. If your request names a tool, as in "with Orca", that procedure is checked first regardless of the order in the rules.
2. The procedure named in the repo or agent rules. If there are several, in the order the rules list them.
3. If nothing is named or registered, or no procedure can be used, the main session runs the tickets one after another itself (the default flow).

The Orca procedure's usage condition is that the `orchestration` skill can be loaded and `status` succeeds with the executable that skill picks. A resumed run uses the procedure of the tool named in the recorded worker identifier, because switching tools midway would lose track of whether the earlier tool's workers finished.

When you register it together with the Paseo procedure, usage conditions are checked in the order written in the registration text. Put the tool to try first on top. That text is in "Paseo 절차와 함께 지정할 때" (Naming it together with the Paseo procedure) in register.md.

## How Orca orchestration works

The coordinating session follows run-ticket's "parallel run" steps and handles workers with Orca commands as the registered Orca procedure ([`worker-procedure.md`](../../extras/orca/worker-procedure.md)) describes. Command arguments follow the guide of the running Orca (`<Orca CLI> skills get orchestration`) and `--help`.

1. **Create a Run**: run `orchestration run-create` with the brief title as the objective and record the Run ID right away. In run-flow it goes into `- 워커 식별자:` (worker identifier) in the state file as `Orca Run <Run ID>`. Tasks are not created ahead of time; each is created when its worker starts.
2. **Start workers**: for each ticket whose blocking tickets are all merged, `orchestration worker-start` creates the Task and the worker together. The worker starts in a new worktree under the coordinator's worktree (`--worktree new-child`), based on the current branch's local ref (`--base-branch refs/heads/<current branch>`). The worktree is named after the ticket number, and the worker spec goes in with `--spec-file`. Implementation workers start as the same agent as the coordinator, with the value from the worker model line of the registration text if there is one (`--model @worker` with the omp setup). Workers due at the same time (up to 3 by default) start from one shell command.
3. **Wait**: after starting workers, the coordinator ends its turn and Orca wakes it with a message. It does not poll status.
   - `worker_done`: if the outcome is success, the report has a branch and commit hash, and that commit is on the ticket branch, it moves on to the merge and integration checks. Anything else counts as a failure.
   - `question`: the worker asked with `ask`. If the brief and ticket answer it, it replies with `reply`; otherwise it asks you and passes your answer on.
   - `escalation`: if the worker stopped without a report, it asks for one with `send`, and counts a second stop as a failure. A worker that exited or was lost counts as a failure. A permission request outside the brief and ticket scope is refused with `deny` and a reason; one inside the scope goes to you.
4. **Send to the same worker**: answers to questions and rebase requests go to the same worker with `orchestration send --to dispatch:<Dispatch ID>` instead of a new worker. A finished worker gets them as a follow-up Task.
5. **Cleanup**: after the merge, it releases the worker with `orchestration worker-release` and removes the worktree and the merged branch with `worktree rm --delete-branch`. If the branch remains, it deletes it with `git branch -d <ticket branch>`. Workers and worktrees of failed tickets and of tickets that failed the integration check are kept so you can look at them.
6. **Resume**: if the session broke, it runs `orchestration run-use` with the recorded Run ID, checks each ticket's state and last report with `task-list`, `worker-list`, and `worker-read`, and continues. Missed messages are in `inbox --terminal run:<Run ID>`. If no Run ID was recorded, it finds the Run with the same brief title in `run-list` and uses it after you confirm.

**Cross-review worker**: the cross review always happens, whether or not tickets run in parallel. run-ticket picks the means in this order: the means you named for this run, the means written in your settings (agent rules, harness settings, saved profiles) or the "cross-review worker" of a registered worker tool procedure, then a model from a different company found by looking up the environment. With the Orca procedure, the worker starts in the coordinator's worktree (`--worktree current`). The agent and model are the ones set by the worker model lines of the registration text; without them, an agent listed by `agent installed` that uses a model from a different company than the implementing model starts on its default model. The spec holds the diff range, the full brief, the criteria list, and the verification criteria to run, and tells the worker to edit no files and report only findings, verification verdicts, and the model name through `worker_done`. If no agent with a model from a different company is installed, run-ticket does not drop the review: it falls back to a fresh-context review on a model from the same company, records the fallback and the model that ran it in the completion record, and continues.

The full commands and judgment rules are in [`extras/orca/worker-procedure.md`](../../extras/orca/worker-procedure.md), and the parallel-run flow the coordinator follows is in [run-ticket](skills/run-ticket.md#running-multiple-tickets).

## How the two modes differ

Merging, integration checks, completion records, the cross review criteria, and the integration review are the same in both.

| Task | Orca | Paseo |
|---|---|---|
| Unit of execution | One Run per brief, one Task per ticket created when its worker starts | No matching concept. The coordinating session keeps the blocking order itself |
| Worker | An Orca worker in a child worktree branched from the current branch (local ref) | One worktree-isolated workspace branched from the current branch (local ref) and one agent inside it |
| Worker model | The worker model line of the registration text (`--model @worker` with the omp setup). Without it, the same agent as the coordinator with no model argument | In this order: the profile pinned by the worker model lines of the registration text, the model those lines give for when that profile is missing, the descriptions of saved agent profiles, then the same provider and model as the coordinating session |
| Detecting completion | The coordinator ends its turn, and Orca wakes it with `worker_done`, `question`, or `escalation` messages | Waits for the completion notification. A session that Paseo did not start waits with `paseo wait` and reads the result with `paseo logs` |
| Permission requests | Out-of-scope ones are refused with `deny`; in-scope ones go to you | Only in-scope ones are approved; the rest go to you |
| Questions, rebase requests | Answer with `reply`; `send` to the same Dispatch | A follow-up prompt to the same agent |
| Resuming | `run-use` and `worker-list` with the recorded Run ID | The recorded workspace ID, agent ID, and branch per ticket |
| Cleanup | `worker-release`, then `worktree rm --delete-branch` | Archive the workspace (Paseo removes the worktree), then delete the branch |
| Cross-review worker | An Orca worker in the coordinator's worktree (`--worktree current`) | An agent started in the coordinator's workspace |

## Notes

- **Worker worktrees see only committed content.** If you start without committing the brief and tickets, workers cannot read them, so run-ticket first checks that the working tree is clean.
- **Worktrees are based on the local ref.** Leaving the base out or giving a remote ref drops unpushed commits (flow documents, tickets merged earlier).
- **No response does not mean the worker finished.** A timeout or an unknown liveness state does not get the worker started again. Starting it again would implement the same ticket twice.
- **Start retries are limited.** When `worker-start` fails, it is not rerun as is; the recovery guidance in its result is followed, and the same Task is restarted with `--retry-of` only after the cause changed. After three failed starts of the same Task, Orca blocks that Task, and run-ticket reports the ticket as failed instead of routing around it with a new Run or Task.
- **Workers in new worktrees stay open after they finish.** Release them with `worker-release` after the merge. To keep talking to a worker, start it with `--keep-open`.
- **Commands change with the Orca version.** The Orca procedure names only the commands and leaves arguments to the running Orca's guide and `--help`.
- **Worktrees other than ticket workers get the same value for name and branch.** The `--name` and `--branch` rule for creating such worktrees with Orca, for example for a work branch, is in "worktree와 브랜치 이름" (Worktree and branch names) in the procedure document.

## Moving from the earlier setup

The per-worker recommended model table in `extras/orca/register.md` (`--model` and `--effort` values matching the omp setup) has been removed. The registration text ("붙일 문구") and the entry conditions are unchanged.

- If you copied the old table's values into a rules file, you can keep them. They count as your own settings.
- If your cross-review worker line pins agents by company, as in "Codex if the implementing model is Claude, Claude Code otherwise", replace it with one agent from your environment or delete the line. Without the line, the procedure picks an installed agent that uses a model from a different company.

---

[All docs](README.md) · [README](../../README.en.md)
