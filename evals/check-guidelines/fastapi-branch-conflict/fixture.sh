mkdir -p app/api .claude/rules
cat > pyproject.toml <<'TOML'
[project]
name = "orders-api"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["fastapi==0.115.6"]

[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F"]
TOML
cat > .claude/rules/python.md <<'MD'
---
paths:
  - "**/*.py"
---

# Python

- 한 줄은 88자를 넘기지 않는다.
- 함수에는 매개변수와 반환값 타입 힌트를 단다.
MD
cat > .claude/rules/api.md <<'MD'
---
paths:
  - "app/api/**/*.py"
---

# API

- API 라우터 파일은 한 줄을 100자까지 쓸 수 있다.
- 응답 필드 이름은 snake_case로 쓴다.
MD
cat > app/main.py <<'PY'
from fastapi import FastAPI

app = FastAPI()
PY
cat > app/legacy.py <<'PY'
def total(items):
    return sum(i["price"] for i in items)
PY
git init -q -b main && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
# origin 기본 브랜치를 흉내 낸다. 실제 원격은 없다.
git remote add origin https://example.invalid/orders-api.git
git update-ref refs/remotes/origin/main HEAD
git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
git switch -qc feature/orders
cat > app/api/orders.py <<'PY'
from fastapi import APIRouter

router = APIRouter()


@router.get("/orders/{order_id}")
def get_order(order_id: int) -> dict:
    return {"order_id": order_id, "order_status": "paid", "total_price": 12000, "unit": "KRW"}


def to_summary(order):
    return {"order_id": order["order_id"], "status": order["order_status"]}
PY
git add -A && git -c user.name=t -c user.email=t@t commit -qm "주문 조회 API 추가"
