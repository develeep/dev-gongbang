<p align="right"><a href="../../skills/set-brief.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › set-brief

# set-brief

set-brief records what was decided in the conversation as one brief, so you can hand the work to a worker or another agent who did not see the conversation. So that working from the brief alone gives the same result as an agent with the conversation context, the skill writes only confirmed facts and agreed decisions, and has subagents who do not know the conversation read the draft to find sentences that can be read more than one way. The brief is published as a GitHub issue or a `docs/context/` document.

> This skill is in progress. Install `gongbang-dev` to use it. Its behavior may change.

| Field | Value |
|---|---|
| Bucket | in-progress |
| Invocation | Model-invoked (only when you ask, or a skill such as run-flow tells it to) |
| Command | `/gongbang:set-brief [summary of the work to record]` |
| Source | [SKILL.md](../../../skills/in-progress/set-brief/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

- Hand off work that does not finish in one session to the next session or another agent.
- Turn a framing record finalized with framing-problems into a brief.

It does not run on its own for general work requests or requests to summarize the conversation. Ask for it, as in "record this as a brief", or call `/gongbang:set-brief`.

## Prerequisites

- **Content to record**: if there is a framing record finalized with framing-problems, the brief is written from it. Otherwise it collects only facts confirmed and decisions agreed in the conversation.
- **To record it as a GitHub issue**: the `gh` CLI must be logged in. The skill recommends a GitHub issue when `git remote -v` includes github.com and `gh auth status` succeeds, and a docs document otherwise.
- **Subagents**: used for the cold-read check. If it cannot start subagents, it skips the cold-read check and tells you so at the confirmation step.
- **Requirements document (optional)**: if there is a requirements document made with analyzing-requirements, it puts that path and the chosen development scope in the brief and checks that no requirement is missing.

## How it works

1. **입력 수집 (Collect input)**: it collects the framing record and the work done after it (changed files, commits, newly agreed decisions). Without a framing record, it collects only facts confirmed and decisions agreed across the whole conversation. If there is a requirements document, it also collects its path and the chosen development scope.
2. **저장 위치 선택 (Choose where to save)**: you choose a GitHub issue or a docs document. The recommendation is the first choice. A docs document goes in `docs/context/`. If the repo rules set a separate directory for work documents, that directory is also offered.
3. **초안 작성 (Write the draft)**: it writes a draft from the template.
   - The title is the "최종 목적" (final goal) written as one line. If the final goal cannot be written in one line, it treats the work as having several goals and asks before writing whether to split the brief per goal.
   - Sections and lines with no content are removed.
   - If there is a requirements document, it checks that each requirement in the chosen development scope has a matching line in "남은 일" (remaining work) or "확인 기준" (verification criteria). A requirement with no matching line goes in "바꾸지 않는 범위" (out of scope) if that was agreed, and in "미확인·위험" (unconfirmed items and risks) if nothing was agreed.
4. **냉독 검증 (Cold-read check)**: readers who do not know the conversation read only the draft, to find sentences that can be read more than one way.
   - It starts 3 subagents at once in fresh contexts and gives them only the full draft and the repository path, without the conversation. If the agent rules or the caller of this skill name an agent for the cold-read check, it uses that agent.
   - Each subagent assumes it has been given the work in that repository and answers five things: the first task and where to start, what to change and what not to change, what not to do, how to judge that the work is done, and what the document alone cannot settle so it would have to ask or guess.
   - The skill compares the answers with what was agreed in the conversation and with each other, and fixes the sentences that caused answers to differ from the agreement or from each other. Items it cannot fix because nothing was agreed move to "미확인·위험".
   - It checks the fixed draft once more. Items that still differ the second time are not fixed and are shown to you in step 5.
5. **사용자 확인 (Confirm with you)**: it shows the following in one message and asks you to confirm. It does not publish before you say it is correct, and if you ask for changes it shows the updated draft again.
   - The full draft
   - Items fixed in the cold-read check, and the differences that remain
   - The external actions to run. For an issue: the repository to create it in and whether it is public, the labels to add, and whether the `context` label will be created. For docs: the save path.

   For a public repository, it asks you to confirm the draft contains no secrets, internal URLs, or personal data, because a published issue stays in caches and notifications even after it is removed.
6. **게시 (Publish)**: it publishes to the chosen location. See [Output](#output) for what is created. After publishing, it looks at the size of "남은 일" and suggests the next skill. If the work is too big to finish in one new context window, it suggests splitting it with set-ticket. If it fits in one window, it suggests running run-ticket in a new session with the brief path or issue number. If another skill called it, it does not suggest anything and passes the brief path or issue number to that skill.

## Output

**GitHub issue**

- It creates an issue with the `context` label and tells you the issue URL. If the label does not exist, it first creates it with `gh label create context --description "맥락 파악서 겸 작업 지시서"`.
- The `context` label serves as the brief list. The next session finds briefs with `gh issue list --label context`.

**docs document**

- It saves the brief as `YYYY-MM-DD-<slug>.md` in the directory chosen in step 2 (`docs/context/` by default). The slug is the title shortened to lowercase English letters and hyphens. If a file with the same name exists, it asks before overwriting. File names set by repo rules (such as `spec.md`) are not used.
- It adds one line to `README.md` in the same directory: `- [YYYY-MM-DD 제목](./YYYY-MM-DD-<slug>.md): 요약 문장` (title, summary sentence). If there is no `README.md`, it creates one with a `# Context` heading.
- It lists the files it saved. It does not commit.

**Brief structure**

The top of the brief has `- 기준 커밋:` (base commit), `- 작성일: YYYY-MM-DD` (written date), and `- 요구사항 문서:` (requirements document) lines, followed by these sections. If there is a framing record, the cells in the right column move into that section.

| Section | Content | Framing record cells moved in |
|---|---|---|
| 요약 (Summary) | Summary of the issue | - |
| 배경·의도 (Background and intent) | Why it is done, and what triggered it | R1 의도 (intent), R1 계기 (trigger) |
| 최종 목적 (Final goal) | The observable state when it is done | R2 이상 (ideal), R5 목표 (goal) |
| 확인된 사실 (Confirmed facts) | A list of confirmed facts | R2 현재 (current state), R2 문제 (problem), R2 원인 (cause) marked "확인됨" (confirmed), R3 자원 (resources) |
| 합의한 작업 (Agreed work) | Solution, grounds for the solution, rejected solutions and why, work done, and the "남은 일" (remaining work) checklist | R5 해법 (solution), R4 근거 (evidence) marked "맞음" (fits) or "조건부" (conditional), R5 제안 해법 (proposed solution) marked "기각" (rejected), R4 근거 marked "맞지 않음" (does not fit) |
| 작업 경계 (Work boundaries) | What changes, "바꾸지 않는 범위" (out of scope), "바꿀 수 없는 조건" (fixed conditions) | R3 제약 (constraints), as fixed conditions |
| 하면 안 되는 것 (What not to do) | Actions not to take, and why | - |
| 확인 기준 (Verification criteria) | A checklist of commands to run with expected results, and changes a user can observe | - |
| 미확인·위험 (Unconfirmed items and risks) | Hypothesized causes and how to check them, side effects with acceptance or mitigation, obstacles | R2 원인 marked "가설" (hypothesis), R6 부작용 (side effects), R6 장애물 (obstacles) |

R4 evidence whose source is "모델 지식, 미검증" (model knowledge, unverified) goes in "미확인·위험" instead of the solution's grounds. Rejected solutions are recorded so that the worker does not investigate alternatives that were already rejected.

The brief is written by these rules:

- Only confirmed facts and agreed decisions. Guesses, recommendations, and hypotheses go only in "미확인·위험".
- Each fact has a source (commit hash, URL, or "사용자 합의" (user agreement)). Paths are as of the base commit at the top.
- Names, paths, and values are written out instead of expressions that point to the conversation, such as "the one mentioned earlier" or "that file".
- Expressions with no criterion, such as "fast" or "clean", are replaced with the numbers, commands, or paths agreed in the conversation. If no criterion was agreed, the expression moves to "미확인·위험".
- Verification criteria are written as externally observable behavior instead of an implementation approach, so that a worker who implements it differently can be judged by the same criteria.

## Customize

| What to change | Where to edit |
|---|---|
| Brief section structure | SKILL.md "기록 템플릿" (Record template) |
| Brief writing rules (sources, expressions with no criterion) | SKILL.md "핵심 규칙" (Core rules) |
| Recommended save location, docs directory | SKILL.md "2. 저장 위치 선택" (2. Choose where to save) |
| docs file name, index line, issue label | SKILL.md "6. 게시와 인덱스 갱신" (6. Publish and update the index) |
| Cold-read check questions and number of subagents | SKILL.md "4. 냉독 검증" (4. Cold-read check) |

If you change section names, line names such as "남은 일", "바꾸지 않는 범위", and "바꿀 수 없는 조건", or the `- 작성일: YYYY-MM-DD` line, you must also change set-ticket, run-ticket, and run-flow. set-ticket and run-ticket find and read briefs by these names and the `^- 작성일: ` regex, and run-flow also recognizes a brief by its `- 작성일:` line. The same applies if you rename the `context` label: all three skills find GitHub briefs with `gh issue list --label context`.

To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **framing-problems**: if you finalize a framing record first, the brief is written from that record.
- **analyzing-requirements**: if there is a requirements document made with this skill, its path and the chosen development scope go in the brief, and set-brief checks that every requirement has a matching line.
- **set-ticket**: if "남은 일" is too big to finish in one new context window, splits the brief into tickets.
- **run-ticket**: if it fits in one window, runs the brief right away in a new session. A brief with no `## 티켓` (Tickets) section is treated as a single ticket.
- **run-flow**: calls this skill in stage 3 (작업 지시서, brief). In that case the run-flow session does all set-brief steps itself and starts fresh contexts only for the cold-read readers. After publishing, run-flow uses the same size criterion to continue to stage 4 (티켓 분할, ticket split) or stage 5 (구현과 리뷰, implementation and review). If you asked for tickets, it goes to stage 4 regardless of size.

---

← Previous: [run-flow](run-flow.md) · [All docs](../README.md) · Next: [set-ticket](set-ticket.md) →
