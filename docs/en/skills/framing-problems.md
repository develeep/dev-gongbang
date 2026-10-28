<p align="right"><a href="../../skills/framing-problems.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › framing-problems

# framing-problems

Does not run a request right away. It gathers the grounds for choosing a solution into a "구체화 기록" (framing record) and finalizes it with the user. It investigates facts through code, docs, and logs, and asks the user about intent and choices. Once the record is final, it continues the work according to the record.

| Field | Value |
|---|---|
| Bucket | productivity |
| Invocation | Model-invoked (only on explicit request) |
| Command | `/gongbang:framing-problems [request to frame]` |
| Source | [SKILL.md](../../../skills/productivity/framing-problems/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

- The request is vague, and working on it right away would likely produce the wrong solution.
- A request like "fix this here" names only a solution, and you want to check whether that solution fixes the real cause.
- A prompt made with prompt-builder or another skill instructs framing before work.

It does not run on its own for general work requests. Ask for it explicitly, as in "frame this first", or call it by name.

## Prerequisites

- With a web search tool, it fills R4 External evidence with sources. Without one, it writes the source as "모델 지식, 미검증" (model knowledge, unverified).
- With the Agent tool, it runs broad investigations in the background.

## How it works

It repeats questions and investigation until all six fields (R1 to R6) are filled. There is no fixed order. It asks the questions that can be answered first.

| Field | What it covers |
|---|---|
| R1 Intent and background | Why you want to do it, what triggered it, who is affected |
| R2 Ideal, current state, cause | Write the observable ideal and current state separately, and mark the cause as "확인됨" (confirmed) or "가설" (hypothesis) |
| R3 Constraints and resources | Conditions that cannot change, and existing code, tools, and docs to reuse as is |
| R4 External evidence | Only for areas with standards, such as security, payments, and personal data, or when requested. Otherwise "해당 없음" (not applicable) with a reason |
| R5 Goal and solution | The cause to change and how to change it. Compares 2 to 3 candidates |
| R6 Side effects and obstacles | Costs and risks the solution creates, and what blocks execution |

Each question comes with a ➡️ recommendation and its reasoning. Answering "맞다" (correct) accepts the summary and all recommendations. To answer differently, reply by number, as in "Q1 b".

- **Compressed mode**: say "fewer questions", and it asks the questions for all steps in one message.
- **Stopping**: say "just do it", and it stops asking and shows the record so far. Unfilled cells are left as "미확인" (unconfirmed), and it notes, one line each, the risks that may result.
- **Going back**: if you correct something already finalized, it finalizes that step again and re-evaluates the decisions in later steps.

## Output

- A framing record as a `항목 | 내용 | 출처 | 근거` (Field, Content, Source, Basis) table
- If you called it directly, it asks whether to carry out the R5 solution and does not act before you answer. If a prompt or another skill called it, it continues that work with the finalized goal and solution.

## Customize

| What to change | Where to edit |
|---|---|
| Fields to fill (R1 to R6) and the criteria for each | SKILL.md "항목" (Fields) |
| Question message format, compressed mode, stop conditions | SKILL.md "질문 방식" (How to ask) |
| Columns of the record table | SKILL.md "구체화 기록" (Framing record) |

It is Model-invoked, so the description sets when it runs. If you change the description, the situations in which Claude chooses this skill also change. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **prompt-builder**: takes the finalized framing record as a draft and builds a prompt. If you choose "실행 시 구체화" (frame at runtime) in the prompt-builder interview, the finished prompt calls this skill every time it runs.
- **set-brief**: turns the finalized framing record into a brief that another session or worker can pick up.

---

← Previous: [set-guidelines](set-guidelines.md) · [All docs](../README.md) · Next: [check-guidelines](check-guidelines.md) →
