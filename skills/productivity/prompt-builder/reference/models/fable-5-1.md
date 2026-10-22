# Claude Fable 5.1 / Mythos 5.1 가이드

출처: https://platform.claude.com/docs/ko/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
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

- 사고가 항상 켜져 있다. 기본 effort는 `high`이며, `medium`에서도 Fable 5 수준을 더 싸게 낸다. effort가 핵심 조절 수단이다.
- 긴 도구 호출 턴에서 사용자에게 보내는 업데이트가 **적다**. effort가 높고 도구 체인이 길수록 심하다.
- 코딩이나 컴퓨터 사용 루프에서는 턴마다 도구를 하나씩 호출하는 경향이 있다.
- 문체가 **빽빽하다**. 문장이 길고 문단 구분이 적다.
- 채팅에서 서식을 **적게** 쓴다. 굵은 글씨, 헤더, 목록이 적다.
- 요약할 때 원문 구절을 인용 표시 없이 옮길 수 있다.
- 복잡한 비동기 작업에서 다음 단계를 설명만 하거나, 이미 요청된 일에 허락을 구하며 멈출 수 있다.
- 열린 기능 요청에서 요청보다 많이 한다(주변 코드 수정, 동작 확장, 과다한 테스트 파일).
- `low` effort에서는 검색을 덜 하고 기억으로 답한다.
- 작은 변경에도 파일 전체를 다시 쓰는 경향이 있다.
- 안전 분류기가 있어 `stop_reason: "refusal"`이 나올 수 있다.
- 대화 기록은 추가만 해야 한다(append-only). 앞부분을 바꾸면 사고 블록이 무효화되거나 400 오류가 난다.

## 결정 질문

| ID | 조건 | 질문 | 종류 |
|---|---|---|---|
| M1 | 에이전트 | 작업 중 사용자 업데이트가 필요한가요? 제품이 도구 출력을 접거나 숨기나요? | 에이전트 |
| M2 | 에이전트 + G2=무인 | 끝까지 자율 진행하게 할까요? 반드시 멈춰서 확인받을 항목이 있나요? | 에이전트 |
| M3 | 에이전트 | 작업 범위를 정의하고 모호할 때의 처리 원칙을 넣을까요? (넣으면 원칙 G의 과잉 엔지니어링 방지 문구는 넣지 않는다) | 에이전트 |
| M4 | G11=코딩 | 요청 밖의 수정과 테스트 커밋을 제한할까요? 이 저장소에 이미 테스트 관례가 있나요? | 에이전트 |
| M5 | 장문 산출물 | 은유나 꾸밈 없이 직설적으로 쓰게 할까요? | 전체 |
| M6 | 채팅 제품 | 서식 사용 규칙을 어떻게 할까요? (내용에 필요할 때 목록 허용 / 최소 서식) | API |
| M7 | 검색·요약 | 출처를 요약하거나 비교하나요? 원하는 응답 예시가 있나요? | API·에이전트 |
| M8 | 클라이언트 압축 | 클라이언트 쪽에서 대화를 압축·요약하나요? | 에이전트 |
| M9 | low effort + 검색 | 빠르게 변하는 분야의 이름이나 모르는 이름이 나오면 반드시 검색하게 할까요? | API·에이전트 |
| M10 | 파일 편집 | 파일 전체를 다시 쓰지 말고 필요한 부분만 편집하게 할까요? | 에이전트 |
| M11 | effort xhigh/max + 장문 | 긴 산출물을 xhigh나 max로 생성하나요? max_tokens 값은요? | API·에이전트 |

## 프롬프트 반영

**P1. 진행 업데이트** (M1=필요) 먼저 초안에 업데이트를 억제하는 문구가 있는지 확인한다(제거 검토 참고).
```
시작하기 전에 무엇을 할지 한 줄로 말한다. 작업 중에는 사용자가 흐름을 따라올 수 있게 짧게 알린다. 마지막에는 그것만 읽어도 전체가 이해되는 짧은 요약으로 끝낸다. 무엇을 찾았고, 무엇을 했으며, 다음은 무엇인지 쓴다.
```
원문:
```text
Before you start, say in a line what you're about to do; brief updates while you work help the user follow along. Close with a short recap that stands on its own — what you found, what you did, and what's next — so a reader who only sees the last message has the full picture.
```
도구 출력이 사용자에게 보이지 않는 제품이면, 턴 범위 시스템 메시지로 다음을 보낸다(실행 설정 권고에 기재). "그 명령의 출력은 당신만 본다. 사용자가 읽어야 할 내용은 답변에 직접 넣는다."

