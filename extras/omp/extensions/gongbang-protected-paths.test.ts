// bun test extras/omp/extensions
// Drives the extension's tool_call handler with the event shape omp 19.2.1
// passes ({ toolName, input }) against throwaway git repositories.
import { afterEach, beforeEach, expect, test } from "bun:test";
import { spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, realpathSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import register, { CORE } from "./gongbang-protected-paths.ts";

const STATE = "docs/context/run-flow/2026-11-26-demo.md";
const env = { ...process.env, GIT_CONFIG_GLOBAL: "/dev/null", GIT_AUTHOR_NAME: "t", GIT_AUTHOR_EMAIL: "t@t", GIT_COMMITTER_NAME: "t", GIT_COMMITTER_EMAIL: "t@t" };

let tmp = "";
let repo = "";
const run = (cwd: string, ...argv: string[]) => {
	const r = spawnSync(argv[0]!, argv.slice(1), { cwd, env, encoding: "utf8" });
	if (r.status !== 0) throw new Error(`${argv.join(" ")}: ${r.stderr}`);
	return r.stdout;
};
const put = (root: string, rel: string, text: string) => {
	mkdirSync(dirname(join(root, rel)), { recursive: true });
	writeFileSync(join(root, rel), text);
};

type Handler = (event: { type: string; toolName: string; toolCallId: string; input: Record<string, unknown> }, ctx: { cwd: string }) => unknown;
let handler: Handler;
const call = async (toolName: string, input: Record<string, unknown>, cwd = repo) =>
	(await handler({ type: "tool_call", toolName, toolCallId: "t1", input }, { cwd })) as { block?: boolean; reason?: string } | undefined;

beforeEach(() => {
	tmp = realpathSync(mkdtempSync(join(tmpdir(), "omp-pp-")));
	repo = join(tmp, "repo");
	mkdirSync(repo);
	run(repo, "git", "init", "-q", "-b", "main");
	put(repo, "src/app.py", "x = 1\n");
	put(repo, "tests/test_app.py", "def test_f():\n    assert True\n");
	put(repo, STATE, "# demo\n\n- 현재 단계: 5. 구현과 리뷰\n");
	run(repo, "git", "add", "-A");
	run(repo, "git", "commit", "-qm", "base");
	run(repo, "python3", CORE!, "init", "--state", STATE);
	const handlers: Handler[] = [];
	register({ on: (name: string, h: Handler) => name === "tool_call" && handlers.push(h) } as never);
	expect(handlers.length).toBe(1);
	handler = handlers[0]!;
});
afterEach(() => rmSync(tmp, { recursive: true, force: true }));

test("write, every edit mode and ast_edit on a protected test are blocked", async () => {
	const blocked: [string, Record<string, unknown>][] = [
		["write", { path: "tests/test_app.py", content: "x" }],
		["write", { path: `[${repo}/tests/test_app.py#1A2B]`, content: "x" }],
		["edit", { input: "[tests/test_app.py#1A2B]\nPUT 1.=1:\n+x\n" }],
		["edit", { input: "*** Begin Patch\n*** Update File: src/app.py\n@@\n-x = 1\n+x = 2\n*** Delete File: tests/test_app.py\n*** End Patch\n" }],
		["edit", { input: "*** Begin Patch\n*** Update File: src/app.py\n*** Move to: tests/test_app.py\n*** End Patch\n" }],
		["edit", { input: "*** Edit File: tests/test_app.py\n*** Find\nassert True\n*** Replace\nassert False\n" }],
		["edit", { input: "# tests/test_app.py\n- make it fail\n" }],
		["edit", { path: "tests/test_app.py", old_string: "True", new_string: "False" }],
		["edit", { path: "src/app.py", edits: [{ op: "update", rename: "tests/test_app.py" }] }],
		["edit", { input: "[src/app.py#1A2B]\nMV tests/test_app.py\n" }],
		["edit", { input: '[src/app.py#1A2B]\nMV "tests/test_app.py"\n' }],
		["ast_edit", { ops: [{ pat: "assert True", out: "assert False" }], paths: ["tests/"] }],
		["edit", { input: "no header at all" }],
	];
	for (const [tool, input] of blocked) {
		const r = await call(tool, input);
		expect({ tool, input, block: r?.block }).toEqual({ tool, input, block: true });
	}
	expect((await call("write", { path: "tests/test_app.py", content: "x" }))?.reason).toContain("보호 경로");
});

test("normal writes, new tests, other tools and finished flows pass", async () => {
	for (const [tool, input] of [
		["write", { path: "src/new.py", content: "x" }],
		["write", { path: "tests/test_new.py", content: "x" }],
		["edit", { input: "[src/app.py#1A2B]\nPUT 1.=1:\n+x = 2\n" }],
		["ast_edit", { ops: [], paths: ["src/**/*.py"] }],
		["bash", { command: "sed -i s/True/False/ tests/test_app.py" }],
		["read", { path: "tests/test_app.py" }],
		["write", { path: "local://notes.md", content: "x" }],
	] as [string, Record<string, unknown>][]) {
		expect({ tool, r: await call(tool, input) }).toEqual({ tool, r: undefined });
	}
	// 끝난 흐름은 python3 없이 지나간다. 켜진 흐름은 python3가 없으면 막는다.
	const path = process.env.PATH;
	process.env.PATH = "/nonexistent";
	try {
		expect((await call("write", { path: "tests/test_app.py", content: "x" }))?.block).toBe(true);
		put(repo, STATE, "# demo\n\n- 현재 단계: 완료\n");
		expect(await call("write", { path: "tests/test_app.py", content: "x" })).toBeUndefined();
	} finally {
		process.env.PATH = path;
	}
});

test("absolute, symlink alias and nested worktree spellings are blocked", async () => {
	symlinkSync(repo, join(tmp, "alias"));
	run(repo, "git", "add", "-A");
	run(repo, "git", "commit", "-qm", "flow docs");
	run(repo, "git", "worktree", "add", "-q", "-b", "ticket", join(repo, ".wt/ticket"));
	for (const p of [join(repo, "tests/test_app.py"), join(tmp, "alias/tests/test_app.py"), join(repo, ".wt/ticket/tests/test_app.py")]) {
		expect({ p, block: (await call("write", { path: p, content: "x" }, tmp))?.block }).toEqual({ p, block: true });
	}
	expect(await call("write", { path: join(repo, ".wt/ticket/src/new.py"), content: "x" }, tmp)).toBeUndefined();
});

test("a repository without a list never needs the core", async () => {
	const plain = join(tmp, "plain");
	mkdirSync(plain);
	run(plain, "git", "init", "-q");
	put(plain, "tests/test_app.py", "x\n");
	expect(await call("write", { path: "tests/test_app.py", content: "y" }, plain)).toBeUndefined();
});
