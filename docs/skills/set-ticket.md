<p align="right"><b>한국어</b> · <a href="../en/skills/set-ticket.md">English</a></p>

# set-ticket

set-brief로 남긴 brief 하나를 티켓 여러 개로 나눈다. 티켓 하나만 읽고 그 티켓의 작업을 끝낼 수 있게 쓰고, 원래 brief에 티켓 목록을 연결한다.

> 만드는 중인 스킬이다. `gongbang-dev`를 설치해야 쓸 수 있고, 동작이 바뀔 수 있다.

| 항목 | 값 |
|---|---|
| 버킷 | in-progress |
| 호출 방식 | User-invoked |
| 호출 | `/gongbang:set-ticket [brief 이슈 번호·URL 또는 docs 경로]` |
| 원문 | [SKILL.md](../../skills/in-progress/set-ticket/SKILL.md) |

## 언제 쓰나

- brief의 "남은 일"이 새 컨텍스트 창 하나로 끝나지 않을 만큼 크다.

## 준비물

- set-brief로 만든 brief. 인자를 주지 않으면 이 대화에서 방금 게시한 brief, 그다음 가장 최근 brief 순서로 찾는다. 이미 티켓으로 나눴거나 끝난 brief는 건너뛴다.
- GitHub 이슈 brief면 `gh` CLI가 로그인돼 있어야 한다.

## 진행 과정

1. brief를 찾아 끝까지 읽는다.
2. brief가 다루는 영역의 코드를 살펴본다. 용어집이나 ADR이 있으면 따르고, 구현을 쉽게 만드는 선행 리팩터링을 찾는다.
3. 분할안을 쓴다.
   - 티켓마다 필요한 모든 계층(스키마, API, UI, 테스트)을 좁게 관통하는 수직 슬라이스로 자른다.
   - 티켓마다 완료 기준과 막힘 관계(먼저 끝나야 하는 티켓)를 정한다.
   - 한 티켓의 결과를 다른 티켓이 쓰면 "NN 티켓의 산출물"로 가리킨다.
   - 어떤 슬라이스도 혼자 초록 상태가 될 수 없는 넓은 리팩터링은 expand → migrate → contract 순서로 나눈다.
4. 분할안을 번호 목록으로 보여 주고 크기, 막힘 관계, 합치거나 나눌 티켓을 묻는다. 승인할 때까지 고친다.
5. 막힘 관계 순서대로 게시하고 brief에 "티켓" 섹션을 덧붙인다.

## 결과물

- **GitHub 이슈**: `ready-for-agent` 라벨을 붙인 티켓 이슈를 brief의 sub-issue로 연결하고, 막힘 관계를 이슈 의존성으로 연결한다. 연결에 실패하면 본문에 적는다.
- **docs 문서**: brief 옆 `docs/context/YYYY-MM-DD-<brief-slug>/` 폴더에 `NN-<slug>.md`로 티켓을 저장한다. 상태는 `ready-for-agent`로 시작한다. 커밋은 하지 않는다.

brief는 닫지 않고, "티켓" 섹션을 덧붙이는 것 외에는 고치지 않는다.

## 커스텀

| 바꾸고 싶은 것 | 고칠 곳 |
|---|---|
| 티켓 섹션 구성 | SKILL.md의 "이슈 티켓 템플릿", "docs 티켓 템플릿" |
| 분할 기준 | SKILL.md의 "핵심 규칙" 1~2, "3. 분할안 작성" |
| 라벨 이름 | SKILL.md의 "5. 게시와 brief 연결" |

티켓 템플릿의 섹션 이름이나 `- 상태:` 줄을 바꾸면 run-ticket도 함께 고쳐야 한다. 복사해서 고치는 방법은 [커스텀 가이드](../customization.md)를 본다.

## 함께 쓰는 스킬

- **set-brief**: 나눌 brief를 만든다.
- **run-ticket**: 게시한 티켓을 새 세션에서 하나씩 실행한다. User-invoked라 set-ticket이 직접 부르지 않고 실행 방법을 안내한다.
