#!/usr/bin/env python3
"""run-flow 보호 경로 목록을 만들고, 쓰기 전에 막고, 수락 전에 검사한다.

보호 경로는 5단계를 시작한 HEAD에 있던 테스트, 판정용 사례, 수락한 테스트다.
목록은 docs/context/run-flow/<상태 파일 이름>.protected 에 두고, 같은 내용을
git 공통 디렉터리(gongbang-protected/)에도 둔다. 상태 파일의 `- 현재 단계:`가
`완료`가 아닌 동안만 목록이 켜진다. 상태 파일이 없으면 켜진 것으로 본다.
목록은 흐름 브랜치에 커밋되므로, PR을 만들기 전에 close로 지워 머지로 새지 않게 한다.

  init   --state <상태 파일> [--base <커밋>] [--path <파일|폴더/> ...] [--no-auto] [--reseal]
         --reseal: 사본이 없는 기존 목록을 사용자가 확인한 뒤 그 내용으로 사본을 다시 만든다
  add    --state <상태 파일> <파일> ...     수락한 테스트를 지금 내용으로 더한다
  remove --state <상태 파일> <경로> ...     목록에서 뺀다(사용자가 정했을 때만)
  verify [--state <상태 파일>] [--rev <커밋> ...]
         보호 경로가 작업 트리, 인덱스, HEAD, --rev 커밋에서 바뀌거나
         지워지거나 보호 폴더에 새 파일이 생겼으면 실패한다
  close  --state <상태 파일>              verify를 통과하면 목록과 사본을 지운다
  guard  [--cwd <폴더>] [--tree] -- <경로> ...
         쓰기 도구 hook이 부른다. --tree는 폴더나 glob 범위다

경로 인자는 지금 폴더 기준이다.

종료 코드: 0 통과, 1 verify·close 위반, 3 guard 차단, 2 오류(호출한 쪽은 막힌 것으로 본다).
"""
import argparse, os, re, subprocess, sys
from pathlib import Path

FLOW_DIR = "docs/context/run-flow"
SNAP_DIR = "gongbang-protected"
HEADER = "# gongbang run-flow protected paths v1. protected_paths.py로만 고친다\n"
STAGE_RE = re.compile(r"^- 현재 단계:\s*(.*?)\s*$", re.M)
# specs/는 넣지 않는다. 설계 명세 문서 폴더로 흔히 쓰여 흐름이 고칠 문서까지 막는다.
TEST_DIRS = {"test", "tests", "__tests__", "spec"}
TEST_NAME = re.compile(
    r"(^test_.+\.py$|.+_test\.(py|go|rb|exs?)$|.+\.(test|spec)\.[cm]?[jt]sx?$"
    r"|.+(Test|Tests|Spec)\.(java|kt|cs|scala|swift)$|.+_spec\.rb$)"
)


class Fail(Exception):
    pass


def git(root, *args, stdin=None):
    r = subprocess.run(["git", *args], cwd=root, input=stdin, capture_output=True)
    if r.returncode != 0:
        raise Fail(f"git {' '.join(args)}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout


def toplevel(start):
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=start, capture_output=True, text=True)
    return Path(os.path.realpath(r.stdout.strip())) if r.returncode == 0 else None


def common_dir(root):
    return Path(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip())


# 목록 파일: "state\t경로", "base\t커밋", "dir\t경로/", "file\t경로\t블롭"(시작 HEAD),
# "added\t경로\t블롭"(수락한 테스트. 아직 커밋 전일 수 있어 인덱스·커밋에서는 없어도 된다)
def parse(text):
    m = {"state": None, "base": None, "files": {}, "dirs": [], "added": set()}
    for n, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        f = line.split("\t")
        if f[0] in ("state", "base") and len(f) == 2:
            m[f[0]] = f[1]
        elif f[0] in ("file", "added") and len(f) == 3:
            m["files"][f[1]] = f[2]
            if f[0] == "added":
                m["added"].add(f[1])
        elif f[0] == "dir" and len(f) == 2 and f[1].endswith("/"):
            m["dirs"].append(f[1])
        else:
            raise Fail(f"목록 {n}행을 읽지 못했다: {line!r}")
    if not m["state"]:
        raise Fail("목록에 state 줄이 없다")
    return m


