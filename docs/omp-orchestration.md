<p align="right"><b>한국어</b> · <a href="./en/omp-orchestration.md">English</a></p>

[README](../README.md) › [문서](README.md) › omp 멀티에이전트 설정

# omp 멀티에이전트 설정

omp(oh-my-pi)에서 메인 세션 하나가 개발 단계의 일을 직접 하고, 교차 리뷰와 brief 냉독 두 가지만 읽기 전용 서브에이전트로 띄우도록 에이전트 2개, 위임 규칙, 설정 예시를 설치하는 방법을 설명합니다. 이 저장소는 모델을 정하지 않습니다. 메인 세션과 교차 리뷰의 모델은 사용자가 자기 환경에서 고릅니다. 이 문서를 읽으면 `extras/omp/`의 파일을 설치하고, 모델을 고르고, 동작을 확인하고, 이전 설치에서 옮겨 올 수 있습니다.

## 목차

- [파일 구성](#파일-구성)
- [설치](#설치)
- [모델 고르기](#모델-고르기)
- [위임 규칙](#위임-규칙)
- [보호 경로 차단](#보호-경로-차단)
- [확인하기](#확인하기)
- [이전 설치에서 옮기기](#이전-설치에서-옮기기)
- [알아 둘 점](#알아-둘-점)

## 파일 구성

| 파일 | 설치 위치 | 역할 |
|---|---|---|
| [`extras/omp/config.yml`](../extras/omp/config.yml) | `~/.omp/agent/config.yml`에 합침 | 값이 빈 예시. 교차 리뷰 `review`와 병렬 워커 `worker` 역할의 자리 |
| [`extras/omp/agents/`](../extras/omp/agents/) | `~/.omp/agent/agents/` | code-reviewer(교차 리뷰), cold-reader(brief 냉독) |
| [`extras/omp/AGENTS.md`](../extras/omp/AGENTS.md) | `~/.omp/agent/AGENTS.md` | 개발 단계, 위임 대상, 실패했을 때 |
| [`extras/omp/extensions/gongbang-protected-paths.ts`](../extras/omp/extensions/gongbang-protected-paths.ts) | `~/.omp/agent/extensions/` | run-flow 보호 경로 쓰기 차단 |

에이전트와 위임 규칙은 사용자 전역에 두므로 모든 프로젝트와 워커로 띄운 omp 세션이 같은 설정을 씁니다. 프로젝트의 `.omp/agents/`에 같은 이름의 에이전트가 있으면 프로젝트 쪽이 이깁니다.

## 설치

저장소 루트에서 에이전트와 위임 규칙을 링크로 겁니다. 저장소에서 고친 내용이 다음 세션부터 반영됩니다.

```bash
mkdir -p ~/.omp/agent/agents
ln -s "$PWD"/extras/omp/agents/*.md ~/.omp/agent/agents/
ln -s "$PWD/extras/omp/AGENTS.md" ~/.omp/agent/AGENTS.md
mkdir -p ~/.omp/agent/extensions
ln -s "$PWD/extras/omp/extensions/gongbang-protected-paths.ts" ~/.omp/agent/extensions/
```

`config.yml`은 값이 빈 예시입니다. 아래 "모델 고르기"대로 값을 채운 줄만 `~/.omp/agent/config.yml`의 `modelRoles`에 옮깁니다. 같은 키가 이미 있으면 그 키 안에서 합칩니다. 옮긴 뒤 `omp config get modelRoles`로 값이 읽히는지 확인합니다.

- `~/.omp/agent/AGENTS.md`는 omp가 읽는 사용자 지침 파일 중 우선순위가 가장 높아서 `~/.claude/CLAUDE.md` 같은 다른 사용자 지침 파일을 가립니다. 그 내용도 필요하면 AGENTS.md에 `@~/.claude/CLAUDE.md`처럼 가져오는 줄을 넣습니다.

## 모델 고르기

모델은 사용자가 고릅니다. 이 저장소는 역할별 모델을 정해 배포하지 않습니다.

- **메인 세션**: 평소 쓰는 omp 설정(`modelRoles.default`)이나 세션에서 고른 모델을 그대로 씁니다. 개발 단계의 일은 모두 이 모델이 합니다.
- **교차 리뷰 (`modelRoles.review`)**: 이번 변경을 구현하는 메인 세션 모델과 다른 회사의 모델을 `<provider>/<모델 id>:<effort>` 형식으로 적습니다. code-reviewer가 `@review`로 이 값을 씁니다. 비워 두면 omp는 오류 없이 code-reviewer를 메인 세션 모델로 돌립니다(omp 19.2.1에서 확인). 그러면 같은 회사 모델의 리뷰가 되므로 반드시 채웁니다.
- **brief 냉독 (cold-reader)**: 모델을 따로 정하지 않도록 `model:` 줄을 두지 않았습니다. 띄운 세션의 모델로 읽는 것이 목적이고, omp 19.2.1에서 세션 모델로 도는 것을 확인했습니다.
- **병렬 워커 (`modelRoles.worker`, 선택)**: 워커 도구 절차를 쓸 때만 채웁니다. Orca 절차는 등록 문구의 워커 모델 줄 `--model @worker`로 이 값을 씁니다. Paseo 절차는 [Paseo 오케스트레이션 설정](paseo-orchestration.md)을 따릅니다. 비워 두면 워커 도구 절차의 규칙대로 고릅니다.

쓸 수 있는 provider와 모델은 다음 명령으로 확인합니다.

```bash
omp models <provider>
```

같은 회사의 모델도 구독과 API 키에 따라 provider 이름이 다를 수 있습니다. 쓰는 인증 방식의 provider로 조회합니다.

`review`가 비어 있으면 run-ticket이 이 세션에서 쓸 수 있는 모델을 조회해 다른 회사 모델을 고르고, 고르지 못하면 같은 회사 모델의 새 컨텍스트 리뷰로 대체하고 완료 기록에 적은 뒤 계속합니다. omp에서 서브에이전트를 부를 때 모델을 그때 넘길 수 있는지는 확인하지 않았습니다. 넘길 수 없으면 빈 `review`로는 교차 리뷰가 매번 같은 회사 대체가 되므로, 설치할 때 먼저 채워 둡니다.

## 위임 규칙

`AGENTS.md`는 메인 세션과 워커로 띄운 omp 세션만 읽고, task 서브에이전트는 읽지 않습니다. 담긴 내용은 다음과 같습니다.

- **개발 단계**: 기획서부터 PR까지 7단계와 단계마다 쓸 스킬, 사용자 확인 지점. [run-flow](skills/run-flow.md)를 실행하면 이 순서를 이어서 진행합니다. PR 본문도 메인 세션이 씁니다.
- **위임**: 완성도가 먼저이므로 맥락을 잃는 분리는 하지 않습니다. 메인 세션이 brief 초안, 구현, 완료 기준과 화면 확인, 원인 정리, 코드 리뷰와 규칙 검사, PR 본문을 직접 합니다. 새 컨텍스트가 있어야 하는 검증 두 가지만 띄웁니다. 교차 리뷰는 code-reviewer가 버그, 작업 경계와 레포 규칙 위반을 보고, 인증·권한·결제·개인정보를 다루는 변경이면 보안도 봅니다. brief 냉독은 메인 세션이 cold-reader 3명을 함께 띄웁니다. 두 결과는 메인 세션이 받아 검증하고 반영합니다. 레포 규칙이 정한 리뷰 스킬은 메인 세션이 하위 에이전트를 띄우지 않는 방식으로 직접 실행합니다.
- **넘기는 것**: code-reviewer에는 diff 범위, brief 전문, 볼 기준 목록, 레포 규칙 파일 경로를 넘기고 비밀값과 원문 로그는 넘기지 않습니다. diff가 리뷰 모델의 입력 한도를 넘으면 디렉터리별로 나눠 맡깁니다. cold-reader에는 대화 없이 brief 초안과 정해진 질문만 넘깁니다.
- **실패했을 때**: 메인 세션이 같은 루프에서 원인을 정리하고 다시 하며, 최초 시도를 포함해 3회 안에 통과시키지 못하면 멈추고 티켓을 다시 나누자고 제안합니다. 더 강한 모델이 필요하면 사용자가 세션 모델을 바꿔 상태 파일로 이어 갑니다.
- **여러 티켓**: 메인 세션이 하나씩 차례로 직접 실행합니다. 병렬 실행은 선택입니다.

omp 설정만으로는 여러 티켓을 차례로 실행합니다. 워커로 병렬 실행하려면 실행을 요청할 때 절차 문서를 알려 주거나, [Orca 절차 등록](../extras/orca/register.md)이나 [Paseo 절차 등록](../extras/paseo/register.md)대로 등록 문구를 규칙 파일에 붙이고 워커 모델 줄을 자기 환경에 맞게 채웁니다. 설치 방법은 [Orca 오케스트레이션 설정](orca-orchestration.md), [Paseo 오케스트레이션 설정](paseo-orchestration.md)에 있습니다. `~/.omp/agent/AGENTS.md`를 위처럼 링크로 설치했으면 등록 문구는 레포의 `AGENTS.md`에 넣거나, 링크 대신 복사본을 두고 넣습니다.

여러 티켓을 병렬로 실행하는 과정은 [run-ticket](skills/run-ticket.md#여러-티켓-실행)에 있습니다.

## 보호 경로 차단

`extras/omp/extensions/gongbang-protected-paths.ts`는 run-flow 흐름이 켜져 있는 저장소에서 omp의 `write`, `edit`(hashline, `apply_patch`, `patch`, `replace`, `sloppy`, `magic` 모드), `ast_edit`가 보호 목록의 파일을 고치려 하면 실행 전에 막고 이유를 돌려줍니다. 서브에이전트(`task`)도 같은 extension이 걸립니다. 목록과 켜지는 조건은 [run-flow의 보호 목록](skills/run-flow.md#보호-목록)에 있습니다.

- 대상 경로가 들어가는 저장소에 켜진 목록(상태 파일의 `- 현재 단계:`가 `완료`가 아닌 `docs/context/run-flow/*.protected`)이 없으면 아무것도 하지 않고 `python3`도 실행하지 않습니다.
- 켜진 목록이 있으면 저장소의 `skills/*/run-flow/scripts/protected_paths.py`를 `python3`로 실행해 판정합니다. run-flow가 어느 버킷에 있어도 찾습니다. 그래서 복사하지 않고 링크로 설치합니다. omp는 링크를 실제 경로로 풀어 불러옵니다. 판정하지 못하거나 이 파일을 찾지 못하면 막습니다.
- `ast_edit`는 폴더나 glob 범위에 보호 파일이 들어 있으면 막습니다. 보호 파일이 없는 경로로 좁혀 다시 부릅니다.
- `edit`에서 대상 경로를 하나도 읽지 못하면 막습니다. hashline의 `MV` 목적지도 대상으로 봅니다.
- `bash`, `eval`(JS·Python)로 쓰는 것은 막지 않습니다. run-flow가 티켓을 수락하기 전에 `protected_paths.py verify`로 잡습니다.

## 확인하기

새 omp 세션에서 확인합니다.

- `/agents`에 code-reviewer와 cold-reader가 보이는지
- `omp config get modelRoles`에 채운 `review` 값이 보이는지
- code-reviewer를 한 번 실행했을 때 세션 폴더(`~/.omp/agent/sessions/<프로젝트>/<세션>/`)의 에이전트 기록에 `review`에 적은 모델이 찍히는지
- 보호 경로 차단: 저장소 루트에서 `bun test extras/omp/extensions`(bun 필요)

## 이전 설치에서 옮기기

이전 설정을 위 "설치"처럼 링크로 설치했으면, 저장소를 갱신하는 순간 지운 에이전트 파일 7개(brief-writer, implementer, hard-implementer, test-writer, root-cause, ui-checker, doc-writer)의 링크가 깨집니다. 다음 순서로 정리합니다.

1. 깨진 에이전트 링크를 지웁니다. 아래 명령은 `~/.omp/agent/agents/`에서 대상이 없는 링크만 지웁니다.

   ```bash
   find ~/.omp/agent/agents -xtype l -print -delete
   ```

2. `~/.omp/agent/AGENTS.md`가 링크면 새 규칙이 바로 반영됩니다. 복사본을 두고 고쳐 썼으면 새 [`AGENTS.md`](../extras/omp/AGENTS.md)를 보고 위임 표와 "실패했을 때"를 옮깁니다.
3. `~/.omp/agent/config.yml`에 예전에 옮긴 항목을 정리합니다.
   - 지웁니다: `modelRoles`의 `brief`, `slow`, `advisor`, `vision`, 최상위 `advisor` 항목, `task.agentModelOverrides`의 `reviewer`와 `security-reviewer`, `retry.fallbackChains`의 `review`, `vision`, `slow`. `review` 대체 체인을 남기면 하네스가 교차 리뷰 모델을 조용히 바꿔 대체가 기록되지 않습니다.
   - 다시 고릅니다: `modelRoles.review`와 `modelRoles.worker`는 위 "모델 고르기"대로 자기 환경에서 다시 고릅니다.
   - 사용자가 정합니다: `default`, `plan`, `task`, `smol`, `tiny`, `commit`과 `retry.fallbackChains.default`는 omp 자체 설정이라 이 저장소가 더는 정하지 않습니다. 예전 값을 그대로 둘지는 사용자가 정합니다.
4. 새 omp 세션에서 위 "확인하기"를 합니다.

## 알아 둘 점

- **교차 리뷰의 읽기 전용은 지시와 사후 확인입니다.** code-reviewer는 diff를 읽으려고 `bash`를 두지만 하위 에이전트를 띄우는 도구는 두지 않습니다. 메인 세션이 호출 전후의 코드 지문을 비교해, 바뀌었으면 그 결과를 쓰지 않고 사용자에게 보여 준 뒤 다음 수단으로 다시 맡깁니다.
- **실패 시 승격은 없습니다.** 다른 에이전트나 더 강한 모델로 자동으로 올리지 않습니다. omp의 대체 모델은 모델을 쓸 수 없을 때만 동작합니다.
- **`default` 대체 체인을 두면 구현한 모델이 섞일 수 있습니다.** 교차 리뷰의 "다른 회사"는 실제로 구현한 모델로 판정하므로, 대체가 일어났으면 완료 기록의 모델을 확인합니다.
- **입력 크기로 모델을 고르는 설정은 없습니다.** diff가 리뷰 모델의 입력 한도를 넘으면 `AGENTS.md`가 디렉터리별로 나눠 리뷰를 맡기게 합니다.

---

[문서 목록](README.md) · [README](../README.md)
