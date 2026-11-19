# 멀티에이전트 개발 규칙

메인 세션(오케스트레이터)이 따르는 규칙입니다. task 서브에이전트는 이 파일을 받지 않습니다. Paseo나 Orca 워커로 띄운 omp 세션은 메인 세션이므로 이 규칙을 따릅니다.

## 개발 단계

기획서부터 PR까지 아래 순서로 진행합니다. 사용자가 `/skill:run-flow`를 실행하면 run-flow 스킬이 이 순서를 이어서 진행합니다. 단계를 하나씩 진행할 때는 단계가 끝나면 결과물 위치와 다음 단계를 알립니다.

| 순서 | 단계 | 스킬 | 결과물 | 사용자 확인 |
|---|---|---|---|---|
| 1 | 요구사항 정리 | analyzing-requirements | 요구사항·개발 범위 문서 | 저장 위치 |
| 2 | 문제 구체화 | framing-problems | 구체화 기록 | 기록 확정 |
| 3 | 작업 지시서 | set-brief | brief | 초안과 게시 위치 |
| 4 | 티켓 분할 | set-ticket | 티켓 | 크기와 순서 승인 |
| 5 | 티켓 구현 | run-ticket | 코드, 완료 기록 | 병렬 실행 계획 |
| 6 | 규칙 검사·교차 리뷰 | run-ticket의 리뷰 단계 | 리뷰 보고 | 머지 여부 결정 |
| 7 | PR | doc-writer가 본문 작성, run-flow가 PR 생성 | PR | PR 본문 |

여러 티켓을 한 번에 실행할 때 함께 시작할 수 있는 티켓이 둘 이상이면 run-ticket이 Paseo나 Orca 워커로 티켓마다 worktree를 나눠 병렬로 실행합니다. 아니면 서브에이전트로 차례로 실행합니다.

## 위임

에이전트 하나에는 목적 하나만 맡깁니다. 서브에이전트, Paseo 워커, Orca 워커 모두 같습니다. 목적 하나는 산출물 하나와 그 산출물을 완성하는 데 필요한 일 전부입니다. 초안의 냉독 검증, 구현의 완료 기준 확인, 실패한 티켓의 원인 정리처럼 자기 작업을 완성하고 검증하는 일은 같은 에이전트에 둡니다. 나누면 맥락을 잃어 완성도가 떨어집니다. 구현과 독립 리뷰, 리뷰 스킬 둘처럼 산출물이 다르면 에이전트를 둘 띄웁니다. 한 에이전트의 결과에 여러 산출물이 섞이면 메인 세션이 그 결과를 리뷰하거나 버그와 AI slop을 찾기 어렵습니다.

| 작업 | 에이전트 |
|---|---|
| 코드 탐색·검색 | scout |
| brief 초안 작성 (set-brief의 입력 수집, 초안, 냉독 검증) | brief-writer |
| brief 냉독 검증 | implementer |
| 명세가 분명한 티켓 구현 | implementer |
| implementer가 2회 실패한 티켓, 대규모 리팩터링, 원인을 모르는 실패의 디버깅 | hard-implementer |
| 테스트 작성·실행 | test-writer |
| UI·화면 검증 | ui-checker |
| 교차 리뷰 | reviewer |
| 코드 리뷰 스킬이 띄우는 하위 리뷰 | task |
| 보안·인증·결제 등 핵심 로직 리뷰 | security-reviewer |
| PR 설명 | doc-writer |

티켓이 처음부터 hard-implementer 행에 해당하면 implementer를 거치지 않고 바로 맡깁니다. run-ticket의 차례 실행에서 티켓마다 띄우는 서브에이전트도 이 표의 구현 에이전트로 띄웁니다.

구현 워커(run-ticket의 2, 3, 4단계를 지시받은 Paseo나 Orca 워커)는 구현과 테스트를 implementer와 test-writer에 맡기지 않고 직접 합니다. 워커와 implementer의 모델이 같아서, 맡기면 같은 문서를 두 번 읽고 넘기지 않은 규칙이 빠집니다. 화면 검증은 ui-checker에 맡깁니다.

reviewer는 다른 회사 모델이므로 교차 리뷰에만 씁니다. 코드 리뷰 스킬의 하위 리뷰까지 맡기면 같은 모델이 같은 diff를 두 번 봅니다.

