<p align="right"><a href="../../skills/prompt-builder.md">한국어</a> · <b>English</b></p>

[README](../../../README.en.md) › [Docs](../README.md) › prompt-builder

# prompt-builder

Work out the prompt you need through an interview and get a finished prompt, tuned to the target model, in the chat. The prompt's content comes only from values gathered in the interview and proposals you approved. Structure and wording follow Claude's and OpenAI's official best practices, adjusted with a guide specific to the target model when one exists. If you have a draft, it asks only about items that are empty or ambiguous in the draft.

| Field | Value |
|---|---|
| Bucket | productivity |
| Invocation | User-invoked |
| Command | `/gongbang:prompt-builder [draft path or description of the prompt to build]` |
| Source | [SKILL.md](../../../skills/productivity/prompt-builder/SKILL.md) |

**Contents**: [When to use](#when-to-use) · [Prerequisites](#prerequisites) · [How it works](#how-it-works) · [Output](#output) · [Customize](#customize) · [Related skills](#related-skills)

## When to use

- Build an API system prompt for a chatbot or service.
- Build a prompt for an agent that uses tools, or a harness prompt for long autonomous runs.
- Build a one-off task prompt, such as analysis or document writing.
- Write the body of a CLAUDE.md or SKILL.md.
- Revise or review an existing prompt draft.

## Prerequisites

- If you have a draft, pass it as text, a file path, or an attachment.
- Decide on the target model. The models below have dedicated guides, which live in the skill folder's `reference/models/`.

  | Target model | Guide file |
  |---|---|
  | Claude Opus 5.5 | `opus-5-5.md` |
  | Claude Opus 5 | `opus-5.md` |
  | Claude Sonnet 5.5 | `sonnet-5-5.md` |
  | Claude Sonnet 5 | `sonnet-5.md` |
  | Claude Fable 5.2, Mythos 5.2 | `fable-5-2.md` |
  | Claude Fable 5.1, Mythos 5.1 | `fable-5-1.md` |
  | Claude Haiku 5.5 | `haiku-5-5.md` |
  | Claude Haiku 4.5 | `haiku-4-5.md` |
  | GPT-6.2 Astra, GPT-6.2 Sol | `gpt-6-2.md` |
  | GPT-6 Astra | `gpt-6-astra.md` |
  | GPT-6.1 Sol | `gpt-6-1-sol.md`. The GPT-6 Astra guide is read as well |

  For models not in the table, only the common best practices apply, with no model-specific adjustment. For a GPT model not in the table, Claude-only items (prefill, thinking settings) are not applied either, and the run setting recommendations list only the model ID.

## How it works

1. **Detect the session model**: It checks this session's model ID and states it in one line in its first response. Whether it is Claude or GPT, the detected model becomes the first choice in the target model question. If it cannot detect one, it says `세션 모델: 확인 불가` (session model: unknown) and asks for the target model without a session model choice.
2. **Basic settings**: It asks these four in one round. Items already clear from the request or draft are restated, not asked.
   - **Type**: API system prompt / agent or harness prompt / one-off task prompt / CLAUDE.md or SKILL.md body. For a CLAUDE.md or SKILL.md body, it asks for the models it will be used with instead of the target model, and you can pick several.
   - **Target model**: the model that will actually run the prompt
   - **Prompt language**: Korean / English. Type in any other language.
   - **How to proceed**: Quick mode asks only required items and gets the rest approved at once as a table of defaults. Detailed interview asks every item, round by round.

   If the session model differs from the target model, it tells you that results from trying the prompt in this session may differ from how the target model behaves.
3. **Read the model guide and check its date**: It reads the target model's guide and states in one line which guide it applies. If the check date at the top of the guide is 90 days old or more and it can fetch web pages, it compares the guide with the source docs on the default effort, thinking settings (for GPT, the supported reasoning effort values), beta headers, and conditions for 400 errors. Where they differ, it follows the source and tells you the difference.
4. **Analyze the draft** (if you have one): It shows the values extracted from the draft as a `항목 | 초안에서 추출한 값 | 상태` (Item | Value extracted from the draft | Status) table and asks you to confirm. In the interview that follows, it asks only about items whose status is ambiguous or missing. If the draft contains wording on the model guide's "제거 검토" (review for removal) list, it shows those as a list and asks about removing each one.
5. **Interview on components**: It asks in the round order for the prompt type. Choice items are asked with a question tool that shows options, or as a numbered list if there is none. Descriptive items such as background, rules, and examples are gathered into one message of numbered questions. After each round, it briefly restates your answers and moves to the next round.
6. **Proposals and model-specific decision questions**: If the values given would leave the running model to judge something without criteria (what to report and what to leave out, classification boundaries and confidence thresholds, what to do when it does not know), it proposes draft text and you approve, edit, or drop it. Facts specific to your organization or product, such as menu paths, policies, prices, and contacts, are asked for, not proposed. Then it asks only the model guide's decision questions that apply to your answers so far.
7. **Assemble and self-review**: It places the values into the assembly skeleton (for GPT, the model guide's skeleton) and reviews the result against the common review checklist and the model guide's review items. Items that fail for lack of information are resolved with questions. Items that still fail because you chose "생략" (skip) are left as warnings in the "Next steps" part of the result.
8. **Deliver**: It delivers in the structure described under Output.

## Output

The result appears in the chat in four parts. To keep the finished prompt easy to copy, no other explanatory paragraphs go between the parts.

1. **Design summary**: the target model and guide applied (the guide's check date, and whether it was compared with the source in this session), type, language, and how you proceeded, decisions reflected, content added from proposals, and best practices applied
2. **Finished prompt**: a code block you can copy as is and save as a `.md` file. If there are several messages, such as a system prompt and a user template, each gets its own block.
3. **Run setting recommendations**: only for API and agent types. For Claude, effort, `max_tokens`, thinking settings, and so on. For GPT, reasoning effort, verbosity, `max_output_tokens`, and so on.
4. **Next steps**: how to test, skipped or defaulted items that may affect quality, format choices it made on its own while assembling, and proposals you did not approve (with the exact sentences and where they would go)

Warnings such as a model mismatch, skipped or defaulted items that may affect quality, unapproved proposals, and failed review items stay in even when the response is shortened.

By default it does not save a file. If the SKILL.md has bundled files, it shows each file in its own block and asks whether to save and where (user skill folder / project skill folder / do not save). If you ask it to save, it confirms the path with you and then saves. If a file with the same name exists, it asks before overwriting.

## Customize

| What to change | File to edit |
|---|---|
| Model guide content | `reference/models/<model>.md` |
| Support a new model | Add a guide to `reference/models/`, and add a row to the "모델 ID 패턴" (Model ID pattern) table in step 3 of SKILL.md. To include it in the target model choices, also edit the B1 row of `reference/interview.md` |
| Interview items, quick mode defaults | `reference/interview.md` |
| Principles common to all models, assembly skeleton, review checklist (Claude-only items are marked "(Claude 대상)" (Claude only)) | `reference/principles.md` |
| Final response structure, conditions for saving files | `reference/output-format.md` |
| CLAUDE.md and SKILL.md authoring rules | `reference/skill-authoring.md` |

To copy and modify the skill, see the [customization guide](../customization.md).

## Related skills

- **framing-problems**: For a one-off prompt, frame the task first with framing-problems and pass the confirmed record as a draft. For an agent prompt run in conversation with a person, or a reusable template, choose "실행 시 구체화" (frame at run time) in the interview, and the finished prompt calls framing-problems before the task every time it runs. That skill must be installed in the runtime environment.
- **building-skills**: After building a SKILL.md draft, pass the output to building-skills to continue with testing and fixes.

---

[All docs](../README.md) · Next: [set-guidelines](set-guidelines.md) →
