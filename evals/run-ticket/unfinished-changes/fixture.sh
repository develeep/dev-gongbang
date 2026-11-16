mkdir -p docs/context/2026-10-22-greeting src
cat > src/greet.py <<'PY'
def greet(name):
    return "hello " + name
PY
cat > src/farewell.py <<'PY'
def farewell(name):
    return "bye " + name
PY
cat > docs/context/2026-10-22-greeting.md <<'MD'
# 인사말을 대문자로 바꾸고 느낌표를 붙인다

- 기준 커밋: `c3d4e5f`
- 작성일: 2026-10-22

## 티켓
- [x] [01: 대문자 변환](./2026-10-22-greeting/01-upper.md)
- [ ] [02: 느낌표 추가](./2026-10-22-greeting/02-exclaim.md)
MD
cat > docs/context/2026-10-22-greeting/02-exclaim.md <<'MD'
# 02: 느낌표 추가

- 부모: [인사말을 대문자로 바꾸고 느낌표를 붙인다](../2026-10-22-greeting.md)
- 막힘 관계: 01: 대문자 변환
- 상태: ready-for-agent

## 만들 것
`greet("a")`가 `HELLO A!`를 돌려준다.

## 완료 기준
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from greet import greet; print(greet('a'))"` → `HELLO A!`
MD
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
start=$(git rev-parse --short HEAD)

# 01 티켓의 변경. 완료 기록의 "바꾼 파일"에 있다.
cat > src/greet.py <<'PY'
def greet(name):
    return ("hello " + name).upper()
PY
cat > docs/context/2026-10-22-greeting/01-upper.md <<MD
# 01: 대문자 변환

- 부모: [인사말을 대문자로 바꾸고 느낌표를 붙인다](../2026-10-22-greeting.md)
- 막힘 관계: 없음 (바로 시작 가능)
- 상태: done

## 만들 것
\`greet("a")\`가 \`HELLO A\`를 돌려준다.

## 완료 기준
- [x] \`python3 -c "import sys; sys.path.insert(0,'src'); from greet import greet; print(greet('a'))"\` → \`HELLO A\`

## 완료 기록
- 완료일: 2026-10-22
- 커밋: 안 함 (작업 시작 HEAD \`$start\`)
- 바꾼 파일: \`src/greet.py\`
MD

# 어느 완료 기록에도 없는 변경. 끊긴 작업의 미완성 변경일 수 있다.
cat > src/farewell.py <<'PY'
def farewell(name):
    return "bye " + name +
PY
