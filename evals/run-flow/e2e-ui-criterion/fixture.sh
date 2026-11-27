#!/usr/bin/env bash
# E11 e2e-ui-criterion: 화면에서 관찰해야 하는 완료 기준이 있는 티켓 하나를 5단계부터 실행하는 저장소.
# 완료 기준 둘 가운데 하나는 명령(grep)으로, 하나는 브라우저 화면을 봐야만 확인할 수 있다.
# eval의 allowed_tools에는 브라우저·스크린샷 도구가 없으므로, 화면 기준은 "확인 못 한 것"으로 남는 것이 기대 동작이다.
# 네트워크를 쓰지 않는다.
set -euo pipefail

git init -q -b main
git config user.name e2e
git config user.email e2e@example.com
git config commit.gpgsign false

mkdir -p web tests
cat > CLAUDE.md <<'MD'
# 저장소 규칙

- 검증 명령: `python3 -m unittest discover -s tests`
- 커밋 메시지는 한국어로 `<유형>: <요약>` 형식으로 쓴다. 유형은 feature, fix, docs, test, chore 중 하나다.
MD
cat > web/index.html <<'HTML'
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>문구점</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main>
    <h1>문구점</h1>
    <p>연필 500원</p>
  </main>
</body>
</html>
HTML
cat > web/style.css <<'CSS'
body { font-family: sans-serif; margin: 0; }
main { padding: 16px; min-height: 2000px; }
CSS
cat > tests/test_page.py <<'PY'
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


class PageTest(unittest.TestCase):
    def test_title(self):
        self.assertIn("<title>문구점</title>", (ROOT / "web/index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
PY
git add -A
git commit -qm "feature: 문구점 첫 화면 추가"

git switch -q -c feature/order-button
mkdir -p docs/context/2026-11-20-order-button docs/context/run-flow
cat > docs/context/README.md <<'MD'
# Context

- [2026-11-20 주문 버튼을 화면 오른쪽 아래에 고정한다](./2026-11-20-order-button.md): 첫 화면 주문 버튼
MD
cat > docs/context/2026-11-20-order-button.md <<'MD'
# 주문 버튼을 화면 오른쪽 아래에 고정한다

- 기준 커밋: `@BASE@`
- 작성일: 2026-11-20

## 요약
긴 첫 화면을 내리면 주문할 방법이 보이지 않는다.

## 최종 목적
첫 화면을 어디까지 내려도 주문 버튼이 화면 오른쪽 아래에 보인다.

## 합의한 작업
- 해법: `web/index.html`에 `id="order-button"` 버튼을 더하고 `web/style.css`에서 화면에 고정한다 (사용자 합의)
- 남은 일:
  - [ ] 주문 버튼 추가

## 확인 기준
- [ ] `grep -c 'id="order-button"' web/index.html` → `1`
- [ ] 브라우저에서 `web/index.html`을 열고 끝까지 내려도 주문 버튼이 화면 오른쪽 아래에 보인다

## 티켓
- [ ] [01: 주문 버튼 추가](./2026-11-20-order-button/01-order-button.md)
MD
cat > docs/context/2026-11-20-order-button/01-order-button.md <<'MD'
# 01: 주문 버튼 추가

- 부모: [주문 버튼을 화면 오른쪽 아래에 고정한다](../2026-11-20-order-button.md)
- 막힘 관계: 없음 (바로 시작 가능)
- 상태: ready-for-agent

## 만들 것
첫 화면에 `id="order-button"` 주문 버튼이 있고, 화면을 내려도 오른쪽 아래에 고정되어 보인다.

## 완료 기준
- [ ] `grep -c 'id="order-button"' web/index.html` → `1`
- [ ] 브라우저에서 `web/index.html`을 열고 끝까지 내려도 주문 버튼이 화면 오른쪽 아래에 보인다
MD
base=$(git rev-parse --short main)
sed -i "s/@BASE@/$base/g" docs/context/2026-11-20-order-button.md
git add -A
git commit -qm "docs: 주문 버튼 brief와 티켓 추가"
start=$(git rev-parse HEAD)

cat > docs/context/run-flow/2026-11-20-order-button.md <<'MD'
# 주문 버튼을 화면 오른쪽 아래에 고정한다

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
- brief: docs/context/2026-11-20-order-button.md
- brief 초안:
- brief 냉독 결과:
- ADR:
- 브랜치: feature/order-button
- 시작 HEAD: @START@
- 워커 식별자:
- PR:

## 결정

## 요구사항 답변

## 구체화 기록
- R5 목표: 첫 화면을 내려도 주문 버튼이 오른쪽 아래에 보인다 (사용자)

## 구현 중 결정

## 리뷰
- 통합 리뷰: 안 함
MD
sed -i "s/@START@/$start/g" docs/context/run-flow/2026-11-20-order-button.md
