<p align="right"><a href="../../skills/run-ticket.md">한국어</a> · <b>English</b></p>

# run-ticket

Implements and reviews one ticket made by set-ticket in a new session, then updates the ticket status and the brief checkboxes. It works without the conversation that made the brief, using only the brief, the ticket, and the completion records of earlier tickets. It does not commit.

> This skill is in progress. Install `gongbang-dev` to use it. Its behavior may change.

| Field | Value |
|---|---|
| Bucket | in-progress |
| Invocation | User-invoked |
| Command | `/gongbang:run-ticket [ticket/brief path, issue number/URL] [range for multiple tickets]` |
| Source | [SKILL.md](../../../skills/in-progress/run-ticket/SKILL.md) |

## When to use

- Run the tickets split with set-ticket one at a time.
- Run a small brief that was not split into tickets. The whole brief is treated as one ticket.
- Run several tickets in order, as in "all remaining tickets".

## Prerequisites

- A brief and tickets made with set-brief and set-ticket
- For GitHub tickets, the `gh` CLI must be logged in.
- If the working tree has changes outside the brief and tickets, it asks whether to commit them before continuing. If you continue as is, earlier changes get mixed into the review.

## How it works

1. It picks a ticket. Without an argument, it takes the most recent brief that still has unfinished tickets, and picks the lowest-numbered ticket whose blocked-by relations are cleared.
2. It reads the ticket, the full brief, the completion records of finished tickets in the same brief, and the repo's CLAUDE.md and AGENTS.md.
3. It implements "만들 것" (what to build). It does not fix problems outside the ticket's scope and leaves them in the report.
4. It checks each done criterion with a command or observation. If one fails, it fixes it. If it cannot fix it, it stops and reports.
5. It reviews, using the first method that applies in this order: the review skill named in the repo rules, the `code-review` skill, its own review.
6. It sets the ticket status to done or closes the issue, updates the brief checkboxes, and leaves a completion record. For the last ticket, it runs the brief's "확인 기준" (verification criteria) and closes the brief.

If the ticket and the repo rules conflict, it asks before continuing. The priority is: the ticket's "하면 안 되는 것" (what not to do) and "작업 경계" (work boundaries), then the repo rules, then the skill's default behavior.

### Running multiple tickets

If you ask for a number range or "all remaining tickets", it starts one subagent per ticket, one after another. They edit the same working tree, so it does not run them in parallel. If a ticket fails its done criteria, it stops. When all are done, it reviews the whole change once.

## Output

- The implemented code changes (not committed)
- A completion record attached to the ticket: completion date, a not-committed note with the HEAD at work start, and changed files. Results other tickets will use go under `## 산출물` (output artifact).
- A report: finished ticket, done criteria results, changed files, output artifact location, review findings not fixed, next ticket

## Customize

| What to change | Where to edit |
|---|---|
| Ticket selection rules | SKILL.md "1. 티켓 고르기" (1. Pick a ticket) |
| Priority of review methods | SKILL.md "5. 리뷰" (5. Review) |
| Completion record format | SKILL.md "6. 완료 기록" (6. Completion record) |

Not committing is a core rule. Even if the repo rules require commits, it leaves that to the user. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **set-brief**, **set-ticket**: create the brief and tickets to run.
- If the **code-review** skill is installed, it is used for the review in step 5.
