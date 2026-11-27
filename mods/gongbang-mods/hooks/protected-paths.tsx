import type { EngineInterface, On } from 'claude-code'

// Blocks the file tools from writing a run-flow protected path (tests at the
// flow's start HEAD, judge cases, accepted tests, the list itself). The rules
// live in hooks/protected_paths.py, a copy of run-flow's
// scripts/protected_paths.py. Bash and other shell writes are not stopped here;
// run-flow's acceptance check (`protected_paths.py verify`) catches them.

// The file tools of Claude Code 2.1.332 (MultiEdit is not one of them) and the key naming their target.
const TOOLS = ['Write', 'Edit', 'NotebookEdit'] as const
const TARGET: Record<string, string> = { Write: 'file_path', Edit: 'file_path', NotebookEdit: 'notebook_path' }
const FLOW_DIR = 'docs/context/run-flow'
const STAGE_RE = /^- 현재 단계:\s*(.*?)\s*$/m

const isAbsolute = (p: string) => p.startsWith('/') || /^[A-Za-z]:[\\/]/.test(p)
const parentOf = (p: string) => {
  const cut = Math.max(p.lastIndexOf('/'), p.lastIndexOf('\\'))
  return cut <= 0 ? p.slice(0, cut + 1) || '/' : p.slice(0, cut)
}
const join = (dir: string, name: string) => (dir.endsWith('/') || dir.endsWith('\\') ? dir + name : `${dir}/${name}`)

// Mirrors is_active in protected_paths.py: a list is on until its state file's
// `- 현재 단계:` reads 완료; a missing state file or state line counts as on.
async function isActive($: EngineInterface, root: string, list: string): Promise<boolean> {
  const state = /^state\t(.+)$/m.exec(await $.fs.read(list))?.[1]
  if (state === undefined || !(await $.fs.exists(join(root, state)))) return true
  return STAGE_RE.exec(await $.fs.read(join(root, state)))?.[1] !== '완료'
}

// Whether the repository the target lands in has an active protected list. Only
// then does the core run, so a session outside a running flow never needs python3.
async function hasActiveList($: EngineInterface, target: string): Promise<boolean> {
  let at = target
  let real: string | undefined
  for (;;) {
    real = (await $.fs.exists(at)) ? (await $.fs.stat(at, { resolve: true })).realPath : undefined
    if (real !== undefined || parentOf(at) === at) break
    at = parentOf(at)
  }
  if (real === undefined) return false
  // An existing target (a link too) starts from the folder it lands in; a new
  // one from its nearest existing folder.
  let dir = at === target ? parentOf(real) : real
  for (;;) {
    const flow = join(dir, FLOW_DIR)
    if (await $.fs.exists(flow)) {
      for (const f of await $.fs.list(flow)) {
        if (f.name.endsWith('.protected') && (await isActive($, dir, join(flow, f.name)))) return true
      }
    }
    if (await $.fs.exists(join(dir, '.git'))) return false
    if (parentOf(dir) === dir) return false
    dir = parentOf(dir)
  }
}

// undefined lets the call run; a string is why it is refused.
async function verdict($: EngineInterface, tool: string, input: Record<string, unknown>): Promise<string | undefined> {
  const cwd = await $.session.cwd()
  const raw = input[TARGET[tool] ?? 'file_path']
  const path = typeof raw === 'string' && raw !== '' ? raw : undefined
  const target = path === undefined ? cwd : isAbsolute(path) ? path : join(cwd, path)
  if (!(await hasActiveList($, target))) return undefined
  if (path === undefined) return 'run-flow 보호 경로를 확인하지 못해 막았다: 대상 경로가 없다'
  const core = `${$.plugin.root}/hooks/protected_paths.py`
  const r = await $.process.run(['python3', core, 'guard', '--cwd', cwd, '--', path])
  if (r.exitCode === 0) return undefined
  if (r.exitCode === 3) return r.stdout.trim()
  return `run-flow 보호 경로를 확인하지 못해 막았다: ${r.stderr.trim() || `종료 코드 ${r.exitCode}`}`
}

export function protectedPaths(on: On) {
  // A matcher keeps this beside the plugin's matcherless tool.call hook (session/recap.tsx).
  on('tool.call', { tool: TOOLS }, async ($, e, next) => {
    // Every failure denies here. A hook that throws let the tool run even with
    // a .catch that answered (claude plugin test, Claude Code 2.1.332).
    const reason = await verdict($, e.tool, e as unknown as Record<string, unknown>).catch(
      (err: unknown) =>
        `run-flow 보호 경로를 확인하지 못해 막았다: ${err instanceof Error ? err.message : String(err)}. python3가 필요하다`,
    )
    return reason === undefined ? next(e) : { deny: reason }
  }).catch(($, e, next) => (next.called ? next(e) : { deny: 'run-flow 보호 경로를 확인하지 못해 막았다' }))
}
