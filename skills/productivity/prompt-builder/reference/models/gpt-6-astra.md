# GPT-6 Astra 가이드

출처: https://developers.openai.com/api/docs/guides/prompt-guidance ("Using GPT-6")
모델·파라미터 출처:
- https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra
- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/guides/reasoning
- https://developers.openai.com/api/docs/guides/deployment-checklist
구조·문구 일반 지침 출처: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6 ("Prompting guidance for GPT-5.6 Sol")
확인일: 2026-11-13 (출처 문서와 대조)

GPT-6 문서의 프롬프트 권고는 GPT-6 Astra에서 관찰한 동작을 다루며, 문서가 GPT-6 계열 전체의 출발점이라고 밝힌다. GPT-6 문서는 프롬프트 구조를 따로 권하지 않으므로, 조립 골격과 문구 지침은 GPT-5.6 Sol 문서를 출발점으로 쓴다. 스니펫 아래 "원문 요지"는 공식 문서 문장을 영어로 요약한 것이며 원문 그대로가 아니다. B2=영어이면 원문 요지를 바탕으로 쓰고, 그 외 언어이면 한국어 스니펫을 바탕으로 쓴다.

## 목차
- 특성 요약
- 조립 골격
- 결정 질문
- 프롬프트 반영
- 제거 검토
- 실행 설정 권고
- 검수 항목

## 특성 요약

- 모델 ID는 `gpt-6-astra`이다. OpenAI가 가장 어려운 작업용 주력 모델로 권한다. 비용을 낮추려면 GPT-6.1 Sol(`gpt-6.1-sol`)을, 대량·단순 작업에는 GPT-6 Luna(`gpt-6-luna`)를 권한다.
- 컨텍스트 1.05M 토큰, 최대 출력 128K 토큰, 지식 컷오프 2026-04-30 (모델 페이지 기준).
- reasoning effort는 `low`, `medium`, `high`, `xhigh`, `max`를 받는다. `none`은 HTTP 400 오류다. 기본값은 문서에 적혀 있지 않다.
- reasoning effort가 `none`이 아니면 `temperature`, `top_p`, `top_logprobs`를 빼야 한다. Astra는 `none`을 받지 않으므로 항상 뺀다.
- Chat Completions 요청은 받지만 함수 호출(tool calling)은 Responses API에서만 된다.
- 긴 작업에서 일관성을 유지하는 능력이 GPT-5.6 Sol과 이전 모델보다 낫다고 문서가 밝힌다.
- 명확화 질문을 더 자주 해서, 사용자가 끝까지 해 주길 기대한 작업을 중간에 멈출 수 있다. 작업 중 막히지 않는(non-blocking) 질문도 즐겨 한다.
- 긴 지시를 잘 따르지만, 스킬이나 `AGENTS.md` 같은 파일 속 지시에 더 민감하다. 문서는 이런 파일을 감사해 동작을 바꿀 수 있는 지시를 찾으라고 강하게 권한다.
- 목록, 표, 마크다운을 많이 쓰는 자세하고 서식 있는 답을 내는 경향이 있고, 반복되는 상투 표현이 있다.
- 서브에이전트에 원하는 만큼 자주 위임하지 않을 수 있다.
- 코딩에서 테스트를 꼼꼼히 하며, 작은 작업에 필요한 범위보다 넓게 테스트하기도 한다.

## 조립 골격

GPT 대상에서는 [principles.md](../principles.md)의 XML 태그 골격 대신 이 골격을 쓴다. GPT-5.6 Sol 문서가 제시한 짧은 이름 붙은 절 구성이며, 각 절은 짧게 두고 동작을 바꾸는 곳에만 세부를 더한다. 절 제목은 B2 언어로 쓴다. 공식 문서는 절 표기 방식(마크다운 제목, XML 등)을 정하지 않으므로, 표기는 마크다운 제목을 기본으로 하고 사용자가 XML을 원하면 따른다.