## 넘기는 것

- 구현·테스트·UI 에이전트에는 대화 기록 대신 brief와 티켓 하나의 전문, 레포 규칙 파일 경로, 검증 명령, 같은 brief의 done 티켓 `## 산출물`을 넘깁니다. 서브에이전트는 `AGENTS.md`를 받지 않으므로 넘기지 않은 규칙은 모릅니다. brief를 프롬프트 맨 앞에 두면 같은 brief로 여러 티켓을 맡길 때 캐시를 다시 씁니다.
- brief-writer에는 냉독 검증을 implementer로 띄우라고 함께 알립니다.
- 커밋 메시지는 메인 세션이 레포 커밋 규칙대로 씁니다.
- 리뷰 에이전트에는 리뷰할 diff 범위와 brief를 넘깁니다. diff가 272K 토큰(약 1MB)을 넘으면 디렉터리별로 나눠 맡깁니다. GPT는 입력이 272K 토큰을 넘으면 입력 단가가 2배, 출력 단가가 1.5배가 됩니다. 나눌 때는 디렉터리를 넘는 공유 타입, API, 설정을 리뷰마다 함께 넘기고, 디렉터리 경계를 넘는 결함은 메인 세션이 봅니다.
- doc-writer에는 diff 전문 대신 brief, 변경 파일 목록(`git diff --stat`), 티켓 완료 기록, 리뷰 기록을 넘깁니다.

## 실패했을 때

실패는 완료 기준이나 테스트를 통과하지 못했다는 보고입니다.

1. implementer가 실패하면 그 실패 보고를 함께 넘겨 한 번 더 맡깁니다. 실패 원인이 티켓의 모호함이나 크기면 다시 맡기지 않고 4번처럼 멈춥니다.
2. 같은 티켓에서 2회 실패하면 앞선 실패 보고를 모두 넘겨 hard-implementer에 맡깁니다. 이어 받은 흐름에 앞선 실패 기록이 있으면 그 횟수부터 셉니다.
3. 구현 워커는 직접 구현해 실패하면 실패 보고를 넘겨 바로 hard-implementer에 맡깁니다.
4. hard-implementer도 통과시키지 못하면 더 올리지 않고 멈춥니다. 실패 보고를 보여 주고 `/skill:set-ticket`으로 티켓을 다시 나누자고 제안합니다.

## 워커

Paseo나 Orca 워커는 서브에이전트로 할 수 없는 일에만 씁니다. 둘 다 쓸 수 있으면 Paseo를 씁니다.

- 여러 티켓을 worktree를 나눠 병렬로 실행할 때. run-ticket의 "병렬 실행"을 따릅니다. 워커는 티켓 하나를 직접 구현하므로 implementer와 같은 모델과 Effort를 씁니다.
- 다른 에이전트(Codex, Claude Code)에게 리뷰나 작업을 맡길 때
- 사용자가 작업 과정을 Paseo나 Orca에서 보거나 워커에게 직접 말을 걸어야 할 때

메인 세션이 Claude면 교차 리뷰는 reviewer가 맡고, reviewer가 같은 회사 모델로 넘어갔을 때만 워커에 맡깁니다.

### Paseo

- 티켓 구현 워커는 `ticket-worker` 프로필로 띄웁니다. 프로필이 없으면 omp provider의 `anthropic/claude-opus-5-5`, thinking `medium`으로 띄웁니다.
- 교차 리뷰 워커는 `cross-review` 프로필로 띄웁니다. 프로필이 없으면 omp provider의 `openai-codex/gpt-6.2-sol`, thinking `high`로 띄웁니다. 메인 세션이 Claude가 아니면 `anthropic/claude-opus-5-5`, thinking `medium`으로 띄웁니다.

### Orca

- 티켓 구현 워커는 `--model @worker`로 띄웁니다.
- 교차 리뷰를 Claude Code 워커에 맡길 때는 `--model claude-opus-5-5 --effort medium`으로 띄웁니다. 메인 세션이 Claude가 아닐 때만 해당합니다. 메인 세션이 Claude면 Codex 워커를 `--model gpt-6.2-sol --effort high`로 띄워 맡깁니다. Opus 워커는 같은 회사 모델이라 교차 리뷰가 되지 않습니다.
