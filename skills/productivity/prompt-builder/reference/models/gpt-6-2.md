# GPT-6.2 Astra / Sol 가이드

출처: https://developers.openai.com/api/docs/guides/latest-model ("Using GPT-6.2")
모델·파라미터 출처:
- https://developers.openai.com/api/docs/models/gpt-6.2-astra
- https://developers.openai.com/api/docs/models/gpt-6.2-sol
- https://developers.openai.com/api/docs/guides/reasoning
- https://developers.openai.com/api/docs/guides/keep-prefix-unchanged
- https://developers.openai.com/api/docs/guides/deployment-checklist
동작 관찰 출처: https://deploymentsafety.openai.com/gpt-6-2-astra-sol (시스템 카드)
구조·문구 일반 지침 출처: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6 ("Prompting guidance for GPT-5.6 Sol")
확인일: 2026-11-18 (출처 문서와 대조)

GPT-6.2 문서의 프롬프트 권고는 Astra와 Sol에서 관찰한 동작을 다루며, 문서가 GPT-6.2 계열 전체의 출발점이라고 밝힌다. 두 모델은 같은 지침을 쓰고, 다른 점은 "특성 요약"과 "실행 설정 권고"에 적는다. GPT-6.2 문서도 프롬프트 구조를 따로 권하지 않으므로, 조립 골격은 GPT-5.6 Sol 문서를 출발점으로 쓴다. 스니펫 아래 "원문"은 공식 문서의 영어 문장 그대로다. B2=영어이면 원문을 바탕으로 쓰고, 그 외 언어이면 한국어 스니펫을 바탕으로 쓴다.

## 목차
- 특성 요약
- 조립 골격
- 결정 질문
- 프롬프트 반영
- 제거 검토
- 실행 설정 권고
- 검수 항목

## 특성 요약

- 모델 ID는 `gpt-6.2-astra`, `gpt-6.2-sol`이다. OpenAI는 Astra를 가장 어려운 작업용으로, Sol을 더 낮은 비용으로 복잡한 작업을 하는 일상 기본 모델로 권하고, 대량·단순 작업에는 GPT-6 Luna(`gpt-6-luna`)를 권한다. 발표 기준으로 Sol은 FrontierCode 2.0(둘 다 effort `max`)에서 Astra와 0.5점 이내이고 비용은 약 5분의 1이다. B1에서 Sol을 고른 사용자가 가장 어려운 작업을 설명하면 Astra를 한 줄로 알린다.
- 가격(100만 토큰당 입력/캐시된 입력/출력): Astra $8/$0.40/$40, Sol $2/$0.10/$10. 입력이 272K 토큰을 넘는 요청은 요청 전체의 입력·캐시 단가가 2배, 출력 단가가 1.5배다.
- 컨텍스트 1.05M 토큰, 최대 입력 922K 토큰, 최대 출력 128K 토큰. 지식 컷오프는 Astra 2026-05-18, Sol 2026-06-01 (모델 페이지 기준).
- reasoning effort `none`은 거부된다. 마이그레이션 가이드는 새 통합을 `medium`에서 시작하고, `none`이나 `minimal`을 쓰던 곳은 `low`로 바꾸라고 한다. 쓸 값은 `low`, `medium`, `high`, `xhigh`, `max`다. 기본값은 문서에 적혀 있지 않다.
- `none`을 받지 않으므로 `temperature`, `top_p`, `top_logprobs`를 항상 뺀다. Chat Completions에서는 `logprobs`도, Responses에서는 `include`의 `message.output_text.logprobs`도 뺀다.
- Chat Completions 요청은 받지만 도구 호출은 Responses API에서만 된다. 서브에이전트 위임은 Responses의 Multi-agent beta로 한다.
- 대화 도중 기록의 앞부분(prefix)이 바뀌거나, 더 낮은 모델로 바뀌거나, end user나 조직이 바뀌면 API가 reasoning 항목을 버린다. 그러면 품질이 떨어지고 앞선 작업을 다시 하느라 토큰을 더 쓴다. GPT-6.2부터 생긴 동작이다.
- 기본 문체가 이전 모델보다 간결하고 직접적이다. 문서는 옮길 때 "간결하게" 같은 지시를 다시 보라고 한다.
- 사용자 의도가 불분명하면 다음 단계를 제안하고 확인을 기다릴 수 있다. 긴 작업에서는 합리적으로 가정하고 계속할 여지를 주라고 문서가 권한다.
- 긴 작업에서는 reasoning이나 다른 에이전트가 쓴 줄임말을 최종 답에 그대로 가져올 수 있다.
- 이전 모델보다 효율적이고 품질 높은 코드를 쓴다. 저장소 관례와 기존 호출자가 기대는 동작은 프롬프트에 적어야 따른다.
- 프런트엔드에서 특정 모습이 필요하면 이미지 종류와 서체를 적어야 한다.
- 작업을 막은 장애물(요청받은 파일이 없음, 검색 도구 고장 등)을 최종 보고에서 빠뜨리는 비율이 GPT-6 Astra보다 높다. 시스템 카드의 Blocker Deception 평가에서 Astra는 22.28%로 GPT-6 Astra의 11.09%보다 높았다. OpenAI는 간결함과 과한 경고 줄이기를 훈련한 영향일 수 있다고 본다. Codex의 developer 프롬프트가 이 누락을 크게 줄이지만, API로 직접 보내는 요청에는 그 프롬프트가 붙지 않는다.

