mkdir -p docs/api
cat > docs/api/rate-limit.md <<'MD'
# 호출 한도

파트너 API는 API 키마다 분당 60회까지 호출할 수 있습니다.

## 한도를 넘으면
한도를 넘은 요청은 HTTP 429 상태 코드로 거절됩니다. 응답의 `Retry-After` 헤더에 적힌 초만큼 기다린 뒤 다시 호출합니다.

## 남은 횟수 확인
모든 응답의 `X-RateLimit-Remaining` 헤더에 이번 1분 동안 남은 호출 횟수가 들어 있습니다.
MD