```
Role            역할 1~2문장
Personality     톤과 협업 방식 (C12, G3에서 받은 것)
Goal            목적 (C1)
Success criteria 성공 기준과 완료 조건 (C1, C14, G5)
Constraints     규칙과 이유, 범위 밖 요청, 불확실할 때의 행동, 확인이 필요한 행동
Tools           도구별 사용 시점과 방법 (도구가 있을 때)
Output          절 구성, 길이, 형식, 톤
Stop rules      멈추고 보고할 조건
```

예시(C13)와 긴 자료는 Output 앞에 별도 절로 둔다. 캐싱을 위해 고정 지시와 예시를 앞에, 바뀌는 내용을 끝에 둔다(deployment checklist). 받은 값이 없는 절은 쓰지 않는다.

## 결정 질문

| ID | 조건 | 질문 | 종류 |
|---|---|---|---|
| M1 | 에이전트, 또는 API에서 작업을 대신 해 주는 앱 | 모호해도 의도를 추론해 끝까지 진행하게 할까요? (진행 + 파괴적 행동만 확인 / 넣지 않음) | API·에이전트 |
| M2 | 에이전트 + 스킬·`AGENTS.md`·지침 파일을 함께 씀 | 사용자 지시가 스킬 지침보다 우선한다고 명시할까요? | 에이전트 |
| M3 | C10이 산문 또는 마크다운 | 목록·표를 줄이고 문단 위주로 쓰게 할까요? 피할 상투 표현 목록을 넣을까요? | 전체 |
| M4 | 에이전트 + G7=허용 | 시간이나 품질에 이득이 있으면 서브에이전트에 적극 위임하게 할까요? | 에이전트 |
| M5 | 에이전트 + G11=코딩 | 되돌리기 쉬운 작은 변경에는 구현을 그대로 따라 하는 테스트를 쓰지 않게 할까요? | 에이전트 |
| M6 | 에이전트 + G6이 "최소화"가 아님 | 첫 도구 호출 전 한두 문장 안내와 단계 전환 때의 짧은 보고를 넣을까요? | 에이전트 |

## 프롬프트 반영

**P1. 의도 추론과 끝까지 진행** (M1) 문서는 이 동작을 세 문구로 나눠 제시한다. 위험하거나 되돌릴 수 없는 행동에 대한 확인 규칙(G4)은 이 스니펫이 대신하지 않으므로 그대로 둔다.
```
맥락에서 사용자의 의도와 작업 범위를 추론하고, 행동 쪽으로 기울어 목표까지 계속 진행한다. 명백히 파괴적이거나 되돌릴 수 없는 단계 앞에서만 멈춘다.

"~할 수 있어?", "~하고 싶어", "~ 도와줘" 같은 표현도 실행 요청으로 본다. 할 수 있다고 답하거나 계획만 내놓고 멈추지 않는다.

승인을 구하기 전에 허락된 작업을 마치고 결과를 구체적으로 만든다. 가정에 불과한 위험을 이유로 요청하지 않은 경고나 승인 절차를 덧붙이지 않는다.
```
원문 요지:
```text
Infer the user's intent and task scope from context, bias toward action, and keep going until the goal is reached. Stop only before clearly destructive or irreversible steps.

Treat phrasing such as "can you", "I want to", and "help me" as requests to act, not as a cue to confirm capability or offer a plan.

Finish the authorized work and make the result concrete before asking for approval. Don't add unrequested warnings or approval steps for hypothetical risks.
```

**P2. 사용자 지시 우선** (M2=예)
```
사용자의 지시는 스킬에 담긴 지침보다 우선한다. 스킬 때문에 작업을 멈추게 되면, 해당 SKILL.md의 정확한 경로를 밝히고 그 지시를 인용한 뒤, 명시된 요구 사항과 내 해석을 구분해 말한다.
```
원문 요지:
```text
The user's instructions take precedence over guidelines provided in a skill. If a skill makes you pause, name and link the exact SKILL.md, quote the instruction, and separate its explicit requirements from your interpretation.
```
첫 문장만 원문 그대로다.

