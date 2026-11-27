<p align="right"><a href="../../skills/write-docs.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › write-docs

# write-docs

Settle the field, audience, purpose, tone, and material of a text first, and get text written with principles that fit the field, in the chat. Use it to write a new draft, refine a draft you bring, or revise an existing document. It does not invent facts, numbers, paths, names, or evidence, and marks values missing from the material as `[확인 필요: 무엇]` ([needs confirmation: what]).

| Field | Value |
|---|---|
| Bucket | productivity |
| Invocation | User-invoked |
| Command | `/gongbang:write-docs [request for the text to write or revise]` |
| Source | [SKILL.md](../../../skills/productivity/write-docs/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

- Write technical documents such as a README, guide, or API docs.
- Write a piece that explains a concept or background, or an opinion piece.
- Refine text you send to people, such as conversation, advice, or stories.
- Write work messages to colleagues, such as work reports, PR descriptions, or Slack messages.
- Revise an existing document, sentences only or including structure.

## Prerequisites

- Material to include (facts, code, documents, links). If the request has none, the skill asks for it separately.
- If you have an original to revise, pass it as an attachment or path. A link such as SharePoint or OneDrive needs a connector or MCP tool that can read it. If the skill cannot read the original or the material, it does not start writing and asks you to paste the file directly or connect a connector.

## How it works

1. **Understand the request**: It looks for the field, audience, purpose, tone, material, and revision scope in the request, the draft you brought, and the file to revise. For a revision, it reads the original to the end. Items that are already clear are not asked but restated in one line, like `확인됨: 독자 - 사내 백엔드 개발자 (요청에 있음)` (confirmed: audience - in-house backend developers (in the request)).
2. **Ask about empty items**: It asks only about items that are empty or open to more than one reading. You can type an answer that is not among the options.
   - Field: technical document / work message / explanation or opinion / conversation, advice, or story
   - Technical document type (when you choose technical document): learning / problem solving / reference / explanation
   - Revision scope (when refining a draft or revising a document): sentences only / including structure

   Items that need a long answer, such as material, are asked separately after the choice questions are answered.
3. **Read the principles**: For every field it reads `reference/clear-writing.md`, and for a technical document it also reads `reference/tech-writing.md`. For a new draft, or when the revision scope is "구조까지" (including structure), it uses the following structure as the skeleton. When the revision scope is "문장만" (sentences only), it keeps the original structure as is.
   - Technical document: the recommended structure of the chosen type
   - Work message: conclusion or status → evidence → remaining work and requests

   When the two sets of principles conflict, technical documents follow `tech-writing.md` and all other fields follow `clear-writing.md`. The principle of not inventing anything comes first in every field.
4. **Write**: It writes only from the material given. When refining a draft or revising a document, it keeps the meaning of the facts and the author's voice, and with "문장만" (sentences only) it does not change section order or headings. If a fact missing from the material would strongly affect the result, it asks. Otherwise it leaves a mark in place, like `[확인 필요: 타임아웃 기본값]` ([needs confirmation: default timeout]), showing what is missing.
5. **Review**: Before delivering, it checks each sentence for whether the reader can tell who does what. A subject that is clear from context may be left out. It first fixes these three patterns.
   - Sentences that hide the actor by turning an action into a noun: "DB 서버 재시작이 이루어졌습니다" ("a DB server restart was performed")
   - Awkward coined word combinations used in place of the usual name: "세션 진입 경계" ("session entry boundary")
   - Sentences whose point is not in the main clause

   Then it finds and fixes the other patterns in "주의할 점" (Cautions) in SKILL.md: the "X가 아니라 Y다" ("not X, but Y") frame that negates an alternative the reader never raised, invented specificity, demonstratives with no referent, missing logical links, metaphors the reader has to decode, a rhythm that breaks every small fact into its own sentence, and compressed noun strings. For a technical document, it also checks:
   - whether there is an overview right below the title
   - whether the same concept uses the same term, without mixing English and Korean terms
   - whether each abbreviation is spelled out the first time it appears
   - whether meta-discourse such as "다음으로" (next) or "앞서 설명했듯이" (as explained above) remains
   - whether translationese such as "~을 통해" (by means of) or "~을 수행합니다" (performs) remains
6. **Deliver**: It shows the result in the chat. Even when revising an existing file, it shows the revision in the chat first and applies it to the file after you approve.
7. **Repeat revisions**: When you say what to change, it repeats steps 4–6. If the field changes, it goes back to step 3 and chooses the principles again.

## Output

- Text shown in the chat. Changes to an existing file are applied after you approve.
- If there are `[확인 필요]` (needs confirmation) marks, it lists them one per line below the result so you can fill them in.

It does not add a note saying it reviewed the text, or a style report.

## Customize

| What to change | File to edit |
|---|---|
| Technical document types and recommended structures, information structure principles, sentence principles (the default is the Toss technical writing guide) | `reference/tech-writing.md` |
| Readable-writing principles applied to every field, work message structure, contrast examples | `reference/clear-writing.md` |
| Patterns to avoid when writing and to look for again in review | "주의할 점" (Cautions) in SKILL.md |
| Fields and question options | "1. 요청 파악" (Understand the request) and "2. 빈 항목 질문" (Ask about empty items) in SKILL.md |
| Technical document review items | "5. 검토" (Review) in SKILL.md |

To use your team's style guide, replace `reference/tech-writing.md` with that guide. For technical documents, this file takes precedence when it conflicts with `clear-writing.md`. The four document types are written separately in the step 2 questions of SKILL.md, and the technical document review items in step 5, so if they do not fit the new guide, edit SKILL.md as well. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

There is no flow that connects to other skills.

---

← Previous: [building-skills](building-skills.md) · [All docs](../README.md) · Next: [set-guidelines](set-guidelines.md) →
