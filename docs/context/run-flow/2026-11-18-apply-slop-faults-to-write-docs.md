# write-docs의 원칙과 검토 항목이 어색한 단어 조합과 빈 문장·엇나간 강조를 다룬다

- 시작일: 2026-11-18
- 현재 단계: 5. 구현과 리뷰
- 멈춘 이유: 없음

## 단계
- [x] 0. 시작 단계 고르기
- [-] 1. 요구사항 정리
- [x] 2. 구체화
- [x] 3. 작업 지시서
- [-] 4. 티켓 분할
- [ ] 5. 구현과 리뷰
- [ ] 6. 머지·PR 결정
- [ ] 7. PR 만들기

## 결과물
- 요구사항 문서: 없음 (요청 문장으로 시작)
- 개발 범위: 요청 문장 "https://zonderlabs.com/slop 글의 핵심 개념을 skills/productivity/write-docs/ 스킬에 적용"
- brief: https://github.com/develeep/dev-gongbang/issues/25
- brief 초안:
- brief 냉독 결과:
- ADR:
- 브랜치: feature/write-docs-slop-faults (worktree /root/dev-gongbang-write-docs-slop)
- 시작 HEAD: a7d2645
- Orca Run:
- PR:

## 결정
- 0단계: 인자가 요청 문장이라 2단계부터 시작. 참고 글(웹 글)은 기획서가 아니라서 1단계를 건너뜀
- 2단계: 구체화 기록 확정. ADR 후보 없음(모든 결정이 문서 수정이라 되돌리기 쉬움)
- 2단계: Q7 답 "ㅁ"을 한글 자판 a 자리로 보고 (a) eval 케이스 추가로 받음
- 3단계: brief 저장 위치 GitHub 이슈 (develeep/dev-gongbang, 공개, context 라벨)
- 3단계: 새 eval 케이스의 grader를 모두 통과해야 완료. 통과 못하면 원칙 문구를 고쳐 다시 실행 (Q1 a)
- 3단계: 출처 줄은 `clear-writing.md` 원칙 8 바로 아래, 원칙 4 새 문장과 원칙 8의 출처라고 범위를 밝힘 (Q2 a)
- 3단계: 5단계는 a7d2645에서 만든 별도 worktree `/root/dev-gongbang-write-docs-slop`에서 진행, 상태 파일도 옮김. 버전 1.11.0, 6단계에서 master 버전이 이미 1.11.0이면 1.12.0 (Q3 a). 계기: 흐름 도중 /root/dev-gongbang에 prompt-builder 변경과 plugin.json 1.11.0 미커밋 변경이 생김
- 3단계: 사용 문서 한·영 :40 패턴 목록에 새 패턴 두 개 추가 (Q4 네)
- 3단계: 원칙 문구와 eval 세부는 작업자가 정하고 6단계 diff에서 확인. 구현자는 커밋·push·PR을 하지 않음
- 3단계: brief를 이슈 #25로 게시. "남은 일"이 새 컨텍스트 창 하나로 끝날 크기라 4단계를 건너뛰고 5단계로
- 5단계: 작업 브랜치 feature/write-docs-slop-faults, worktree /root/dev-gongbang-write-docs-slop. 상태 파일을 worktree로 옮겨 커밋

## 요구사항 답변

