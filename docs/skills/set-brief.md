<p align="right"><b>한국어</b> · <a href="../en/skills/set-brief.md">English</a></p>

[README](../../README.md) › [문서](../README.md) › set-brief

# set-brief

대화에서 확정한 내용을 작업 지시서(brief) 하나로 남긴다. 이 brief를 읽는 사람은 대화를 보지 못한 작업자나 다른 에이전트다. brief만 읽고 작업해도 대화 맥락을 가진 에이전트와 같은 결과가 나오게 쓴다.

> 만드는 중인 스킬이다. `gongbang-dev`를 설치해야 쓸 수 있고, 동작이 바뀔 수 있다.

| 항목 | 값 |
|---|---|
| 버킷 | in-progress |
| 호출 방식 | User-invoked |
| 호출 | `/gongbang:set-brief [남길 작업 요약]` |
| 원문 | [SKILL.md](../../skills/in-progress/set-brief/SKILL.md) |

**목차**: [언제 쓰나](#언제-쓰나) · [준비물](#준비물) · [진행 과정](#진행-과정) · [결과물](#결과물) · [커스텀](#커스텀) · [함께 쓰는 스킬](#함께-쓰는-스킬)

## 언제 쓰나

- 한 세션에서 끝나지 않는 작업을 다음 세션이나 다른 에이전트에 넘긴다.
- framing-problems로 확정한 구체화 기록을 작업 지시서로 바꾼다.

## 준비물

- GitHub 이슈로 남기려면 `git remote -v`에 github.com이 있고 `gh auth status`가 성공해야 한다. 아니면 docs 문서를 추천한다.
- 냉독 검증에는 Agent 도구가 필요하다. 없으면 그 단계를 건너뛰고 알린다.

## 진행 과정

1. 구체화 기록과 그 뒤에 한 작업(바꾼 파일, 커밋, 새 결정)을 모은다. 기록이 없으면 대화에서 확인된 사실과 합의한 결정만 모은다.
2. 저장 위치를 고른다. GitHub 이슈 또는 `docs/context/` 문서다.
3. 템플릿으로 초안을 쓴다. 목적이 여럿이면 쓰기 전에 brief를 나눌지 묻는다.
4. 대화 내용 없이 초안만 받은 서브에이전트 3개에게 같은 질문을 하고, 답이 합의와 어긋나거나 서로 갈리는 곳의 문장을 고친다. 이 과정을 냉독 검증이라 부른다.
5. 초안, 고친 항목, 실행할 외부 작업을 보여 주고 확인받는다. 공개 저장소면 비밀값, 내부 URL, 개인 정보가 없는지 확인을 요청한다.
6. 게시한다.

## 결과물

- **GitHub 이슈**: `context` 라벨을 붙여 만든다. 라벨이 없으면 새로 만든다. 다음 세션은 `gh issue list --label context`로 목록을 본다.
- **docs 문서**: `docs/context/YYYY-MM-DD-<slug>.md`로 저장하고, 같은 디렉터리의 `README.md`에 한 줄을 추가한다. 커밋은 하지 않는다.

brief에는 요약, 배경·의도, 최종 목적, 확인된 사실, 합의한 작업, 작업 경계, 하면 안 되는 것, 확인 기준, 미확인·위험 섹션이 있다. 내용이 없는 섹션은 지운다.

## 커스텀

| 바꾸고 싶은 것 | 고칠 곳 |
|---|---|
| brief 섹션 구성 | SKILL.md의 "기록 템플릿" |
| docs 저장 경로와 파일 이름 | SKILL.md의 "2. 저장 위치 선택", "6. 게시와 인덱스 갱신" |
| 냉독 검증 질문 | SKILL.md의 "4. 냉독 검증" |

섹션 이름, "남은 일" 같은 줄 이름, `- 작성일: YYYY-MM-DD` 줄을 바꾸면 set-ticket과 run-ticket도 함께 고쳐야 한다. 두 스킬이 이 이름과 `^- 작성일: ` 정규식으로 brief를 찾고 읽는다. 복사해서 고치는 방법은 [커스텀 가이드](../customization.md)를 본다.

## 함께 쓰는 스킬

- **framing-problems**: 먼저 구체화 기록을 확정하면 그 기록을 기준으로 brief를 쓴다.
- **set-ticket**: "남은 일"이 새 컨텍스트 창 하나로 끝나지 않을 크기면 티켓으로 나눈다.
- **run-ticket**: 한 창으로 끝날 크기면 새 세션에서 바로 실행한다.

set-ticket과 run-ticket은 User-invoked라 set-brief가 직접 부르지 않는다. 게시를 마치면 어느 쪽을 실행할지 안내한다.

---

← 이전: [check-guidelines](check-guidelines.md) · [문서 목록](../README.md) · 다음: [set-ticket](set-ticket.md) →
