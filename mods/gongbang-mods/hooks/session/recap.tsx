// Session pane, recap half: keeps a live recap (goal, now, waiting on you, next) that context.tsx draws,
// plus /where. Adapted from where-am-i in hamzafer/claude-code-mods (MIT, see LICENSE here): the band
// above the prompt was removed. One Haiku call after each turn writes the recap.
import { atom, read, update } from 'claude-code'
import type { EngineInterface, On } from 'claude-code'

import type { Recap } from '../../types'
import { refresh } from './context'

const MODEL = 'haiku'
const MAX_LOG = 20

// Held by the host, so the recap survives a hot reload of this file.
const recap = atom({ plugin: 'gongbang-mods', key: 'recap' } as const, null as Recap | null)
const live = atom({ plugin: 'gongbang-mods', key: 'live' } as const, '')
// The turn a summary may still land for. Held by the host too, so a summary from before a hot reload sees a newer turn.
const latest = atom({ plugin: 'gongbang-mods', key: 'turn' } as const, '')

export function sessionRecap(on: On) {
  let prompt = ''
  let log: string[] = []
  let slash = false // the last message was a slash command, which may or may not start a turn

  // session.start (the /where command) lives in context.tsx: one module takes each unmatched event once.

  on('prompt.submit', async ($, e, next) => {
    // A slash command like /where answers nothing the last turn waited on, and may start no turn:
    // leave the band as it is. One that does start a turn is picked up by turn.start.
    if (e.text.startsWith('/')) {
      slash = true
      return next(e)
    }
    slash = false
    prompt = e.text.slice(0, 1500)
    log = []
    await update($, live, () => 'reading your message')
    await clearWaiting($)
    return next(e)
  }).catch(($, e, next) => next(e)) // a failure here must never block the person's work

  // A new turn of Claude's own: a summary of an older one is stale, and the person has answered.
  on('turn.start', async ($, e, next) => {
    if (!e.agentId) {
      // A turn a slash command started: its text is the prompt. Other turns keep the person's
      // own message, including ones Claude Code starts itself, like a background agent finishing.
      if (slash && e.text) {
        prompt = e.text.slice(0, 1500)
        log = []
      }
      slash = false
      await update($, latest, () => e.turnId ?? '')
      await clearWaiting($)
    }
    return next(e)
  })

  // Observe only: note what is happening, then let the call run untouched.
  // Only Claude's own calls count: one another mod makes in the background (`$.tool.call`,
  // `$.mcp.call`) is raised by that plugin, and `next.origin` names it instead of the engine.
  on('tool.call', async ($, e, next) => {
    if (next.origin.plugin !== 'engine') return next(e)
    const line = describe(e as unknown as Record<string, unknown>)
    log = [...log, e.agentId ? `(agent) ${line}` : line].slice(-MAX_LOG)
    if (!e.agentId) await update($, live, () => line)
    const r = await next(e)
    return r
  }).catch(($, e, next) => next(e)) // a failure here must never block the person's work

  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    if (!e.agentId) {
      await update($, live, () => '')
      const mine = e.turnId ?? ''
      await update($, latest, () => mine) // also for a turn that raised no turn.start, and after a hot reload
      const isCurrent = async () => (await read($, latest)) === mine
      void summarize($, prompt, log, e.answer, isCurrent).catch(() => {}) // in the background, so the turn ends at once
      await refresh($).catch(() => {}) // the context half; a subagent's turn fills its own window, not this one
    }
    return r
  })

  on('command.run', { command: 'where' }, async $ => ({ text: await longRecap($, prompt, log) }))

}

// A short label for one tool call: what a person would say Claude is doing. A Bash call names
// its program, not the command line: the label is drawn and sent to Haiku.
export function describe(e: Record<string, unknown>): string {
  return clean(labelOf(e)).replace(/\s+/g, ' ')
}

function labelOf(e: Record<string, unknown>): string {
  const tool = String(e.tool)
  const s = (k: string) => (typeof e[k] === 'string' ? (e[k] as string) : '')
  const file = (p: string) => p.split('/').slice(-2).join('/')
  if (tool === 'Bash') return `running ${s('description') || program(s('command'))}`
  if (tool === 'Edit' || tool === 'Write') return `editing ${file(s('file_path'))}`
  if (tool === 'Read') return `reading ${file(s('file_path'))}`
  if (tool === 'Grep' || tool === 'Glob') return `searching for ${s('pattern').slice(0, 40)}`
  if (tool === 'Agent') return `starting an agent: ${s('description')}`
  if (tool === 'AskUserQuestion') return 'asking you a question'
  if (tool.startsWith('mcp__')) return `using ${tool.split('__').slice(1).join(' ')}`
  return `using ${tool}`
}

