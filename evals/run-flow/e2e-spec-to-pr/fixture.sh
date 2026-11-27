#!/usr/bin/env bash
# E2→E3 e2e-spec-to-pr: E2(e2e-spec-three-tickets) 실행이 끝난 작업 트리와 상태 파일을 그대로 입력으로 써
# 6단계부터 7단계(PR)까지 이어 가는 분할 연속 사례.
#
# 입력 찾기(앞에서 처음 있는 것):
#   1. 환경 변수 E2E_E2_WORKTREE: E2 실행의 작업 트리 폴더(`claude plugin eval --keep-temp`로 남긴 scaffold 폴더)
#   2. <저장소>/evals/results/e2e-spec-three-tickets/worktree/ : E2 실행 뒤 그 scaffold 폴더를 이 경로로 복사해 둔 것.
#      evals/results/는 .gitignore로 git에서 빠져 있다.
# 입력이 없거나 E2가 6단계까지 가지 못했으면(상태 파일의 현재 단계가 6이 아니거나 통합 리뷰가 완료가 아니면)
# "E2 실패로 미실행"을 출력하고 E2E-NOT-RUN.md에 이유를 남긴 뒤 0으로 끝난다. 이때 사례는 실행하지 않은 것으로 적는다.
#
# 네트워크를 쓰지 않는다. 원격과 gh 대역은 e2e-pr과 같은 방식이다(.e2e/remote.git, .e2e/bin/gh).
set -euo pipefail

root=$PWD
here=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
src="${E2E_E2_WORKTREE:-}"
if [ -z "$src" ] && [ -n "$here" ] && [ -d "$here/../../results/e2e-spec-three-tickets/worktree" ]; then
  src="$here/../../results/e2e-spec-three-tickets/worktree"
fi
# 스크립트가 복사본이거나 BASH_SOURCE를 못 쓸 때: 현재 폴더(저장소 루트)와 그 위쪽에서도 찾는다.
if [ -z "$src" ]; then
  for c in "$root/evals/results/e2e-spec-three-tickets/worktree" "$root/../evals/results/e2e-spec-three-tickets/worktree"; do
    if [ -d "$c" ]; then src="$c"; break; fi
  done
fi

not_run() {
  printf '# E2 실패로 미실행\n\n- 이유: %s\n- 입력 경로: %s\n' "$1" "${src:-없음}" > E2E-NOT-RUN.md
  echo "E2 실패로 미실행: $1"
  exit 0
}

[ -n "$src" ] && [ -d "$src" ] || not_run "E2 결과 폴더가 없다"
[ -d "$src/.git" ] || not_run "E2 결과 폴더에 git 저장소가 없다"
state=$(cd "$src" && command grep -RlE --include='*.md' --exclude-dir=.git '^- 현재 단계: ' docs/context/run-flow 2>/dev/null | head -n 1 || true)
[ -n "$state" ] || not_run "E2 결과에 상태 파일이 없다"
command grep -qE '^- 현재 단계: 6' "$src/$state" || not_run "E2 상태 파일이 6단계가 아니다 ($state)"
command grep -qE '^- 통합 리뷰: 완료' "$src/$state" || not_run "E2 상태 파일에 통합 리뷰 완료 기록이 없다 ($state)"
branch=$(git -C "$src" symbolic-ref --short HEAD 2>/dev/null || true)
[ "$branch" = "feature/product-list" ] || not_run "E2 작업 브랜치가 feature/product-list가 아니다 (${branch:-분리된 HEAD})"
git -C "$src" rev-parse -q --verify refs/heads/main >/dev/null || not_run "E2 결과에 main 브랜치가 없다"

# ---- E2 작업 트리와 상태 파일을 그대로 복사 ----
cp -a "$src/." "$root/"
git config user.name e2e
git config user.email e2e@example.com
git config commit.gpgsign false

# ---- 로컬 원격, gh 대역 (e2e-pr과 같음) ----
mkdir -p .e2e/bin .e2e/gh-config .claude
rm -rf .e2e/remote.git .e2e/gh-calls.log .e2e/pr-body.md
git init -q --bare .e2e/remote.git
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/acme/stationery.git
git config "url.$root/.e2e/remote.git.pushInsteadOf" https://github.com/acme/stationery.git
git config http.proxy http://127.0.0.1:9
command grep -qxF '.e2e/' .git/info/exclude 2>/dev/null || printf '.e2e/\n.claude/settings.local.json\n' >> .git/info/exclude
cat > .e2e/bin/gh <<'SH'
#!/usr/bin/env bash
# e2e gh 대역. 네트워크를 쓰지 않는다.
dir="$(cd "$(dirname "$0")/.." && pwd)"
echo "$*" >> "$dir/gh-calls.log"
case "${1:-} ${2:-}" in
  "auth status") echo "github.com: Logged in to github.com account e2e (gh 대역)"; exit 0 ;;
  "repo view") echo '{"visibility":"PRIVATE","defaultBranchRef":{"name":"main"},"nameWithOwner":"acme/stationery"}'; exit 0 ;;
  "pr create")
    prev=""
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
git push -q origin main
echo "E2 결과로 시작: $src ($state)"
