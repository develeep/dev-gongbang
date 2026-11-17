mkdir -p src
cat > src/greet.py <<'PY'
def greet(name):
    return ("hello " + name).upper()
PY
# brief와 상태 파일은 저장소 밖 폴더에 두고 .scratch 심볼릭 링크로 붙인다
ext="$(mktemp -d)"
mkdir -p "$ext/greeting/2026-10-22-greeting" "$ext/greeting/run-flow"
ln -s "$ext" .scratch
printf '.scratch\n' > .gitignore
cat > "$ext/greeting/2026-10-22-greeting.md" <<'MD'
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
cat > "$ext/greeting/2026-10-22-greeting/01-upper.md" <<'MD'
# 01: 대문자 변환

- 부모: [인사말을 대문자로 바꾸고 느낌표를 붙인다](../2026-10-22-greeting.md)
- 막힘 관계: 없음 (바로 시작 가능)
- 상태: done

## 만들 것
`greet("a")`가 `HELLO A`를 돌려준다.

## 완료 기준
- [x] `python3 -c "import sys; sys.path.insert(0,'src'); from greet import greet; print(greet('a'))"` → `HELLO A`
MD
cat > "$ext/greeting/2026-10-22-greeting/02-exclaim.md" <<'MD'
# 02: 느낌표 추가

- 부모: [인사말을 대문자로 바꾸고 느낌표를 붙인다](../2026-10-22-greeting.md)
- 막힘 관계: 01: 대문자 변환
- 상태: ready-for-agent

## 만들 것
`greet("a")`가 `HELLO A!`를 돌려준다.

## 완료 기준
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from greet import greet; print(greet('a'))"` → `HELLO A!`
MD
cat > "$ext/greeting/run-flow/2026-10-22-greeting.md" <<'MD'
# 인사말을 대문자로 바꾸고 느낌표를 붙인다

- 시작일: 2026-10-22
- 현재 단계: 5. 구현과 리뷰
- 멈춘 이유: 새 세션에서 이어 감. 이 상태 파일 경로를 인자로 run-flow를 다시 실행한다

## 단계
- [x] 0. 시작 단계 고르기
- [-] 1. 요구사항 정리
- [-] 2. 구체화
- [x] 3. 작업 지시서
- [x] 4. 티켓 분할
- [ ] 5. 구현과 리뷰
- [ ] 6. 머지·PR 결정
- [ ] 7. PR 만들기

## 결과물
- 요구사항 문서: 없음
- 개발 범위: 없음
- brief: `.scratch/greeting/2026-10-22-greeting.md`
- brief 초안:
- brief 냉독 결과:
- ADR:
- 브랜치: `feature/greet`
- 시작 HEAD:
- Orca Run:
- PR:

## 결정
- 상태 파일 위치: brief 옆 `.scratch/greeting/run-flow/` (사용자 결정)

## 구현 중 결정

## 리뷰
- 통합 리뷰: 안 함
MD
git init -q && git checkout -q -b feature/greet && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
