#!/usr/bin/env python3
"""Self-check for run-flow start_stage.py on throwaway folders.

Run: python3 scripts/test_start_stage.py
"""
import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

CORE = Path(__file__).resolve().parent.parent / "skills/in-progress/run-flow/scripts/start_stage.py"
BRIEF = "docs/context/2026-11-27-list.md"
T1 = "docs/context/2026-11-27-list/01-sort.md"
T2 = "docs/context/2026-11-27-list/02-filter.md"
STATE = "docs/context/run-flow/2026-11-27-list.md"


def write(root, rel, text):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def brief(tickets=True):
    body = "# 목록\n\n- 작성일: 2026-11-27\n\n## 합의한 작업\n- 남은 일:\n  - [ ] 정렬\n\n## 확인 기준\n- [ ] `pytest`\n"
    if tickets:
        body += "\n## 티켓\n- [ ] [01: 정렬](./2026-11-27-list/01-sort.md)\n- [ ] [02: 필터](./2026-11-27-list/02-filter.md)\n"
    return body


def state(stage, review="안 함"):
    return (f"# 목록\n\n- 시작일: 2026-11-27\n- 현재 단계: {stage}\n- 멈춘 이유: 없음\n\n"
            f"## 결과물\n- brief: `{BRIEF}`\n\n## 리뷰\n- 통합 리뷰: {review}\n")


class StartStage(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="ss-")).resolve()
        write(self.root, BRIEF, brief())
        write(self.root, T1, "# 정렬\n\n- 상태: done\n")
        write(self.root, T2, "# 필터\n\n- 상태: ready-for-agent\n")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def run_core(self, *args):
        r = subprocess.run([sys.executable, str(CORE), *args], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_brief_and_ticket_with_open_ticket_start_at_5(self):
        self.assertEqual(self.run_core(BRIEF)["stage"], "5")
        r = self.run_core(T1)
        self.assertEqual((r["kind"], r["stage"], r["brief"]), ("ticket", "5", BRIEF))

    def test_done_brief_goes_to_5_only_when_its_open_flow_has_no_review(self):
        write(self.root, T2, "# 필터\n\n- 상태: 완료됨\n")
        self.assertEqual(self.run_core(BRIEF)["stage"], "5")  # 완료됨은 완료 값이 아니다
        r = self.run_core(BRIEF, "--done", "완료됨")
        self.assertEqual((r["stage"], r["state_file"]), ("6", None))
        write(self.root, STATE, state("5. 구현과 리뷰"))
        r = self.run_core(BRIEF, "--done", "완료됨")
        self.assertEqual((r["stage"], r["state_file"]), ("5", STATE))
        write(self.root, STATE, state("5. 구현과 리뷰", review="완료 (HEAD abc, 코드 지문 t-1)"))
        self.assertEqual(self.run_core(BRIEF, "--done", "완료됨")["stage"], "6")

    def test_brief_without_tickets_leaves_size_call_to_the_session(self):
        write(self.root, BRIEF, brief(tickets=False))
        r = self.run_core(BRIEF)
        self.assertIsNone(r["stage"])
        self.assertIn("크기", r["reason"])

    def test_state_requirements_planning_and_sentence(self):
        write(self.root, STATE, state("4. 티켓 분할"))
        self.assertEqual(self.run_core(STATE)["stage"], "4. 티켓 분할")
        write(self.root, "docs/req.md", "# 요구\n\n## 개발 범위\n- a\n\n## 요구사항\n- b\n")
        self.assertEqual(self.run_core("docs/req.md")["stage"], "2")
        write(self.root, "plan.pdf", "x")
        self.assertEqual(self.run_core("plan.pdf")["stage"], "1")
        self.assertEqual(self.run_core("목록에 정렬을 넣어줘")["kind"], "unknown")

    def test_no_argument_and_status_find_open_flows(self):
        r = self.run_core()
        self.assertEqual((r["stage"], r["brief"]), ("5", BRIEF))
        write(self.root, STATE, state("3. 작업 지시서"))
        write(self.root, "docs/context/run-flow/2026-11-01-old.md", state("완료"))
        r = self.run_core()
        self.assertEqual((r["stage"], r["state_file"]), ("3. 작업 지시서", STATE))
        write(self.root, "docs/context/run-flow/2026-11-27-other.md", state("2. 구체화"))
        r = self.run_core()
        self.assertIsNone(r["stage"])
        self.assertEqual(len(r["candidates"]), 2)
        r = self.run_core("status")
        self.assertEqual(sorted(c["stage"] for c in r["candidates"]), ["2. 구체화", "3. 작업 지시서"])
        self.assertEqual(r["candidates"][0]["remaining"], 1)


if __name__ == "__main__":
    unittest.main()