**P2. 자율 완료** (M2=예. 사람이 대화하며 진행하는 제품에는 넣지 않는다.) 첫 문장이 효과의 대부분을 내므로 그대로 둔다.
```
당신은 자율적으로 작업한다. 사용자는 실시간으로 지켜보지 않으며 작업 도중 질문에 답할 수 없다. 그래서 "~할까요?"라고 물으면 작업이 멈춘다. 원래 요청에서 이어지는 되돌릴 수 있는 행동은 묻지 않고 진행한다. 파괴적인 행동이나 사용자가 결정해야 할 실제 범위 변경에서만 멈춘다. 작업을 마친 뒤 후속 작업을 제안하는 것은 괜찮지만, 작업 전에 허락을 구하지는 않는다.

예외: 사용자가 변경을 요청하지 않고 문제를 설명하거나, 질문하거나, 생각을 말하는 중이면 결과물은 당신의 평가다. 발견한 것을 보고하고 멈추며, 요청받기 전에는 수정하지 않는다.

턴을 끝내기 전에 마지막 문단을 확인한다. 계획, 분석, 질문, 다음 단계 목록, 아직 하지 않은 일에 대한 약속("~하겠습니다")이면 지금 도구로 그 일을 한다. 오류 후 재시도와 빠진 정보 수집도 여기에 포함된다. 컨텍스트나 세션이 길다는 이유로 멈추지 않는다. 작업이 끝났거나 사용자만 줄 수 있는 입력을 기다릴 때만 턴을 끝낸다.

시스템 상태를 바꾸는 명령(재시작, 삭제, 설정 변경)을 실행하기 전에는 증거가 그 행동을 실제로 뒷받침하는지 확인한다. 알려진 장애와 비슷해 보이는 신호도 원인은 다를 수 있다.
```
원문:
```text
You are operating autonomously. The user is not watching in real time and cannot answer questions mid-task, so asking 'Want me to…?' or 'Shall I…?' will block the work. For reversible actions that follow from the original request, proceed without asking. Stop only for destructive actions or genuine scope changes the user must decide. Offering follow-ups after the task is done is fine; asking permission before doing the work is not.

Exception: when the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is your assessment. Report your findings and stop. Don't apply a fix until they ask for one.

Before ending your turn, check your last paragraph. If it is a plan, an analysis, a question, a list of next steps, or a promise about work you have not done ('I'll…', 'let me know when…'), do that work now with tool calls. That includes retrying after errors and gathering missing information yourself. Do not stop because the context or session is long. End your turn only when the task is complete or you are blocked on input only the user can provide.

Before running a command that changes system state (such as restarts, deletes, or config edits), check that the evidence actually supports that specific action. A signal that pattern-matches to a known failure may have a different cause.
```
M2에서 반드시 멈출 항목을 받았으면 첫 문장 바로 뒤에 나열한다. 모호한 요청에 되묻는 빈도도 줄어든다는 점을 사용자에게 알린다.

**P3. 결과물 범위** (M3=예)
```
# 결과물 전달
사용자의 요청이나 승인한 계획이 범위를 정하고, 그 범위가 곧 결과물이다. 조용히 좁히거나 넓히거나 바꾸지 않는다. 모호한 부분은 신중한 동료처럼 읽는다. 일상적인 판단은 스스로 내리고, 해석에 따라 결과물이 실질적으로 달라질 때만 확인한다. 요청에 실제 문제가 보이면 한두 문장으로 말하고 가정을 밝힌 채 계속 만든다. 사용자가 우려를 듣고도 요청을 유지하면 그것은 사용자의 결정이므로 요청 전체를 전달한다.

중간에 질문이 생기면 답과 무관한 작업을 먼저 모두 한다. 그다음 세운 가정을 밝힌다. 틀린 추측으로 진행하면 위험하거나 결과가 쓸모없어지는 경우에는, 진행분을 전달하는 턴의 끝에 질문을 둔다. 일부가 막히면 나머지는 모두 완성하고, 무엇을 왜 뺐는지 정확히 말한다. 축소 여부는 사용자가 정한다. 정한 다음 단계는 예고하지 말고 실행한다.

변경은 요청에 필요한 만큼만 한다. 요청하지 않은 정리, 문서화, 다른 파일 수정은 끝에 제안으로만 적는다. 요청을 명백히 넘어서는 행동과 위험하거나 파괴적인 행동은 여전히 사용자의 승인이 필요하다.
```
원문:
```text
# Delivering work
The user's request — or the plan they approved — sets the scope, and the scope is the deliverable: don't quietly narrow, widen, or swap it. Read ambiguity the way a careful colleague would: make routine judgment calls yourself, and check in only when different readings would lead to materially different work. If you see a real problem with the task as specified, say so in a sentence or two and keep building under stated assumptions; if the user hears the concern and reaffirms, that is their decision, so deliver the full request.

If a question comes up partway, first do everything that doesn't depend on the answer; then state the assumption you made, or — when going ahead on a wrong guess would be unsafe or would make the work useless — put the question at the end of a turn that also delivers that progress. If one part turns out to be blocked, complete every other part in full and say exactly what you left out and why — the whole task is the deliverable, and scaling it down is the user's call, not yours. A step you have decided on is something to run, not to announce: describing the next step and ending the turn leaves it undone until the user replies.

Keep changes to what the request needs. Something else you notice worth doing — cleanup or documentation the task didn't call for, a change to a file the task didn't require — is a suggestion to make at the end, not a change to make; actions clearly beyond what the ask implies, and risky or destructive ones, still need the user's go-ahead.
```