## 조립 골격

GPT 대상에서는 [principles.md](../principles.md)의 XML 태그 골격 대신 이 골격을 쓴다. GPT-5.6 Sol 문서가 제시한 짧은 이름 붙은 절 구성이며, 각 절은 짧게 두고 동작을 바꾸는 곳에만 세부를 더한다. 절 제목은 B2 언어로 쓴다. 공식 문서는 절 표기 방식(마크다운 제목, XML 등)을 정하지 않으므로, 표기는 마크다운 제목을 기본으로 하고 사용자가 XML을 원하면 따른다.

```
Role            역할 1~2문장
Personality     톤과 협업 방식 (C12, G3에서 받은 것)
Goal            목적 (C1)
Success criteria 성공 기준과 완료 조건 (C1, C14, G5)
Constraints     규칙과 이유, 범위 밖 요청, 불확실할 때의 행동, 확인이 필요한 행동
Tools           도구별 사용 시점과 방법 (도구가 있을 때)
Output          절 구성, 길이, 형식, 톤
Stop rules      멈추고 보고할 조건
```

예시(C13)와 긴 자료는 Output 앞에 별도 절로 둔다. 캐싱과 reasoning 보존을 위해 고정 지시와 예시를 앞에, 바뀌는 내용을 끝에 둔다. 받은 값이 없는 절은 쓰지 않는다.

## 결정 질문

