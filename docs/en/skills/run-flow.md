<p align="right"><a href="../../skills/run-flow.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › run-flow

# run-flow

Takes a planning document, a request, or a brief and runs the development stages in order, from organizing requirements to opening a PR. It loads the skill for each stage itself, so you do not run each stage's skill by hand. You only answer the confirmations and questions each skill asks.

> This skill is in progress. Install `gongbang-dev` to use it. Its behavior may change.

| Field | Value |
|---|---|
| Bucket | in-progress |
| Invocation | User-invoked |
| Command | `/gongbang:run-flow [planning doc path/link \| request \| brief path/issue number]` |
| Source | [SKILL.md](../../../skills/in-progress/run-flow/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

- You want to go from a planning document or a request to a PR, answering only confirmations and questions along the way.
- You want to finish a brief that stopped partway. Run it without an argument and it finds an unfinished brief and continues. The framing record lives only in the conversation, so if it stopped before the brief was published, start again with the original argument.
- You run several features at once. Create one Orca workspace per feature and run run-flow in each.

## Prerequisites

- The stage skills: analyzing-requirements, framing-problems, set-brief, set-ticket, run-ticket. Installing `gongbang` and `gongbang-dev` together provides all of them.
- To run several tickets in parallel, Orca must be running and the `orchestration` skill installed. Otherwise tickets run in order.
- To open a PR, you need a github.com remote and a logged-in `gh` CLI. Otherwise it shows the PR description and stops.
- To use a different model at each stage, install the [omp multi-agent setup](../omp-orchestration.md).

## How it works

0. It picks the starting stage from the argument. A brief starts at stage 4 to 6 depending on its ticket status, a requirements document or a request sentence at stage 2, and a planning document at stage 1. A brief is also a Markdown document, so it is checked before the planning-document rule. Without an argument it looks for unfinished briefs and, if there are several, lists them for you to choose.
1. **Requirements**: analyzing-requirements turns the planning document into a requirements document.
2. **Framing**: if there are several development scopes, you pick one for this run; then framing-problems confirms a framing record.
3. **Brief**: set-brief records the brief. If the remaining work will not fit in one session, it goes to stage 4; otherwise to stage 5.
4. **Tickets**: set-ticket splits the brief into tickets and publishes them.
5. **Implementation and review**: if the current branch is the default branch, it first asks for a work branch name and creates it. Then run-ticket runs all remaining tickets. With Orca, it starts one worker per ticket and runs them in parallel. Even a single ticket goes to a worker or subagent with a fresh context, so the implementer works from the brief and ticket alone, without this conversation. If a ticket fails its done criteria, it stops and asks whether to split the ticket again.
6. **Merge and PR decision**: it collects done criteria results, review findings, changed files, and commits, and asks you to choose: open a PR, fix something, or stop. When it starts at stage 6 without a run-ticket report, it collects them from the tickets' completion records and the git history.
7. **Open the PR**: if needed, it creates a work branch and commits, then writes the PR description, pushes, and opens the PR.

Every confirmation a stage skill asks (confirming the framing record, where to save the requirements document, the brief draft and where to publish it, the ticket split, the Orca run plan) is still asked. What run-flow removes is running the next skill yourself each time a stage ends.

## Output

- A requirements document, a brief, tickets, the implemented code, and commits
- A GitHub PR. You do the merge.
- A final report: where each stage's output is, the PR URL, and review findings not fixed

## Customize

| What to change | Where to edit |
|---|---|
| Starting stage per argument | SKILL.md "0. 시작 단계 고르기" (0. Pick the starting stage) |
| How tickets run | run-ticket's SKILL.md, or name a ticket execution skill in the repo rules |
| PR description format | The repo's PR template, or SKILL.md "7. PR 만들기" (7. Open the PR) |

Behavior inside a stage is changed in that stage's skill. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **analyzing-requirements**, **framing-problems**, **set-brief**, **set-ticket**, **run-ticket**: the skills it loads at each stage. set-brief, set-ticket, and run-ticket are Model-invoked so that run-flow can load them, and they run only when you or another skill asks for them.
- **orchestration** (Orca): used for the parallel run in stage 5 and for cross-review workers.

---

← Previous: [check-guidelines](check-guidelines.md) · [All docs](../README.md) · Next: [set-brief](set-brief.md) →
