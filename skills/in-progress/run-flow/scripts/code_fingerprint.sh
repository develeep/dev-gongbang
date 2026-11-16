#!/usr/bin/env bash
# 흐름 문서를 뺀 작업 트리의 tree 해시를 출력한다.
set -euo pipefail

usage() {
  cat <<'USAGE'
사용법: code_fingerprint.sh [흐름 문서 경로...]

저장소 안에서 실행한다. 지금 작업 트리의 tree 해시 한 줄을 출력한다.
커밋하지 않은 변경과 새 파일이 들어가고, 인자로 준 경로(파일이나 폴더)는 뺀다.
리뷰한 코드와 지금 코드가 같은지 비교할 때 쓴다. 실제 인덱스는 바꾸지 않는다.

예: code_fingerprint.sh docs/context docs/adr/0003-cache.md
USAGE
}

case "${1:-}" in -h|--help) usage; exit 0 ;; esac

if ! git_dir=$(git rev-parse --absolute-git-dir 2>/dev/null); then
  echo "오류: git 저장소 안에서 실행해야 한다. 지금 위치: $PWD" >&2
  exit 2
fi
if ! git rev-parse --verify -q HEAD >/dev/null; then
  echo "오류: 커밋이 하나도 없어 HEAD를 읽을 수 없다. 커밋을 만든 뒤 다시 실행한다." >&2
  exit 2
fi

# 임시 인덱스에서만 작업하므로 사용자가 stage한 내용은 그대로 남는다.
export GIT_INDEX_FILE="$git_dir/run-flow-fingerprint-index"
trap 'rm -f "$GIT_INDEX_FILE"' EXIT

cd "$(git rev-parse --show-toplevel)"
git read-tree HEAD
git add -A
if [ "$#" -gt 0 ]; then
  git rm -r -q --cached --ignore-unmatch -- "$@"
fi
git write-tree
