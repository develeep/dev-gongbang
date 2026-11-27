// gongbang-protected-paths: omp의 쓰기 도구가 run-flow 보호 경로(흐름 시작 HEAD의
// 테스트, 판정용 사례, 수락한 테스트, 목록 파일)를 고치지 못하게 막는다.
// 판정은 run-flow의 scripts/protected_paths.py(guard)가 한다. 이 파일은 저장소의
// extras/omp/extensions/ 에서 ~/.omp/agent/extensions/ 로 링크해 설치한다. omp는
// 링크를 실제 경로로 풀어 불러오므로 아래 CORE 경로가 저장소 안을 가리킨다.
// bash, eval, python으로 쓰는 것은 여기서 막지 않는다. run-flow 수락 검사
// (protected_paths.py verify)가 사후에 잡는다.
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import { spawnSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync, realpathSync, statSync } from "node:fs";
import { dirname, isAbsolute, join, resolve } from "node:path";

// run-flow를 다른 버킷으로 옮겨도 찾도록 버킷 이름을 고정하지 않는다. 못 찾으면 check가 막는다.
const SKILLS = join(import.meta.dir, "../../../skills");
export const CORE = (() => {
	try {
		return readdirSync(SKILLS).map(b => join(SKILLS, b, "run-flow/scripts/protected_paths.py")).find(p => existsSync(p));
	} catch {
		return undefined;
	}
})();
const FLOW_DIR = "docs/context/run-flow";
const STAGE_RE = /^- 현재 단계:\s*(.*?)\s*$/m;
const URL_RE = /^[a-z][a-z0-9+.-]*:\/\//i;

// 도구 입력에서 쓰는 대상을 꺼낸다. 대상을 못 찾으면 빈 배열이다.
function targets(toolName: string, input: Record<string, unknown>): { paths: string[]; tree: boolean } | undefined {
	const str = (v: unknown) => (typeof v === "string" && v.trim() !== "" ? v.trim() : undefined);
	const unwrap = (p: string) => /^\[(.+)#[^\]#]*\]$/.exec(p)?.[1] ?? p;
	if (toolName === "write") {
		const p = str(input.path);
		return { paths: p ? [unwrap(p)] : [], tree: false };
	}
	if (toolName === "ast_edit") {
		const list = Array.isArray(input.paths) ? input.paths.map(str).filter((p): p is string => !!p) : [];
		return { paths: list, tree: true };
	}
	if (toolName !== "edit" && toolName !== "apply_patch") return undefined;
	const paths: string[] = [];
	const p = str(input.path);
	if (p) paths.push(unwrap(p));
	for (const e of Array.isArray(input.edits) ? input.edits : []) {
		const r = str((e as Record<string, unknown>)?.rename);
		if (r) paths.push(r);
	}
	const text = str(input.input);
	if (text) {
		let fence = false;
		const magic: string[] = [];
		for (const line of text.split("\n")) {
			const hash = /^\s*\[([^\]#]+)#[^\]]*\]\s*$/.exec(line); // hashline [PATH#TAG]
			const move = /^\s*MV\s+(.+?)\s*$/.exec(line); // hashline `MV DEST`
			const patch = /^\*\*\* (?:Add|Update|Delete|Edit) File: (.+?)(?: all)?\s*$/.exec(line) ?? /^\*\*\* Move to: (.+?)\s*$/.exec(line);
			if (/^\s*(```|~~~)/.test(line)) fence = !fence;
			if (hash) paths.push(hash[1]!.trim());
			else if (move) paths.push(move[1]!.replace(/^(["'])(.*)\1$/, "$2"));
			else if (patch) paths.push(patch[1]!.trim());
			else if (!fence && /^# \S/.test(line)) magic.push(line.slice(2).trim()); // magic 모드 `# path`
		}
		if (paths.length === 0) paths.push(...magic);
	}
	return { paths, tree: false };
}

// protected_paths.py의 is_active와 같다. 상태 파일의 `- 현재 단계:`가 완료가 될 때까지 켜져 있고,
// 상태 파일이나 state 줄이 없으면 켜진 것으로 본다.
function isActive(root: string, list: string): boolean {
	const state = /^state\t(.+)$/m.exec(readFileSync(list, "utf8"))?.[1];
	if (state === undefined || !existsSync(join(root, state))) return true;
	return STAGE_RE.exec(readFileSync(join(root, state), "utf8"))?.[1] !== "완료";
}

// 대상이 들어가는 저장소에 켜진 보호 목록이 있는지. 없으면 python3 없이 지나간다.
function hasActiveList(target: string): boolean {
	let at = target;
	while (!existsSync(at) && dirname(at) !== at) at = dirname(at);
	let dir: string;
	try {
		// 있는 파일(링크 포함)은 실제로 가리키는 곳의 폴더에서, 새 파일은 가장 가까운 있는 폴더에서 시작한다.
		const real = realpathSync(at);
		dir = statSync(real).isDirectory() ? real : dirname(real);
	} catch {
		return false;
	}
	for (;;) {
		const flow = join(dir, FLOW_DIR);
		if (existsSync(flow) && readdirSync(flow).some(n => n.endsWith(".protected") && isActive(dir, join(flow, n)))) return true;
		if (existsSync(join(dir, ".git")) || dirname(dir) === dir) return false;
		dir = dirname(dir);
	}
}

function globBase(p: string): string {
	const parts = p.split(/[\\/]/);
	const cut = parts.findIndex(s => /[*?[{]/.test(s));
	return cut < 0 ? p : parts.slice(0, cut).join("/") || ".";
}

export function check(toolName: string, input: Record<string, unknown>, cwd: string): string | undefined {
	const t = targets(toolName, input);
	if (!t) return undefined;
	const local = t.paths.filter(p => !URL_RE.test(p));
	const probe = local.length ? local.map(p => resolve(cwd, t.tree ? globBase(p) : p)) : [cwd];
	if (!probe.some(hasActiveList)) return undefined;
	if (local.length === 0) {
		return t.paths.length ? undefined : "run-flow 보호 경로를 확인하지 못해 막았다: 쓰는 대상 경로를 읽지 못했다";
	}
	if (!CORE) {
		return "run-flow 보호 경로를 확인하지 못해 막았다: 저장소의 skills/*/run-flow/scripts/protected_paths.py를 찾지 못했다. extension은 복사하지 않고 링크로 설치한다";
	}
	const r = spawnSync("python3", [CORE, "guard", "--cwd", cwd, ...(t.tree ? ["--tree"] : []), "--", ...local], {
		encoding: "utf8",
		timeout: 20_000,
	});
	if (r.status === 0) return undefined;
	if (r.status === 3) return r.stdout.trim();
	return `run-flow 보호 경로를 확인하지 못해 막았다: ${(r.stderr || String(r.error ?? `종료 코드 ${r.status}`)).trim()}`;
}

export default function gongbangProtectedPaths(pi: ExtensionAPI) {
	// 핸들러가 던지거나 시간을 넘기면 omp가 그 호출을 막는다(fail-closed).
	pi.on("tool_call", async (event, ctx) => {
		const reason = check(event.toolName, (event.input ?? {}) as Record<string, unknown>, ctx.cwd);
		return reason === undefined ? undefined : { block: true, reason };
	});
}
