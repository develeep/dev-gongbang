#!/usr/bin/env bash
# E8 e2e-resume-mid-5: 5단계 도중 끊긴 흐름을 이어 가는 저장소.
# - 티켓 01(금액 형식)은 done이고 완료 기록이 있다. 바꾼 파일은 src/price.py (커밋하지 않음).
# - 티켓 02(할인 표시)는 ready-for-agent이고, 미완성 변경 src/discount.py(새 파일)가 작업 트리에 남아 있다.
# - 상태 파일 `## 구현 중 결정`에 티켓 02에 걸리는 결정이 있다: 할인한 금액은 10원 단위로 내린다.
#   티켓 02 문서에는 이 결정이 없다. 결정을 쓰면 `format_discount(1234, 10)` → `1,110원 (10% 할인)`, 안 쓰면 `1,111원`이나 `1,110.6원`.
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
cat > src/price.py <<'PY'
def format_price(amount):
    """금액(정수, 원)을 화면에 보일 문자열로 바꾼다."""
    return str(amount)
PY
cat > tests/test_price.py <<'PY'
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from price import format_price


class FormatPriceTest(unittest.TestCase):
    def test_returns_text(self):
        self.assertIsInstance(format_price(1000), str)


if __name__ == "__main__":
    unittest.main()
PY
git add -A
git commit -qm "feature: 가격 표시 함수 추가"

git switch -q -c feature/discount-label
mkdir -p docs/context/2026-11-20-discount-label docs/context/run-flow
cat > docs/context/README.md <<'MD'
# Context

- [2026-11-20 할인 가격을 보여 준다](./2026-11-20-discount-label.md): 금액 형식과 할인 표시
MD
cat > docs/context/2026-11-20-discount-label.md <<'MD'
# 할인 가격을 보여 준다

- 기준 커밋: `@BASE@`
- 작성일: 2026-11-20

## 요약
할인 상품의 할인 뒤 가격이 화면에 없다.

## 최종 목적
`format_discount(1000, 10)`이 `900원 (10% 할인)`을 돌려준다.

## 합의한 작업
- 해법: 금액 형식 함수를 먼저 고치고, 그 위에 할인 표시 함수를 더한다 (사용자 합의)
- 남은 일:
  - [ ] 금액 형식
  - [ ] 할인 표시

## 확인 기준
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from discount import format_discount; print(format_discount(1000, 10))"` → `900원 (10% 할인)`

## 티켓
- [ ] [01: 금액 형식](./2026-11-20-discount-label/01-price-format.md)
- [ ] [02: 할인 표시](./2026-11-20-discount-label/02-discount.md)
MD
cat > docs/context/2026-11-20-discount-label/01-price-format.md <<'MD'
# 01: 금액 형식

- 부모: [할인 가격을 보여 준다](../2026-11-20-discount-label.md)
- 막힘 관계: 없음 (바로 시작 가능)
- 상태: ready-for-agent

## 만들 것
`format_price(1000)`이 `1,000원`을 돌려준다.

## 완료 기준
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from price import format_price; print(format_price(1000))"` → `1,000원`
MD
cat > docs/context/2026-11-20-discount-label/02-discount.md <<'MD'
# 02: 할인 표시

- 부모: [할인 가격을 보여 준다](../2026-11-20-discount-label.md)
- 막힘 관계: 01: 금액 형식
- 상태: ready-for-agent

## 만들 것
`format_discount(price, rate)`가 할인한 금액을 01 티켓의 금액 형식으로 쓰고 뒤에 `(<rate>% 할인)`을 붙인다. 새 파일 `src/discount.py`에 둔다.

## 완료 기준
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from discount import format_discount; print(format_discount(1000, 10))"` → `900원 (10% 할인)`
MD
base=$(git rev-parse --short main)
sed -i "s/@BASE@/$base/g" docs/context/2026-11-20-discount-label.md
git add -A
git commit -qm "docs: 할인 표시 brief와 티켓 추가"
start=$(git rev-parse HEAD)
short=$(git rev-parse --short HEAD)

# ---- 티켓 01: 끝났지만 커밋하지 않은 변경과 완료 기록 ----
cat > src/price.py <<'PY'
def format_price(amount):
    """금액(정수, 원)을 화면에 보일 문자열로 바꾼다."""
    return f"{amount:,}원"
PY
cat > docs/context/2026-11-20-discount-label/01-price-format.md <<'MD'
# 01: 금액 형식

- 부모: [할인 가격을 보여 준다](../2026-11-20-discount-label.md)
- 막힘 관계: 없음 (바로 시작 가능)
- 상태: done

## 만들 것
`format_price(1000)`이 `1,000원`을 돌려준다.

## 완료 기준
- [x] `python3 -c "import sys; sys.path.insert(0,'src'); from price import format_price; print(format_price(1000))"` → `1,000원`

## 완료 기록
- 완료일: 2026-11-20
- 커밋: 안 함 (작업 시작 HEAD `@SHORT@`)
- 바꾼 파일: `src/price.py`
- 확인한 것: `python3 -c "import sys; sys.path.insert(0,'src'); from price import format_price; print(format_price(1000))"` → `1,000원` (확인한 HEAD 작업 트리)
MD
sed -i "s/@SHORT@/$short/g" docs/context/2026-11-20-discount-label/01-price-format.md
sed -i -e 's/^  - \[ \] 금액 형식$/  - [x] 금액 형식/' -e 's/^- \[ \] \[01: /- [x] [01: /' docs/context/2026-11-20-discount-label.md

# ---- 티켓 02: 끊긴 미완성 변경 ----
cat > src/discount.py <<'PY'
from price import format_price


def format_discount(price, rate):
    discounted = price * (100 - rate) / 100
    # TODO(02): 금액 처리와 표시 문자열을 마저 쓴다
    raise NotImplementedError
PY

cat > docs/context/run-flow/2026-11-20-discount-label.md <<'MD'
# 할인 가격을 보여 준다

- 시작일: 2026-11-20
- 현재 단계: 5. 구현과 리뷰
- 멈춘 이유: 세션이 끊김. run-flow를 이 상태 파일을 인자로 다시 실행해 이어 간다

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
- brief: docs/context/2026-11-20-discount-label.md
- brief 초안:
- brief 냉독 결과:
- ADR:
- 브랜치: feature/discount-label
- 시작 HEAD: @START@
- 워커 식별자:
- PR:

## 결정

## 요구사항 답변

## 구체화 기록
- R5 목표: 할인 상품에 할인 뒤 가격을 보여 준다 (사용자)

## 구현 중 결정
- 할인한 금액은 10원 단위로 내린다(예: 1,234원의 10% 할인은 1,110원): 사용자 답(티켓 02 구현 중 질문), 걸리는 티켓 02

## 리뷰
- 통합 리뷰: 안 함
MD
sed -i "s/@START@/$start/g" docs/context/run-flow/2026-11-20-discount-label.md

mkdir -p .git/e2e-judge
cat > .git/e2e-judge/test_judge.py <<'PY'
"""E8 판정용. 저장소 루트에서 `python3 .git/e2e-judge/test_judge.py`로 돌린다."""
import pathlib
import sys
import unittest

root = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "src"))

from discount import format_discount
from price import format_price


class Judge(unittest.TestCase):
    def test_brief(self):
        self.assertEqual(format_discount(1000, 10), "900원 (10% 할인)")

    def test_decision_floor_to_ten(self):
        self.assertEqual(format_discount(1234, 10), "1,110원 (10% 할인)")

    def test_ticket1_kept(self):
        self.assertEqual(format_price(1000), "1,000원")


if __name__ == "__main__":
    unittest.main()
PY
