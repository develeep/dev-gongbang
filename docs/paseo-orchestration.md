<p align="right"><b>한국어</b> · <a href="./en/paseo-orchestration.md">English</a></p>

[README](../README.md) › [문서](README.md) › Paseo 오케스트레이션 설정

# Paseo 오케스트레이션 설정

[Paseo](https://paseo.sh/docs)에서 run-ticket이 여러 티켓을 워커로 병렬 실행하도록 Paseo 도구, 예시 에이전트 프로필, 워크스페이스 스크립트를 설정하는 방법을 설명합니다. Paseo 방식은 티켓마다 현재 브랜치에서 갈라진 worktree 워크스페이스 하나와 그 안의 에이전트 하나를 띄우고, 조정자 세션이 막힘 관계 순서와 머지를 맡습니다. 이 문서를 읽으면 `extras/paseo/`의 파일을 설치하고, 워커 절차를 등록하고, 동작을 확인하고, Orca와 함께 쓸 수 있습니다.

Paseo 절차는 스킬 밖의 선택 설정입니다. run-ticket 스킬은 특정 워커 도구를 직접 다루지 않고, 사용자가 정해 준 워커 도구 절차나 레포·에이전트 규칙(CLAUDE.md, AGENTS.md)이 지정한 절차가 있고 그 사용 조건을 만족할 때만 여러 티켓을 병렬로 실행합니다. 병렬 워커는 기본 흐름이 아니라 이렇게 사용자가 지정하거나 등록할 때만 쓰는 선택 경로이고, 지정도 등록도 없으면 메인 세션이 티켓을 차례로 직접 실행합니다. 워커와 교차 리뷰의 모델은 이 저장소가 정하지 않고 사용자의 규칙, 저장된 프로필, 환경을 따릅니다. 매번 절차를 알려 주지 않으려면 Paseo를 설치한 뒤 Paseo 절차 문서 [`extras/paseo/worker-procedure.md`](../extras/paseo/worker-procedure.md)를 규칙 파일에 등록합니다.

## 목차

- [파일 구성](#파일-구성)
- [설치](#설치)
- [절차 등록](#절차-등록)
- [프로필](#프로필)
- [Paseo 오케스트레이션 방식](#paseo-오케스트레이션-방식)
- [Orca와 함께 쓰기](#orca와-함께-쓰기)
- [확인하기](#확인하기)
- [알아 둘 점](#알아-둘-점)
- [지운 프로필과 플레이북](#지운-프로필과-플레이북)

## 파일 구성

| 파일 | 설치 위치 | 역할 |
|---|---|---|
| [`extras/paseo/worker-procedure.md`](../extras/paseo/worker-procedure.md) | 조정자 세션이 읽음. 규칙 파일에 경로를 적습니다 | Paseo로 워커를 만들고, 기다리고, 끝을 판정하고, 이어 받고, 정리하는 절차와 교차 리뷰 워커를 띄우는 방법. 절 이름은 run-ticket `references/multi-ticket.md`의 "워커 도구 절차" 항목과 같습니다 |
| [`extras/paseo/register.md`](../extras/paseo/register.md) | 읽고 따라 함 | 규칙 파일에 붙일 등록 문구, 값을 자리 표시로 둔 워커 모델 줄, Orca 절차와 함께 지정하는 문구 |
| [`extras/paseo/config.json`](../extras/paseo/config.json) | `~/.paseo/config.json`에 합침 | Paseo 도구를 에이전트에 주는 설정(`daemon.mcp.injectIntoAgents`)과 provider·모델을 비운 예시 프로필 2개(`ticket-worker`, `cross-review`) |
| 레포 루트 [`paseo.json`](../paseo.json) | 이 레포에 있음 | 이 레포의 워크스페이스 스크립트 `check`(`python3 scripts/check.py`). 자기 레포에는 같은 형식으로 직접 만듭니다 |

## 설치

1. **Paseo 도구 켜기**: Settings → 호스트 → Agents에서 Enable Paseo tools를 켜거나, `~/.paseo/config.json`에 `daemon.mcp.injectIntoAgents: true`를 넣습니다. 켠 뒤 새 에이전트를 시작하거나 기존 에이전트를 다시 불러와야 도구를 받습니다.
2. **프로필(선택)**: `extras/paseo/config.json`의 `daemon.agentProfiles` 항목을 `~/.paseo/config.json`의 같은 키에 합치고, 각 프로필의 `provider`(필수)와 `model`(선택)을 자기 환경의 값으로 채운 뒤 `paseo reload`를 실행합니다. 기존 파일을 덮어쓰지 않습니다. 프로필은 데몬을 재시작하지 않아도 반영됩니다. Settings → 호스트 → Agents → Agent profiles에서 직접 만들어도 됩니다. 쓸 수 있는 provider는 `paseo provider ls`로, 모델은 `paseo provider models <provider>`로 확인합니다. `cross-review`에는 구현에 쓰는 모델과 다른 회사의 모델을 넣습니다. 프로필을 합치지 않아도 절차는 동작합니다(아래 [프로필](#프로필)).
3. **워크스페이스 스크립트**: 레포 루트에 `paseo.json`을 둡니다. 이 레포의 것은 다음과 같습니다.

   ```json
   {"scripts": {"check": {"command": "python3 scripts/check.py"}}}
   ```

   `paseo script ls`로 목록을 보고 `paseo script start check`로 실행합니다.

4. **절차 등록**: 아래 [절차 등록](#절차-등록)대로 규칙 파일에 Paseo 절차를 지정합니다.

## 절차 등록

자세한 방법은 [`extras/paseo/register.md`](../extras/paseo/register.md)에 있습니다.

1. **절차 문서의 경로를 정합니다.** 이 저장소를 클론해 두었으면 `<dev-gongbang 경로>/extras/paseo/worker-procedure.md`의 절대 경로를 씁니다. 팀이 함께 쓰는 레포면 `worker-procedure.md`를 그 레포에 복사해 커밋하고 레포 기준 경로를 씁니다.
2. **규칙 파일에 등록 문구를 붙입니다.** 모든 프로젝트에서 쓰려면 사용자 전역 규칙 파일(Claude Code는 `~/.claude/CLAUDE.md`, omp는 `~/.omp/agent/AGENTS.md` 등)에, 한 레포에서만 쓰려면 그 레포의 `CLAUDE.md`나 `AGENTS.md`에 넣습니다. 경로는 글로만 적고 `@<경로>`로 가져오지 않습니다.

   ```markdown
   ## 워커 도구 절차

   run-ticket의 워커 도구 절차는 Paseo 절차입니다. 여러 티켓을 병렬로 실행하거나 교차 리뷰를 워커에 맡길 때 `<worker-procedure.md 경로>`를 읽고 따릅니다.
   ```

3. **워커 모델을 정합니다(선택).** 쓸 프로필을 고정하거나 고정한 프로필이 없을 때의 모델을 정하려면 등록 문구 아래에 워커 모델 줄을 더합니다. 문구는 register.md의 "워커 모델 정하기"에 있고, 값은 자리 표시뿐이라 자기 환경의 것으로 채웁니다.
4. **확인합니다.** 새 세션에서 "run-ticket의 워커 도구 절차가 무엇인지 알려 줘"라고 물어 1번의 경로가 나오는지 봅니다.

`~/.omp/agent/AGENTS.md`를 이 저장소의 `extras/omp/AGENTS.md`에 링크로 설치했으면, 그 파일에 문구를 넣는 것은 클론한 저장소의 파일을 고치는 것입니다. 링크 대신 복사본을 두고 고치거나 레포의 `AGENTS.md`에 넣습니다.

## 프로필

이 폴더의 `config.json`은 병렬 경로와 교차 리뷰가 쓰는 프로필 둘만 예시로 둡니다. 두 프로필 모두 `provider`를 빈 문자열로, `model`·`modeId`·`thinkingOptionId`를 빼 둔 채 배포합니다. Paseo 프로필 형식에서 `provider`는 반드시 있어야 하는 문자열이고 `model`, `modeId`, `thinkingOptionId`는 없어도 되므로, 키는 두고 값만 비웠습니다. 모드와 thinking 값은 provider와 모델마다 다르므로 함께 고릅니다.

| 프로필 | 목적 | 고치는가 | 채울 값 |
|---|---|---|---|
| `ticket-worker` | 병렬 경로에서 티켓 하나 구현과 커밋 | 예 | 자기 환경의 provider와 모델 |
| `cross-review` | 구현한 모델과 다른 회사의 모델로 diff를 읽기 전용 리뷰. 기준은 버그, 작업 경계와 레포 규칙 위반, 인증·권한·결제·개인정보 변경이면 보안 | 아니오 | 구현에 쓰는 모델과 다른 회사의 provider와 모델 |

등록 문구의 워커 모델 줄이 프로필이나 모델을 정했으면 그것이 먼저입니다. 정하지 않았으면 에이전트를 띄우는 세션은 프로필마다 설명을 읽고 맡길 일에 맞는 것을 고릅니다. provider가 비어 있는 프로필은 쓰지 않고, 모델이 없는 프로필은 그 provider의 모델을 조회해 고릅니다. 맞는 프로필이 없으면 쓸 수 있는 provider와 모델을 조회해 고르고, 무엇으로 띄웠는지 알립니다. 교차 리뷰에는 구현한 모델과 같은 회사의 모델을 쓰지 않습니다.

## Paseo 오케스트레이션 방식

run-ticket은 여러 티켓을 실행할 때 사용자나 부른 쪽이 정한 도구의 절차, 레포·에이전트 규칙이 지정한 절차(여럿이면 적힌 순서) 순서로 보고, 그 절차의 사용 조건을 만족하는 첫 절차를 씁니다. 지정도 등록도 없거나 쓸 수 있는 절차가 없으면 메인 세션이 티켓을 차례로 직접 실행합니다(기본 흐름). Paseo 절차의 사용 조건은 세션에 Paseo의 워크스페이스·에이전트 관리 도구가 있거나 `paseo ls`가 성공하는 것입니다. 두 방식의 비교는 [Orca 오케스트레이션 설정](orca-orchestration.md#두-방식의-차이)에 있습니다.

Paseo 절차로 실행하면 다음처럼 동작합니다. 머지, 통합 검증, 완료 기록, 교차 리뷰, 통합 리뷰는 Orca와 같습니다.

- **실행 단위**: Paseo에는 Run이나 Task 같은 개념이 없어 조정자 세션이 막힘 관계 순서를 직접 지킵니다.
- **워커**: 티켓마다 현재 브랜치(로컬 ref)에서 갈라진 worktree 격리 워크스페이스와 그 안의 에이전트 하나를 띄웁니다.
- **워커 모델**: 등록 문구의 워커 모델 줄이 고정한 프로필, 그 프로필이 없을 때 적은 모델, 저장된 에이전트 프로필의 설명, 조정자 세션과 같은 provider·모델 순서로 고릅니다.
- **끝남 감지**: 완료 알림을 기다리고 상태를 되풀이해 조회하지 않습니다. Paseo가 띄운 세션이 아니면 알림이 오지 않으므로 `paseo wait`로 기다리고 `paseo logs`로 결과를 읽습니다.
- **질문·리베이스 요청**: 같은 에이전트에 후속 프롬프트로 보냅니다.
- **이어 받기**: 기록한 티켓별 워크스페이스 ID, 에이전트 ID, 브랜치로 이어 받습니다. run-flow에서는 상태 파일의 `- 워커 식별자:`에 `Paseo 01: 워크스페이스 <ID>, 에이전트 <ID>, 브랜치 <브랜치>; 02: …` 형식으로 적습니다.
- **정리**: 워크스페이스를 archive(Paseo가 worktree 제거)한 뒤 브랜치를 지웁니다.

교차 리뷰는 병렬 실행 여부와 상관없이 늘 하고, 변경을 구현한 모델과 다른 회사의 모델이 맡습니다. 맡길 모델은 고정하지 않고 부를 때마다 사용자가 이번 실행에서 지정한 수단, 사용자 설정(에이전트 규칙, 하네스 설정, 저장된 프로필)에 적힌 수단, 환경 조회로 고른 다른 회사 모델 순서로 고릅니다. 워커 도구 절차의 "교차 리뷰 워커"는 이 가운데 하나입니다. Paseo 절차로 띄울 때 모델은 등록 문구의 워커 모델 줄(프로필, 프로필이 없을 때의 모델), 저장된 프로필의 설명(값을 채운 `cross-review` 등), 쓸 수 있는 모델 조회 순서로 고르고, 구현한 모델과 같은 회사의 모델은 쓰지 않습니다. 다른 회사 모델을 쓸 수 없으면 리뷰를 생략하지 않고 같은 회사 모델의 새 컨텍스트 리뷰로 대체하며, 대체했다는 것과 수행한 모델을 완료 기록에 적은 뒤 계속합니다.

명령과 판정 규칙의 전문은 [`extras/paseo/worker-procedure.md`](../extras/paseo/worker-procedure.md)에, 조정자가 따르는 병렬 실행 흐름은 [run-ticket](skills/run-ticket.md#여러-티켓-실행)에 있습니다.

## Orca와 함께 쓰기

- Orca 절차와 Paseo 절차를 함께 등록하면 등록 문구에 적은 순서로 사용 조건을 확인해 처음 되는 절차를 씁니다. 먼저 쓸 도구를 위에 적습니다. 문구는 [register.md](../extras/paseo/register.md)의 "Orca 절차와 함께 지정할 때"에 있습니다.
- 요청에 "Paseo로"라고 적으면 순서와 상관없이 Paseo 절차를 먼저 확인합니다. 사용 조건을 만족하지 못하면 규칙에 적힌 다음 절차를 봅니다.
- 이어 받는 실행은 기록에 남은 워커 식별자가 가리키는 도구의 절차를 씁니다.
- 워커 모델은 도구마다 등록 문구의 워커 모델 줄이 정합니다. Paseo는 등록한 고정 프로필, 그 프로필이 없을 때 적은 모델, 저장된 프로필의 설명 순서입니다. 이 저장소는 권장 모델 값을 주지 않습니다.

## 확인하기

- 새 세션에서 "run-ticket의 워커 도구 절차가 무엇인지 알려 줘"라고 물어 등록한 `worker-procedure.md` 경로가 나오는지
- 예시 프로필을 합쳤으면 Paseo 세션의 프로필 조회에 `ticket-worker`와 `cross-review`가 provider를 채운 채로 보이는지. 에이전트에게 "Paseo 프로필을 보여 줘"라고 묻거나 Settings에서 확인합니다.
- `paseo script ls`에 `check`가 보이는지

## 알아 둘 점

- **worktree의 기준은 로컬 ref입니다.** 원격 ref를 기준으로 주면 push하지 않은 커밋이 빠지므로 절차는 로컬 ref를 씁니다.
- **worktree 준비 명령은 기준 브랜치에서 읽힙니다.** `paseo.json`의 worktree 준비 명령은 고른 기준 브랜치에 커밋된 버전에서 읽힙니다.
- **프로필을 고쳐도 이미 띄운 에이전트는 바뀌지 않습니다.**
- **Paseo 도구 주입은 보안 경계가 아닙니다.** 셸을 쓸 수 있는 에이전트는 CLI로 같은 일을 할 수 있습니다.

## 지운 프로필과 플레이북

개발 플로우를 메인 세션 하나의 루프로 접으면서, 부르는 곳이 없어진 프로필과 플레이북을 지우고 남은 두 프로필의 모델 값을 비웠습니다.

| 지운 것 | 하던 일 | 지금은 |
|---|---|---|
| 프로필 `locate`, `behavior-checklist`, `impact` | 로직 위치, 수정 전 동작, 변경 영향 조사 | 메인 세션이 직접 조사합니다 |
| 프로필 `root-cause` | 원인 보고 | 메인 세션이 직접 원인을 찾습니다. 병렬 경로의 통합 검증 실패도 같습니다 |
| 프로필 `brief-draft`, `cold-read` | brief 초안과 냉독 | 메인 세션이 초안을 쓰고, 냉독 독자는 세션의 서브에이전트로 띄워 세션 모델을 따릅니다 |
| 프로필 `proposal-diff`, `hard-implementer` | 제안 diff, 실패한 티켓의 승격 구현 | 메인 세션이 직접 구현하고, 승인이 필요하면 직접 묻습니다 |
| 프로필 `skill-review`, `security-review` | 리뷰 스킬 실행, 보안 리뷰 | 메인 세션이 리뷰 스킬을 실행하고, 보안은 교차 리뷰의 조건부 기준으로 합쳤습니다 |
| 프로필 `ui-check` | 화면 확인 | 메인 세션이 직접 확인합니다 |
| 프로필 `pr-body`, `change-doc` | PR 본문, 변경 설명 문서 | 메인 세션이 씁니다 |
| 프로필 `advisor`, `env-setup` | 계획 자문, 환경 설정 | 대체하는 것이 없습니다 |
| 프로필 `connector` | Claude Code 전용 커넥터의 자료 읽기 | 자료를 파일로 넘기거나 1단계를 Claude Code에서 실행합니다 |
| `playbooks/`(플레이북 `run-ticket`과 역할 `ticket-implementer`, `ticket-reviewer`) | Playbooks 패널에서 티켓 하나를 구현·리뷰·승인 | run-ticket 스킬을 직접 실행합니다 |

옮기는 방법은 다음과 같습니다.

- **프로필**: `~/.paseo/config.json`에 예전 프로필을 합쳐 두었으면, 위 표의 프로필은 흐름이 더 이상 부르지 않으니 지우고 `paseo reload`를 실행합니다. 남겨 두어도 동작은 하지만, 병렬 경로의 세션이 설명을 읽고 고를 수 있으므로 지우는 편이 안전합니다. `ticket-worker`와 `cross-review`는 예전 값을 그대로 써도 됩니다. 그 값은 사용자 설정으로 취급됩니다. 다만 `cross-review`의 설명이 "Claude가 구현한 diff"처럼 구현 모델을 전제하면 새 예시의 설명으로 바꿉니다.
- **플레이북**: 플레이북을 복사해 둔 레포에서 `.paseo/plugins/playbooks/run-ticket.yaml`과 `.paseo/plugins/playbooks/roles/ticket-implementer/`, `.paseo/plugins/playbooks/roles/ticket-reviewer/`를 지우고 커밋합니다. 다른 플레이북을 쓰지 않으면 Playbooks 플러그인도 지워도 됩니다. 티켓 하나는 run-ticket 스킬로 실행합니다.
- **등록 문구**: 바뀌지 않았습니다. register.md의 워커 모델 줄에 예전 표의 값을 적어 두었으면 그대로 써도 되고, 지우면 절차가 프로필과 환경에서 고릅니다.

---

[문서 목록](README.md) · [README](../README.md)
