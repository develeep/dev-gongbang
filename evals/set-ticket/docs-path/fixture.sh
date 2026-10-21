mkdir -p docs/context src/orders src/web
cat > src/orders/api.py <<'PY'
def list_orders(request):
    rows = db.query("SELECT id, customer, phone, total, created_at FROM orders")
    return {"orders": rows}
PY
cat > src/web/orders.html <<'HTML'
<table id="orders"></table>
HTML
cat > docs/context/2026-10-20-order-csv-export.md <<'MD'
# 관리자가 주문 목록을 CSV로 내려받을 수 있다

- 기준 커밋: `a1b2c3d`
- 작성일: 2026-10-20

## 최종 목적
관리자가 주문 목록 화면에서 기간을 골라 CSV 파일을 내려받는다.

## 합의한 작업
- 해법: 서버에서 CSV를 만들어 내려준다
- 남은 일:
  - [ ] 관리자만 호출할 수 있는 CSV 내보내기 엔드포인트
  - [ ] 주문 목록 화면의 내보내기 버튼
  - [ ] 시작일·종료일 기간 필터
  - [ ] 10만 행을 넘으면 비동기로 만들고 완료 메일 발송

## 작업 경계
- 바꾸지 않는 범위: `list_orders` 응답 형식
- 바꿀 수 없는 조건: 새 외부 라이브러리 추가 불가

## 하면 안 되는 것
- CSV에 전화번호 열을 넣는다: 법무팀 합의
MD
