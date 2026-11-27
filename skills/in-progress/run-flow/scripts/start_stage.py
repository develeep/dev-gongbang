#!/usr/bin/env python3
"""run-flow 0단계: 인자로 시작 단계를 판정한다.

  start_stage.py [<인자>] [--done <완료 값> ...]

인자는 status, 상태 파일, brief, 티켓, 요구사항 문서, 기획서 파일, 폴더 경로이거나
비워 둔다. 저장소의 docs 문서로 정해지는 것만 판정하고 JSON 한 줄을 낸다.

  kind        status | state | brief | ticket | requirements | planning | search | unknown
  stage       시작 단계("1"~"7"). 정하지 못하면 null
  reason      근거 한 줄
  state_file  이어 쓸 끝나지 않은 상태 파일. 없으면 null
  candidates  고를 후보(status, 여럿 찾음): path, title, stage, stopped, remaining

stage가 null이면 SKILL.md 0단계 표로 이 세션이 정한다. 요청 문장, 링크,
GitHub 이슈, GitHub 티켓 상태, `## 티켓`이 없는 brief의 크기 판단이 그렇다.
--done은 레포 규칙이나 상태 파일 `## 결정`이 정한 완료 표시다(done은 늘 완료).
"""
import argparse, json, os, re, sys
from pathlib import Path

STAGE_RE = re.compile(r"^- 현재 단계:\s*(.*?)\s*$", re.M)
BRIEF_RE = re.compile(r"^- 작성일: \d{4}-\d{2}-\d{2}", re.M)
STATUS_RE = re.compile(r"^- 상태:\s*(\S+)", re.M)
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
SKIP_DIRS = {".git", "node_modules"}


def section(text, name):
    m = re.search(rf"^## {re.escape(name)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else None


def read(p):
    try:
        return Path(p).read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeError):
        return ""


def md_files(top):
    seen = set()
    for d, dirs, files in os.walk(top, followlinks=True):
        real = os.path.realpath(d)
        if real in seen:
            dirs[:] = []
            continue
        seen.add(real)
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        yield from (Path(d) / f for f in sorted(files) if f.endswith(".md"))


def stage_of(text):
    m = STAGE_RE.search(text)
    return m.group(1) if m else None


def first_title(text):
    m = re.search(r"^# (.+)$", text, re.M)
    return m.group(1).strip() if m else ""


class Repo:
    def __init__(self, top, done):
        self.top, self.done = top, done
        self.docs = {p: read(p) for p in md_files(top)}

    def states(self):
        return [p for p, t in self.docs.items() if stage_of(t) and stage_of(t) != "완료"]

    def briefs(self):
        return [p for p, t in self.docs.items() if BRIEF_RE.search(t)]

    def tickets(self, brief):
        """brief의 docs 티켓 경로, GitHub 티켓 수. `## 티켓`이 없으면 None."""
        sec = section(self.docs.get(brief) or read(brief), "티켓")
        if sec is None:
            return None
        docs = [(brief.parent / link.split("#")[0]).resolve() for link in LINK_RE.findall(sec)
                if "://" not in link and link.split("#")[0].endswith(".md")]
        return docs, len(re.findall(r"^\s*- \[[ x]\] #\d+", sec, re.M))

    def remaining(self, brief):
        """끝나지 않은 티켓 수. GitHub 티켓이 있으면 None(gh로 본다)."""
        t = self.tickets(brief)
        if t is None:
            work = section(self.docs.get(brief) or read(brief), "합의한 작업") or ""
            return len(re.findall(r"^\s*- \[ \]", work, re.M))
        docs, github = t
        if github:
            return None
        return sum(1 for p in docs if (STATUS_RE.search(read(p)) or [None, None])[1] not in self.done)

    def state_for(self, doc):
        """doc을 `## 결과물`에 적은 끝나지 않은 상태 파일."""
        rel = os.path.relpath(doc, self.top)
        for s in self.states():
            out = section(self.docs[s], "결과물") or ""
            if rel in out or Path(doc).name in out:
                return s
        return None

    def candidate(self, p):
        t = self.docs.get(p) or read(p)
        if stage_of(t):
            brief = next((b for b in self.briefs() if Path(b).name in (section(t, "결과물") or "")), None)
            m = re.search(r"^- 멈춘 이유:\s*(.*)$", t, re.M)
            return {"path": rel(p), "title": first_title(t), "stage": stage_of(t), "stopped": m.group(1) if m else None,
                    "remaining": self.remaining(brief) if brief else None}
        return {"path": rel(p), "title": first_title(t), "remaining": self.remaining(p)}


