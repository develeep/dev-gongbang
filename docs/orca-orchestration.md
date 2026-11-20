<p align="right"><b>한국어</b> · <a href="./en/orca-orchestration.md">English</a></p>

[README](../README.md) › [문서](README.md) › Orca 오케스트레이션 설정

# Orca 오케스트레이션 설정

[Orca](https://orca.dev/docs/cli/orchestration)에서 run-ticket이 여러 티켓을 워커로 병렬 실행하고 교차 리뷰를 다른 회사 모델의 워커에 맡기도록 설정하는 방법을 설명합니다. Orca 방식은 brief 하나에 Orca Run 하나를 만들고, 티켓마다 현재 브랜치에서 갈라진 child worktree에 워커를 띄웁니다. 조정자 세션은 막힘 관계 순서와 머지를 맡고, 워커가 끝나거나 물으면 Orca가 조정자 세션을 깨웁니다. run-ticket은 Orca를 먼저 쓰고, Orca를 쓸 수 없을 때 [Paseo](paseo-orchestration.md)를 씁니다. 이 문서는 Orca 1.4.265를 기준으로 합니다.

## 목차

- [설치](#설치)
- [도구 고르는 순서](#도구-고르는-순서)
- [Orca 오케스트레이션 방식](#orca-오케스트레이션-방식)
- [두 방식의 차이](#두-방식의-차이)
- [확인하기](#확인하기)
- [알아 둘 점](#알아-둘-점)

## 설치

1. **Orca 실행**: Orca 앱을 띄우고, 조정자 세션(run-ticket이나 run-flow를 실행할 세션)을 Orca의 터미널이나 채팅에서 엽니다. 다른 곳에서 열면 Orca가 워커 소식을 그 세션에 전하지 못합니다.
2. **CLI 확인**: 스킬은 Orca 실행 파일을 다음 순서로 고릅니다. 환경 변수 `ORCA_CLI_COMMAND`의 값(Orca가 WSL 세션에 넣어 줍니다), Linux에서 Orca 터미널 밖이면 `orca-ide`, 그 밖에는 `orca`입니다. Linux에서 맨 `orca`는 GNOME 화면 낭독기일 수 있으므로 직접 실행하지 않습니다.
3. **스킬 설치**: 아래 명령으로 Orca에 들어 있는 `orchestration`, `orca-cli` 스킬을 설치합니다. 감지한 에이전트(Claude Code, Codex, omp 등)의 스킬 폴더에 연결됩니다. Orca를 업데이트한 뒤에는 `skills update`로 스킬도 맞춥니다.

   ```bash
   <Orca CLI> skills install
   ```

4. **omp 위임 규칙**: 구현 워커의 모델은 omp 역할 `worker`를 씁니다. [omp 멀티에이전트 설정](omp-orchestration.md)대로 `extras/omp/`를 설치합니다.
5. **교차 리뷰 워커(선택)**: reviewer 서브에이전트를 쓸 수 없을 때를 위해 Codex와 Claude Code CLI를 Orca 호스트에 설치해 둡니다. `<Orca CLI> agent installed`에 보이는 에이전트만 워커로 띄울 수 있습니다.

## 도구 고르는 순서

run-ticket은 여러 티켓을 실행할 때 워커 도구를 다음 순서로 고르고, 처음 되는 것을 씁니다. 사용자가 도구를 정해 주면 그것을 쓰고, 이어 받는 실행은 기록에 남은 식별자의 도구를 씁니다.

1. Orca: `orchestration` 스킬을 불러올 수 있고, 그 스킬이 고른 실행 파일로 `status`가 성공할 때
2. Paseo: 세션에 Paseo의 워크스페이스·에이전트 관리 도구가 있거나 `paseo ls`가 성공할 때
3. 둘 다 없으면 서브에이전트로 차례 실행

교차 리뷰는 에이전트 규칙이 정한 에이전트(omp 설정에서는 reviewer), 이 worktree에 띄운 다른 회사 모델의 Orca 워커, Paseo로 띄운 에이전트 순서로 맡깁니다. 셋 다 없으면 건너뜁니다.

## Orca 오케스트레이션 방식

조정자 세션은 run-ticket의 "병렬 실행" 절차를 따르고, 워커를 다루는 일은 Orca 명령으로 합니다. 명령 인자는 실행 중인 Orca의 안내(`<Orca CLI> skills get orchestration`)와 `--help`가 기준입니다.

1. **Run 만들기**: brief 제목을 목표로 `orchestration run-create`를 실행하고 Run ID를 기록합니다. run-flow에서는 상태 파일의 `- Orca Run:`에 적습니다.
2. **워커 띄우기**: 막는 티켓이 모두 머지된 티켓마다 `orchestration worker-start`로 Task와 워커를 함께 만듭니다. 워커는 조정자 worktree 아래 새 worktree(`--worktree new-child`)에서, 현재 브랜치의 로컬 ref(`--base-branch`)를 기준으로 시작합니다. 구현 워커는 조정자와 같은 에이전트로 `--model @worker`를 붙여 띄웁니다. 같은 때에 띄울 워커(기본 3개까지)는 셸 명령 하나에서 함께 시작합니다.
3. **기다리기**: 워커를 띄운 뒤 조정자는 턴을 끝내고, Orca가 메시지로 깨웁니다. 상태를 되풀이해 조회하지 않습니다.
   - `worker_done`: 결과가 성공이고 보고한 커밋이 티켓 브랜치에 있으면 머지와 통합 검증으로 넘어갑니다. 그 밖에는 실패로 처리합니다.
   - `question`: 워커가 `ask`로 물은 것입니다. brief와 티켓으로 답할 수 있으면 `reply`로 답하고, 아니면 사용자에게 물어 전합니다.
   - `escalation`: 워커가 보고 없이 멈췄거나, 사라졌거나, 권한을 요청한 것입니다. 범위 밖 권한 요청은 `deny`로 거절하고, 범위 안의 것은 사용자에게 묻습니다.
4. **리베이스 요청**: 머지가 충돌하면 같은 워커에 `orchestration send --to dispatch:<Dispatch ID>`로 보냅니다. 끝난 워커에게 보내도 후속 Task로 이어집니다.
5. **정리**: 머지한 뒤 `orchestration worker-release`로 워커를 놓아주고 `worktree rm --delete-branch`로 worktree와 머지된 브랜치를 지웁니다. 실패한 티켓의 워커와 worktree는 사용자가 볼 수 있게 남깁니다.
6. **이어 받기**: 세션이 끊겼으면 기록한 Run ID로 `orchestration run-use`를 실행하고, `task-list`, `worker-list`, `worker-read`로 티켓별 상태와 마지막 보고를 확인한 뒤 이어 갑니다.

교차 리뷰를 워커에 맡길 때는 구현한 모델이 Claude면 Codex를, 아니면 Claude Code를 조정자와 같은 worktree(`--worktree current`)에 띄우고, 파일은 고치지 말고 지적만 보고하게 합니다. 모델과 effort는 `extras/omp/AGENTS.md`의 "워커" 절이 정합니다.

자세한 절차는 [run-ticket](skills/run-ticket.md#여러-티켓-실행)에 있습니다.

## 두 방식의 차이

머지, 통합 검증, 완료 기록, 교차 리뷰, 통합 리뷰는 두 방식이 같습니다.

| 하는 일 | Orca | Paseo |
|---|---|---|
| 실행 단위 | brief마다 Run 하나, 워커를 띄울 때 티켓마다 Task 하나 | 대응하는 개념이 없습니다. 조정자 세션이 막힘 관계 순서를 직접 지킵니다 |
| 워커 | 현재 브랜치(로컬 ref)에서 갈라진 child worktree의 Orca 워커 | 현재 브랜치(로컬 ref)에서 갈라진 worktree 격리 워크스페이스와 그 안의 에이전트 하나 |
| 워커 모델 | 에이전트 규칙의 `--model @worker` | 저장된 에이전트 프로필의 설명을 읽어 고릅니다. 없으면 에이전트 규칙, 그것도 없으면 조정자 세션과 같은 provider·모델 |
| 끝남 감지 | 조정자가 턴을 끝내면 Orca가 `worker_done`, `question`, `escalation` 메시지로 깨웁니다 | 완료 알림을 기다립니다. Paseo가 띄운 세션이 아니면 `paseo wait`로 기다리고 `paseo logs`로 결과를 읽습니다 |
| 질문·리베이스 요청 | `reply`로 답하고, 같은 Dispatch에 `send` | 같은 에이전트에 후속 프롬프트 |
| 이어 받기 | 기록한 Run ID로 `run-use`, `worker-list` | 기록한 티켓별 워크스페이스 ID, 에이전트 ID, 브랜치 |
| 정리 | `worker-release` 후 `worktree rm --delete-branch` | 워크스페이스를 archive(Paseo가 worktree 제거)한 뒤 브랜치 삭제 |

## 확인하기

- `<Orca CLI> status`에 `runtimeState: ready`가 나오는지
- `<Orca CLI> skills get orchestration`이 안내를 출력하는지. 모르는 명령이라고 나오면 Orca를 업데이트합니다.
- `<Orca CLI> orchestration worker-start --help`에 `--base-branch`와 `--model`이 있는지
- 조정자 세션에서 `<Orca CLI> orchestration run-current`가 오류 없이 끝나는지. Run이 없으면 `runId=none`이 나옵니다.

## 알아 둘 점

- **워커의 worktree는 커밋된 내용만 봅니다.** brief와 티켓을 커밋하지 않고 시작하면 워커가 읽지 못하므로 run-ticket이 작업 트리가 깨끗한지 먼저 확인합니다.
- **worktree의 기준은 로컬 ref입니다.** 기준을 빼거나 원격 ref를 주면 push하지 않은 커밋(흐름 문서, 앞서 머지한 티켓)이 빠집니다.
- **조용함은 끝남이 아닙니다.** 응답이 없거나 시간이 초과돼도 워커가 끝났다고 보지 않고, 다시 띄우지 않습니다. 같은 티켓을 두 번 구현하게 됩니다.
- **시작 재시도에는 한도가 있습니다.** 같은 Task의 시작이 세 번 실패하면 Orca가 그 Task를 막습니다. 새 Run이나 Task로 돌아가지 않고 그 티켓을 실패로 보고합니다.
- **새 worktree의 워커는 끝나도 열려 있습니다.** 머지한 뒤 `worker-release`로 놓아줍니다. 사용자가 워커와 계속 대화하려면 `--keep-open`으로 띄웁니다.
- **명령은 Orca 버전에 따라 바뀝니다.** 스킬은 명령 이름만 적고 인자는 실행 중인 Orca의 안내와 `--help`를 따르게 합니다.

---

[문서 목록](README.md) · [README](../README.md)
