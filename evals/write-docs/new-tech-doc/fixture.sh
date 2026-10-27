mkdir -p notes
cat > notes/retry-memo.md <<'MD'
# 결제 SDK 재시도 옵션 메모 (회의 중 적음)
- 재시도 설정은 RetryConfig 객체로 넘긴다: PaymentClient(retry=RetryConfig(...))
- max_retries: 기본 3. 0이면 재시도하지 않음
- backoff: "exponential" 또는 "fixed". 기본 exponential
- base_delay: 첫 재시도 전 대기 시간. 기본값은? (민수님께 물어보기)
- timeout: 요청 하나당 타임아웃, 단위 초. 기본값 못 들음
- retry_on: 재시도할 HTTP 상태 코드 목록. 503은 기본 포함, 나머지는 확인 중
- 결제 승인(approve)은 멱등 키가 없으면 재시도하지 않음
MD