async function summarize($: EngineInterface, prompt: string, log: string[], answer: string, isCurrent: () => Promise<boolean>) {
  const before = await read($, recap)
  const r = await $.model.complete({
    model: MODEL,
    maxTokens: 300,
    system:
      'You keep a one-glance recap of a coding session for someone with ADHD. Plain words, no em dashes, ' +
      'each field at most 70 characters. Reply with JSON only: {"goal","now","waiting","next"}. ' +
      '"goal": the overall aim of the session (keep the previous goal unless it clearly changed). ' +
      '"now": what was just done. "waiting": what the assistant is waiting on from the person, or "". ' +
      '"next": the next step.',
    prompt: [
      `Previous recap: ${before ? JSON.stringify(before) : 'none'}`,
      `The person's latest message: ${prompt}`,
      `Tools used this turn: ${log.join('; ') || 'none'}`,
      `The assistant's reply: ${answer.slice(0, 2500)}`,
    ].join('\n\n'),
  })
  if (!r.isAnswered || !(await isCurrent())) return // a newer turn started while Haiku was writing: this recap is stale
  const parsed = parseRecap(r.text)
  if (parsed) await update($, recap, () => parsed)
}

// The person just answered: whatever the last turn waited on is no longer theirs to do.
async function clearWaiting($: EngineInterface) {
  await update($, recap, r => (r && r.waiting !== '' ? { ...r, waiting: '' } : r))
}

async function longRecap($: EngineInterface, prompt: string, log: string[]) {
  const messages = (await $.session.messages()).slice(-12)
  const r = await $.model.complete({
    model: MODEL,
    maxTokens: 500,
    system:
      'Write a recap of this coding session for someone who lost track. Plain words, no em dashes. ' +
      'At most 6 short bullets: the goal, what is done, what is happening now, what is waiting on them, the next step.',
    prompt: [
      `<transcript>\n${messages.filter(m => m.text.trim() !== '').map(m => `[${m.role === 'user' ? 'person' : 'assistant'}] ${m.text.slice(0, 800)}`).join('\n')}\n</transcript>`,
      `Latest message: ${prompt}`,
      `Recent tool calls: ${log.join('; ') || 'none'}`,
      'Write the recap of the transcript above now: the bullets only, not a reply to it.',
    ].join('\n\n'),
  })
  return r.isAnswered ? r.text : 'Could not build a recap right now.'
}

// The tools whose second word is a subcommand worth naming: `git push`, `npm test`.
const SUBCOMMANDS = new Set(['git', 'gh', 'npm', 'pnpm', 'yarn', 'bun', 'docker', 'cargo', 'go', 'kubectl', 'make'])

// A command's program, never its arguments (a token often sits there): `curl -H "…" url` is `curl`,
// `cd /x && npm test` is `npm test`. A start that is no plain name (`FOO=1`, a quote, a subshell) says so.
export function program(command: string): string {
  const words = command.replace(/^\s*cd\s+\S+\s*(?:&&|;)\s*/, '').trim().split(/\s+/)
  const name = words[0]!.slice(words[0]!.lastIndexOf('/') + 1)
  if (!/^[\w.+-]{1,30}$/.test(name)) return 'a shell command'
  return SUBCOMMANDS.has(name) && /^[a-z][a-z-]{0,19}$/.test(words[1] ?? '') ? `${name} ${words[1]}` : name
}

// The engine refuses a band with a control character in it, and every mod's band goes with it: drop
// escape sequences, control characters and bidi overrides. The same as agent-radar's `clean`.
const ESCAPES = /\x1b(?:\[[0-?]*[ -/]*[@-~]|[\]PX^_][\s\S]*?(?:\x07|\x1b\\|$)|[@-Z\\-_])|\x9b[0-?]*[ -/]*[@-~]|[\x90\x98\x9d\x9e\x9f][\s\S]*?(?:\x07|\x9c|$)|[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f‪-‮⁦-⁩]/g
export function clean(text: string) {
  return text.replace(ESCAPES, '')
}

// At most 70 characters, cut at a word: the model does not always keep to the limit.
export function clip(raw: string, max = 70) {
  const text = clean(raw).replace(/\s+/g, ' ')
  const first = text.split(/(?<=[.!?])\s/)[0] ?? text // one sentence
  if (first.length <= max) return first.replace(/\.$/, '')
  return `${first.slice(0, first.lastIndexOf(' ', max - 1))}…`
}

// The model's JSON, tolerating a code fence around it.
export function parseRecap(text: string): Recap | null {
  const body = text.slice(text.indexOf('{'), text.lastIndexOf('}') + 1)
  try {
    const o = JSON.parse(body) as Record<string, unknown>
    const field = (k: string) => (typeof o[k] === 'string' ? clip((o[k] as string).replace(/\s*—\s*/g, ', ').trim()) : '')
    if (!field('goal')) return null
    return { goal: field('goal'), now: field('now'), waiting: field('waiting'), next: field('next') }
  } catch {
    return null
  }
}
