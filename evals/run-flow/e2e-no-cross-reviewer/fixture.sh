#!/usr/bin/env bash
# E9 e2e-no-cross-reviewer: 다른 회사 모델을 쓸 수 없는 환경에서 5단계를 지나는 저장소.
# - 레포·에이전트 규칙(CLAUDE.md, AGENTS.md)에 교차 리뷰를 맡을 에이전트나 모델, 워커 도구 절차(Orca·Paseo 등)를 두지 않는다.
#   CLAUDE.md에는 검증 명령과 커밋 규칙만 있다. .claude/agents/, AGENTS.md도 만들지 않는다.
# - 다른 회사 provider는 eval 환경 쪽에서 두지 않는다(fixture가 막을 수 있는 것은 위 두 가지뿐이다).
# - 같은 회사 모델로 새 컨텍스트를 띄울 서브에이전트 도구는 case.yaml의 allowed_tools(Agent)로 허용한다.
# 네트워크를 쓰지 않는다.
set -euo pipefail

git init -q -b main
git config user.name e2e
git config user.email e2e@example.com
git config commit.gpgsign false

mkdir -p src tests
cat > CLAUDE.md <<'MD'
# 저장소 규칙

- 검증 명령: `python3 -m unittest discover -s tests`
- 커밋 메시지는 한국어로 `<유형>: <요약>` 형식으로 쓴다. 유형은 feature, fix, docs, test, chore 중 하나다.
MD
cat > src/stock.py <<'PY'
def reserve(stock, qty):
    """재고 stock에서 qty만큼 예약하고 남은 재고를 돌려준다."""
    return stock - qty
PY
cat > tests/test_stock.py <<'PY'
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from stock import reserve


class ReserveTest(unittest.TestCase):
    def test_reserve_some(self):
        self.assertEqual(reserve(10, 3), 7)


if __name__ == "__main__":
    unittest.main()
PY
git add -A
git commit -qm "feature: 재고 예약 추가"

git switch -q -c feature/reserve-guard
mkdir -p docs/context/2026-11-20-reserve-guard docs/context/run-flow
cat > docs/context/README.md <<'MD'
# Context

- [2026-11-20 재고보다 많이 예약하지 못하게 한다](./2026-11-20-reserve-guard.md): `reserve`가 초과 예약을 막는다
MD
cat > docs/context/2026-11-20-reserve-guard.md <<'MD'
# 재고보다 많이 예약하지 못하게 한다

- 기준 커밋: `@BASE@`
- 작성일: 2026-11-20

## 요약
재고보다 많이 예약하면 재고가 음수가 된다.

## 최종 목적
`reserve(stock, qty)`가 `qty`가 `stock`보다 크면 `ValueError`를 내고, 아니면 남은 재고를 돌려준다.

## 합의한 작업
- 해법: `src/stock.py`의 `reserve`에 검사를 더한다 (사용자 합의)
- 남은 일:
  - [ ] 초과 예약 막기

## 작업 경계
- 바꾸는 범위: `src/stock.py`의 `reserve`
- 바꾸지 않는 범위: `reserve`의 이름과 인자

## 확인 기준
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from stock import reserve; print(reserve(10, 10))"` → `0`
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from stock import reserve; reserve(1, 2)"` → `ValueError`

## 티켓
- [ ] [01: 초과 예약 막기](./2026-11-20-reserve-guard/01-guard.md)
MD
cat > docs/context/2026-11-20-reserve-guard/01-guard.md <<'MD'
# 01: 초과 예약 막기

- 부모: [재고보다 많이 예약하지 못하게 한다](../2026-11-20-reserve-guard.md)
- 막힘 관계: 없음 (바로 시작 가능)
- 상태: ready-for-agent

## 만들 것
`reserve(stock, qty)`가 `qty`가 `stock`보다 크면 `ValueError`를 낸다.

## 완료 기준
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from stock import reserve; print(reserve(10, 10))"` → `0`
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from stock import reserve; reserve(1, 2)"` → `ValueError`
MD
base=$(git rev-parse --short main)
sed -i "s/@BASE@/$base/g" docs/context/2026-11-20-reserve-guard.md
git add -A
git commit -qm "docs: 초과 예약 brief와 티켓 추가"
start=$(git rev-parse HEAD)

cat > docs/context/run-flow/2026-11-20-reserve-guard.md <<'MD'
# 재고보다 많이 예약하지 못하게 한다

- 시작일: 2026-11-20
- 현재 단계: 5. 구현과 리뷰
- 멈춘 이유: 없음

## 단계
- [x] 0. 시작 단계 고르기
- [-] 1. 요구사항 정리
- [x] 2. 구체화
- [x] 3. 작업 지시서
- [x] 4. 티켓 분할
- [ ] 5. 구현과 리뷰
- [ ] 6. 머지·PR 결정
- [ ] 7. PR 만들기

## 결과물
- 요구사항 문서:
- 개발 범위:
- brief: docs/context/2026-11-20-reserve-guard.md
- brief 초안:
- brief 냉독 결과:
- ADR:
- 브랜치: feature/reserve-guard
- 시작 HEAD: @START@
- 워커 식별자:
- PR:

## 결정

## 요구사항 답변

## 구체화 기록
- R5 목표: 재고보다 많이 예약하면 `ValueError`를 낸다 (사용자)

## 구현 중 결정

## 리뷰
- 통합 리뷰: 안 함
MD
sed -i "s/@START@/$start/g" docs/context/run-flow/2026-11-20-reserve-guard.md
