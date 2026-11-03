import type { Register } from 'claude-code'

import { chatSplit } from './chat-split'
import { compactTools } from './compact-tools'
import { sessionContext } from './session/context'
import { sessionRecap } from './session/recap'

export const register: Register = on => {
  compactTools(on)
  chatSplit(on)
  sessionRecap(on)
  sessionContext(on)
}
