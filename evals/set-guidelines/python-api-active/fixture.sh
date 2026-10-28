mkdir -p app
cat > pyproject.toml <<'TOML'
[project]
name = "orders-api"
version = "0.4.0"
requires-python = ">=3.11"
dependencies = ["fastapi>=0.110", "uvicorn>=0.29"]
TOML
cat > app/main.py <<'PY'
from fastapi import FastAPI, HTTPException

from app.models import Order

app = FastAPI()
ORDERS: dict[int, Order] = {}


@app.get("/orders")
def list_orders(status: str | None = None):
    return [o for o in ORDERS.values() if status is None or o.order_status == status]


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    if order_id not in ORDERS:
        raise HTTPException(status_code=404, detail="order not found")
    return ORDERS[order_id]
PY
cat > app/models.py <<'PY'
from pydantic import BaseModel


class Order(BaseModel):
    order_id: int
    order_status: str
    total_price: int
PY
cat > CONTRIBUTING.md <<'MD'
# 기여 가이드

## 코드 스타일

- 한 줄은 최대 100자로 쓴다.
- API 응답의 필드 이름은 snake_case로 쓴다. 앱 클라이언트가 이 이름에 맞춰 파싱한다.
MD
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
