<p align="right"><b>한국어</b> · <a href="../en/skills/run-flow.md">English</a></p>

[README](../../README.md) › [문서](../README.md) › run-flow

# run-flow

기획서, 요청, brief 중 하나를 받아 요구사항 정리부터 PR 생성까지 개발 단계를 차례로 이어서 진행합니다. 단계마다 그 단계의 스킬을 대신 불러오므로, 단계마다 스킬을 실행하지 않고 각 스킬이 묻는 확인과 질문에만 답하면 됩니다.

> 만드는 중인 스킬입니다. `gongbang-dev`를 설치해야 쓸 수 있고, 동작이 바뀔 수 있습니다.

| 항목 | 값 |
|---|---|
| 버킷 | in-progress |
| 호출 방식 | User-invoked |
| 호출 | `/gongbang:run-flow [기획서 경로·링크 \| 요청 \| brief 경로·이슈 번호]` |
| 원문 | [SKILL.md](../../skills/in-progress/run-flow/SKILL.md) |

**목차**: [언제 쓰나](#언제-쓰나) · [준비물](#준비물) · [진행 과정](#진행-과정) · [결과물](#결과물) · [커스텀](#커스텀) · [함께 쓰는 스킬](#함께-쓰는-스킬)

## 언제 쓰나

- 기획서나 요청 하나로 PR까지 진행하고, 중간에는 확인과 질문에만 답하고 싶을 때
- 진행하다 멈춘 brief를 이어서 끝낼 때. 인자 없이 실행하면 끝나지 않은 brief를 찾아 이어 갑니다.
- 여러 기능을 동시에 진행할 때. 기능마다 Orca 작업 공간을 따로 만들고 각각 run-flow를 실행합니다.

## 준비물

- 단계 스킬: analyzing-requirements, framing-problems, set-brief, set-ticket, run-ticket. `gongbang`과 `gongbang-dev`를 함께 설치하면 모두 있습니다.
- 여러 티켓을 병렬로 실행하려면 Orca가 실행 중이고 `orchestration` 스킬이 설치돼 있어야 합니다. 없으면 티켓을 차례로 실행합니다.
- PR을 만들려면 github.com 원격과 로그인된 `gh` CLI가 있어야 합니다. 없으면 PR 본문만 보여 주고 멈춥니다.
- 단계마다 모델을 나눠 쓰려면 [omp 멀티에이전트 설정](../omp-orchestration.md)을 설치합니다.

## 진행 과정

0. 인자로 시작 단계를 고릅니다. 기획서면 1단계, 요구사항 문서나 요청 문장이면 2단계, brief면 티켓 상태에 따라 4~6단계부터 시작합니다. 인자가 없으면 끝나지 않은 brief를 찾고, 여럿이면 목록을 보여 주고 고르게 합니다.
1. **요구사항 정리**: analyzing-requirements로 기획서를 요구사항 문서로 정리합니다.
2. **구체화**: 개발 범위가 여럿이면 이번에 진행할 범위 하나를 고른 뒤, framing-problems로 구체화 기록을 확정합니다.
3. **작업 지시서**: set-brief로 brief를 남깁니다. 남은 일이 한 세션에 끝나지 않을 크기면 4단계로, 아니면 5단계로 갑니다.
4. **티켓 분할**: set-ticket으로 티켓을 나눠 게시합니다.
5. **구현과 리뷰**: run-ticket으로 남은 티켓 전부를 실행합니다. Orca가 있으면 티켓마다 워커를 띄워 병렬로 실행합니다. 티켓이 하나여도 새 컨텍스트의 워커나 서브에이전트에게 맡겨, 대화 없이 brief와 티켓만 보고 구현하게 합니다. 완료 기준을 통과하지 못한 티켓이 나오면 멈추고, 티켓을 다시 나눌지 묻습니다.
6. **머지·PR 결정**: 완료 기준 결과, 리뷰 지적, 바뀐 파일과 커밋을 모아 보여 주고 PR 만들기, 고치기, 멈추기 중 하나를 고르게 합니다.
7. **PR 만들기**: 필요하면 작업 브랜치를 만들고 커밋한 뒤, PR 본문을 써서 push하고 PR을 만듭니다.

각 단계 스킬이 묻는 확인(구체화 기록 확정, 요구사항 문서 저장 위치, brief 초안과 게시 위치, 티켓 분할안, Orca 실행 계획)은 그대로 묻습니다. run-flow가 없애는 것은 단계가 끝날 때마다 다음 스킬을 직접 실행하던 일입니다.

## 결과물

- 요구사항 문서, brief, 티켓, 구현 코드와 커밋
- GitHub PR. 머지는 사용자가 합니다.
- 마무리 보고: 단계별 결과물 위치, PR URL, 고치지 않은 리뷰 지적

## 커스텀

| 바꾸고 싶은 것 | 고칠 곳 |
|---|---|
| 인자별 시작 단계 | SKILL.md의 "0. 시작 단계 고르기" |
| 티켓 실행 방법 | run-ticket의 SKILL.md, 또는 레포 규칙에 티켓 실행 스킬 지정 |
| PR 본문 형식 | 레포의 PR 템플릿, 또는 SKILL.md의 "7. PR 만들기" |

단계 안의 동작은 각 단계 스킬에서 고칩니다. 복사해서 고치는 방법은 [커스텀 가이드](../customization.md)를 보세요.

## 함께 쓰는 스킬

- **analyzing-requirements**, **framing-problems**, **set-brief**, **set-ticket**, **run-ticket**: 단계마다 불러오는 스킬입니다. set-brief, set-ticket, run-ticket은 run-flow가 불러올 수 있도록, 사용자나 다른 스킬이 지시할 때만 쓰는 Model-invoked입니다.
- **orchestration**(Orca): 5단계의 병렬 실행과 교차 리뷰 워커에 씁니다.

---

← 이전: [check-guidelines](check-guidelines.md) · [문서 목록](../README.md) · 다음: [set-brief](set-brief.md) →
