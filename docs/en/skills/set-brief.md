<p align="right"><a href="../../skills/set-brief.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › set-brief

# set-brief

Records what was decided in the conversation as one brief. The readers of this brief are workers or other agents who did not see the conversation. It is written so that working from the brief alone gives the same result as an agent with the conversation context.

> This skill is in progress. Install `gongbang-dev` to use it. Its behavior may change.

| Field | Value |
|---|---|
| Bucket | in-progress |
| Invocation | User-invoked |
| Command | `/gongbang:set-brief [summary of the work to record]` |
| Source | [SKILL.md](../../../skills/in-progress/set-brief/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

- Hand off work that does not finish in one session to the next session or another agent.
- Turn a framing record finalized with framing-problems into a brief.

## Prerequisites

- To record it as a GitHub issue, `git remote -v` must include github.com and `gh auth status` must succeed. Otherwise it recommends a docs document.
- The cold-read check needs the Agent tool. Without it, that step is skipped and you are told.

## How it works

1. It collects the framing record and the work done after it (changed files, commits, new decisions). If there is no record, it collects only facts confirmed and decisions agreed in the conversation.
2. You choose where to save: a GitHub issue or a `docs/context/` document.
3. It writes a draft from the template. If there are several goals, it asks whether to split the brief before writing.
4. It asks the same questions to 3 subagents that get only the draft, without the conversation. Where their answers differ from what was agreed or from each other, it fixes the sentences. This is called the cold-read check.
5. It shows the draft, the fixed items, and the external actions to run, and asks you to confirm. For a public repository, it asks you to confirm there are no secrets, internal URLs, or personal data.
6. It publishes.

## Output

- **GitHub issue**: created with the `context` label. If the label does not exist, it creates it. The next session lists briefs with `gh issue list --label context`.
- **docs document**: saved as `docs/context/YYYY-MM-DD-<slug>.md`, with one line added to `README.md` in the same directory. It does not commit.

The brief has these sections: 요약 (Summary), 배경·의도 (Background and intent), 최종 목적 (Final goal), 확인된 사실 (Confirmed facts), 합의한 작업 (Agreed work), 작업 경계 (work boundaries), 하면 안 되는 것 (what not to do), 확인 기준 (verification criteria), 미확인·위험 (unconfirmed items and risks). Sections with no content are removed.

## Customize

| What to change | Where to edit |
|---|---|
| Brief section structure | SKILL.md "기록 템플릿" (Record template) |
| docs save path and file name | SKILL.md "2. 저장 위치 선택" (2. Choose where to save), "6. 게시와 인덱스 갱신" (6. Publish and update the index) |
| Cold-read check questions | SKILL.md "4. 냉독 검증" (4. Cold-read check) |

If you change section names, line names such as "남은 일" (remaining work), or the `- 작성일: YYYY-MM-DD` (written date) line, you must also change set-ticket and run-ticket. Both skills find and read briefs by these names and the `^- 작성일: ` regex. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **framing-problems**: if you finalize a framing record first, the brief is written from that record.
- **set-ticket**: if "남은 일" is too big to finish in one new context window, splits it into tickets.
- **run-ticket**: if it fits in one window, runs it right away in a new session.

set-ticket and run-ticket are User-invoked, so set-brief does not call them directly. After publishing, it tells you which one to run.

---

← Previous: [check-guidelines](check-guidelines.md) · [All docs](../README.md) · Next: [set-ticket](set-ticket.md) →
