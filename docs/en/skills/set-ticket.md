<p align="right"><a href="../../skills/set-ticket.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › set-ticket

# set-ticket

When a brief recorded with set-brief is too big to work on in one go, set-ticket splits it into small tickets that can each be verified on their own. Each ticket is written so that a worker who saw neither the conversation nor how the brief was written can finish it by reading that one ticket. The skill publishes the tickets as GitHub sub-issues or docs files and links the ticket list to the original brief.

> This skill is in progress. Install `gongbang-dev` to use it. Its behavior may change.

| Field | Value |
|---|---|
| Bucket | in-progress |
| Invocation | Model-invoked (only when you ask, or a skill such as run-flow tells it to) |
| Command | `/gongbang:set-ticket [brief issue number/URL or docs path]` |
| Source | [SKILL.md](../../../skills/in-progress/set-ticket/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

- The brief's "남은 일" (remaining work) is too big to finish in one new context window.
- set-brief finished publishing and suggested splitting the brief with set-ticket.

It does not run on its own to split general work without a brief or for to-do list requests. Ask for it, as in "split this brief into tickets", or call `/gongbang:set-ticket`.

## Prerequisites

- **A brief made with set-brief**: pass an issue number or URL, or a docs path, as the argument. Without an argument, it looks in this order:
  1. If this conversation ended with set-brief publishing a brief, that brief
  2. Whichever is more recent: the latest issue with the `context` label, or the document with the latest date among documents that have a `- 작성일:` (written date) line. A brief that already has a `## 티켓` (Tickets) section, or whose "남은 일" has no empty checkbox, is already split or finished, so it is skipped.

  docs briefs are found by their `- 작성일:` line across the whole repository, so briefs outside `docs/context/` or in folders matched by `.gitignore` are found too. It proceeds with the brief it found and tells you in one line which brief it chose. If it finds none, it says so and stops.
- **For a GitHub brief**: the `gh` CLI must be logged in. It creates ticket issues and links sub-issues and blocked-by relations with `gh api`.

## How it works

1. **brief 찾기 (Find the brief)**: it reads the whole brief. For a GitHub brief, it also reads the comments with `gh issue view <번호> --comments`.
2. **코드베이스 탐색 (Explore the codebase)**: if this conversation has not looked at the code yet, it checks the current state of the area the brief covers. If the repository has a glossary or ADRs, it uses those terms in ticket titles and descriptions and follows the ADRs. It also looks for prefactoring that makes the implementation easier.
3. **분할안 작성 (Write the split plan)**: it splits the brief's "남은 일" into tickets using the [split criteria](#split-criteria) below. Prefactoring, if any, becomes the first ticket.
4. **분할안 확인 (Review the split plan)**: it shows the split plan as a numbered list. Each ticket has a title, blocked-by relations (numbers of tickets that must finish first, or "없음" (none)), what to build, and done criteria. It then asks whether the unit size is right (too big / too small), whether the blocked-by relations are right, and whether any tickets should be merged or split further. It revises and shows the plan again until you approve.
5. **게시와 brief 연결 (Publish and link to the brief)**: it creates the tickets where the brief lives, in blocked-by order, and appends a `## 티켓` section to the end of the brief. Blocking tickets are created first so that blocked-by relations can use real numbers. On GitHub, before publishing, it checks the sub-issues already linked to the brief and its `## 티켓` section. It does not create a ticket again if one with the same title as in the split plan exists, and only adds the missing links. So running it again after an interrupted publish does not create the same ticket twice.

After publishing, it suggests running the tickets one at a time with run-ticket in a new session. If another skill called it, it does not suggest anything and returns to that skill.

### Split criteria

- **Vertical slice**: a ticket does not cover just one layer. It cuts narrowly through every layer it needs (schema, API, UI, tests). A finished ticket can be demonstrated or verified on its own.
- **Size**: a ticket must be finishable in one new context window. If the session is interrupted or work continues in a new session, the worker starts without the earlier tickets' conversation, reading only that ticket and the completion records of earlier tickets. If you choose parallel execution, each ticket's worker starts the same way.
- **What to build**: written as behavior instead of file paths and code to implement, because implementation paths and code go stale quickly. It does include names that change (fields, types, columns, functions) and the commands to check the done criteria with their expected results. If prototype code captures a decision (state machine, schema, type shape) more precisely than prose, only the part that holds the decision is included, with a note that it came from the prototype.
- **Done criteria**: items in the brief's "확인 기준" (verification criteria) that can be checked once that ticket alone is finished are copied word for word. The rest are run from the brief by run-ticket when it finishes the last ticket.
- **Blocked-by**: the tickets that must finish before this ticket starts. A ticket with no blocking tickets can start right away.
- **Output artifacts**: when one ticket's result (for example, a checklist of behavior before the change, or measurements) is used by another ticket, the producing ticket's "만들 것" (what to build) says "결과를 이 티켓의 산출물로 남긴다" (leave the result as this ticket's output artifact), the consuming ticket's done criteria say "NN 티켓의 산출물" (output artifact of ticket NN), and the consuming ticket is blocked by the producing ticket. Each ticket runs in a new session, so without this the later ticket cannot find the result. Other tickets' results are referred to with this phrase instead of a path. run-ticket stores artifacts in the `## 산출물` (Output artifacts) section of a docs ticket or in the completion comment of a GitHub ticket.
- **Restrictions**: items from the brief's "하면 안 되는 것" (what not to do), "바꾸지 않는 범위" (out of scope), and "바꿀 수 없는 조건" (fixed conditions) that relate to the ticket are copied in the brief's exact wording. If it is unclear whether an item relates, it is copied.
- **Wording**: instead of phrases that need the conversation to interpret, such as "as decided earlier", "like the ticket above", or "cleanly", tickets name the names, values, and ticket numbers directly.

### Splitting a broad refactor

When one mechanical change, such as renaming a column or changing a shared type, spreads across the whole codebase so that no slice can go green (pass CI) on its own, it splits the work in expand–contract order instead of vertical slices.

1. **expand**: add the new form next to the old one so nothing breaks.
2. **migrate**: move call sites in groups by package or directory. Each group is one ticket, and all are blocked by the expand ticket. Because the old form is still there, CI is green for each group.
3. **contract**: once no call sites remain, remove the old form. Blocked by every migrate ticket.

If groups also cannot go green on their own, the order stays the same, the groups share one integration branch, and a final "통합 및 검증" (integrate and verify) ticket is blocked by every group ticket. Green is promised only at that final ticket. In this case, the blocked-by lines of the group tickets and the "통합 및 검증" ticket end with `(통합 브랜치 공유)` (shared integration branch), and the group tickets' done criteria contain only checks that the group can pass on its own. When run-ticket sees this marker, it runs those tickets one after another in a single working tree instead of a worktree per ticket, and does not run the full test suite for group tickets.

## Output

**GitHub issue**

- It creates an issue with the `ready-for-agent` label for each ticket. If the label does not exist, it creates it first.
- It links each ticket issue to the brief as a sub-issue. If linking fails, it puts `Part of #<brief 번호>` (brief number) at the top of the ticket body.
- It links blocked-by relations as issue dependencies (blocked by). If linking fails, it adds a "막힘 관계" (Blocked by) section to the ticket body.
- It appends a `## 티켓` section to the end of the brief body, listing `- [ ] #<번호> <제목>` (number, title) in blocked-by order.
- It lists the ticket URLs.

A ticket body has these sections: 부모 (Parent), 만들 것 (What to build), 완료 기준 (Done criteria), 막힘 관계 (Blocked by, only when native linking failed), 하면 안 되는 것 (What not to do), and 작업 경계 (Work boundaries: out of scope, fixed conditions). Sections with no content are removed. A GitHub ticket is finished when it is closed.

**docs document**

- It creates a folder in the brief's directory, named after the brief file without `.md`, for example `docs/context/YYYY-MM-DD-<brief-slug>/`. Ticket folder names set by repo rules (such as `issues/`) are not used.
- It saves each ticket as one file, `NN-<slug>.md`. NN is numbered from `01` in blocked-by order, and the slug is the title shortened to lowercase English letters and hyphens. If a file with the same name exists, it asks before overwriting.
- It appends a `## 티켓` section to the end of the brief document, listing `- [ ] [NN: <제목>](./YYYY-MM-DD-<brief-slug>/NN-<slug>.md)`.
- It lists the files it saved and changed. It does not commit.

A ticket file has a `# NN: <제목>` (title) heading, then `- 부모:` (parent), `- 막힘 관계:` (blocked by), and `- 상태: ready-for-agent` (status) lines, followed by the 만들 것, 완료 기준, 하면 안 되는 것, and 작업 경계 sections. Sections with no content are removed. When run-ticket finishes a ticket, it changes the status to `done` and appends `## 완료 기록` (Completion record).

**brief**

It does not close the brief, and it does not change the brief except to append the `## 티켓` section. Tickets copy the brief's wording and point to the brief as their parent, so changing the brief would make it disagree with the tickets, and closing it would leave workers unable to find the full context.

## Customize

| What to change | Where to edit |
|---|---|
| Ticket section structure | SKILL.md "이슈 티켓 템플릿" (Issue ticket template), "docs 티켓 템플릿" (docs ticket template) |
| Split criteria (vertical slices, ticket size, how to write "what to build") | SKILL.md "핵심 규칙" (Core rules), "3. 분할안 작성" (3. Write the split plan) |
| Questions asked when showing the split plan | SKILL.md "4. 분할안 확인" (4. Review the split plan) |
| Label name, docs ticket folder and file names | SKILL.md "5. 게시와 brief 연결" (5. Publish and link to the brief) |

If you change section names in the ticket templates, the `- 상태:` (status) line, the `## 티켓` section appended to the brief, or the `(통합 브랜치 공유)` marker on blocked-by lines, you must also change run-ticket. run-ticket uses these names and the marker to find tickets, decide whether they are done, and choose how to run them. run-flow also finds unfinished tickets by the `## 티켓` section and `- 상태: done`.

To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **set-brief**: creates the brief to split. After publishing, it suggests splitting with this skill when "남은 일" is big.
- **run-ticket**: runs the published tickets one at a time. When it finishes the last ticket, it runs the brief's "확인 기준". If you specified a worker tool procedure, or one is registered in the repo or agent rules, it runs several tickets in parallel.
- **run-flow**: calls this skill in stage 4 (티켓 분할, ticket split). After publishing, it asks whether to continue stage 5 (구현과 리뷰, implementation and review) in the same session or in a new one. ADRs left in run-flow stage 2 are read and followed by this skill when it explores the codebase.

---

← Previous: [set-brief](set-brief.md) · [All docs](../README.md) · Next: [run-ticket](run-ticket.md) →
