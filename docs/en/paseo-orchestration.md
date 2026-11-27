<p align="right"><a href="../paseo-orchestration.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › Paseo orchestration setup

# Paseo orchestration setup

This guide sets up Paseo tools, example agent profiles, and a workspace script in [Paseo](https://paseo.sh/docs) so run-ticket can run several tickets in parallel with workers. In the Paseo mode, each ticket gets one worktree workspace branched from the current branch and one agent inside it, and the coordinating session keeps the blocking order and does the merges. After reading it, you can install the files in `extras/paseo/`, register the worker procedure, check that they work, and use them alongside Orca.

The Paseo procedure is optional setup outside the skills. The run-ticket skill does not handle any particular worker tool itself; it runs several tickets in parallel only when you name a worker tool procedure or the repo or agent rules (CLAUDE.md, AGENTS.md) name one, and its usage conditions are met. Parallel workers are not the default flow but an optional path used only when you name or register a procedure like this; without either, the main session runs the tickets one after another itself. This repository does not set the models of workers or of the cross review; they follow your rules, saved profiles, and environment. To avoid naming the procedure every time, after installing Paseo, register the Paseo procedure document [`extras/paseo/worker-procedure.md`](../../extras/paseo/worker-procedure.md) in a rules file.

## Contents

- [Files](#files)
- [Install](#install)
- [Register the procedure](#register-the-procedure)
- [Profiles](#profiles)
- [How Paseo orchestration works](#how-paseo-orchestration-works)
- [Using it with Orca](#using-it-with-orca)
- [Check the setup](#check-the-setup)
- [Notes](#notes)
- [Removed profiles and playbooks](#removed-profiles-and-playbooks)

## Files

| File | Install location | Role |
|---|---|---|
| [`extras/paseo/worker-procedure.md`](../../extras/paseo/worker-procedure.md) | Read by the coordinating session. Its path goes in a rules file | How to create, wait for, judge, resume, and clean up workers with Paseo, and how to start a cross-review worker. Its section names match the "워커 도구 절차" (Worker tool procedure) items in run-ticket's `references/multi-ticket.md` |
| [`extras/paseo/register.md`](../../extras/paseo/register.md) | Read and followed by you | The registration text to paste into a rules file, worker model lines with placeholder values, and the text for naming it together with the Orca procedure |
| [`extras/paseo/config.json`](../../extras/paseo/config.json) | Merge into `~/.paseo/config.json` | The setting that gives Paseo tools to agents (`daemon.mcp.injectIntoAgents`) and two example profiles (`ticket-worker`, `cross-review`) with the provider and model left empty |
| [`paseo.json`](../../paseo.json) at the repo root | Already in this repo | This repo's workspace script `check` (`python3 scripts/check.py`). For your own repo, create one in the same format |

## Install

1. **Turn on Paseo tools**: turn on Enable Paseo tools in Settings → host → Agents, or put `daemon.mcp.injectIntoAgents: true` in `~/.paseo/config.json`. After turning it on, start a new agent or reload an existing one so it gets the tools.
2. **Profiles (optional)**: merge the `daemon.agentProfiles` entries of `extras/paseo/config.json` into the same key of `~/.paseo/config.json`, fill in each profile's `provider` (required) and `model` (optional) with values from your environment, then run `paseo reload`. Do not overwrite the existing file. Profiles take effect without restarting the daemon. You can also create them in Settings → host → Agents → Agent profiles. List the available providers with `paseo provider ls` and their models with `paseo provider models <provider>`. Give `cross-review` a model from a different company than the one you implement with. The procedure works without merging the profiles (see [Profiles](#profiles) below).
3. **Workspace script**: put a `paseo.json` at the repo root. This repo's file is:

   ```json
   {"scripts": {"check": {"command": "python3 scripts/check.py"}}}
   ```

   List scripts with `paseo script ls` and run it with `paseo script start check`.

4. **Register the procedure**: name the Paseo procedure in a rules file as described in [Register the procedure](#register-the-procedure) below.

## Register the procedure

The full steps are in [`extras/paseo/register.md`](../../extras/paseo/register.md).

1. **Decide the path of the procedure document.** If you cloned this repository, use the absolute path of `<path to dev-gongbang>/extras/paseo/worker-procedure.md`. For a repo your team shares, copy `worker-procedure.md` into that repo, commit it, and use the repo-relative path.
2. **Paste the registration text into a rules file.** To use it in every project, put it in your user-level rules file (`~/.claude/CLAUDE.md` for Claude Code, `~/.omp/agent/AGENTS.md` for omp, and so on); to use it in one repo, put it in that repo's `CLAUDE.md` or `AGENTS.md`. Write the path as plain text; do not import it with `@<path>`.

   ```markdown
   ## 워커 도구 절차

   run-ticket의 워커 도구 절차는 Paseo 절차입니다. 여러 티켓을 병렬로 실행하거나 교차 리뷰를 워커에 맡길 때 `<worker-procedure.md 경로>`를 읽고 따릅니다.
   ```

3. **Set the worker models (optional).** To pin the profiles to use, or to set the model for when the pinned profile is missing, add worker model lines below the registration text. The lines are in "워커 모델 정하기" (Setting worker models) in register.md; their values are placeholders, so fill in your own.
4. **Check.** In a new session, ask "what is run-ticket's worker tool procedure?" and see that the path from step 1 comes back.

If `~/.omp/agent/AGENTS.md` is a link to this repository's `extras/omp/AGENTS.md`, putting the text in that file edits the file in your clone. Keep a copy instead of the link and edit the copy, or put the text in the repo's `AGENTS.md`.

## Profiles

This folder's `config.json` keeps only the two profiles that the parallel path and the cross review use, as examples. Both ship with `provider` set to an empty string and without `model`, `modeId`, or `thinkingOptionId`. In the Paseo profile format, `provider` is a required string while `model`, `modeId`, and `thinkingOptionId` are optional, so the key stays and only its value is empty. Mode and thinking values differ by provider and model, so pick them together.

| Profile | Purpose | Edits files | Values to fill in |
|---|---|---|---|
| `ticket-worker` | Implement and commit one ticket on the parallel path | Yes | A provider and model from your environment |
| `cross-review` | Read-only review of a diff on a model from a different company than the implementing model. Checks bugs, task-scope and repo-rule violations, and security when the change touches authentication, authorization, payments, or personal data | No | A provider and model from a different company than the one you implement with |

If the worker model lines of the registration text set a profile or model, those come first. Otherwise the session that starts an agent reads each profile's notes and picks the one that fits the job. It skips profiles with an empty provider, and for a profile without a model it looks up that provider's models and picks one. If no profile fits, it looks up the available providers and models, picks one, and tells you what it used. The cross review never uses a model from the same company as the implementing model.

## How Paseo orchestration works

When running several tickets, run-ticket looks at the procedure for the tool named by you or the caller, then the procedures named in the repo or agent rules (in the order listed), and uses the first one whose usage conditions are met. If nothing is named or registered, or no procedure can be used, the main session runs the tickets one after another itself (the default flow). The Paseo procedure's usage condition is that the session has Paseo's workspace and agent management tools, or `paseo ls` succeeds. The comparison of the two modes is in [Orca orchestration setup](orca-orchestration.md#how-the-two-modes-differ).

With the Paseo procedure, it works as follows. Merging, integration checks, completion records, the cross review, and the integration review are the same as with Orca.

- **Unit of execution**: Paseo has nothing like a Run or Task, so the coordinating session keeps the blocking order itself.
- **Worker**: per ticket, one worktree-isolated workspace branched from the current branch (local ref) and one agent inside it.
- **Worker model**: picked in this order: the profile pinned by the worker model lines of the registration text, the model those lines give for when that profile is missing, the descriptions of saved agent profiles, then the same provider and model as the coordinating session.
- **Detecting completion**: waits for the completion notification and does not poll status. A session that Paseo did not start gets no notification, so it waits with `paseo wait` and reads the result with `paseo logs`.
- **Questions, rebase requests**: a follow-up prompt to the same agent.
- **Resuming**: from the recorded workspace ID, agent ID, and branch per ticket. In run-flow they go into `- 워커 식별자:` (worker identifier) in the state file in the format `Paseo 01: 워크스페이스 <ID>, 에이전트 <ID>, 브랜치 <브랜치>; 02: …`.
- **Cleanup**: archive the workspace (Paseo removes the worktree), then delete the branch.

The cross review always happens, whether or not tickets run in parallel, and is done by a model from a different company than the model that implemented the change. Its model is not fixed; each time, it is picked in this order: the means you named for this run, the means written in your settings (agent rules, harness settings, saved profiles), then a model from a different company found by looking up the environment. The worker tool procedure's "cross-review worker" is one of these means. When starting it with the Paseo procedure, it picks the model in this order: the worker model lines of the registration text (profile, then the model for when the profile is missing), the descriptions of saved profiles (such as a filled-in `cross-review`), then a lookup of available models. It never uses a model from the same company as the implementing model. If no model from a different company is available, the review is not dropped: it falls back to a fresh-context review on a model from the same company, records the fallback and the model that ran it in the completion record, and continues.

The full commands and judgment rules are in [`extras/paseo/worker-procedure.md`](../../extras/paseo/worker-procedure.md), and the parallel-run flow the coordinator follows is in [run-ticket](skills/run-ticket.md#running-multiple-tickets).

## Using it with Orca

- If you register the Orca and Paseo procedures together, the usage conditions are checked in the order of the registration text and the first procedure that works is used. Put the tool to use first at the top. The text is in "Orca 절차와 함께 지정할 때" (Naming it together with the Orca procedure) in [register.md](../../extras/paseo/register.md).
- If you write "with Paseo" in your request, the Paseo procedure is checked first regardless of the order. If its usage conditions are not met, the next procedure in the rules is checked.
- A resumed run uses the procedure of the tool named in the recorded worker identifier.
- For each tool, the worker model lines of its registration text set the worker models. For Paseo, the order is the pinned profile, then the model set for when it is missing, then the descriptions of saved profiles. This repository gives no recommended model values.

## Check the setup

- In a new session, ask "what is run-ticket's worker tool procedure?" and see that the registered `worker-procedure.md` path comes back
- If you merged the example profiles, the profile list in a Paseo session shows `ticket-worker` and `cross-review` with their provider filled in. Ask an agent "show me the Paseo profiles" or check in Settings.
- `paseo script ls` shows `check`.

## Notes

- **Worktrees branch from a local ref.** Giving a remote ref as the base leaves out commits you have not pushed, so the procedure uses the local ref.
- **The worktree setup command is read from the base branch.** The worktree setup command in `paseo.json` is read from the version committed on the chosen base branch.
- **Editing a profile does not change agents already started.**
- **Injecting Paseo tools is not a security boundary.** An agent that can use a shell can do the same through the CLI.

## Removed profiles and playbooks

With the development flow folded into one loop in the main session, the profiles and playbooks that nothing calls anymore were removed, and the model values of the two remaining profiles were emptied.

| Removed | What it did | Now |
|---|---|---|
| Profiles `locate`, `behavior-checklist`, `impact` | Finding logic, pre-change behavior, change impact | The main session investigates itself |
| Profile `root-cause` | Cause reports | The main session finds the cause itself, including integration-check failures on the parallel path |
| Profiles `brief-draft`, `cold-read` | Brief draft and cold read | The main session writes the draft; cold readers start as the session's subagents and follow the session model |
| Profiles `proposal-diff`, `hard-implementer` | Proposed diffs, escalated implementation of failed tickets | The main session implements itself and asks directly when approval is needed |
| Profiles `skill-review`, `security-review` | Running review skills, security review | The main session runs review skills; security is now a conditional criterion of the cross review |
| Profile `ui-check` | Screen checks | The main session checks itself |
| Profiles `pr-body`, `change-doc` | PR descriptions, change documents | The main session writes them |
| Profiles `advisor`, `env-setup` | Plan advice, environment setup | Nothing replaces them |
| Profile `connector` | Reading material through Claude Code-only connectors | Hand the material over as files, or run stage 1 in Claude Code |
| `playbooks/` (the `run-ticket` playbook and the `ticket-implementer` and `ticket-reviewer` roles) | Implementing, reviewing, and approving one ticket from the Playbooks panel | Run the run-ticket skill directly |

To move over:

- **Profiles**: if you merged the old profiles into `~/.paseo/config.json`, delete the profiles in the table above, since the flow no longer calls them, and run `paseo reload`. They still work if kept, but a session on the parallel path may read their notes and pick one, so deleting them is safer. You can keep your old values for `ticket-worker` and `cross-review`; they count as your own settings. If the `cross-review` notes assume an implementing model, as in "a diff implemented by Claude", replace them with the new example's notes.
- **Playbooks**: in each repo where you copied them, delete `.paseo/plugins/playbooks/run-ticket.yaml`, `.paseo/plugins/playbooks/roles/ticket-implementer/`, and `.paseo/plugins/playbooks/roles/ticket-reviewer/`, and commit. If you use no other playbooks, you can remove the Playbooks plugin too. Run single tickets with the run-ticket skill.
- **Registration text**: unchanged. If the worker model lines in register.md hold values from the old table, you can keep them; without them, the procedure picks from your profiles and environment.

---

[All docs](README.md) · [README](../../README.en.md)