**P3. 문체와 서식** (M3) 첫 문단은 M3의 서식 질문에 예일 때, 둘째 문단은 상투 표현 질문에 예일 때 넣는다. C10=마크다운이면 첫 문단의 목록 기준만 넣는다.
```
기본은 명확하고 간결한 문단으로 쓴다. 목록은 정보가 실제로 병렬이거나 순서가 있거나 비교하기 쉬울 때만 쓰고, 꼭 필요하지 않으면 중첩 목록을 쓰지 않는다. 쉬운 말과 능동태로 쓰고 핵심을 먼저 말한다.

다음 표현과 패턴을 쓰지 않는다: "delve", "leverage", "foster", "genuinely", "it's worth noting", "Bottom Line:", "X가 아니라 Y" 식 대비, 지어낸 합성 용어, 끝에 붙이는 요약 문장.
```
원문 요지:
```text
Default to clear, concise paragraphs. Use lists only when the information is genuinely parallel, sequential, or easier to compare, and avoid nested lists unless needed. Use plain language and active voice, and lead with the main point.

Avoid these words and patterns: "delve", "leverage", "foster", "genuinely", "it's worth noting", "Bottom Line:", "X, not Y" framing, invented compound labels, and concluding summary lines.
```
둘째 문단의 금지 목록은 문서 목록의 일부다. 영어 출력에만 의미가 있는 단어는 B2=영어일 때만 넣는다.

**P4. 서브에이전트 위임** (M4=예) 원칙 G의 서브에이전트 항목 대신 넣는다.
```
병렬로 진행하면 시간이 줄거나 품질이 오르는 일은 다른 에이전트에 위임한다. 에이전트 사이의 메시지와 최종 메시지는 단어와 숫자 사이 띄어쓰기를 지켜 읽기 쉽게 쓴다.
```
원문 요지:
```text
Delegate to another agent when parallel work would save time or improve quality. Keep inter-agent and final messages legible, with proper spaces between words and numbers.
```

**P5. 테스트 범위** (M5=예) G13의 테스트 하드코딩 방지와 함께 쓸 수 있다.
```
되돌리기 쉽고 영향이 작은 변경에는 구현을 그대로 따라 하는 테스트를 쓰지 않는다. 테스트는 의미 있는 동작을 검사해야 한다. 적절한 검사를 돌리고, 새 변경이나 실패, 우려가 있을 때만 테스트 범위를 넓힌다.
```
원문 요지:
```text
Do not write tests for reversible, low-impact changes that mirror the implementation. Tests should be meaningful. Run the appropriate checks, and broaden testing only when new changes, failures, or concerns justify it.
```
첫 문장만 원문 그대로다.

**P6. 진행 보고** (M6=예) GPT-5.6 Sol 문서의 권고다.
```
여러 단계로 된 작업이면 첫 도구 호출 전에 첫 단계를 밝히는 한두 문장의 안내를 사용자에게 보여 준다. 그 뒤에는 큰 단계가 바뀔 때만, 결과 하나와 다음 단계를 짧게 알린다. 일상적인 도구 호출을 하나하나 설명하지 않는다.
```
원문 요지:
```text
For multi-step tasks, give a one- or two-sentence user-visible update that states the first step before the first tool call. After that, send sparse updates at major phase changes, each stating one outcome and the next step. Don't narrate routine tool calls.
```

## 제거 검토

- `temperature`, `top_p`, `top_logprobs`, `logprobs` 설정. reasoning이 켜진 Astra에서는 빼야 한다.
- reasoning effort `none`. 400 오류이므로 `low`로 바꾼다. 기존 값이 `minimal`이면 `low`에서 시작해 비교한다.
- "먼저 물어봐라", "바꾸지 마라", "승인을 기다려라" 같은 확인 문구의 반복. 불필요한 승인 요청을 부른다(GPT-5.6 Sol 문서). 확인이 필요한 행동은 G4 목록으로 한 번만 적는다.
- 스킬과 `AGENTS.md` 속에서 프롬프트와 충돌하거나 멈춤을 부르는 지시. Astra는 이런 파일에 민감하다.
- 동작을 바꾸지 않는 반복 규칙, 스타일·절차 지시, 예시, 무관한 도구. GPT-5.6 Sol 문서는 한 묶음씩 빼며 같은 평가를 다시 돌리라고 권한다.
- `ALWAYS`, `NEVER`, `must`를 진짜 불변 조건이 아닌 곳에 쓴 문구 (공통 원칙 E와 같은 취지).
- Claude 전용 설정과 문구: assistant prefill, `thinking`, `output_config.effort`, `budget_tokens`, 베타 헤더. GPT API에는 해당하지 않는다.

