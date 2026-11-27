#!/usr/bin/env bash
# E1 e2e-request-single: 작은 기능 요청 한 줄로 시작하는 저장소.
# 네트워크를 쓰지 않는다. 원격이 없어 brief 저장 위치는 docs가 추천된다.
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
cat > src/slug.py <<'PY'
import re


def slugify(text):
    """제목을 URL에 쓰는 slug로 바꾼다."""
    text = text.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", text)
PY
cat > tests/test_slug.py <<'PY'
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from slug import slugify


class SlugifyTest(unittest.TestCase):
    def test_words_joined_with_hyphen(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_lowercase(self):
        self.assertEqual(slugify("ABC"), "abc")


if __name__ == "__main__":
    unittest.main()
PY
git add -A
git commit -qm "feature: slugify 추가"
