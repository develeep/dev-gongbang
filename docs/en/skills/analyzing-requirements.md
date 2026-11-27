<p align="right"><a href="../../skills/analyzing-requirements.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › analyzing-requirements

# analyzing-requirements

Hand over a planning document link or file, and you get a markdown document that organizes the requirements, the development scope per service and development area, and the content of each planning document section. Developers and agents read this document instead of the planning document, so the skill does not fill in anything the planning document does not say, and it asks about ambiguous parts before writing.

> This skill is in progress. Install `gongbang-dev` to use it. Its behavior may change.

| Field | Value |
|---|---|
| Bucket | in-progress |
| Invocation | Model-invoked |
| Command | `/gongbang:analyzing-requirements [planning document link or file path]` |
| Source | [SKILL.md](../../../skills/in-progress/analyzing-requirements/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

- You get a planning document link or file and want the requirements organized or analyzed.
- Before development starts, you want to split what to build by service and development area (web, api, etc.).

If you hand over a planning document and ask something like "organize the requirements" or "summarize this planning document", Claude can choose this skill without you typing its name.

## Prerequisites

- **Planning document**: a PDF, PPT(X), or MD file (attached or as a path), or a link such as SharePoint or OneDrive. If neither the argument nor the request includes a planning document, it asks for a link or path.
- **A tool that can read the link**: for a link, a connector or MCP tool that can read it must be connected. If it cannot read the planning document, it does not start, and it tells you to connect a connector or MCP tool that can read the link.

## How it works

1. **기획서 읽기 (Read the planning document)**: it reads the whole planning document and identifies the section structure and the services and development areas that appear.
2. **모호한 부분 질문 (Ask about ambiguous parts)**: it asks about all ambiguous parts in one message as a numbered list, and each question says what is ambiguous and why. If the service names or development areas cannot be told from the planning document, it asks here. It moves on after you answer.
3. **문서 작성 (Write the document)**: it writes the document from the template in [Output](#output). The document contains only what the planning document says and what you answered. Items with no answer are marked `확인 필요` (needs confirmation) in their place and also collected in the "확인 필요" list at the end.
4. **검증 (Verify)**: it checks that every item in the document has grounds in the planning document or your answers. Items without grounds are removed or changed to `확인 필요`, and the changed document is checked again. Then it goes the other way: for each section of the planning document, it checks that the document has a matching section or `확인 필요` item, and adds any missing section. The first check only looks at the grounds of items that were written, so a section dropped entirely from a large planning document is found by this reverse check.
5. **저장 (Save)**: it asks where to save and saves a markdown file at that path.

## Output

One markdown document, written from this template:

```markdown
# <기획서 제목> 요구사항

## 개발 범위

| 서비스 | 개발 영역 | 내용 |
|---|---|---|
| <서비스명> | <web, api 등> | <이 영역에서 개발할 것> |

## 요구사항

- <요구사항>

## <기획서에 있는 섹션>

<섹션 내용>

## 확인 필요

- <항목>: <무엇이 정해지지 않았는지>
```

- **개발 범위 (Development scope)**: always included. Split by service name and development area (web, api, etc.) in a `서비스 | 개발 영역 | 내용` (Service, Development area, Details) table.
- **요구사항 (Requirements)**: always included.
- **Sections in the planning document**: only sections that are in the planning document, such as as-is, to-be, screen list, feature list, and schedule, in the planning document's order. Sections that are not in the planning document are not created.
- **확인 필요 (Needs confirmation)**: items with no answer, and what is still undecided for each. They are also marked `확인 필요` in their place in the body, so readers can see which parts are undecided.

Slide paths or numbers are not written as sources.

## Customize

| What to change | Where to edit |
|---|---|
| Document template, sections always included | SKILL.md "3. 문서 작성" (3. Write the document) |
| Supported input formats | SKILL.md "입력" (Input) |
| What the document may contain, and how `확인 필요` is marked | SKILL.md "규칙" (Rules) |
| How grounds are checked | SKILL.md "4. 검증" (4. Verify) |

If you rename the `## 개발 범위` or `## 요구사항` sections, also change run-flow. run-flow recognizes an MD file with these two sections as a requirements document and starts from stage 2 (구체화, framing).

It is Model-invoked, so the description sets when it runs. If you change the description, the situations in which Claude chooses this skill also change. To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **run-flow**: when a flow starts from a planning document, run-flow calls this skill in stage 1 (요구사항 정리, requirements) and passes the saved requirements document to stage 2 (구체화, framing). If there are several development scopes, it has you choose one for this flow and frames the chosen scope with framing-problems. run-flow writes the answers this skill collects to `## 요구사항 답변` (requirement answers) in its state file as soon as they arrive, so the answers survive even if the flow is interrupted before the document is saved.
- **set-brief**: writes the requirements document's path and the chosen development scope in the brief, and checks that each requirement in that scope has a matching line in the brief's "남은 일" (remaining work) or "확인 기준" (verification criteria).

---

← Previous: [run-ticket](run-ticket.md) · [All docs](../README.md)