def rel(p):
    return os.path.relpath(p)


def judge_brief(repo, brief, kind="brief"):
    state = repo.state_for(brief)
    left = repo.remaining(brief)
    if left is None:
        return dict(kind=kind, stage=None, reason="GitHub 티켓 상태는 gh로 확인한다", state_file=state)
    if left and repo.tickets(brief) is None:
        return dict(kind=kind, stage=None, reason="`## 티켓`이 없는 brief: 남은 일 크기로 4나 5를 정한다", state_file=state)
    if left:
        return dict(kind=kind, stage="5", reason=f"끝나지 않은 티켓 {left}개", state_file=state)
    review = section(repo.docs[state], "리뷰") if state else None
    if review and re.search(r"^- 통합 리뷰: 안 함", review, re.M):
        return dict(kind=kind, stage="5", reason="티켓은 모두 끝났고 통합 리뷰를 안 함", state_file=state)
    return dict(kind=kind, stage="6", reason="티켓이 모두 끝남", state_file=state)


def search(repo):
    states = repo.states()
    if len(states) == 1:
        return dict(kind="search", stage=stage_of(repo.docs[states[0]]), reason="끝나지 않은 상태 파일 하나",
                    state_file=rel(states[0]))
    if states:
        return dict(kind="search", stage=None, reason="끝나지 않은 상태 파일 여럿: 고르게 한다",
                    candidates=[repo.candidate(s) for s in states])
    open_briefs = [b for b in repo.briefs() if repo.remaining(b) != 0]
    if len(open_briefs) == 1:
        return {**judge_brief(repo, open_briefs[0]), "kind": "search", "brief": rel(open_briefs[0])}
    if open_briefs:
        return dict(kind="search", stage=None, reason="끝나지 않은 brief 여럿: 고르게 한다",
                    candidates=[repo.candidate(b) for b in open_briefs])
    return dict(kind="search", stage=None, reason="끝나지 않은 상태 파일과 docs brief가 없다: GitHub brief를 보거나 묻는다")


def judge(arg, done):
    root = Path(os.getcwd())
    if arg == "status":
        repo = Repo(root, done)
        return dict(kind="status", stage=None, reason="끝나지 않은 흐름 목록",
                    candidates=[repo.candidate(s) for s in repo.states()])
    if not arg:
        return search(Repo(root, done))
    p = Path(arg)
    if not p.exists():
        return dict(kind="unknown", stage=None, reason="파일이나 폴더가 아니다: 요청 문장, 링크, 이슈 번호는 0단계 표로 정한다")
    if p.is_dir():
        return search(Repo(p, done))
    p = p.resolve()
    repo = Repo(root, done)
    text = read(p)
    if p.suffix == ".md" and stage_of(text):
        return dict(kind="state", stage=stage_of(text), reason="상태 파일의 현재 단계", state_file=rel(p))
    if p.suffix == ".md" and BRIEF_RE.search(text):
        return judge_brief(repo, p)
    owner = next((b for b in repo.briefs() if p in (repo.tickets(b) or ([], 0))[0]), None)
    if owner:
        return {**judge_brief(repo, owner, kind="ticket"), "brief": rel(owner)}
    if p.suffix == ".md" and re.search(r"^## 개발 범위", text, re.M) and re.search(r"^## 요구사항", text, re.M):
        state = repo.state_for(p)
        return dict(kind="requirements", stage=stage_of(repo.docs[state]) if state else "2",
                    reason="요구사항 문서" + (", 이어 쓸 상태 파일 있음" if state else ""), state_file=rel(state) if state else None)
    if p.suffix.lower() in (".md", ".pdf", ".ppt", ".pptx"):
        return dict(kind="planning", stage="1", reason="위 행에 맞지 않는 기획서 파일")
    return dict(kind="unknown", stage=None, reason="판정할 수 없는 파일 형식")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arg", nargs="?", default="")
    ap.add_argument("--done", action="append", default=[])
    a = ap.parse_args(argv)
    out = {"state_file": None, "candidates": [], **judge(a.arg, {"done", *a.done})}
    if isinstance(out["state_file"], Path):
        out["state_file"] = rel(out["state_file"])
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
