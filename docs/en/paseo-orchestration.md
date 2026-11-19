<p align="right"><a href="../paseo-orchestration.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › Paseo orchestration setup

# Paseo orchestration setup

This guide sets up Paseo tools, agent profiles, a workspace script, and optional playbooks in [Paseo](https://paseo.sh/docs) so run-ticket can run several tickets in parallel with workers. In the Paseo mode, each ticket gets one worktree workspace branched from the current branch and one agent inside it, and the coordinating session keeps the blocking order and does the merges. After reading it, you can install the files in `extras/paseo/`, check that they work, and use them alongside Orca.

## Contents

- [Files](#files)
- [Install](#install)
- [Profiles](#profiles)
- [How Paseo orchestration works](#how-paseo-orchestration-works)
- [Run one ticket with a playbook](#run-one-ticket-with-a-playbook)
- [Using it with Orca](#using-it-with-orca)
- [Check the setup](#check-the-setup)
- [Notes](#notes)

## Files

| File | Install location | Role |
|---|---|---|
| [`extras/paseo/config.json`](../../extras/paseo/config.json) | Merge into `~/.paseo/config.json` | The setting that gives Paseo tools to agents (`daemon.mcp.injectIntoAgents`) and 12 agent profiles, one per situation |
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

## Profiles

The session that starts an agent reads each profile's notes and picks the one that fits the situation. If no profile fits, it looks up the available providers and models, picks one, and tells you what it used.

| Profile | Situation | Model · thinking |
|---|---|---|
| `locate` | Read-only search in a known scope, checklist of behavior before a change | Haiku 5.5 · medium |
| `root-cause` | Tracing the cause of a bug, searching the whole repo, assessing the impact of an API change | Opus 5.5 · high |
| `draft` | Brief drafts, documents that explain a change | Opus 5.5 · xhigh |
| `ticket-worker` | Implementing a ticket, writing a proposed diff, cold-reading a brief | Opus 5.5 · medium |
| `hard-implementer` | A ticket that failed twice, a large refactor, a failure with an unknown cause | Opus 5.5 · xhigh |
| `cross-review` | Cross review by another company's model, running review skills | GPT-6.1 Sol · high |
| `security-review` | Security review of changes to authentication, permissions, payments, or personal data | Opus 5.5 · high |
| `ui-check` | Checking done criteria in a browser | GPT-6.1 Terra · medium |
| `commit-pr` | Commit messages, PR descriptions | Haiku 5.5 · medium |
| `advisor` | Assessing a plan or design, a second opinion when stuck | Fable 5.2 · high |
| `env-setup` | Setting up agent tools and the dev environment, workspace operations | Opus 5.5 · medium |
| `connector` | Reading material through connectors that only Claude Code has (SharePoint, Figma, and so on) | Opus 5.5 on Claude Code |

The models match the per-role models in the [omp multi-agent setup](omp-orchestration.md). Only `connector` uses the `claude` provider, with the `auto` mode. If you have not connected any connector to Claude Code, delete this profile.

- `locate` has a 100K context, so give it a narrow scope. Hand a search across the whole repo to `root-cause`.
- Starting several `cross-review` agents on the same diff repeats the same findings. Give each review a different angle.
- `draft` only writes the draft and returns it. The session that receives the draft starts the cold reads itself with `ticket-worker`. When an agent starts agents inside itself, a stall is hard to notice.

## How Paseo orchestration works

When running several tickets, run-ticket picks a worker tool in this order and uses the first one that works. If you name a tool, it uses that one.

1. Paseo: the session has Paseo's workspace and agent management tools, or `paseo ls` succeeds
2. Orca: the `orchestration` skill is available
3. Neither: run the tickets one after another with subagents

The two modes differ as follows. Merging, integration checks, completion records, the cross review, and the integration review are the same in both.

| Task | Orca | Paseo |
|---|---|---|
| Unit of execution | One Run, a Task per ticket, blocking relations as Task deps | No matching concept. The coordinating session keeps the blocking order itself |
| Worker | An Orca worker in a child worktree | Per ticket, one worktree-isolated workspace branched from the current branch (local ref) and one agent inside it |
| Worker model | `--model @worker` from the agent rules | Picked by reading the descriptions of saved agent profiles. Without one, the agent rules; without those, the same provider and model as the coordinating session |
| Detecting completion | Status checks from the orchestration skill | Waits for the completion notification. Does not poll status. A session that Paseo did not start gets no notification, so it waits with `paseo wait` and reads the result with `paseo logs` |
| Questions, rebase requests | Pass the answer to the worker | A follow-up prompt to the same agent |
| Resuming | The recorded Run ID | The recorded workspace ID, agent ID, and branch per ticket |
| Cleanup | Release the worker, delete the worktree and branch | Archive the workspace (Paseo removes the worktree), then delete the branch |

For the cross review, it uses the first method that works in this order: the agent set by the agent rules, an agent on another company's model started with Paseo, then an Orca worker. If none works, it skips the cross review. When starting it with Paseo, it uses the `cross-review` profile.

The detailed steps are in [run-ticket](skills/run-ticket.md#running-multiple-tickets).

## Run one ticket with a playbook

The `run-ticket` playbook is for a person running one ticket from the Playbooks panel. It takes one input, `ticket` (a ticket path, issue number, or URL).

1. **implement**: `ticket-implementer` performs steps 2, 3, and 4 of the run-ticket skill and commits to the branch.
2. **review**: `ticket-reviewer` reviews read-only on another company's model. If it has findings, the run goes back to implement, up to twice.
3. **approve**: a person approves whether it can be merged.

The playbook does not merge; you do. Running several tickets in parallel is done by the run-ticket skill, not the playbook.

## Using it with Orca

- If both tools are available, Paseo is used. To use Orca, write "with Orca" in your request or put it in the agent rules.
- A resumed run uses the tool whose identifiers are in the record.
- The "워커" (Workers) section of the omp delegation rules ([omp multi-agent setup](omp-orchestration.md)) sets the worker models for both tools.

## Check the setup

- In a Paseo session, the profile list shows the 12 profiles in the [Profiles](#profiles) table. Ask an agent "show me the Paseo profiles" or check in Settings.
- `paseo script ls` shows `check`.
- The Playbooks panel shows "티켓 실행" (Run ticket) without errors.

## Notes

- **Playbooks are not an official Paseo feature.** They come from a third-party plugin (lerenn/playbooks), and the plugin README warns that the YAML format may break with each minor release before v1.0. That is why the run-ticket skill does not rely on playbooks.
- **Worktrees branch from a local ref.** Giving a remote ref as the base leaves out commits you have not pushed, so the skill uses the local ref.
- **The worktree setup command is read from the base branch.** The worktree setup command in `paseo.json` is read from the version committed on the chosen base branch.
- **Editing a profile does not change agents already started.**
- **Injecting Paseo tools is not a security boundary.** An agent that can use a shell can do the same through the CLI.

---

[All docs](README.md) · [README](../../README.en.md)
