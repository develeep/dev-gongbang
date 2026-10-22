# Claude Sonnet 5 가이드

출처: https://platform.claude.com/docs/ko/build-with-claude/prompt-engineering/prompting-claude-sonnet-5
확인일: 2026-10-01 (출처 문서와 대조)
각 스니펫 아래에 공식 문서의 영어 원문을 둔다. B2=영어이면 원문을 바탕으로 쓰고, 그 외 언어이면 한국어 스니펫을 바탕으로 쓴다. Sonnet 5.5는 이 파일이 아니라 [sonnet-5-5.md](sonnet-5-5.md)를 쓴다.

## 목차
- 특성 요약
- 결정 질문
- 프롬프트 반영
- 제거 검토
- 실행 설정 권고
- 검수 항목

## 특성 요약

- 응답 길이를 작업 복잡도에 맞춰 스스로 조절한다.
- **지시를 문자 그대로 해석한다.** 특히 낮은 effort에서 그렇다. 한 항목에 대한 지시를 다른 항목으로 일반화하지 않고, 요청하지 않은 것을 추론하지 않는다. 적용 범위를 명시해야 한다.
- effort를 엄격하게 따른다. `low`와 `medium`에서는 요청 범위만 하므로, 중간 난이도 작업에서 사고가 부족할 수 있다.
- 적응형 사고가 **기본으로 켜져 있다**(`thinking`을 생략해도 켜짐). 수동 `budget_tokens`는 400 오류가 난다.
- Sonnet 4.6보다 도구를 적극적으로 쓴다. 사고를 끄면 도구 사용과 검색이 줄어든다.
- 긴 작업 중에도 진행 보고를 잘 한다.
- `temperature`, `top_p`, `top_k`를 기본값이 아닌 값으로 주면 400 오류가 난다.
- 토크나이저가 바뀌어 같은 텍스트가 약 30% 더 많은 토큰이 된다.
- 개방형 프론트엔드 요청에서는 고정된 하우스 스타일로 수렴한다.
- 대략적인 대응 관계: Sonnet 5의 `medium`이 Sonnet 4.6의 `high`, Sonnet 5의 `high`가 Sonnet 4.6의 `max`와 비슷하다.

## 결정 질문

| ID | 조건 | 질문 | 종류 |
|---|---|---|---|
| M1 | 전체 | 서식이나 규칙이 적용될 범위를 알려 주세요. (전체 섹션·전체 응답 / 특정 부분만) | 전체 |
| M2 | API·단발 | 장황함을 줄일까요? 원하는 간결함을 보여 주는 좋은 응답 예시가 있나요? | API·단발 |
| M3 | A3=속도 또는 비용 | low effort를 유지해야 하나요? 다단계 추론이 필요한 작업인가요? | API·에이전트 |
| M4 | 사고를 끄고 도구 사용 | 사고를 끄고 쓰나요? 그렇다면 도구를 언제 쓰라고 명시할까요? | 에이전트·API |
| M5 | 톤이 중요한 제품 | 따뜻하거나 대화체인 목소리가 필요한가요? 구체적인 톤 설명을 주세요. | API |
| M6 | C15=프론트엔드 UI 생성 | 디자인 방향을 구체적으로 줄 수 있나요? (사양 제공 / 먼저 4가지 방향을 제안받아 선택) | 전체 |
| M7 | 코드 리뷰 | 리뷰 뒤에 별도의 검증·필터 단계가 있나요? | 에이전트 |
| M8 | 대화형 코딩 | 작업, 의도, 제약을 첫 턴에 모두 명시할 수 있나요? | 에이전트 |
| M9 | 적응형 사고 과다 | 큰 시스템 프롬프트에서 사고가 너무 자주 일어나는 것을 줄일까요? | API |

## 프롬프트 반영

**P1. 범위 명시** (M1) 규칙마다 적용 범위를 문장에 직접 쓴다. 예: "이 서식을 첫 섹션뿐 아니라 모든 섹션에 적용한다." Sonnet 5는 명시하지 않은 범위로 넓혀 적용하지 않는다.

**P2. 간결성** (M2=예)
```
간결하고 초점이 분명하게 응답한다. 꼭 필요하지 않은 맥락은 빼고 예시는 최소한으로 쓴다.
```
원문:
```text
Provide concise, focused responses. Skip non-essential context, and keep examples minimal.
```
사용자가 좋은 응답 예시를 주면 `<examples>`에 넣는다. 긍정 예시가 금지 지시보다 효과적이다.

**P3. low effort에서의 추론 유도** (M3=low 유지 + 다단계)
```
이 작업은 여러 단계의 추론이 필요하다. 응답하기 전에 문제를 신중히 생각한다.
```
원문:
```text
This task involves multistep reasoning. Think carefully through the problem before responding.
```
low를 유지할 필요가 없으면 프롬프트 대신 effort를 `high`나 `xhigh`로 올리라고 권고한다.

**P4. 사고 과다 억제** (M9=예)
```
사고는 지연 시간을 늘리므로 답의 품질을 의미 있게 높일 때만 한다. 보통은 여러 단계의 추론이 필요한 문제에 해당한다. 애매하면 바로 답한다.
```
원문:
```text
Thinking adds latency and should only be used when it will meaningfully improve answer quality, typically for problems that require multistep reasoning. When in doubt, respond directly.
```

