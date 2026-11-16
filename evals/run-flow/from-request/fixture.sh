mkdir -p src
cat > src/orders.py <<'PY'
def list_orders(user_id):
    return db.query("SELECT id, status, created_at FROM orders WHERE user_id = ?", user_id)
PY
cat > src/notify.py <<'PY'
def send_email(to, subject, body):
    smtp.send(to, subject, body)
PY
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
