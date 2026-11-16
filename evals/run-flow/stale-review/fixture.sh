mkdir -p docs/context/2026-10-22-greeting src
cat > src/greet.py <<'PY'
def greet(name):
    return "hello " + name
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
  - [x] 느낌표 추가

## 확인 기준
- `python3 -c "import sys; sys.path.insert(0,'src'); from greet import greet; print(greet('a'))"` → `HELLO A!`

## 티켓
- [x] [01: 대문자 변환](./2026-10-22-greeting/01-upper.md)
- [x] [02: 느낌표 추가](./2026-10-22-greeting/02-exclaim.md)
MD
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm "docs: 인사말 brief와 티켓 추가"
start=$(git rev-parse --short HEAD)

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
git add -A && git -c user.name=t -c user.email=t@t commit -qm "feature: 인사말 대문자 변환"

cat > src/greet.py <<'PY'
def greet(name):
    return ("hello " + name).upper() + "!"
PY
cat > docs/context/2026-10-22-greeting/02-exclaim.md <<MD
# 02: 느낌표 추가

- 부모: [인사말을 대문자로 바꾸고 느낌표를 붙인다](../2026-10-22-greeting.md)
- 막힘 관계: 01: 대문자 변환
- 상태: done

## 만들 것
\`greet("a")\`가 \`HELLO A!\`를 돌려준다.

## 완료 기준
- [x] \`python3 -c "import sys; sys.path.insert(0,'src'); from greet import greet; print(greet('a'))"\` → \`HELLO A!\`

## 완료 기록
- 완료일: 2026-10-22
- 커밋: 안 함 (작업 시작 HEAD \`$start\`)
- 바꾼 파일: \`src/greet.py\`
MD
git add -A && git -c user.name=t -c user.email=t@t commit -qm "feature: 인사말 끝에 느낌표 추가"

mkdir -p docs/context/run-flow
head=$(git rev-parse --short HEAD)
cat > docs/context/run-flow/2026-10-22-greeting.md <<MD
# 인사말을 대문자로 바꾸고 느낌표를 붙인다

- 시작일: 2026-10-22
- 현재 단계: 6. 머지·PR 결정
- 멈춘 이유: 6단계에서 멈추기를 고름. run-flow를 이 상태 파일을 인자로 다시 실행한다

## 단계
- [x] 0. 시작 단계 고르기
- [-] 1. 요구사항 정리
- [x] 2. 구체화
- [x] 3. 작업 지시서
- [x] 4. 티켓 분할
- [x] 5. 구현과 리뷰
- [ ] 6. 머지·PR 결정
- [ ] 7. PR 만들기

## 결과물
- brief: docs/context/2026-10-22-greeting.md
- 시작 HEAD: $start

## 리뷰
- 통합 리뷰: 완료 (HEAD $head, 코드 지문 4b825dc642cb6eb9a060e54bf8d69288fbee4904)
- brief 확인 기준: \`greet('a')\` → \`HELLO A!\`: 통과
MD
git add -A && git -c user.name=t -c user.email=t@t commit -qm "docs: 흐름 상태 파일 추가"

# 리뷰한 뒤에 코드가 바뀌었다. 커밋하지 않은 변경이다.
cat > src/greet.py <<'PY'
def greet(name):
    return ("hello " + name.strip()).upper() + "!"
PY
