#!/usr/bin/env bash
# E3 e2e-pr: 티켓이 끝나고 통합 리뷰가 기록된 흐름을 6단계부터 이어 가 PR까지 만드는 저장소.
# 네트워크를 쓰지 않는다.
# - 원격: `git remote -v`의 fetch 줄은 github.com 주소지만, push는 pushInsteadOf로 .e2e/remote.git(로컬 bare)에 간다.
#   http.proxy를 닫힌 포트로 둬 github.com에 실제로 접속하는 git 명령은 바로 실패한다.
# - gh 대역: .e2e/bin/gh. .claude/settings.local.json의 env.PATH로 앞에 둔다. 호출은 .e2e/gh-calls.log에,
#   `gh pr create`의 본문은 .e2e/pr-body.md에 남는다. 진짜 gh가 불리면 GH_CONFIG_DIR가 빈 폴더라 인증이 없다.
# - 리뷰 기록의 코드 지문은 run-flow scripts/code_fingerprint.sh와 같은 방법(docs/context 제외)으로 계산한다.
set -euo pipefail

root=$PWD
git init -q -b main
git config user.name e2e
git config user.email e2e@example.com
git config commit.gpgsign false

# ---- 로컬 원격, gh 대역 ----
mkdir -p .e2e/bin .e2e/gh-config .claude
git init -q --bare .e2e/remote.git
git remote add origin https://github.com/acme/stationery.git
git config "url.$root/.e2e/remote.git.pushInsteadOf" https://github.com/acme/stationery.git
git config http.proxy http://127.0.0.1:9
printf '.e2e/\n.claude/settings.local.json\n' >> .git/info/exclude
cat > .e2e/bin/gh <<'SH'
#!/usr/bin/env bash
# e2e gh 대역. 네트워크를 쓰지 않는다.
dir="$(cd "$(dirname "$0")/.." && pwd)"
echo "$*" >> "$dir/gh-calls.log"
case "${1:-} ${2:-}" in
  "auth status") echo "github.com: Logged in to github.com account e2e (gh 대역)"; exit 0 ;;
  "repo view") echo '{"visibility":"PRIVATE","defaultBranchRef":{"name":"main"},"nameWithOwner":"acme/stationery"}'; exit 0 ;;
  "pr create")
    prev=""; body=""
    for a in "$@"; do
      case "$prev" in --body-file|-F) cp "$a" "$dir/pr-body.md" ;; --body|-b) printf '%s\n' "$a" > "$dir/pr-body.md" ;; esac
      case "$a" in --body-file=*) cp "${a#--body-file=}" "$dir/pr-body.md" ;; --body=*) printf '%s\n' "${a#--body=}" > "$dir/pr-body.md" ;; esac
      prev="$a"
    done
    echo "https://github.com/acme/stationery/pull/1"; exit 0 ;;
  "pr view"|"pr list") echo "no pull requests found (gh 대역)" >&2; exit 1 ;;
  *) echo "gh 대역: 지원하지 않는 명령: $*" >&2; exit 1 ;;
esac
SH
chmod +x .e2e/bin/gh
cat > .claude/settings.local.json <<JSON
{
  "env": {
    "PATH": "$root/.e2e/bin:$PATH",
    "GH_CONFIG_DIR": "$root/.e2e/gh-config"
  }
}
JSON

# ---- main: 원래 코드 ----
mkdir -p src tests
cat > CLAUDE.md <<'MD'
# 저장소 규칙

- 검증 명령: `python3 -m unittest discover -s tests`
- 커밋 메시지는 한국어로 `<유형>: <요약>` 형식으로 쓴다. 유형은 feature, fix, docs, test, chore 중 하나다.
- PR 제목은 커밋 메시지 제목과 같은 형식으로 쓴다.
MD
cat > src/greet.py <<'PY'
def greet(name):
    return "hello " + name
PY
cat > tests/test_greet.py <<'PY'
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from greet import greet


class GreetTest(unittest.TestCase):
    def test_contains_name(self):
        self.assertIn("A", greet("A"))


if __name__ == "__main__":
    unittest.main()
PY
git add -A
git commit -qm "feature: 인사말 함수 추가"
git push -q origin main
start=$(git rev-parse --short HEAD)

# ---- 작업 브랜치: 흐름 문서 커밋 ----
git switch -q -c feature/greet-upper
mkdir -p docs/context/2026-11-20-greet-upper docs/context/run-flow
cat > docs/context/README.md <<'MD'
# Context

- [2026-11-20 인사말을 대문자로 바꾼다](./2026-11-20-greet-upper.md): `greet`가 대문자 인사말을 돌려준다
MD
cat > docs/context/2026-11-20-greet-upper.md <<'MD'
# 인사말을 대문자로 바꾼다

- 기준 커밋: `@START@`
- 작성일: 2026-11-20

## 요약
`greet`가 돌려주는 인사말이 화면에서 눈에 띄지 않는다.

## 최종 목적
`greet("a")`가 `HELLO A`를 돌려준다.

