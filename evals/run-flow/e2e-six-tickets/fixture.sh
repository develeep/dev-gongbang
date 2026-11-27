#!/usr/bin/env bash
# E10 e2e-six-tickets: 일렬로 이어진 티켓 6개(01→02→…→06)를 5단계부터 끝까지 실행하는 저장소.
# 긴 흐름에서 메인 컨텍스트가 커질 때(A9) 품질이 떨어지는지 재는 사례다.
# 상태 파일 `## 구현 중 결정`에 티켓 03·05·06에 걸리는 결정 셋을 미리 둔다. 티켓 문서에는 결정 내용이 없다.
#   D1(03): 공백이 여럿 이어지면 하이픈 하나로 바꾼다
#   D2(05): 30자를 넘으면 단어 중간을 자르지 않고 30자 안의 마지막 하이픈 앞에서 자른다
#   D3(06): 결과가 비면 `untitled`를 돌려준다
# 판정용 테스트는 작업 트리 밖 .git/e2e-judge/test_judge.py에 둔다. 에이전트에게 알리지 않는다.
# 네트워크를 쓰지 않는다.
set -euo pipefail

git init -q -b main
git config user.name e2e
git config user.email e2e@example.com
git config commit.gpgsign false

mkdir -p src tests
cat > CLAUDE.md <<'MD'
# 저장소 규칙

- 검증 명령: `python3 -m unittest discover -s tests`
- 커밋 메시지는 한국어로 `<유형>: <요약>` 형식으로 쓴다. 유형은 feature, fix, docs, test, chore 중 하나다.
MD
cat > src/slug.py <<'PY'
def make_slug(title):
    """글 제목을 주소에 쓰는 slug로 바꾼다. 아직 아무것도 바꾸지 않는다."""
    return title
PY
cat > tests/test_slug_base.py <<'PY'
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from slug import make_slug


class MakeSlugBaseTest(unittest.TestCase):
    def test_plain_word_kept(self):
        self.assertEqual(make_slug("abc"), "abc")


if __name__ == "__main__":
    unittest.main()
PY
git add -A
git commit -qm "feature: slug 함수 뼈대 추가"

git switch -q -c feature/make-slug
d=docs/context/2026-11-20-make-slug
mkdir -p "$d" docs/context/run-flow
cat > docs/context/README.md <<'MD'
# Context

- [2026-11-20 글 제목으로 주소용 slug를 만든다](./2026-11-20-make-slug.md): `make_slug`를 여섯 단계로 완성한다
MD
cat > docs/context/2026-11-20-make-slug.md <<'MD'
# 글 제목으로 주소용 slug를 만든다

- 기준 커밋: `@BASE@`
- 작성일: 2026-11-20

## 요약
글 주소에 제목이 그대로 들어가 공백과 기호가 섞인다.

## 최종 목적
`make_slug(title)`이 영문 소문자, 숫자, 하이픈만으로 된 30자 이하 slug를 돌려준다.

## 합의한 작업
- 해법: `src/slug.py`의 `make_slug`를 티켓 6개로 차례로 완성한다 (사용자 합의)
- 남은 일:
  - [ ] 앞뒤 공백 지우기
  - [ ] 소문자로 바꾸기
  - [ ] 공백을 하이픈으로
  - [ ] 허용하지 않는 문자 지우기
  - [ ] 길이 제한
  - [ ] 빈 결과 처리

## 작업 경계
- 바꾸는 범위: `src/slug.py`의 `make_slug`
- 바꾸지 않는 범위: `make_slug`의 이름과 인자

## 확인 기준
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from slug import make_slug; print(make_slug('  Hello,   World!  '))"` → `hello-world`
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from slug import make_slug; print(len(make_slug('word ' * 20)) <= 30)"` → `True`

## 티켓
- [ ] [01: 앞뒤 공백 지우기](./2026-11-20-make-slug/01-strip.md)
- [ ] [02: 소문자로 바꾸기](./2026-11-20-make-slug/02-lower.md)
- [ ] [03: 공백을 하이픈으로](./2026-11-20-make-slug/03-hyphen.md)
- [ ] [04: 허용하지 않는 문자 지우기](./2026-11-20-make-slug/04-charset.md)
- [ ] [05: 길이 제한](./2026-11-20-make-slug/05-length.md)
- [ ] [06: 빈 결과 처리](./2026-11-20-make-slug/06-empty.md)
MD

