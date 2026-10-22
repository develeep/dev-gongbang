mkdir -p docs/context/2026-10-21-discount-rounding src
cat > src/price.py <<'PY'
def final_price(price, rate):
    return int(price * (1 - rate))
PY
cat > docs/context/2026-10-21-discount-rounding.md <<'MD'
# 할인가를 원 단위 반올림으로 바꾼다

- 기준 커밋: `b2c3d4e`
- 작성일: 2026-10-21

## 티켓
- [ ] [01: 현재 할인가 기록](./2026-10-21-discount-rounding/01-record-current.md)
- [ ] [02: 반올림으로 변경](./2026-10-21-discount-rounding/02-round.md)
MD
cat > docs/context/2026-10-21-discount-rounding/01-record-current.md <<'MD'
# 01: 현재 할인가 기록

- 부모: [할인가를 원 단위 반올림으로 바꾼다](../2026-10-21-discount-rounding.md)
- 막힘 관계: 없음 (바로 시작 가능)
- 상태: ready-for-agent

## 만들 것
`final_price`에 (1999, 0.1), (1005, 0.5), (999, 0.33)을 넣은 현재 결과표를 만들고, 결과를 이 티켓의 산출물로 남긴다. 코드는 바꾸지 않는다.

## 완료 기준
- [ ] 세 입력의 현재 결과가 산출물에 있다
MD
cat > docs/context/2026-10-21-discount-rounding/02-round.md <<'MD'
# 02: 반올림으로 변경

- 부모: [할인가를 원 단위 반올림으로 바꾼다](../2026-10-21-discount-rounding.md)
- 막힘 관계: 01: 현재 할인가 기록
- 상태: ready-for-agent

## 만들 것
`final_price`가 버림 대신 반올림한다.

## 완료 기준
- [ ] 01 티켓의 산출물에 있는 세 입력 중 결과가 바뀐 것과 그대로인 것을 표로 보인다
MD
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
