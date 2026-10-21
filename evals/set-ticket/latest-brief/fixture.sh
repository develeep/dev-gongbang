mkdir -p docs/context src/auth
cat > src/auth/login.py <<'PY'
def login(email, password):
    user = db.find_user(email)
    return user and user.check(password)
PY
cat > docs/context/2026-09-01-signup-email-verify.md <<'MD'
# 가입 시 이메일 인증을 요구한다

- 기준 커밋: `1111111`
- 작성일: 2026-09-01

## 합의한 작업
- 남은 일:
  - [ ] 가입 후 인증 메일 발송
  - [ ] 인증 링크 클릭 시 계정 활성화
MD
cat > docs/context/2026-10-15-login-lockout.md <<'MD'
# 로그인 5회 실패 시 계정을 15분 잠근다

- 기준 커밋: `2222222`
- 작성일: 2026-10-15

## 합의한 작업
- 남은 일:
  - [ ] 실패 횟수 기록과 5회 실패 시 15분 잠금
  - [ ] 잠긴 계정 로그인 시 남은 시간 안내
  - [ ] 관리자 화면에서 잠금 해제
MD
cat > docs/context/README.md <<'MD'
# Context

- [2026-09-01 가입 시 이메일 인증을 요구한다](./2026-09-01-signup-email-verify.md): 가입 이메일 인증
- [2026-10-15 로그인 5회 실패 시 계정을 15분 잠근다](./2026-10-15-login-lockout.md): 로그인 잠금
MD
