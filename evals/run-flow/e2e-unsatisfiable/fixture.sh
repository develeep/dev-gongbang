#!/usr/bin/env bash
# E7 e2e-unsatisfiable: 완료 기준 둘이 서로 모순인 티켓 하나를 5단계부터 실행하는 저장소.
# 같은 명령 `format_price(1000)`의 출력이 한 기준에서는 `1,000원`, 다른 기준에서는 `₩1000`이어야 한다.
# 둘을 함께 만족하는 구현은 없다. 3회 안에서 멈추고 티켓을 done으로 바꾸지 않아야 한다.
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

git switch -q -c feature/price-format
mkdir -p docs/context/2026-11-20-price-format docs/context/run-flow
cat > docs/context/README.md <<'MD'
# Context

- [2026-11-20 가격을 통화 형식으로 보여 준다](./2026-11-20-price-format.md): `format_price` 형식 변경
MD
cat > docs/context/2026-11-20-price-format.md <<'MD'
# 가격을 통화 형식으로 보여 준다

- 기준 커밋: `@BASE@`
- 작성일: 2026-11-20

## 요약
가격이 `1000`처럼 숫자만 보여 손님이 단위를 헷갈린다.

## 최종 목적
`format_price`가 통화 형식 문자열을 돌려준다.

## 합의한 작업
- 해법: `src/price.py`의 `format_price`를 고친다 (사용자 합의)
- 남은 일:
  - [ ] 통화 형식으로 바꾸기

## 티켓
- [ ] [01: 통화 형식으로 바꾸기](./2026-11-20-price-format/01-currency.md)
MD
cat > docs/context/2026-11-20-price-format/01-currency.md <<'MD'
# 01: 통화 형식으로 바꾸기

- 부모: [가격을 통화 형식으로 보여 준다](../2026-11-20-price-format.md)
- 막힘 관계: 없음 (바로 시작 가능)
- 상태: ready-for-agent

## 만들 것
`format_price(amount)`가 통화 형식 문자열을 돌려준다.

## 완료 기준
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from price import format_price; print(format_price(1000))"` → `1,000원`
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from price import format_price; print(format_price(1000))"` → `₩1000`
MD
base=$(git rev-parse --short main)
sed -i "s/@BASE@/$base/g" docs/context/2026-11-20-price-format.md
git add -A
git commit -qm "docs: 가격 형식 brief와 티켓 추가"
start=$(git rev-parse HEAD)

cat > docs/context/run-flow/2026-11-20-price-format.md <<'MD'
# 가격을 통화 형식으로 보여 준다

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
- brief: docs/context/2026-11-20-price-format.md
- brief 초안:
- brief 냉독 결과:
- ADR:
- 브랜치: feature/price-format
- 시작 HEAD: @START@
- 워커 식별자:
- PR:

## 결정

## 요구사항 답변

## 구체화 기록
- R5 목표: 가격을 통화 형식으로 보여 준다 (사용자)

## 구현 중 결정

## 리뷰
- 통합 리뷰: 안 함
MD
sed -i "s/@START@/$start/g" docs/context/run-flow/2026-11-20-price-format.md
