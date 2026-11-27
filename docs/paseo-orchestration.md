<p align="right"><b>한국어</b> · <a href="./en/paseo-orchestration.md">English</a></p>

[README](../README.md) › [문서](README.md) › Paseo 오케스트레이션 설정

# Paseo 오케스트레이션 설정

[Paseo](https://paseo.sh/docs) 도구와 예시 에이전트 프로필을 설치하고 Paseo 워커 절차를 규칙 파일에 등록하면, run-ticket이 여러 티켓을 Paseo 워커로 병렬 실행하고 교차 리뷰를 다른 회사 모델의 에이전트에 맡길 수 있습니다. 티켓마다 현재 브랜치에서 갈라진 worktree 워크스페이스 하나와 그 안의 에이전트 하나를 띄우고, 조정자 세션(run-ticket이나 run-flow를 실행하는 세션)이 막힘 관계 순서와 머지를 맡습니다. 이 문서를 읽으면 `extras/paseo/`의 파일을 설치하고, 워커 절차를 등록하고, 설치를 확인할 수 있고, Paseo 방식이 어떻게 동작하는지 알 수 있습니다.

병렬 실행은 사용자가 고를 때만 쓰는 선택 경로입니다. run-ticket은 사용자가 이번 실행에서 워커 도구 절차를 지정했거나 레포·에이전트 규칙(CLAUDE.md, AGENTS.md)에 절차가 등록돼 있고, 그 절차의 사용 조건을 만족할 때만 티켓을 병렬로 실행합니다. 지정도 등록도 없으면 메인 세션이 티켓을 차례로 직접 실행합니다. 워커와 교차 리뷰의 모델은 이 저장소가 정하지 않고 사용자의 규칙, 저장된 프로필, 환경을 따릅니다. Paseo 절차는 [Orca 절차](orca-orchestration.md)와 함께 등록할 수도 있습니다.

## 목차

- [파일 구성](#파일-구성)
- [설치](#설치)
- [절차 등록](#절차-등록)
- [확인하기](#확인하기)
- [프로필](#프로필)
- [도구 고르는 순서](#도구-고르는-순서)
- [Paseo 오케스트레이션 방식](#paseo-오케스트레이션-방식)
- [알아 둘 점](#알아-둘-점)
- [이전 설정에서 옮기기](#이전-설정에서-옮기기)

## 파일 구성

| 파일 | 설치 위치 | 역할 |
|---|---|---|
| [`extras/paseo/worker-procedure.md`](../extras/paseo/worker-procedure.md) | 조정자 세션이 읽음. 규칙 파일에 경로를 적습니다 | Paseo로 워커를 만들고, 기다리고, 끝을 판정하고, 이어 받고, 정리하는 절차와 교차 리뷰 워커를 띄우는 방법. 절 이름은 run-ticket `references/multi-ticket.md`의 "워커 도구 절차" 항목과 같습니다 |
| [`extras/paseo/register.md`](../extras/paseo/register.md) | 사용자가 읽고 따라 함 | 규칙 파일에 붙일 등록 문구, 값을 자리 표시로 둔 워커 모델 줄, Orca 절차와 함께 지정하는 문구 |
| [`extras/paseo/config.json`](../extras/paseo/config.json) | `~/.paseo/config.json`에 합침 | Paseo 도구를 에이전트에 주는 설정(`daemon.mcp.injectIntoAgents`)과 provider·모델을 비운 예시 프로필 2개(`ticket-worker`, `cross-review`) |
| 레포 루트 [`paseo.json`](../paseo.json) | 이 레포에 있음 | 이 레포의 워크스페이스 스크립트 `check`(`python3 scripts/check.py`). 자기 레포에는 같은 형식으로 직접 만듭니다 |

## 설치

1. **Paseo 도구 켜기**: Settings → 호스트 → Agents에서 Enable Paseo tools를 켜거나, `~/.paseo/config.json`에 `daemon.mcp.injectIntoAgents: true`를 넣습니다. 켠 뒤 새 에이전트를 시작하거나 기존 에이전트를 다시 불러와야 도구를 받습니다.
2. **프로필(선택)**: `extras/paseo/config.json`의 `daemon.agentProfiles` 항목을 `~/.paseo/config.json`의 같은 키에 합칩니다. 기존 파일을 통째로 덮어쓰지 않습니다. 각 프로필의 `provider`(필수)와 `model`(선택)을 자기 환경의 값으로 채운 뒤 `paseo reload`를 실행합니다. 프로필은 데몬을 재시작하지 않아도 반영됩니다. Settings → 호스트 → Agents → Agent profiles에서 직접 만들어도 됩니다.
   - 쓸 수 있는 provider는 `paseo provider ls`로, 모델은 `paseo provider models <provider>`로 확인합니다.
   - `cross-review`에는 구현에 쓰는 모델과 다른 회사의 모델을 넣습니다.
   - 프로필을 합치지 않아도 절차는 동작합니다. 고르는 순서는 아래 [프로필](#프로필)에 있습니다.
3. **워크스페이스 스크립트(선택)**: 레포 루트에 `paseo.json`을 둡니다. 이 레포의 것은 다음과 같습니다. `paseo script ls`로 목록을 보고 `paseo script start check`로 실행합니다.

   ```json
   {"scripts": {"check": {"command": "python3 scripts/check.py"}}}
   ```

4. **절차 등록**: 아래 [절차 등록](#절차-등록)대로 규칙 파일에 Paseo 절차를 지정합니다.

## 절차 등록

자세한 방법은 [`extras/paseo/register.md`](../extras/paseo/register.md)에 있습니다.

1. **절차 문서의 경로를 정합니다.** 이 저장소를 클론해 두었으면 `<dev-gongbang 경로>/extras/paseo/worker-procedure.md`의 절대 경로를 씁니다. 저장소를 갱신하면 절차도 함께 갱신됩니다. 팀이 함께 쓰는 레포면 `worker-procedure.md`를 그 레포에 복사해 커밋하고 레포 기준 경로를 씁니다.
2. **규칙 파일에 등록 문구를 붙입니다.** 모든 프로젝트에서 쓰려면 사용자 전역 규칙 파일(Claude Code는 `~/.claude/CLAUDE.md`, Codex는 `~/.codex/AGENTS.md`, omp는 `~/.omp/agent/AGENTS.md`)에, 한 레포에서만 쓰려면 그 레포의 `CLAUDE.md`나 `AGENTS.md`에 넣습니다. 경로는 글로만 적고 `@<경로>`로 가져오지 않습니다. 가져오면 워커를 쓰지 않는 세션도 절차 전문을 읽습니다.

   ```markdown
   ## 워커 도구 절차

   run-ticket의 워커 도구 절차는 Paseo 절차입니다. 여러 티켓을 병렬로 실행하거나 교차 리뷰를 워커에 맡길 때 `<worker-procedure.md 경로>`를 읽고 따릅니다.
   ```

3. **워커 모델을 정합니다(선택).** 쓸 프로필을 고정하거나, 그 프로필이 없을 때 쓸 provider·모델·thinking을 정하려면 등록 문구 아래에 워커 모델 줄을 더합니다. 문구는 register.md의 "워커 모델 정하기"에 있고, 값은 자리 표시뿐이라 자기 환경의 것으로 채웁니다.

`~/.omp/agent/AGENTS.md`를 이 저장소의 `extras/omp/AGENTS.md`에 링크로 설치했으면, 그 파일에 문구를 넣는 것은 클론한 저장소의 파일을 고치는 것입니다. 링크 대신 복사본을 두고 고치거나 레포의 `AGENTS.md`에 넣습니다.

## 확인하기

- 새 세션에서 "run-ticket의 워커 도구 절차가 무엇인지 알려 줘"라고 물어 등록한 `worker-procedure.md` 경로가 나오는지
- `paseo ls`가 성공하는지
- 예시 프로필을 합쳤으면 `ticket-worker`와 `cross-review`가 provider를 채운 채로 보이는지. 에이전트에게 "Paseo 프로필을 보여 줘"라고 묻거나 Settings에서 확인합니다.
- `paseo.json`을 두었으면 `paseo script ls`에 `check`가 보이는지

병렬 실행 조건을 만족하고 이 절차가 선택되면, run-ticket은 계획 승인을 받을 때 워커를 띄울 도구로 Paseo를 보여 줍니다.

## 프로필

`extras/paseo/config.json`은 병렬 경로와 교차 리뷰가 쓰는 프로필 두 개를 예시로 둡니다. 두 프로필 모두 `provider`를 빈 문자열로 두고 `model`·`modeId`·`thinkingOptionId`는 빼 두었습니다. Paseo 프로필 형식에서 `provider`는 반드시 있어야 하는 문자열이고 나머지는 없어도 되기 때문입니다. 모드와 thinking 값은 provider와 모델마다 다르므로 함께 고릅니다.

| 프로필 | 맡는 일 | 파일을 고치는가 | 채울 값 |
|---|---|---|---|
| `ticket-worker` | 병렬 경로에서 티켓 하나를 자기 worktree에서 구현하고, 완료 기준을 확인한 뒤 커밋 | 예 | 자기 환경의 provider와 모델 |
| `cross-review` | 구현한 모델과 다른 회사의 모델로 diff를 읽고 지적만 보고. 기준은 버그, 작업 경계와 레포 규칙 위반이고, 인증·권한·결제·개인정보를 다루는 변경이면 보안 | 아니오 | 구현에 쓰는 모델과 다른 회사의 provider와 모델 |

워커를 띄우는 세션은 다음 순서로 모델을 고릅니다.

1. 등록 문구의 워커 모델 줄이 고정한 프로필. 그 프로필이 없으면 그 줄에 적은 provider, 모델, thinking
2. 워커 모델 줄이 없으면 저장된 프로필마다 설명을 읽고 맡길 일에 맞는 프로필. provider가 비어 있는 프로필은 쓰지 않고, 모델이 없는 프로필은 그 provider에서 쓸 수 있는 모델을 조회해 고릅니다.
3. 맞는 프로필이 없으면 구현 워커는 조정자 세션과 같은 provider와 모델, 교차 리뷰 워커는 쓸 수 있는 provider와 모델을 조회해 고른 다른 회사 모델

어느 경우든 무엇으로 띄웠는지 알리고, 교차 리뷰에는 구현한 모델과 같은 회사의 모델을 쓰지 않습니다.

## 도구 고르는 순서

run-ticket은 여러 티켓을 실행할 때 워커 도구 절차를 다음 순서로 보고, 사용 조건을 만족하는 첫 절차를 씁니다.

1. 사용자나 부른 쪽이 정한 도구의 절차. 요청에 "Paseo로"처럼 도구를 적으면 규칙의 순서와 상관없이 그 절차를 먼저 확인합니다.
2. 레포·에이전트 규칙이 지정한 절차. 여럿이면 규칙에 적힌 순서로 봅니다.
3. 지정도 등록도 없거나 쓸 수 있는 절차가 없으면 메인 세션이 티켓을 차례로 직접 실행합니다(기본 흐름).

Paseo 절차의 사용 조건은 세션에 Paseo의 워크스페이스·에이전트 관리 도구가 있거나 `paseo ls`가 성공하는 것입니다. 교차 리뷰 워커만 띄울 때는 에이전트 관리 도구가 있거나 `paseo ls`가 성공하면 됩니다. 이어 받는 실행은 기록에 남은 워커 식별자가 가리키는 도구의 절차를 씁니다.

Orca 절차와 함께 등록하면 등록 문구에 적은 순서로 사용 조건을 확인합니다. 먼저 쓸 도구를 위에 적습니다. 문구는 [register.md](../extras/paseo/register.md)의 "Orca 절차와 함께 지정할 때"에 있습니다. 워커 모델은 도구마다 그 도구의 워커 모델 줄이 정하고, 이 저장소는 권장 모델 값을 주지 않습니다. 두 방식의 비교는 [Orca 오케스트레이션 설정](orca-orchestration.md#두-방식의-차이)에 있습니다.

## Paseo 오케스트레이션 방식

조정자 세션은 run-ticket의 "병렬 실행" 절차를 따르고, 워커를 다루는 일은 등록한 Paseo 절차([`worker-procedure.md`](../extras/paseo/worker-procedure.md))대로 합니다. Paseo에는 Run이나 Task 같은 실행 단위가 없어 조정자 세션이 막힘 관계 순서를 직접 지킵니다. 세션에 Paseo 도구가 없고 `paseo` CLI만 있으면 같은 일을 CLI로 하고, 인자는 `paseo workspace create --help`와 `paseo run --help`로 확인합니다.

1. **워커 띄우기**: 막는 티켓이 모두 머지된 티켓마다 worktree 격리 워크스페이스를 만듭니다. 새 브랜치로 갈라지고, 기준은 현재 브랜치의 로컬 ref(`refs/heads/<현재 브랜치>`)입니다. 워크스페이스 제목은 티켓 번호와 제목입니다. 그 워크스페이스에 에이전트를 하나 띄우고 워커 spec을 첫 프롬프트로 줍니다. 모델은 [프로필](#프로필)의 순서로 고릅니다.
2. **기다리기**: 워커가 끝나거나, 오류가 나거나, 권한을 요청하면 Paseo가 조정자 세션에 알립니다. 알림을 기다리고 상태를 되풀이해 조회하지 않습니다. 결과는 알림에 담긴 마지막 응답으로 읽습니다. Paseo가 띄운 세션이 아니면(환경 변수 `PASEO_AGENT_ID`가 없으면) 알림이 오지 않으므로 `paseo wait <에이전트 ID>`로 기다리고 `paseo logs <에이전트 ID>`로 결과를 읽습니다.
3. **끝 판정**: 워커가 턴을 끝냈다고 통과한 것으로 보지 않습니다. 보고에 브랜치와 커밋 해시가 있고 그 커밋이 티켓 브랜치에 있을 때만 통과로 머지와 통합 검증으로 넘어가고, 질문이면 답을 정하고, 그 밖에는 실패로 처리합니다. 권한 요청은 brief와 티켓 범위 안의 것만 승인하고, 아니면 사용자에게 묻습니다.
4. **같은 워커에 보내기**: 질문 답과 리베이스 요청은 새 에이전트를 띄우지 않고 같은 에이전트에 후속 프롬프트로 보냅니다.
5. **정리**: 머지한 뒤 그 티켓의 워크스페이스를 archive합니다. Paseo가 그 안의 에이전트를 정리하고 worktree를 지웁니다. 티켓 브랜치가 남아 있으면 `git branch -d <티켓 브랜치>`로 지웁니다. 실패한 티켓과 통합 검증에 실패한 티켓의 워크스페이스는 archive하지 않습니다.
6. **이어 받기**: 기록에 남은 에이전트 ID마다 상태를 한 번 조회합니다. 이어 받은 세션은 워커를 띄운 세션이 아니라서 완료 알림을 받지 못하므로, Paseo가 띄운 세션이면 실행 중인 워커에 하던 일을 마치고 결과를 보고하라는 후속 프롬프트를 보내 알림을 받습니다. 기록에 없는 워커는 찾지 않습니다. 워크스페이스 제목만으로 찾으면 다른 실행의 워커를 잡을 수 있습니다.

워커 식별자는 티켓마다 티켓 번호, 워크스페이스 ID, 에이전트 ID, 브랜치이고, 워크스페이스와 에이전트를 만들자마자 기록합니다. run-flow에서는 상태 파일의 `- 워커 식별자:` 줄에 한 줄로 적습니다.

```
- 워커 식별자: Paseo 01: 워크스페이스 <워크스페이스 ID>, 에이전트 <에이전트 ID>, 브랜치 <브랜치>; 02: 워크스페이스 <워크스페이스 ID>, 에이전트 <에이전트 ID>, 브랜치 <브랜치>
```

**교차 리뷰 워커**: 교차 리뷰는 병렬 실행 여부와 상관없이 늘 하고, 맡길 수단은 run-ticket이 사용자가 이번 실행에서 지정한 수단, 사용자 설정(에이전트 규칙, 하네스 설정, 저장된 프로필)이나 등록한 워커 도구 절차의 "교차 리뷰 워커", 환경 조회로 고른 다른 회사 모델 순서로 고릅니다. Paseo 절차로 맡기면 다른 회사 모델의 에이전트를 조정자의 워크스페이스에 띄우고 완료 알림으로 결과를 받습니다. 모델은 [프로필](#프로필)의 순서로 고르고(값을 채운 `cross-review` 등), 구현한 모델과 같은 회사의 모델은 쓰지 않습니다. 첫 프롬프트에는 diff 범위, brief 전문, 기준 목록, 실행할 확인 기준을 넣고, 파일은 고치지 말고 지적, 확인 기준 판정, 수행한 모델 이름만 보고하게 합니다. 다른 회사 모델을 하나도 고를 수 없으면 run-ticket은 리뷰를 생략하지 않고 같은 회사 모델의 새 컨텍스트 리뷰로 대체하며, 대체했다는 것과 수행한 모델을 완료 기록에 적은 뒤 계속합니다.

명령과 판정 규칙의 전문은 [`extras/paseo/worker-procedure.md`](../extras/paseo/worker-procedure.md)에, 조정자가 따르는 병렬 실행 흐름은 [run-ticket](skills/run-ticket.md#여러-티켓-실행)에 있습니다.

## 알아 둘 점

- **worktree의 기준은 로컬 ref입니다.** 원격 ref를 기준으로 주면 push하지 않은 커밋(흐름 문서, 앞서 머지한 티켓)이 빠지므로 절차는 로컬 ref를 씁니다.
- **워크스페이스는 막는 티켓이 머지된 뒤에 만듭니다.** 미리 만들면 막는 티켓의 변경이 없는 커밋에서 갈라집니다.
- **worktree 준비 명령은 기준 브랜치에서 읽힙니다.** `paseo.json`의 worktree 준비 명령은 고른 기준 브랜치에 커밋된 버전에서 읽힙니다.
- **프로필을 고쳐도 이미 띄운 에이전트는 바뀌지 않습니다.**
- **Paseo 도구 주입은 보안 경계가 아닙니다.** 셸을 쓸 수 있는 에이전트는 CLI로 같은 일을 할 수 있습니다.

## 이전 설정에서 옮기기

개발 플로우를 메인 세션 하나의 루프로 접으면서, 부르는 곳이 없어진 프로필과 플레이북을 지우고 남은 두 프로필의 모델 값을 비웠습니다. 지운 프로필이 하던 조사, 원인 찾기, brief 초안, 구현, 화면 확인, PR 본문은 메인 세션이 직접 하고, brief 냉독은 세션의 서브에이전트가, 보안 리뷰는 교차 리뷰의 조건부 기준이 맡습니다. 예전 설정을 합쳐 두었으면 다음처럼 정리합니다.

- **프로필**: `~/.paseo/config.json`에서 `locate`, `behavior-checklist`, `impact`, `root-cause`, `brief-draft`, `cold-read`, `proposal-diff`, `hard-implementer`, `skill-review`, `security-review`, `ui-check`, `pr-body`, `change-doc`, `advisor`, `env-setup`, `connector`를 지우고 `paseo reload`를 실행합니다. 남겨 두면 병렬 경로의 세션이 설명을 읽고 이 프로필을 고를 수 있습니다.
- **`ticket-worker`와 `cross-review`**: 예전 값을 그대로 써도 됩니다. 그 값은 사용자 설정으로 취급합니다. `cross-review`의 설명(`notes`)이 "Claude가 구현한 diff"처럼 구현 모델을 전제하면 새 예시의 설명으로 바꿉니다.
- **`connector`로 자료를 읽던 경우**: 자료를 파일로 넘기거나, 그 링크를 읽을 수 있는 커넥터나 MCP 도구가 있는 세션에서 요구사항 정리를 실행합니다.
- **플레이북**: 플레이북을 복사해 둔 레포에서 `.paseo/plugins/playbooks/run-ticket.yaml`, `.paseo/plugins/playbooks/roles/ticket-implementer/`, `.paseo/plugins/playbooks/roles/ticket-reviewer/`를 지우고 커밋합니다. 다른 플레이북을 쓰지 않으면 Playbooks 플러그인도 지워도 됩니다. 티켓 하나는 run-ticket 스킬로 실행합니다.
- **등록 문구**: 바뀌지 않았습니다. register.md의 워커 모델 줄에 예전 값을 적어 두었으면 그대로 써도 되고, 지우면 절차가 프로필과 환경에서 고릅니다.

---

[문서 목록](README.md) · [README](../README.md)
