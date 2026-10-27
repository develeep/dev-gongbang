mkdir -p src/orders
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
