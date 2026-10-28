mkdir -p .claude/rules
cat > .claude/rules/python.md <<'MD'
---
paths:
  - "**/*.py"
---

# Python

- 함수에는 매개변수와 반환값 타입 힌트를 단다.
MD
n=0
for d in billing catalog shipping; do
  mkdir -p "$d"
  for i in $(seq 1 44); do
    n=$((n + 1))
    printf 'def fn_%d(value: int) -> int:\n    return value + %d\n' "$n" "$n" > "$d/mod_$i.py"
  done
done
# 구역마다 위반 하나씩
printf 'def fn_v1(value):\n    return value * 2\n' > billing/mod_7.py
printf 'def fn_v2(value):\n    return value * 3\n' > catalog/mod_21.py
printf 'def fn_v3(value):\n    return value * 4\n' > shipping/mod_35.py
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