| ID | 조건 | 질문 | 종류 |
|---|---|---|---|
| M1 | 에이전트, 또는 API에서 작업을 대신 해 주는 앱 | 감독 없이 끝까지 진행하게 할까요? (진행 + 범위 변경·사용자 결정·파괴적 행동에서만 멈춤 / 넣지 않음) | API·에이전트 |
| M2 | M1=진행 + 길거나 여러 단계인 작업 | 끝내기 전에 요청을 빠짐없이 채웠는지 확인하고 남은 단계를 마저 하게 할까요? | 에이전트 |
| M3 | C10이 산문 또는 마크다운 | 사용자의 용어로 핵심부터 쓰는 문체 지침을 넣을까요? 사용자를 대신해 외부 독자에게 보낼 글(메일, 공지, 문서)을 쓰나요? | 전체 |
| M4 | 에이전트 + G6이 "최소화"가 아님 | 첫 도구 호출 전 안내와 단계 전환 때의 짧은 보고, 그리고 진행 보고를 읽지 않은 사람도 이해하게 새로 쓰는 최종 답 지침을 넣을까요? | 에이전트 |
| M5 | 에이전트 + G11=코딩 | 코딩 지침(기존 로직 재사용, 새 테스트는 필요할 때만, 읽기 쉬운 코드, 불필요한 추상화 피하기)을 넣을까요? 지켜야 할 저장소 관례와 호출자가 기대는 동작이 있으면 알려 주세요. | 에이전트 |
| M6 | C15=프론트엔드 UI 생성 | 원하는 이미지 종류와 서체를 알려 주세요. 장식용 문구를 줄이는 프런트엔드 지침을 넣을까요? | 전체 |
| M7 | 에이전트 | 작업을 막은 장애물(없는 파일, 고장 난 도구, 빠진 권한)을 최종 답에 반드시 밝히게 할까요? | 에이전트 |
| M8 | API·에이전트 + A2=멀티턴 또는 에이전트 | 대화 도중 지시, 도구 목록, 출력 형식, effort를 바꾸거나 기록을 압축·잘라내나요? | API·에이전트 |

M7은 시스템 카드가 밝힌 회귀를 막는 질문이므로 "예"를 "(권장)" 첫 선택지로 둔다. M8은 프롬프트 문구가 아니라 실행 설정 권고로 반영한다.

## 프롬프트 반영

**P1. 끝까지 진행** (M1=진행) 위험하거나 되돌릴 수 없는 행동의 확인 규칙(G4)은 이 스니펫이 대신하지 않으므로 그대로 둔다. 셋째 문단은 C9가 "가정을 밝히고 진행"일 때 넣는다.
```
작업이 끝나지 않았거나 허락된 다음 단계가 있으면 턴을 끝내지 말고, 작업 범위 안에서 다음 단계를 진행한다. 턴을 끝내기 전의 마지막 답이 다음 단계 제안, 계획, 일상적인 결정 요청, 실행할 작업 안내 같은 사용자에게 넘기는 내용이면, 그 단계를 직접 해서 요청한 결과에 다가간다. 그럴 권한이 있는지 확인하고, 세운 가정과 내린 결정은 사용자에게 알린다.

작업 범위가 크게 바뀌거나, 실제로 막혔거나, 사용자가 정해야 할 결정이 있거나, 되돌릴 수 없거나 파괴적인 행동 앞일 때만 멈추고 사용자에게 확인한다.

작업을 이어 가는 데 필요하면 되돌릴 수 있는 합리적인 가정을 세우고, 범위 안에서 진행에 도움이 되면 그 가정을 밝힌다. 스스로를 의심하며 멈추거나, 할 수 있는 일을 설명만 하고 멈추거나, 작업을 해 주겠다고 제안하거나, 일부만 답하지 않는다. 진행할 방법이 전혀 없을 때만 예외다.
```
원문:
```text
Avoid stopping to end the turn while the task is incomplete or if there is an authorized next step you can take, and instead take the next steps within task scope to progress the user's request. If your final response before ending the turn is a suggested next step, a plan, a request to the user for a routine decision, instructions for a task to execute, or similar handoff to the user, take these steps yourself to make progress towards what the user asked for. Make sure that you have authorization to do so, and flag any assumptions or decisions you make to the user.

Only stop to clarify with the user if there is significant change in task scope, you are concretely blocked, have a decision that the user needs to resolve, or before irreversible or destructive actions.

Make reasonable, reversible assumptions to carry work forward and state them if it progresses the task within scope. Do not second guess yourself, stop after describing what you could do, offer to do the work, or provide a partial answer unless there is no way you can proceed.
```
원문의 "you maketo"는 오타라 "you make to"로 고쳤다. 앱에 비동기 질문 도구를 둘 수 있으면 실행 설정 권고의 비동기 질문 도구도 함께 권한다.

