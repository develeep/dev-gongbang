import { expect, test } from 'claude-code/testing'

const props = (placement: 'dock' | 'inline') => ({
  title: 'Pokémon',
  isFocused: false,
  bodyColumns: 50,
  placement,
  scroll: { offset: 0, bodyRows: 30 },
  view: {},
})

test('the session goes on top of the pokemon pane, the mon stays under it', async ($, on) => {
  // Stands for the pokemon mod beneath: its own pane tree.
  on('ui.render', ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text>charmander-scene</Text>
  })

  for (const placement of ['dock', 'inline'] as const) {
    const ui = await $.ui.mount({
      plugin: 'pokemon',
      surface: 'terminal',
      component: 'Pane',
      requestId: 'pokemon',
      props: props(placement),
    })
    expect((await ui.find({ type: 'Text', text: /Goal/ }))?.text).toContain('Goal')
    expect((await ui.find({ type: 'Text', text: /charmander-scene/ }))?.text).toBe('charmander-scene')
    await ui.unmount()
  }
})

test('the Session pane still draws on its own', async $ => {
  const ui = await $.ui.mount({
    plugin: 'gongbang-mods',
    surface: 'terminal',
    component: 'Pane',
    requestId: 'side',
    props: { ...props('dock'), title: 'Session' },
  })
  expect((await ui.find({ type: 'Text', text: /Goal/ }))?.text).toContain('Goal')
  expect(await ui.find({ type: 'Text', text: /charmander/ })).toBeFalsy()
  await ui.unmount()
})