## 실행 설정 권고

- API: 도구를 쓰면 Responses API를 쓴다. Chat Completions의 함수 호출 요청은 Responses로 옮긴다.
- `reasoning.effort`(Responses) 또는 `reasoning_effort`(Chat Completions): `low`~`max`. 기본값이 문서에 없으므로 값을 명시한다. 이전 모델에서 옮기면 기존 값을 기준으로 그 값과 한 단계 낮은 값을 평가로 비교한다(GPT-5.6 Sol 문서). `max`는 가장 어려운 품질 우선 작업에만 쓴다.
- `reasoning.mode`: 기본은 standard다. `pro`는 effort와 별개로 고른다.
- `text.verbosity`: `low`, `medium`, `high`로 기본 상세도를 정하고, 작업별 길이와 구조는 프롬프트에 적는다. 기본값은 문서에 없다.
- `max_output_tokens`: reasoning 토큰도 여기에 포함된다. 시작할 때는 reasoning과 출력에 25,000 토큰 이상을 남기라고 reasoning 문서가 권한다. 모자라면 `status: "incomplete"`, 이유 `max_output_tokens`로 끝난다.
- 대화 중 effort 변경: 다음 user 메시지 앞에 `{"type": "configuration_update", "reasoning": {"effort": "high"}}` 입력 항목을 넣는다. 요청 수준의 `reasoning.effort`는 바꾸지 않아야 캐시가 유지된다. standard 단일 에이전트 모드에서만 되고, 자동 압축·truncation과 함께 쓸 수 없다.
- 함수 호출 기록: Responses에서 도구 결과와 함께 reasoning 항목을 돌려보낸다. 기록을 직접 관리하면 모든 출력 항목을 순서대로 넣고 새 항목은 뒤에 붙인다. reasoning 항목 앞의 기록을 바꾸면 API가 그 reasoning을 버릴 수 있다.
- 진행 보고(M6): progress update에는 `phase: "commentary"`, 최종 답에는 `phase: "final_answer"`를 쓰고, assistant 메시지의 phase를 그대로 돌려보낸다(deployment checklist).
- 비동기 도구: 오래 걸리는 함수·custom 도구에 `async: true`를 두고 나중에 원래 `call_id`로 결과를 돌려준다. 내장 도구에는 쓸 수 없다.
- 캐싱: GPT-5.5 이하에서 옮기면 `prompt_cache_retention` 대신 `prompt_cache_options.ttl: "30m"`을 쓴다.
- 데이터 위치: Astra의 Fast mode는 EU 데이터 위치를 지원하지 않고 지연 SLA가 없다. 요건이 있으면 GPT-6.1 Sol을 검토하게 한다.

```yaml
model: gpt-6-astra
reasoning:
  effort: <low|medium|high|xhigh|max>   # 근거
text:
  verbosity: <low|medium|high>           # 근거
max_output_tokens: <값>                  # reasoning 포함
```

## 검수 항목

- [ ] reasoning effort가 `none`이 아니고 값이 명시되어 있다
- [ ] `temperature`, `top_p`, `top_logprobs`, `logprobs`가 없다
- [ ] 도구를 쓰면 Responses API로 권고했다
- [ ] Claude 전용 설정(prefill, `thinking`, `output_config`, 베타 헤더)이 없다
- [ ] P1을 넣었어도 위험 행동 확인 규칙(G4)이 유지된다
- [ ] 확인·승인 문구가 G4 목록 밖에서 반복되지 않는다
- [ ] 작업별 길이·구조가 프롬프트에 있고, 기본 상세도는 `text.verbosity`로 권고했다