def render(m):
    out = [HEADER, f"state\t{m['state']}\n", f"base\t{m['base']}\n"]
    out += [f"dir\t{d}\n" for d in sorted(set(m["dirs"]))]
    out += [f"{'added' if p in m['added'] else 'file'}\t{p}\t{b}\n" for p, b in sorted(m["files"].items())]
    return "".join(out)


def manifest_rel(state):
    return f"{FLOW_DIR}/{Path(state).stem}.protected"


def is_active(root, m):
    state = root / m["state"]
    if not state.is_file():
        return True
    found = STAGE_RE.findall(state.read_text(encoding="utf-8", errors="replace"))
    return not found or found[0] != "완료"


def manifests(root, active_only=True):
    d = root / FLOW_DIR
    out = []
    for p in sorted(d.glob("*.protected")) if d.is_dir() else []:
        m = parse(p.read_text(encoding="utf-8"))
        if not active_only or is_active(root, m):
            out.append((f"{FLOW_DIR}/{p.name}", m))
    return out


def check_rel(rel):
    if not rel or rel.startswith("/") or ".." in rel.split("/") or any(c in rel for c in "\t\n"):
        raise Fail(f"저장소 안의 상대 경로가 아니다: {rel!r}")
    return rel


def repo_rel(root, path):
    """저장소 안 경로를 루트 기준 POSIX 상대 경로로. 밖이면 None."""
    real = os.path.realpath(path)
    rel = os.path.relpath(real, root)
    return None if rel == ".." or rel.startswith("../") else Path(rel).as_posix()


def blob_of(root, rel):
    p = root / rel
    if p.is_symlink():
        return git(root, "hash-object", "--stdin", stdin=os.fsencode(os.readlink(p))).decode().strip()
    if not p.is_file():
        return None
    return git(root, "hash-object", "--", rel).decode().strip()


def tree_of(root, rev):
    out = {}
    for rec in git(root, "ls-tree", "-r", "-z", "--full-tree", rev).split(b"\0"):
        if rec:
            meta, path = rec.split(b"\t", 1)
            out[path.decode()] = meta.split()[2].decode()
    return out


def index_of(root):
    out, conflicts = {}, set()
    for rec in git(root, "ls-files", "-s", "-z").split(b"\0"):
        if rec:
            meta, path = rec.split(b"\t", 1)
            _, blob, stage = meta.decode().split()
            (conflicts.add(path.decode()) if stage != "0" else out.__setitem__(path.decode(), blob))
    return out, conflicts


def worktree_files_under(root, d):
    tracked = git(root, "ls-files", "-z", "--", d).split(b"\0")
    others = git(root, "ls-files", "-z", "--others", "--exclude-standard", "--", d).split(b"\0")
    return {p.decode() for p in tracked + others if p and (root / p.decode()).exists()}


def under(rel, d):
    return rel.startswith(d)


def is_test(rel):
    parts = rel.split("/")
    return any(p in TEST_DIRS for p in parts[:-1]) or bool(TEST_NAME.match(parts[-1]))


def save(root, rel, m):
    text = render(m)
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")
    snap = common_dir(root) / SNAP_DIR / Path(rel).name
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_text(text, encoding="utf-8")


def load_named(root, state):
    rel = manifest_rel(state)
    if not (root / rel).is_file():
        raise Fail(f"목록이 없다: {rel}. 먼저 init을 실행한다")
    return rel, parse((root / rel).read_text(encoding="utf-8"))


def repo_root():
    root = toplevel(os.getcwd())
    if root is None:
        raise Fail("git 저장소 안에서 실행해야 한다")
    return root


