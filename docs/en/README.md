<p align="right"><a href="../README.md">한국어</a> · <b>English</b></p>

[README](../../README.en.md) › Docs

# Docs

All usage docs for dev-gongbang. Each skill page covers when to use it, prerequisites, how it works, output, how to customize it, and related skills, in the same order.

## Skills

### User-invoked

- [prompt-builder](skills/prompt-builder.md): Designs or revises system and agent prompts, CLAUDE.md, and SKILL.md through an interview.
- [building-skills](skills/building-skills.md): Completes a skill and repeats testing, review, and fixes.
- [write-docs](skills/write-docs.md): Drafts text or revises existing documents.
- [set-guidelines](skills/set-guidelines.md): Creates coding rules and linter/formatter config that fit the repo.

### Model-invoked

- [framing-problems](skills/framing-problems.md): Confirms intent, cause, and constraints as a framing record before work.
- [check-guidelines](skills/check-guidelines.md): Checks code against the repo's rules and fixes violations.

## In-progress skills

Install `gongbang-dev` to use these.

### User-invoked

- [set-brief](skills/set-brief.md): Records what was decided in the conversation as a brief.
- [set-ticket](skills/set-ticket.md): Splits a large brief into tickets.
- [run-ticket](skills/run-ticket.md): Implements and reviews one ticket in a new session.

### Model-invoked

- [analyzing-requirements](skills/analyzing-requirements.md): Turns a planning document into a requirements and development scope document.

## Guides

- [Customizing skills](customization.md): How to copy, edit, check, and test a skill
- [Choosing a skill](../../README.en.md#choosing-a-skill): Which skill fits which situation, and how skills chain together
