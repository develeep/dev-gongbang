#!/usr/bin/env python3
"""run-ticket 교차 리뷰의 코드 지문, 기록 줄, 완료 게이트.

  fingerprint [--brief <brief>] [--exclude <경로> ...]
      작업 트리의 코드 지문 한 줄. 커밋하지 않은 변경과 새 파일이 들어가고,
      커밋만 해서는 바뀌지 않는다. 흐름 문서는 뺀다: --brief를 주면 brief와
      그 티켓 폴더(<brief 이름에서 .md를 뺀 폴더>/), 그리고 늘
      docs/context/run-flow/(run-flow 상태 파일과 보호 목록).
  record --mode other|same|self [--model <모델>] --fingerprint <지문>
      완료 기록의 `- 교차 리뷰:` 줄. other는 다른 회사 모델, same은 같은 회사
      대체, self는 새 컨텍스트 없이 한 자기 리뷰다. 모델을 확인할 수 없으면
      --model "수행 모델 확인 불가: <맡긴 수단>"으로 준다.
  gate [--brief <brief>] [--exclude <경로> ...] <기록> ...
      기록마다 마지막 `- 교차 리뷰:` 줄이 완료나 대체이고, 그 줄의 지문이 지금
      지문과 같아야 통과한다. 기록은 docs 티켓이나 brief 경로, 또는 GitHub
      완료 코멘트를 stdin으로 넘기는 `-`다. fingerprint와 같은 --brief,
      --exclude를 준다.

종료 코드: 0 통과, 1 gate 거부, 2 오류.
"""
import argparse, hashlib, os, re, subprocess, sys, tempfile
from pathlib import Path

FLOW_DIR = "docs/context/run-flow"
LINE_RE = re.compile(r"^- 교차 리뷰: (.*?)\s*$", re.M)
DONE_RE = re.compile(r"^(완료|대체) \(.*코드 지문 (\S+)\)$")


class Fail(Exception):
    pass


def git(root, *args, env=None, stdin=None):
    r = subprocess.run(["git", *args], cwd=root, env=env, input=stdin, capture_output=True)
    if r.returncode != 0:
        raise Fail(f"git {' '.join(args[:2])}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout


def repo_root():
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if r.returncode != 0:
        raise Fail("git 저장소 안에서 실행해야 한다")
    return Path(os.path.realpath(r.stdout.strip()))


def excludes(root, brief, extra):
    out = [FLOW_DIR]
    for p in ([brief, str(Path(brief).with_suffix(""))] if brief else []) + list(extra):
        rel = os.path.relpath(os.path.realpath(p), root)
        if rel == ".." or rel.startswith("../"):
            raise Fail(f"저장소 밖 경로다: {p}")
        out.append(Path(rel).as_posix())
    return out


def tree_token(root, skip):
    with tempfile.TemporaryDirectory() as d:
        env = {**os.environ, "GIT_INDEX_FILE": os.path.join(d, "index")}
        git(root, "read-tree", "HEAD", env=env)
        git(root, "add", "-u", env=env)
        # 새 파일은 일반 파일과 심볼릭 링크만 담는다. 장치 파일 같은 것이 있으면 git add 전체가 실패한다.
        new = [p for p in git(root, "ls-files", "-z", "--others", "--exclude-standard", env=env).split(b"\0")
               if p and (os.path.islink(root / os.fsdecode(p)) or os.path.isfile(root / os.fsdecode(p)))]
        if new:
            git(root, "add", "--pathspec-from-file=-", "--pathspec-file-nul", env=env, stdin=b"\0".join(new))
        git(root, "rm", "-r", "-q", "--cached", "--ignore-unmatch", "--", *skip, env=env)
        return "t-" + git(root, "write-tree", env=env).decode().strip()


def status_token(root, skip):
    # tree 해시를 못 구할 때: HEAD, 상태, diff로 만든 지문. 커밋하면 바뀐다.
    spec = ["--", ".", *[f":(exclude){p}" for p in skip]]
    h = hashlib.sha256()
    for args in (["rev-parse", "HEAD"], ["status", "--porcelain", *spec], ["diff", "HEAD", "--binary", *spec]):
        h.update(git(root, *args))
    return "s-" + h.hexdigest()[:40]


def fingerprint(root, skip):
    try:
        return tree_token(root, skip)
    except Fail as e:
        print(f"tree 지문을 구하지 못해 상태 지문을 쓴다: {e}", file=sys.stderr)
        return status_token(root, skip)


def record_line(mode, model, fp):
    if mode != "self" and not model:
        raise Fail("--model이 필요하다. 확인할 수 없으면 \"수행 모델 확인 불가: <맡긴 수단>\"을 준다")
    body = {"other": model, "same": f"같은 회사 모델 {model}", "self": "새 컨텍스트 없음, 메인 세션 자기 리뷰"}[mode]
    return f"- 교차 리뷰: {'완료' if mode == 'other' else '대체'} ({body}, 코드 지문 {fp})"


def gate(records, current):
    bad = []
    for name, text in records:
        lines = LINE_RE.findall(text)
        if not lines:
            bad.append(f"{name}: `- 교차 리뷰:` 줄이 없다. 교차 리뷰 없이 완료하지 않는다")
            continue
        m = DONE_RE.match(lines[-1])
        if not m:
            bad.append(f"{name}: 마지막 교차 리뷰 줄이 완료나 대체가 아니거나 코드 지문이 없다: {lines[-1]}")
        elif m.group(2) != current:
            bad.append(f"{name}: 리뷰 뒤에 코드가 바뀌었다(기록 {m.group(2)}, 지금 {current}). 바뀐 변경을 다시 리뷰한다")
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("fingerprint", "gate"):
        p = sub.add_parser(name)
        p.add_argument("--brief")
        p.add_argument("--exclude", action="append", default=[])
    sub.choices["gate"].add_argument("records", nargs="+")
    p = sub.add_parser("record")
    p.add_argument("--mode", choices=["other", "same", "self"], required=True)
    p.add_argument("--model")
    p.add_argument("--fingerprint", required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "record":
            print(record_line(a.mode, a.model, a.fingerprint))
            return 0
        root = repo_root()
        current = fingerprint(root, excludes(root, a.brief, a.exclude))
        if a.cmd == "fingerprint":
            print(current)
            return 0
        records = [("stdin" if r == "-" else r, sys.stdin.read() if r == "-" else Path(r).read_text(encoding="utf-8"))
                   for r in a.records]
        bad = gate(records, current)
        if bad:
            print("교차 리뷰 게이트 거부. 완료로 바꾸지 않는다:")
            print("\n".join(f"  {b}" for b in bad))
            return 1
        print(f"교차 리뷰 게이트 통과 (기록 {len(records)}개, 코드 지문 {current})")
        return 0
    except (Fail, OSError, ValueError) as e:
        print(f"오류: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
