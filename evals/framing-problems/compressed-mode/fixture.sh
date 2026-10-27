mkdir -p config logs
cat > config/notify-worker.yaml <<'Y'
queue: payment-failed-notify
workers: 4
batch_size: 1
poll_interval_seconds: 30
Y
cat > logs/notify-worker.log <<'L'
2026-10-19T10:00:00 queue_depth=3 processed=3
2026-10-19T10:00:30 queue_depth=2 processed=2
2026-10-19T10:01:00 queue_depth=4 processed=4
L
