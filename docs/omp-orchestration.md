<p align="right"><b>한국어</b> · <a href="./en/omp-orchestration.md">English</a></p>

[README](../README.md) › [문서](README.md) › omp 멀티에이전트 설정

# omp 멀티에이전트 설정

omp(oh-my-pi)에서 개발 단계마다 다른 모델을 쓰도록 역할별 모델, 서브에이전트 9개, 위임 규칙을 설정하는 방법을 설명합니다. 설계와 오케스트레이션은 Opus 5.5 high, brief 초안은 Opus 5.5 xhigh, 반복 구현도 Opus 5.5 xhigh, 탐색과 PR 설명은 Haiku 5.5, 교차 리뷰는 GPT-6.2 Sol high로 두고, 막히는 문제에서만 Fable 5.2 high와 Opus 5.5 xhigh 자문으로 올립니다. 이 문서를 읽으면 `extras/omp/`의 파일을 설치하고, 동작을 확인하고, 모델을 바꿀 수 있습니다.

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
| [`extras/omp/agents/`](../extras/omp/agents/) | `~/.omp/agent/agents/` | brief-writer, cold-reader, implementer, hard-implementer, root-cause, test-writer, ui-checker, doc-writer, code-reviewer |
| [`extras/omp/AGENTS.md`](../extras/omp/AGENTS.md) | `~/.omp/agent/AGENTS.md` | 개발 단계, 위임 대상, 실패 시 승격, Paseo·Orca 워커 사용 기준 |

에이전트와 위임 규칙은 사용자 전역에 두므로 모든 프로젝트와 Paseo·Orca 워커가 같은 설정을 씁니다. 프로젝트의 `.omp/agents/`에 같은 이름의 에이전트가 있으면 프로젝트 쪽이 이깁니다.

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
| brief 초안 작성 | brief-writer (`brief`) | Opus 5.5 · xhigh |
| 티켓 구현 워커 (병렬 실행) | Paseo는 `ticket-worker` 프로필, Orca는 `AGENTS.md`가 `--model @worker`로 띄움 (`worker`) | Paseo는 Opus 5.5 · medium, Orca는 Opus 5.5 · xhigh |
| 범위가 정해진 코드 위치 찾기·동작 조사 | bundled scout (`smol`) | Haiku 5.5 · medium |
| 일반 구현·테스트 | implementer, test-writer (`task`) | Opus 5.5 · xhigh |
| brief 냉독 읽기 | cold-reader (`task`) | Opus 5.5 · xhigh |
| 리뷰 스킬과 그 하위 리뷰 | code-reviewer (`review`) | GPT-6.2 Sol · high |
| 어려운 구현·디버깅 | hard-implementer (`slow`) + 자문 (`advisor`) | Fable 5.2 · high + Opus 5.5 · xhigh |
| 고치지 않는 원인 보고 | root-cause | Opus 5.5 · high |
| 교차 리뷰 | bundled reviewer (`review`) | GPT-6.2 Sol · high |
| 교차 리뷰 워커 (구현한 모델이 Claude가 아닐 때의 Claude Code 워커) | `AGENTS.md`가 지정. Orca는 `--model` | Opus 5.5 · medium |
| 교차 리뷰 워커 (구현한 모델이 Claude이고 reviewer가 Claude로 넘어갔을 때의 Codex 워커) | Paseo는 `cross-review` 프로필, Orca는 `AGENTS.md`가 `--model`로 지정 | GPT-6.2 Sol · high |
| 보안·핵심 로직 리뷰 | bundled security-reviewer | Opus 5.5 · high |
| UI·화면 검증 | ui-checker (`vision`) | GPT-6.1 Terra · medium |
| 커밋·PR 설명 | `commit`, doc-writer (`smol`) | Haiku 5.5 · medium |

이 배치는 Anthropic 구독 한도가 GPT 구독보다 넉넉하다고 보고 Claude 쪽 effort를 높게 두고, GPT는 교차 리뷰와 UI 검증, 대체 모델에만 씁니다. 수치는 Artificial Analysis의 effort별 비교입니다.

