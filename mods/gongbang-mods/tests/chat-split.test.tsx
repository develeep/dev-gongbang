import { expect, test } from 'claude-code/testing'

const TEXT = ['# Title', 'Some **bold** text.', '', '> quoted line', '', '---', '', '```ts', 'const a = 1', '```', '', '| a | b |', '| - | - |', '| 1 | 2 |'].join('\n')

test('a reply draws headings, quotes, rules and code by hand, the rest as markdown', async $ => {
  const ui = await $.ui.mount({
    plugin: 'gongbang-mods',
    surface: 'terminal',
    component: 'AssistantMessage',
    requestId: 'm1',
    props: { text: TEXT, isFirstOfReply: true },
  })
  expect((await ui.find({ type: 'Text', text: /^Title$/ }))?.text).toBe('Title')
  expect((await ui.find({ type: 'Text', text: /quoted line/ }))?.text).toBe('quoted line')
  expect((await ui.find({ type: 'Text', text: /^─+$/ }))).toBeTruthy()
  expect((await ui.find({ type: 'Code' }))).toBeTruthy()
  expect((await ui.find({ type: 'Markdown', text: /\| a \| b \|/ }))).toBeTruthy()
  await ui.unmount()
})
