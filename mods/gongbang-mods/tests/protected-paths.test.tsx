import type { On } from 'claude-code'
import { expect, test } from 'claude-code/testing'

// A small file system: directories, files, file texts, and links (path -> where it lands).
type World = {
  dirs: string[]
  files: string[]
  texts?: Record<string, string>
  links?: Record<string, string>
  lists?: Record<string, string[]>
}

const STATE = '/repo/docs/context/run-flow/2026-11-26-demo.md'
const LIST = '/repo/docs/context/run-flow/2026-11-26-demo.protected'
const REPO: World = {
  dirs: ['/', '/repo', '/repo/.git', '/repo/src', '/repo/tests', '/repo/docs', '/repo/docs/context', '/repo/docs/context/run-flow', '/alias'],
  files: ['/repo/src/app.py', '/repo/tests/test_app.py', STATE, LIST],
  texts: {
    [STATE]: '# demo\n\n- 현재 단계: 5. 구현과 리뷰\n',
    [LIST]: 'state\tdocs/context/run-flow/2026-11-26-demo.md\nfile\ttests/test_app.py\tabc\n',
  },
  lists: { '/repo/docs/context/run-flow': ['2026-11-26-demo.md', '2026-11-26-demo.protected'] },
}
const PLAIN: World = {
  dirs: ['/', '/plain', '/plain/.git', '/plain/tests'],
  files: ['/plain/tests/test_app.py'],
  lists: {},
}

