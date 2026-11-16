mkdir -p docs/context/2026-10-22-greeting src
cat > src/greet.py <<'PY'
def greet(name):
    return ("hello " + name).upper()
PY
cat > docs/context/2026-10-22-greeting.md <<'MD'
# 인사말을 대문자로 바꾸고 느낌표를 붙인다

- 기준 커밋: `c3d4e5f`
- 작성일: 2026-10-22

## 요약
`greet`가 돌려주는 인사말이 밋밋해서 화면에서 눈에 띄지 않는다.

## 최종 목적
`greet("a")`가 `HELLO A!`를 돌려준다.

## 합의한 작업
- 해법: 소문자 인사말을 대문자로 바꾸고 끝에 느낌표를 붙인다
- 남은 일:
  - [x] 대문자 변환
  - [ ] 느낌표 추가

## 확인 기준
- `python3 -c "import sys; sys.path.insert(0,'src'); from greet import greet; print(greet('a'))"` → `HELLO A!`

## 티켓
- [x] [01: 대문자 변환](./2026-10-22-greeting/01-upper.md)
- [ ] [02: 느낌표 추가](./2026-10-22-greeting/02-exclaim.md)
MD
cat > docs/context/2026-10-22-greeting/01-upper.md <<'MD'
# 01: 대문자 변환

- 부모: [인사말을 대문자로 바꾸고 느낌표를 붙인다](../2026-10-22-greeting.md)
- 막힘 관계: 없음 (바로 시작 가능)
- 상태: done

## 만들 것
`greet("a")`가 `HELLO A`를 돌려준다.

## 완료 기준
- [x] `python3 -c "import sys; sys.path.insert(0,'src'); from greet import greet; print(greet('a'))"` → `HELLO A`

## 완료 기록
- 완료일: 2026-10-22
- 커밋: 안 함 (작업 시작 HEAD `c3d4e5f`)
- 바꾼 파일: `src/greet.py`
MD
cat > docs/context/2026-10-22-greeting/02-exclaim.md <<'MD'
# 02: 느낌표 추가

- 부모: [인사말을 대문자로 바꾸고 느낌표를 붙인다](../2026-10-22-greeting.md)
- 막힘 관계: 01: 대문자 변환이 끝나야 한다
- 상태: ready-for-agent

## 만들 것
`greet("a")`가 `HELLO A!`를 돌려준다.

## 완료 기준
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from greet import greet; print(greet('a'))"` → `HELLO A!`
MD
mkdir -p docs/context/run-flow
cat > docs/context/run-flow/2026-10-22-greeting.md <<'MD'
# 인사말을 대문자로 바꾸고 느낌표를 붙인다

- 시작일: 2026-10-22
- 현재 단계: 5. 구현과 리뷰
- 멈춘 이유: 02 티켓 실행 중 세션 종료. `/run-flow docs/context/run-flow/2026-10-22-greeting.md`로 이어 간다

## 단계
- [x] 0. 시작 단계 고르기
- [-] 1. 요구사항 정리
- [x] 2. 구체화
- [x] 3. 작업 지시서
- [x] 4. 티켓 분할
- [ ] 5. 구현과 리뷰
- [ ] 6. 머지·PR 결정
- [ ] 7. PR 만들기

## 결과물
- 요구사항 문서: 없음 (요청 문장으로 시작)
- 개발 범위: 없음
- brief: [docs/context/2026-10-22-greeting.md](../2026-10-22-greeting.md)
- ADR: 없음
- 브랜치:
- PR:

## 결정
MD
cat > docs/context/run-flow/2026-10-01-login-rate-limit.md <<'MD'
# 로그인 시도를 IP당 분당 5회로 제한한다

- 시작일: 2026-10-01
- 현재 단계: 완료
- 멈춘 이유: 없음

## 단계
- [x] 0. 시작 단계 고르기
- [-] 1. 요구사항 정리
- [x] 2. 구체화
- [x] 3. 작업 지시서
- [-] 4. 티켓 분할
- [x] 5. 구현과 리뷰
- [x] 6. 머지·PR 결정
- [x] 7. PR 만들기

## 결과물
- 요구사항 문서: 없음 (요청 문장으로 시작)
- 개발 범위: 없음
- brief: 없음 (저장소에서 지움)
- ADR: 없음
- 브랜치: feature/login-rate-limit
- PR: https://github.com/example/app/pull/12

## 결정
- 6단계: PR 만들기
MD
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
