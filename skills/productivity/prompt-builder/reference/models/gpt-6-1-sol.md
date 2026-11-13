# GPT-6.1 Sol 가이드

출처: https://developers.openai.com/api/docs/guides/prompt-guidance ("Using GPT-6")
모델·파라미터 출처:
- https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6.1-sol
- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/guides/reasoning
- https://developers.openai.com/api/docs/guides/deployment-checklist
구조·문구 일반 지침 출처: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6 ("Prompting guidance for GPT-5.6 Sol")
확인일: 2026-11-13 (출처 문서와 대조)

OpenAI 문서에 GPT-6.1 Sol에서만 관찰한 프롬프트 권고는 없다. GPT-6 문서는 GPT-6 Astra에서 관찰한 권고를 계열 전체의 출발점으로 제시하므로, 이 파일은 Sol의 API 차이만 두고 조립 골격, 결정 질문, 프롬프트 반영 스니펫은 [gpt-6-astra.md](gpt-6-astra.md)를 함께 읽어 쓴다. 그 스니펫을 넣으면 Sol에서는 평가로 확인하라고 "다음 단계"에 적는다.

## 목차
- 특성 요약
- 결정 질문
- 프롬프트 반영
- 제거 검토
- 실행 설정 권고
- 검수 항목

## 특성 요약

- 모델 ID는 `gpt-6.1-sol`이다. OpenAI는 Astra에 가까운 성능을 더 낮은 비용으로 내는, 지능과 비용의 균형용 모델로 소개한다. 가장 어려운 작업에는 GPT-6 Astra를 권한다. B1에서 Sol을 고른 사용자가 그런 작업을 설명하면 한 줄로 알린다.
- 컨텍스트 1.05M 토큰, 최대 출력 128K 토큰, 지식 컷오프 2026-04-30 (모델 페이지 기준).
- reasoning effort는 `low`, `medium`, `high`, `xhigh`, `max`를 받고, 생략하면 `medium`이다. `none`과 `minimal`은 지원하지 않는다.
- reasoning effort가 `none`이 아니면 `temperature`, `top_p`, `top_logprobs`를 빼야 한다. Sol은 `none`을 받지 않으므로 항상 뺀다.
- Chat Completions 요청은 받지만 함수 호출은 Responses API에서만 된다.
- `reasoning.context: "all_turns"`로 이전 턴의 호환되는 reasoning을 다시 쓸 수 있다. 값은 `auto`, `current_turn`, `all_turns`이다.
- 이전 버전 `gpt-6-sol`은 `none`을 받았다. `gpt-6-sol`에서 옮길 때 effort가 `none`이었으면 `low`로 바꾼다.
- Fast mode에서 EU 데이터 위치를 지원하고, Ultrafast mode는 US·EU 데이터 위치와 global 처리를 지원한다(Astra는 EU를 지원하지 않는다).

## 결정 질문

[gpt-6-astra.md](gpt-6-astra.md)의 M1~M6을 같은 조건으로 쓰고, 아래를 더한다.

| ID | 조건 | 질문 | 종류 |
|---|---|---|---|
| M7 | API·에이전트 + A2=멀티턴 또는 에이전트 | 턴이 바뀌어도 목표가 대체로 같은가요? (같음 → 이전 reasoning 재사용 / 턴마다 바뀜) | API·에이전트 |

M7은 프롬프트 문구가 아니라 실행 설정 권고로 반영한다.

## 프롬프트 반영

[gpt-6-astra.md](gpt-6-astra.md)의 P1~P6을 같은 조건으로 쓴다. Sol 전용 스니펫은 없다.

## 제거 검토

[gpt-6-astra.md](gpt-6-astra.md)의 목록을 그대로 쓰고, 다음을 더한다.

- `gpt-6-sol`의 `reasoning_effort: "none"`을 전제로 한 Chat Completions 함수 호출. GPT-6.1 Sol에서는 Responses로 옮긴다.

## 실행 설정 권고

[gpt-6-astra.md](gpt-6-astra.md)의 실행 설정 권고를 쓰되, 다음이 다르다.

- `reasoning.effort`: 기본은 `medium`이다. GPT-5.6 Sol 문서는 `medium`을 균형 잡힌 출발점으로, `low`를 품질이 유지될 때의 지연 민감 작업용으로, `high`·`xhigh`는 평가에서 의미 있는 향상이 확인될 때만 권한다.
- `reasoning.context`(M7): 목표가 턴마다 대체로 같으면 `all_turns`를 쓴다. 목표가 자주 바뀌면 오래된 reasoning이 토큰과 지연을 늘리고 예전 접근에 묶을 수 있으므로 `current_turn`을 쓴다(GPT-5.6 Sol 문서). `store: false`로 `all_turns`를 쓰면 reasoning 항목만이 아니라 모든 출력 항목을 다시 보내야 한다.
- 데이터 위치: EU가 필요하면 Fast mode를 쓸 수 있다.

```yaml
model: gpt-6.1-sol
reasoning:
  effort: <low|medium|high|xhigh|max>   # 생략 시 medium
  context: <all_turns|current_turn>      # M7
text:
  verbosity: <low|medium|high>
max_output_tokens: <값>                  # reasoning 포함
```

## 검수 항목

- [ ] [gpt-6-astra.md](gpt-6-astra.md)의 검수 항목을 통과했다
- [ ] Astra 스니펫을 넣었다면 Sol에서 평가하라는 안내가 "다음 단계"에 있다
- [ ] `all_turns`를 권고했다면 `store: false`일 때 모든 출력 항목을 다시 보내라는 안내가 있다
