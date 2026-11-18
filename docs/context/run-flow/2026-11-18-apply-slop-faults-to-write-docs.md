# write-docs의 원칙과 검토 항목이 어색한 단어 조합과 빈 문장·엇나간 강조를 다룬다

- 시작일: 2026-11-18
- 현재 단계: 7. PR 만들기
- 멈춘 이유: 없음

## 단계
- [x] 0. 시작 단계 고르기
- [-] 1. 요구사항 정리
- [x] 2. 구체화
- [x] 3. 작업 지시서
- [-] 4. 티켓 분할
- [x] 5. 구현과 리뷰
- [x] 6. 머지·PR 결정
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
- 5단계: 통합 리뷰 뒤 brief 이슈 #25에 결과 코멘트를 남기고 닫음
- 6단계: PR 만들기. 커밋은 feature(스킬·문서·버전), eval(새 케이스), chore(상태 파일) 세 개로 나눔. ADR 후보 없음(구현 중 결정은 모두 문서·eval 문구라 되돌리기 쉬움)

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
- 원칙 4 끝에 두 문장을 덧붙이고, 출처 줄은 "원칙 4의 마지막 두 문장과 원칙 8"로 범위를 밝힘: 확인 기준의 `보통 부르는 이름` grep이 원칙 4 한 줄만 잡아야 함 (#25)
- 새 eval `coined-names-buried-point`의 분야를 "설명"으로 정함: 기술 문서면 `tech-writing.md`도 읽혀 `clear-writing.md`의 효과만 보기 어려움 (#25)
- eval 초안 문장은 원칙 8 본문의 예와 대비 예시 두 쌍을 피해 새 문장("결제 입구 지점에 자리합니다", "~라는 점이 핵심이라고 할 수 있습니다", "원활한 업무에 보탬이 되었으면 합니다")으로 씀: 예시를 옮기기만 해서 통과하지 못하게 함 (#25)
- eval 프롬프트 자료 줄에 "결제 입구 지점"의 뜻을 넣음: 뜻이 없으면 `[확인 필요]`가 정답이 되어 결함을 시험하지 못함 (#25)
- 구현 결과: brief 확인 기준 13개 통과. eval 1회 실행, with arm 3/3 PASS(1.00), without arm도 1.00이라 Δ 0.00. 이 케이스로는 새 규칙의 효과를 확인하지 못함 (implementer 보고)
- 구현 중 사고: implementer가 상대 경로로 메인 작업 트리(/root/dev-gongbang)의 write-docs 파일 4개를 잠시 고쳤다가 `git apply -R`로 되돌림. 메인 트리 write-docs 경로에 남은 변경 없음 확인 (Main, `git status`)

## 리뷰
- 통합 리뷰: 완료 (HEAD 1253628, 코드 지문 41d3df199b45c9b03b6801f8a8c80cb93cce6657)
- 교차 리뷰 모델: openai-codex/gpt-6.1-sol (reviewer). 코드 리뷰·규칙 검사도 같은 모델(code-reviewer)
- brief 확인 기준: 13개 모두 통과 (Main이 리뷰 지적 반영 뒤 작업 트리에서 다시 실행: check.py 0, 원칙 8, 원칙 4 grep 1줄, 출처 줄, 주의할 점 9, 원칙 7개 0·8개 1, 근거 18곳 출력 없음, case.yaml 5, version 한 줄, eval with 3/3 PASS)
- 규칙 검사 (check-guidelines, code-reviewer gpt-6.1-sol): 범위 내 위반 없음. `scripts/check.py` 종료 코드 0
- 교차 리뷰 (reviewer, openai-codex/gpt-6.1-sol): correct, 차단 0 권고 0, 신뢰도 0.94. brief 확인 기준 명령(check.py, 원칙 8개, 예시 블록, 출처, 주의할 점 9개, 근거 18곳, eval 5개, 버전 한 줄) 직접 실행해 통과 확인
- 코드 리뷰 (code-review, code-reviewer gpt-6.1-sol): Standards 0건. Spec 권고 1건: `coined-names-buried-point/case.yaml:39-40` 사실 grader가 원본에 없는 결제 중단 시점을 덧붙여도 통과시킴(without 1회차가 "시작 후 약 30분"으로 연결) → 고침: FAIL 조건에 원본에 없는 결제 중단 시작·끝 시각을 정하는 경우 추가, eval 재실행
- eval 재실행 2회차(grader 강화 후): with 0.89(3회차 facts FAIL), without 0.89, Δ 0. with 3회차 본문은 통과한 2회차와 같은 문장("배포는 금요일 오후 2시에 시작하고, 약 30분 동안 결제가 멈춥니다")이라 grader 문구가 judge를 과하게 엄격하게 만든 것으로 판단. without 1회차("배포가 시작되면 약 30분 동안")는 의도대로 FAIL → grader에 원본처럼 나란히 쓰면 PASS, 본문에 중단 시점을 특정하면 FAIL로 명시하고 3회차 실행. 스킬 문구는 고치지 않음
- eval 재실행 3회차: with 1.00(3/3 PASS), without 1.00, Δ 0.00. 완료 기준(with 전부 PASS) 충족. 새 규칙의 추가 효과는 이 케이스로 입증되지 않음
- 건너뛴 리뷰: 보안 리뷰: 인증·권한·결제·개인정보 코드를 다루지 않음(문서·eval 변경)
- 범위 밖 문제: `skills/productivity/building-skills/references/authoring-rules.md:77` W6 경고(시간에 따라 틀려질 표현), 배포 디렉터리 진단의 아이콘·임시 mod README 누락(실패 조건 아님)
