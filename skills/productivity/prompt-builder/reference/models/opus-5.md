# Claude Opus 5 가이드

출처: https://platform.claude.com/docs/ko/build-with-claude/prompt-engineering/prompting-claude-opus-5
확인일: 2026-10-01 (출처 문서와 대조)
각 스니펫 아래에 공식 문서의 영어 원문을 둔다. B2=영어이면 원문을 바탕으로 쓰고, 그 외 언어이면 한국어 스니펫을 바탕으로 쓴다.

## 목차
- 특성 요약
- 결정 질문
- 프롬프트 반영
- 제거 검토
- 실행 설정 권고
- 검수 항목

## 특성 요약

- 기본 응답이 이전 Opus보다 **길다**. effort는 말하는 양이 아니라 사고량을 조절하므로, 길이는 프롬프트로 조절한다.
- 에이전트 작업 중 내레이션이 많고, 디스크에 쓰는 문서도 길어지는 경향이 있다.
- 지시가 없어도 스스로 검증하고 실수를 고친다. 검증 지시를 넣으면 과잉 검증이 된다.
- 요청하지 않은 단계를 넣어 범위를 넓히는 경향이 있다.
- 서브에이전트에 쉽게 위임한다.
- 이전 진술을 고친 과정을 자주 설명한다.
- 사고는 기본으로 켜져 있고, effort가 `high` 이하일 때만 끌 수 있다. 끄면 도구 호출이 텍스트로 새어 나오거나 내부 태그가 노출될 수 있다.
- 리뷰 프롬프트에 "심각한 것만" 같은 기준이 있으면 문자 그대로 따라 적게 보고한다.
- 1M 토큰 컨텍스트를 지원한다.

## 결정 질문

| ID | 조건 | 질문 | 종류 |
|---|---|---|---|
| M1 | API·단발 | 응답 길이를 간결하게 통제할까요? (간결 지시 추가 / 기본 길이 유지) | API·단발 |
| M2 | 에이전트 | 작업 중 내레이션을 어떻게 할까요? (시작 한 줄 + 중요 발견 시 + 결과 먼저 / 기본) | 에이전트 |
| M3 | 산출물이 파일 문서 | 작성하는 문서 길이를 과제에 맞게 제한할까요? | 에이전트·단발 |
| M4 | 좁은 범위 작업, 또는 G8=금지하고 제안만 | 요청 범위를 넓히지 않도록 범위 제한 지시를 넣을까요? (넣으면 원칙 G의 과잉 엔지니어링 방지 문구는 넣지 않는다) | 에이전트 |
| M5 | G7=허용 + 위임 기준 | 위임 기준을 넣을까요? 하네스에서 수치 상한을 걸 수 있나요? (Claude Code/Agent SDK) | 에이전트 |
| M6 | 사용자 대상 제품 | 사소한 자기 수정 설명을 숨길까요? | API·에이전트 |
| M7 | 사고를 꺼야 함 | 사고를 끄고 써야 하는 이유가 있나요? (없음 → low effort로 켠 상태 권장 / 있음) | API·에이전트 |
| M8 | 코드 리뷰 | 리뷰 뒤에 별도의 필터링 단계가 있나요? | 에이전트 |

## 프롬프트 반영

**P1. 간결성** (M1=추가) 시스템 프롬프트 본문에 넣는다.
```
응답은 핵심에 집중해 짧고 간결하게 쓴다. 면책 문구와 단서는 짧게 하고, 대부분의 분량을 본론에 쓴다. 설명을 요청받으면 깊은 설명을 특별히 요청하지 않는 한 개요 수준으로 답한다.
```
원문:
```text
Keep responses focused, brief, and concise. Keep disclaimers and caveats short, and spend most of the response on the main answer. When asked to explain something, give a high-level summary unless an in-depth explanation is specifically requested.
```
긴 시스템 프롬프트면 끝부분에 짧은 리마인더를 한 번 더 넣는다.
```
<tone_preference>
출력은 적당히 간결하게 유지한다.
</tone_preference>
```
원문:
```text
<tone_preference>
Keep outputs reasonably concise.
</tone_preference>
```

**P2. 내레이션 형태** (M2)
```
첫 도구 호출 전에 무엇을 할지 한 문장으로 말한다. 작업 중에는 중요한 것을 발견했거나 방향을 바꿀 때만 짧게 알린다. 끝나면 결과부터 말한다. 첫 문장은 "무슨 일이 있었나" 또는 "무엇을 찾았나"에 답하고, 세부 내용은 그 뒤에 둔다.
```
원문:
```text
Before your first tool call, say in one sentence what you're about to do. While working, give a brief update only when you find something important or change direction. When you finish, lead with the outcome: your first sentence should answer "what happened" or "what did you find," with supporting detail after it for readers who want it.
```

**P3. 문서 길이** (M3=예)
```
작성하는 문서의 길이는 과제에 필요한 만큼으로 맞춘다. 내용은 빠짐없이 다루되 군더더기 섹션, 중복 요약, 상투적인 문구로 늘리지 않는다.
```
원문:
```text
Match the length of written documents to what the task needs: cover the substance, but do not pad with filler sections, redundant summaries, or boilerplate.
```