- **구현**: Opus 5.5 xhigh는 FrontierCode-AA 2.0 43.8%, Terminal-Bench 4.0 59.6%로 medium(33.1%, 52.5%)보다 높고 GPT-6.2 Sol medium(41.4%, 56.1%)도 넘습니다. 그래서 구현은 GPT로 옮기지 않고 Claude에 두며, 구현과 리뷰를 다른 회사 모델로 나누는 구조도 유지합니다. 응답이 느리면 `task`와 `worker`를 high로 내립니다.
- **어려운 구현**: 구현이 이미 Opus 5.5 xhigh라 승격할 단계로 Fable 5.2 high를 씁니다. FrontierCode-AA 2.0이 49.1%로 Opus 5.5 xhigh(43.8%)보다 높습니다. 자문은 본 모델과 다른 시각을 주도록 Opus 5.5 xhigh로 둡니다.
- **문서**: brief는 문서 품질 지표(AA-Briefcase)에서 Opus 5.5 xhigh가 1760으로 Fable 5.2 xhigh(1737)보다 높아 Opus에 둡니다. PR 설명과 커밋 메시지는 받은 기록을 정해진 형식으로 옮기는 짧은 작업이라 Haiku 5.5로 둡니다.
- **리뷰**: 코드 리뷰는 GPT-6.1 Sol high에서 점수가 더 오르지 않았고, GPT 한도를 아끼려고 GPT-6.2 Sol도 high로 둡니다.
- Sonnet 5.5는 단가가 Opus 5.5의 절반이지만 토큰을 더 써서 작업당 비용이 비슷하므로 구현에 쓰지 않습니다.

리뷰에 GPT-6.2 Astra 대신 Sol을 쓰는 이유: OpenAI 발표에서 Sol은 병합 가능한 변경인지를 보는 FrontierCode 2.0에서 Astra와 0.5점 이내이고 비용은 약 5분의 1입니다. ChatGPT 구독(`openai-codex`)에서 Astra의 컨텍스트는 272K로 Sol(500K)보다 작아 큰 diff 리뷰에도 불리합니다.

모델을 쓸 수 없을 때(한도 초과 등)는 남은 턴을 GPT-6.2 Sol high로 이어 갑니다. 리뷰와 UI 검증은 반대로 Opus 5.5로 넘깁니다.

## 위임 규칙

`AGENTS.md`는 메인 세션과 Paseo나 Orca가 띄운 omp 워커만 읽고, task 서브에이전트는 읽지 않습니다. 담긴 내용은 다음과 같습니다.

- **개발 단계**: 기획서부터 PR까지 7단계와 단계마다 쓸 스킬, 사용자 확인 지점. [run-flow](skills/run-flow.md)를 실행하면 이 순서를 이어서 진행합니다.
- **위임**: 작업마다 맡길 에이전트. 에이전트 하나에는 목적 하나만 맡기고, 목적은 받은 결과를 확인할 기준으로 가릅니다. 확인할 기준이 다르면 에이전트를 나눕니다. 기준이 섞인 결과는 메인 세션이 리뷰하거나 버그와 AI slop을 찾기 어렵기 때문입니다. 다만 완성도가 먼저이므로 맥락을 잃는 분리는 하지 않습니다. 작성이나 구현을 맡은 에이전트가 자기 산출물의 검증과 결과 반영까지 책임지고, 냉독 읽기나 화면 확인처럼 새 컨텍스트가 필요한 검증만 별도 에이전트가 하되 그 결과는 산출물을 만든 쪽이 받아 반영합니다. 교차 리뷰는 bundled reviewer, 리뷰 스킬과 그 하위 리뷰는 code-reviewer에 맡깁니다. 둘 다 다른 회사 모델(GPT)이라 구현한 모델과 다른 실수를 잡습니다. reviewer는 버그만 보고하는 형식이 고정돼 있어 리뷰 스킬의 지시를 따르지 못하므로 따로 둡니다.
- **넘기는 것**: 구현·테스트·UI 에이전트에는 대화 기록 대신 brief와 티켓 하나, 레포 규칙 파일 경로, 검증 명령, 앞 티켓 산출물을 넘깁니다. 리뷰 에이전트에는 diff 범위와 brief를, doc-writer에는 diff 전문 대신 변경 파일 목록, 완료 기록, 리뷰 기록을 넘깁니다.
- **실패했을 때**: implementer가 실패하면 실패 보고를 함께 넘겨 한 번 더 맡기고, 같은 티켓에서 2회 실패하면 hard-implementer에 맡깁니다. 그래도 실패하거나 실패 원인이 티켓의 모호함이면 멈추고 티켓을 다시 나누자고 제안합니다. 처음부터 대규모 리팩터링이나 원인 모를 디버깅이면 바로 hard-implementer에 맡깁니다. 구현 워커(Paseo나 Orca 워커)는 직접 구현해 실패하면 바로 hard-implementer에 맡깁니다. 통합 검증 실패처럼 고치지 않고 원인 보고만 필요하면 root-cause에 맡깁니다.
- **워커**: 함께 시작할 수 있는 티켓이 둘 이상이라 worktree를 나눠 병렬로 실행할 때, 다른 에이전트에게 맡길 때, 사용자가 워커를 직접 볼 때만 Paseo나 Orca 워커를 씁니다. 둘 다 쓸 수 있으면 Paseo를 씁니다([Paseo 오케스트레이션 설정](paseo-orchestration.md)). 티켓 구현 워커는 Paseo에서는 Opus 5.5 medium, Orca에서는 Opus 5.5 xhigh로 띄우고, 구현과 테스트를 implementer에 맡기지 않고 직접 합니다. 워커와 implementer의 모델이 같아서 맡기면 같은 문서를 두 번 읽기 때문입니다. 화면 검증만 ui-checker에 맡깁니다. 바꾸려면 Paseo는 `ticket-worker` 프로필을, Orca는 `modelRoles.worker`를 고칩니다. 교차 리뷰는 메인 세션이 아니라 변경을 구현한 모델과 다른 회사의 모델이 맡습니다. 이 설정에서 구현 에이전트와 구현 워커는 모두 Claude이므로 메인 세션의 모델과 상관없이 reviewer(GPT)가 맡습니다.

