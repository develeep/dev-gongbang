#!/usr/bin/env bash
# E2 e2e-spec-three-tickets: 기획서 MD 하나로 1~6단계를 지나는 저장소.
# 기획서의 기능 셋 가운데 둘(정렬, 재고 필터)은 서로 기대지 않고, 하나(목록 조회)는 둘을 함께 쓴다.
# 네트워크를 쓰지 않는다. 원격이 없어 brief는 docs에 저장된다.
set -euo pipefail

git init -q -b main
git config user.name e2e
git config user.email e2e@example.com
git config commit.gpgsign false

mkdir -p src/catalog tests docs/spec
cat > CLAUDE.md <<'MD'
# 저장소 규칙

- 검증 명령: `python3 -m unittest discover -s tests`
- 커밋 메시지는 한국어로 `<유형>: <요약>` 형식으로 쓴다. 유형은 feature, fix, docs, test, chore 중 하나다.
MD
cat > src/catalog/__init__.py <<'PY'
PY
cat > src/catalog/products.py <<'PY'
"""상품 데이터. 상품은 name, price, stock 키를 가진 dict다."""

SAMPLE = [
    {"name": "연필", "price": 500, "stock": 10},
    {"name": "공책", "price": 1500, "stock": 0},
    {"name": "가위", "price": 1500, "stock": 3},
    {"name": "자", "price": 800, "stock": 5},
]


def names(products):
    return [p["name"] for p in products]
PY
cat > tests/test_products.py <<'PY'
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from catalog.products import SAMPLE, names


class ProductsTest(unittest.TestCase):
    def test_names_keep_order(self):
        self.assertEqual(names(SAMPLE), ["연필", "공책", "가위", "자"])


if __name__ == "__main__":
    unittest.main()
PY
cat > docs/spec/product-list.md <<'MD'
# 문구점 상품 목록 개선 기획서

## 배경

손님이 상품 목록에서 원하는 상품을 찾기 어렵다는 문의가 매주 들어온다. 목록이 등록 순서로만 나오고 품절 상품도 섞여 있다.

## 기능

1. **가격순 정렬**: 상품 목록을 가격이 낮은 순으로 정렬한다. 가격이 같은 상품의 순서는 정해지지 않았다.
2. **재고 있는 상품만 보기**: 품절 상품을 목록에서 뺄 수 있다.
3. **목록 조회**: 위 두 기능을 함께 써서 목록을 돌려주는 함수 하나를 둔다. 정렬과 품절 제외는 각각 켜고 끌 수 있다.

## 대상

- 서비스: 문구점 카탈로그 (`src/catalog/` 파이썬 모듈)
- 화면 작업은 이번 범위가 아니다.

## 일정

- 이번 주 안
MD
git add -A
git commit -qm "chore: 카탈로그 모듈과 기획서 추가"
