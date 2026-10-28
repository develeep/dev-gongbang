<p align="right"><a href="../../skills/prompt-builder.md">한국어</a> · <b>English</b></p>

# prompt-builder

Assembles a prompt only from values gathered in the interview and proposals you approved. Structure and wording follow Claude's official best practices, adjusted with a guide specific to the target model. If you have a draft, it asks only about empty items. If not, it interviews you from scratch.

| Field | Value |
|---|---|
| Bucket | productivity |
| Invocation | User-invoked |
| Command | `/gongbang:prompt-builder [draft path or description of the prompt to build]` |
| Source | [SKILL.md](../../../skills/productivity/prompt-builder/SKILL.md) |

## When to use

- Build an API system prompt for a chatbot or service.
- Build a prompt for an agent that uses tools, or a harness prompt for long autonomous runs.
- Build a one-off task prompt, such as analysis or document writing.
- Write the body of a CLAUDE.md or SKILL.md.
- Revise or review an existing prompt draft.

## Prerequisites

- If you have a draft, pass it as text, a file path, or an attachment.
- Target model guides exist for Opus 5.5, Opus 5, Sonnet 5.5, Sonnet 5, Fable 5.1, and Haiku 4.5. For other models, only the common best practices apply, with no model-specific adjustment.

## How it works

1. Detects the session model and tells you.
2. Asks the basic settings all at once: prompt type, target model, prompt language (Korean / English), and how to proceed.
   - **Quick mode**: Asks only required items, and gets the rest approved at once as a table of defaults.
   - **Detailed interview**: Asks every item, round by round.
3. Reads the target model guide. If the guide's check date is more than 90 days old and WebFetch is available, compares it against the official docs.
4. If you have a draft, shows a table of items extracted from it, and later asks only about items that are ambiguous or missing.
5. Interviews you on the components. Choice items are asked with a selection prompt, and descriptive items such as background, rules, and examples are asked as numbered questions.
6. If the values given would leave the running model to judge something without criteria, proposes draft text and gets it approved, edited, or dropped. Then asks model-specific decision questions.
7. Assembles the prompt, reviews it itself, and delivers the result.

## Output

Appears in the chat in four parts.

1. **Design summary**: target model, guides applied, decisions reflected, content added from proposals
2. **Finished prompt**: a code block you can copy as is and save as a `.md` file
3. **Run setting recommendations**: only for API and agent types. Effort, `max_tokens`, thinking settings, and so on
4. **Next steps**: how to test, impact of skipped items, proposals that were not approved

By default it does not save a file. If the SKILL.md has bundled files or you ask to save, it confirms the path with you and then saves.

## Customize

| What to change | File to edit |
|---|---|
| Model guide content | `reference/models/<model>.md` |
| Support a new model | Add a guide to `reference/models/`, and add a row to the "모델 ID 패턴" (Model ID pattern) table in step 3 of SKILL.md |
| Interview items, quick mode defaults | `reference/interview.md` |
| Principles and review checklist common to all models | `reference/principles.md` |
| Final response structure | `reference/output-format.md` |
| CLAUDE.md and SKILL.md authoring rules | `reference/skill-authoring.md` |

For how to copy and edit a skill, see the [customization guide](../customization.md).

## Related skills

- **framing-problems**: For a one-off prompt, frame the task first with framing-problems and pass the confirmed record as a draft. For an agent prompt or reusable template, if you choose "실행 시 구체화" (frame at run time) in the interview, the finished prompt calls framing-problems every time it runs. That skill must be installed in the runtime environment.
- **building-skills**: After building a SKILL.md draft, pass the output to building-skills to continue with testing and fixes.
