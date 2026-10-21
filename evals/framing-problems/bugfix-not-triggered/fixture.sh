mkdir -p src
cat > src/auth.py <<'PY'
import hashlib

USERS = {"alice": hashlib.sha256(b"pw123").hexdigest()}

def login(username, password):
    stored = USERS.get(username)
    # 버그: 입력 비밀번호를 해시하지 않고 비교한다
    return stored is not None and stored == password
PY
