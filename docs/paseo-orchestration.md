<p align="right"><b>한국어</b> · <a href="./en/paseo-orchestration.md">English</a></p>

[README](../README.md) › [문서](README.md) › Paseo 오케스트레이션 설정

# Paseo 오케스트레이션 설정

[Paseo](https://paseo.sh/docs)에서 run-ticket이 여러 티켓을 워커로 병렬 실행하도록 Paseo 도구, 에이전트 프로필, 워크스페이스 스크립트, 선택 사항인 플레이북을 설정하는 방법을 설명합니다. Paseo 방식은 티켓마다 현재 브랜치에서 갈라진 worktree 워크스페이스 하나와 그 안의 에이전트 하나를 띄우고, 조정자 세션이 막힘 관계 순서와 머지를 맡습니다. 이 문서를 읽으면 `extras/paseo/`의 파일을 설치하고, 워커 절차를 등록하고, 동작을 확인하고, Orca와 함께 쓸 수 있습니다.

Paseo 절차는 스킬 밖의 선택 설정입니다. run-ticket 스킬은 특정 워커 도구를 직접 다루지 않고, 사용자가 정해 준 워커 도구 절차나 레포·에이전트 규칙(CLAUDE.md, AGENTS.md)이 지정한 절차가 있고 그 사용 조건을 만족할 때만 여러 티켓을 병렬로 실행합니다. 그런 절차가 없으면 서브에이전트로 차례로 실행합니다. 그래서 매번 절차를 알려 주지 않으려면 Paseo를 설치한 뒤 Paseo 절차 문서 [`extras/paseo/worker-procedure.md`](../extras/paseo/worker-procedure.md)를 규칙 파일에 등록합니다.

## 목차

- [파일 구성](#파일-구성)
- [설치](#설치)
- [절차 등록](#절차-등록)
- [프로필](#프로필)
- [Paseo 오케스트레이션 방식](#paseo-오케스트레이션-방식)
- [플레이북으로 티켓 하나 실행하기](#플레이북으로-티켓-하나-실행하기)
- [Orca와 함께 쓰기](#orca와-함께-쓰기)
- [확인하기](#확인하기)
- [알아 둘 점](#알아-둘-점)

## 파일 구성

| 파일 | 설치 위치 | 역할 |
|---|---|---|
| [`extras/paseo/worker-procedure.md`](../extras/paseo/worker-procedure.md) | 조정자 세션이 읽음. 규칙 파일에 경로를 적습니다 | Paseo로 워커를 만들고, 기다리고, 끝을 판정하고, 이어 받고, 정리하는 절차와 교차 리뷰 워커를 띄우는 방법. 절 이름은 run-ticket `references/multi-ticket.md`의 "워커 도구 절차" 항목과 같습니다 |
| [`extras/paseo/register.md`](../extras/paseo/register.md) | 읽고 따라 함 | 규칙 파일에 붙일 등록 문구, 워커 모델 줄과 프로필·omp 설정 값, Orca 절차와 함께 지정하는 문구 |
| [`extras/paseo/config.json`](../extras/paseo/config.json) | `~/.paseo/config.json`에 합침 | Paseo 도구를 에이전트에 주는 설정(`daemon.mcp.injectIntoAgents`)과 목적별 에이전트 프로필 18개 |
| [`extras/paseo/playbooks/`](../extras/paseo/playbooks/) | 쓰려는 레포의 `.paseo/plugins/playbooks/` | 티켓 하나를 실행하는 플레이북 `run-ticket`과 역할 2개(`ticket-implementer`, `ticket-reviewer`). 선택 사항이고 Playbooks 플러그인이 필요합니다 |
| 레포 루트 [`paseo.json`](../paseo.json) | 이 레포에 있음 | 이 레포의 워크스페이스 스크립트 `check`(`python3 scripts/check.py`). 자기 레포에는 같은 형식으로 직접 만듭니다 |

## 설치

1. **Paseo 도구 켜기**: Settings → 호스트 → Agents에서 Enable Paseo tools를 켜거나, `~/.paseo/config.json`에 `daemon.mcp.injectIntoAgents: true`를 넣습니다. 켠 뒤 새 에이전트를 시작하거나 기존 에이전트를 다시 불러와야 도구를 받습니다.
2. **프로필**: `extras/paseo/config.json`의 `daemon.agentProfiles` 항목을 `~/.paseo/config.json`의 같은 키에 합치고 `paseo reload`를 실행합니다. 기존 파일을 덮어쓰지 않습니다. 프로필은 데몬을 재시작하지 않아도 반영됩니다. Settings → 호스트 → Agents → Agent profiles에서 같은 값으로 직접 만들어도 됩니다. `connector`를 뺀 프로필의 provider는 omp이므로 omp provider가 켜져 있어야 합니다. 다른 provider를 쓰면 `provider`, `model`, `modeId`, `thinkingOptionId`를 그 provider의 값으로 바꿉니다. 쓸 수 있는 provider는 `paseo provider ls`로, 모델은 `paseo provider models <provider>`로 확인합니다.
3. **플레이북(선택)**: `paseo plugin add lerenn/playbooks`로 플러그인을 설치하고, 쓰려는 레포에서 아래 명령을 실행한 뒤 커밋합니다. Playbooks 패널에서 "Start in a new workspace"로 시작하면 현재 커밋에서 갈라진 worktree에서 실행됩니다.

   ```bash
   mkdir -p .paseo/plugins/playbooks && cp -R <dev-gongbang 경로>/extras/paseo/playbooks/. .paseo/plugins/playbooks/
   ```

4. **워크스페이스 스크립트**: 레포 루트에 `paseo.json`을 둡니다. 이 레포의 것은 다음과 같습니다.

   ```json
   {"scripts": {"check": {"command": "python3 scripts/check.py"}}}
   ```

   `paseo script ls`로 목록을 보고 `paseo script start check`로 실행합니다.

5. **절차 등록**: 아래 [절차 등록](#절차-등록)대로 규칙 파일에 Paseo 절차를 지정합니다.

## 절차 등록

자세한 방법은 [`extras/paseo/register.md`](../extras/paseo/register.md)에 있습니다.

1. **절차 문서의 경로를 정합니다.** 이 저장소를 클론해 두었으면 `<dev-gongbang 경로>/extras/paseo/worker-procedure.md`의 절대 경로를 씁니다. 팀이 함께 쓰는 레포면 `worker-procedure.md`를 그 레포에 복사해 커밋하고 레포 기준 경로를 씁니다.
2. **규칙 파일에 등록 문구를 붙입니다.** 모든 프로젝트에서 쓰려면 사용자 전역 규칙 파일(Claude Code는 `~/.claude/CLAUDE.md`, omp는 `~/.omp/agent/AGENTS.md` 등)에, 한 레포에서만 쓰려면 그 레포의 `CLAUDE.md`나 `AGENTS.md`에 넣습니다. 경로는 글로만 적고 `@<경로>`로 가져오지 않습니다.

   ```markdown
   ## 워커 도구 절차

   run-ticket의 워커 도구 절차는 Paseo 절차입니다. 여러 티켓을 병렬로 실행하거나 교차 리뷰를 워커에 맡길 때 `<worker-procedure.md 경로>`를 읽고 따릅니다.
   ```

3. **워커 모델을 정합니다(선택).** 쓸 프로필을 고정하거나 프로필이 없을 때의 모델을 정하려면 등록 문구 아래에 워커 모델 줄을 더합니다. 문구와 이 폴더 프로필·omp 설정 값은 register.md의 "워커 모델 정하기"에 있습니다.
4. **확인합니다.** 새 세션에서 "run-ticket의 워커 도구 절차가 무엇인지 알려 줘"라고 물어 1번의 경로가 나오는지 봅니다.

`~/.omp/agent/AGENTS.md`를 이 저장소의 `extras/omp/AGENTS.md`에 링크로 설치했으면, 그 파일에 문구를 넣는 것은 클론한 저장소의 파일을 고치는 것입니다. 링크 대신 복사본을 두고 고치거나 레포의 `AGENTS.md`에 넣습니다.

## 프로필

**프로필 하나에는 목적 하나만 둡니다.** 목적은 받은 결과를 확인할 기준으로 가릅니다. 확인할 기준이 하나면 목적이 하나입니다. 구현과 독립 리뷰, 리뷰 스킬 둘처럼 확인할 기준이 다르면 에이전트를 둘 띄웁니다. 한 에이전트의 결과에 기준이 다른 것이 섞이면 결과를 받는 메인 세션이 그 결과를 리뷰하거나 버그와 AI slop을 찾기 어렵습니다.

**완성도가 먼저이므로 맥락을 잃는 분리는 하지 않습니다.** 작성이나 구현을 맡은 에이전트는 자기 산출물을 검증하고 그 결과를 반영해 완성하는 것까지 책임집니다. 초안의 냉독 검증, 구현의 완료 기준 확인, 실패한 티켓의 원인 정리를 떼어 다른 에이전트에 완성을 넘기지 않습니다. 이것을 나누면 뒤 에이전트가 앞 에이전트의 맥락을 다시 쌓아야 합니다. 냉독 읽기나 화면 확인처럼 새 컨텍스트가 있어야 하는 검증은 별도 에이전트가 하되, 그 결과는 산출물을 만든 쪽이 받아 반영합니다. 프로필을 더할 때는 목적이 하나인지, 나눠서 맥락을 잃지 않는지를 함께 봅니다.

에이전트를 띄우는 세션은 프로필마다 설명을 읽고 맡길 일의 목적에 맞는 것을 고릅니다. 맞는 프로필이 없으면 쓸 수 있는 provider와 모델을 조회해 고르고, 무엇으로 띄웠는지 알립니다.

| 프로필 | 목적 | 고치는가 | 모델 · thinking |
|---|---|---|---|
| `locate` | 기존 로직의 위치 찾기 | 아니오 | Haiku 5.5 · medium |
| `behavior-checklist` | 수정 전 동작 체크리스트 작성 | 아니오 | Haiku 5.5 · medium |
| `root-cause` | 버그나 실패의 원인 보고 | 아니오 | Opus 5.5 · high |
| `impact` | 정해진 변경 하나의 영향과 위험 산정 | 아니오 | Opus 5.5 · high |
| `brief-draft` | 작업 지시서(brief) 초안 작성과 그 초안의 냉독 검증 | 초안만 | Opus 5.5 · xhigh |
| `cold-read` | 초안을 쓴 쪽이 띄우는 냉독 읽기 | 아니오 | Opus 5.5 · medium |
| `change-doc` | 끝난 변경의 설명 문서 작성 | 문서만 | Opus 5.5 · xhigh |
| `ticket-worker` | 티켓 하나 구현과 커밋 | 예 | Opus 5.5 · medium |
| `proposal-diff` | 티켓 하나의 제안 diff 작성 | diff만 | Opus 5.5 · medium |
| `hard-implementer` | 앞선 구현이 실패해 올라왔거나(서브에이전트 구현 두 번 실패, 구현 워커 한 번 실패), 큰 리팩터링이거나, 원인을 모르는 실패를 고치는 티켓 하나를 원인 정리부터 구현 | 예 | Opus 5.5 · xhigh |
| `cross-review` | Claude가 구현한 diff의 버그를 다른 회사 모델로 찾기. 구현한 모델이 Claude가 아니면 쓰지 않음 | 아니오 | GPT-6.2 Sol · high |
| `skill-review` | 리뷰 스킬 하나 실행 | 아니오 | GPT-6.2 Sol · high |
| `security-review` | 보안 결함 찾기 | 아니오 | Opus 5.5 · high |
| `ui-check` | 브라우저로 완료 기준 확인 | 아니오 | GPT-6.1 Terra · medium |
| `pr-body` | PR 본문 작성 | 아니오 | Haiku 5.5 · medium |
| `advisor` | 계획이나 설계 하나 평가 | 아니오 | Fable 5.2 · high |
| `env-setup` | 도구·환경 설정 문제 하나 해결 | 설정만 | Opus 5.5 · medium |
| `connector` | Claude Code 커넥터(SharePoint, Figma 등)로 자료 읽기 | 아니오 | Claude Code의 Opus 5.5 |

모델은 [omp 멀티에이전트 설정](omp-orchestration.md)의 역할별 모델과 같게 두었습니다. `connector`만 provider가 `claude`이고 모드는 `auto`입니다. Claude Code에 커넥터를 연결해 두지 않았으면 이 프로필을 지웁니다.

- `locate`와 `behavior-checklist`는 컨텍스트가 100K라 범위를 좁혀 맡깁니다. 범위가 넓으면 범위를 나눠 여러 번 맡깁니다. 목적이 원인 찾기나 영향 산정일 때만 `root-cause`나 `impact`를 씁니다.
- 리뷰 스킬이 여럿이면 `skill-review`를 스킬마다 하나씩 띄웁니다. 한 에이전트에 스킬 둘을 묶으면 어느 지적이 어느 기준에서 나왔는지 가릴 수 없습니다.
- `brief-draft`는 초안을 쓰고 `cold-read`를 띄워 자기 초안을 검증한 뒤 돌려줍니다. 초안과 그 검증은 한 작업이라 나누지 않습니다.
- 커밋 메시지 프로필은 두지 않습니다. 커밋 메시지는 변경을 만든 세션이 맥락을 가진 채로 씁니다.
- 원인 보고만 필요하면 `root-cause`에, 원인을 찾아 고치는 것까지 맡길 일이면 `hard-implementer`에 맡깁니다. 원인을 찾은 에이전트와 고치는 에이전트를 나누면 고치는 쪽이 원인을 다시 찾아야 합니다.

## Paseo 오케스트레이션 방식

run-ticket은 여러 티켓을 실행할 때 사용자나 부른 쪽이 정한 도구의 절차, 레포·에이전트 규칙이 지정한 절차(여럿이면 적힌 순서) 순서로 보고, 그 절차의 사용 조건을 만족하는 첫 절차를 씁니다. 쓸 수 있는 절차가 없으면 서브에이전트로 차례 실행합니다. Paseo 절차의 사용 조건은 세션에 Paseo의 워크스페이스·에이전트 관리 도구가 있거나 `paseo ls`가 성공하는 것입니다. 두 방식의 비교는 [Orca 오케스트레이션 설정](orca-orchestration.md#두-방식의-차이)에 있습니다.

Paseo 절차로 실행하면 다음처럼 동작합니다. 머지, 통합 검증, 완료 기록, 교차 리뷰, 통합 리뷰는 Orca와 같습니다.

- **실행 단위**: Paseo에는 Run이나 Task 같은 개념이 없어 조정자 세션이 막힘 관계 순서를 직접 지킵니다.
- **워커**: 티켓마다 현재 브랜치(로컬 ref)에서 갈라진 worktree 격리 워크스페이스와 그 안의 에이전트 하나를 띄웁니다.
- **워커 모델**: 등록 문구의 워커 모델 줄이 고정한 프로필, 그 프로필이 없을 때 적은 모델, 저장된 에이전트 프로필의 설명, 조정자 세션과 같은 provider·모델 순서로 고릅니다.
- **끝남 감지**: 완료 알림을 기다리고 상태를 되풀이해 조회하지 않습니다. Paseo가 띄운 세션이 아니면 알림이 오지 않으므로 `paseo wait`로 기다리고 `paseo logs`로 결과를 읽습니다.
- **질문·리베이스 요청**: 같은 에이전트에 후속 프롬프트로 보냅니다.
- **이어 받기**: 기록한 티켓별 워크스페이스 ID, 에이전트 ID, 브랜치로 이어 받습니다. run-flow에서는 상태 파일의 `- 워커 식별자:`에 `Paseo 01: 워크스페이스 <ID>, 에이전트 <ID>, 브랜치 <브랜치>; 02: …` 형식으로 적습니다.
- **정리**: 워크스페이스를 archive(Paseo가 worktree 제거)한 뒤 브랜치를 지웁니다.

교차 리뷰는 변경을 구현한 모델과 다른 회사의 모델이 맡습니다. 에이전트 규칙이 정한 에이전트, 워커 도구 절차의 "교차 리뷰 워커" 순서로 처음 되는 방법을 씁니다. 모두 안 되면 건너뜁니다. Paseo 절차로 띄울 때 모델은 등록 문구의 워커 모델 줄(프로필, 프로필이 없을 때의 모델), 저장된 프로필의 설명, 쓸 수 있는 모델 조회 순서로 고르고, 구현한 모델과 같은 회사의 모델은 쓰지 않습니다. 이 폴더의 값을 쓰면 구현한 모델이 Claude일 때 `cross-review` 프로필을 씁니다.

명령과 판정 규칙의 전문은 [`extras/paseo/worker-procedure.md`](../extras/paseo/worker-procedure.md)에, 조정자가 따르는 병렬 실행 흐름은 [run-ticket](skills/run-ticket.md#여러-티켓-실행)에 있습니다.

## 플레이북으로 티켓 하나 실행하기

플레이북 `run-ticket`은 사람이 Playbooks 패널에서 티켓 하나를 실행할 때 씁니다. 입력은 `ticket`(티켓 경로, 이슈 번호나 URL) 하나입니다.

1. **implement**: `ticket-implementer`가 run-ticket 스킬의 2, 3, 4단계를 수행하고 브랜치에 커밋합니다.
2. **review**: `ticket-reviewer`가 다른 회사 모델로 읽기 전용 리뷰를 합니다. 지적이 있으면 implement로 되돌립니다. 최대 2회입니다.
3. **approve**: 사람이 머지해도 되는지 승인합니다.

머지는 플레이북이 하지 않고 사용자가 합니다. 여러 티켓 병렬 실행은 플레이북이 아니라 run-ticket 스킬이 합니다.

## Orca와 함께 쓰기

- Orca 절차와 Paseo 절차를 함께 등록하면 등록 문구에 적은 순서로 사용 조건을 확인해 처음 되는 절차를 씁니다. 먼저 쓸 도구를 위에 적습니다. 문구는 [register.md](../extras/paseo/register.md)의 "Orca 절차와 함께 지정할 때"에 있습니다.
- 요청에 "Paseo로"라고 적으면 순서와 상관없이 Paseo 절차를 씁니다.
- 이어 받는 실행은 기록에 남은 워커 식별자가 가리키는 도구의 절차를 씁니다.
- 워커 모델은 도구마다 등록 문구의 워커 모델 줄이 정합니다. Paseo는 에이전트 프로필이 먼저입니다. [omp 멀티에이전트 설정](omp-orchestration.md)에 맞춘 값은 각 register.md의 표에 있습니다.

## 확인하기

- 새 세션에서 "run-ticket의 워커 도구 절차가 무엇인지 알려 줘"라고 물어 등록한 `worker-procedure.md` 경로가 나오는지
- Paseo 세션에서 프로필 조회에 [프로필](#프로필) 표의 18개가 보이는지. 에이전트에게 "Paseo 프로필을 보여 줘"라고 묻거나 Settings에서 확인합니다.
- `paseo script ls`에 `check`가 보이는지
- Playbooks 패널에 "티켓 실행"이 오류 없이 보이는지

## 알아 둘 점

- **플레이북은 Paseo 공식 기능이 아닙니다.** 서드파티 플러그인(lerenn/playbooks)이고, 플러그인 README가 v1.0 전에는 마이너 릴리스마다 YAML 형식이 깨질 수 있다고 경고합니다. 그래서 Paseo 워커 절차도 플레이북을 쓰지 않습니다.
- **worktree의 기준은 로컬 ref입니다.** 원격 ref를 기준으로 주면 push하지 않은 커밋이 빠지므로 절차는 로컬 ref를 씁니다.
- **worktree 준비 명령은 기준 브랜치에서 읽힙니다.** `paseo.json`의 worktree 준비 명령은 고른 기준 브랜치에 커밋된 버전에서 읽힙니다.
- **프로필을 고쳐도 이미 띄운 에이전트는 바뀌지 않습니다.**
- **Paseo 도구 주입은 보안 경계가 아닙니다.** 셸을 쓸 수 있는 에이전트는 CLI로 같은 일을 할 수 있습니다.

---

[문서 목록](README.md) · [README](../README.md)
