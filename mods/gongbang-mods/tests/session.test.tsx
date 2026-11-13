import { expect, test } from 'claude-code/testing'

test('the Session pane draws the goal', async $ => {
  const ui = await $.ui.mount({
    plugin: 'gongbang-mods',
    surface: 'terminal',
    component: 'Pane',
    requestId: 'side',
    props: {
      title: 'Session',
      isFocused: false,
      bodyColumns: 50,
      placement: 'dock',
      scroll: { offset: 0, bodyRows: 30 },
      view: {},
    },
  })
  expect((await ui.find({ type: 'Text', text: /Goal/ }))?.text).toContain('Goal')
  await ui.unmount()
})
