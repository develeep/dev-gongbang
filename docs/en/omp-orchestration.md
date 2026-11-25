<p align="right"><a href="../omp-orchestration.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › [Docs](README.md) › omp multi-agent setup

# omp multi-agent setup

This guide sets up omp (oh-my-pi) to use a different model at each development stage, with per-role models, nine subagents, and delegation rules. Design and orchestration use Opus 5.5 high, brief drafting uses Opus 5.5 xhigh, routine implementation also uses Opus 5.5 xhigh, exploration and PR descriptions use Haiku 5.5, and cross review uses GPT-6.2 Sol high. Only problems that get stuck move up to Fable 5.2 high with Opus 5.5 xhigh as an advisor. After reading it, you can install the files in `extras/omp/`, check that they work, and change models.

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
| [`extras/omp/agents/`](../../extras/omp/agents/) | `~/.omp/agent/agents/` | brief-writer, cold-reader, implementer, hard-implementer, root-cause, test-writer, ui-checker, doc-writer, code-reviewer |
| [`extras/omp/AGENTS.md`](../../extras/omp/AGENTS.md) | `~/.omp/agent/AGENTS.md` | Development stages, delegation targets, escalation on failure |

The agents and the delegation rules live at the user level, so every project and every omp session started as a worker uses the same setup. If a project's `.omp/agents/` has an agent with the same name, the project's agent wins.

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
| Brief drafting | brief-writer (`brief`) | Opus 5.5 · xhigh |
| Ticket implementation worker (parallel run, when a worker tool procedure is registered) | Orca: `--model @worker` in the worker model line of the registration text (`worker`); Paseo: the `ticket-worker` profile | Orca: Opus 5.5 · xhigh; Paseo: Opus 5.5 · medium |
| Finding code and checking behavior in a known scope | Bundled scout (`smol`) | Haiku 5.5 · medium |
| Routine implementation, tests | implementer, test-writer (`task`) | Opus 5.5 · xhigh |
| Brief cold read | cold-reader (`task`) | Opus 5.5 · xhigh |
| Review skills and their sub-reviews | code-reviewer (`review`) | GPT-6.2 Sol · high |
| Hard implementation, debugging | hard-implementer (`slow`) + advisor (`advisor`) | Fable 5.2 · high + Opus 5.5 · xhigh |
| Root-cause report without fixing | root-cause | Opus 5.5 · high |
| Cross review | Bundled reviewer (`review`) | GPT-6.2 Sol · high |
| Cross review worker (a Claude Code worker, when the implementing model is not Claude) | The worker model line of the registration text; Orca uses `--model` | Opus 5.5 · medium |
| Cross review worker (a Codex worker, when the implementing model is Claude and the reviewer fell back to Claude) | Orca: `--model` in the registration text; Paseo: the `cross-review` profile | GPT-6.2 Sol · high |
| Security and core-logic review | Bundled security-reviewer | Opus 5.5 · high |
| UI and screen checks | ui-checker (`vision`) | GPT-6.1 Terra · medium |
| Commit messages, PR descriptions | `commit`, doc-writer (`smol`) | Haiku 5.5 · medium |

This setup assumes the Anthropic subscription has more usage than the GPT subscription, so it keeps Claude effort high and uses GPT only for cross review, UI checks, and fallback. The numbers come from Artificial Analysis's per-effort comparisons.

- **Implementation**: Opus 5.5 xhigh scores 43.8% on FrontierCode-AA 2.0 and 59.6% on Terminal-Bench 4.0, above medium (33.1%, 52.5%) and above GPT-6.2 Sol medium (41.4%, 56.1%). So implementation stays on Claude instead of moving to GPT, which also keeps implementation and review on models from different companies. If responses are too slow, lower `task` and `worker` to high.
- **Hard implementation**: Implementation already runs on Opus 5.5 xhigh, so escalation goes to Fable 5.2 high, which scores 49.1% on FrontierCode-AA 2.0 against 43.8% for Opus 5.5 xhigh. The advisor is Opus 5.5 xhigh so it gives a view from a different model.
- **Documents**: Briefs stay on Opus because Opus 5.5 xhigh scores 1760 on the document-quality metric (AA-Briefcase), above Fable 5.2 xhigh (1737). PR descriptions and commit messages are short tasks that move given records into a fixed format, so they stay on Haiku 5.5.
- **Review**: Code review scores stopped rising at GPT-6.1 Sol high, and GPT-6.2 Sol also stays at high to save GPT usage.
- Sonnet 5.5 costs half as much per token as Opus 5.5 but uses more tokens, so its cost per task is about the same, and it is not used for implementation.

Why reviews use GPT-6.2 Sol instead of Astra: in OpenAI's announcement, Sol scores within 0.5 points of Astra on FrontierCode 2.0, which checks whether changes meet maintainers' merge bar, at about one fifth of the cost. On a ChatGPT subscription (`openai-codex`), Astra's context is 272K, smaller than Sol's 500K, which also hurts reviews of large diffs.

When a model is unavailable (for example, over its usage limit), the rest of the turn continues on GPT-6.2 Sol high. Review and UI checks fall back the other way, to Opus 5.5.