**P5. 도구 사용 유도** (M4=예) 도구마다 왜, 언제 써야 하는지 사용자에게 받아 명시한다. 예: "최신 정보가 필요한 질문에는 답하기 전에 <검색 도구>로 확인한다. 학습 데이터 이후에 바뀌었을 수 있기 때문이다."

**P6. 톤** (M5) 사용자가 준 톤 설명을 쓴다. 예: "따뜻하고 협력적인 어조를 쓰고, 답하기 전에 사용자가 제시한 관점을 먼저 받아 준다." 문체의 다양성은 temperature가 아니라 지시로 만든다.

**P7. 프론트엔드** (M6)
- 사양 제공: 사용자가 준 팔레트(hex), 서체, 레이아웃, radius, 모션 수치를 그대로 명시한다. "그 색은 쓰지 마"나 "깔끔하게" 같은 일반 지시는 다른 고정 팔레트로 옮겨 갈 뿐이다.
- 방향 제안:
```
만들기 전에 이 요청에 맞는 서로 다른 시각적 방향 4가지를 제안한다(각각 배경 hex, 강조색 hex, 서체, 한 줄 근거). 사용자에게 하나를 고르게 하고, 고른 방향만 구현한다.
```
원문:
```text
Before building, propose 4 distinct visual directions tailored to this brief (each as: bg hex / accent hex / typeface, plus a one-line rationale). Ask the user to pick one, then implement only that direction.
```
- 공통으로 흔한 AI 기본 미감을 피하는 지시를 넣는다: Inter/Roboto/Arial/시스템 폰트, 흰 배경이나 어두운 배경의 보라 그라디언트, 예측 가능한 레이아웃. 맥락에 맞는 고유한 서체, 일관된 색 테마, 마이크로 인터랙션을 쓰게 한다.

**P8. 코드 리뷰 커버리지** (M7=예)
```
확신이 없거나 심각도가 낮은 것까지 발견한 문제를 모두 보고한다. 이 단계에서는 중요도나 확신도로 거르지 않는다. 걸러내는 일은 별도의 검증 단계가 한다. 이 단계의 목표는 커버리지다. 실제 버그를 조용히 빠뜨리는 것보다 나중에 걸러질 발견을 보고하는 편이 낫다. 발견마다 확신도와 예상 심각도를 적는다.
```
원문:
```text
Report every issue you find, including ones you are uncertain about or consider low-severity. Do not filter for importance or confidence at this stage - a separate verification step will do that. Your goal here is coverage: it is better to surface a finding that later gets filtered out than to silently drop a real bug. For each finding, include your confidence level and an estimated severity so a downstream filter can rank them.
```
M7=아니오면 구체적인 기준을 사용자에게 받는다. 예: "잘못된 동작, 테스트 실패, 오해를 부르는 결과를 낼 수 있는 버그는 모두 보고하고, 순수한 스타일이나 이름 취향만 뺀다."

**P9. 대화형 코딩** (M8=예) 첫 user 턴 템플릿에 작업, 의도, 제약을 모두 담는 섹션을 만든다. 여러 턴에 걸쳐 조금씩 주는 모호한 지시는 토큰 효율과 성능을 떨어뜨린다.

## 제거 검토

- "도구 호출 3번마다 진행 상황을 요약하라" 같은 진행 보고 강제 스캐폴딩
- `temperature`, `top_p`, `top_k` 설정. 400 오류가 난다.
- `budget_tokens`를 쓰는 수동 확장 사고. 400 오류가 난다.
- "심각한 것만 보고", "보수적으로" 같은 리뷰 기준 (P8 참고)
- "그 색은 쓰지 마" 같은 일반적인 디자인 금지 지시

## 실행 설정 권고

- `output_config.effort`: 기본값 `high`. 가장 어려운 코딩과 에이전트 작업은 `xhigh`, 비용에 민감하면 `medium`, 짧고 범위가 정해진 작업이나 지연 시간에 민감한 작업은 `low`. 벤치마크할 때는 effort 이름이 아니라 관찰된 사고 길이로 맞춘다.
- `thinking`: 생략하면 적응형으로 켜진다. 끄려면 `{type: "disabled"}`. Sonnet 4.6에서 사고를 끄고 쓰던 워크로드는 낮은 effort로 켠 상태를 먼저 시도한다.
- `max_tokens`: 사고와 응답을 합친 한도다. `high` 이상이면 넉넉하게 잡는다. 토크나이저 때문에 Sonnet 4.6 기준 값에서 약 30% 늘린다. 응답이 잘리면(`stop_reason: "max_tokens"`) 값을 올리거나 `medium`으로 낮춘다.
- 샘플링 파라미터는 모두 제거한다.
- 대화형 코딩 제품은 `xhigh` 또는 `high`에 자동 모드 같은 자율 기능을 더한다.
- 컴퓨터 사용: 1080p가 균형이 좋고, 비용에 민감하면 720p나 1366×768을 쓴다.

## 검수 항목

- [ ] 규칙마다 적용 범위가 명시되어 있다
- [ ] temperature, top_p, top_k, budget_tokens가 없다
- [ ] max_tokens 권고에 사고 여유분과 토크나이저 증가분이 반영됐다
