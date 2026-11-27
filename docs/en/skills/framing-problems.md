<p align="right"><a href="../../skills/framing-problems.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › framing-problems

# framing-problems

Before work starts, framing-problems records why you want the change, what causes the problem, and what cannot change in a "구체화 기록" (framing record), and finalizes it with you. The skill investigates facts it can learn from code, docs, logs, and git history and shows them with sources. It asks you about intent and choices. Once the record is final, the work continues according to the record's goal and solution.

| Field | Value |
|---|---|
| Bucket | productivity |
| Invocation | Model-invoked (only when you ask, or a prompt or skill tells it to) |
| Command | `/gongbang:framing-problems [request to frame]` |
| Source | [SKILL.md](../../../skills/productivity/framing-problems/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

- The request is vague, and working on it right away would likely produce a solution you do not want.
- A request like "fix this here" names only a solution, and you want to check first whether that solution fixes the real cause.
- A prompt made with prompt-builder, or another skill such as run-flow, tells it to frame the work first.

It does not run on its own for general work requests. Ask for it directly, as in "frame this first", or call `/gongbang:framing-problems`.

## Prerequisites

Nothing is required. It uses these tools when they are available:

- **Web search tool**: used to fill R4 External evidence. Without one, it says so and writes the source as "모델 지식, 미검증" (model knowledge, unverified).
- **Question tool that shows choices**: when every question in a message is multiple choice, it asks them in a choice dialog. Without one, it asks with a numbered list.

## How it works

1. It shows an R1 to R6 checklist. It updates the checklist each time all cells of a step are finalized.
2. The skill investigates facts that code, docs, logs, git history, or the conversation can answer, and shows them with sources (file path, document name, URL). Even investigations that scan many files are not handed to another agent; it reads the originals itself. Anything learned without a source is written as "가설" (hypothesis).
3. It asks you about intent, success criteria, and choices. Each message asks every question that can be asked now, meaning every question whose answer depends only on cells already finalized. Usually the first message asks R1, R2, and R3 together, and the R5 solution is asked after the R2 cause, R3 constraints, and R4 verdict (when R4 is filled) are finalized.
4. A cell is finalized only when you say it is correct. Investigated facts are also finalized only after you confirm them, and the prompt or skill that called this skill cannot finalize cells on your behalf.
5. When every cell of R1 to R6 is settled, it shows the whole record once and asks you to finalize it.

### Fields to fill

There is no fixed order. Cells are filled as soon as their questions can be asked.

| Field | What it covers |
|---|---|
| R1 Intent and background | Why you want to do it, what triggered it (a specific event or a recurring situation), and who is affected. If the request names only a solution, it asks what you hope that solution will change |
| R2 Ideal, current state, cause | The ideal, written as an observable criterion, and the current state, checked in code, output, or logs, are written separately. The problem is written as "the ideal is X but currently it is Y", and the cause is marked "확인됨" (confirmed) or "가설" (hypothesis) |
| R3 Constraints and resources | Conditions that cannot change (technology, schedule, organization, compatibility), and existing code, tools, and docs to reuse as is |
| R4 External evidence | Filled for areas with costly-to-get-wrong standards such as security, payments, personal data, and regulation, when R3 has no existing approach to follow, or when you ask. For each known solution and standard, it records whether it fits your situation (fits / conditional / does not fit), the cells that support that judgment, and the source URL. Otherwise it writes one line: "R4 해당 없음: 이유" (R4 not applicable: reason) |
| R5 Goal and solution | Sets the cause to change (goal) and how to change it (solution) separately. Compares 2 to 3 candidates among the proposed solution, a solution using R3 resources, and a solution from R4 |
| R6 Side effects and obstacles | New costs and risks the solution creates (call sites it touches, settings, people who use the result) and what blocks execution (permissions, dependencies, schedule). For each side effect it decides to accept it, mitigate it, or change the solution |

- If the request contains a solution, it records that solution as the "R5 제안 해법" (R5 proposed solution) and first agrees on the problem that solution is meant to solve. If the investigated cause supports the proposed solution, it recommends it as a strong candidate from the first message. If not, it shows why.
- If the cause chosen as the R5 goal is a "가설" (hypothesis), it adds a way to check it (reproduce, measure, logs) to the R6 obstacles. If the hypothesis turns out wrong, it goes back to R2.
- If a side effect cannot be accepted, it goes back to R5.

### How to answer questions

A question message comes in this order: progress line, summary and questions, confirmation request.

- **Progress line**: the first line shows the steps covered and the number of questions, for example `**R2·R3 · 질문 2개 · 답이 필요합니다**` (R2·R3 · 2 questions · answer needed). You can tell from the notification alone whether an answer is needed.
- **Recommendation**: each question comes with a ➡️ recommendation and its reasoning. If the reasoning does not come from an investigated fact or a finalized cell and is something only you know (intent, trigger, operating procedures, and so on), the recommendation starts with "추정:" (guess:). Answering "네" (yes) to a question accepts its recommendation.
- **Confirmation request**: the last line asks you to confirm. Answering "맞다" (correct) accepts the summary and all recommendations. To answer differently, give the question number and choice, as in "Q1 b".

If you answer differently from the recommendation or add new information, the next message starts with the updated summary and asks you to confirm it along with the next questions. When every question is multiple choice, it uses the question tool, puts the recommendation as the first choice, and ends its label with "(추천)" (recommended). With more than 4 questions, it asks in text.

### Asking fewer questions or stopping

- **Compressed mode**: if you ask for fewer questions, or the calling prompt or skill says so, it shows the whole framing record filled by investigation and the questions for all steps in one message. The progress line is `**R1~R6 한 번에 · 질문 <개수>개 · 답이 필요합니다**` (R1 to R6 at once · N questions · answer needed). Cells not yet finalized are marked "확인 필요" (needs confirmation), and one answer can finalize several steps. R6 side effects and obstacles and causes marked "가설" remain as questions.
- **Stopping**: if you say "그냥 해줘" (just do it) or "그만 묻고 진행해" (stop asking and go ahead), it stops asking and shows the record so far. Unfilled cells are left as "미확인" (unconfirmed). If the R5 solution is unconfirmed, it follows the proposed solution and says so. It notes, one line each, the risks that "가설" causes and unconfirmed R6 cells may bring.

### Correcting finalized content

If you correct something already finalized, for example "그게 아니고" (that's not it), it updates the record in this order. This also applies after the record was finalized and the work has moved on.

1. It finds which step the correction is a premise of, and finalizes that step again.
2. It reviews the later steps in order. Decisions whose "근거" (Basis) column includes a changed cell are judged again, and the rest are checked to see whether their conclusions still hold. Solutions already chosen are also judged again.
3. It shows the result one line each, as in `R3 유지: 제약이 의도와 무관함` (R3 kept: the constraint is unrelated to the intent) or `R5 변경: 캐시 추가 → 타임아웃 재시도` (R5 changed: add cache → retry on timeout).

If the correction is only about wording (a term or a sentence), it fixes just that cell.

## Output

**Framing record**: shown in the conversation as a `항목 | 내용 | 출처 | 근거` (Field, Content, Source, Basis) table.

| Column | Content |
|---|---|
| 항목 (Field) | R1 의도 (intent), R1 계기 (trigger), R2 이상 (ideal), R2 현재 (current state), R2 문제 (problem), R2 원인 (cause), R3 제약 (constraints), R3 자원 (resources), R4 근거 (evidence), R5 제안 해법 (proposed solution, 채택 / 기각: adopted / rejected), R5 목표 (goal), R5 해법 (solution), R6 부작용 (side effects), R6 장애물 (obstacles). Multiple values go in separate rows |
| 내용 (Content) | The finalized value |
| 출처 (Source) | "사용자" (user), the file, document, or URL checked, or "미확인" (unconfirmed) |
| 근거 (Basis) | Other cells this cell's decision depends on. Used to find which cells to review when finalized content is corrected |

After the record is finalized, what happens next depends on who called the skill.

- **When you called it directly**: it asks whether to carry out the R5 solution and does not act before you answer.
- **When a prompt or another skill called it**: it continues the work that prompt or skill asked for, following the finalized R5 goal and solution.

## Customize

| What to change | Where to edit |
|---|---|
| Fields to fill (R1 to R6) and the criteria for each | SKILL.md "항목" (Fields) |
| Question message format, compressed mode, stop conditions | SKILL.md "질문 방식" (How to ask) |
| Order for correcting finalized content | SKILL.md "되돌아가기" (Going back) |
| Fields and columns of the record table | SKILL.md "구체화 기록" (Framing record) |
| What to do after the record is finalized | SKILL.md "마무리" (Wrap-up) |

If you rename the record's fields (R1 의도, R5 해법, and so on), also change set-brief's "기록 템플릿" (Record template). set-brief uses these names to move framing record cells into brief sections.

It is Model-invoked, so the description sets when it runs. If you change the description, the situations in which Claude chooses this skill also change. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **prompt-builder**: hand it the finalized framing record as a draft, and it builds a prompt from that content. When you build an agent prompt that runs in conversation with a person, or a reusable template, choosing "실행 시 구체화" (frame at runtime) in the interview makes the finished prompt call this skill before work each time it runs. framing-problems must also be installed where the prompt runs.
- **set-brief**: records the finalized framing record as a brief that another session or worker can pick up.
- **run-flow**: calls this skill in stage 2 (구체화, framing). Each time you finalize a cell, run-flow writes it to `## 구체화 기록` in its state file, so answers you already gave are not asked again if the flow is interrupted.

---

← Previous: [write-docs](write-docs.md) · [All docs](../README.md) · Next: [check-guidelines](check-guidelines.md) →
