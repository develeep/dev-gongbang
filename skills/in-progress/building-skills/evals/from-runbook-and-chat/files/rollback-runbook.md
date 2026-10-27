# 결제 API 롤백 런북 (payments-api)

담당: 플랫폼팀 / 최종 수정: 2026-09

## 언제
- 배포 후 15분 안에 5xx 비율이 2%를 넘거나, p95 지연이 800ms를 넘으면 롤백한다.
- 지표는 Grafana 대시보드 "payments-api / golden signals"에서 본다.

## 절차
1. #deploy-payments 채널에 "롤백 시작: <버전>" 을 남긴다.
2. ArgoCD에서 앱 `payments-api-prod` 의 직전 정상 revision 을 확인한다.
   - `argocd app history payments-api-prod`
3. 자동 동기화를 끈다. 끄지 않으면 ArgoCD가 git 의 최신 커밋으로 다시 되돌린다.
   - `argocd app set payments-api-prod --sync-policy none`
4. 롤백: `argocd app rollback payments-api-prod <REVISION_ID>`
5. 5분간 지표 확인. 정상화되면 채널에 "롤백 완료" 를 남긴다.
6. 원인 커밋을 git 에서 revert 하는 PR 을 올리고, 머지 후 자동 동기화를 다시 켠다.
   - `argocd app set payments-api-prod --sync-policy automated`

## DB 마이그레이션이 포함된 배포
- 마이그레이션이 있는 배포는 앱만 롤백하면 안 된다. 스키마가 앞서 있으면 구버전 앱이 실패한다.
- 이 경우 DBA 온콜(@dba-oncall)에게 먼저 호출하고 기다린다.
