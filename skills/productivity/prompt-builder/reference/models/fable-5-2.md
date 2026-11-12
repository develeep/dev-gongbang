# Claude Fable 5.2 / Mythos 5.2 가이드

출처: https://platform.claude.com/docs/ko/build-with-claude/prompt-engineering/prompting-claude-fable-5-2
사고 설정 출처: https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting
확인일: 2026-11-12 (출처 문서와 대조)
각 스니펫 아래에 공식 문서의 영어 원문을 둔다. B2=영어이면 원문을 바탕으로 쓰고, 그 외 언어이면 한국어 스니펫을 바탕으로 쓴다. 이 가이드의 지시는 새 대화에만 적용한다. 대화 도중 system을 바꾸면 사고 블록을 돌려보낼 때 400 오류가 난다.

## 목차
- 특성 요약
- 결정 질문
- 프롬프트 반영
- 제거 검토
- 실행 설정 권고
- 검수 항목

## 특성 요약

- 사고가 항상 켜져 있다. `thinking: enabled`와 `disabled`는 모두 400 오류다. **기본 effort는 `high`**다.
- effort 단계의 순서는 다른 모델과 같지만 단계별 사고량이 다르다. 코딩 평가에서 `low`가 Fable 5.1의 높은 effort에 가깝다. 이득의 대부분은 `medium`→`high`에서 나오고, `high` 위의 이득은 고르지 않다. effort는 답변 길이를 거의 바꾸지 않는다.
- `high` 이상에서는 인사말을 포함해 거의 모든 답변 전에 사고한다. `medium` 이상에서는 "바로 답하라"는 지시로 사고를 막을 수 없다(Fable 5.1은 대체로 따랐다).
- `low`와 `medium`에서 남은 일을 나열하거나, 계속할지 묻거나, 오류·타임아웃 같은 흔한 장애물에서 멈추며 턴을 끝낼 때가 있다.
- 시스템 프롬프트의 승인 규칙을 넓게 해석한다. "이 대화 밖 사람에게 메시지 보내기"를 승인 대상으로 두자 일상적인 동료 요청의 절반가량을 보류했다.
- 코드 소유를 밝히지 않거나 남의 코드로 소개하면, 중복이 생겨도 기존 구조에 덧붙인다. 소유자라고 알리면 중복 통합이 10% 미만에서 약 75%로 늘지만, 출력 토큰이 70~80% 늘고 요청하지 않은 변경(주로 테스트, 문서)이 생기며 기존 동작이 바뀌기도 한다. "No drive-by refactors" 규칙을 앞에 두어도 절반 이상에서 통합했다. PR 요약에서 작은 변경을 자주 빠뜨린다.
- 긴 도구 호출 중에 텍스트를 적게 쓰고, 첫 도구 호출 전에 무엇을 할지 말하지 않을 수 있다. 도구 사이의 업데이트는 사고 블록으로 오고, 기본 `thinking.display`에서는 비어 있다.
- 짧은 작업에서는 서브에이전트를 거의 쓰지 않지만, 위임을 권하는 프롬프트에서는 쉽게 위임한다. `xhigh`와 `max`에서는 자기 작업 리뷰에도 서브에이전트를 쓴다.
- 쌓인 메모리, 노트, 지시 파일 때문에 필요 없는 승인을 구할 수 있다(주로 멀티에이전트). "never"를 예외 없는 절대 규칙으로 받아들인다.
- 글은 Fable 5.1보다 낫고 명료함은 Opus 5.5와 비슷하다. 문체 규칙을 엄격히 따라서, "문장당 20단어 이하" 같은 하드 제한은 글을 끊기게 만든다.
- 안전 분류기 대상: 사이버, 생물학, frontier_llm, 추론 추출(`reasoning_extraction`), general_harms. 무해한 사이버·생명과학 작업도 걸릴 수 있다. 거부되면 `stop_reason: "refusal"`이 반환된다. Mythos 5.2는 같은 능력을 검증된 조직에만 제공한다.
- 대화 기록은 추가만 해야 한다(append-only). system, tools, 이전 메시지를 바꾸면 이후 사고 블록이 무효가 되고 기본적으로 400 오류가 난다.

## 결정 질문

