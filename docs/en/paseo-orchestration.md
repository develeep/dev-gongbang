<p align="right"><a href="../paseo-orchestration.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › Paseo orchestration setup

# Paseo orchestration setup

This guide sets up Paseo tools, agent profiles, a workspace script, and optional playbooks in [Paseo](https://paseo.sh/docs) so run-ticket can run several tickets in parallel with workers. In the Paseo mode, each ticket gets one worktree workspace branched from the current branch and one agent inside it, and the coordinating session keeps the blocking order and does the merges. After reading it, you can install the files in `extras/paseo/`, register the worker procedure, check that they work, and use them alongside Orca.

The Paseo procedure is optional setup outside the skills. The run-ticket skill does not handle any particular worker tool itself; it runs several tickets in parallel only when you name a worker tool procedure or the repo or agent rules (CLAUDE.md, AGENTS.md) name one, and its usage conditions are met. Without one, it runs them one after another with subagents. So, to avoid naming the procedure every time, after installing Paseo, register the Paseo procedure document [`extras/paseo/worker-procedure.md`](../../extras/paseo/worker-procedure.md) in a rules file.

## Contents

- [Files](#files)
- [Install](#install)
- [Register the procedure](#register-the-procedure)
- [Profiles](#profiles)
- [How Paseo orchestration works](#how-paseo-orchestration-works)
- [Run one ticket with a playbook](#run-one-ticket-with-a-playbook)
- [Using it with Orca](#using-it-with-orca)
- [Check the setup](#check-the-setup)
- [Notes](#notes)

## Files

| File | Install location | Role |
|---|---|---|
| [`extras/paseo/worker-procedure.md`](../../extras/paseo/worker-procedure.md) | Read by the coordinating session. Its path goes in a rules file | How to create, wait for, judge, resume, and clean up workers with Paseo, and how to start a cross-review worker. Its section names match the "워커 도구 절차" (Worker tool procedure) items in run-ticket's `references/multi-ticket.md` |
| [`extras/paseo/register.md`](../../extras/paseo/register.md) | Read and followed by you | The registration text to paste into a rules file, worker model lines with the profile and omp setup values, and the text for naming it together with the Orca procedure |
| [`extras/paseo/config.json`](../../extras/paseo/config.json) | Merge into `~/.paseo/config.json` | The setting that gives Paseo tools to agents (`daemon.mcp.injectIntoAgents`) and 18 agent profiles, one per purpose |
| [`extras/paseo/playbooks/`](../../extras/paseo/playbooks/) | `.paseo/plugins/playbooks/` in the repo where you use it | The `run-ticket` playbook that runs one ticket, and two roles (`ticket-implementer`, `ticket-reviewer`). Optional, and needs the Playbooks plugin |
| [`paseo.json`](../../paseo.json) at the repo root | Already in this repo | This repo's workspace script `check` (`python3 scripts/check.py`). For your own repo, create one in the same format |

## Install

1. **Turn on Paseo tools**: turn on Enable Paseo tools in Settings → host → Agents, or put `daemon.mcp.injectIntoAgents: true` in `~/.paseo/config.json`. After turning it on, start a new agent or reload an existing one so it gets the tools.
2. **Profiles**: merge the `daemon.agentProfiles` entries of `extras/paseo/config.json` into the same key of `~/.paseo/config.json`, then run `paseo reload`. Do not overwrite the existing file. Profiles take effect without restarting the daemon. You can also create them with the same values in Settings → host → Agents → Agent profiles. Every profile except `connector` uses the omp provider, so the omp provider must be enabled. If you use another provider, change `provider`, `model`, `modeId`, and `thinkingOptionId` to that provider's values. List the available providers with `paseo provider ls` and their models with `paseo provider models <provider>`.
3. **Playbooks (optional)**: install the plugin with `paseo plugin add lerenn/playbooks`, then run the command below in the repo where you use it and commit. Starting from the Playbooks panel with "Start in a new workspace" runs it in a worktree branched from the current commit.

   ```bash
   mkdir -p .paseo/plugins/playbooks && cp -R <path to dev-gongbang>/extras/paseo/playbooks/. .paseo/plugins/playbooks/
   ```

4. **Workspace script**: put a `paseo.json` at the repo root. This repo's file is:

   ```json
   {"scripts": {"check": {"command": "python3 scripts/check.py"}}}
   ```

   List scripts with `paseo script ls` and run it with `paseo script start check`.

5. **Register the procedure**: name the Paseo procedure in a rules file as described in [Register the procedure](#register-the-procedure) below.

## Register the procedure

The full steps are in [`extras/paseo/register.md`](../../extras/paseo/register.md).

1. **Decide the path of the procedure document.** If you cloned this repository, use the absolute path of `<path to dev-gongbang>/extras/paseo/worker-procedure.md`. For a repo your team shares, copy `worker-procedure.md` into that repo, commit it, and use the repo-relative path.
2. **Paste the registration text into a rules file.** To use it in every project, put it in your user-level rules file (`~/.claude/CLAUDE.md` for Claude Code, `~/.omp/agent/AGENTS.md` for omp, and so on); to use it in one repo, put it in that repo's `CLAUDE.md` or `AGENTS.md`. Write the path as plain text; do not import it with `@<path>`.

   ```markdown
   ## 워커 도구 절차

   run-ticket의 워커 도구 절차는 Paseo 절차입니다. 여러 티켓을 병렬로 실행하거나 교차 리뷰를 워커에 맡길 때 `<worker-procedure.md 경로>`를 읽고 따릅니다.
   ```

3. **Set the worker models (optional).** To pin the profiles to use, or to set the model for when the pinned profile is missing, add worker model lines below the registration text. The lines and the values for this folder's profiles and the omp setup are in "워커 모델 정하기" (Setting worker models) in register.md.
4. **Check.** In a new session, ask "what is run-ticket's worker tool procedure?" and see that the path from step 1 comes back.

If `~/.omp/agent/AGENTS.md` is a link to this repository's `extras/omp/AGENTS.md`, putting the text in that file edits the file in your clone. Keep a copy instead of the link and edit the copy, or put the text in the repo's `AGENTS.md`.

## Profiles

**One profile has one purpose.** A purpose is defined by the standard used to check its result. One standard means one purpose. When the standards differ, such as an implementation and an independent review, or two review skills, start two agents. When one agent's result mixes work checked against different standards, the main session that receives it has a hard time reviewing it and finding bugs and AI slop.

**Quality of the result comes first, so do not split where context is lost.** The agent that writes or implements something is responsible for verifying its own output and applying the results to finish it. The cold read of a draft, checking the done criteria of an implementation, and working out the cause of a failed ticket are not split off so that another agent finishes the work. Splitting these makes the second agent rebuild the first agent's context. Checks that need a fresh context, such as a cold read or a screen check, are done by a separate agent, but the agent that made the output takes the results and applies them. When you add a profile, check both that it has one purpose and that splitting it off loses no context.

If the worker model lines of the registration text set a profile or model, those come first. Otherwise the session that starts an agent reads each profile's notes and picks the one that fits the purpose of the job. If no profile fits, it looks up the available providers and models, picks one, and tells you what it used.

| Profile | Purpose | Edits files | Model · thinking |
|---|---|---|---|
| `locate` | Find where existing logic lives | No | Haiku 5.5 · medium |
| `behavior-checklist` | Write a checklist of behavior before a change | No | Haiku 5.5 · medium |
| `root-cause` | Report the cause of a bug or failure | No | Opus 5.5 · high |
| `impact` | Assess the impact and risk of one given change | No | Opus 5.5 · high |
| `brief-draft` | Draft a brief and cold-read that draft | Draft only | Opus 5.5 · xhigh |
| `cold-read` | The cold reader that the drafting side starts | No | Opus 5.5 · medium |
| `change-doc` | Write a document that explains a finished change | Document only | Opus 5.5 · xhigh |
| `ticket-worker` | Implement and commit one ticket | Yes | Opus 5.5 · medium |
| `proposal-diff` | Write a proposed diff for one ticket | Diff only | Opus 5.5 · medium |
| `hard-implementer` | Implement one ticket that came up after earlier implementation failed (a subagent failed twice, or an implementation worker failed once), is a large refactor, or fixes a failure with an unknown cause, starting from the cause | Yes | Opus 5.5 · xhigh |
| `cross-review` | Find bugs in a diff implemented by Claude with another company's model. Not used when the implementing model is not Claude | No | GPT-6.2 Sol · high |
| `skill-review` | Run one review skill | No | GPT-6.2 Sol · high |
| `security-review` | Find security defects | No | Opus 5.5 · high |
| `ui-check` | Check done criteria in a browser | No | GPT-6.1 Terra · medium |
| `pr-body` | Write a PR description | No | Haiku 5.5 · medium |
| `advisor` | Assess one plan or design | No | Fable 5.2 · high |
| `env-setup` | Fix one tool or environment setup problem | Settings only | Opus 5.5 · medium |
| `connector` | Read material through Claude Code connectors (SharePoint, Figma, and so on) | No | Opus 5.5 on Claude Code |

The models match the per-role models in the [omp multi-agent setup](omp-orchestration.md). Only `connector` uses the `claude` provider, with the `auto` mode. If you have not connected any connector to Claude Code, delete this profile.

- `locate` and `behavior-checklist` have a 100K context, so give them a narrow scope. If the scope is wide, split it and hand it over in several runs. Use `root-cause` or `impact` only when the purpose is finding a cause or assessing impact.
- With several review skills, start one `skill-review` per skill. If one agent runs two skills, you cannot tell which finding came from which standard.
- `brief-draft` writes the draft, starts `cold-read` agents to verify its own draft, and then returns it. The draft and its check are one job, so they are not split.
- There is no commit message profile. The session that made the change writes the commit message while it still has the context.
- If you only need a cause report, use `root-cause`. If the job is to find the cause and fix it, use `hard-implementer`. Splitting the agent that finds the cause from the agent that fixes it makes the second one find the cause again.

## How Paseo orchestration works

When running several tickets, run-ticket looks at the procedure for the tool named by you or the caller, then the procedures named in the repo or agent rules (in the order listed), and uses the first one whose usage conditions are met. If no procedure can be used, it runs the tickets one after another with subagents. The Paseo procedure's usage condition is that the session has Paseo's workspace and agent management tools, or `paseo ls` succeeds. The comparison of the two modes is in [Orca orchestration setup](orca-orchestration.md#how-the-two-modes-differ).

With the Paseo procedure, it works as follows. Merging, integration checks, completion records, the cross review, and the integration review are the same as with Orca.

- **Unit of execution**: Paseo has nothing like a Run or Task, so the coordinating session keeps the blocking order itself.
- **Worker**: per ticket, one worktree-isolated workspace branched from the current branch (local ref) and one agent inside it.
- **Worker model**: picked in this order: the profile pinned by the worker model lines of the registration text, the model those lines give for when that profile is missing, the descriptions of saved agent profiles, then the same provider and model as the coordinating session.
- **Detecting completion**: waits for the completion notification and does not poll status. A session that Paseo did not start gets no notification, so it waits with `paseo wait` and reads the result with `paseo logs`.
- **Questions, rebase requests**: a follow-up prompt to the same agent.
- **Resuming**: from the recorded workspace ID, agent ID, and branch per ticket. In run-flow they go into `- 워커 식별자:` (worker identifier) in the state file in the format `Paseo 01: 워크스페이스 <ID>, 에이전트 <ID>, 브랜치 <브랜치>; 02: …`.
- **Cleanup**: archive the workspace (Paseo removes the worktree), then delete the branch.

The cross review is done by a model from a different company than the model that implemented the change. It uses the first method that works in this order: the agent set by the agent rules, then the worker tool procedure's "cross-review worker". If none works, it skips the cross review. When starting it with the Paseo procedure, it picks the model in this order: the worker model lines of the registration text (profile, then the model for when the profile is missing), the descriptions of saved profiles, then a lookup of available models. It never uses a model from the same company as the implementing model. With this folder's values, it uses the `cross-review` profile when the implementing model is Claude.

The full commands and judgment rules are in [`extras/paseo/worker-procedure.md`](../../extras/paseo/worker-procedure.md), and the parallel-run flow the coordinator follows is in [run-ticket](skills/run-ticket.md#running-multiple-tickets).

## Run one ticket with a playbook

The `run-ticket` playbook is for a person running one ticket from the Playbooks panel. It takes one input, `ticket` (a ticket path, issue number, or URL).

1. **implement**: `ticket-implementer` performs steps 2, 3, and 4 of the run-ticket skill and commits to the branch.
2. **review**: `ticket-reviewer` reviews read-only on another company's model. If it has findings, the run goes back to implement, up to twice.
3. **approve**: a person approves whether it can be merged.

The playbook does not merge; you do. Running several tickets in parallel is done by the run-ticket skill, not the playbook.

## Using it with Orca

- If you register the Orca and Paseo procedures together, the usage conditions are checked in the order of the registration text and the first procedure that works is used. Put the tool to use first at the top. The text is in "Orca 절차와 함께 지정할 때" (Naming it together with the Orca procedure) in [register.md](../../extras/paseo/register.md).
- If you write "with Paseo" in your request, the Paseo procedure is checked first regardless of the order. If its usage conditions are not met, the next procedure in the rules is checked.
- A resumed run uses the procedure of the tool named in the recorded worker identifier.
- For each tool, the worker model lines of its registration text set the worker models. For Paseo, the order is the pinned profile, then the model set for when it is missing, then the descriptions of saved profiles. Values that match the [omp multi-agent setup](omp-orchestration.md) are in the table of each register.md.

## Check the setup

- In a new session, ask "what is run-ticket's worker tool procedure?" and see that the registered `worker-procedure.md` path comes back
- In a Paseo session, the profile list shows the 18 profiles in the [Profiles](#profiles) table. Ask an agent "show me the Paseo profiles" or check in Settings.
- `paseo script ls` shows `check`.
- The Playbooks panel shows "티켓 실행" (Run ticket) without errors.

## Notes

- **Playbooks are not an official Paseo feature.** They come from a third-party plugin (lerenn/playbooks), and the plugin README warns that the YAML format may break with each minor release before v1.0. That is why the Paseo worker procedure does not use playbooks either.
- **Worktrees branch from a local ref.** Giving a remote ref as the base leaves out commits you have not pushed, so the procedure uses the local ref.
- **The worktree setup command is read from the base branch.** The worktree setup command in `paseo.json` is read from the version committed on the chosen base branch.
- **Editing a profile does not change agents already started.**
- **Injecting Paseo tools is not a security boundary.** An agent that can use a shell can do the same through the CLI.

---

[All docs](README.md) · [README](../../README.en.md)
