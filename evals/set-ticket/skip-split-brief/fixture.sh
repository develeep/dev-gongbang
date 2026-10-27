mkdir -p docs/context/2026-10-24-coupon-apply src/cart
cat > src/cart/cart.py <<'PY'
def add_item(cart, sku, qty=1):
    cart.items[sku] = cart.items.get(sku, 0) + qty
PY
cat > docs/context/2026-10-10-cart-quantity.md <<'MD'
# 장바구니 상품 수량을 바꿀 수 있다

- 기준 커밋: `4444444`
- 작성일: 2026-10-10

## 합의한 작업
- 남은 일:
  - [ ] 장바구니 화면에서 상품 수량 변경
  - [ ] 수량을 0으로 바꾸면 상품 삭제
  - [ ] 재고보다 많이 담으면 남은 재고 수 안내
MD
cat > docs/context/2026-10-22-shipping-fee.md <<'MD'
# 5만 원 이상 주문은 배송비를 받지 않는다

- 기준 커밋: `5555555`
- 작성일: 2026-10-22

## 합의한 작업
- 남은 일:
  - [x] 주문 합계 5만 원 이상이면 배송비 0원
  - [x] 결제 화면에 무료 배송까지 남은 금액 표시
MD
cat > docs/context/2026-10-24-coupon-apply.md <<'MD'
# 결제 화면에서 쿠폰 코드를 적용할 수 있다

- 기준 커밋: `6666666`
- 작성일: 2026-10-24

## 합의한 작업
- 남은 일:
  - [ ] 쿠폰 코드 입력과 할인 적용
  - [ ] 만료된 쿠폰 안내

## 티켓
- [ ] [01: 쿠폰 코드 적용](./2026-10-24-coupon-apply/01-apply-code.md)
- [ ] [02: 만료 쿠폰 안내](./2026-10-24-coupon-apply/02-expired-notice.md)
MD
cat > docs/context/2026-10-24-coupon-apply/01-apply-code.md <<'MD'
# 01: 쿠폰 코드 적용

- 부모: [결제 화면에서 쿠폰 코드를 적용할 수 있다](../2026-10-24-coupon-apply.md)
- 막힘 관계: 없음 (바로 시작 가능)
- 상태: ready-for-agent

## 만들 것
결제 화면에 쿠폰 코드를 입력하면 할인된 합계가 보인다.
MD
cat > docs/context/2026-10-24-coupon-apply/02-expired-notice.md <<'MD'
# 02: 만료 쿠폰 안내

- 부모: [결제 화면에서 쿠폰 코드를 적용할 수 있다](../2026-10-24-coupon-apply.md)
- 막힘 관계: 01: 쿠폰 코드 적용
- 상태: ready-for-agent

## 만들 것
만료된 쿠폰 코드를 입력하면 만료일과 함께 적용할 수 없다고 안내한다.
MD
cat > docs/context/README.md <<'MD'
# Context

- [2026-10-10 장바구니 상품 수량을 바꿀 수 있다](./2026-10-10-cart-quantity.md): 장바구니 수량 변경
- [2026-10-22 5만 원 이상 주문은 배송비를 받지 않는다](./2026-10-22-shipping-fee.md): 무료 배송 기준
- [2026-10-24 결제 화면에서 쿠폰 코드를 적용할 수 있다](./2026-10-24-coupon-apply.md): 쿠폰 적용
MD
