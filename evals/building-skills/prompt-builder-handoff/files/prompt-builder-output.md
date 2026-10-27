## 프롬프트 설계 요약
- 대상 모델: claude-sonnet-5-5 (사용자 지정) · 적용 가이드: 공통 + Sonnet 5.5 가이드 (확인일 2026-10-01, 이번 세션 대조 안 함)
- 종류: CLAUDE.md·SKILL.md · 언어: 한국어 · 진행 방식: 빠른 모드
- 반영한 결정:
  - K10 호출 방식: Model-invoked
  - K4 자유도: 중간 (선호 패턴 있음)
  - K6 번들 파일: 없음
  - K7 사용 모델: Sonnet
  - K9 자주 틀리는 점: ① 우리 DB는 PostgreSQL 15이고 `CREATE INDEX`는 반드시 `CONCURRENTLY`로 만들어야 운영 중 테이블 락이 안 걸린다 ② `CONCURRENTLY`는 트랜잭션 블록 안에서 실행할 수 없어서, 우리 마이그레이션 도구(sqitch)의 change 파일 맨 위에 `-- sqitch:no-transaction` 주석이 있어야 한다 ③ NOT NULL 컬럼 추가는 기본값 없이 하면 기존 행 때문에 실패한다
- 제안해 넣은 내용: 없음
- 적용한 best practice: description에 무엇과 언제, 체크리스트, 3인칭

## 완성 프롬프트

````markdown
---
name: SQL-Migration-Review
description: 제가 SQL 마이그레이션 파일을 리뷰해 드립니다. 마이그레이션 리뷰를 도와드려요.
---

# SQL 마이그레이션 리뷰

SQL(Structured Query Language)은 관계형 데이터베이스를 다루는 언어입니다. 마이그레이션은 데이터베이스 스키마를 버전별로 바꾸는 파일입니다. 인덱스는 조회를 빠르게 하는 자료구조입니다.

당신은 반드시 아래를 지켜야 합니다. MUST follow ALL rules. NEVER skip. ALWAYS check. CRITICAL.

## 리뷰 절차

1. 사용자가 준 마이그레이션 파일을 읽는다.
2. 인덱스 생성, 컬럼 추가, 테이블 삭제를 찾는다.
3. 문제를 표로 정리한다: `파일 | 줄 | 문제 | 고치는 법`.

자세한 내용은 [references/postgres-tips.md](references/postgres-tips.md) 참고.
````

## 다음 단계
- 대표 입력 3개 이상으로 테스트하세요.
- ⚠ K8(평가 시나리오)을 빠른 모드에서 받지 못했습니다. 대표 요청 3개와 near-miss 2개가 필요합니다.
- ⚠ 승인받지 못한 보완 제안 1: 판단 기준 — `<리뷰 절차>` 뒤에 넣을 문장: "운영 테이블에 락을 거는 변경(일반 CREATE INDEX, 기본값 없는 NOT NULL 추가, 테이블 재작성)은 '차단', 나머지 스타일 문제는 '권고'로 등급을 나눈다."
- ⚠ 통과하지 못한 검수 항목: K9 답이 있는데 "주의할 점" 절이 없습니다.
- 형식 선택: 결과 표 열 구성(파일 | 줄 | 문제 | 고치는 법)은 제가 정했습니다.
