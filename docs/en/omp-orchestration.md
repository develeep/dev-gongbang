<p align="right"><a href="../omp-orchestration.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › omp multi-agent setup

# omp multi-agent setup

This guide sets up omp (oh-my-pi) so that one main session does all the work from planning document to PR itself and hands only the two checks that need a fresh context, the cross review and the brief cold read, to read-only subagents. `extras/omp/` holds two agents, delegation rules, a model config example, and an extension that blocks writes to run-flow protected paths. This repository does not choose models; you choose them in your own environment. After reading this guide, you can install these files, choose the cross review model, check the setup, and clean up an earlier install.

## Contents

- [Files](#files)
- [Install](#install)
- [Choose models](#choose-models)
- [Check the setup](#check-the-setup)
- [Delegation rules](#delegation-rules)
- [Protected path blocking](#protected-path-blocking)
- [Notes](#notes)
- [Migrate from an earlier install](#migrate-from-an-earlier-install)

## Files

| File | Install location | Role |
|---|---|---|
| [`extras/omp/agents/`](../../extras/omp/agents/) | `~/.omp/agent/agents/` | code-reviewer (cross review), cold-reader (brief cold read) |
| [`extras/omp/AGENTS.md`](../../extras/omp/AGENTS.md) | `~/.omp/agent/AGENTS.md` | Rules the main session follows: development stages, delegation, what to hand over, what to do on failure |
| [`extras/omp/extensions/gongbang-protected-paths.ts`](../../extras/omp/extensions/gongbang-protected-paths.ts) | `~/.omp/agent/extensions/` | Blocks writes to run-flow protected paths |
| [`extras/omp/config.yml`](../../extras/omp/config.yml) | Merge into `~/.omp/agent/config.yml` | An example with empty values. Slots for the cross review role `review` and the parallel worker role `worker` |

The agents and the delegation rules live at the user level, so every project and every omp session started as a worker uses the same setup. If a project's `.omp/agents/` has an agent with the same name, the project's agent wins.

## Install

If you installed the earlier setup, do [Migrate from an earlier install](#migrate-from-an-earlier-install) first.

1. **Link the files**: from the repository root, link the agents, the delegation rules, and the extension. Edits in the repository take effect from the next session. The extension looks up the judging script inside the repository, so it must be a link ([Protected path blocking](#protected-path-blocking)).

   ```bash
   mkdir -p ~/.omp/agent/agents ~/.omp/agent/extensions
   ln -s "$PWD"/extras/omp/agents/*.md ~/.omp/agent/agents/
   ln -s "$PWD/extras/omp/AGENTS.md" ~/.omp/agent/AGENTS.md
   ln -s "$PWD/extras/omp/extensions/gongbang-protected-paths.ts" ~/.omp/agent/extensions/
   ```

2. **Set the models**: `extras/omp/config.yml` is an example with empty values. Fill in `review` (required) and `worker` (optional) as described in [Choose models](#choose-models) below, and copy only the filled lines into `modelRoles` in `~/.omp/agent/config.yml`. If `modelRoles` already exists, merge into it. Then run `omp config get modelRoles` to check that the values load.
3. **Import other instruction files (if needed)**: `~/.omp/agent/AGENTS.md` has the highest priority among the user-level instruction files omp reads, so it hides other user-level files such as `~/.claude/CLAUDE.md`. If you still need that content, add an import line such as `@~/.claude/CLAUDE.md` to AGENTS.md. If AGENTS.md is a link, that line would go into the file in your clone, so keep a copy instead of the link and add it there.

## Choose models

You choose the models. This repository does not ship a model per role. Write values in the form `<provider>/<model id>:<effort>`.

- **Main session**: uses the model from your usual omp settings (`modelRoles.default`) or the one you pick in the session. This model does all the work of the development stages.
- **Cross review (`modelRoles.review`)**: write a model from a different company than the main session model that implements the change. code-reviewer uses this value through `@review`. If you leave it empty, omp runs code-reviewer on the main session model without an error (checked on omp 19.2.1). That makes it a same-company review, so always fill it in.
- **Brief cold read (cold-reader)**: has no `model:` line, so it runs on the model of the session that starts it (checked on omp 19.2.1). It pins no model so that it surfaces the reading differences the worker who actually implements the brief would hit.
- **Parallel worker (`modelRoles.worker`, optional)**: fill this only when a worker tool procedure runs tickets in parallel. The Orca procedure uses it when you write `--model @worker` in the worker model line of the registration text ([Orca orchestration setup](orca-orchestration.md)). The Paseo procedure does not use it; it picks from the worker model lines of the registration text and Paseo profiles ([Paseo orchestration setup](paseo-orchestration.md)). If it is empty, the worker tool procedure's rules pick the model.

List the providers and models you can use with the command below. Models from the same company can sit under different provider names depending on whether you use a subscription or an API key, so query the provider for the sign-in method you use.

```bash
omp models <provider>
```

If `review` is empty, run-ticket looks up the models this session can use and picks one from a different company. If it cannot, it falls back to a fresh-context review on a model from the same company, writes that in the completion record, and continues. Whether omp can pass a model to a subagent at call time has not been checked. If it cannot, an empty `review` makes every cross review a same-company fallback, so fill it in when you install.

## Check the setup

Check in a new omp session:

- `/agents` lists code-reviewer and cold-reader.
- `omp config get modelRoles` shows the `review` value you filled in.
- After running code-reviewer once, its record in the session folder (`~/.omp/agent/sessions/<project>/<session>/`) shows the model you wrote in `review`.
- Protected path blocking: from the repository root, `bun test extras/omp/extensions` passes (needs bun).

## Delegation rules

`AGENTS.md` is read by the main session and by omp sessions started as workers. Task subagents do not get it. It sets these rules.

**Development stages**: the seven stages from planning document to PR run in the order below. Running `/skill:run-flow` has run-flow go through them in order ([run-flow](skills/run-flow.md)). When you run the stages one at a time, the end of each stage reports where its output is and what comes next.

| Order | Stage | Skill |
|---|---|---|
| 1 | 요구사항 정리 (Requirements) | analyzing-requirements |
| 2 | 문제 구체화 (Problem framing) | framing-problems |
| 3 | 작업 지시서 (Brief) | set-brief |
| 4 | 티켓 분할 (Ticket split) | set-ticket |
| 5 | 티켓 구현 (Ticket implementation) | run-ticket |
| 6 | 규칙 검사·교차 리뷰 (Rule check and cross review) | run-ticket's review stage |
| 7 | PR | The main session writes the description and run-flow opens the PR |

**Delegation**: completeness comes first, so work is not split in ways that lose context. The main session drafts the brief, implements, checks completion criteria and screens, works out why a ticket failed, does code review and rule checks, and writes the PR description itself. It starts only the two checks that need a fresh context as read-only subagents, then verifies and applies what comes back.

| Check | Agent | What it does |
|---|---|---|
| Cross review | code-reviewer | On a model from a different company than the implementing model, looks for bugs and for violations of the task boundary and the repo rules, and also for security when the change touches authentication, authorization, payments, or personal data. Runs the verification criteria commands itself to judge them |
| Brief cold read | cold-reader | The main session starts three of them in one message. Each reads only the brief draft, without the conversation, and answers fixed questions |

A review skill named by the repo rules is run by the main session itself in a way that starts no sub-agents; if it cannot be run that way, the main session reviews directly and notes it in the report.

**What goes out and what comes back**:

- code-reviewer gets the diff range (from the HEAD where the work started), the full brief, the list of criteria to check, the repo rules file paths, and the verification criteria to run. No secrets or raw logs.
- If the diff exceeds the review model's input limit, the review is split by directory. Shared types, APIs, and settings that cross directories go with every review, and the main session looks for defects that cross directory boundaries.
- code-reviewer returns only the findings (criterion, severity, file and line, evidence, how to fix), a `met`, `unmet`, or `확인 못 함` (could not check) verdict per verification criterion, and the name of the model that ran. The main session reproduces each finding or compares it with the code or rule text, and marks it `수용 / 기각(사유) / 범위 밖` (accepted / rejected (reason) / out of scope).
- cold-reader gets only the full brief draft, the repository path, and the fixed questions, without the conversation.

**On failure**: if a ticket fails its completion criteria or tests, the main session works out the cause in the same loop and tries again. If the cause is an unclear or oversized ticket, it stops instead of retrying. If it cannot pass within three attempts, counting the first, it stops, writes the attempt count and cause in `- 멈춘 이유:` (reason stopped) in the state file, and suggests splitting the ticket again with `/skill:set-ticket`. If a stronger model is needed, you switch the session model and continue from the state file.

**Multiple tickets**: the main session runs them one at a time itself. It runs them in parallel only when you or the rules name a worker tool procedure and run-ticket's conditions for a parallel run are met. If the integration check fails in a parallel run, the main session works out the cause itself. The steps are in [run-ticket's running multiple tickets](skills/run-ticket.md#running-multiple-tickets).

To run tickets in parallel with workers, name the procedure document when you ask for the run, or paste the registration text into a rules file as described under "Register the procedure" in [Orca orchestration setup](orca-orchestration.md) or [Paseo orchestration setup](paseo-orchestration.md). If you installed `~/.omp/agent/AGENTS.md` as a link, put the registration text in the repo's `AGENTS.md`, or keep a copy instead of the link and put it there.

## Protected path blocking

In a repository with an active run-flow flow, `extras/omp/extensions/gongbang-protected-paths.ts` refuses omp's `write`, `edit` (hashline, `apply_patch`, `patch`, `replace`, `sloppy`, and `magic` modes), and `ast_edit` before they run when they target a file on the protected list, and returns the reason. Subagents (`task`) get the same extension. The list and when it is on are described in [run-flow's protected list](skills/run-flow.md#protected-list).

- If the repository the target lands in has no active list (a `docs/context/run-flow/*.protected` whose state file's `- 현재 단계:` (current stage) is not `완료` (done)), it does nothing and does not run `python3`.
- If an active list exists, it runs the repository's `skills/*/run-flow/scripts/protected_paths.py` with `python3` to decide, whichever bucket run-flow is in. omp resolves the link to its real path when it loads the extension, so only a linked extension finds this script inside the repository.
- If it cannot find the script, cannot decide, or the decision takes longer than 20 seconds, it refuses.
- `ast_edit` is refused when its folder or glob scope holds a protected file. Narrow the paths to ones without protected files and call it again.
- An `edit` whose target path cannot be read at all is refused. A hashline `MV` destination counts as a target too.
- Writes through `bash` or `eval` (JS, Python) are not blocked. run-flow catches them with `protected_paths.py verify` before it accepts a ticket.

## Notes

- **The cross review stays read-only through instructions and an after-the-fact check.** code-reviewer keeps `bash` to read the diff and run the verification criteria commands, but has no tool for starting sub-agents. Verification commands that change repository files (snapshot updates, formatters in write mode, and so on) are not run and are marked `확인 못 함` (could not check). The main session compares the code fingerprint before and after the call; if it changed, the session does not use the result, shows you what changed, and hands the review to the next option.
- **Failure does not escalate automatically.** Nothing moves the work to another agent or a stronger model automatically. omp fallback models apply only when a model is unavailable.
- **A `default` fallback chain can mix in another implementing model.** The cross review's "different company" is judged against the model that actually implemented the change, so if a fallback happened, check the model in the completion record.
- **No setting picks a model by input size.** If a diff exceeds the review model's input limit, `AGENTS.md` has the review split by directory.

## Migrate from an earlier install

If you installed the earlier setup with links, updating the repository breaks the links to the seven removed agents (brief-writer, implementer, hard-implementer, test-writer, root-cause, ui-checker, doc-writer). Clean up in this order.

1. Remove the broken agent links. This command removes only links in `~/.omp/agent/agents/` whose target no longer exists.

   ```bash
   find ~/.omp/agent/agents -xtype l -print -delete
   ```

2. If `~/.omp/agent/AGENTS.md` is a link, the new rules apply right away. If you edited a copy, carry "위임" (Delegation) and "실패했을 때" (On failure) over from the new [`AGENTS.md`](../../extras/omp/AGENTS.md).
3. Clean up the entries you copied into `~/.omp/agent/config.yml` earlier.
   - Remove: `brief`, `slow`, `advisor`, and `vision` under `modelRoles`; the top-level `advisor`; `reviewer` and `security-reviewer` under `task.agentModelOverrides`; and `review`, `vision`, and `slow` under `retry.fallbackChains`. If the `review` fallback chain stays, the harness silently changes the cross review model and the fallback is not recorded.
   - Choose again: pick `modelRoles.review` and `modelRoles.worker` as in [Choose models](#choose-models).
   - Fine to keep: `default`, `plan`, `task`, `smol`, `tiny`, `commit`, and `retry.fallbackChains.default` are omp's own settings, and this repository no longer sets them.
4. Run [Check the setup](#check-the-setup) in a new omp session.

---

[All docs](README.md) · [README](../../README.en.md)