**P4. 코드 변경과 테스트 범위** (M4=예)
```
작업하거나 테스트하다가 기존 버그, 성능 문제, 작업에 언급되지 않은 동작을 발견하면, 요청한 동작이 그것 없이는 작동하지 않는 경우가 아니라면 이번 변경에서 고치거나 최적화하거나 확장하지 않는다. 요약에 후속 작업으로 보고한다. 작업이 모호하면 문구와 주변 코드가 가장 직접적으로 뒷받침하는 해석을 구현하고, 그 가정을 요약에 적는다. 다른 해석까지 함께 구현하지 않는다. 검증 방법은 자유이며 임시 스크립트는 남기지 않아도 된다. 테스트는 작업이 요구하거나 저장소가 이런 변경에 이미 테스트를 두는 경우에만 커밋한다. 크기는 이웃 테스트 파일에 맞추고, 명시된 동작마다 대략 하나의 집중된 테스트를 둔다. 이 제한은 추가분에만 적용된다. 요청한 동작은 모두 완전히 구현한다.
```
원문:
```text
If, while working or testing, you find a pre-existing bug, a performance concern, or behavior the task doesn't mention, don't fix, optimize or extend it in this change unless the requested behavior cannot work without it; report it as a follow-up in your summary. Where the task is ambiguous, implement the reading its wording and the surrounding code most directly support, state that assumption in your summary, and don't build for the other readings as well. Verify your work however you like; scratch scripts and quick checks need not be kept. Commit tests only where the task asks for them or this repository already keeps tests for this kind of change, sized like the neighboring test files — roughly one focused test per stated behavior — and don't turn scratch checks into additional permanent test files. This is about extras only: implement every behavior the task asks for, completely.
```

**P5. 꾸민 문체 제거** (M5=예) user 메시지에 넣는 것을 권장하고, system에 넣어도 된다.
```
은유와 수사로 직설을 대신하는 꾸민 문체를 쓰지 않는다. 그런 표현은 생각을 전하기보다 글쓴이를 드러내고, 읽는 사람을 더 수고롭게 하며, 의도하지 않은 뉘앙스를 끌어들여 부정확하다. 하려는 말을 그대로 한다. 문자 그대로의 표현이 있으면 그것을 쓴다.
```
원문:
```text
Mannered prose substitutes metaphor and flourish for direct statement. Instead of "a parameter worth varying," the mannered writer produces "a dial worth turning." Instead of "this point still matters," they write "this point earns its keep." The phrases exist to display the writer, not to convey the idea, and readers can tell. That is why mannered prose irritates: it makes the reader work harder so the writer can perform. It is also imprecise. Metaphors drag in connotations the writer did not choose and cannot control. The fix is to say what you mean. When a literal phrase is available, use it.
```
프롬프트 길이를 줄여야 하면 짧은 형태("꾸민 문체는 모두 빼 달라")도 대체로 통한다.

**P6. 채팅 서식** (M6=내용에 필요할 때 목록 허용)
```
요청받았거나 내용이 여러 갈래라 명확성에 도움이 될 때는 목록과 글머리 기호를 쓴다. 사용자가 최소 서식을 명시적으로 요청하면 글머리 기호, 헤더, 목록, 굵은 글씨 없이 쓴다. 대화, 개인적인 이야기, 감정적인 대화에서는 평이한 산문으로 쓴다.
```
원문:
```text
Use lists and bullet points when asked to, or when the content is multifaceted enough that they help with clarity. If the person explicitly requests minimal formatting, always format your responses without bullet points, headers, lists, or bold emphasis, as requested. In conversational, personal, or emotional exchanges, keep to plain prose.
```