def cmd_init(a):
    root = repo_root()
    state = check_rel(repo_rel(root, a.state) or "")
    rel = manifest_rel(state)
    if (root / rel).is_file():
        m = parse((root / rel).read_text(encoding="utf-8"))
        snap = common_dir(root) / SNAP_DIR / Path(rel).name
        if not snap.is_file():
            # 사본이 없으면 목록이 셸로 바뀌었는지 알 수 없다. 사용자가 목록을 확인했을 때만 다시 봉인한다.
            if not a.reseal:
                raise Fail(f"{rel}의 사본이 없다({snap}). 목록을 사용자에게 보여 주고 맞다고 하면 --reseal을 붙여 다시 실행한다")
            snap.parent.mkdir(parents=True, exist_ok=True)
            snap.write_text(render(m), encoding="utf-8")
        print(f"이미 있는 목록을 그대로 쓴다: {rel} (base {m['base']}, 파일 {len(m['files'])}개)")
        return 0
    base = git(root, "rev-parse", "--verify", f"{a.base}^{{commit}}").decode().strip()
    tree = tree_of(root, base)
    m = {"state": state, "base": base, "files": {}, "dirs": [], "added": set()}
    if not a.no_auto:
        m["files"].update({p: b for p, b in tree.items() if is_test(p)})
    for raw in a.path:
        p = check_rel((repo_rel(root, raw) or "") + ("/" if raw.endswith(("/", os.sep)) else ""))
        if p.endswith("/"):
            hits = {f: b for f, b in tree.items() if under(f, p)}
            if not hits:
                raise Fail(f"시작 HEAD에 이 폴더의 파일이 없다: {p}")
            m["dirs"].append(p)
            m["files"].update(hits)
        elif p in tree:
            m["files"][p] = tree[p]
        else:
            raise Fail(f"시작 HEAD에 없는 파일이다: {p}. 폴더면 끝에 /를 붙인다")
    save(root, rel, m)
    print(f"목록을 만들었다: {rel} (base {base}, 파일 {len(m['files'])}개, 폴더 {len(m['dirs'])}개)")
    for p in sorted(m["files"]):
        print(f"  {p}")
    return 0


def cmd_add(a):
    root = repo_root()
    rel, m = load_named(root, a.state)
    for raw in a.paths:
        p = check_rel(repo_rel(root, raw) or "")
        b = blob_of(root, p)
        if b is None:
            raise Fail(f"파일이 없다: {p}")
        m["files"][p] = b
        m["added"].add(p)
        print(f"보호 목록에 더함: {p}")
    save(root, rel, m)
    return 0


def cmd_remove(a):
    root = repo_root()
    rel, m = load_named(root, a.state)
    for raw in a.paths:
        p = check_rel((repo_rel(root, raw) or "") + ("/" if raw.endswith("/") else ""))
        if p in m["dirs"]:
            m["dirs"].remove(p)
        elif m["files"].pop(p, None) is None:
            raise Fail(f"목록에 없다: {p}")
        m["added"].discard(p)
        print(f"보호 목록에서 뺌: {p}")
    save(root, rel, m)
    return 0


def verify_one(root, rel, m, revs):
    bad = []
    snap = common_dir(root) / SNAP_DIR / Path(rel).name
    if not snap.is_file():
        raise Fail(f"{rel}의 사본이 없다({snap}). 목록을 init·add·remove 밖에서 만들었거나 다른 clone이다")
    if snap.read_text(encoding="utf-8") != (root / rel).read_text(encoding="utf-8"):
        bad.append(f"{rel}: 목록 파일이 protected_paths.py 밖에서 바뀌었다")
    files, dirs = m["files"], m["dirs"]
    index, conflicts = index_of(root)
    views = [("작업 트리", None), ("인덱스", index), ("HEAD", tree_of(root, "HEAD"))]
    views += [(f"커밋 {r}", tree_of(root, r)) for r in revs]
    for p in sorted(conflicts):
        if p in files or any(under(p, d) for d in dirs):
            bad.append(f"{p}: 인덱스에 충돌이 남아 있다")
    for name, view in views:
        for p, want in sorted(files.items()):
            got = blob_of(root, p) if view is None else view.get(p)
            if got is None:
                if view is None or p not in m["added"]:
                    bad.append(f"{p}: {name}에서 지워졌다")
            elif got != want:
                bad.append(f"{p}: {name}에서 바뀌었다")
        for d in dirs:
            have = worktree_files_under(root, d) if view is None else {p for p in view if under(p, d)}
            for p in sorted(have - set(files)):
                bad.append(f"{p}: {name}에서 보호 폴더 {d}에 새로 생겼다")
    return bad


