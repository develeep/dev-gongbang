#!/usr/bin/env bash
# E4 e2e-planted-bug: 경계값에서 틀리기 쉬운 티켓 하나를 5단계부터 구현하는 저장소.
# 함정: 같은 모듈의 기존 `count_chunks`는 total이 size로 나누어떨어지거나 0일 때 한 개를 더 센다.
#       이것을 그대로 써서 `chunk_ranges`를 만들면 빈 조각 `(8, 8)`이나 `(0, 0)`이 생긴다.
#       티켓 완료 기준은 보통 경우만 보고, 경계는 brief의 확인 기준에만 있다.
# 판정용 테스트는 작업 트리 밖 .git/e2e-judge/test_judge.py에 둔다. 에이전트에게 알리지 않는다.
#   측정할 때 --keep-temp로 남긴 폴더에서 `python3 .git/e2e-judge/test_judge.py`로 돌려 결과를 측정 기록에 적는다.
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
cat > src/chunks.py <<'PY'
"""큰 목록을 일정한 크기의 조각으로 나눠 보내는 데 쓰는 도우미."""


def count_chunks(total, size):
    """예전 배치 작업이 쓰는 조각 수. 호출부가 이 값에 기대므로 동작을 바꾸지 않는다."""
    return total // size + 1
PY
cat > tests/test_chunks.py <<'PY'
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from chunks import count_chunks


class CountChunksTest(unittest.TestCase):
    def test_partial_last_chunk(self):
        self.assertEqual(count_chunks(10, 4), 3)


if __name__ == "__main__":
    unittest.main()
PY
git add -A
git commit -qm "feature: 조각 수 도우미 추가"

git switch -q -c feature/chunk-ranges
mkdir -p docs/context/2026-11-20-chunk-ranges docs/context/run-flow
cat > docs/context/README.md <<'MD'
# Context

- [2026-11-20 조각 범위 목록을 돌려준다](./2026-11-20-chunk-ranges.md): `chunk_ranges`가 `[start, end)` 쌍 목록을 돌려준다
MD
cat > docs/context/2026-11-20-chunk-ranges.md <<'MD'
# 조각 범위 목록을 돌려준다

- 기준 커밋: `@BASE@`
- 작성일: 2026-11-20

## 요약
배치 전송이 조각마다 시작·끝 위치를 직접 계산하다 마지막 조각을 빠뜨린 적이 있다.

## 최종 목적
`chunk_ranges(total, size)`가 `0`부터 `total`까지를 `size`씩 나눈 `(start, end)` 쌍 목록을 돌려준다. `end`는 포함하지 않는다.

## 합의한 작업
- 해법: `src/chunks.py`에 `chunk_ranges(total, size)`를 더한다 (사용자 합의)
- 남은 일:
  - [ ] `chunk_ranges` 추가

## 작업 경계
- 바꾸는 범위: `src/chunks.py`에 새 함수 추가
- 바꾸지 않는 범위: `count_chunks`의 동작 (예전 배치 작업이 기대함)
- 바꿀 수 없는 조건: 빈 조각(`start == end`)을 돌려주지 않는다

## 하면 안 되는 것
- `count_chunks`를 고치는 것: 예전 배치 작업의 조각 수가 바뀐다

## 확인 기준
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from chunks import chunk_ranges; print(chunk_ranges(10, 4))"` → `[(0, 4), (4, 8), (8, 10)]`
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from chunks import chunk_ranges; print(chunk_ranges(8, 4))"` → `[(0, 4), (4, 8)]`
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from chunks import chunk_ranges; print(chunk_ranges(0, 4))"` → `[]`
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from chunks import chunk_ranges; chunk_ranges(5, 0)"` → `ValueError`

## 티켓
- [ ] [01: 조각 범위 함수 추가](./2026-11-20-chunk-ranges/01-chunk-ranges.md)
MD
cat > docs/context/2026-11-20-chunk-ranges/01-chunk-ranges.md <<'MD'
# 01: 조각 범위 함수 추가

- 부모: [조각 범위 목록을 돌려준다](../2026-11-20-chunk-ranges.md)
- 막힘 관계: 없음 (바로 시작 가능)
- 상태: ready-for-agent

## 만들 것
`chunk_ranges(total, size)`가 `(start, end)` 쌍 목록을 돌려준다. 같은 모듈에 조각 수를 세는 `count_chunks`가 있다.

## 하면 안 되는 것
- `count_chunks`를 고치는 것: 예전 배치 작업의 조각 수가 바뀐다

## 완료 기준
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from chunks import chunk_ranges; print(chunk_ranges(10, 4))"` → `[(0, 4), (4, 8), (8, 10)]`
MD
base=$(git rev-parse --short main)
sed -i "s/@BASE@/$base/g" docs/context/2026-11-20-chunk-ranges.md
git add -A
git commit -qm "docs: 조각 범위 brief와 티켓 추가"
start=$(git rev-parse HEAD)

cat > docs/context/run-flow/2026-11-20-chunk-ranges.md <<'MD'
# 조각 범위 목록을 돌려준다

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
- brief: docs/context/2026-11-20-chunk-ranges.md
- brief 초안:
- brief 냉독 결과:
- ADR:
- 브랜치: feature/chunk-ranges
- 시작 HEAD: @START@
- 워커 식별자:
- PR:

## 결정

## 요구사항 답변

## 구체화 기록
- R5 목표: `chunk_ranges(total, size)`가 `(start, end)` 쌍 목록을 돌려준다 (사용자)
- R3 제약: `count_chunks`의 동작은 바꾸지 않는다, 빈 조각은 돌려주지 않는다 (사용자)

## 구현 중 결정

## 리뷰
- 통합 리뷰: 안 함
MD
sed -i "s/@START@/$start/g" docs/context/run-flow/2026-11-20-chunk-ranges.md

# 판정용 테스트: 작업 트리 밖(.git 안)에 둔다.
mkdir -p .git/e2e-judge
cat > .git/e2e-judge/test_judge.py <<'PY'
"""E4 판정용. 저장소 루트에서 `python3 .git/e2e-judge/test_judge.py`로 돌린다."""
import pathlib
import sys
import unittest

root = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "src"))

from chunks import chunk_ranges, count_chunks


class Judge(unittest.TestCase):
    def test_partial(self):
        self.assertEqual(chunk_ranges(10, 4), [(0, 4), (4, 8), (8, 10)])

    def test_exact_multiple(self):
        self.assertEqual(chunk_ranges(8, 4), [(0, 4), (4, 8)])

    def test_empty(self):
        self.assertEqual(chunk_ranges(0, 4), [])

    def test_bad_size(self):
        with self.assertRaises(ValueError):
            chunk_ranges(5, 0)

    def test_count_chunks_unchanged(self):
        self.assertEqual(count_chunks(8, 4), 3)


if __name__ == "__main__":
    unittest.main()
PY
