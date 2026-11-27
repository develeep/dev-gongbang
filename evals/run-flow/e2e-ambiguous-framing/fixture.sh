#!/usr/bin/env bash
# E6 e2e-ambiguous-framing: 확정된 구체화 기록에 두 가지로 읽히는 문장이 든 흐름을 3단계(작업 지시서)부터 이어 가는 저장소.
# 두 가지로 읽히는 문장: R5 목표의 "미결제 알림은 하루에 한 번만 보낸다"
#   - 주문마다 하루 한 번인지, 고객마다 하루 한 번(주문이 여럿이어도 한 통)인지 기록만으로 정할 수 없다.
#   - 코드(`src/reminder.py`)도 어느 쪽인지 알려 주지 않는다.
# 네트워크를 쓰지 않는다. 원격이 없어 brief는 docs에 저장된다.
set -euo pipefail

git init -q -b main
git config user.name e2e
git config user.email e2e@example.com
git config commit.gpgsign false

mkdir -p src tests docs/context/run-flow
cat > CLAUDE.md <<'MD'
# 저장소 규칙

- 검증 명령: `python3 -m unittest discover -s tests`
- 커밋 메시지는 한국어로 `<유형>: <요약>` 형식으로 쓴다. 유형은 feature, fix, docs, test, chore 중 하나다.
MD
cat > src/reminder.py <<'PY'
"""미결제 주문 알림. 주문은 id, customer, paid 키를 가진 dict다."""


def unpaid(orders):
    return [o for o in orders if not o["paid"]]


def send_reminders(orders, send):
    """미결제 주문마다 send(customer, order_id)를 부른다. 지금은 부를 때마다 모두 다시 보낸다."""
    for o in unpaid(orders):
        send(o["customer"], o["id"])
PY
cat > tests/test_reminder.py <<'PY'
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from reminder import unpaid


class UnpaidTest(unittest.TestCase):
    def test_only_unpaid(self):
        orders = [{"id": 1, "customer": "c", "paid": True}, {"id": 2, "customer": "c", "paid": False}]
        self.assertEqual([o["id"] for o in unpaid(orders)], [2])


if __name__ == "__main__":
    unittest.main()
PY
git add -A
git commit -qm "feature: 미결제 알림 추가"
git switch -q -c feature/reminder-once

cat > docs/context/run-flow/2026-11-20-reminder-once.md <<'MD'
# 미결제 알림이 반복해서 가지 않게 한다

- 시작일: 2026-11-20
- 현재 단계: 3. 작업 지시서
- 멈춘 이유: 없음

## 단계
- [x] 0. 시작 단계 고르기
- [-] 1. 요구사항 정리
- [x] 2. 구체화
- [ ] 3. 작업 지시서
- [ ] 4. 티켓 분할
- [ ] 5. 구현과 리뷰
- [ ] 6. 머지·PR 결정
- [ ] 7. PR 만들기

## 결과물
- 요구사항 문서:
- 개발 범위:
- brief:
- brief 초안:
- brief 냉독 결과:
- ADR:
- 브랜치: feature/reminder-once
- 시작 HEAD:
- 워커 식별자:
- PR:

## 결정

## 요구사항 답변

## 구체화 기록
| 항목 | 내용 | 출처 | 근거 |
|---|---|---|---|
| R1 의도 | 고객이 같은 미결제 알림을 하루에 여러 번 받아 항의한다 | 사용자 | - |
| R1 계기 | 지난주 알림 배치가 한 시간마다 돌면서 항의 문의가 12건 들어왔다 | 사용자 | - |
| R2 이상 | 고객이 미결제 알림 때문에 항의하지 않는다 | 사용자 | R1 의도 |
| R2 현재 | `send_reminders`는 부를 때마다 미결제 주문 전부에 다시 보낸다 | `src/reminder.py` | - |
| R2 원인 | 보낸 기록을 남기지 않는다 (확인됨) | `src/reminder.py` | R2 현재 |
| R3 제약 | `send(customer, order_id)` 호출 형태는 바꾸지 않는다 (알림 서비스 계약) | 사용자 | - |
| R3 자원 | `unpaid(orders)` | `src/reminder.py` | - |
| R4 근거 | R4 해당 없음: 내부 알림 빈도 조정이라 외부 표준이 없다 | - | - |
| R5 목표 | 미결제 알림은 하루에 한 번만 보낸다 | 사용자 | R2 이상 |
| R5 해법 | `send_reminders`가 보낸 기록(날짜)을 받아 같은 날 이미 보냈으면 건너뛴다 | 사용자 승인 | R5 목표, R3 제약 |
| R6 부작용 | 알림 배치가 하루 첫 실행에서 실패하면 그날 알림이 늦어진다: 감수 | 사용자 | R5 해법 |

## 구현 중 결정

## 리뷰
- 통합 리뷰: 안 함
MD