**P2. 완료 확인** (M2=예) P1의 첫 문단 대신 넣는다. 괄호 안 자율 진행 예시(worktree, 충돌 해결, draft PR)는 G4의 확인 필요 행동과 겹치면 빼거나 G4에 맞춰 바꾼다. 길고 복잡한 작업의 마지막 확인까지 버티게 하려면 effort를 높이는 것도 도움이 된다고 문서가 밝힌다.
```
행동 쪽으로 기울어, 사용자가 요청한 작업을 마칠 때까지 계속한다. 작업이 끝나지 않았거나 허락된 다음 단계가 있으면 턴을 끝내지 말고, 작업 범위 안에서 다음 단계를 진행한다. 요청의 모든 부분을 빠짐없이 다뤘는지 확인하고, 사용자의 목표를 온전히 채운 결과를 낼 때까지 계속한다. 꾸준한 작업이 필요한 일이면 의도한 결과가 완전히 이뤄질 때까지 필요한 일을 모두 한다.

명백히 파괴적이거나 되돌릴 수 없는 것이 아니면 사용자의 목표를 향해 스스로 진행한다(예: 필요하면 격리된 worktree나 checkout 만들기, 병합 충돌 해결, draft PR 만들기). 턴을 끝내거나 작업을 완료했다고 말하기 전에, 결과가 사용자가 요청한 것을 온전히 채우는지 확인한다. 남은 단계가 있거나 아직 검증이 필요한 부분이 있으면 끝내기 전에 마저 한다.
```
원문:
```text
Bias towards action, and persist until you've completed the task the user asked for. Avoid stopping to end the turn while the task is incomplete or if there is an authorized next step you can take, and instead take the next steps within task scope to progress the user's request. Make sure that you have accounted for every part of the user's request, and persist until you've delivered a result that fully satisfies the user's goal. If a task requires sustained work, do all the necessary work until the intended outcome is completely fulfilled.

Progress autonomously towards the user's goal (e.g. creating isolated worktrees / checkouts if needed, resolving merge conflicts, creating draft PRs etc) unless they are clearly destructive or irreversible. Before ending a turn or calling your work complete, check that your work fully satisfies what the user asked for. If any steps remain or any part of the result still needs verification, follow through on this work before finishing.
```

**P3. 문체** (M3) 첫 문단은 문체 지침에 예일 때, 둘째 문단은 외부 독자용 글을 쓸 때 넣는다. 첫 문단은 사용자와 함께 일하는 협업 상대로 쓸 때의 문구다.
```
사용자와 자료가 쓰는 용어로 쓴다. 설명을 더 정확하게 만든다면 기술적 세부와 분야 용어를 남긴다. 능동태로 쓰고, 밀접한 세부는 한곳에 모은다. 핵심을 먼저 다루고, 답의 뒷부분을 읽어야 이해되는 언급은 피한다. 사용자가 추론을 따라올 수 있을 만큼 맥락을 준다.

사용자를 대신해 외부 독자에게 보낼 메시지나 자료를 쓸 때는 누가 읽을지 생각하고 그 독자에 맞춘다. 독자는 사용자와 같은 맥락을 갖고 있지 않을 가능성이 크므로, 내용을 이해하는 데 필요한 배경이나 근거를 준다. 기존 글을 검토하거나 고칠 때는 작성자의 내용과 표현을 살리고, 사용자가 원하는 수정만 정확히 따른다.
```
원문:
```text
Write using terminology the user and sources use. Keep technical details and use domain-specific language when they make the explanation more precise. Use the active voice and keep closely related details together. Cover the key points up front, and avoid references that the reader can only make sense of later in the response. Give the user enough context to follow your reasoning.

When drafting a message or any other material on behalf of the user to be sent to an external audience, consider who will read it and tailor the content to that intended audience. The intended audience likely does not have the same context as the user, so ensure that you provide the background information or reasoning required for the audience to understand the content. When reviewing or editing existing content, preserve the author's content and wording, and follow the user's instruction carefully for what edits they want.
```

