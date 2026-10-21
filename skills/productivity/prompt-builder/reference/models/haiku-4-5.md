# Claude Haiku 4.5 가이드

Haiku 4.5에는 모델 전용 프롬프팅 문서가 없다. 공통 best practice 문서가 적용 대상 모델로 Haiku 4.5를 포함하므로 공통 원칙을 그대로 쓰고, 이 파일에는 공통 원칙과 다른 API 차이와 공식 문서에 적힌 특성만 둔다.

출처:
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting
- https://platform.claude.com/docs/en/build-with-claude/extended-thinking
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
확인일: 2026-10-01 (출처 문서와 대조)

## 목차
- 특성 요약
- 결정 질문
- 프롬프트 반영
- 제거 검토
- 실행 설정 권고
- 검수 항목

## 특성 요약

- 사고는 **확장 사고만** 지원한다(`thinking: {type: "enabled", budget_tokens: N}`). 기본값은 꺼짐이다. `thinking: {type: "adaptive"}`는 400 오류가 난다.
- effort로 사고 깊이를 조절할 수 없다. 확장 사고만 쓰는 모델 중 effort를 지원하는 것은 Opus 4.5뿐이다. 사고 깊이는 `budget_tokens`로 정한다.
- 인터리브드 사고(도구 호출 사이의 사고)를 지원하지 않는다. `interleaved-thinking-2025-05-14` 헤더는 받아도 무시된다.
- 이전 턴의 사고 블록은 컨텍스트에서 제거된다(4.6 이후 모델은 유지하고 입력으로 과금한다).
- 마지막 assistant 턴 prefill을 받는다. prefill 중단은 Claude 4.6 모델부터 적용된다.
- 컨텍스트 인식이 있어서 대화 중 남은 컨텍스트 윈도우(토큰 예산)를 추적한다. 압축이나 외부 저장이 있다는 사실을 알려 주지 않으면 한도에 가까워질 때 작업을 일찍 마무리하려 할 수 있다.
- 공식 스킬 가이드는 Haiku를 빠르고 경제적인 모델로 분류하고, Opus에서 잘 되는 지시도 Haiku에는 더 자세한 안내가 필요할 수 있다고 본다.

## 결정 질문

| ID | 조건 | 질문 | 종류 |
|---|---|---|---|
| M1 | API·에이전트·단발 | 여러 단계의 추론이 필요한 작업인가요? (확장 사고 켬 / 끔) | 전체 |
| M2 | C10=JSON 또는 분류 작업 | 출력 형식을 어떻게 강제하나요? (structured outputs·enum 도구 / prefill / 지시만) | API·단발 |
| M3 | 나중에 다른 모델로 옮길 가능성 | 이 프롬프트를 4.6 이후 모델(Sonnet 5.5 등)로 옮길 계획이 있나요? | 전체 |
| M4 | K7에 Haiku 포함 | Opus나 Sonnet에서 잘 되던 지시 중 Haiku에서 더 자세히 풀어 써야 할 단계가 있나요? | SKILL.md |

## 프롬프트 반영

**P1. 컨텍스트 한도 안내** (G10=예. 공통 원칙 G의 "컨텍스트 압축 안내"를 Haiku 4.5에서는 꼭 넣는다. 컨텍스트 인식 때문에 한도 근처에서 일찍 마무리하는 경향이 공식 문서에 적혀 있다.)
```
컨텍스트 윈도우는 한도에 가까워지면 자동으로 압축되므로, 멈춘 곳에서 계속 작업할 수 있다. 그러니 토큰 예산 때문에 작업을 일찍 멈추지 않는다. 한도에 가까워지면 컨텍스트가 새로 고쳐지기 전에 지금까지의 진행 상황과 상태를 메모리에 저장한다. 남은 컨텍스트와 관계없이 작업을 끝까지 마친다.
```
하네스가 압축 대신 외부 파일 저장을 쓰면 첫 문장을 그 방식에 맞게 바꾼다.

**P2. 형식 강제** (M2) M2=prefill이고 M3=예이면, prefill은 4.6 이후 모델에서 400 오류가 나므로 structured outputs나 지시로 바꾸는 편이 이전에 유리하다고 알리고 고르게 한다. M3=아니오이면 prefill을 그대로 쓸 수 있다.

**P3. 자세한 단계** (M4=예) 사용자가 지목한 단계를 번호 단계로 풀어 쓴다. 단계 내용은 사용자에게 받는다.

## 제거 검토

- `thinking: {type: "adaptive"}` 설정. 400 오류가 난다.
- `output_config.effort` 설정. Haiku 4.5는 effort를 지원하지 않는다.
- 다른 모델용 가이드에서 가져온 "effort를 낮춰라", "사고는 항상 켜져 있다" 같은 전제를 둔 문구

## 실행 설정 권고

- `model`: `claude-haiku-4-5`
- `output_config.effort`: 쓰지 않는다.
- `thinking`: M1=끔이면 생략한다(기본 꺼짐). M1=켬이면 `{type: "enabled", budget_tokens: N}`을 쓴다.
  - `budget_tokens`는 최소 1,024이고 `max_tokens`보다 작아야 한다.
  - 시작값: 단순한 작업은 1,024 근처에서 시작해 조금씩 올린다. 복잡한 작업은 16,000 이상에서 시작해 지연과 품질을 보며 조정한다.
  - 32,000을 넘는 예산은 연결 시간 초과를 피하려고 배치 처리로 보낸다.
  - 캐시를 쓰는 대화에서는 예산을 바꾸지 않는다. 바꾸면 캐시 중단점이 무효화된다.
- `max_tokens`: 사고 토큰도 여기에 포함되므로 사고 예산에 응답 길이를 더해 잡는다.
- 사용량 확인: 응답의 `usage.output_tokens_details.thinking_tokens`로 실제 사고 토큰을 본다.

## 검수 항목

- [ ] `adaptive` 사고와 effort 설정이 없다
- [ ] 확장 사고를 켰다면 `budget_tokens`가 1,024 이상이고 `max_tokens`보다 작다
- [ ] G10=예이면 P1 컨텍스트 한도 안내가 들어갔다
- [ ] prefill을 쓴다면 M3에서 이전 계획이 없다고 확인받았다
