<p align="right"><a href="../paseo-orchestration.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › Paseo orchestration setup

# Paseo orchestration setup

Once you install the [Paseo](https://paseo.sh/docs) tools and the example agent profiles and register the Paseo worker procedure in a rules file, run-ticket can run several tickets in parallel with Paseo workers and hand the cross review to an agent on another company's model. Each ticket gets one worktree workspace branched from the current branch and one agent inside it, and the coordinating session (the session that runs run-ticket or run-flow) keeps the blocking order and does the merges. After reading this guide, you can install the files in `extras/paseo/`, register the worker procedure, and check the setup, and you know how the Paseo mode works.

Running in parallel is an optional path you choose. run-ticket runs tickets in parallel only when you name a worker tool procedure for this run or one is registered in the repo or agent rules (CLAUDE.md, AGENTS.md), and that procedure's usage conditions are met. Without either, the main session runs the tickets one after another itself. This repository does not set the models of workers or of the cross review; they follow your rules, saved profiles, and environment. You can also register the Paseo procedure together with the [Orca procedure](orca-orchestration.md).

## Contents

- [Files](#files)
- [Install](#install)
- [Register the procedure](#register-the-procedure)
- [Check the setup](#check-the-setup)
- [Profiles](#profiles)
- [Tool order](#tool-order)
- [How Paseo orchestration works](#how-paseo-orchestration-works)
- [Notes](#notes)
- [Moving from the earlier setup](#moving-from-the-earlier-setup)

## Files

| File | Install location | Role |
|---|---|---|
| [`extras/paseo/worker-procedure.md`](../../extras/paseo/worker-procedure.md) | Read by the coordinating session. Its path goes in a rules file | How to create, wait for, judge, resume, and clean up workers with Paseo, and how to start a cross-review worker. Its section names match the "워커 도구 절차" (Worker tool procedure) items in run-ticket's `references/multi-ticket.md` |
| [`extras/paseo/register.md`](../../extras/paseo/register.md) | Read and followed by you | The registration text to paste into a rules file, worker model lines with placeholder values, and the text for naming it together with the Orca procedure |
| [`extras/paseo/config.json`](../../extras/paseo/config.json) | Merge into `~/.paseo/config.json` | The setting that gives agents the Paseo tools (`daemon.mcp.injectIntoAgents`) and two example profiles with empty provider and model (`ticket-worker`, `cross-review`) |
| [`paseo.json`](../../paseo.json) at the repo root | Already in this repo | This repo's workspace script `check` (`python3 scripts/check.py`). Create your own in the same format for your repo |

## Install

1. **Turn on the Paseo tools**: turn on Enable Paseo tools in Settings → host → Agents, or put `daemon.mcp.injectIntoAgents: true` in `~/.paseo/config.json`. After turning it on, start a new agent or reload existing ones so they get the tools.
2. **Profiles (optional)**: merge the `daemon.agentProfiles` entries of `extras/paseo/config.json` into the same key of `~/.paseo/config.json`. Do not overwrite the whole file. Fill in each profile's `provider` (required) and `model` (optional) with values from your environment, then run `paseo reload`. Profiles take effect without restarting the daemon. You can also create them in Settings → host → Agents → Agent profiles.
   - List the available providers with `paseo provider ls` and their models with `paseo provider models <provider>`.
   - Give `cross-review` a model from a different company than the one you implement with.
   - The procedure works without merging the profiles. The order it picks models in is under [Profiles](#profiles) below.
3. **Workspace script (optional)**: put a `paseo.json` at the repo root. This repo's is below. List scripts with `paseo script ls` and run it with `paseo script start check`.

   ```json
   {"scripts": {"check": {"command": "python3 scripts/check.py"}}}
   ```

4. **Register the procedure**: name the Paseo procedure in a rules file as described in [Register the procedure](#register-the-procedure) below.

## Register the procedure

The full steps are in [`extras/paseo/register.md`](../../extras/paseo/register.md).

1. **Decide the path of the procedure document.** If you cloned this repository, use the absolute path of `<path to dev-gongbang>/extras/paseo/worker-procedure.md`; updating the repository updates the procedure too. For a repo your team shares, copy `worker-procedure.md` into that repo, commit it, and use the repo-relative path.
2. **Paste the registration text into a rules file.** To use it in every project, put it in your user-level rules file (`~/.claude/CLAUDE.md` for Claude Code, `~/.codex/AGENTS.md` for Codex, `~/.omp/agent/AGENTS.md` for omp); to use it in one repo, put it in that repo's `CLAUDE.md` or `AGENTS.md`. Write the path as plain text; do not import it with `@<path>`. An import makes sessions that use no workers read the whole procedure too.

   ```markdown
   ## 워커 도구 절차

   run-ticket의 워커 도구 절차는 Paseo 절차입니다. 여러 티켓을 병렬로 실행하거나 교차 리뷰를 워커에 맡길 때 `<worker-procedure.md 경로>`를 읽고 따릅니다.
   ```

3. **Set the worker models (optional).** To pin the profile to use, or the provider, model, and thinking to use when that profile is missing, add worker model lines below the registration text. The lines are in "워커 모델 정하기" (Setting worker models) in register.md; their values are placeholders, so fill in your own.

If `~/.omp/agent/AGENTS.md` is a link to this repository's `extras/omp/AGENTS.md`, putting the text in that file edits the file in your clone. Keep a copy instead of the link and edit the copy, or put the text in the repo's `AGENTS.md`.

## Check the setup

- In a new session, ask "what is run-ticket's worker tool procedure?" and see that the registered `worker-procedure.md` path comes back
- `paseo ls` succeeds
- If you merged the example profiles, `ticket-worker` and `cross-review` show with their provider filled in. Ask an agent "show me the Paseo profiles" or check in Settings.
- If you added `paseo.json`, `paseo script ls` lists `check`

When the parallel-run conditions are met and this procedure is picked, run-ticket shows Paseo as the tool for starting workers when it asks you to approve the plan.

## Profiles

`extras/paseo/config.json` holds two example profiles, used by the parallel path and the cross review. Both ship with `provider` as an empty string and without `model`, `modeId`, or `thinkingOptionId`, because in the Paseo profile format `provider` is a required string and the rest are optional. Mode and thinking values differ by provider and model, so choose them together.

| Profile | Job | Edits files | Values to fill |
|---|---|---|---|
| `ticket-worker` | In the parallel path, implements one ticket in its own worktree, checks the completion criteria, and commits | Yes | A provider and model from your environment |
| `cross-review` | Reads the diff on a model from a different company than the implementing model and reports findings only. The criteria are bugs and violations of the task boundary and the repo rules, plus security when the change touches authentication, authorization, payments, or personal data | No | A provider and model from a different company than the one you implement with |

The session starting a worker picks the model in this order:

1. The profile pinned by the worker model lines of the registration text. If that profile is missing, the provider, model, and thinking those lines give
2. Without worker model lines, the saved profile whose description fits the job. Profiles with an empty provider are skipped, and for a profile without a model, it looks up the models available for that provider.
3. With no fitting profile, implementation workers use the same provider and model as the coordinating session, and cross-review workers use a model from a different company picked by looking up the available providers and models

Either way it says what it started the worker with, and the cross review never uses a model from the same company as the implementing model.

## Tool order

When running several tickets, run-ticket looks at worker tool procedures in this order and uses the first one whose usage conditions are met.

1. The procedure for the tool named by you or the caller. If your request names a tool, as in "with Paseo", that procedure is checked first regardless of the order in the rules.
2. The procedure named in the repo or agent rules. If there are several, in the order the rules list them.
3. If nothing is named or registered, or no procedure can be used, the main session runs the tickets one after another itself (the default flow).

The Paseo procedure's usage condition is that the session has Paseo's workspace and agent management tools or `paseo ls` succeeds. Starting only a cross-review worker needs the agent management tools or a successful `paseo ls`. A resumed run uses the procedure of the tool named in the recorded worker identifier.

When you register it together with the Orca procedure, usage conditions are checked in the order written in the registration text. Put the tool to try first on top. That text is in "Orca 절차와 함께 지정할 때" (Naming it together with the Orca procedure) in [register.md](../../extras/paseo/register.md). Each tool's worker model lines set its worker models, and this repository gives no recommended model values. The two modes are compared in [Orca orchestration setup](orca-orchestration.md#how-the-two-modes-differ).

## How Paseo orchestration works

The coordinating session follows run-ticket's "parallel run" steps and handles workers as the registered Paseo procedure ([`worker-procedure.md`](../../extras/paseo/worker-procedure.md)) describes. Paseo has no execution unit such as a Run or Task, so the coordinating session keeps the blocking order itself. If the session has no Paseo tools but has the `paseo` CLI, it does the same with the CLI and checks arguments with `paseo workspace create --help` and `paseo run --help`.

1. **Start workers**: for each ticket whose blocking tickets are all merged, it creates a worktree-isolated workspace. The workspace branches off on a new branch, based on the current branch's local ref (`refs/heads/<current branch>`), and is titled with the ticket number and title. It starts one agent in that workspace and gives it the worker spec as the first prompt. The model is picked in the order under [Profiles](#profiles).
2. **Wait**: Paseo notifies the coordinating session when a worker finishes, errors, or asks for permission. The session waits for the notification and does not poll status. It reads the result from the last response in the notification. In a session that Paseo did not start (no `PASEO_AGENT_ID` environment variable), no notification comes, so it waits with `paseo wait <agent ID>` and reads the result with `paseo logs <agent ID>`.
3. **Judge the end**: a worker ending its turn does not mean it passed. Only when the report has a branch and commit hash and that commit is on the ticket branch does the ticket pass on to the merge and integration checks; a question gets an answer; anything else counts as a failure. Permission requests inside the brief and ticket scope are approved; others go to you.
4. **Send to the same worker**: answers to questions and rebase requests go to the same agent as a follow-up prompt instead of a new agent.
5. **Cleanup**: after the merge, it archives the ticket's workspace; Paseo cleans up the agents in it and removes the worktree. If the ticket branch remains, it deletes it with `git branch -d <ticket branch>`. Workspaces of failed tickets and of tickets that failed the integration check are not archived.
6. **Resume**: it checks the status of each recorded agent ID once. A resuming session did not start the workers, so it gets no completion notifications; if Paseo started this session, it sends running workers a follow-up prompt asking them to finish and report, so the notification comes to it. It does not search for workers that are not recorded, because matching by workspace title alone can pick up another run's worker.

The worker identifier is, per ticket, the ticket number, workspace ID, agent ID, and branch, recorded as soon as the workspace and agent are created. In run-flow it goes on one line in `- 워커 식별자:` (worker identifier) in the state file.

```
- 워커 식별자: Paseo 01: 워크스페이스 <워크스페이스 ID>, 에이전트 <에이전트 ID>, 브랜치 <브랜치>; 02: 워크스페이스 <워크스페이스 ID>, 에이전트 <에이전트 ID>, 브랜치 <브랜치>
```

**Cross-review worker**: the cross review always happens, whether or not tickets run in parallel. run-ticket picks the means in this order: the means you named for this run, the means written in your settings (agent rules, harness settings, saved profiles) or the "cross-review worker" of a registered worker tool procedure, then a model from a different company found by looking up the environment. With the Paseo procedure, an agent on another company's model starts in the coordinator's workspace and the result comes with the completion notification. The model is picked in the order under [Profiles](#profiles) (such as a filled-in `cross-review`), and never from the same company as the implementing model. The first prompt holds the diff range, the full brief, the criteria list, and the verification criteria to run, and tells the agent to edit no files and report only findings, verification verdicts, and the model name. If no model from a different company can be picked, run-ticket does not drop the review: it falls back to a fresh-context review on a model from the same company, records the fallback and the model that ran it in the completion record, and continues.

The full commands and judgment rules are in [`extras/paseo/worker-procedure.md`](../../extras/paseo/worker-procedure.md), and the parallel-run flow the coordinator follows is in [run-ticket](skills/run-ticket.md#running-multiple-tickets).

## Notes

- **Worktrees are based on the local ref.** A remote ref as the base drops unpushed commits (flow documents, tickets merged earlier), so the procedure uses the local ref.
- **Workspaces are created after their blocking tickets are merged.** Created earlier, they branch from a commit without the blocking tickets' changes.
- **Worktree setup commands are read from the base branch.** The worktree setup commands in `paseo.json` are read from the version committed on the chosen base branch.
- **Editing a profile does not change agents already started.**
- **Paseo tool injection is not a security boundary.** An agent with a shell can do the same through the CLI.

## Moving from the earlier setup

When the development flow was folded into one loop in the main session, the profiles and playbooks nothing called anymore were removed, and the model values of the two remaining profiles were emptied. The investigation, cause-finding, brief drafting, implementation, screen checks, and PR descriptions the removed profiles did are now done by the main session itself; the brief cold read runs as the session's subagents, and security review is a conditional criterion of the cross review. If you merged the earlier setup, clean up as follows.

- **Profiles**: remove `locate`, `behavior-checklist`, `impact`, `root-cause`, `brief-draft`, `cold-read`, `proposal-diff`, `hard-implementer`, `skill-review`, `security-review`, `ui-check`, `pr-body`, `change-doc`, `advisor`, `env-setup`, and `connector` from `~/.paseo/config.json`, then run `paseo reload`. If they stay, a session in the parallel path may read their descriptions and pick one.
- **`ticket-worker` and `cross-review`**: you can keep your earlier values. They count as your own settings. If the description (`notes`) of `cross-review` assumes an implementing model, as in "a diff Claude implemented", replace it with the new example's description.
- **If you read material through `connector`**: pass the material as files, or run requirements analysis in a session with a connector or MCP tool that can read the link.
- **Playbooks**: in a repo where you copied the playbook, delete `.paseo/plugins/playbooks/run-ticket.yaml`, `.paseo/plugins/playbooks/roles/ticket-implementer/`, and `.paseo/plugins/playbooks/roles/ticket-reviewer/`, and commit. If you use no other playbooks, you can remove the Playbooks plugin too. Run a single ticket with the run-ticket skill.
- **Registration text**: unchanged. If you wrote earlier values in the worker model lines of register.md, you can keep them; if you delete them, the procedure picks from profiles and the environment.

---

[All docs](README.md) · [README](../../README.en.md)