| ID | 조건 | 질문 | 종류 |
|---|---|---|---|
| M1 | 에이전트 | 오류, 타임아웃, 빈 결과 같은 흔한 장애물에서 멈추지 않고 끝까지 진행하게 할까요? (effort `low`·`medium`이면 특히 권장) | 에이전트 |
| M2 | G4 답이 있음 | 승인 목록의 각 항목을 구체적인 행동으로 좁혀 주세요. 승인 없이 해도 되는 일상 단계가 있으면 알려 주세요. | 에이전트 |
| M3 | G11=코딩 + G8≠금지하고 제안만 | 모델을 이 코드베이스의 소유자로 두고 구조 개선(중복 통합 등)까지 맡길까요? (소유자로 둠 / 최소 변경) | 에이전트 |
| M4 | 에이전트 + G6≠최소화 | 하네스가 도구 결과 뒤에 턴 범위 시스템 메시지를 붙일 수 있나요? | 에이전트 |
| M5 | 최종 보고·인계 문서를 사람이 읽음 | 최종 보고를 맥락이 없는 독자도 바로 이해하게 쓰게 할까요? | 에이전트·단발 |

## 프롬프트 반영

**P1. 작업 끝까지 하기** (M1=예) 시스템 프롬프트에 넣는다. 이 문구를 넣으면 모델이 덜 묻기 때문에, 위험하거나 되돌릴 수 없는 행동의 확인 절차는 하네스에 따로 둔다고 알린다. 미완료로 끝나는 세션이 절반가량 줄고 출력 토큰이 약 30% 는다.
```
# 작업 마무리
사용자가 요청한 일이 남아 있는 동안 멈추지 않는다. 끈기 있게 계속하고 꼭 필요할 때만 멈춘다.

상태 메모와 미결 사항에 대한 확인은 환영하지만, 사용자 답에 달려 있지 않은 작업은 불필요하게 멈추지 않고 계속한다.

사용자에게 방향을 바꿔 달라고 청하거나 기다리겠다고 제안하고 있다면, 그 대신 작업의 다음 부분을 진행한다. 오류, 타임아웃, 잠긴 파일, 빈 결과, 실패하는 도구 같은 흔한 장애물을 만날 수 있다. 먼저 원인을 진단하고, 실제로 막힌 것이 아니면 가진 권한으로 넘어간다(기다렸다 재시도, 요청 수정, 다른 도구나 출처 사용).

누군가 분명히 막아 둔 것(손대지 말라고 표시된 파일, 의도적으로 주지 않은 권한, 안전 장치)은 건드리지 않는다. 발견한 것을 그대로 말하고, 작업을 끝낼 다른 안전한 방법을 찾는다. 작업을 끝내기 전에 멈추는 것은 드물게만 정당하다. 사용자 입력 없이 진행할 수 없거나, 막힌 것이 의도적이라 넘으면 안 되는 경우다. 위험하거나 파괴적인 행동에 대한 확인 요구는 이 지시보다 우선한다.
```
원문:
```text
# Finishing work
Please avoid stopping while you still owe work the user asked for. Be persistent and do not stop unless needed.

While status notes are welcome, as is clarifying with the user on open decisions, carry on with work that does not depend on the user's answer without unnecessary stops.

If you notice yourself inviting the user to redirect you or offering to wait, instead proceed on the next part of the task. You may meet ordinary obstacles like errors, timeouts, locked files, empty results or failing tools. Diagnose them first, and when they are not real blockers, work through them with the access you have (wait and retry, fix the request, use another tool or source) rather than stopping unnecessarily.

If someone clearly decided something is a hard blocker, such as a file marked not to be touched, access that was intentionally withheld, or a safety guardrail, leave it alone, say plainly what you found, and look for another safe way to finish the task. Stopping before the task is complete is very rarely merited, as in when the task can't move forward without user input, or where the blocker is deliberate and should not be worked past. This does not override the need for confirmation on risky or destructive actions.
```

**P2. 승인 범위** (M2) 스니펫 없이 원칙 G "가역성과 안전"의 목록을 다음 기준으로 다듬는다. 원문: 없음 (문서 설명을 바탕으로 작성).
- 넓은 범주("외부로 메시지 보내기")는 구체적인 행동("고객에게 이메일 발송")으로 바꾼다.
- "never ~" 규칙은 범위가 있는 규칙으로 바꾼다. 예: "파일을 절대 지우지 않는다" → "파일을 지우기 전에 승인받는다".
- M2에서 받은 승인 불필요 단계는 목록으로 명시한다. "더 자유롭게 행동하라" 같은 막연한 문구는 쓰지 않는다.

