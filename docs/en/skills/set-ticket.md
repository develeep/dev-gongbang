<p align="right"><a href="../../skills/set-ticket.md">한국어</a> · <b>English</b></p>

# set-ticket

Splits one brief recorded with set-brief into several tickets. Each ticket is written so that reading it alone is enough to finish its work. It links the ticket list to the original brief.

> This skill is in progress. Install `gongbang-dev` to use it. Its behavior may change.

| Field | Value |
|---|---|
| Bucket | in-progress |
| Invocation | User-invoked |
| Command | `/gongbang:set-ticket [brief issue number/URL or docs path]` |
| Source | [SKILL.md](../../../skills/in-progress/set-ticket/SKILL.md) |

## When to use

- The brief's "남은 일" (remaining work) is too big to finish in one new context window.

## Prerequisites

- A brief made with set-brief. Without an argument, it looks first for the brief just published in this conversation, then for the most recent brief. Briefs already split into tickets or finished are skipped.
- For a GitHub issue brief, the `gh` CLI must be logged in.

## How it works

1. It finds the brief and reads all of it.
2. It looks at the code in the area the brief covers. It follows a glossary or ADRs if they exist, and looks for prefactoring that makes the implementation easier.
3. It writes a split plan.
   - Each ticket is a vertical slice that cuts narrowly through every layer it needs (schema, API, UI, tests).
   - Each ticket gets done criteria and a blocked-by relation (tickets that must finish first).
   - When one ticket uses another ticket's result, it points to it as "NN 티켓의 산출물" (output artifact of ticket NN).
   - A broad refactor where no slice can go green on its own is split in expand → migrate → contract order.
4. It shows the split plan as a numbered list and asks about size, blocked-by relations, and tickets to merge or split. It revises until you approve.
5. It publishes in blocked-by order and appends a "티켓" (Tickets) section to the brief.

## Output

- **GitHub issue**: ticket issues with the `ready-for-agent` label, linked to the brief as sub-issues, with blocked-by relations linked as issue dependencies. If linking fails, it writes them in the body.
- **docs document**: tickets saved as `NN-<slug>.md` in a `docs/context/YYYY-MM-DD-<brief-slug>/` folder next to the brief. The status starts as `ready-for-agent`. It does not commit.

It does not close the brief, and it does not change the brief except to append the "티켓" section.

## Customize

| What to change | Where to edit |
|---|---|
| Ticket section structure | SKILL.md "이슈 티켓 템플릿" (Issue ticket template), "docs 티켓 템플릿" (docs ticket template) |
| Split criteria | SKILL.md "핵심 규칙" (Core rules) 1 to 2, "3. 분할안 작성" (3. Write the split plan) |
| Label name | SKILL.md "5. 게시와 brief 연결" (5. Publish and link to the brief) |

If you change section names in the ticket templates or the `- 상태:` (status) line, you must also change run-ticket. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **set-brief**: creates the brief to split.
- **run-ticket**: runs the published tickets one at a time in a new session. It is User-invoked, so set-ticket does not call it directly and tells you how to run it.
