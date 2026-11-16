<p align="right"><b>한국어</b> · <a href="./en/omp-orchestration.md">English</a></p>

[README](../README.md) › [문서](README.md) › omp 멀티에이전트 설정

# omp 멀티에이전트 설정

omp(oh-my-pi)에서 개발 단계마다 다른 모델을 쓰도록 역할별 모델, 서브에이전트 5개, 위임 규칙을 설정하는 방법을 설명합니다. 설계와 오케스트레이션은 Opus 5.5 high, 반복 구현은 Sonnet 5.5 medium, 탐색과 문서는 Haiku 5.5, 교차 리뷰는 GPT-6.1 Sol high로 두고, 막히는 문제에서만 Opus 5.5 xhigh와 Fable 5.2 자문으로 올립니다. 이 문서를 읽으면 `extras/omp/`의 파일을 설치하고, 동작을 확인하고, 모델을 바꿀 수 있습니다.

## 목차

- [파일 구성](#파일-구성)
- [설치](#설치)
- [단계별 모델](#단계별-모델)
- [위임 규칙](#위임-규칙)
- [확인하기](#확인하기)
- [모델 바꾸기](#모델-바꾸기)
- [알아 둘 점](#알아-둘-점)

## 파일 구성

| 파일 | 설치 위치 | 역할 |
|---|---|---|
| [`extras/omp/config.yml`](../extras/omp/config.yml) | `~/.omp/agent/config.yml`에 합침 | 역할별 모델·Effort, reviewer·security-reviewer 모델, 대체 모델 |
| [`extras/omp/agents/`](../extras/omp/agents/) | `~/.omp/agent/agents/` | implementer, hard-implementer, test-writer, ui-checker, doc-writer |
| [`extras/omp/AGENTS.md`](../extras/omp/AGENTS.md) | `~/.omp/agent/AGENTS.md` | 개발 단계, 위임 대상, 실패 시 승격, Orca 사용 기준 |

에이전트와 위임 규칙은 사용자 전역에 두므로 모든 프로젝트와 Orca 워커가 같은 설정을 씁니다. 프로젝트의 `.omp/agents/`에 같은 이름의 에이전트가 있으면 프로젝트 쪽이 이깁니다.

## 설치

저장소 루트에서 에이전트와 위임 규칙을 링크로 겁니다. 저장소에서 고친 내용이 다음 세션부터 반영됩니다.

```bash
mkdir -p ~/.omp/agent/agents
ln -s "$PWD"/extras/omp/agents/*.md ~/.omp/agent/agents/
ln -s "$PWD/extras/omp/AGENTS.md" ~/.omp/agent/AGENTS.md
```

`config.yml`은 기존 설정을 덮어쓰지 않도록 `modelRoles`, `advisor`, `task`, `retry.fallbackChains` 항목을 `~/.omp/agent/config.yml`에 직접 옮깁니다. 같은 키가 이미 있으면 그 키 안에서 합칩니다. 옮긴 뒤 `omp config get modelRoles`로 값이 읽히는지 확인합니다.

- GPT는 ChatGPT 구독(`openai-codex`) 기준입니다. OpenAI API 키를 쓰면 `openai-codex/`를 `openai/`로 바꿉니다. 쓸 수 있는 모델은 `omp models openai-codex`, `omp models openai`로 확인합니다.
- `~/.omp/agent/AGENTS.md`는 omp가 읽는 사용자 지침 파일 중 우선순위가 가장 높아서 `~/.claude/CLAUDE.md` 같은 다른 사용자 지침 파일을 가립니다. 그 내용도 필요하면 AGENTS.md에 `@~/.claude/CLAUDE.md`처럼 가져오는 줄을 넣습니다.

## 단계별 모델

| 단계 | omp 설정 | 모델 · Effort |
|---|---|---|
| 오케스트레이터·설계 | 메인 세션 `default`, 계획 모드 `plan` | Opus 5.5 · high |
| 코드 탐색 | bundled scout (`smol`) | Haiku 5.5 · medium |
| 일반 구현·테스트 | implementer, test-writer (`task`) | Sonnet 5.5 · medium |
| 어려운 구현·디버깅 | hard-implementer (`slow`) + 자문 (`advisor`) | Opus 5.5 · xhigh + Fable 5.2 · high |
| 교차 리뷰 | bundled reviewer (`review`) | GPT-6.1 Sol · high |
| 보안·핵심 로직 리뷰 | bundled security-reviewer | Opus 5.5 · high |
| UI·화면 검증 | ui-checker (`vision`) | GPT-6.1 Terra · medium |
| 커밋·PR 설명 | `commit`, doc-writer (`smol`) | Haiku 5.5 · medium |

모델을 쓸 수 없을 때(한도 초과 등)는 남은 턴을 GPT-6.1 Sol high로 이어 갑니다. 리뷰와 UI 검증은 반대로 Opus 5.5로 넘깁니다.

## 위임 규칙

`AGENTS.md`는 메인 세션과 Orca가 띄운 omp 워커만 읽고, task 서브에이전트는 읽지 않습니다. 담긴 내용은 다음과 같습니다.

- **개발 단계**: 기획서부터 PR까지 7단계와 단계마다 쓸 스킬, 사용자 확인 지점(구체화 기록 확정, 티켓 분할 승인, 머지 결정)
- **위임**: 작업마다 맡길 에이전트
- **넘기는 것**: 서브에이전트에는 대화 기록 대신 brief와 티켓 하나를, 리뷰 에이전트에는 diff 범위와 brief를 넘깁니다.
- **실패했을 때**: implementer가 같은 티켓에서 2회 실패하면 hard-implementer에 맡기고, 그래도 실패하면 멈추고 티켓을 다시 나누자고 제안합니다.
- **Orca**: 여러 티켓을 worktree를 나눠 병렬로 실행할 때, 다른 에이전트에게 맡길 때, 사용자가 워커를 직접 볼 때만 Orca 워커를 씁니다.

여러 티켓을 병렬로 실행하는 과정은 [run-ticket](skills/run-ticket.md#여러-티켓-실행)에 있습니다.

## 확인하기

새 omp 세션에서 확인합니다.

- `/agents`에 implementer, hard-implementer, test-writer, ui-checker, doc-writer가 보이는지
- 에이전트를 한 번씩 실행했을 때 세션 폴더(`~/.omp/agent/sessions/<프로젝트>/<세션>/`)의 에이전트별 기록에 위 표의 모델이 찍히는지
- hard-implementer를 실행한 뒤 그 에이전트 폴더에 `__advisor.jsonl`이 생기는지. 자문 모델(Fable 5.2)의 기록입니다.

## 모델 바꾸기

- 단계의 모델은 `modelRoles`에서 그 역할만 바꿉니다. 에이전트 파일은 `@task`처럼 역할을 가리키므로 고치지 않아도 됩니다.
- 비용을 줄이려면 모델을 바꾸기 전에 Effort부터 내립니다.
- `max`는 기본값으로 쓰지 않습니다. 비용이 크게 늘고 점수가 오히려 떨어지기도 합니다.
- 한 대화 안에서는 Effort를 바꾸지 않습니다. 바꾸면 프롬프트 캐시가 무효화됩니다.

## 알아 둘 점

- **실패 시 승격은 설정이 아니라 규칙입니다.** omp의 대체 모델은 모델을 쓸 수 없을 때만 동작합니다. implementer에서 hard-implementer로 올리는 판단은 `AGENTS.md`를 읽은 메인 세션이 합니다.
- **승격은 한 단계입니다.** Sonnet 5.5 medium에서 바로 Opus 5.5 xhigh + Fable 5.2 자문으로 올립니다. 그 사이에 Sonnet 5.5 high를 넣으려면 `model: anthropic/claude-sonnet-5-5:high`인 에이전트를 하나 더 만들고 `AGENTS.md`의 "실패했을 때"에 넣습니다.
- **입력 크기로 모델을 고르는 설정은 없습니다.** GPT는 입력이 272K 토큰을 넘으면 단가가 2배가 되므로, `AGENTS.md`가 큰 diff를 디렉터리별로 나눠 리뷰를 맡기게 합니다.
- **자문은 hard-implementer에만 붙습니다.** 에이전트 파일의 `advisor: true`는 전체 설정 `advisor.enabled: false`와 상관없이 그 에이전트에만 자문을 붙입니다. 자문은 붙은 세션의 모든 턴을 읽으므로 메인 세션에는 켜지 않습니다.
- **Haiku 5.5의 컨텍스트는 100K입니다.** 다른 모델(1M)보다 작으므로 scout에는 찾을 범위를 좁혀 맡깁니다.

---

[문서 목록](README.md) · [README](../README.md)
