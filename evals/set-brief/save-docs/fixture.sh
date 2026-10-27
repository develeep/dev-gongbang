mkdir -p docs/context src/orders
cat > src/orders/detail.py <<'PY'
def order_detail(order_id):
    order = db.get_order(order_id)
    return {"id": order.id, "status": order.status, "items": order.items}
PY
cat > src/orders/shipments.py <<'PY'
# shipments(order_id, carrier, tracking_no, shipped_at)
def find_shipment(order_id):
    return db.query_one("SELECT carrier, tracking_no FROM shipments WHERE order_id = ?", order_id)
PY
cat > docs/context/2026-09-01-signup-email-verify.md <<'MD'
# 가입 시 이메일 인증을 요구한다

- 기준 커밋: `1111111`
- 작성일: 2026-09-01

## 합의한 작업
- 남은 일:
  - [ ] 가입 후 인증 메일 발송
MD
cat > docs/context/README.md <<'MD'
# Context

- [2026-09-01 가입 시 이메일 인증을 요구한다](./2026-09-01-signup-email-verify.md): 가입 이메일 인증
MD
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
