mkdir -p docs/context/run-flow src
cat > src/orders.py <<'PY'
def list_orders(user_id):
    return db.query("SELECT id, status, created_at FROM orders WHERE user_id = ?", user_id)
PY
cat > src/notify.py <<'PY'
def send_email(to, subject, body):
    smtp.send(to, subject, body)
PY
cat > docs/context/run-flow/2026-11-10-shipping-email.md <<'MD'
# 주문이 배송 시작되면 고객에게 이메일 알림을 보낸다

- 시작일: 2026-11-10
- 현재 단계: 2. 구체화
- 멈춘 이유: 없음

## 단계
- [x] 0. 시작 단계 고르기
- [-] 1. 요구사항 정리
- [ ] 2. 구체화
- [ ] 3. 작업 지시서
- [ ] 4. 티켓 분할
- [ ] 5. 구현과 리뷰
- [ ] 6. 머지·PR 결정
- [ ] 7. PR 만들기

## 결과물
- 요구사항 문서: 없음 (요청 문장으로 시작)
- 개발 범위: 없음
- brief:
- ADR:
- 브랜치:
- PR:

## 결정

## 구체화 기록

| 칸 | 내용 | 출처 | 상태 |
|---|---|---|---|
| R1 최종 목적 | 주문 상태가 `shipped`로 바뀌면 그 주문의 고객에게 배송 시작 이메일이 한 번 간다 | 사용자 합의 | 확인됨 |
| R2 현재 | 주문 상태가 바뀌어도 고객에게 알림이 없다 | `src/orders.py` | 확인됨 |
| R3 만족 기준 | 같은 주문에 이메일이 두 번 가지 않는다 | 사용자 합의 | 확인됨 |
| R4 해법 | 상태를 `shipped`로 바꾸는 곳에서 `src/notify.py`의 `send_email`을 부른다 | 사용자 합의 | 확인됨 |
| R5 바꾸지 않는 범위 | `send_email`의 SMTP 설정 | 사용자 합의 | 확인됨 |
| R6 부작용 | SMTP 실패가 상태 변경을 막지 않는다 | 사용자 합의 | 확인됨 |
MD
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