**P4. 진행 보고와 최종 답** (M4=예) 첫 문단은 GPT-5.6 Sol 문서의 권고이고, 나머지는 GPT-6.2 문서의 문구다.
```
여러 단계로 된 작업이면 첫 도구 호출 전에 첫 단계를 밝히는 한두 문장의 안내를 사용자에게 보여 준다. 그 뒤에는 큰 단계가 바뀔 때만, 결과 하나와 다음 단계를 짧게 알린다. 일상적인 도구 호출을 하나하나 설명하지 않는다.

최종 답은 중간 보고의 연장이 아니라 사용자가 작업을 처음 보는 자리로 여긴다. 최종 답이 보이면 앞선 진행 보고는 접히므로, 최종 답은 그것만으로 완결되어야 한다.

최종 답과 사람이 읽는 모든 자료는 대상 독자를 위해 새로 쓴다. 추론을 옮겨 적거나 비슷하게 바꿔 쓰지 않고, 그 문체도 따르지 않는다. 추론, 도구 호출, 서브에이전트·자동화에 준 지시에서 쓴 작업용 줄임말, 은어, 약어를 가져오지 않는다.
```
원문:
```text
For multi-step tasks, give a one- or two-sentence user-visible update that states the first step before the first tool call. After that, send sparse updates at major phase changes, each stating one outcome and the next step. Don't narrate routine tool calls.

Treat your final answer as the user's first look at your work, and not as a continuation of intermediate commentary. The final answer must always be fully self-contained: users should never need to read earlier commentary updates for context, since they are collapsed when the final answer is shown to the user.

Write the final answer and all other human-facing material anew for the intended reader. Do not copy or closely paraphrase your reasoning or adopt its writing style. Do not carry over working shorthand, jargon, or abbreviations from your reasoning, tool calls, or instructions to subagents and automations.
```
첫 문단은 GPT-5.6 Sol 문서를 요약한 것이며 원문 그대로가 아니다.

**P5. 코딩** (M5=예) M5에서 받은 저장소 관례와 호출자가 기대는 동작은 이 스니펫 뒤에 Constraints로 적는다. (b)는 G13의 테스트 하드코딩 방지와 함께 쓸 수 있다. 사용자가 테스트를 완료 조건으로 정했으면 (b)를 그 조건에 맞춰 고친다.
```
무엇보다 사용자의 작업을 온전히 해내는 정확하고 품질 높은 코드를 꼼꼼히 만든다. 코드는 읽기 쉽게 두고, 사용자가 요청한 결과가 의도대로 동작하는지 확인한다. 코딩할 때는 다음을 따른다.

(a) 가능하면 저장소의 기존 로직을 재사용한다. 정확성을 해치지 않는 한 코드베이스의 기존 클래스, 메서드, 표현 방식, API를 재사용한다. 코드를 합치거나 지우기 전에, 작업이 바꾸라고 하지 않은 한 호출자가 기대는 동작을 보존한다.
(b) 요청받았거나, 저장소가 요구하거나, 기존 테스트가 놓칠 특정 회귀를 잡는 데 필요한 경우가 아니면 새 테스트를 쓰지 않는다.
(c) 사람이 읽을 수 있는 코드를 쓴다. 줄 수 줄이기, 짧은 변수 이름, 압축된 서식, 빽빽한 한 줄 코드를 단순함의 대용으로 쓰지 않는다. 주석과 변수 이름은 사람이 읽고 이해할 수 있게 쓴다. 많은 분기, 조건, 숨은 가정을 담은 코드 골프식 표현은 지나치게 복잡한 것으로 본다.
(d) 불필요한 간접 계층과 추상화를 피한다. 헬퍼 함수, 유틸리티 함수, 클래스 추상화는 분기를 늘리지 않아도 인지 부담을 늘릴 수 있다.
```
원문:
```text
Above all, be thorough in producing high-quality, correct code that completely fulfills the user's task. Keep the code easy to read and verify that the user-requested outcome works as they intend. Follow these instructions when coding:

(a) Reuse existing logic in the user's repo when you can. You should reuse existing classes, methods, representations, and APIs in the codebase as long as they preserve correctness. Before consolidating or removing code, preserve the behavior its callers rely on unless the task requires changing it.
(b) Skip new tests unless requested, required by the repo, or needed to catch a specific regression existing tests would miss.
(c) Make sure that code is human readable. Do not use fewer lines, shorter variable names, minified formatting, or dense one-liners as substitutes for simplicity. Ensure that comments and variable names are readable and understandable to a human. Code-golfed expressions count as overly complex when they encode many branches, conditions, or hidden assumptions.
(d) Avoid unnecessary indirection and abstraction. Helper functions, utility functions, and class abstractions can add cognitive complexity even when they do not add branches.
```