## 합의한 작업
- 해법: 인사말 전체를 대문자로 바꾼다 (사용자 합의)
- 남은 일:
  - [x] 대문자 변환

## 작업 경계
- 바꾸는 범위: `src/greet.py`의 `greet`
- 바꾸지 않는 범위: 빈 이름 입력 처리

## 확인 기준
- [x] `python3 -c "import sys; sys.path.insert(0,'src'); from greet import greet; print(greet('a'))"` → `HELLO A`

## 티켓
- [x] [01: 대문자 변환](./2026-11-20-greet-upper/01-upper.md)
MD
cat > docs/context/2026-11-20-greet-upper/01-upper.md <<'MD'
# 01: 대문자 변환

- 부모: [인사말을 대문자로 바꾼다](../2026-11-20-greet-upper.md)
- 막힘 관계: 없음 (바로 시작 가능)
- 상태: done

## 만들 것
`greet("a")`가 `HELLO A`를 돌려준다.

## 완료 기준
- [x] `python3 -c "import sys; sys.path.insert(0,'src'); from greet import greet; print(greet('a'))"` → `HELLO A`

## 완료 기록
- 완료일: 2026-11-20
- 커밋: 안 함 (작업 시작 HEAD `@START@`)
- 바꾼 파일: `src/greet.py`, `tests/test_greet_upper.py`
- 확인한 것: `python3 -c "import sys; sys.path.insert(0,'src'); from greet import greet; print(greet('a'))"` → `HELLO A` (확인한 HEAD 작업 트리)
- 고치지 않은 지적: 빈 이름 `greet("")`가 `HELLO `를 돌려준다: brief 작업 경계 밖(바꾸지 않는 범위)
MD
sed -i "s/@START@/$start/g" docs/context/2026-11-20-greet-upper.md docs/context/2026-11-20-greet-upper/01-upper.md
git add -A
git commit -qm "docs: 인사말 대문자 brief와 티켓 추가"

# ---- 커밋하지 않은 구현 ----
cat > src/greet.py <<'PY'
def greet(name):
    return ("hello " + name).upper()
PY
cat > tests/test_greet_upper.py <<'PY'
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from greet import greet


class GreetUpperTest(unittest.TestCase):
    def test_upper(self):
        self.assertEqual(greet("a"), "HELLO A")


if __name__ == "__main__":
    unittest.main()
PY

head=$(git rev-parse --short HEAD)
export GIT_INDEX_FILE="$root/.git/e2e-fingerprint-index"
git read-tree HEAD
git add -A
git rm -r -q --cached --ignore-unmatch -- docs/context
fp=$(git write-tree)
rm -f "$GIT_INDEX_FILE"
unset GIT_INDEX_FILE

cat > docs/context/run-flow/2026-11-20-greet-upper.md <<'MD'
# 인사말을 대문자로 바꾼다

- 시작일: 2026-11-20
- 현재 단계: 6. 머지·PR 결정
- 멈춘 이유: 없음

## 단계
- [x] 0. 시작 단계 고르기
- [-] 1. 요구사항 정리
- [x] 2. 구체화
- [x] 3. 작업 지시서
- [x] 4. 티켓 분할
- [x] 5. 구현과 리뷰
- [ ] 6. 머지·PR 결정
- [ ] 7. PR 만들기

## 결과물
- 요구사항 문서:
- 개발 범위:
- brief: docs/context/2026-11-20-greet-upper.md
- brief 초안:
- brief 냉독 결과:
- ADR:
- 브랜치: feature/greet-upper
- 시작 HEAD: @START@
- 워커 식별자:
- PR:

## 결정

## 요구사항 답변

## 구체화 기록
- R1 의도: 인사말이 화면에서 눈에 띄게 한다 (사용자)
- R5 목표: `greet("a")`가 `HELLO A`를 돌려준다 (사용자)
- R5 해법: 인사말 전체를 대문자로 바꾼다 (사용자 승인)

## 구현 중 결정

## 리뷰
- 통합 리뷰: 완료 (HEAD @HEAD@, 코드 지문 @FP@)
- 교차 리뷰 모델: claude-opus-5-5 (교차 리뷰 대체: 같은 회사 모델, 다른 회사 모델 없음)
- brief 확인 기준: `python3 -c "import sys; sys.path.insert(0,'src'); from greet import greet; print(greet('a'))"` → `HELLO A`: 통과
- 코드 리뷰: 빈 이름 `greet("")`가 `HELLO `를 돌려준다: 고치지 않음 (brief 작업 경계 밖)
- 교차 리뷰(같은 회사 대체): 지적 없음
- 범위 밖 문제: 빈 이름 입력 처리
MD
sed -i -e "s/@START@/$start/g" -e "s/@HEAD@/$head/g" -e "s/@FP@/$fp/g" docs/context/run-flow/2026-11-20-greet-upper.md
# 상태 파일과 구현은 커밋하지 않은 채로 둔다. 6단계 "PR 만들기"에서 커밋 하나로 묶는다.