ticket() {
  # $1 번호, $2 slug, $3 제목, $4 막힘 관계, $5 만들 것, $6 파이썬 식, $7 기대 결과
  cat > "$d/$1-$2.md" <<MD
# $1: $3

- 부모: [글 제목으로 주소용 slug를 만든다](../2026-11-20-make-slug.md)
- 막힘 관계: $4
- 상태: ready-for-agent

## 만들 것
$5

## 완료 기준
- [ ] \`python3 -c "import sys; sys.path.insert(0,'src'); from slug import make_slug; print($6)"\` → \`$7\`
MD
}
ticket 01 strip "앞뒤 공백 지우기" "없음 (바로 시작 가능)" \
  "\`make_slug\`가 제목 앞뒤의 공백을 지운다." "make_slug('  abc  ')" "abc"
ticket 02 lower "소문자로 바꾸기" "01: 앞뒤 공백 지우기" \
  "\`make_slug\`가 결과를 소문자로 바꾼다." "make_slug('ABC')" "abc"
ticket 03 hyphen "공백을 하이픈으로" "02: 소문자로 바꾸기" \
  "\`make_slug\`가 단어 사이의 공백을 하이픈으로 바꾼다." "make_slug('Hello World')" "hello-world"
ticket 04 charset "허용하지 않는 문자 지우기" "03: 공백을 하이픈으로" \
  "\`make_slug\`가 영문 소문자, 숫자, 하이픈이 아닌 문자를 지운다." "make_slug('Hi, there!')" "hi-there"
ticket 05 length "길이 제한" "04: 허용하지 않는 문자 지우기" \
  "\`make_slug\`의 결과가 30자를 넘지 않는다." "len(make_slug('word ' * 20)) <= 30" "True"
ticket 06 empty "빈 결과 처리" "05: 길이 제한" \
  "\`make_slug\`가 빈 결과를 돌려주지 않는다." "make_slug('!!!') != ''" "True"

base=$(git rev-parse --short main)
sed -i "s/@BASE@/$base/g" docs/context/2026-11-20-make-slug.md
git add -A
git commit -qm "docs: slug brief와 티켓 6개 추가"
start=$(git rev-parse HEAD)

cat > docs/context/run-flow/2026-11-20-make-slug.md <<'MD'
# 글 제목으로 주소용 slug를 만든다

- 시작일: 2026-11-20
- 현재 단계: 5. 구현과 리뷰
- 멈춘 이유: 없음

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
- 요구사항 문서:
- 개발 범위:
- brief: docs/context/2026-11-20-make-slug.md
- brief 초안:
- brief 냉독 결과:
- ADR:
- 브랜치: feature/make-slug
- 시작 HEAD: @START@
- 워커 식별자:
- PR:

## 결정

## 요구사항 답변

## 구체화 기록
- R5 목표: 영문 소문자, 숫자, 하이픈만으로 된 30자 이하 slug (사용자)

## 구현 중 결정
- 공백이 여럿 이어지면 하이픈 하나로 바꾼다(`a  b` → `a-b`): 사용자 답, 걸리는 티켓 03
- 30자를 넘으면 단어 중간을 자르지 않고 30자 안의 마지막 하이픈 앞에서 자른다(`alpha beta gamma delta epsilons zeta` → `alpha-beta-gamma-delta`). 30자 안에 하이픈이 없으면 30자에서 자른다: 사용자 답, 걸리는 티켓 05
- 결과가 비면 `untitled`를 돌려준다: 사용자 답, 걸리는 티켓 06

## 리뷰
- 통합 리뷰: 안 함
MD
sed -i "s/@START@/$start/g" docs/context/run-flow/2026-11-20-make-slug.md

mkdir -p .git/e2e-judge
cat > .git/e2e-judge/test_judge.py <<'PY'
"""E10 판정용. 저장소 루트에서 `python3 .git/e2e-judge/test_judge.py`로 돌린다.
결정 셋(D1·D2·D3)을 지킨 수는 test_d1~test_d3의 통과 수다."""
import pathlib
import sys
import unittest

root = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "src"))

from slug import make_slug


class Judge(unittest.TestCase):
    def test_brief(self):
        self.assertEqual(make_slug("  Hello,   World!  "), "hello-world")

    def test_d1_collapse_spaces(self):
        self.assertEqual(make_slug("a  b"), "a-b")

    def test_d2_cut_at_hyphen(self):
        self.assertEqual(make_slug("alpha beta gamma delta epsilons zeta"), "alpha-beta-gamma-delta")

    def test_d3_untitled(self):
        self.assertEqual(make_slug("!!!"), "untitled")

    def test_max_len(self):
        self.assertLessEqual(len(make_slug("word " * 20)), 30)


if __name__ == "__main__":
    unittest.main()
PY