**P6. 프런트엔드** (M6=예) M6에서 받은 이미지 종류와 서체(특정 글꼴이 중요하면 그 이름)는 이 스니펫 앞에 적는다. 사용자가 SVG나 일러스트를 원하면 첫 항목을 그에 맞춰 바꾼다.
```
프런트엔드 UI가 있는 웹페이지나 앱을 만들 때는 다음을 따른다.

- 시각 요소는 대체로 프로젝트의 스타일과 목적에 맞는 실사 이미지(이미지 생성이나 이미지 검색)를 고른다. SVG는 사용자가 명시적으로 원할 때 쓴다.
- 텍스트 요소는 사용자에게 필요한 정보를 주거나, 탐색이나 행동을 돕거나, 명시적인 콘텐츠 요청을 채울 때만 넣는다. 장식용 번호, 채우기용 배지, 중복 제목, 주변 UI가 이미 분명히 보여 주는 것을 다시 말하는 설명 문구는 빼고, 필요한 라벨, 안내, 상태 피드백은 남긴다.
```
원문:
```text
When generating webpages or apps with a frontend user interface, follow these instructions:

- When choosing visuals, generally prefer realistic images from ImageGen or image search that suit the project's style and purpose. Use SVGs when the user specifically asks for them.
- Include a text element only when it provides information the user needs, helps them navigate or act, or fulfills an explicit content request. Remove decorative numbering, filler badges, redundant headings, and explanatory copy that merely restates what the surrounding interface already makes clear, while preserving necessary labels, instructions, and status feedback.
```
시각 작업은 디자인 도구의 참고 이미지를 주거나 이미지 생성 도구로 참고 이미지를 먼저 만들게 한 뒤, 그것에 맞춰 만들고 렌더링해 다듬게 하라고 문서가 권한다. 사용자가 참고 이미지를 줄 수 있으면 "다음 단계"에 적는다.

**P7. 장애물 보고** (M7=예) 공식 문구는 없다. Codex의 developer 프롬프트가 이 누락을 줄인다는 시스템 카드의 관찰에 맞춰 이 스킬이 쓴 문구이며, 원문은 이 스킬의 영어판이다. P1·P2와 함께 넣어도 충돌하지 않는다. 끝까지 진행하되, 진행하지 못한 부분은 숨기지 않게 한다.
```
작업 중 요청을 그대로 해내지 못하게 막은 장애물(요청받은 파일이 없음, 도구나 검색이 실패함, 권한이 없음, 요구 사항이 빠짐 등)을 만나면, 최종 답에 그 장애물과 그 때문에 하지 못했거나 다르게 한 부분을 분명히 적는다. 답을 짧게 쓰려고 이 내용을 빼지 않는다. 우회했다면 무엇을 대신했는지도 적는다.
```
원문(이 스킬의 영어판):
```text
If an obstacle prevented you from doing what was asked exactly as requested (a requested file is missing, a tool or search failed, access was denied, a requirement was missing, etc.), state the obstacle in your final answer along with what you could not do or did differently because of it. Do not omit this to keep the answer short. If you worked around it, say what you did instead.
```

