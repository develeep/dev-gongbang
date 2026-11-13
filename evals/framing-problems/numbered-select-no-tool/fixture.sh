mkdir -p src/orders docs/notes
cat > src/orders/handler.py <<'PY'
from db import query

def list_orders(user_id):
    orders = query("SELECT * FROM orders WHERE user_id = %s", user_id)
    for o in orders:
        # 주문마다 상품을 따로 조회한다
        o["items"] = query("SELECT * FROM order_items WHERE order_id = %s", o["id"])
    return orders
PY
cat > src/orders/schema.sql <<'SQL'
CREATE TABLE orders (id BIGINT PRIMARY KEY, user_id BIGINT, created_at TIMESTAMP);
CREATE TABLE order_items (id BIGINT PRIMARY KEY, order_id BIGINT, sku TEXT);
-- order_items.order_id 에는 인덱스가 없다
SQL
cat > docs/notes/order-latency.md <<'MD'
# 주문 조회 API 지연 (2026-11-12 정리)

## 계기
- 2026-11-10 주에 "주문 내역이 안 뜬다"는 고객센터 문의가 34건 들어왔다
- 대부분 주문이 100건 넘는 단골 고객이다

## 목표
- `GET /orders` p95를 300ms 이하로 낮춘다 (CS팀과 합의)

## 현재
- APM 기준 `GET /orders` p95 2.4s, 주문 100건 이상 고객은 p95 6s

## 제약
- 스키마 변경(인덱스 추가 포함)은 DBA 승인이 필요하고 보통 3영업일 걸린다
- 이번 분기 Redis 같은 새 인프라는 들일 수 없다
- 응답 JSON 형식은 앱 호환 때문에 바꿀 수 없다
MD