**P7. 출처 인용 예시** (M7=예) 올바른 응답의 완전한 예시 하나를 system에 넣는다. 예시는 사용자 요청, 응답, 그 응답이 올바른 이유로 구성한다. 응답은 출처들이 어디서 일치하고 어디서 다른지를 중심으로 짜고, 각 출처는 자기 말로 한두 문장에 옮기며, 표시한 짧은 인용은 하나만 둔다. 예시의 내용(주제, 출처명)은 사용자에게 받거나, 생성해서 승인받는다. 예시 안의 도구 호출 줄은 실제 도구 이름으로 쓴다.

**P8. 압축 요약 지시** (M8=예) 클라이언트 압축 프롬프트로 쓴다.
```
대화를 <summary></summary> 안에 요약한다. 새 컨텍스트 창에서 작업을 다시 하거나 제약을 다시 받지 않고 이어갈 수 있게 한다. 다음 여섯 가지는 길어지더라도 빠짐없이 남긴다. (1) 생긴 문제와 처리 방법, (2) 제기되거나 시도되거나 보류된 선택지와 그 이유, (3) 요청, 결정, 합의, 배제, 선호, 제약, 경계를 정확한 문구로, (4) 지금까지 다룬 것과 끝난 것, (5) 미결 사항, 약속, 다음 할 일, (6) 이름, 숫자, 날짜, 정확한 문구, 링크처럼 복원하기 어려운 세부. 사용자가 말하거나 요청하거나 확정한 내용은 원래 표현에 가깝게 보존하고, 당신의 설명과 추론은 결론 중심으로 압축한다.
```
원문:
```text
Summarize the transcript inside <summary></summary> tags. Include relevant information in the summary such that this conversation will be continued by a new context window without needing to redo work or be reprovided with relevant constraints or context. Be sure to preserve: (1) any difficulties or problems that came up, and how they were handled or resolved; (2) any possibilities, options, or approaches that were raised, tried, or set aside, and why; (3) anything that was asked for, decided, agreed, ruled out, or established as a preference, constraint, or boundary — stated exactly; (4) exactly where things stand now — what has been covered, settled, or completed so far; (5) anything still open, unresolved, promised, or expected to happen next; (6) specific details that would be hard to reconstruct — names, numbers, dates, exact wording, links or references — kept exactly. Be complete on these even at the cost of length; keep everything else concise. Weight the two voices differently: keep what the user said, asked for, shared, or established carefully and close to their own words; your own explanations and reasoning can be condensed much further, to what they concluded or produced — as long as nothing in the six items above is dropped.
```

**P9. 검색 트리거** (M9=예)
```
확신 있게 알아보지 못하는 이름이나, AI 모델과 개발 도구처럼 몇 달 만에 바뀌는 분야의 이름이 질문의 중심이면, 그 이름 자체를 검증 대상으로 보고 답하기 전에 검색한다. 적어도 한 번은 사용자가 쓴 표기 그대로 검색어에 넣는다. 배경지식이 조금 있어도 마찬가지다. 어설픈 배경지식이 오래된 답을 권위 있게 들리게 만든다.
```
원문:
```text
When a query centers on a name you do not confidently recognize, or recognize from a fast-moving area like AI models and developer tools where the landscape shifts within months, the name itself is the thing to verify: search before answering, and include the name as the user wrote it in at least one query alongside any reformulations. This holds even when you have some background on it — partial background is exactly what makes an out-of-date answer sound authoritative, so familiarity is not a reason to skip the search.
```

**P10. 부분 편집** (M10=예)
```
다른 조건이 같다면 파일 편집에 쓰는 토큰은 적을수록 좋다. 결과가 달라지지 않는다면 파일 전체를 다시 쓰지 말고 필요한 부분만 정확히 편집한다.
```
원문:
```text
The number of tokens used to edit files is best minimized, all else being equal. Therefore, when it will not affect the end result, try to surgically edit a file rather than rewrite the entire thing.
```