def cmd_verify(a):
    root = repo_root()
    targets = [load_named(root, a.state)] if a.state else manifests(root)
    bad = []
    for rel, m in targets:
        bad += verify_one(root, rel, m, a.rev)
    if bad:
        return report_bad("보호 경로 검사 실패. 수락하지 않는다:", bad)
    print(f"보호 경로 검사 통과 (목록 {len(targets)}개)")
    return 0


def report_bad(head, bad):
    print(head)
    for b in dict.fromkeys(bad):
        print(f"  {b}")
    return 1


def cmd_close(a):
    root = repo_root()
    rel, m = load_named(root, a.state)
    bad = verify_one(root, rel, m, [])
    if bad:
        return report_bad("보호 경로 검사 실패. 목록을 닫지 않는다:", bad)
    (root / rel).unlink()
    (common_dir(root) / SNAP_DIR / Path(rel).name).unlink()
    print(f"목록을 닫았다: {rel}. 이 삭제를 흐름 문서와 함께 커밋한다")
    return 0


GLOB_CHARS = re.compile(r"[*?\[{]")


def nearest_existing(path):
    p = Path(path)
    while not os.path.lexists(p) and p != p.parent:
        p = p.parent
    return p


def guard_one(path, cwd, tree):
    if tree:
        parts = Path(path).parts
        cut = next((i for i, s in enumerate(parts) if GLOB_CHARS.search(s)), len(parts))
        path = os.path.join(*parts[:cut]) if cut else "."
    absolute = os.path.normpath(os.path.join(cwd, os.path.expanduser(path)))
    anchor = nearest_existing(absolute)
    real = os.path.join(os.path.realpath(anchor), os.path.relpath(absolute, anchor))
    real = os.path.normpath(real)
    start = real if os.path.isdir(real) else os.path.dirname(real)
    start = str(nearest_existing(start))
    root = toplevel(start)
    if root is None:
        return None
    rel = repo_rel(root, real)
    if rel is None:
        return None
    for mrel, m in manifests(root):
        protected = set(m["files"]) | {mrel}
        if rel in protected or any(under(rel, d) for d in m["dirs"]):
            return f"{rel} ({mrel})"
        if tree:
            scope = "" if rel == "." else rel.rstrip("/") + "/"
            hit = next((p for p in sorted(protected | set(m["dirs"])) if p.startswith(scope)), None)
            if hit:
                return f"{hit} ({mrel}, 범위 {rel})"
    return None


def cmd_guard(a):
    if not a.paths:
        raise Fail("검사할 경로가 없다")
    for p in a.paths:
        hit = guard_one(p, a.cwd, a.tree)
        if hit:
            print(f"run-flow 보호 경로라 쓸 수 없다: {hit}. 기존 테스트와 판정용 사례는 고치지 않는다. "
                  "고쳐야 하면 멈추고 사용자에게 알린다")
            return 3
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init")
    p.add_argument("--state", required=True)
    p.add_argument("--base", default="HEAD")
    p.add_argument("--path", action="append", default=[])
    p.add_argument("--no-auto", action="store_true")
    p.add_argument("--reseal", action="store_true")
    for name in ("add", "remove"):
        p = sub.add_parser(name)
        p.add_argument("--state", required=True)
        p.add_argument("paths", nargs="+")
    p = sub.add_parser("verify")
    p.add_argument("--state")
    p.add_argument("--rev", action="append", default=[])
    p = sub.add_parser("close")
    p.add_argument("--state", required=True)
    p = sub.add_parser("guard")
    p.add_argument("--cwd", default=os.getcwd())
    p.add_argument("--tree", action="store_true")
    p.add_argument("paths", nargs="*")
    a = ap.parse_args(argv)
    try:
        cmds = {"init": cmd_init, "add": cmd_add, "remove": cmd_remove, "verify": cmd_verify, "close": cmd_close,
                "guard": cmd_guard}
        return cmds[a.cmd](a)
    except (Fail, OSError, ValueError) as e:
        print(f"오류: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
