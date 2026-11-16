# 멀티에이전트 개발 규칙

메인 세션(오케스트레이터)이 따르는 규칙입니다. task 서브에이전트는 이 파일을 받지 않습니다. Orca 워커로 띄운 omp 세션은 메인 세션이므로 이 규칙을 따릅니다.

## 개발 단계

기획서부터 PR까지 아래 순서로 진행합니다. 사용자가 `/skill:run-flow`를 실행하면 run-flow 스킬이 이 순서를 이어서 진행합니다. 단계를 하나씩 진행할 때는 단계가 끝나면 결과물 위치와 다음 단계를 알립니다.

| 순서 | 단계 | 스킬 | 결과물 | 사용자 확인 |
|---|---|---|---|---|
| 1 | 요구사항 정리 | analyzing-requirements | 요구사항·개발 범위 문서 | 저장 위치 |
| 2 | 문제 구체화 | framing-problems | 구체화 기록 | 기록 확정 |
| 3 | 작업 지시서 | set-brief | brief | 초안과 게시 위치 |
| 4 | 티켓 분할 | set-ticket | 티켓 | 크기와 순서 승인 |
| 5 | 티켓 구현 | run-ticket | 코드, 완료 기록 | Orca 실행 계획 |
| 6 | 규칙 검사·교차 리뷰 | run-ticket 5단계 | 리뷰 보고 | 머지 여부 결정 |
| 7 | PR | doc-writer가 본문 작성, run-flow가 PR 생성 | PR | |

여러 티켓을 한 번에 실행하면 run-ticket이 Orca 워커로 티켓마다 worktree를 나눠 병렬로 실행합니다.

## 위임

| 작업 | 에이전트 |
|---|---|
| 코드 탐색·검색 | scout |
| 명세가 분명한 티켓 구현 | implementer |
| implementer가 2회 실패한 티켓, 대규모 리팩터링, 원인을 모르는 실패의 디버깅 | hard-implementer |
| 테스트 작성·실행 | test-writer |
| UI·화면 검증 | ui-checker |
| 교차 리뷰 | reviewer |
| 보안·인증·결제 등 핵심 로직 리뷰 | security-reviewer |
| PR 설명·커밋 메시지 | doc-writer |

## 넘기는 것

- 구현·테스트·UI 에이전트에는 대화 기록 대신 brief와 티켓 하나의 전문을 넘깁니다. brief를 프롬프트 맨 앞에 두면 같은 brief로 여러 티켓을 맡길 때 캐시를 다시 씁니다.
- 리뷰 에이전트에는 리뷰할 diff 범위와 brief를 넘깁니다. diff가 272K 토큰(약 1MB)을 넘으면 디렉터리별로 나눠 맡깁니다. GPT는 입력이 272K 토큰을 넘으면 단가가 2배가 됩니다.

## 실패했을 때

실패는 완료 기준이나 테스트를 통과하지 못했다는 보고입니다.

1. implementer가 같은 티켓에서 2회 실패하면 앞선 실패 보고를 함께 넘겨 hard-implementer에 맡깁니다.
2. hard-implementer도 통과시키지 못하면 더 올리지 않고 멈춥니다. 실패 보고를 보여 주고 `/skill:set-ticket`으로 티켓을 다시 나누자고 제안합니다.

## Orca

Orca 워커는 서브에이전트로 할 수 없는 일에만 씁니다.

- 여러 티켓을 worktree를 나눠 병렬로 실행할 때. run-ticket의 "Orca 병렬 실행"을 따릅니다.
- 다른 에이전트(Codex, Claude Code)에게 리뷰나 작업을 맡길 때
- 사용자가 작업 과정을 Orca에서 보거나 워커에게 직접 말을 걸어야 할 때
