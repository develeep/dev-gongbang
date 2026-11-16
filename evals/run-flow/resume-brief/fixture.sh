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
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
