<p align="right"><a href="../../skills/write-docs.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › write-docs

# write-docs

Writes a new draft, refines a draft you bring, or revises an existing document. Before writing, it sets the field, audience, purpose, tone, and material, then writes with principles that fit the field. It does not invent facts, numbers, paths, names, or evidence, and marks missing values as `[확인 필요: 무엇]` ([needs confirmation: what]).

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
- Revise an existing document, sentences only or including structure.

## Prerequisites

- Material to include (facts, code, documents, links)
- If you have an original to revise, pass it as an attachment or path. A SharePoint or OneDrive link needs a connector or MCP tool that can read it. If the skill cannot read it, it does not start writing.

## How it works

1. Finds the field, audience, purpose, tone, material, and revision scope in the request and the original. Items that are already clear are restated in one line.
2. Asks only about items that are empty or open to more than one reading.
   - Field: technical document / explanation / opinion / conversation, advice, story
   - Technical document type: learning / problem solving / reference / explanation
   - Revision scope: sentences only / including structure
   - Items that need a long answer, such as material, are asked separately after the choice questions.
3. Reads the principles for the field. For a technical document, it uses the recommended structure of the chosen type as the skeleton. If the revision scope is "문장만" (sentences only), it keeps the original structure as is.
4. Writes only from the material given.
5. Finds and fixes common patterns: the "X가 아니라 Y다" ("not X, but Y") frame, invented specificity, demonstratives with no referent, compressed noun strings, and so on.
6. Shows the result in the chat. Even when revising an existing file, it applies changes to the file only after approval.
7. When you give feedback, it repeats steps 4–6.

## Output

- Text shown in the chat. Once you approve, it is applied to the file.
- If there are `[확인 필요]` (needs confirmation) marks, it lists them one per line below the result.

## Customize

| What to change | File to edit |
|---|---|
| Technical document types, recommended structure, sentence principles (the default is the Toss technical writing guide) | `reference/tech-writing.md` |
| Readable-writing principles and examples applied to every field | `reference/clear-writing.md` |
| Patterns to avoid when writing and to look for again in review | "주의할 점" (Cautions) in SKILL.md |

To use your team's style guide, replace `reference/tech-writing.md` with that guide. For technical documents, `clear-writing.md` principles that conflict with this file give way to `tech-writing.md`. For how to copy and edit a skill, see the [customization guide](../customization.md).

## Related skills

There is no flow that connects to other skills. Use it on its own.

---

← Previous: [building-skills](building-skills.md) · [All docs](../README.md) · Next: [set-guidelines](set-guidelines.md) →