여러 티켓을 병렬로 실행하는 과정은 [run-ticket](skills/run-ticket.md#여러-티켓-실행)에 있습니다.

## 확인하기

새 omp 세션에서 확인합니다.

- `/agents`에 brief-writer, cold-reader, implementer, hard-implementer, root-cause, test-writer, ui-checker, doc-writer, code-reviewer가 보이는지
- 에이전트를 한 번씩 실행했을 때 세션 폴더(`~/.omp/agent/sessions/<프로젝트>/<세션>/`)의 에이전트별 기록에 위 표의 모델이 찍히는지
- hard-implementer를 실행한 뒤 그 에이전트 폴더에 `__advisor.jsonl`이 생기는지. 자문 모델(Opus 5.5)의 기록입니다.

## 모델 바꾸기

- 단계의 모델은 `modelRoles`에서 그 역할만 바꿉니다. 에이전트 파일은 `@task`처럼 역할을 가리키므로 고치지 않아도 됩니다. 교차 리뷰용 Claude Code·Codex 워커의 모델만 `AGENTS.md`의 "워커" 절에 직접 적혀 있습니다. omp 역할은 다른 에이전트의 워커에 쓸 수 없기 때문입니다.
- 비용을 줄이려면 모델을 바꾸기 전에 Effort부터 내립니다.
- `max`는 기본값으로 쓰지 않습니다. 비용이 크게 늘고 점수가 오히려 떨어지기도 합니다.
- 한 대화 안에서는 Effort를 바꾸지 않습니다. 바꾸면 프롬프트 캐시가 무효화됩니다.

## 알아 둘 점

- **실패 시 승격은 설정이 아니라 규칙입니다.** omp의 대체 모델은 모델을 쓸 수 없을 때만 동작합니다. implementer에서 hard-implementer로 올리는 판단은 `AGENTS.md`를 읽은 메인 세션이 합니다.
- **승격은 한 단계입니다.** Opus 5.5 xhigh에서 바로 Fable 5.2 high + Opus 5.5 xhigh 자문으로 올립니다. 그 사이에 단계를 넣으려면 그 모델을 `model:`에 적은 에이전트를 하나 더 만들고 `AGENTS.md`의 "실패했을 때"에 넣습니다.
- **Fable 5.2 한도**: 구독에서 Fable 한도가 Opus와 따로 잡히면 hard-implementer가 먼저 한도에 걸릴 수 있습니다. 그때는 `retry.fallbackChains.slow`에 따라 Opus 5.5 xhigh로 이어 갑니다.
- **입력 크기로 모델을 고르는 설정은 없습니다.** GPT는 입력이 272K 토큰을 넘으면 입력 단가가 2배, 출력 단가가 1.5배가 되므로, `AGENTS.md`가 큰 diff를 디렉터리별로 나눠 리뷰를 맡기게 합니다.
- **자문은 hard-implementer에만 붙습니다.** 에이전트 파일의 `advisor: true`는 전체 설정 `advisor.enabled: false`와 상관없이 그 에이전트에만 자문을 붙입니다. 자문은 붙은 세션의 모든 턴을 읽으므로 메인 세션에는 켜지 않습니다.
- **Haiku 5.5의 컨텍스트는 100K입니다.** 다른 모델(1M)보다 작으므로 scout에는 찾을 범위를 좁혀 맡깁니다.

---

[문서 목록](README.md) · [README](../README.md)
