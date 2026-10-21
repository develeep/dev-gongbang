mkdir -p docs/context
for pkg in billing orders shipping reports; do
  mkdir -p src/$pkg
  for i in 1 2 3 4 5; do
    printf 'def handle_%s(event):\n    return lookup(event.user_id)\n' "$i" > src/$pkg/h$i.py
  done
done
printf 'class Event:\n    user_id: int\n' > src/event.py
cat > docs/context/2026-10-18-rename-user-id.md <<'MD'
# Event의 user_id 필드를 account_id로 바꾼다

- 기준 커밋: `3333333`
- 작성일: 2026-10-18

## 최종 목적
`src/` 어디에도 `Event.user_id`를 읽는 코드가 남지 않고 모든 코드가 `account_id`를 쓴다.

## 합의한 작업
- 남은 일:
  - [ ] `Event.user_id`를 `account_id`로 이름 변경
  - [ ] billing, orders, shipping, reports 패키지의 모든 호출부 변경

## 작업 경계
- 바꿀 수 없는 조건: 모든 커밋에서 CI가 통과해야 한다
MD
