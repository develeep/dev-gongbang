# 지난 롤백 때 Claude와 나눈 대화 (발췌, 2026-10-14)

사용자: payments-api 방금 배포했는데 5xx 3% 나와. 롤백 도와줘.
Claude: ArgoCD에서 `argocd app rollback payments-api-prod` 를 실행하면 됩니다. 먼저 `argocd app history payments-api` 로 revision을 볼게요.
사용자: 앱 이름 틀렸어. prod 는 `payments-api-prod` 고 `payments-api` 는 스테이징이야. 헷갈리면 큰일나.
Claude: 알겠습니다. `argocd app history payments-api-prod` 결과 직전 정상 revision 은 41 입니다. 바로 롤백하겠습니다.
사용자: 잠깐, 자동 동기화 먼저 꺼야지. 지난번에 그거 안 꺼서 3분 뒤에 다시 문제 버전으로 돌아갔어.
Claude: 네, `--sync-policy none` 으로 끄고 롤백하겠습니다.
사용자: 그리고 revision 번호는 history 출력의 ID 열이야. 그 옆 Revision 열은 git SHA 라서 rollback 에 넣으면 에러나.
Claude: 확인했습니다. ID 41 로 롤백했습니다. 지표 5분 확인 후 알려드릴게요.
사용자: 좋아. 그리고 채널에 남길 때는 버전을 git 태그(v2.31.0 같은)로 써. revision ID 로 쓰면 다른 사람들이 못 알아봐.
Claude: 5분간 5xx 0.1%, p95 310ms 로 정상화됐습니다. #deploy-payments 에 "롤백 완료: v2.31.0 → v2.30.4" 를 남겼습니다.
사용자: 굿. 다음부턴 이 순서 그대로 해줘. 마이그레이션 있는 배포면 손대지 말고 DBA부터 부르고.
