---
tags: [building-skills]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

지난번 결제 API 롤백할 때 대화랑 우리 런북 줄게. 이걸로 다음부터 롤백할 때 쓸 스킬 만들어줘. /building-skills 로 해주고, 테스트 돌리는 건 생략.

질문하면 이렇게 답한다.
- 호출 방식은 Model-invoked. 이름은 rolling-back-payments-api.
- 자유도는 낮음. 순서와 명령을 바꾸지 않는다. 번들 파일은 없다. 모델은 Sonnet.
- 대표 요청: ① "payments-api 방금 배포했는데 5xx 3% 나와. 롤백해줘" ② "결제 API p95가 900ms 넘었어. 직전 버전으로 되돌려줘" ③ "prod 결제 API v2.31.0 배포 문제 있어 보여. 롤백 진행해줘"
- near-miss: ① "스테이징 재배포해줘" ② "ArgoCD 앱 새로 만들어줘"
- 자료에 없는 것(예: 마이그레이션 포함 여부 확인 방법)은 모른다. Claude가 새로 제안하는 내용은 넣지 않는다.

Input files: rollback-runbook.md, chat-log.md
