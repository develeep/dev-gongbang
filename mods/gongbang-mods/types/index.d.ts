// Session pane, context half (hooks/session/context.tsx).
export type Slice = { name: string; tokens: number; color: string; kind: 'used' | 'free' | 'buffer' }

export type Reading = {
  slices: Slice[]
  total: number // tokens in use
  window: number // the window measured against
  percent: number
  compactsAt?: number // where auto-compaction runs, when it is on
}

// Session pane, recap half (hooks/session/recap.tsx).
export type Recap = { goal: string; now: string; waiting: string; next: string }

declare module 'claude-code' {
  interface PluginState {
    'gongbang-mods': { reading: Reading | null; isHidden: boolean; recap: Recap | null; live: string; turn: string }
    // Owned by next-steps (hamzafer/claude-code-mods), read so the pane leaves out its own next while that list shows.
    'next-steps': { steps: { turnId: string; items: string[] } | null; active: boolean }
  }
}
