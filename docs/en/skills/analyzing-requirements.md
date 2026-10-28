<p align="right"><a href="../../skills/analyzing-requirements.md">한국어</a> · <b>English</b></p>

# analyzing-requirements

Reads a planning document and organizes the requirements, the development scope per service and development area, and the content of each planning document section into a markdown document. Developers and agents read this document instead of the planning document. So it does not fill in anything the planning document does not say, and it asks about ambiguous parts first.

> This skill is in progress. Install `gongbang-dev` to use it. Its behavior may change.

| Field | Value |
|---|---|
| Bucket | in-progress |
| Invocation | Model-invoked |
| Command | `/gongbang:analyzing-requirements [planning document link or file path]` |
| Source | [SKILL.md](../../../skills/in-progress/analyzing-requirements/SKILL.md) |

## When to use

- You get a planning document link or file and want the requirements organized or analyzed.
- Before development starts, you want to split what to build by service and development area (web, api, etc.).

If you hand over a planning document and ask something like "organize the requirements in this planning document", Claude can choose this skill without you typing its name.

## Prerequisites

- A planning document: a PDF, PPT(X), or MD file, or a link such as SharePoint or OneDrive
- For a link, a connector or MCP tool that can read it must be connected. If it cannot read the planning document, it does not start.

## How it works

1. It reads the whole planning document and identifies the section structure, services, and development areas.
2. It asks about all ambiguous parts at once, as a numbered list. Each question says what is ambiguous and why.
3. It writes the document from the template.
4. It checks that every item has grounds in the planning document or your answers. Items without grounds are removed or changed to `확인 필요` (needs confirmation).
5. It asks where to save and saves a markdown file.

## Output

One markdown document.

- **Development scope**: a `서비스 | 개발 영역 | 내용` (Service, Development area, Details) table. Always included.
- **Requirements**: always included.
- **Sections in the planning document**: as-is, to-be, screen list, feature list, schedule, and so on. Only sections that are in the planning document, in the planning document's order.
- **확인 필요** (needs confirmation): items with no answer. They are also marked `확인 필요` in their place in the body.

## Customize

| What to change | Where to edit |
|---|---|
| Document template, sections always included | SKILL.md "3. 문서 작성" (3. Write the document) |
| Supported input formats | SKILL.md "입력" (Input) |

To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

It does not connect to other skills. Use it on its own.