**P3. 코드 소유** (M3=소유자로 둠) 이 문구와 원칙 G의 과잉 엔지니어링 방지 문구는 함께 넣지 않는다. 출력 토큰이 70~80% 늘고 요청하지 않은 변경이 생길 수 있으니 diff와 PR 요약을 직접 검토하라고 사용자에게 알린다. M3=최소 변경이면 넣지 않는다.
```
당신은 이 코드베이스의 소유자이자 장기 유지보수자이며, 설계는 당신이 정한다.
```
원문:
```text
You are the owner and long-term maintainer of this codebase, and its design is up to you.
```

**P4. 진행 보고 형태** (G6=시작 한 줄 + 마지막 요약. 사람이 대화하며 진행하는 작업에 가장 유용하다.)
```
시작하기 전에 무엇을 할지 한 줄로 말한다. 작업 중에는 사용자가 흐름을 따라올 수 있게 짧게 알린다. 마지막에는 그것만 읽어도 전체가 이해되는 짧은 요약(무엇을 찾았고, 무엇을 했으며, 다음은 무엇인지)으로 끝낸다.
```
원문:
```text
Before you start, say in a line what you're about to do; brief updates while you work help the user follow along. Close with a short recap that stands on its own (what you found, what you did, and what's next), so a reader who only sees the last message has the full picture.
```

**P5. 중간 업데이트 대체 문구** (M4=아니오) 하네스 알림을 붙일 수 없을 때만 시스템 프롬프트에 넣는다. M4=예이면 넣지 않고 실행 설정 권고의 하네스 알림을 쓴다.
```
도구를 몇 번 호출할 때마다 사용자에게 진행 상황을 한 줄로 알린다.
```
원문:
```text
Every few tool calls, give the user a one-line update on where things stand.
```

**P6. 읽기 쉬운 보고** (M5=예) 독자에 맞게 조정한다. 초안에 문장 길이 같은 하드 문체 제한이 있으면 먼저 제거 여부를 묻는다(제거 검토 참고).
```
# 명확한 전달
똑똑하지만 맥락이 없는 독자를 위해 쓴다. 독자는 당신의 도구 호출, 추론, 연 파일을 보지 못했고, 다른 일을 하다 막 넘어왔을 수 있다. 메시지는 다른 맥락을 찾지 않아도 이해되게 쓴다. 핵심은 처음 몇 문장에 둔다. 문장 순서는 점진적으로 공개하고, 12번째 줄에서야 이해되는 정의 안 된 용어나 개념을 첫 줄에 쓰지 않는다.

쉬운 단어로, 이해하기 쉬운 완결된 문장으로 쓴다. 작업 중에 만든 용어나 약어는 쓰지 말고, 그것이 무엇인지 누구나 알 수 있게 말한다. 대체로 ASD-STE100 Simplified Technical English 방식으로 쓴다. 문장은 짧게, 한 문장에 한 생각, 능동태, 같은 대상에는 같은 단어. 생각이 이어지는 곳은 흐르는 산문 문단으로 쓰고, 글머리 기호는 서로 독립된 항목 목록에만 쓴다. 독자가 묻지 않은 세부는 빼고 간결하게 쓰되 핵심 맥락은 반드시 담는다. 사용자에게 보이는 글은 최대한 사람이 읽기 쉽고 명확하게 쓴다.
```
원문:
```text
# Communicating clearly
Write for an intelligent but low-context reader. The person reading has not seen your tool calls, your reasoning or the files you opened, and may be switching in from other work. Messages should generally be self-contained: the reader should understand what you mean without having to dig for other context. Put the key points in the first few sentences. Practice progressive disclosure in your sentence order, and do not use undefined references and ideas in line 1 that won't make sense until the reader reaches line 12.

Use plain words, and write in clear, understandable full sentences. Do not use a term or abbreviation that you made up during the work. Say what the thing is in a way any reader would understand. Write mostly in the style of ASD-STE100 Simplified Technical English: short sentences, one idea per sentence, active voice, and consistently using the same word for the same thing. Use a paragraph of flowing prose where ideas connect, and keep bullets for lists of separate items. Leave out unnecessary details unless the reader asks and practice concision, but do ensure that your messages have the key context. Aim to make your user-facing text as human-readable and clear as possible.
```

## 제거 검토

