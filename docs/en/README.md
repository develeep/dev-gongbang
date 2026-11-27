<p align="right"><a href="../README.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › Docs

# Docs

The list of dev-gongbang usage docs. Find how to use each skill, how to install the mods, how to customize a skill, and how to set up agents and worker tools here. Each skill page covers when to use it, prerequisites, how it works, output, how to customize it, and related skills, in the same order.

## Skills

Available when you install `gongbang`.

### User-invoked

- [prompt-builder](skills/prompt-builder.md): Designs system and agent prompts, CLAUDE.md, and SKILL.md through an interview that follows the Claude and GPT per-model guides, or revises and reviews an existing draft.
- [building-skills](skills/building-skills.md): Completes a skill from a SKILL.md draft or from material such as conversation logs, runbooks, or code, then repeats static checks, test runs, human review, and fixes.
- [write-docs](skills/write-docs.md): Sets field, audience, purpose, tone, and material through questions, then drafts the text or revises a draft or existing document you bring.
- [set-guidelines](skills/set-guidelines.md): Picks guides from awesome-guidelines that fit the repo's languages and frameworks, then writes the ones you choose: `.claude/rules/` rule files, CLAUDE.md/AGENTS.md, and linter/formatter config.

### Model-invoked

- [framing-problems](skills/framing-problems.md): Before work starts, confirms with you a framing record of intent, cause, and constraints.
- [check-guidelines](skills/check-guidelines.md): Checks code in the chosen scope against the repo's rule files and linter/formatter config, and fixes the violations you choose.

## In-progress skills

Install `gongbang-dev` to use these. Their behavior changes often.

### User-invoked

- [run-flow](skills/run-flow.md): Takes a planning document, a request, or a brief and loads the stage skills in order, from organizing requirements to opening a PR.

### Model-invoked

- [set-brief](skills/set-brief.md): Records a framing record or session result as a brief that a worker with no context can pick up.
- [set-ticket](skills/set-ticket.md): Splits a large brief into tickets that can each be verified on their own.
- [run-ticket](skills/run-ticket.md): Takes the brief and ticket documents and implements and reviews one ticket. Several tickets run in order, and run in parallel on workers only when a worker tool procedure is named or registered.
- [analyzing-requirements](skills/analyzing-requirements.md): Turns a planning document into a requirements and development scope document.

## Mods

- [gongbang-mods](mods.md): In the Claude Code screen, folds tool calls to one line, splits messages into cards, and shows the session goal and context usage in a side pane. The page also covers blocking writes to run-flow protected paths, outside mods that pair well, the status line script, and `extras/setup.sh`.

## Guides

- [Customizing skills](customization.md): How to copy, edit, check, and test a skill
- [omp multi-agent setup](omp-orchestration.md): How to install the cross-review and brief cold-read agents, the delegation rules, and the protected path extension in omp (oh-my-pi), and choose your models
- [Orca orchestration setup](orca-orchestration.md): Optional setup that installs Orca and registers its worker procedure in a rules file so run-ticket can run several tickets in parallel on Orca workers, and how the Orca mode works
- [Paseo orchestration setup](paseo-orchestration.md): Optional setup that installs the Paseo agent profiles and workspace scripts and registers the worker procedure in a rules file so run-ticket can run several tickets in parallel on Paseo workers, and how the Paseo mode works
- [Choosing a skill](../../README.en.md#choosing-a-skill): Which skill fits which situation, and how skills chain together
