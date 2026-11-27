#!/usr/bin/env python3
"""Self-check for run-flow protected_paths.py on throwaway git repos.

Run: python3 scripts/test_protected_paths.py
"""
import os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "skills/in-progress/run-flow/scripts/protected_paths.py"
MOD_COPY = ROOT / "mods/gongbang-mods/hooks/protected_paths.py"
STATE = "docs/context/run-flow/2026-11-26-demo.md"
MANIFEST = "docs/context/run-flow/2026-11-26-demo.protected"
GIT_ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, env=GIT_ENV, check=True, capture_output=True, text=True).stdout


def core(cwd, *args):
    return subprocess.run([sys.executable, str(CORE), *args], cwd=cwd, env=GIT_ENV, capture_output=True, text=True)


def write(root, rel, text):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class ProtectedPaths(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="pp-")).resolve()
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        files = {
            "src/app.py": "def f():\n    return 1\n",
            "tests/test_app.py": "def test_f():\n    assert True\n",
            "web/button.test.ts": "it('x', () => {})\n",
            "evals/judge/case-1.yaml": "expect: 1\n",
            "README.md": "# demo\n",
            "specs/login/spec.md": "# login spec\n",
            STATE: "# demo\n\n- 현재 단계: 5. 구현과 리뷰\n",
        }
        for rel, text in files.items():
            write(self.repo, rel, text)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "base")
        self.base = git(self.repo, "rev-parse", "HEAD").strip()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def init(self, *extra):
        r = core(self.repo, "init", "--state", STATE, "--path", "evals/judge/", *extra)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        return r

    def guard(self, *paths, cwd=None, tree=False):
        args = ["guard", "--cwd", str(cwd or self.repo)] + (["--tree"] if tree else []) + ["--", *map(str, paths)]
        return core(self.repo, *args)

    def verify(self, *extra):
        return core(self.repo, "verify", *extra)

    def snap(self):
        common = git(self.repo, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
        return Path(common) / "gongbang-protected/2026-11-26-demo.protected"

    # 목록 만들기
    def test_init_lists_start_head_tests_and_judge_dir_only(self):
        self.init()
        text = (self.repo / MANIFEST).read_text(encoding="utf-8")
        for rel in ("tests/test_app.py", "web/button.test.ts", "evals/judge/case-1.yaml"):
            self.assertIn(f"\t{rel}\t", text)
        self.assertIn("dir\tevals/judge/", text)
        self.assertNotIn("src/app.py", text)
        self.assertNotIn("specs/login/spec.md", text)
        self.assertIn(f"base\t{self.base}", text)
        common = git(self.repo, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
        self.assertTrue((Path(common) / "gongbang-protected/2026-11-26-demo.protected").is_file())

    def test_init_accepts_dot_slash_and_hidden_paths(self):
        write(self.repo, ".judge/case.yaml", "x\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "hidden judge")
        r = core(self.repo, "init", "--state", STATE, "--no-auto", "--path", "./.judge/", "--path", "./src/app.py")
        self.assertEqual(r.returncode, 0, r.stderr)
        text = (self.repo / MANIFEST).read_text(encoding="utf-8")
        self.assertIn("dir\t.judge/", text)
        self.assertIn("file\tsrc/app.py\t", text)
        self.assertNotIn("tests/test_app.py", text)

    def test_init_paths_are_relative_to_cwd(self):
        r = core(self.repo / "src", "init", "--state", f"../{STATE}", "--no-auto", "--path", "app.py")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("file\tsrc/app.py\t", (self.repo / MANIFEST).read_text(encoding="utf-8"))

    def test_init_again_without_snapshot_needs_reseal(self):
        self.init()
        self.snap().unlink()
        self.assertEqual(core(self.repo, "init", "--state", STATE).returncode, 2)
        self.assertFalse(self.snap().exists())
        r = core(self.repo, "init", "--state", STATE, "--reseal")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.verify().returncode, 0)

    def test_init_again_keeps_existing_list_for_resumed_flow(self):
        self.init()
        before = (self.repo / MANIFEST).read_text(encoding="utf-8")
        write(self.repo, "src/new.py", "x = 1\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "later")
        r = core(self.repo, "init", "--state", STATE)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.repo / MANIFEST).read_text(encoding="utf-8"), before)

    # 쓰기 전 차단
    def test_guard_blocks_protected_paths_in_every_spelling(self):
        self.init()
        alias = self.tmp / "alias"
        alias.symlink_to(self.repo)
        link = self.repo / "src/link_to_test.py"
        link.symlink_to(self.repo / "tests/test_app.py")
        for p in ("tests/test_app.py", self.repo / "tests/test_app.py", alias / "tests/test_app.py",
                  "src/../tests/test_app.py", link, MANIFEST, "evals/judge/new-case.yaml"):
            r = self.guard(p)
            self.assertEqual(r.returncode, 3, f"{p}: {r.stdout}{r.stderr}")
        r = self.guard("test_app.py", cwd=self.repo / "tests")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)

    def test_guard_allows_normal_and_new_test_writes(self):
        self.init()
        for p in ("src/app.py", "tests/test_new.py", "README.md", STATE, "new/dir/file.py", self.tmp / "outside.txt"):
            r = self.guard(p)
            self.assertEqual(r.returncode, 0, f"{p}: {r.stdout}{r.stderr}")

    def test_guard_allows_everything_when_flow_is_complete(self):
        self.init()
        write(self.repo, STATE, "# demo\n\n- 현재 단계: 완료\n")
        self.assertEqual(self.guard("tests/test_app.py").returncode, 0)

    def test_guard_fails_closed_when_state_file_is_missing(self):
        self.init()
        (self.repo / STATE).unlink()
        self.assertEqual(self.guard("tests/test_app.py").returncode, 3)

    def test_guard_tree_scope_blocks_only_scopes_holding_protected_files(self):
        self.init()
        self.assertEqual(self.guard("tests", tree=True).returncode, 3)
        self.assertEqual(self.guard("tests/**/*.py", tree=True).returncode, 3)
        self.assertEqual(self.guard(".", tree=True).returncode, 3)
        self.assertEqual(self.guard("src", tree=True).returncode, 0)

    def test_guard_follows_nested_worktree_and_nested_repo(self):
        self.init()
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "flow docs")
        git(self.repo, "worktree", "add", "-q", "-b", "ticket", str(self.repo / ".wt/ticket"))
        wt = self.repo / ".wt/ticket"
        self.assertEqual(self.guard(wt / "tests/test_app.py").returncode, 3)
        self.assertEqual(self.guard(wt / "src/app.py").returncode, 0)
        nested = self.repo / "vendor/lib"
        nested.mkdir(parents=True)
        git(nested, "init", "-q")
        write(nested, "tests/test_app.py", "x\n")
        self.assertEqual(self.guard(nested / "tests/test_app.py").returncode, 0)

    def test_guard_reports_errors_as_exit_2(self):
        r = core(self.repo, "guard", "--cwd", str(self.repo))
        self.assertEqual(r.returncode, 2)

    # 사후 수락 검사
    def test_verify_passes_with_unrelated_changes(self):
        self.init()
        write(self.repo, "src/app.py", "def f():\n    return 2\n")
        write(self.repo, "tests/test_new.py", "def test_new():\n    pass\n")
        write(self.repo, "tests/__pycache__/x.pyc", "junk")
        write(self.repo, "notes.txt", "x\n")
        r = self.verify()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_verify_catches_worktree_staged_commit_and_deletion(self):
        cases = {
            "worktree": lambda: write(self.repo, "tests/test_app.py", "def test_f():\n    assert False\n"),
            "staged": lambda: (write(self.repo, "tests/test_app.py", "changed\n"),
                               git(self.repo, "add", "tests/test_app.py"),
                               write(self.repo, "tests/test_app.py", "def test_f():\n    assert True\n")),
            "commit": lambda: (write(self.repo, "web/button.test.ts", "it.skip('x', () => {})\n"),
                               git(self.repo, "commit", "-qam", "skip")),
            "delete": lambda: (self.repo / "tests/test_app.py").unlink(),
            "judge-new": lambda: write(self.repo, "evals/judge/case-2.yaml", "expect: 2\n"),
            "judge-delete": lambda: git(self.repo, "rm", "-q", "evals/judge/case-1.yaml"),
        }
        for name, act in cases.items():
            with self.subTest(name):
                self.tearDown()
                self.setUp()
                self.init()
                act()
                r = self.verify()
                self.assertEqual(r.returncode, 1, f"{name}: {r.stdout}{r.stderr}")

    def test_verify_checks_reported_worker_commit(self):
        self.init()
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "flow docs")
        git(self.repo, "switch", "-qc", "worker")
        write(self.repo, "tests/test_app.py", "edited by worker\n")
        git(self.repo, "commit", "-qam", "worker edit")
        git(self.repo, "switch", "-q", "main")
        self.assertEqual(self.verify().returncode, 0)
        r = self.verify("--rev", "worker")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("tests/test_app.py", r.stdout)

    def test_verify_catches_manifest_tampering_and_missing_snapshot(self):
        self.init()
        text = (self.repo / MANIFEST).read_text(encoding="utf-8")
        write(self.repo, MANIFEST, "".join(l for l in text.splitlines(True) if "test_app.py" not in l))
        self.assertEqual(self.verify().returncode, 1)
        write(self.repo, MANIFEST, text)
        common = git(self.repo, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
        (Path(common) / "gongbang-protected/2026-11-26-demo.protected").unlink()
        self.assertEqual(self.verify().returncode, 2)

    def test_verify_named_state_checks_even_without_other_flows(self):
        r = self.verify()
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.verify("--state", STATE)
        self.assertEqual(r.returncode, 2, r.stdout)

    # 수락한 테스트 더하기와 빼기
    def test_add_protects_accepted_test_and_remove_releases_it(self):
        self.init()
        write(self.repo, "tests/test_new.py", "def test_new():\n    pass\n")
        self.assertEqual(self.guard("tests/test_new.py").returncode, 0)
        r = core(self.repo, "add", "--state", STATE, "tests/test_new.py")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.guard("tests/test_new.py").returncode, 3)
        self.assertEqual(self.verify().returncode, 0)
        write(self.repo, "tests/test_new.py", "def test_new():\n    assert 0\n")
        self.assertEqual(self.verify().returncode, 1)
        r = core(self.repo, "remove", "--state", STATE, "tests/test_new.py")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.guard("tests/test_new.py").returncode, 0)
        self.assertEqual(self.verify().returncode, 0)

    # 흐름 끝
    def test_close_refuses_violation_then_removes_list_and_snapshot(self):
        self.init()
        write(self.repo, "tests/test_app.py", "changed\n")
        self.assertEqual(core(self.repo, "close", "--state", STATE).returncode, 1)
        self.assertTrue((self.repo / MANIFEST).is_file())
        git(self.repo, "checkout", "--", "tests/test_app.py")
        r = core(self.repo, "close", "--state", STATE)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertFalse((self.repo / MANIFEST).exists())
        self.assertFalse(self.snap().exists())
        self.assertEqual(self.guard("tests/test_app.py").returncode, 0)

    def test_mod_copy_matches_core(self):
        self.assertEqual(MOD_COPY.read_bytes(), CORE.read_bytes())


if __name__ == "__main__":
    unittest.main()