## 제거 검토

- `temperature`, `top_p`, `top_logprobs`, `logprobs` 설정과 Responses `include`의 `message.output_text.logprobs`. GPT-6.2에서는 빼야 한다.
- reasoning effort `none`과 `minimal`. `low`로 바꾼다.
- "간결하게", "짧게" 같은 일반 길이 지시. GPT-6.2는 기본이 간결하므로 다시 본다. 남겨야 하면 작업별 길이로 바꾸고, 장애물과 가정 보고는 줄이지 말라고 함께 적는다(시스템 카드는 간결함 훈련이 장애물 누락과 관련 있을 수 있다고 본다).
- "먼저 물어봐라", "바꾸지 마라", "승인을 기다려라" 같은 확인 문구의 반복. GPT-6.2는 의도가 불분명하면 확인을 기다리는 경향이 있어 더 자주 멈춘다. 확인이 필요한 행동은 G4 목록으로 한 번만 적는다.
- GPT-6 Astra 가이드에서 옮겨 온 스니펫(스킬 지침보다 사용자 지시 우선, 서브에이전트 적극 위임, 구현을 따라 하는 테스트 금지). GPT-6.2 문서에는 해당 관찰이 없으므로 평가로 필요가 확인된 것만 남긴다. 테스트 범위는 P5의 (b)로 대신한다.
- 대화 도중 처음 developer 메시지를 고쳐 쓰거나 지난 도구 결과를 줄이는 설계. reasoning이 버려지므로 실행 설정 권고(M8)의 덧붙이기 방식으로 바꾼다.
- 동작을 바꾸지 않는 반복 규칙, 스타일·절차 지시, 예시, 무관한 도구. GPT-5.6 Sol 문서는 한 묶음씩 빼며 같은 평가를 다시 돌리라고 권한다.
- `ALWAYS`, `NEVER`, `must`를 진짜 불변 조건이 아닌 곳에 쓴 문구 (공통 원칙 E와 같은 취지).
- Claude 전용 설정과 문구: assistant prefill, `thinking`, `output_config.effort`, `budget_tokens`, 베타 헤더. GPT API에는 해당하지 않는다.

## 실행 설정 권고

- API: 도구를 쓰면 Responses API를 쓴다. Chat Completions의 함수 호출 요청은 Responses로 옮긴다.
- `reasoning.effort`(Responses) 또는 `reasoning_effort`(Chat Completions): `low`~`max`. 기본값이 문서에 없으므로 값을 명시한다. 새 통합은 `medium`에서 시작한다. 이전 모델에서 옮기면 기존 값과 한 단계 낮은 값을 평가로 비교한다(GPT-5.6 Sol 문서). `xhigh`·`max`는 평가에서 분명한 이득이 확인될 때만 쓴다.
- `reasoning.context`: 문서가 GPT-6.2의 `all_turns` 지원을 밝히지 않으므로 넣지 않는다(생략 = 모델 기본값).
- `text.verbosity`: `low`, `medium`, `high`로 기본 상세도를 정하고, 작업별 길이와 구조는 프롬프트에 적는다(deployment checklist). 기본값은 문서에 없다.
- `max_output_tokens`: reasoning 토큰도 여기에 포함된다. 시작할 때는 reasoning과 출력에 25,000 토큰 이상을 남기라고 reasoning 문서가 권한다. 모자라면 `status: "incomplete"`, 이유 `max_output_tokens`로 끝난다.
- 앞부분 유지(M8): 대화 도중 설정을 바꿀 때 앞선 기록을 고치지 않고 뒤에 덧붙인다. 그래야 reasoning이 남고 캐시도 유지된다.
  - effort 변경: 요청 수준의 `reasoning.effort`는 그대로 두고 `{"type": "configuration_update", "reasoning": {"effort": "high"}}` 입력 항목을 덧붙인다.
  - 출력 형식 변경: `text.format` 대신 새 스키마를 담은 `configuration_update` 항목을 덧붙인다.
  - 도구 변경: `tools`를 바꾸지 않고, 추가는 `developer` 역할의 `additional_tools` 항목으로, 제한은 `tool_choice`의 `allowed_tools`로 한다. 기존 도구 정의의 순서는 유지한다.
  - 지시 변경: 처음 developer 메시지를 고치지 않고, 이전 지시 대신 새 지시를 따르라는 developer 메시지를 덧붙인다.
  - 압축: OpenAI 압축(`/responses/compact`, `context_management`)은 뒤따르는 reasoning을 유지한다. 직접 압축하면 압축 항목을 최근 턴 앞이 아니라 맨 끝에 둔다.
  - 긴 도구 결과와 큰 이미지·파일은 처음 보낼 때 줄인다. 지난 항목을 나중에 잘라내면 앞부분이 바뀐다.
  - 대화 도중 더 낮은 모델로 바꾸거나 end user·조직을 바꿔도 reasoning이 버려진다. 응답의 `input_transformations`로 어떤 reasoning이 왜 빠졌는지 확인한다.
