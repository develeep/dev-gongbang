import type { On } from 'claude-code'

// The input field worth showing for each tool; anything else falls back to the first string field.
const KEYS = ['command', 'file_path', 'pattern', 'path', 'url', 'query', 'description', 'prompt']

function summarize(input: unknown): string {
  if (!input || typeof input !== 'object') return ''
  const rec = input as Record<string, unknown>
  const key = KEYS.find(k => typeof rec[k] === 'string') ?? Object.keys(rec).find(k => typeof rec[k] === 'string')
  return key ? (String(rec[key]).split('\n')[0] ?? '') : ''
}

// Folds each tool call and its result into one line; ctrl+o still shows everything.
export function compactTools(on: On) {
  on('ui.render', { component: 'ToolUse' }, ($, e, next) => {
    // ctrl+o and --verbose still show everything.
    if (e.props.isExpanded) return next(e)

    const { Box, Text } = $.ui.resolve(e)
    const { tool, input, isRunning, isErrored, isInterrupted } = e.props
    const [mark, color] = isRunning
      ? ['…', 'yellow']
      : isInterrupted
        ? ['⏹', 'yellow']
        : isErrored
          ? ['✗', 'red']
          : ['✓', 'green']

    return (
      <Box>
        <Text color={color}>{mark} </Text>
        <Text bold>{tool}</Text>
        <Text dimColor wrap="truncate-end"> {summarize(input)}</Text>
      </Box>
    )
  })

  // The result block goes away in the compact view; the row's mark says how it ended.
  on('ui.render', { component: 'ToolResult' }, ($, e, next) => {
    if (e.props.isExpanded) return next(e)
    const { Box } = $.ui.resolve(e)
    return <Box />
  })
}
