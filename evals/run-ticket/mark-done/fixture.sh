mkdir -p docs/context/2026-10-22-greeting src
cat > src/greet.py <<'PY'
def greet(name):
    return "hello " + name
PY
cat > docs/context/2026-10-22-greeting.md <<'MD'
# 인사말에 느낌표를 붙인다

- 기준 커밋: `c3d4e5f`
- 작성일: 2026-10-22

## 티켓
- [ ] [01: 느낌표 추가](./2026-10-22-greeting/01-exclaim.md)
MD
cat > docs/context/2026-10-22-greeting/01-exclaim.md <<'MD'
# 01: 느낌표 추가

- 부모: [인사말에 느낌표를 붙인다](../2026-10-22-greeting.md)
- 막힘 관계: 없음 (바로 시작 가능)
- 상태: ready-for-agent

## 만들 것
`greet("a")`가 `hello a!`를 돌려준다.

## 완료 기준
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from greet import greet; print(greet('a'))"` → `hello a!`
MD
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