**P4. 범위 제한** (M4=예)
```
요청한 것을 의도한 범위로 전달한다. 일상적인 판단은 스스로 내리고, 요청을 다르게 읽으면 결과물이 실질적으로 달라질 때만 확인한다. 요청이 잘못됐거나 더 나은 방법이 있으면 한 문장으로 말하고, 범위를 조용히 좁히거나 넓히거나 바꾸지 말고 요청대로 진행한다. 작업 전체를 끝내되, 요청을 명백히 벗어나는 행동은 하지 않는다.
```
원문:
```text
Deliver what was asked, at the scope intended. Make routine judgment calls yourself, and check in only when different readings of the request would lead to materially different work. If the request seems mistaken or a better approach exists, say so in a sentence and continue with the task as asked rather than quietly narrowing, widening, or transforming it. Finish the whole task, and stop short of actions that are clearly beyond what was asked.
```

**P5. 서브에이전트 위임 기준** (M5=예)
```
정말로 독립적이고 병렬화할 수 있는 큰 작업(예: 여러 파일에 걸친 폭넓은 조사)만 서브에이전트에 위임한다. 도구 호출 몇 번으로 직접 끝낼 수 있는 일은 위임하지 않고, 자기 작업을 검증하는 데도 서브에이전트를 쓰지 않는다. 하나로 충분하면 하나만 쓰고, 생성 수는 적게 유지한다.
```
원문:
```text
Delegate to a subagent only for large tasks that are genuinely independent and parallelizable, such as a wide multi-file investigation. Do not delegate work you can finish yourself in a handful of tool calls, and do not use subagents to verify or double-check your own work. If one subagent can complete the task, use one rather than several, and keep spawn counts low.
```
수치 상한은 `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, SDK의 `max_budget_usd`로 건다(Claude Code 2.1.217 이상). 실행 설정 권고에 기재한다. 커스텀 시스템 프롬프트에서는 위임 지시를 직접 넣어야 한다.

**P6. 자기 수정 설명 제한** (M6=예)
```
이전 진술의 오류가 사용자의 코드, 결론, 결정을 바꿀 때만 바로잡는다. 바로잡을 때는 짧고 분명하게 말하고 작업을 계속한다. 사용자에게 영향이 없는 사소한 실수는 설명 없이 고치고 넘어간다.
```
원문:
```text
Only correct an earlier statement when the error would change the user's code, conclusions, or decisions. State corrections plainly and briefly, then continue the task. For slips that change nothing for the user, make the fix and move on without noting it.
```

**P7. 사고를 끈 상태의 완화** (M7=있음일 때만)
```
도구를 쓸 때는 먼저 한 문장을 말해도 된다. 요청한 것을 표현할 수 있는 도구가 없으면 추측하지 말고 그렇다고 말한다. 응답에 내부용이나 시스템용 XML 태그를 넣지 않는다.
```
원문:
```text
When you use a tool, you may say a brief sentence first. If no tool can express what the user asked for, say so instead of guessing. Do not include internal or system XML tags in your response.
```
사고 태그를 이름으로 지목하는 지시는 오히려 효과가 떨어지므로 쓰지 않는다.

**P8. 코드 리뷰 커버리지** (M8=예)
```
확신이 없거나 심각도가 낮은 것까지 발견한 문제를 모두 보고한다. 이 단계에서는 중요도나 확신도로 거르지 않는다. 걸러내는 일은 이후 검증 단계가 한다. 발견마다 확신도와 예상 심각도를 적는다.
```
원문: 없음 (문서 설명을 바탕으로 작성). B2=영어이면 위 스니펫을 영어로 옮긴다.
M8=아니오면 "중요한" 같은 모호한 말 대신 구체적인 기준을 사용자에게 받아 쓴다.

## 제거 검토

- "최종 검증 단계를 넣어라", "서브에이전트로 검증하라" 같은 검증 지시와 별도 검증 스캐폴딩. 과잉 검증을 유발한다.
- "답을 다시 확인하라", "응답 전에 재검증하라" 같은 재확인 지시
- "생각하지 마라", "추론하지 마라" 규칙. 사고를 껐을 때 태그 유출을 늘린다.
- "심각도 높은 것만 보고하라" 같은 리뷰 기준 (M8 참고)

## 실행 설정 권고

- `output_config.effort`: 기본값 `high`에서 시작한다. 품질이 유지되면 `low`나 `medium`으로 비용과 지연 시간을 줄이고, 어려운 코딩과 에이전트 작업은 `xhigh`로 올린다. 이전 모델의 effort 값을 그대로 쓰지 말고 다시 측정한다.
- `thinking`: 켠 상태를 권장한다. 대부분의 작업에서 `low` effort로 켜 두는 것이 비슷한 비용으로 끄는 것보다 낫다. 꺼야 하면 effort를 `high` 이하로 둔다. `xhigh`나 `max`와 함께 끄면 400 오류가 난다.
- 서브에이전트 상한(Claude Code/SDK): 위 P5의 환경 변수를 쓴다.

## 검수 항목

- [ ] 검증이나 재확인 지시가 남아 있지 않다
- [ ] 길이 통제를 effort가 아니라 프롬프트로 했다 (M1=추가일 때)
- [ ] 사고를 끈 경우 effort가 `high` 이하이고 P7이 들어갔다
