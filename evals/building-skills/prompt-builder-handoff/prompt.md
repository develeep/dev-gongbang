---
tags: [building-skills]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

/building-skills 아래 prompt-builder 결과로 스킬 완성해줘. 이번엔 실행 테스트는 빼고 정적 검사까지만 해줘.

질문하면 이렇게 답한다.
- 보완 제안 1(차단/권고 등급 기준)은 그대로 넣는다. 그 밖에 Claude가 새로 제안하는 내용은 넣지 않는다.
- 이름은 reviewing-sql-migrations로 한다.
- references/postgres-tips.md는 만든 적 없다. 링크를 지운다.
- 결과 표 열 구성(파일 | 줄 | 문제 | 고치는 법)은 그대로 쓴다.
- 대표 요청: ① "migrations/deploy/add_orders_status.sql 리뷰해줘" ② "이번 PR에 있는 sqitch change 파일들 운영에 올려도 되는지 봐줘" ③ "users 테이블에 email 인덱스 추가하는 마이그레이션, 락 걸리는지 확인해줘"
- near-miss: ① "users에 phone 컬럼 추가하는 마이그레이션 파일 새로 만들어줘" ② "orders 조회 쿼리가 느린데 어떤 인덱스 걸지 추천해줘"

Input files: prompt-builder-output.md