- "답하기 전에 숙고하지 말고 바로 답하라" 같은 문구. 사고를 막지 못한다. 지우고 effort를 낮춘다.
- "문장당 20단어 이하", "한 문장에 지시 하나" 같은 하드 문체 제한. 글이 끊긴다. P6을 넣기 전에 지운다.
- 프롬프트에 적은 큰 토큰 예산. 없이 시험한다. API의 task budgets 베타 기능과는 별개다.
- 위임을 권하는 상시 지시(system 프롬프트, 스킬, 에이전트 파일). 서브에이전트를 과하게 쓰면 먼저 지운다.
- Opus 5.5 가이드의 "이전 답변은 끝난 것으로 본다" 문구. 이전 답변을 다시 검토하게 하려면 뺀다. `high`에서는 후속 턴의 사고가 줄고 이전 실수를 지적할 가능성이 크게 떨어진다.
- 이유가 사라진 주의 문구와 "never" 규칙(메모리, 노트, 지시 파일 포함). 범위와 이유가 있는 규칙으로 고쳐 쓴다.
- "첫 오류에서 멈추고 검토받으라" 같은 불필요한 정지 조건.
- 추론을 응답에 적게 하는 지시(프롬프트, 스킬, 도구 설명). `reasoning_extraction` 거부가 날 수 있다. 추론을 보려면 `thinking.display: "summarized"`를 쓴다.

## 실행 설정 권고

- `output_config.effort`: `high`를 명시하고 `medium`, `xhigh`와 자체 평가로 비교한다. Fable 5.1이나 Opus 5.5에서 맞춘 값을 그대로 옮기지 않는다. 평가가 유지되면 `medium`으로 낮춘다. 에이전트 작업을 `low`·`medium`으로 돌리면 P1을 함께 넣는다. 한 워크플로 안에서 단계를 섞어도 된다(계획은 `medium`, 긴 실행은 더 높게).
- effort를 대화 중에 바꿀 때: 메시지별 effort(베타 헤더 `mid-conversation-output-config-2026-07-01`)는 프롬프트 캐시를 유지한다. 최상위 effort를 바꾸면 캐시가 처음부터 다시 쌓인다.
- 진행 업데이트 수신: `thinking.display: "updates"`(베타 헤더 `thinking-display-updates-2026-08-18`) 또는 `"summarized"`. 기본값 `"omitted"`에서는 비어 있다.
- 조용한 구간 알림(M4=예): 말없이 도구 단계가 여러 번 이어지면, 최신 도구 결과 뒤에 턴 범위 시스템 메시지(`role: "system"`, `clear_at: "next_user_message"`, 베타 헤더 `mid-conversation-system-clear-at-2026-08-21`)로 다음 문구를 붙인다. 원문: "The user hasn't heard from you in a while: say in a few words what you're doing, then continue."
- 대화 기록: assistant 턴은 사고 블록까지 받은 그대로 추가한다. 지시 변경은 최신 턴에 넣거나 대화 중간 시스템 메시지로 붙인다. 기록을 줄일 때는 context editing이나 압축을 쓴다. 대체 수단으로 `thinking.block_binding.prefix_mismatch_behavior: "drop_block"`(베타 헤더 `thinking-binding-controls-2026-08-01`)이 있지만, 매 턴 사고를 버리면 모델이 다시 사고해 출력 토큰이 늘므로 측정 후 쓴다.
- 서브에이전트 도구: 필요 이상으로 위임할 때만 설명을 고친다. 서브에이전트가 세션 비용에 얼마를 더하는지, 언제 위임할 가치가 있고 없는지, 위임할 때 어떻게 지시를 전달할지 적는다. 서브에이전트의 기본 모델도 확인한다. 비용 중심의 긴 설명이 `high`에서 서브에이전트 수를 절반가량 줄였다.
- 승인 응답: 계속 진행시킬 때는 "계속"만 보내지 말고 원하는 것을 구체적으로 말한다(예: "스테이징 DB에 마이그레이션을 실행해").
- 위험하거나 되돌릴 수 없는 행동의 확인 절차는 하네스에 직접 둔다.
- 정당한 사이버·생명과학 작업이 막히면 Cyber Verification Program이나 Life Sciences Verification Program에 신청한다.

## 검수 항목

- [ ] "바로 답하라"류 문구와 하드 문체 제한이 없다
- [ ] P3과 원칙 G의 과잉 엔지니어링 방지 문구가 함께 들어가지 않았다
- [ ] 승인 목록에 넓은 범주나 범위 없는 "never" 규칙이 없다
- [ ] P5는 하네스 알림을 쓸 수 없을 때만 들어갔다
- [ ] 하네스 권고(append-only, effort 비교, 확인 절차)가 에이전트 종류에 기재됐다
