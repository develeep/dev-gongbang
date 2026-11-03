import type { On } from 'claude-code'

// Draws the person's prompts and Claude's replies as titled cards, with headings, code, quotes and rules styled.
export function chatSplit(on: On) {
  // The person's own prompts become a card; task notifications and agent messages stay as the engine draws them.
  on('ui.render', { component: 'UserMessage' }, async ($, e, next) => {
    if (e.props.origin.kind !== 'composer') return next(e)

    const { Box, Text } = $.ui.resolve(e)
    return (
      <Box flexDirection="column" borderStyle="round" borderColor="suggestion" paddingX={1} marginTop={1}>
        <Text bold color="suggestion">● You</Text>
        {await next(e)}
      </Box>
    )
  })

  // Each reply block is its own card; only the first carries the title.
  // ponytail: a tool call between blocks splits the reply into several cards; merging them needs the whole turn's rows.
  on('ui.render', { component: 'AssistantMessage' }, async ($, e, next) => {
    const { Box, Text, Code, Markdown } = $.ui.resolve(e)
    const isFirst = e.props.isFirstOfReply
    const ruleWidth = Math.max(10, (e.viewport?.columns ?? 80) - 6)

    const body = splitBlocks(e.props.text).map((b, i) => {
      const gap = i === 0 ? 0 : 1
      switch (b.kind) {
        case 'heading': {
          const [mark, color] = b.level === 1 ? ['█ ', 'claude'] : b.level === 2 ? ['▌ ', 'claude'] : ['▸ ', 'suggestion']
          return (
            <Box marginTop={gap}>
              <Text bold color={color}>{mark}</Text>
              <Text bold underline={b.level === 1}>{b.text}</Text>
            </Box>
          )
        }
        case 'code':
          return (
            <Box flexDirection="column" borderStyle="round" borderColor="subtle" paddingX={1} marginTop={gap}>
              {b.language && <Text dimColor>{b.language}</Text>}
              <Code source={b.source} language={b.language || undefined} />
            </Box>
          )
        case 'quote':
          return (
            <Box flexDirection="column" marginTop={gap}>
              {b.lines.map(line => (
                <Box>
                  <Text color="suggestion">┃ </Text>
                  <Text italic dimColor>{line}</Text>
                </Box>
              ))}
            </Box>
          )
        case 'rule':
          return <Box marginTop={gap}><Text dimColor>{'─'.repeat(ruleWidth)}</Text></Box>
        default:
          return <Box marginTop={gap}><Markdown text={b.text} /></Box>
      }
    })

    return (
      <Box flexDirection="column" borderStyle="round" borderColor="claude" paddingX={1} marginTop={isFirst ? 1 : 0}>
        {isFirst && <Box marginBottom={1}><Text bold color="claude">◆ Claude</Text></Box>}
        {body.length ? body : await next(e)}
      </Box>
    )
  })
}

type Block =
  | { kind: 'heading'; level: number; text: string }
  | { kind: 'code'; language: string; source: string }
  | { kind: 'quote'; lines: string[] }
  | { kind: 'rule' }
  | { kind: 'text'; text: string }

// Pulls out the parts drawn by hand (headings, fences, quotes, rules); everything else,
// tables and lists included, stays one Markdown chunk so the engine draws it as before.
// ponytail: line-based, no nesting (a quote holding a fence stays a quote); a real parser if that shows up.
export function splitBlocks(text: string): Block[] {
  const blocks: Block[] = []
  let prose: string[] = []
  const flush = () => {
    const t = prose.join('\n').trim()
    if (t) blocks.push({ kind: 'text', text: t })
    prose = []
  }
  const lines = text.split('\n')
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i] ?? ''
    const fence = line.match(/^\s*(```+|~~~+)\s*([\w+-]*)/)
    if (fence) {
      flush()
      const close = fence[1] ?? '```'
      const src: string[] = []
      for (i++; i < lines.length && !(lines[i] ?? '').trim().startsWith(close); i++) src.push(lines[i] ?? '')
      blocks.push({ kind: 'code', language: fence[2] ?? '', source: src.join('\n') })
      continue
    }
    const heading = line.match(/^(#{1,6})\s+(.*?)\s*#*\s*$/)
    if (heading) {
      flush()
      blocks.push({ kind: 'heading', level: heading[1]!.length, text: heading[2]!.replace(/\*\*|__|`/g, '') })
      continue
    }
    // A --- right under a text line is a setext heading in markdown, so only a rule after a blank line counts.
    if (/^\s*([-*_])(\s*\1){2,}\s*$/.test(line) && !/\S/.test(prose[prose.length - 1] ?? '')) {
      flush()
      blocks.push({ kind: 'rule' })
      continue
    }
    if (/^\s*>/.test(line)) {
      flush()
      const quote: string[] = []
      for (; i < lines.length && /^\s*>/.test(lines[i] ?? ''); i++) quote.push((lines[i] ?? '').replace(/^\s*>\s?/, ''))
      i--
      blocks.push({ kind: 'quote', lines: quote })
      continue
    }
    prose.push(line)
  }
  flush()
  return blocks
}