## Delegation rules

`AGENTS.md` is read only by the main session and by omp sessions started as workers. Task subagents do not read it. It covers:

- **Development stages**: the seven stages from planning document to PR, the skill for each stage, and the points where you confirm. Running [run-flow](skills/run-flow.md) goes through them in order.
- **Delegation**: which agent takes each kind of work. One agent gets one purpose, and a purpose is defined by the standard used to check its result. Work checked against different standards goes to separate agents, because a result that mixes standards is hard for the main session to review and to check for bugs and AI slop. Completeness comes first, though, so work is not split in ways that lose context. The agent that writes or implements something is responsible for verifying its own output and applying the results. Only checks that need a fresh context, such as a cold read or a screen check, go to a separate agent, and the agent that made the output takes their results and applies them. The cross review goes to the bundled reviewer, and review skills with their sub-reviews go to code-reviewer. Both run another company's model (GPT), so they catch mistakes the implementing model misses. The reviewer has a fixed bug-only report format and cannot follow a review skill's instructions, so the two are kept separate.
- **What to hand over**: implementation, test, and UI agents get the brief and one ticket, the repo rules file paths, the verification commands, and earlier tickets' output artifacts instead of the conversation. Review agents get the diff range and the brief. doc-writer gets the changed-file list, completion records, and review record instead of the full diff.
- **On failure**: if implementer fails, it is handed the task once more along with the failure report; if it fails the same ticket twice, hard-implementer takes it. If that also fails, or the cause of failure is an ambiguous ticket, the session stops and suggests splitting the ticket again. A large refactor or a debugging task with an unknown cause from the start goes straight to hard-implementer. When only a root-cause report is needed without a fix, such as when integration verification fails, root-cause takes it.
- **Multiple tickets**: unless you or the rules name a usable worker tool procedure and the parallel-run conditions are met, several tickets run one after another with subagents, and the subagent started for each ticket is the implementation agent from the delegation table. The cross review is done by a model from a different company than the model that implemented the change. In this setup the implementation agents are all Claude, so the reviewer (GPT) takes it whatever the main session's model is.

The omp setup alone runs several tickets in order. To run them in parallel with workers, name the procedure document when you ask for the run, or paste the registration text into a rules file as described in [registering the Orca procedure](../../extras/orca/register.md) or [registering the Paseo procedure](../../extras/paseo/register.md). "워커 모델 정하기" (Setting worker models) in each document has worker model values that match this setup. Installation is described in [Orca orchestration setup](orca-orchestration.md) and [Paseo orchestration setup](paseo-orchestration.md). If you installed `~/.omp/agent/AGENTS.md` as a link as above, put the registration text in the repo's `AGENTS.md`, or keep a copy instead of the link and put it there.

How several tickets run in parallel is described in [run-ticket](skills/run-ticket.md#running-multiple-tickets).

## Check the setup

Check in a new omp session:

- `/agents` lists brief-writer, cold-reader, implementer, hard-implementer, root-cause, test-writer, ui-checker, doc-writer, and code-reviewer.
- After running each agent once, its record in the session folder (`~/.omp/agent/sessions/<project>/<session>/`) shows the model from the table above.
- After running hard-implementer, its agent folder has an `__advisor.jsonl`. This is the advisor model's (Opus 5.5) record.

## Change models

- To change a stage's model, change only that role in `modelRoles`. Agent files point to roles such as `@task`, so you do not need to edit them. Only the models of the Claude Code and Codex cross review workers are written directly, in the worker model lines of the worker tool procedure's registration text, because omp roles cannot be used for another agent's workers. For the ticket implementation worker's model, edit `modelRoles.worker` with the Orca procedure, or the `ticket-worker` profile with the Paseo procedure.
- To cut cost, lower the effort before switching to another model.
- Do not use `max` as a default. Cost rises sharply and scores sometimes drop.
- Keep the effort fixed within one conversation. Changing it invalidates the prompt cache.

## Notes

- **Escalation on failure is a rule, not a setting.** omp fallback models apply only when a model is unavailable. The main session, reading `AGENTS.md`, decides when to move from implementer to hard-implementer.
- **Escalation has one step.** It goes straight from Opus 5.5 xhigh to Fable 5.2 high with the Opus 5.5 xhigh advisor. To add a step in between, create one more agent with that model in `model:` and add it to "실패했을 때" (On failure) in `AGENTS.md`.
- **Fable 5.2 usage limit**: If your subscription tracks Fable usage separately from Opus, hard-implementer may hit its limit first. It then continues on Opus 5.5 xhigh through `retry.fallbackChains.slow`.
- **No setting picks a model by input size.** GPT doubles its input price and raises its output price 1.5 times when input exceeds 272K tokens, so `AGENTS.md` has large diffs split by directory before review.
- **Only hard-implementer has an advisor.** `advisor: true` in the agent file attaches an advisor to that agent alone, regardless of the global `advisor.enabled: false`. An advisor reads every turn of its session, so keep it off in the main session.
- **Haiku 5.5 has a 100K context.** It is smaller than the other models (1M), so give scout a narrow search scope.

---

[All docs](README.md) · [README](../../README.en.md)
