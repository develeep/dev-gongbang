<p align="right"><b>한국어</b> · <a href="../en/skills/building-skills.md">English</a></p>

# building-skills

스킬을 명세에 맞추고, 실제로 돌려 봤을 때 스킬 없이 할 때보다 나은 상태까지 다듬는다. Claude 공식 skill best practice와 Agent Skills 명세를 기준으로 정적 검사, 실행 테스트, 사람 리뷰, 수정을 반복한다.

| 항목 | 값 |
|---|---|
| 버킷 | productivity |
| 호출 방식 | User-invoked |
| 호출 | `/gongbang:building-skills [스킬 폴더 경로, SKILL.md 초안, 또는 만들 스킬 설명]` |
| 원문 | [SKILL.md](../../skills/productivity/building-skills/SKILL.md) |

## 언제 쓰나

입력에 따라 세 모드 중 하나로 진행한다.

| 모드 | 입력 |
|---|---|
| A. prompt-builder 이어받기 | prompt-builder 출력(설계 요약, SKILL.md 코드블록, 다음 단계) |
| B. 기존 스킬 개선 | 스킬 폴더나 SKILL.md |
| C. 단독 신규 | 만들 스킬 설명, 대화 기록, 런북, 코드, 리뷰 코멘트 같은 자료 |

## 준비물

- Python 3.9 이상. 번들 스크립트는 표준 라이브러리만 쓴다.
- 대표 요청 3개. Model-invoked 스킬이면 비슷하지만 스킬을 쓰면 안 되는 요청(near-miss) 2개도 준비한다. 없으면 스킬이 초안 3개를 보여 주고 승인받는다.
- 검증 3단계(description 측정)를 고르면 `claude` CLI가 필요하다.

## 진행 과정

1. 입력을 보고 모드를 정한다. 모드 B는 고치기 전에 원본을 `<name>-workspace/skill-snapshot/`에 복사해 비교 기준으로 둔다.
2. 사양표(K1~K10)를 `항목 | 값 | 출처 | 상태` 표로 보여 주고, 모호하거나 없는 항목만 묻는다.
3. 작성 규칙에 따라 SKILL.md와 번들 파일을 쓰거나 고친다. 형식 문제는 바로 고치고, 내용은 넣을 문장을 그대로 제안해 승인받는다.
4. `scripts/check_skill.py`로 정적 검사를 하고 ERROR가 없어질 때까지 고친다.
5. 검증 강도를 고른다. 단계는 누적된다.

   | 단계 | 하는 일 | 비용 |
   |---|---|---|
   | 1. 점검 (기본) | 대표 요청을 스킬을 쓴 실행으로만 돌리고 채점·리뷰 | 서브에이전트 3개 안팎 |
   | 2. 비교 | 1에 더해 기준 실행(스킬 없이, 또는 스냅숏)과 비교 | 서브에이전트 6개 이상 |
   | 3. description | 2에 더해 description의 실행 여부를 측정하고 다듬음 | `claude -p` 수십 회 이상 |

   User-invoked 스킬은 이름으로 부르므로 3단계를 쓰지 않는다.
6. 테스트를 만들어 실행하고 채점한다. 테스트 결과는 스킬 폴더 옆 `<name>-workspace/`에 쌓인다.
7. 결과를 분석하기 전에 리뷰 페이지(`review.html`)부터 전달한다. 케이스마다 피드백을 적고 "피드백 내보내기"를 누르면 `feedback.json`이 내려받아진다. 그 파일을 돌려준다.
8. 실패한 assertion, 피드백, 실행 기록으로 원인을 찾아 수정안을 표로 보여 준다. 고친 뒤 6단계부터 반복한다.
9. 마지막 정적 검사 후 전달한다.

## 결과물

- 완성한 스킬 폴더
- 번들 파일이나 추가 frontmatter가 있으면 `<name>.skill` 패키지. Claude Code에서는 `~/.claude/skills/<name>/`(사용자)이나 `.claude/skills/<name>/`(프로젝트)에 복사해 쓸 수도 있다.
- 마무리 보고: 최종 통과율과 반복 횟수, 반영한 수정, 남은 WARN·실패·승인받지 못한 수정안

## 커스텀

| 바꾸고 싶은 것 | 고칠 파일 |
|---|---|
| 스킬 작성 규칙과 사람 검토 체크리스트 | `references/authoring-rules.md` |
| 사양표 항목, 모드별 입력 처리 | `references/intake.md` |
| 테스트 작성·채점 방법, 진단표 | `references/evaluation.md` |
| description 다듬는 절차 | `references/description-tuning.md` |
| 기계로 확인하는 규칙 | `scripts/check_skill.py` |

복사해서 고치는 방법은 [커스텀 가이드](../customization.md)를 본다.

## 함께 쓰는 스킬

- **prompt-builder**: SKILL.md 초안을 prompt-builder로 만들고 그 출력을 넘기면 모드 A로 이어받는다. prompt-builder가 이미 확인받은 값은 다시 묻지 않는다.
- 이 저장소의 스킬을 고친 뒤 모드 B로 시험할 수 있다. 방법은 [커스텀 가이드](../customization.md#고친-스킬-시험하기)에 있다.