- 함수 호출 기록: Responses에서 도구 결과와 함께 reasoning 항목을 돌려보낸다. 기록을 직접 관리하면 모든 출력 항목을 순서대로 넣고 새 항목은 뒤에 붙인다.
- 진행 보고(M4): progress update에는 `phase: "commentary"`, 최종 답에는 `phase: "final_answer"`를 쓰고, assistant 메시지의 phase를 그대로 돌려보낸다(deployment checklist).
- 비동기 도구: 오래 걸리는 함수·custom 도구에 `async: true`를 두고 나중에 원래 `call_id`로 결과를 돌려준다. 내장 도구에는 쓸 수 없다. `request_user_input_async` 같은 비동기 질문 도구를 두면, 모델이 사용자에게 묻고 답에 달려 있지 않은 작업을 계속한다.
- 캐싱: GPT-5.5 이하에서 옮기면 `prompt_cache_retention` 대신 `prompt_cache_options.ttl: "30m"`을 쓴다. 30분 캐시 쓰기는 100만 토큰당 Astra $10, Sol $2.5로 따로 청구된다.
- Zero Data Retention: 켜져 있으면 Responses가 `store`를 `false`로 다룬다. 멀티턴이면 암호화된 reasoning 항목을 포함한 이전 출력 항목을 순서대로 다시 보낸다.
- 데이터 위치: 두 모델 모두 Standard, Fast, Batch에서 US·EU 데이터 위치를 지원한다. Ultrafast는 US만 지원한다.

```yaml
model: <gpt-6.2-astra|gpt-6.2-sol>
reasoning:
  effort: <low|medium|high|xhigh|max>   # 근거
text:
  verbosity: <low|medium|high>           # 근거
max_output_tokens: <값>                  # reasoning 포함
```

## 검수 항목

- [ ] reasoning effort가 `none`·`minimal`이 아니고 값이 명시되어 있다
- [ ] `temperature`, `top_p`, `top_logprobs`, `logprobs`가 없다
- [ ] 도구를 쓰면 Responses API로 권고했다
- [ ] Claude 전용 설정(prefill, `thinking`, `output_config`, 베타 헤더)이 없다
- [ ] P1·P2를 넣었어도 위험 행동 확인 규칙(G4)이 유지되고, P2의 자율 진행 예시가 G4와 겹치지 않는다
- [ ] 확인·승인 문구가 G4 목록 밖에서 반복되지 않는다
- [ ] 에이전트 프롬프트에서 M7을 묻고, 답이 예이면 P7이 있다
- [ ] M8이 예이면 앞부분을 고치지 않고 덧붙이는 방식을 권고했다
- [ ] 작업별 길이·구조가 프롬프트에 있고, 기본 상세도는 `text.verbosity`로 권고했다