function mount(on: On, world: World, guard: (argv: readonly string[]) => { exitCode: number; stdout?: string; stderr?: string } | Error) {
  const calls: (readonly string[])[] = []
  const ran: string[] = []
  const real = (p: string) => {
    for (const [from, to] of Object.entries(world.links ?? {})) {
      if (p === from || p.startsWith(from + '/')) return to + p.slice(from.length)
    }
    return p
  }
  const has = (p: string) => world.dirs.includes(real(p)) || world.files.includes(real(p))
  on('session.cwd', () => ({ value: '/repo' }))
  on('fs.exists', ($: unknown, e: { path: string }) => ({ value: has(e.path) }))
  on('fs.stat', ($: unknown, e: { path: string; resolve: boolean }) => {
    if (!has(e.path)) throw new Error(`ENOENT: ${e.path}`)
    const kind = world.dirs.includes(real(e.path)) ? 'dir' : 'file'
    return { value: { kind, size: 0, mtimeMs: 0, isLink: real(e.path) !== e.path, ...(e.resolve ? { realPath: real(e.path) } : {}) } }
  })
  on('fs.list', ($: unknown, e: { path: string }) => ({
    value: (world.lists?.[real(e.path)] ?? []).map(name => ({ name, kind: 'file', size: 0, mtimeMs: 0, isLink: false })),
  }))
  on('fs.read', ($: unknown, e: { path: string }) => {
    const text = world.texts?.[real(e.path)]
    if (text === undefined) throw new Error(`ENOENT: ${e.path}`)
    return { value: text }
  })
  on('process.run', ($: unknown, e: { argv: readonly string[] }) => {
    calls.push(e.argv)
    const r = guard(e.argv)
    // A command that cannot start: $.process.run rejects.
    if (r instanceof Error) return { deny: r.message }
    return { value: { exitCode: r.exitCode, stdout: r.stdout ?? '', stderr: r.stderr ?? '', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  on('tool.call', ($: unknown, e: { tool: string }) => {
    ran.push(e.tool)
    return { result: 'ran' }
  })
  return { calls, ran }
}

const BLOCK = { exitCode: 3, stdout: 'run-flow 보호 경로라 쓸 수 없다: tests/test_app.py' }

test('an Edit of a protected test in an active flow is denied before the tool runs', async ($, on) => {
  const w = mount(on, REPO, () => BLOCK)
  const r = await $.tool.call({ tool: 'Edit', file_path: '/repo/tests/test_app.py', old_string: 'a', new_string: 'b' })
  expect(r.deny ?? r.text ?? '').toContain('보호 경로')
  expect(w.ran).toEqual([])
  expect(w.calls.length).toBe(1)
  const argv = w.calls[0]!
  expect(argv[0]).toBe('python3')
  expect(argv[1]).toMatch(/hooks\/protected_paths\.py$/)
  expect(argv.slice(2)).toEqual(['guard', '--cwd', '/repo', '--', '/repo/tests/test_app.py'])
})

test('Write, NotebookEdit and a subagent call are checked the same way', async ($, on) => {
  const w = mount(on, REPO, () => BLOCK)
  await $.tool.call({ tool: 'Write', file_path: 'tests/test_app.py', content: 'x' })
  await $.tool.call({ tool: 'NotebookEdit', notebook_path: '/repo/tests/n.ipynb', new_source: 'x' })
  await $.tool.call({ tool: 'Edit', file_path: '/repo/tests/test_app.py', old_string: 'a', new_string: 'b', agentId: 'sub1' })
  expect(w.ran).toEqual([])
  expect(w.calls.map(a => a[a.length - 1])).toEqual(['tests/test_app.py', '/repo/tests/n.ipynb', '/repo/tests/test_app.py'])
})

test('a write the core allows runs, and Bash or Read is never checked', async ($, on) => {
  const w = mount(on, REPO, () => ({ exitCode: 0 }))
  await $.tool.call({ tool: 'Write', file_path: '/repo/src/new.py', content: 'x' })
  await $.tool.call({ tool: 'Bash', command: "sed -i s/a/b/ tests/test_app.py" })
  await $.tool.call({ tool: 'Read', file_path: '/repo/tests/test_app.py' })
  expect(w.ran).toEqual(['Write', 'Bash', 'Read'])
  expect(w.calls.length).toBe(1)
})

test('a repository without a protected list never starts the core', async ($, on) => {
  const w = mount(on, PLAIN, () => new Error('must not run'))
  await $.tool.call({ tool: 'Edit', file_path: '/plain/tests/test_app.py', old_string: 'a', new_string: 'b' })
  await $.tool.call({ tool: 'Write', file_path: '/plain/new/dir/file.py', content: 'x' })
  expect(w.ran).toEqual(['Edit', 'Write'])
  expect(w.calls.length).toBe(0)
})

test('a finished flow never starts the core, so python3 is not needed', async ($, on) => {
  const done: World = { ...REPO, texts: { ...REPO.texts, [STATE]: '# demo\n\n- 현재 단계: 완료\n' } }
  const w = mount(on, done, () => new Error('must not run'))
  await $.tool.call({ tool: 'Edit', file_path: '/repo/tests/test_app.py', old_string: 'a', new_string: 'b' })
  expect(w.ran).toEqual(['Edit'])
  expect(w.calls.length).toBe(0)
})

test('a link spelling is followed to the repository that holds the list', async ($, on) => {
  const w = mount(on, { ...REPO, links: { '/alias': '/repo' } }, () => BLOCK)
  await $.tool.call({ tool: 'Edit', file_path: '/alias/tests/test_app.py', old_string: 'a', new_string: 'b' })
  expect(w.ran).toEqual([])
  expect(w.calls.length).toBe(1)
})

test('a core error fails closed', async ($, on) => {
  const w = mount(on, REPO, () => ({ exitCode: 2, stderr: '오류: 목록 3행을 읽지 못했다' }))
  const r = await $.tool.call({ tool: 'Write', file_path: '/repo/src/app.py', content: 'x' })
  expect(w.ran).toEqual([])
  expect(r.deny ?? r.text ?? '').toContain('목록 3행')
})

test('a core that cannot start fails closed', async ($, on) => {
  const w = mount(on, REPO, () => new Error('spawn python3 ENOENT'))
  const r = await $.tool.call({ tool: 'Write', file_path: '/repo/src/app.py', content: 'x' })
  expect(w.ran).toEqual([])
  expect(r.deny ?? r.text ?? '').toContain('보호 경로')
})