## 구체화 기록
| 항목 | 내용 | 출처 | 근거 |
|---|---|---|---|
| R1 의도 | zonderlabs 글의 핵심 개념(명료하지 않은 글 = AI slop, 결함 3가지)을 write-docs에 반영해 쓴 글·고친 글에 그 결함이 남지 않게 한다 | 사용자 | - |
| R1 계기 | 글을 읽고 예방 차원에서 반영. write-docs 결과물의 실패 사례는 없음 | 사용자 (Q1 a) | - |
| R2 이상 | write-docs가 쓰거나 고친 글에 글의 결함 3가지(인물·행동 숨기기, 모호한 단어, 빈 문장·엇나간 강조)가 남지 않는다 | 사용자 | R1 의도 |
| R2 현재 | 결함 1, 결함 2의 지시어·명사 나열은 이미 다룸: `clear-writing.md` 원칙 2·4·7, `tech-writing.md` 3.1·3.3-1·3.4, `SKILL.md` "주의할 점" | `skills/productivity/write-docs/` | - |
| R2 현재 | 빈 곳 두 가지: (1) 사람이 대상을 보통 부르는 이름 대신 어색한 단어 조합을 쓰는 것을 막는 규칙 없음 (원칙 4 "즉석 이름표"만 일부 다룸) (2) 문장의 요점을 주절에 두고 내용 없는 문장을 지우라는 규칙 없음 (원칙 1·6만 일부 다룸) | `reference/clear-writing.md`, `SKILL.md` | - |
| R2 문제 | 이상은 결함 3가지가 남지 않는 것인데, 현재는 빈 곳 두 가지가 규칙과 검토 항목에 없다 | - | R2 이상, R2 현재 |
| R2 원인 | 빈 곳 두 가지가 원칙과 5단계 검토 항목에 없어 결과물에 남을 수 있다 (가설) | - | R2 현재 |
| R2 결정 | 글의 3분류를 새 검토 틀로 들이지 않고 빈 곳 두 가지만 원칙에 넣는다. 이미 있는 원칙은 그대로 둔다 | 사용자 (Q2 네) | R2 현재 |
| R3 제약 | 적용 범위는 모든 분야: `clear-writing.md` 원칙, `SKILL.md` "주의할 점"과 5단계 검토 | 사용자 (Q3 a) | R1 의도 |
| R3 제약 | 예시는 한국어 사례로 새로 만들고, 출처 줄에 글 URL과 Williams 책을 `tech-writing.md` 출처 줄 형식으로 적는다 | 사용자 (Q4 a) | R3 자원 |
| R3 자원 | `reference/clear-writing.md`(원칙 7개, 대비 예시), `SKILL.md` "주의할 점", `tech-writing.md` 출처 줄 형식, `evals/write-docs/` 케이스 4개, `docs/skills/write-docs.md`·`docs/en/skills/write-docs.md` | 저장소 | - |
| R4 근거 | 해당 없음: 비용이 큰 표준 영역이 아니고, 근거 자료는 사용자가 지정한 글(근거: Williams, *Style: The Basics of Clarity and Grace*). 영어의 "요점을 문장 끝에"는 한국어 어순에 맞춰 "요점을 주절에 둔다"로 옮긴다 | https://zonderlabs.com/slop | R3 제약 |
| R5 제안 해법 | 글의 핵심 개념을 write-docs에 적용 (채택: 해법 A로 구체화) | 사용자 | - |
| R5 목표 | 빈 곳 두 가지(어색한 단어 조합, 빈 문장·엇나간 강조)가 원칙과 검토 항목에 없는 상태를 바꾼다 | - | R2 원인 |
| R5 해법 | A: `clear-writing.md` 원칙 4에 "사람이 대상을 보통 부르는 이름으로 쓴다"는 문장 추가, 원칙 8 "요점을 주절에 두고, 요점이 없는 문장은 지운다" 신설, 대비 예시 2개, `SKILL.md` "주의할 점" 2개 항목, 출처 줄, `SKILL.md` "원칙 7개" → "8개" | 사용자 (Q5 a) | R2 결정, R3 제약 |
| R5 해법 | 대비 예시 2개: (1) "DB 준비 상태 점검은 세션 진입 경계에 자리한다." → "서버는 로그인 요청을 처리하기 전에 DB에 연결되는지 확인한다." (2) "결과 말고는 어떤 것도 다른 것에 기대지 않으므로, 빌드가 반환되는 대로 보고하겠습니다." → "빌드가 끝나면 결과를 알려 드릴게요." | 사용자 (Q6 네) | R3 제약 |
| R5 기각 | B(원칙 4·6·7에 흩어 넣기): 한 개념이 세 원칙에 흩어짐. C("주의할 점"만): 3단계에서 읽는 원칙 파일이 그대로라 쓰는 단계에 영향이 약함 | 사용자 (Q5 a) | R5 목표 |
| R6 부작용 | `evals/write-docs/` 채점 기준 18곳의 `SKILL.md:<줄>` 근거가 어긋남 → 완화: 같은 변경에서 줄 번호를 고친다 | `evals/write-docs/*/case.yaml` | R5 해법 |
| R6 부작용 | 스킬 동작 변경 → 완화: `plugin.json` 1.10.0 → 1.11.0, `docs/skills/write-docs.md`·`docs/en/skills/write-docs.md` 갱신(내용이 바뀐 부분이 있으면), `docs/customization.md`는 파일 구성이 같아 그대로, `scripts/check.py` 실행 | 사용자 (Q8 네), `.claude/CLAUDE.md` | R5 해법 |
| R6 부작용 | 원인이 가설 → 완화: eval 케이스 1개 추가. 두 결함이 든 초안을 "문장만"으로 다듬게 하고, 결함을 고쳤는지와 사실을 지켰는지 채점 | 사용자 (Q7 a) | R2 원인 |
| R6 장애물 | 현재 브랜치가 `master`이고 무관한 작업 트리 변경(수정 4개, 새 파일 2개)이 있음 → 감수: 5단계에서 작업 브랜치 이름을 묻고, 무관한 변경은 이 흐름의 커밋에 넣지 않음 | `git status` | - |

## 구현 중 결정

## 리뷰
- 통합 리뷰: 안 함
