#!/usr/bin/env python3
"""Self-check for run-ticket cross_review.py on throwaway git repos.

Run: python3 scripts/test_cross_review.py
"""
import os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "skills/in-progress/run-ticket/scripts/cross_review.py"
BRIEF = "docs/context/2026-11-27-demo.md"
TICKET = "docs/context/2026-11-27-demo/01-a.md"
GIT_ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, env=GIT_ENV, check=True, capture_output=True, text=True).stdout


def write(root, rel, text):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class CrossReview(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp(prefix="cr-")).resolve()
        git(self.repo, "init", "-q", "-b", "main")
        for rel, text in {"src/app.py": "x = 1\n", BRIEF: "# demo\n", TICKET: "- 상태: ready-for-agent\n",
                          "docs/context/run-flow/s.md": "- 현재 단계: 5\n"}.items():
            write(self.repo, rel, text)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "base")

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def core(self, *args, stdin=None):
        return subprocess.run([sys.executable, str(CORE), *args], cwd=self.repo, env=GIT_ENV, input=stdin,
                              capture_output=True, text=True)

    def fp(self):
        r = self.core("fingerprint", "--brief", BRIEF)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def record(self, line):
        write(self.repo, TICKET, f"- 상태: done\n\n## 완료 기록\n{line}\n")

    def test_fingerprint_follows_code_not_flow_docs_or_commits(self):
        before = self.fp()
        write(self.repo, TICKET, "- 상태: done\n")
        write(self.repo, BRIEF, "# demo\n- [x] 01\n")
        write(self.repo, "docs/context/run-flow/s.protected", "state\tx\n")
        self.assertEqual(self.fp(), before)
        write(self.repo, "src/new.py", "y = 2\n")
        changed = self.fp()
        self.assertNotEqual(changed, before)
        git(self.repo, "add", "src/new.py")
        git(self.repo, "commit", "-qm", "user commit")
        self.assertEqual(self.fp(), changed)

    def test_fingerprint_skips_special_files(self):
        os.mkfifo(self.repo / "src/pipe")
        r = self.core("fingerprint")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(r.stdout.startswith("t-"), r.stdout + r.stderr)

    def test_record_lines(self):
        self.assertEqual(self.core("record", "--mode", "other", "--model", "gpt-5", "--fingerprint", "t-1").stdout,
                         "- 교차 리뷰: 완료 (gpt-5, 코드 지문 t-1)\n")
        self.assertEqual(self.core("record", "--mode", "same", "--model", "sonnet", "--fingerprint", "t-1").stdout,
                         "- 교차 리뷰: 대체 (같은 회사 모델 sonnet, 코드 지문 t-1)\n")
        self.assertEqual(self.core("record", "--mode", "self", "--fingerprint", "t-1").stdout,
                         "- 교차 리뷰: 대체 (새 컨텍스트 없음, 메인 세션 자기 리뷰, 코드 지문 t-1)\n")
        self.assertEqual(self.core("record", "--mode", "same", "--fingerprint", "t-1").returncode, 2)

    def test_gate_passes_current_review_and_refuses_missing_skipped_or_stale(self):
        write(self.repo, "src/app.py", "x = 2\n")
        line = self.core("record", "--mode", "same", "--model", "sonnet", "--fingerprint", self.fp()).stdout.strip()
        cases = {
            "current": (f"- 교차 리뷰: 건너뜀 (없음)\n{line}", 0),
            "missing": ("- 커밋: 안 함", 1),
            "skipped": (f"{line}\n- 교차 리뷰: 건너뜀 (모델 없음)", 1),
            "no fingerprint": ("- 교차 리뷰: 완료 (gpt-5)", 1),
        }
        for name, (text, code) in cases.items():
            with self.subTest(name):
                self.record(text)
                r = self.core("gate", "--brief", BRIEF, TICKET)
                self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        self.record(line)
        write(self.repo, "src/app.py", "x = 3\n")
        r = self.core("gate", "--brief", BRIEF, TICKET)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("리뷰 뒤에 코드가 바뀌었다", r.stdout)

    def test_gate_reads_github_comment_from_stdin(self):
        line = self.core("record", "--mode", "other", "--model", "gpt-5", "--fingerprint", self.fp()).stdout
        self.assertEqual(self.core("gate", "--brief", BRIEF, "-", stdin=f"## 완료 기록\n{line}").returncode, 0)
        self.assertEqual(self.core("gate", "--brief", BRIEF, "-", stdin="## 완료 기록\n").returncode, 1)


if __name__ == "__main__":
    unittest.main()
