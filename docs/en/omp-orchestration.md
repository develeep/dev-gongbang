<p align="right"><a href="../omp-orchestration.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › omp multi-agent setup

# omp multi-agent setup

This guide sets up omp (oh-my-pi) so that one main session does the work of every development stage itself and starts only two read-only subagents: the cross review and the brief cold read. It installs two agents, delegation rules, and a config example. This repository does not choose models. You choose the models for the main session and the cross review in your own environment. After reading it, you can install the files in `extras/omp/`, choose models, check that they work, and migrate from an earlier install.

## Contents

- [Files](#files)
- [Install](#install)
- [Choose models](#choose-models)
- [Delegation rules](#delegation-rules)
- [Protected path blocking](#protected-path-blocking)
- [Check the setup](#check-the-setup)
- [Migrate from an earlier install](#migrate-from-an-earlier-install)
- [Notes](#notes)

## Files

| File | Install location | Role |
|---|---|---|
| [`extras/omp/config.yml`](../../extras/omp/config.yml) | Merge into `~/.omp/agent/config.yml` | An example with empty values. Slots for the cross review role `review` and the parallel worker role `worker` |
| [`extras/omp/agents/`](../../extras/omp/agents/) | `~/.omp/agent/agents/` | code-reviewer (cross review), cold-reader (brief cold read) |
| [`extras/omp/AGENTS.md`](../../extras/omp/AGENTS.md) | `~/.omp/agent/AGENTS.md` | Development stages, delegation targets, what to do on failure |
| [`extras/omp/extensions/gongbang-protected-paths.ts`](../../extras/omp/extensions/gongbang-protected-paths.ts) | `~/.omp/agent/extensions/` | Blocks writes to run-flow protected paths |

The agents and the delegation rules live at the user level, so every project and every omp session started as a worker uses the same setup. If a project's `.omp/agents/` has an agent with the same name, the project's agent wins.

## Install

From the repository root, link the agents and the delegation rules. Edits in the repository take effect from the next session.

```bash
mkdir -p ~/.omp/agent/agents
ln -s "$PWD"/extras/omp/agents/*.md ~/.omp/agent/agents/
ln -s "$PWD/extras/omp/AGENTS.md" ~/.omp/agent/AGENTS.md
mkdir -p ~/.omp/agent/extensions
ln -s "$PWD/extras/omp/extensions/gongbang-protected-paths.ts" ~/.omp/agent/extensions/
```

`config.yml` is an example with empty values. Fill in values as described in "Choose models" below, and copy only the filled lines into `modelRoles` in `~/.omp/agent/config.yml`. If a key already exists, merge inside that key. Then run `omp config get modelRoles` to check that the values load.

- `~/.omp/agent/AGENTS.md` has the highest priority among the user-level instruction files omp reads, so it hides other user-level files such as `~/.claude/CLAUDE.md`. If you still need that content, add an import line such as `@~/.claude/CLAUDE.md` to AGENTS.md.

## Choose models

You choose the models. This repository does not ship a model per role.

- **Main session**: uses the model from your usual omp settings (`modelRoles.default`) or the one you pick in the session. This model does all the work of the development stages.
- **Cross review (`modelRoles.review`)**: write a model from a different company than the main session model that implements the change, in the form `<provider>/<model id>:<effort>`. code-reviewer uses this value through `@review`. If you leave it empty, omp runs code-reviewer on the main session model without an error (checked on omp 19.2.1). That makes it a same-company review, so always fill it in.
- **Brief cold read (cold-reader)**: has no `model:` line, so it does not pin a model. The aim is to read with the model of the session that starts it; on omp 19.2.1 it does run on the session model.
- **Parallel worker (`modelRoles.worker`, optional)**: fill this only when you use a worker tool procedure. The Orca procedure uses it through `--model @worker` in the worker model line of the registration text. For the Paseo procedure, follow [Paseo orchestration setup](paseo-orchestration.md). If it is empty, the worker tool procedure's rules pick the model.

List the providers and models you can use with:

```bash
omp models <provider>
```

Models from the same company can sit under different provider names depending on whether you use a subscription or an API key. Query the provider for the sign-in method you use.

If `review` is empty, run-ticket looks up the models this session can use and picks one from a different company. If it cannot, it falls back to a fresh-context review on a model from the same company, writes that fallback in the completion record, and continues. Whether omp can pass a model to a subagent at call time has not been checked. If it cannot, an empty `review` makes every cross review a same-company fallback, so fill it in when you install.

## Delegation rules

`AGENTS.md` is read only by the main session and by omp sessions started as workers. Task subagents do not read it. It covers:

- **Development stages**: the seven stages from planning document to PR, the skill for each stage, and the points where you confirm. Running [run-flow](skills/run-flow.md) goes through them in order. The main session also writes the PR description.
- **Delegation**: completeness comes first, so work is not split in ways that lose context. The main session drafts the brief, implements, checks completion criteria and screens, works out causes of failure, does code review and rule checks, and writes the PR description itself. It starts only the two checks that need a fresh context. In the cross review, code-reviewer looks for bugs and for violations of the task boundary and the repo rules, and also for security when the change touches authentication, authorization, payments, or personal data. For the brief cold read, the main session starts three cold-readers together. The main session takes both results, verifies them, and applies them. A review skill named by the repo rules is run by the main session itself, without starting sub-agents.
- **What to hand over**: code-reviewer gets the diff range, the full brief, the list of criteria to check, and the repo rules file paths, but no secrets or raw logs. If the diff exceeds the review model's input limit, it is split by directory. cold-reader gets only the brief draft and the fixed questions, without the conversation.
- **On failure**: the main session works out the cause in the same loop and tries again. If it cannot pass within three attempts, counting the first, it stops and suggests splitting the ticket again. If a stronger model is needed, you switch the session model and continue from the state file.
- **Multiple tickets**: the main session runs them one at a time itself. Running them in parallel is optional.

The omp setup alone runs several tickets in order. To run them in parallel with workers, name the procedure document when you ask for the run, or paste the registration text into a rules file as described in [registering the Orca procedure](../../extras/orca/register.md) or [registering the Paseo procedure](../../extras/paseo/register.md), and fill in its worker model lines for your environment. Installation is described in [Orca orchestration setup](orca-orchestration.md) and [Paseo orchestration setup](paseo-orchestration.md). If you installed `~/.omp/agent/AGENTS.md` as a link as above, put the registration text in the repo's `AGENTS.md`, or keep a copy instead of the link and put it there.

How several tickets run in parallel is described in [run-ticket](skills/run-ticket.md#running-multiple-tickets).

## Protected path blocking

In a repository with an active run-flow flow, `extras/omp/extensions/gongbang-protected-paths.ts` refuses omp's `write`, `edit` (hashline, `apply_patch`, `patch`, `replace`, `sloppy`, and `magic` modes), and `ast_edit` before they run when they target a file on the protected list, and returns the reason. Subagents (`task`) get the same extension. The list and when it is on are described in [run-flow's protected list](skills/run-flow.md#protected-list).

- If the repository the target lands in has no active list (a `docs/context/run-flow/*.protected` whose state file's `- 현재 단계:` is not `완료`), it does nothing and does not run `python3`.
- If an active list exists, it runs the repository's `skills/*/run-flow/scripts/protected_paths.py` with `python3` to decide, whichever bucket run-flow is in. That is why it is installed as a link, not a copy: omp resolves the link to its real path when loading. If it cannot decide or cannot find that file, it refuses.
- `ast_edit` is refused when its folder or glob scope holds a protected file. Narrow the paths to ones without protected files and call it again.
- An `edit` whose target path cannot be read at all is refused. A hashline `MV` destination counts as a target too.
- Writes through `bash` or `eval` (JS, Python) are not blocked. run-flow catches them with `protected_paths.py verify` before it accepts a ticket.

## Check the setup

Check in a new omp session:

- `/agents` lists code-reviewer and cold-reader.
- `omp config get modelRoles` shows the `review` value you filled in.
- After running code-reviewer once, its record in the session folder (`~/.omp/agent/sessions/<project>/<session>/`) shows the model you wrote in `review`.
- Protected path blocking: from the repository root, `bun test extras/omp/extensions` (needs bun).

## Migrate from an earlier install

If you installed the earlier setup with links as in "Install" above, updating the repository breaks the links to the seven removed agent files (brief-writer, implementer, hard-implementer, test-writer, root-cause, ui-checker, doc-writer). Clean up in this order.

1. Remove the broken agent links. This command removes only links in `~/.omp/agent/agents/` whose target no longer exists.

   ```bash
   find ~/.omp/agent/agents -xtype l -print -delete
   ```

2. If `~/.omp/agent/AGENTS.md` is a link, the new rules apply right away. If you kept and edited a copy, carry the delegation table and "실패했을 때" (On failure) over from the new [`AGENTS.md`](../../extras/omp/AGENTS.md).
3. Clean up the entries you copied into `~/.omp/agent/config.yml` earlier.
   - Remove: `brief`, `slow`, `advisor`, and `vision` under `modelRoles`; the top-level `advisor` entry; `reviewer` and `security-reviewer` under `task.agentModelOverrides`; and `review`, `vision`, and `slow` under `retry.fallbackChains`. If the `review` fallback chain stays, the harness silently changes the cross review model and the fallback is not recorded.
   - Choose again: pick `modelRoles.review` and `modelRoles.worker` again for your environment, as in "Choose models" above.
   - Your call: `default`, `plan`, `task`, `smol`, `tiny`, `commit`, and `retry.fallbackChains.default` are omp's own settings, and this repository no longer sets them. You decide whether to keep your earlier values.
4. Run "Check the setup" above in a new omp session.

## Notes

- **The cross review's read-only status rests on instructions and an after-the-fact check.** code-reviewer keeps `bash` to read the diff, but has no tool for starting sub-agents. The main session compares the code fingerprint before and after the call. If it changed, the session does not use the result, shows you the change, and hands the review to the next option.
- **There is no escalation on failure.** Nothing moves the work to another agent or a stronger model automatically. omp fallback models apply only when a model is unavailable.
- **A `default` fallback chain can mix in another implementing model.** The cross review's "different company" is judged against the model that actually implemented the change, so if a fallback happened, check the model in the completion record.
- **No setting picks a model by input size.** If a diff exceeds the review model's input limit, `AGENTS.md` has the review split by directory.

---

[All docs](README.md) · [README](../../README.en.md)
