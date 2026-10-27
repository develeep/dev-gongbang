mkdir -p docs/context src/sales
touch src/sales/__init__.py
cat > src/sales/data.py <<'PY'
ROWS = [
    {"date": "2026-10-01", "amount": 1200},
    {"date": "2026-10-09", "amount": 800},
    {"date": "2026-10-15", "amount": 1500},
    {"date": "2026-10-20", "amount": 300},
]


def load_rows():
    return list(ROWS)
PY
cat > src/sales/formatters.py <<'PY'
def to_csv(rows):
    lines = ["date,amount"] + [f"{r['date']},{r['amount']}" for r in rows]
    return "\n".join(lines)
PY
cat > src/sales/__main__.py <<'PY'
import argparse

from sales.data import load_rows
from sales.formatters import to_csv

parser = argparse.ArgumentParser(prog="sales")
sub = parser.add_subparsers(dest="cmd", required=True)
report = sub.add_parser("report")
report.add_argument("--format", choices=["csv"], default="csv")
args = parser.parse_args()
print(to_csv(load_rows()))
PY
cat > docs/context/2026-10-26-sales-report-options.md <<'MD'
# 매출 리포트 명령에 JSON 출력과 날짜 필터를 추가한다

- 기준 커밋: `8888888`
- 작성일: 2026-10-26

## 최종 목적
`sales report`가 JSON으로도 출력하고, 시작일 이후 매출만 골라 출력한다.

## 확인된 사실
- `sales report`는 `src/sales/__main__.py`에서 `--format csv`만 받는다: `8888888`
- CSV 변환은 `src/sales/formatters.py`의 `to_csv`가 한다: `8888888`

## 합의한 작업
- 남은 일:
  - [ ] `sales report --format json`으로 매출 행을 JSON 배열로 출력
  - [ ] `sales report --since YYYY-MM-DD`로 그 날짜 이후 행만 출력

## 작업 경계
- 바꾸지 않는 범위: 옵션 없이 실행한 `sales report`의 CSV 출력
- 바꿀 수 없는 조건: 새 외부 라이브러리 추가 불가

## 확인 기준
- [ ] `PYTHONPATH=src python3 -m sales report --format json | python3 -c "import json,sys; print(len(json.load(sys.stdin)))"` → `4`
- [ ] `PYTHONPATH=src python3 -m sales report --since 2026-10-15 | wc -l` → `3`
- [ ] `PYTHONPATH=src python3 -m sales report`의 첫 줄이 `date,amount`
MD
