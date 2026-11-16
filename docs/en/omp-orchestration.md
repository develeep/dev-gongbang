<p align="right"><a href="../omp-orchestration.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › omp multi-agent setup

# omp multi-agent setup

This guide sets up omp (oh-my-pi) to use a different model at each development stage, with per-role models, six subagents, and delegation rules. Design and orchestration use Opus 5.5 high, routine implementation uses Sonnet 5.5 medium, exploration and docs use Haiku 5.5, and cross review uses GPT-6.1 Sol high. Only problems that get stuck move up to Opus 5.5 xhigh with Fable 5.2 as an advisor. After reading it, you can install the files in `extras/omp/`, check that they work, and change models.

## Contents

- [Files](#files)
- [Install](#install)
- [Models per stage](#models-per-stage)
- [Delegation rules](#delegation-rules)
- [Check the setup](#check-the-setup)
- [Change models](#change-models)
- [Notes](#notes)

## Files

| File | Install location | Role |
|---|---|---|
| [`extras/omp/config.yml`](../../extras/omp/config.yml) | Merge into `~/.omp/agent/config.yml` | Per-role models and effort, reviewer and security-reviewer models, fallback models |
| [`extras/omp/agents/`](../../extras/omp/agents/) | `~/.omp/agent/agents/` | brief-writer, implementer, hard-implementer, test-writer, ui-checker, doc-writer |
| [`extras/omp/AGENTS.md`](../../extras/omp/AGENTS.md) | `~/.omp/agent/AGENTS.md` | Development stages, delegation targets, escalation on failure, when to use Orca |

The agents and the delegation rules live at the user level, so every project and every Orca worker uses the same setup. If a project's `.omp/agents/` has an agent with the same name, the project's agent wins.

## Install

From the repository root, link the agents and the delegation rules. Edits in the repository take effect from the next session.

```bash
mkdir -p ~/.omp/agent/agents
ln -s "$PWD"/extras/omp/agents/*.md ~/.omp/agent/agents/
ln -s "$PWD/extras/omp/AGENTS.md" ~/.omp/agent/AGENTS.md
```

To keep your existing settings, copy the `modelRoles`, `advisor`, `task`, and `retry.fallbackChains` entries from `config.yml` into `~/.omp/agent/config.yml` by hand. If a key already exists, merge inside that key. Then run `omp config get modelRoles` to check that the values load.

- GPT entries assume a ChatGPT subscription (`openai-codex`). If you use an OpenAI API key, change `openai-codex/` to `openai/`. List the available models with `omp models openai-codex` and `omp models openai`.
- `~/.omp/agent/AGENTS.md` has the highest priority among the user-level instruction files omp reads, so it hides other user-level files such as `~/.claude/CLAUDE.md`. If you still need that content, add an import line such as `@~/.claude/CLAUDE.md` to AGENTS.md.

## Models per stage

| Stage | omp setting | Model · effort |
|---|---|---|
| Orchestrator, design | Main session `default`, plan mode `plan` | Opus 5.5 · high |
| Brief drafting | brief-writer (`default`) | Opus 5.5 · high |
| Code exploration | Bundled scout (`smol`) | Haiku 5.5 · medium |
| Routine implementation, tests, brief cold-read check | implementer, test-writer (`task`) | Sonnet 5.5 · medium |
| Hard implementation, debugging | hard-implementer (`slow`) + advisor (`advisor`) | Opus 5.5 · xhigh + Fable 5.2 · high |
| Cross review, sub-reviews of the code review skill | Bundled reviewer (`review`) | GPT-6.1 Sol · high |
| Security and core-logic review | Bundled security-reviewer | Opus 5.5 · high |
| UI and screen checks | ui-checker (`vision`) | GPT-6.1 Terra · medium |
| Commit messages, PR descriptions | `commit`, doc-writer (`smol`) | Haiku 5.5 · medium |

When a model is unavailable (for example, over its usage limit), the rest of the turn continues on GPT-6.1 Sol high. Review and UI checks fall back the other way, to Opus 5.5.

## Delegation rules

`AGENTS.md` is read only by the main session and by omp workers started by Orca. Task subagents do not read it. It covers:

- **Development stages**: the seven stages from planning document to PR, the skill for each stage, and the points where you confirm. Running [run-flow](skills/run-flow.md) goes through them in order.
- **Delegation**: which agent takes each kind of work
- **What to hand over**: implementation, test, and UI agents get the brief and one ticket, the repo rules file paths, the verification commands, and earlier tickets' output artifacts instead of the conversation. Review agents get the diff range and the brief. doc-writer gets the changed-file list, completion records, and review record instead of the full diff.
- **On failure**: if implementer fails, it is handed the task once more along with the failure report; if it fails the same ticket twice, hard-implementer takes it. If that also fails, or the cause of failure is an ambiguous ticket, the session stops and suggests splitting the ticket again. A large refactor or a debugging task with an unknown cause from the start goes straight to hard-implementer.
- **Orca**: Orca workers are used only to run tickets in parallel in separate worktrees when two or more tickets can start together, to hand work to another agent, or when you want to watch a worker directly.

How several tickets run in parallel is described in [run-ticket](skills/run-ticket.md#running-multiple-tickets).

## Check the setup

Check in a new omp session:

- `/agents` lists brief-writer, implementer, hard-implementer, test-writer, ui-checker, and doc-writer.
- After running each agent once, its record in the session folder (`~/.omp/agent/sessions/<project>/<session>/`) shows the model from the table above.
- After running hard-implementer, its agent folder has an `__advisor.jsonl`. This is the advisor model's (Fable 5.2) record.

## Change models

- To change a stage's model, change only that role in `modelRoles`. Agent files point to roles such as `@task`, so you do not need to edit them.
- To cut cost, lower the effort before switching to another model.
- Do not use `max` as a default. Cost rises sharply and scores sometimes drop.
- Keep the effort fixed within one conversation. Changing it invalidates the prompt cache.

## Notes

- **Escalation on failure is a rule, not a setting.** omp fallback models apply only when a model is unavailable. The main session, reading `AGENTS.md`, decides when to move from implementer to hard-implementer.
- **Escalation has one step.** It goes straight from Sonnet 5.5 medium to Opus 5.5 xhigh with the Fable 5.2 advisor. To add a Sonnet 5.5 high step in between, create one more agent with `model: anthropic/claude-sonnet-5-5:high` and add it to "실패했을 때" (On failure) in `AGENTS.md`.
- **No setting picks a model by input size.** GPT doubles its price when input exceeds 272K tokens, so `AGENTS.md` has large diffs split by directory before review.
- **Only hard-implementer has an advisor.** `advisor: true` in the agent file attaches an advisor to that agent alone, regardless of the global `advisor.enabled: false`. An advisor reads every turn of its session, so keep it off in the main session.
- **Haiku 5.5 has a 100K context.** It is smaller than the other models (1M), so give scout a narrow search scope.

---

[All docs](README.md) · [README](../../README.en.md)