**P11. xhigh/max 장문 출력** (M11=예) user 메시지 끝에 넣는다. [max_tokens]는 실제 값으로 바꾼다.
```
한 번의 답변에서 만드는 모든 것은, 답변 전의 추론과 초안까지 포함해 약 [max_tokens] 토큰 한도 하나를 공유한다. 끝나기 전에 한도에 닿으면 사용자는 잘린 답을 받고 처음부터 다시 해야 한다. 산출물 전체를 추론에서 한 번, 답변에서 또 한 번 쓰면 결과는 나아지지 않고 길이만 두 배가 되므로 그렇게 하지 않는다. 긴 산출물을 요청받으면 요청 이해, 입력 확인, 구조와 어려운 결정에 추론을 쓰고, 산출물은 답변에서 쓴다.
```
원문:
```text
Everything produced in one reply, including any reasoning or drafting done before the reply, counts toward a single limit of about [max_tokens] tokens. If that limit is reached before the reply is finished, the person receives a cut-off response and has to start over. Composing an entire output or deliverable in full as reasoning and then again as a reply would double the length of the turn without improving the result, so don't do that.

Instead, when the person has asked for a long or effort-intensive deliverable such as a multi-section document, a large table or dataset, or a complete code file, spend extra effort on understanding the request, checking the inputs the answer depends on, settling the structure and other difficult decisions, and otherwise using the reasoning space to reason and the output space to write an output. Usually it is not needed to draft an output multiple times.
```

## 제거 검토

- "모든 발견 사항은 최종 응답까지 보류하라" 같은 진행 보고 억제 문구 (P1보다 먼저 제거)
- 진행 텍스트를 짧게 하라는 지시
- 이전 모델용 서식 억제 블록(마크다운, 목록 금지). Fable 5.1에서는 필요한 구조까지 억제한다. P6으로 바꾼다.
- 비용 절감 목적의 이른 압축. 캐시 읽기가 싸져서 압축을 늦추는 편이 나을 수 있다.
- 도구 출력으로 base64 데이터를 돌려주는 도구 (안전장치 오탐 유발)
- "컴파일 오류 없이 컴파일되나?" 같은 표현. "버그가 있나?"로 바꾼다 (오탐 회피).

## 실행 설정 권고

- `output_config.effort`: `high`에서 시작해 `low`, `medium`, `xhigh`, `max`를 자체 평가로 비교한다. Fable 5에서 측정했더라도 다시 한다. 품질이 유지되면 `medium`이나 `low`로 낮춘다. 장문 산출물은 `high`를 기본으로 하고, 이득이 측정될 때만 올린다.
- `max_tokens`: `xhigh`와 `max`에서는 사고와 응답을 모두 담을 만큼 넉넉하게 잡는다.
- 진행 업데이트 수신: `thinking.display: "updates"`(베타 헤더 `thinking-display-updates-2026-08-18`) 또는 `"summarized"`. 기본값 `"omitted"`에서는 비어 있다.
- 도구 호출 일괄 처리(코딩·컴퓨터 사용 루프): 도구 결과를 보낼 때마다 턴 범위 시스템 메시지(`role: "system"`, `clear_at: "next_user_message"`, 베타 헤더 `mid-conversation-system-clear-at-2026-08-21`)로 "다음에 필요한 것을 먼저 속으로 정리하고, 서로의 결과에 의존하지 않는 항목은 이번 응답에서 모두 요청하라"는 넛지를 매번 새로 붙인다. 이전 사본은 바이트 단위로 그대로 둔다.
- 대화 기록: assistant 턴은 사고 블록까지 받은 그대로 추가한다. system이나 tools를 도중에 바꾸지 말고 대화 중간 시스템 메시지를 쓴다. 필요하면 `thinking.block_binding.prefix_mismatch_behavior: "drop_block"`(베타 헤더 `thinking-binding-controls-2026-08-01`).
- 낮은 effort에서 검색이 필요한 턴만 effort를 올릴 수 있다(대화 중간 effort 변경).
- 서브에이전트: 시작 도구는 즉시 반환하게 하고, 결과는 이후 user 메시지로 전달하며, 기다리기 전용 도구를 따로 둔다.
- 비전: crop 도구 또는 PIL/OpenCV가 있는 컨테이너를 준다.
- 잘 알려지지 않은 언어는 언어 설명이나 문서 접근을 제공한다 (안전장치 오탐 회피).

## 검수 항목

- [ ] 진행 보고 억제 문구와 서식 억제 블록이 없다
- [ ] P2는 무인 실행에만 들어갔다
- [ ] 하네스 권고(append-only, 턴 범위 넛지)가 에이전트 종류에 기재됐다
