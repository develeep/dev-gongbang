# dev-gongbang 플로우를 단일 루프로 접는 계획

dev-gongbang v1.14.0(master `0c50de8`)의 개발 플로우를 Anthropic 글 「에이전트 구축: 서브 에이전트를 메인 에이전트 루프에 통합해야 하는 시점」과 비교하고, 2026-11-25 사용자 결정에 따라 위임을 접는 순서를 정한 계획입니다. 대상은 `skills/in-progress/`의 run-flow와 단계 스킬, 흐름이 부르는 framing-problems와 check-guidelines, `extras/omp/`, `extras/orca/`, `extras/paseo/`입니다. 앞선 문서는 [원칙 문서](./2026-11-19-multi-agent-orchestration-principles.md), [설계안](./2026-11-19-multi-agent-orchestration.md), [강화 계획](./2026-11-20-orchestration-hardening-plan.md)입니다.

이 문서는 계획만 담습니다. 스킬, 규칙, extras는 고치지 않았고 eval도 돌리지 않았습니다. 분석은 네 갈래(단계 스킬의 위임 지점, 구현·리뷰 위임 계층, 상시 컨텍스트·eval·게이트, 기존 설계의 근거)로 했고, 그 기록의 인용은 파일을 다시 열어 맞는 것만 옮겼습니다.

## 이 문서를 읽는 법

- **글의 주장**은 `A12`처럼 번호로 가리킵니다. 번호의 뜻은 맨 끝 "부록: 글 주장 번호"에 있습니다. 글 주소는 `https://claude.com/ko/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop`입니다.
- **근거**는 레포 기준 상대 경로와 줄 번호(`path:line`)입니다. 같은 파일의 줄이 이어지면 `path:10, :15`처럼 씁니다. 줄 번호는 `0c50de8` 기준입니다.
- **줄임**: 원칙은 `docs/context/design/2026-11-19-multi-agent-orchestration-principles.md`, 설계는 `docs/context/design/2026-11-19-multi-agent-orchestration.md`, 강화는 `docs/context/design/2026-11-20-orchestration-hardening-plan.md`입니다. `원칙:59`는 원칙 문서 59행입니다. 원칙 문서와 설계안은 2026-11-26에 이 계획대로 다시 썼으므로, `원칙:NN`·`설계:NN`은 지금 파일이 아니라 개정 전 `f991a4d` 판(`git show f991a4d:<경로>`)의 줄입니다. 강화 계획은 줄 수를 바꾸지 않고 표시만 붙여 `강화:NN`은 지금 파일에서도 맞습니다.
- **(추론)**은 파일에 적혀 있지 않은 해석이고, **미확인**은 확인하지 못한 것입니다. 미확인은 7절에 모았습니다.
- **위임 지점 번호**(R1, S1, T1, M1 등)는 3절 표의 번호이고, **사례 번호**(E1 등)는 5절 표의 번호입니다.

## 1. 한 줄 결론과 목표 모양

**한 줄 결론**: 지금 플로우는 단계 순서를 스킬에 둔 점은 글과 같지만(A31), 메인 세션을 조정자로 두고 초안, 구현, 리뷰, PR 본문을 역할 12개와 워커에 나눠 맡기는 점이 글과 다릅니다(A4, A13, A29). 메인 세션 하나가 0~7단계를 직접 하고 다른 회사 모델의 교차 리뷰와 brief 냉독 두 가지만 읽기 전용 호출로 남기도록, e2e 사례 약 10개로 기준선을 먼저 잡은 뒤 위임을 하나씩 접습니다(A36, A46). 병렬 워커는 지우지 않고, 사용자가 고를 때만(이번 실행에서 워커 도구 절차를 지정하거나 에이전트 규칙에 등록했을 때) 쓰는 선택 경로로 둡니다(결정 8).

### 목표 모양

기본 흐름은 메인 단일 루프, 교차 리뷰, 냉독 예외 하나이고, 병렬 워커는 선택입니다.

| 누가 | 무엇을 | 형태 |
|---|---|---|
| 메인 세션 (모델 하나, 컨텍스트 창 하나) | 0~7단계의 일 전부: 요구사항 정리, 구체화, brief 초안과 수정, 티켓 분할, 구현, 완료 기준 확인, 코드 리뷰와 규칙 검사, 리뷰 지적의 검증과 반영, 완료 기록, PR 본문, 커밋 메시지, 바깥 쓰기 | run-flow와 단계 스킬의 절차를 그대로 따르는 단일 루프입니다. 계획을 쓴 세션이 실행도 합니다(A26, A29). 모델은 사용자가 고른 세션 모델입니다 |
| 교차 리뷰 (남김 1) | 이번 변경을 구현한 모델과 다른 회사의 모델이 diff를 읽고 지적을 돌려줍니다 | 아래 "교차 리뷰의 형태" |
| 냉독 독자 (남김 2) | 대화를 모르는 독자 3명이 brief 초안만 읽고 5문항에 답합니다 | 아래 "냉독의 형태" |
| 병렬 워커 (선택) | 함께 시작할 수 있는 티켓을 티켓마다 worktree의 워커가 구현합니다. 메인 세션은 순서를 지키고 머지와 완료 기록, 교차 리뷰 호출을 합니다 | 지금의 진입 조건(`skills/in-progress/run-ticket/references/multi-ticket.md:26-30`)을 PR #38 그대로 씁니다: 사용자나 부른 쪽이 워커 도구 절차(`extras/orca/`, `extras/paseo/`)를 명시 지정했으면 그것을 먼저, 아니면 레포·에이전트 규칙에 등록된 절차를 씁니다. 결정 8의 "사용자가 등록할 때만"은 사용자의 선택(지정이나 등록)이 있을 때만 병렬이 된다는 뜻으로 읽고, 이 분기를 등록 하나로 좁히지 않습니다. 지정도 등록도 없으면 메인이 티켓을 차례로 직접 합니다. 워커의 모델은 고정하지 않고 사용자 설정과 환경을 따릅니다(결정 1, 결정 8) |
| 사용자 | 지금과 같은 확인: 구체화 기록 확정, brief 게시, 티켓 분할안 승인, 작업 브랜치, 흐름 문서 커밋, 6단계 선택, PR 본문 | 스킬이 묻는 질문을 그대로 받습니다(`skills/in-progress/run-flow/SKILL.md:14, :17`) |
| 코드 | 코드 지문 계산, 레포 검증 명령 | `skills/in-progress/run-flow/scripts/code_fingerprint.sh:28-38` |

없어지는 것은 조정자 선언, brief 초안 서브에이전트, 구현 서브에이전트와 실패 시 승격, 리뷰 역할 셋(reviewer, code-reviewer, security-reviewer)의 구분, 화면 확인·PR 본문·탐색 역할, 병렬 워커가 쓰던 원인 보고 역할, 부르는 곳이 없는 Paseo 프로필과 플레이북, 역할별 모델 고정입니다. Orca·Paseo 병렬 워커 절차는 없어지지 않고 기본 흐름에서 빠져 선택 기능이 됩니다. 항목별 처리는 3절에 있습니다.

### 교차 리뷰의 형태 (A12, A40)

- **부르는 방식**: 메인 세션이 run-ticket 5단계에서 도구를 쓰듯 한 번 부르고, 결과를 받아 같은 대화에서 이어 갑니다. 리뷰어는 사용자와 대화하지 않고 다음 단계를 정하지 않습니다. 일을 넘겨주고 끝내는 핸드오프가 아닙니다(A40).
- **넘기는 것**: 리뷰할 diff 범위(작업 시작 HEAD 기준), brief 전문, 볼 기준 목록입니다. 기준은 버그, 작업 경계와 레포 규칙 위반이고, 인증·권한·결제·개인정보를 다루는 변경이면 보안을 더합니다. 보안 리뷰를 따로 부르지 않고 이 조건부 기준으로 합칩니다(결정 5). 리뷰어는 이것만 있으면 일할 수 있으므로 경계가 컨텍스트 기준입니다(A12). 비밀값과 원문 로그는 넘기지 않습니다(강화:67).
- **권한**: 읽기 전용입니다. 파일을 고치거나 커밋하지 않고 바깥에 쓰지 않습니다. 메인 세션은 호출 전후의 코드 지문을 비교해 확인합니다.
- **돌려받는 것**: 지적 목록과 수행한 모델 이름만 받습니다. 지적마다 어느 기준의 지적인지, 심각도, 파일과 줄, 근거, 고칠 방법을 적습니다. 지금 code-reviewer의 보고 형식(`extras/omp/agents/code-reviewer.md:12`)에 기준 칸을 더한 것이고, 근거에는 재현 명령이나 원문을 적게 합니다. 요약, 총평, 수정 diff는 받지 않습니다.
- **메인이 검증**: 지적을 하나씩 재현하거나 코드·규칙 원문과 대조해 `수용 / 기각(사유) / 범위 밖`으로 적습니다. 수용한 것을 고친 뒤 검증 명령을 다시 돌립니다. 지적이 없다는 보고는 수락의 근거가 아니라 입력 하나로 봅니다(원칙:76).
- **모델**: 모델 id를 고정하지 않습니다. 조건은 "이번 변경을 실제로 구현한 모델과 다른 회사"뿐입니다(`skills/in-progress/run-ticket/SKILL.md:108`). 부를 때마다 다음 순서에서 처음 되는 것을 씁니다.
  1. 사용자가 이번 실행에서 지정한 모델이나 수단
  2. 사용자 설정(에이전트 규칙 파일, 하네스 설정, 저장된 프로필)에 적힌 교차 리뷰 수단
  3. 환경 조회: 이 세션에서 쓸 수 있는 provider, 모델, 에이전트 목록에서 다른 회사 모델을 고르고, 무엇을 골랐는지 알립니다
  4. 다른 회사 모델이 없으면 같은 회사 모델의 새 컨텍스트 리뷰로 대체합니다. 넘기는 것, 읽기 전용, 반환 형식은 위와 같습니다. 대체했다는 사실을 완료 기록에 적고 흐름을 계속합니다(결정 6)
- **독립 판정**: 계획한 모델이 아니라 실제로 수행한 모델로 판정하고, 상태 파일 `- 교차 리뷰 모델:`에 적습니다(`skills/in-progress/run-ticket/SKILL.md:114`, `skills/in-progress/run-flow/assets/state-file.md:37`). 수행한 모델이 구현한 모델과 같은 회사면 다음 수단으로 다시 맡기고, 남은 수단이 4번뿐이면 4번의 대체로 칩니다.
- **실패했을 때**: 리뷰를 건너뛰고 진행하는 경로는 없앱니다. 응답이 없거나 결과를 읽을 수 없으면 위 순서의 다음 수단에 다시 맡깁니다. 다른 회사 모델을 구하지 못한 것은 멈출 이유가 아니라 4번의 대체 조건입니다. 이때 완료 기록에 "교차 리뷰 대체(같은 회사 모델 <모델 이름>, 다른 회사 모델 없음)"처럼 대체했다는 것과 수행 모델을 적고 6단계로 갑니다(결정 6). 같은 회사 모델은 같은 실수를 함께 놓치기 쉬우므로(`skills/in-progress/run-ticket/SKILL.md:108`) 대체 리뷰는 독립 검증으로 치지 않고, 사용자가 완료 기록에서 그 사실을 보게 합니다.
- **부르는 수단**: omp에서는 읽기 전용 서브에이전트 하나, Orca나 Paseo를 등록한 환경에서는 그 도구의 교차 리뷰 워커입니다. 셋 다 없는 환경(플러그인만 설치)에서는 세션이 띄우는 읽기 전용 서브에이전트를 씁니다. 그 서브에이전트에 다른 회사 모델을 줄 수 없으면 세션과 같은 회사 모델로 띄우는 4번의 대체가 됩니다(결정 6). 새 컨텍스트를 하나도 띄울 수 없는 환경에서 어떻게 할지는 결정 6이 다루지 않아 열린 질문 Q10으로 올렸습니다(6절).

### 냉독의 형태

- 메인 세션이 brief 초안을 직접 쓴 뒤 새 컨텍스트의 독자 3명을 한 메시지에서 함께 띄웁니다. 대화 없이 초안 전문, 저장소 경로, 고정 5문항만 줍니다(`skills/in-progress/set-brief/SKILL.md:57-69`).
- 독자는 답만 돌려주고 초안을 고치지 않습니다. 답을 비교하고 원인 문장을 고치는 일은 메인 세션이 합니다(`skills/in-progress/set-brief/SKILL.md:71`).
- 독자의 모델은 따로 정하지 않고 세션 모델을 따릅니다. 접은 뒤에는 구현하는 쪽이 메인 세션이므로, "구현할 작업자와 같은 모델이 읽어야 한다"(`skills/in-progress/set-brief/SKILL.md:57`)는 조건이 기본 경로에서는 그대로 채워집니다. 선택 경로(병렬 워커)에서는 티켓을 워커가 구현하므로 워커 모델이 세션 모델과 다를 수 있고, 그때는 이 조건이 채워지지 않습니다. 대응은 set-brief의 기존 분기(같은 줄의 "에이전트 규칙이나 이 스킬을 부른 쪽이 냉독 검증을 맡을 에이전트를 정해 두었으면 그 에이전트")를 씁니다. 워커 모델로 냉독 에이전트를 정해 두었으면 그것으로 띄우고, 아니면 세션 모델로 읽은 뒤 워커 모델과 다르다는 사실을 냉독 결과 파일(`.review.md`)에 적습니다. brief는 3단계에서 쓰고 병렬 여부는 5단계에서 정해지므로, 3단계에서 워커 모델을 알 수 있는 것은 사용자가 워커 도구 절차를 미리 등록해 둔 경우뿐입니다 **(추론)**.
- 글 기준으로는 끝나면 버리는 새 창 여럿(A10)이자 블랙박스 검증(A12)입니다. 메인 세션은 대화를 이미 알고 있어 이 검증을 대신할 수 없습니다 **(추론)**.

## 2. 차이 표

| 축 | 글 | 현재 (v1.14.0) | 차이 | 근거 |
|---|---|---|---|---|
| 루프 구조 | 모델 하나와 컨텍스트 창 하나가 도구 루프를 돌리고, 계획을 쓴 쪽이 실행합니다(A26, A29). 순서와 절차는 스킬에 둡니다(A31). 고정 파이프라인과 최상단 오케스트레이터가 하던 일은 모델이 합니다(A4) | 메인 세션은 "조정자"입니다. 0~7단계 순서와 시작 단계 판정표가 스킬 문장으로 정해져 있고, 단계가 끝나면 바로 다음 단계로 갑니다. 1·2·4단계는 메인이 직접 하고, 3단계의 초안·냉독과 5단계의 구현은 새 컨텍스트에 맡깁니다 | 순서를 스킬에 둔 것은 글과 같습니다. 다른 점은 메인이 초안과 구현을 하지 않는다는 것입니다. 구현하는 쪽은 계획을 만든 대화를 보지 못합니다 | `skills/in-progress/run-flow/SKILL.md:10, :15, :47-61, :65-81, :91, :99, :103, :109, :122`, `extras/omp/AGENTS.md:3` |
| 위임 | 세 조건일 때만 남깁니다: 측정된 컨텍스트 저하(A9), 버릴 수 있는 새 창의 병렬(A10), 도구 선택 실패나 지침 충돌(A11). 경계는 컨텍스트 기준으로 긋고 결과는 간결하게 받으며(A12), 메인이 도구로 부릅니다(A40). 문제 유형으로 나누면 인계마다 내용이 빠집니다(A13) | 스킬에 위임 지점 22곳(3절 가), omp 위임 표에 역할 12개와 자문 역할, Paseo 프로필 18개, 플레이북 역할 2개, Orca·Paseo 워커가 있습니다. 스킬은 역할 이름을 모르고 "에이전트 규칙이 정해 두었으면 그 에이전트"로 부릅니다. 나누는 기준은 "확인할 기준이 다르면 에이전트를 둘"입니다 | 세 조건에 분명히 드는 것은 냉독(A10, A12), 병렬 워커(A10), 교차 리뷰(A12의 블랙박스 검증), 화면 확인(A11, 추론)입니다. 컨텍스트를 이유로 든 위임(초안, 구현, 탐색, PR 본문)은 저하를 측정한 기록이 없습니다. 판정 기준으로 역할을 나누는 것은 글의 "컨텍스트 기준"과 다릅니다 | `extras/omp/AGENTS.md:23, :27-40`, `extras/paseo/config.json:6-168`, `skills/in-progress/run-ticket/SKILL.md:80, :90, :92, :104, :110, :116`, `skills/in-progress/run-flow/SKILL.md:103` |
| 컨텍스트 공개 | 스킬로 컨텍스트를 필요할 때만 싣고(A20, A22), 여러 작업의 컨텍스트를 한 창에 두어 앞 결과를 잇습니다(A21). 메모와 기록을 신중히 다룹니다(A25) | 스킬 설명, SKILL.md, 단계별 참조 파일 순으로 필요할 때 읽습니다. 사용자 답, 결정, 리뷰는 상태 파일에 바로 적습니다. 단계 사이에는 대화 대신 결과물을 넘깁니다. 서브에이전트는 에이전트 규칙을 받지 못해, 맡길 때 필요한 것을 모두 넘겨야 합니다 | 필요할 때 싣는 구조와 상태 파일은 글과 같습니다. 다른 점은 초안과 구현이 메인 창 밖에서 일어나 앞 단계의 대화가 이어지지 않는다는 것입니다. 인계 목록이 그 빈자리를 메웁니다. 도구 검색(A20)은 플러그인이 아니라 하네스의 기능이라 이 레포에는 대응하는 것이 없습니다 | `.claude/CLAUDE.md:67-70`, `skills/in-progress/run-flow/SKILL.md:16, :34, :103, :143`, `skills/in-progress/run-ticket/SKILL.md:22`, `extras/omp/AGENTS.md:50`, `skills/in-progress/run-flow/references/brief-stage.md:15-22` |
| 게이트·예산 | 턴·비용 예산과 쓰기 게이트는 하네스가 겁니다(A26). 검증과 승인 게이트는 도구로, 기계적인 부분은 코드로 옮깁니다(A32, A33) | 사람 승인은 스킬 문장입니다(push·PR, brief 게시, 티켓 분할안). 흐름 스킬에서 코드로 된 것은 코드 지문 스크립트 하나입니다. 도구 제한은 code-reviewer의 `tools:` 줄(쓰기 도구 이름은 없지만 `bash`와 `task`가 있고, bash를 읽기 명령에만 쓰라는 것은 본문 지시)과 플레이북 리뷰 역할의 `readonly: true`뿐이고 나머지 역할은 지시문으로만 막습니다. 선택 플레이북에는 머지 전 사람 승인 gate가 있습니다(수동 머지 전용). 예산은 두지 않기로 정했고, 반복은 승격 사다리(implementer 2회, hard-implementer, 멈춤)로 끝납니다 | 예산이 없는 것은 사용자 결정이라 그대로 둡니다(6절). 범용 쓰기 게이트(기존 테스트·보호 경로를 고치지 못하게 막는 도구 제한)가 없고 지시문뿐인 점은 글과 다릅니다. 승인 gate는 Paseo 플레이북의 머지 승인 하나가 이미 도구로 있습니다. 접으면 메인이 직접 구현하므로, 기존 테스트를 고치지 못하게 막는 장치(강화 P4, 아직 없음)가 더 필요해집니다 | `skills/in-progress/run-flow/SKILL.md:17`, `skills/in-progress/set-brief/SKILL.md:83`, `skills/in-progress/set-ticket/SKILL.md:85`, `skills/in-progress/run-flow/scripts/code_fingerprint.sh:28-38`, `extras/omp/agents/code-reviewer.md:5, :10`, `extras/paseo/playbooks/roles/ticket-reviewer/role.yaml:2`, `extras/paseo/playbooks/run-ticket.yaml:47-49`, `extras/omp/AGENTS.md:60-62`, 원칙:207, 설계:475, 강화:94 |
| 평가 | 중앙의 e2e 세트와 스킬별 작은 세트를 둡니다. 골든 사례 10개로 시작할 수 있습니다(A36). 구조를 비교할 때는 작업 완료 평가가 기준입니다(A37). 작업별로 비교하고(A44), 여러 번 돌리고(A45), 하나 접을 때마다 전후를 비교합니다(A46) | 스킬 단위 동작 사례 67개와 트리거 사례 67개가 있습니다. run-flow 사례 10개는 시작 단계 판정, 재개, 금지 동작을 보고, 1~7단계를 끝까지 채점하는 사례는 없습니다. 서브에이전트 도구를 허용한 사례는 둘뿐입니다. 실행 명령에 반복 횟수가 없고 CI는 정적 검사만 돌립니다. 흐름을 바꿀 때는 새 사례만 돌리기로 정해 두었습니다 | 접기 전후를 비교할 기준선이 없습니다. 기존 사례 대부분은 서브에이전트를 띄울 수 없는 조건에서 돌아 위임 경로를 지나지 않습니다 **(추론)**. 지금 사례만으로는 접기의 영향을 볼 수 없습니다 | `evals/run-flow/done-brief/case.yaml:8, :11-38`, `evals/run-ticket/multi-sequential/case.yaml:8`, `evals/check-guidelines/large-repo-all/case.yaml:13`, `README.md:144-149`, `.github/workflows/check.yml:19-22`, 설계:29 |
| 모델 교체 대응 | 단순한 루프는 다음 모델로 옮기기 쉽습니다(A23). 굳은 멀티 에이전트 구조는 새 모델이 더 많은 일을 하는 것을 막습니다(A24) | omp 설정의 역할 12개에 모델과 effort가 고정돼 있고, reviewer와 security-reviewer의 모델, 대체 체인 4개가 따로 있습니다. root-cause는 모델 id가 파일에 직접 적혀 있습니다. Paseo 프로필 18개, 플레이북 역할 2개, Orca·Paseo 등록 문구의 표에도 모델이 적혀 있습니다. 같은 티켓 구현 워커가 Orca에서는 xhigh, Paseo에서는 medium입니다. 벤치마크 수치가 설정 주석에 들어 있습니다 | 모델이 바뀌면 설정, 에이전트 파일, 프로필, 등록 문구, 문서를 함께 고쳐야 합니다 **(추론)**. 2026-11-25 결정에 따라 역할별 고정을 없애고 사용자 설정과 환경에서 고릅니다 | `extras/omp/config.yml:5-42, :48-53, :55-67`, `extras/omp/agents/root-cause.md:4`, `extras/paseo/config.json:6-168`, `extras/paseo/playbooks/roles/ticket-reviewer/role.yaml:3`, `extras/orca/register.md:37-41`, `extras/paseo/register.md:36-40`, `docs/omp-orchestration.md:50` |

## 3. 위임 처리 표

처리는 다섯입니다. **접기**는 메인 세션이 직접 하도록 바꾸는 것, **남기기**는 1절의 형태로 남기는 것, **삭제**는 부르는 곳이 없어 지우기만 하는 것입니다. **선택**은 기본 흐름에서는 빠지고, 사용자가 고를 때만(워커 도구 절차를 지정하거나 등록했을 때) 쓰는 것입니다(결정 8). **범위 밖**은 개발 플로우가 아니어서 이 계획이 다루지 않는 것입니다(결정 7). "측정 뒤 확정"은 5절의 비교에서 접은 쪽이 낮으면 남길 후보라는 뜻입니다. 단계는 4절의 번호입니다.

### 가. 스킬 안의 위임 지점 (22곳)

| # | 지점 | 근거 | 처리 | 잃는 것 | 대응 | 단계 |
|---|---|---|---|---|---|---|
| R1 | run-flow 3단계: set-brief의 입력 수집, 초안, 냉독을 서브에이전트에 맡김 | `skills/in-progress/run-flow/SKILL.md:103`, `skills/in-progress/run-flow/references/brief-stage.md:3, :13-26` | 접기 | 초안과 냉독 결과가 메인 컨텍스트에 남습니다. 저하를 측정한 적은 없습니다 | 메인이 초안을 씁니다. 초안은 지금처럼 저장소 밖 임시 파일에, 냉독 결과는 `.review.md` 파일에 둡니다. 구체화 대화를 그대로 쓰므로 기록만 넘기던 인계가 없어지고(A21), 서브에이전트 안에서 냉독을 다시 띄우는 중첩도 없어집니다 | P1-1 |
| S1 | set-brief 4단계: 냉독 독자 3명을 병렬로 띄움 | `skills/in-progress/set-brief/SKILL.md:57-73` | **남기기** (2026-11-25 결정) | 없음 | 메인이 직접 띄우고, 독자는 세션 모델을 따릅니다 | P1-1 |
| R2 | run-flow 5단계: 구현을 새 컨텍스트의 워커나 서브에이전트에 맡김 | `skills/in-progress/run-flow/SKILL.md:122` | 접기 | 대화 없이 brief와 티켓만으로 구현되는지가 구현 과정에서 드러나던 것, 티켓마다 새 컨텍스트 | brief가 혼자 읽히는지는 냉독(S1)이 계속 봅니다. 티켓마다 완료 기록을 파일에 남기고, 4단계 뒤의 새 세션 선택(`skills/in-progress/run-flow/SKILL.md:111`)을 그대로 둡니다. 긴 흐름의 저하는 E10으로 잽니다 | P1-3 |
| R3 | run-flow 7단계: 규칙이 정했으면 PR 본문을 에이전트에 맡김 | `skills/in-progress/run-flow/references/pr-stage.md:4` | 접기 | 거의 없습니다 | 메인이 같은 입력(brief, `git diff --stat`, 완료 기록, 리뷰 기록)으로 씁니다. 사용자 확인(`skills/in-progress/run-flow/references/pr-stage.md:5`)은 그대로 둡니다 | P1-2 |
| R4 | run-flow 6단계 "고치기": run-ticket의 리뷰 단계를 다시 실행 | `skills/in-progress/run-flow/references/merge-stage.md:16` | 유지 (위임이 아니라 스킬을 다시 부르는 것) | 없음 | 리뷰 단계가 "메인의 리뷰와 교차 리뷰 호출"로 바뀌는 것만 따라갑니다 | P1-4 |
| R5 | run-flow 5단계: 레포 규칙이 지정한 별도 티켓 실행 스킬을 부릅니다. 불러올 수 없는 User-invoked 스킬이면 멈추고, 사용자가 그 스킬을 따로 실행한 뒤 brief를 인자로 run-flow를 다시 실행하도록 안내합니다 | `skills/in-progress/run-flow/SKILL.md:133`, `docs/skills/run-flow.md:73` | 열린 질문 Q11 | 분기를 빼면 레포가 티켓 실행 절차를 바꿀 수 있는 확장 지점을 잃습니다 | 실제 구현 위임 여부는 단정하지 않습니다. 분기를 유지할 때 접기 조건을 어디까지 요구할지는 Q11에서 정합니다 | P1-3, P0-3 |
| T1 | run-ticket 3단계: 구현을 에이전트에 맡김 | `skills/in-progress/run-ticket/SKILL.md:80` | 접기 | 구현 보고를 메인이 다시 확인하던 두 번째 눈 | 4단계는 명령과 관찰로만 판정합니다. 독립된 눈은 교차 리뷰입니다 | P1-3 |
| T2 | run-ticket 4단계: 화면 기준을 UI 확인 에이전트에 맡김 | `skills/in-progress/run-ticket/SKILL.md:90` | 접기 (측정 뒤 확정) | 비전 모델과 브라우저 도구, 구현과 분리된 확인(A11, A12) | 메인에 브라우저나 스크린샷 도구가 있으면 직접 확인하고, 없으면 같은 줄의 기존 규칙대로 "확인 못 한 것"에 적습니다. E11에서 낮게 나오면 남길 후보 1순위입니다 | P1-5 |
| T3 | run-ticket 4단계: 실패 처리(다시 맡기기, 다른 에이전트로 올리기) | `skills/in-progress/run-ticket/SKILL.md:92`, `extras/omp/AGENTS.md:60-62` | 접기 | 다른 모델과 새 컨텍스트로 다시 해 보는 것 | 같은 루프에서 원인을 정리하고 다시 합니다. 최초 시도를 포함해 3회에서 멈추고(설계:25), `- 멈춘 이유:`에 적은 뒤 티켓 재분할을 묻습니다. 더 강한 모델이 필요하면 사용자가 세션 모델을 바꿔 상태 파일로 이어 갑니다 | P1-3 |
| T4 | run-ticket 5단계: 세 리뷰를 서브에이전트로 함께 띄움 | `skills/in-progress/run-ticket/SKILL.md:96` | 접기 | 리뷰가 동시에 돌던 시간 이득 | 코드 리뷰와 규칙 검사는 메인이 차례로 하고, 교차 리뷰만 부릅니다 | P1-4 |
| T5 | run-ticket 5단계: 리뷰 스킬의 하위 리뷰를 에이전트에 맡김 | `skills/in-progress/run-ticket/SKILL.md:98-104` | 접기 (외부 스킬의 하위 위임을 기본 경로에서 어떻게 둘지는 Q9) | 리뷰 스킬을 다른 회사 모델로 돌리던 것 | 코드 리뷰는 세 분기입니다: 레포 규칙이 지정한 리뷰 스킬(`:100`), 자동 발견한 `code-review`나 `<플러그인>:code-review` 스킬(`:101`), 맞는 스킬이 없을 때의 직접 리뷰(`:102`). 앞 두 분기는 외부 스킬이 서브에이전트를 띄우게 하고, 에이전트 규칙이 정한 에이전트로 그 하위 리뷰를 띄웁니다(`:104`). 실행 주체를 메인으로 바꿔도 외부 스킬이 스스로 띄우는 하위 위임은 두 분기 모두에 남습니다. 교차 리뷰의 기준 목록에 "작업 경계와 레포 규칙 위반"을 넣고, 레포 규칙이 정한 리뷰 스킬은 메인이 실행합니다. 그 스킬의 하위 위임을 허용할지, 위임하지 않는 실행 모드(없으면 직접 리뷰)로 돌릴지는 정하지 않고 Q9로 올립니다 | P1-4 |
| T6 | run-ticket 5단계: 교차 리뷰 | `skills/in-progress/run-ticket/SKILL.md:108-114` | **남기기** | 없음 | 1절의 형태로 고칩니다 | P0-2, P0-3 |
| T7 | run-ticket 5단계: 보안 리뷰를 에이전트에 맡김 | `skills/in-progress/run-ticket/SKILL.md:116` | 접기: 교차 리뷰의 조건부 기준으로 합침 (결정 5) | 보안만 보는 별도 호출 | 인증·권한·결제·개인정보 변경이면 교차 리뷰 기준에 보안을 넣습니다. E5에서 낮게 나오면 같은 수단을 보안 기준으로 한 번 더 부릅니다 | P1-4 |
| M1 | 여러 티켓 병렬 실행: 티켓마다 worktree의 워커 | `skills/in-progress/run-ticket/references/multi-ticket.md:36-70, :72-83` | **선택** (결정 8) | 기본 흐름에서는 병렬 처리량(A10)과 worktree 격리. 등록한 사용자는 잃지 않습니다 | 지우지 않습니다. 사용자가 고를 때만 병렬로 돌고, 아니면 메인이 차례로 합니다. 지금의 진입 조건(`skills/in-progress/run-ticket/references/multi-ticket.md:26-30`)은 명시 지정(사용자·부른 쪽)을 먼저, 레포·에이전트 규칙 등록을 다음으로 보는 PR #38의 분기이고, 이 분기를 좁히지 않고 그대로 둡니다. 결정 8의 "등록할 때만"은 사용자 선택으로만 병렬이 된다는 뜻입니다. worktree, 머지, 이어 받기, 워커 식별자, 알림 대기 절차도 이 경로에 남습니다. 워커의 모델은 고정하지 않습니다(결정 1) | P2-2 |
| M2 | 차례 실행: 티켓마다 서브에이전트 하나 | `skills/in-progress/run-ticket/references/multi-ticket.md:90` | 접기 | T1과 같습니다 | 같은 줄의 기존 폴백대로 같은 세션에서 차례로 합니다 | P1-3 |
| M3 | 통합 검증이 실패하면 원인 보고 에이전트를 부름 | `skills/in-progress/run-ticket/references/multi-ticket.md:64` | 접기 (선택 경로 안에서) | 고치지 않는 쪽의 원인 보고 | 통합 검증 실패는 병렬 머지에서만 생깁니다. 병렬 경로는 남기되(결정 8), 그 안에서 원인 보고 에이전트를 부르지 않고 메인이 직접 원인을 찾습니다 | P2-2 |
| M4 | 막는 티켓을 머지한 직후의 교차 리뷰 | `skills/in-progress/run-ticket/references/multi-ticket.md:65` | **남기기** (선택 경로 안에서) | 없음 | 병렬 경로가 남으므로(결정 8) 이 교차 리뷰도 그대로 둡니다. 1절의 형태와 모델 선택 순서를 따릅니다. 차례 실행은 끝에 통합 리뷰를 한 번 합니다(`skills/in-progress/run-ticket/references/multi-ticket.md:97`). 이른 리뷰를 차례 실행에도 둘지는 E2와 E4 결과로 정합니다. 지금 허용하는 `- 교차 리뷰: 건너뜀 (<이유>)` 기록(`skills/in-progress/run-ticket/references/multi-ticket.md:65`)과 그 줄로 재개를 판단하는 규칙(`:52`)은 P0-3에서 함께 바꿉니다 | P0-2, P0-3, P2-2 |
| M5 | 사용자 승인이 필요한 레포: 서브에이전트에는 제안 diff까지만 맡김 | `skills/in-progress/run-ticket/references/multi-ticket.md:95` | 접기 | 없음 | 메인이 직접 묻고 적용하므로 이 제약이 없어집니다 | P1-3 |
| M6 | 교차 리뷰 워커 | `skills/in-progress/run-ticket/references/multi-ticket.md:84`, `skills/in-progress/run-ticket/SKILL.md:111` | **남기기** | 없음 | 교차 리뷰를 부르는 수단 가운데 하나로 남깁니다 | P0-2, P2-2 |
| F1 | framing-problems: 넓은 조사를 백그라운드 서브에이전트로 돌림 | `skills/productivity/framing-problems/SKILL.md:17` | 접기 | 조사와 질문이 겹치던 시간, 원시 파일 읽기가 메인 밖에 있던 것 | 같은 줄의 기존 폴백대로 직접 조사합니다. 출처 표기 규칙은 그대로 둡니다. 요약이 아닌 원본을 메인이 봅니다(A21) | P2-1 |
| G1 | check-guidelines: 파일이 100개를 넘으면 구역마다 서브에이전트 | `skills/engineering/check-guidelines/SKILL.md:50` | 접기 (측정 뒤 확정) | 큰 범위를 동시에 검사하는 것, 메인 컨텍스트 보호 | 구역을 차례로 검사하고 구역마다 결과를 보고서에 바로 적습니다. 승인 절차는 그대로 둡니다. run-flow 경로에서는 바꾼 파일만 검사하므로(`skills/in-progress/run-ticket/SKILL.md:106`) 이 지점을 거의 지나지 않습니다 **(추론)** | P2-1 |
| B1 | building-skills: 평가 실행을 깨끗한 컨텍스트의 서브에이전트로 띄움 | `skills/productivity/building-skills/SKILL.md:79-80`, `skills/productivity/building-skills/references/evaluation.md:92` | **범위 밖** (결정 7) | 없음 | 개발 플로우가 아니라 스킬을 재는 도구이므로 그대로 둡니다. 접으면 평가가 성립하지 않습니다. 스킬을 쓴 세션이 스스로 실행하면 엄밀하지 않다고 스킬이 적어 두었습니다 | 없음 |
| B2 | building-skills: 채점을 서브에이전트에 맡겨도 됨 | `skills/productivity/building-skills/references/evaluation.md:124` | **범위 밖** (결정 7) | 없음 | 그대로 둡니다. 직접 채점도 이미 허용돼 있습니다 | 없음 |

위임이 없는 스킬은 analyzing-requirements, set-ticket, write-docs, prompt-builder, set-guidelines입니다. 도구 선택 실패나 지침 충돌(A11)을 이유로 적은 위임은 스킬 안에 없습니다.

### 나. omp 역할 (`extras/omp/`)

| 역할 | 정의 | 지금 모델 | 처리 | 잃는 것 | 대응 | 단계 |
|---|---|---|---|---|---|---|
| 메인 세션 | `extras/omp/config.yml:7` | Opus 5.5 high | 남기기 (단일 루프의 주체) | 없음 | 모델 줄은 레포가 배포하는 값에서 뺍니다 | P2-3 |
| brief-writer | `extras/omp/agents/brief-writer.md:2-5` | `@brief` | 접기 | 문서용 높은 effort, 메인 컨텍스트 절약 | R1 | P1-1 |
| cold-reader | `extras/omp/agents/cold-reader.md:2-4` | `@task` | **남기기** | 없음 | `model:` 줄을 빼 세션 모델을 따르게 합니다. 띄우는 쪽이 brief-writer에서 메인으로 바뀝니다(`extras/omp/AGENTS.md:31, :51`) | P1-1 |
| implementer | `extras/omp/agents/implementer.md:2-4` | `@task` | 접기 | 티켓마다 새 컨텍스트 | T1, M2 | P1-3 |
| hard-implementer | `extras/omp/agents/hard-implementer.md:2-5` | `@slow`와 자문 | 접기 | 더 강한 모델로 올리는 것 | T3 | P1-3 |
| advisor (역할) | `extras/omp/config.yml:41-46` | Opus 5.5 xhigh | 접기 | 막혔을 때의 다른 시각 | hard-implementer와 함께 지웁니다 | P1-3 |
| test-writer | `extras/omp/agents/test-writer.md:2-4` | `@task` | 삭제 | 거의 없습니다. 스킬에 부르는 곳이 없습니다 | 테스트는 구현이 함께 씁니다(`skills/in-progress/run-ticket/SKILL.md:82`) | P1-3 |
| root-cause | `extras/omp/agents/root-cause.md:2-4` | 모델 id 직접 | 접기 | M3 | M3 | P2-2 |
| ui-checker | `extras/omp/agents/ui-checker.md:2-4` | `@vision` | 접기 (측정 뒤 확정) | T2 | T2 | P1-5 |
| doc-writer | `extras/omp/agents/doc-writer.md:2-4` | `@smol` | 접기 | 낮은 모델로 아끼던 비용 | R3 | P1-2 |
| code-reviewer | `extras/omp/agents/code-reviewer.md:2-6` | `@review`, `tools:`에 쓰기 없음 | **남기기**: 교차 리뷰 에이전트 하나로 바꿈 | 없음 | 쓰기 도구 이름이 없는 `tools:` 줄을 가진 유일한 파일이라 omp의 교차 리뷰 수단으로 씁니다. `spawns:`를 빼고 모델은 사용자 설정을 따르게 합니다. 다만 `tools:`에 하위 에이전트를 띄우는 `task`와 `bash`가 있고(`extras/omp/agents/code-reviewer.md:5`), 읽기 전용은 bash를 저장소를 바꾸지 않는 명령에만 쓰라는 본문 지시(`:10`)라서 도구로 강제된 경계라고 할 수 없습니다. `task`와 쓰기 가능한 `bash`를 둘지, 실제 읽기 전용 수단이 없을 때 어떻게 할지는 Q9에서 함께 정합니다 | P0-2, P1-4 |
| reviewer (bundled) | `extras/omp/AGENTS.md:37`, `extras/omp/config.yml:51` | `@review` | 접기 (code-reviewer와 합침) | 버그만 보고하는 고정 형식 | 1절의 반환 형식으로 바꿉니다. 둘을 나눈 이유는 형식 차이였습니다(`extras/omp/AGENTS.md:44`) | P1-4 |
| security-reviewer (bundled) | `extras/omp/AGENTS.md:39`, `extras/omp/config.yml:53` | Opus 5.5 high 고정 | 접기 (결정 5) | T7 | T7. 접은 뒤에도 이 역할을 Claude로 두면 메인이 Claude일 때 같은 회사가 됩니다 | P1-4 |
| scout (bundled) | `extras/omp/AGENTS.md:29`, `extras/omp/config.yml:27-28` | `smol` | 접기 | 탐색 출력이 메인 밖에 있던 것, 낮은 모델 비용 | 메인이 직접 찾습니다. 스킬에 이름으로 부르는 곳이 없습니다 | P2-1 |
| `commit` 역할 | `extras/omp/config.yml:31-32` | Haiku 5.5 medium | 삭제 | 없음. 규칙은 이미 메인이 커밋 메시지를 쓴다고 합니다(`extras/omp/AGENTS.md:52`) | 없음 | P2-3 |

### 다. Orca·Paseo의 워커, 프로필, 플레이북

| 대상 | 정의 | 처리 | 잃는 것 | 대응 | 단계 |
|---|---|---|---|---|---|
| Orca 티켓 구현 워커 | `extras/orca/worker-procedure.md:28-34` | **선택** (결정 8) | 없음 | M1. 절차를 지우지 않고 등록했을 때만 씁니다. 워커의 모델은 이미 "에이전트 규칙이 정했으면 그것, 없으면 모델 인자를 빼고 알림"(`extras/orca/worker-procedure.md:32`)이라 결정 1과 맞습니다 | P2-2 |
| Orca 교차 리뷰 워커 | `extras/orca/worker-procedure.md:72-74` | **남기기** | 없음 | "구현한 모델이 Claude면 Codex, 그 밖이면 Claude Code"라는 고정을 "설치된 에이전트 가운데 다른 회사 모델을 쓰는 것"으로 바꿉니다 | P0-2 |
| Orca 등록 문구의 모델 표 | `extras/orca/register.md:35-41` | 삭제 | 권장값 안내 | 자리 표시만 있는 문구(`extras/orca/register.md:29-33`)를 남깁니다 | P0-2 |
| Paseo `ticket-worker` | `extras/paseo/config.json:70-78` | **선택** (결정 8) | 없음 | M1. 병렬 경로가 쓰는 프로필이라 남깁니다. 지금 적힌 provider와 모델(`extras/paseo/config.json:73-76`)은 빼고 사용자 설정과 환경을 따르게 합니다(결정 1). 프로필을 예시로 배포할지는 Q7과 함께 정합니다 | P2-2 |
| Paseo `cross-review` | `extras/paseo/config.json:97-105` | **남기기** (프로필을 계속 배포할지는 Q7) | 없음 | 절차가 이미 "규칙의 프로필, 규칙의 대체 모델, 저장된 프로필의 설명, 쓸 수 있는 모델 조회" 순서로 고릅니다(`extras/paseo/worker-procedure.md:66`) | P0-2 |
| Paseo 등록 문구의 모델 표 | `extras/paseo/register.md:34-40` | 삭제 | 권장값 안내 | 자리 표시만 있는 문구(`extras/paseo/register.md:29-32`)를 남깁니다 | P0-2 |
| Paseo `skill-review` | `extras/paseo/config.json:106-114` | 접기 | T5 | T5 | P1-4 |
| Paseo `security-review` | `extras/paseo/config.json:115-123` | 접기 (결정 5) | T7 | T7 | P1-4 |
| Paseo `ui-check` | `extras/paseo/config.json:124-132` | 접기 (측정 뒤 확정) | T2 | T2 | P1-5 |
| Paseo `brief-draft` | `extras/paseo/config.json:43-51` | 접기 | R1 | R1 | P1-1 |
| Paseo `cold-read` | `extras/paseo/config.json:52-60` | 삭제 (프로필만) | Paseo 에이전트로 냉독을 띄우는 길 | 냉독 독자는 세션의 서브에이전트로 띄우고 세션 모델을 따릅니다. 지금은 이 프로필이 medium, omp의 cold-reader가 `@task`(xhigh)로 서로 다릅니다 | P1-1 |
| Paseo `pr-body` | `extras/paseo/config.json:133-141` | 접기 | R3 | R3 | P1-2 |
| Paseo `hard-implementer` | `extras/paseo/config.json:88-96` | 삭제 | 없음. Paseo 워커 절차와 `multi-ticket.md`에 이 프로필로 올리는 단계가 없습니다 | 없음 | P1-3 |
| Paseo `proposal-diff` | `extras/paseo/config.json:79-87` | 삭제 | M5 | M5 | P1-3 |
| Paseo `root-cause` | `extras/paseo/config.json:25-33` | 접기 | M3 | M3 | P2-2 |
| Paseo `locate`, `behavior-checklist`, `impact` | `extras/paseo/config.json:7-15, :16-24, :34-42` | 삭제 | 조사 출력이 메인 밖에 있던 것. 스킬과 절차가 이름으로 부르지 않습니다 | 메인이 직접 조사합니다 | P2-1 |
| Paseo `change-doc`, `advisor`, `env-setup` | `extras/paseo/config.json:61-69, :142-150, :151-159` | 삭제 | 플로우 밖에서 쓰던 편의 프로필 | 없음 | P2-3 |
| Paseo `connector` | `extras/paseo/config.json:160-167` | 삭제 제안 (Q7) | omp 세션에서 Claude Code 전용 커넥터의 자료를 읽는 길(A11에 해당) | 사용자가 자료를 파일로 넘기거나 Claude Code에서 1단계를 실행합니다 | P2-3 |
| 플레이북 `ticket-implementer` | `extras/paseo/playbooks/roles/ticket-implementer/role.yaml:1-3`, `extras/paseo/playbooks/run-ticket.yaml:15-29` | 삭제 | 사람이 Playbooks 패널에서 티켓 하나를 돌리는 선택 기능 | run-ticket을 직접 실행합니다 | P2-3 |
| 플레이북 `ticket-reviewer` | `extras/paseo/playbooks/roles/ticket-reviewer/role.yaml:1-3`, `extras/paseo/playbooks/run-ticket.yaml:31-49` | 삭제 | 구현과 리뷰의 되돌림 루프(최대 2회), 머지 승인 gate | 없음 | P2-3 |

## 4. 우선순위 변경안

### 공통 규칙

- 한 번에 하나만 접고, 접을 때마다 5절의 비교를 한 뒤 다음으로 갑니다(A43, A46).
- 단계마다 brief 하나로 만들어 진행합니다(강화:44의 방식).
- 끝나는 조건은 강화 계획의 것을 그대로 씁니다(강화:35-40). 스킬 동작이 바뀌면 `docs/skills/<스킬>.md`와 영어판을 같은 커밋에서 고치고(`.claude/CLAUDE.md:27`), `skills/`를 바꾸면 `.claude-plugin/plugin.json` 버전을 올리고(`.claude/CLAUDE.md:21`), `extras/`를 바꾸면 해당 설정 문서를 고치고(`.claude/CLAUDE.md:50`), `scripts/check.py`를 통과시킵니다.
- eval이 도는 동안에는 `skills/`를 고치지 않습니다(`.claude/CLAUDE.md:85`).

### 순서와 의존

| # | 항목 | 선행 | 비교에 쓰는 사례 |
|---|---|---|---|
| P0-1 | e2e 골든 사례와 기준선 | 없음 | 전부 |
| P0-2 | 교차 리뷰를 도구 호출 형태로 고정하고 리뷰 모델 고정을 풂 | P0-1 | E4, E5 |
| P0-3 | 교차 리뷰 건너뜀을 없애고, 다른 회사 모델이 없으면 같은 회사 대체를 기록하고 계속함 | P0-2 | E9, run-ticket 기존 사례 7개, 선택 경로의 E2-P |
| P1-1 | brief 초안 접기 | P0-1 | E1, E2, E6 |
| P1-2 | PR 본문 접기 | P0-1 | E3 |
| P1-3 | 구현과 실패 승격 접기 | P0-2, P0-3 | E1, E2, E7, E8, E10 |
| P1-4 | 리뷰 역할 합치기 | P0-3, P1-3 | E4, E5 |
| P1-5 | 화면 확인 접기 | P1-3 | E11 |
| P2-1 | 조사 위임 접기 | P0-1 | framing-problems와 check-guidelines의 기존 사례, E1 |
| P2-2 | 병렬 워커를 선택 경로로 정리 | P1-3, P1-4 | E2, E8, 선택 경로의 E2-P, E8-P |
| P2-3 | 남은 프로필·플레이북·모델 설정 정리, 설계 문서 표시 | 앞 단계 전부 | 전부 |

P0는 아무것도 접지 않습니다. 재는 수단을 만들고, 남길 것의 모양을 먼저 고정합니다. 글의 순서(평가, 남길 것을 도구 형태로, 하나씩 통합)와 같습니다(A36, A40, A41, A43). P1은 run-flow가 매번 지나는 위임을 위험이 낮은 것부터 접습니다. P2는 선택 기능이거나 고칠 범위가 넓은 것입니다. 병렬 워커는 지우지 않고 사용자가 고를 때만 쓰는 선택 경로로 정리하는 단계라(결정 8), 기본 흐름이 정해진 뒤 마지막에 둡니다.

### P0-1. e2e 골든 사례와 기준선

- **무엇을**: 5절의 E1~E10을 `evals/run-flow/` 아래에 `e2e-` 접두사로 더합니다. 서브에이전트 도구를 허용해 지금의 위임 경로가 실제로 돌게 합니다. 턴 상한 때문에 1~7단계를 한 사례에 넣지 못하면, E2가 끝난 작업 트리와 상태 파일을 그대로 E3의 입력으로 쓰는 분할 연속 사례 E2→E3를 함께 둡니다(5절 표 아래). 그다음 스킬과 extras를 건드리지 않은 `0c50de8`에서 5절대로 돌려 기준선을 남깁니다.
- **바꿀 파일**: `evals/run-flow/e2e-<이름>/case.yaml`, `evals/run-flow/e2e-<이름>/fixture.sh`(새로 만듦). 분할 연속 사례는 E3 변형의 `fixture.sh`가 E2 실행 결과 폴더에서 작업 트리와 상태 파일을 복사해 시작합니다. 결과 폴더는 git에서 빠져 있으므로(`.gitignore:2`), 사례별 비교 표는 측정 기록 문서 `docs/context/design/2026-11-25-fold-measurements.md`(새로 만듦)에 따로 남깁니다.
- **위험**: e2e 한 번의 턴 수와 비용을 모릅니다. 지금 가장 긴 사례가 60턴입니다(`evals/run-ticket/multi-sequential/case.yaml:7`). 사용자 답을 프롬프트에 미리 주는 방식(`evals/set-brief/save-docs/case.yaml:8`)이 여러 단계를 잇는 흐름에서도 통하는지 모릅니다. 기준선의 통과율이 낮거나 흔들리면 접기 전에 사례부터 고칩니다.

### P0-2. 교차 리뷰를 도구 호출 형태로 고정하고 리뷰 모델 고정을 풂

- **무엇을**: run-ticket 5단계의 교차 리뷰를 1절의 형태(넘기는 것, 읽기 전용, 반환 형식, 메인의 검증, 모델 선택 순서, 수행 모델 기록)로 고쳐 씁니다. 다른 리뷰 역할은 아직 그대로 둡니다. 리뷰 모델을 id로 적은 곳은 아래 "모델 고정 풀기" 표대로 풉니다.
- **바꿀 파일**:
  - `skills/in-progress/run-ticket/SKILL.md`(108~114행)
  - `skills/in-progress/run-ticket/references/multi-ticket.md`(84행의 "교차 리뷰 워커" 항목)
  - `extras/omp/agents/code-reviewer.md`(교차 리뷰 에이전트로 설명과 보고 형식을 바꿈)
  - `extras/omp/AGENTS.md`(37행, 44~46행, 53행)
  - `extras/omp/config.yml`(37~39행)
  - `extras/orca/worker-procedure.md`(74행), `extras/orca/register.md`(25~41행)
  - `extras/paseo/worker-procedure.md`(66행), `extras/paseo/register.md`(25~40행), `extras/paseo/config.json`(97~105행)
  - `docs/skills/run-ticket.md`, `docs/omp-orchestration.md`, `docs/orca-orchestration.md`, `docs/paseo-orchestration.md`와 `docs/en/`의 같은 파일
- **위험**: omp에서 서브에이전트를 부를 때 모델을 그때 넘길 수 있는지 모릅니다. 넘길 수 없으면 `review` 역할 한 줄이 사용자 설정으로 남아야 합니다. 그 값이 비어 있으면 run-ticket은 1절의 순서대로 환경 조회(3번)로 다른 회사 모델을 고르고, 고를 수 없으면 4번의 같은 회사 대체로 기록하고 계속합니다(결정 6, 아래 "모델 고정 풀기"의 `review` 행과 같음). 다만 모델을 그때 넘길 수 없는 호스트에서는 환경 조회로 고른 모델을 서브에이전트에 줄 수 없어, 빈 `review` 값이면 교차 리뷰가 매번 같은 회사 대체로 떨어집니다. 그래서 설치 문서가 먼저 고르게 안내합니다. 조회 명령은 이미 문서에 있습니다(`docs/omp-orchestration.md:41`).

### P0-3. 교차 리뷰 건너뜀을 없애고 같은 회사 대체를 기록하게 함

- **무엇을**: 리뷰를 건너뛰는 경로를 없앱니다. "모두 안 되면 건너뛰고 보고에 적는다"(`skills/in-progress/run-ticket/SKILL.md:112`)를 "다른 회사 모델의 수단이 모두 안 되면 같은 회사 모델의 새 컨텍스트 리뷰로 대체한다"로 바꿉니다. "교차 리뷰 건너뜀(같은 회사 모델)" 보고(`skills/in-progress/run-ticket/SKILL.md:114`)는 "교차 리뷰 대체(같은 회사 모델 <모델 이름>)"로 바꿔, 대체한 사실과 수행 모델을 완료 기록과 상태 파일 `- 교차 리뷰 모델:`에 적고 흐름을 계속하게 합니다(결정 6). 대체 리뷰도 1절의 넘기는 것, 읽기 전용, 반환 형식, 메인의 검증을 그대로 따릅니다. `review` 대체 체인(Opus)은 지웁니다(강화:136). 하네스가 모델을 조용히 바꾸면 대체가 기록되지 않고, 모델 id를 레포가 정하는 것도 결정 1과 맞지 않기 때문입니다. 대체는 스킬이 명시적으로 하고 적습니다.
- **바꿀 파일**:
  - `skills/in-progress/run-ticket/SKILL.md`(112행, 114행)
  - `skills/in-progress/run-ticket/references/multi-ticket.md`(52행, 65행. 선택 경로의 막는 티켓 교차 리뷰도 건너뛰지 않게 합니다. 65행의 기록은 ``- 교차 리뷰: 완료 (`<머지 커밋 해시>`, <수행한 모델>)``이나 ``- 교차 리뷰: 대체 (`<머지 커밋 해시>`, 같은 회사 모델 <수행한 모델>)``만 남기고 `- 교차 리뷰: 건너뜀 (<이유>)`를 지웁니다. 52행의 재개 판정은 `완료`나 `대체` 줄이 있어야 리뷰가 끝난 것으로 보고, 막힌 티켓의 워커를 띄우기 전에 그 줄을 확인합니다. P0-3 전에 남은 `건너뜀` 기록은 리뷰하지 않은 것으로 봅니다. 막힌 티켓의 워커를 아직 띄우지 않았으면 막는 티켓의 교차 리뷰부터 다시 하고, 이미 띄웠거나 머지했으면 통합 리뷰(`:69`)가 그 범위를 함께 본다고 완료 기록에 적습니다)
  - `extras/omp/config.yml`(60~62행)
  - `docs/orca-orchestration.md`(71행), `docs/paseo-orchestration.md`(122행), `docs/omp-orchestration.md`(74행)와 영어판
  - `docs/skills/run-ticket.md`(35행의 "모두 없으면 건너뛰고 보고에 적습니다")와 `docs/en/skills/run-ticket.md`(35행의 "it skips the cross review and says so in the report"). P0-2도 이 파일을 고치지만, 건너뛰기 설명을 지우는 시점은 P0-3입니다
  - eval. 리뷰용 새 컨텍스트 수단(서브에이전트 도구)은 허용하고, 구현을 맡기지 않았는지는 P1-3에서 따로 채점합니다(P1-3 참조)
    - `evals/run-ticket/review-fallback-no-skill/case.yaml`(3행의 설명, 10행의 `allowed_tools`에 `Agent`를 더함, 28~39행. 지금은 건너뛴 이유를 적고 done으로 바꾸는 것을 PASS로 판정함. 교차 리뷰를 했거나 같은 회사 새 컨텍스트 리뷰로 대체하고 대체를 적은 것만 PASS로, 건너뛴 것은 FAIL로 고침)
    - 5단계를 지나 done을 단언하는 나머지 기존 사례 `evals/run-ticket/mark-done/case.yaml`(8행 `allowed_tools`에 `Agent`를 더함, 22~26행 `reviewed` 판정에 교차 리뷰나 대체 기록을 더함), `evals/run-ticket/no-ticket-brief-done/case.yaml`(8행, 완료 기록 판정에 같은 조건). 두 사례와 `review-fallback-no-skill`의 `fixture.sh`는 고치지 않습니다. fixture에 교차 리뷰 수단을 정한 규칙이 없어 4번의 같은 회사 대체를 지나는 것이 판정 대상입니다. 리뷰 호출이 늘어 `max_turns: 30`이 모자라면 턴 상한을 올립니다
    - `evals/run-ticket/multi-sequential/case.yaml`(25~29행 `one-integrated-review`에 교차 리뷰나 대체 기록을 더함. 8행의 `Agent`는 남김)
    - `evals/run-ticket/prior-artifact/`, `scratch-brief/`는 완료를 단언하지 않으므로 `allowed_tools`에 `Agent`만 더하고 판정은 그대로 둡니다. `unfinished-changes/`는 구현 전 질문에서 끝나(`max_turns: 10`) 5단계를 지나지 않습니다 **(추론)**
    - `evals/run-flow/e2e-no-cross-reviewer/case.yaml`, `fixture.sh`(E9, 새로 만듦). 다른 회사 모델은 막고(fixture 규칙에 교차 리뷰 수단이 없고, Orca·Paseo 절차를 지정·등록하지 않으며, eval 환경에 다른 회사 provider를 두지 않음), 같은 회사 모델로 새 컨텍스트를 띄울 `Agent`는 허용합니다. eval 러너에서 다른 회사 모델을 확실히 막을 수 있는지는 미확인입니다(7절)
- **위험**:
  - 다른 회사 모델이 없는 환경(플러그인만 설치)에서는 흐름이 멈추지 않는 대신, 독립된 눈이 없는 채로 6단계에 갑니다. P1-3 뒤에는 교차 리뷰가 유일한 독립 검증이므로, 그 환경의 사용자는 완료 기록의 대체 표시를 보고 판단해야 합니다. 대체 표시가 PR 본문까지 이어지는지는 E3에서 봅니다(PR 본문은 리뷰 기록을 입력으로 씁니다).
  - eval 영향: eval 환경에 다른 회사 모델이 없으면 run-ticket 사례는 같은 회사 대체로 지나가므로, 티켓이 done이 되는 것을 단언하는 기존 사례는 멈춤 때문에 깨지지 않습니다. 다만 대체 리뷰도 새 컨텍스트를 띄워야 하는데, run-ticket 사례 7개 가운데 서브에이전트 도구를 허용한 것은 `multi-sequential` 하나입니다(`evals/run-ticket/multi-sequential/case.yaml:8`, 나머지는 `allowed_tools`에 `Agent`가 없음). 5단계를 지나는 사례는 위 파일 목록대로 허용 도구에 서브에이전트 도구를 더하고 판정을 고칩니다. 새 컨텍스트를 하나도 띄울 수 없는 환경의 동작은 결정 6이 다루지 않았으므로 Q10으로 올렸고, Q10이 정해질 때까지 그 조건의 사례는 만들지 않습니다.
  - 2026-11-20 결정의 "쓸 수 없으면 리뷰 실패, 수락하지 않음"(강화:13, :144)을 결정 6이 바꿉니다(6절).

### P1-1. brief 초안 접기 (R1, brief-writer, `brief-draft`, `cold-read`)

- **무엇을**: run-flow 3단계에서 set-brief의 모든 단계를 메인이 합니다. 냉독 독자는 메인이 직접 띄웁니다. 초안을 저장소 밖 임시 파일에 두는 규칙과 냉독 결과를 `.review.md`에 남기는 규칙(`skills/in-progress/run-flow/references/brief-stage.md:28-31`)은 그대로 둡니다. set-brief의 SKILL.md는 고치지 않습니다.
- **바꿀 파일**:
  - `skills/in-progress/run-flow/SKILL.md`(103행)
  - `skills/in-progress/run-flow/references/brief-stage.md`(3행, 11~26행)
  - `extras/omp/agents/brief-writer.md`(삭제), `extras/omp/agents/cold-reader.md`(4행의 `model:`)
  - `extras/omp/AGENTS.md`(30~31행, 51행), `extras/omp/config.yml`(10~11행)
  - `extras/paseo/config.json`(43~60행)
  - `docs/skills/run-flow.md`(40행), `docs/omp-orchestration.md`, `docs/paseo-orchestration.md`(85~86행, 104행)와 영어판
- **위험**: 독자 3명의 답이 메인 컨텍스트에 들어오고, 두 번째 검증까지 가면 두 배가 됩니다. 메인은 대화를 알고 있어, 대화에만 있던 내용을 brief에서 빠뜨려도 스스로 알아채기 어렵습니다. 이것을 잡는 것이 냉독이므로 E6에서 냉독이 실제로 불렸는지를 함께 봅니다.

### P1-2. PR 본문 접기 (R3, doc-writer, `pr-body`)

- **무엇을**: 메인이 PR 본문을 씁니다. diff 전문 대신 변경 파일 목록과 필요한 파일만 읽는 문장은 남깁니다.
- **바꿀 파일**: `skills/in-progress/run-flow/references/pr-stage.md`(4행), `extras/omp/agents/doc-writer.md`(삭제), `extras/omp/AGENTS.md`(17행, 40행, 54행), `extras/paseo/config.json`(133~141행), `docs/skills/run-flow.md`(44행), `docs/omp-orchestration.md`와 영어판
- **위험**: 낮습니다. 긴 흐름 끝에서 쓰므로 본문에 리뷰의 고치지 않은 지적이 빠지는지를 E3에서 봅니다.

### P1-3. 구현과 실패 승격 접기 (R2, T1, T3, M2, M5, implementer, hard-implementer, advisor, test-writer)

- **무엇을**: 메인이 티켓을 차례로 직접 구현합니다. 실패하면 같은 루프에서 원인을 정리하고 다시 하며, 최초 시도를 포함해 3회에서 멈춥니다. implementer에 딸린 승격 사다리와 자문은 implementer가 없으면 성립하지 않으므로 함께 접습니다. "에이전트 하나에는 목적 하나" 문단(`extras/omp/AGENTS.md:23`)을 지웁니다. "맥락을 잃는 분리는 하지 않습니다"(`extras/omp/AGENTS.md:25`)는 남깁니다.
- 별도 티켓 실행 스킬 분기(R5)를 그대로 두면 구현 위임 금지와 P0-3의 교차 리뷰 조건을 충족하는지는 그 스킬에 달려 있습니다. 기본 경로에서 이 조건을 요구할지는 Q11에서 정합니다.
- **바꿀 파일**:
  - `skills/in-progress/run-flow/SKILL.md`(10행의 조정자 선언, 122행, 134행의 "시도한 에이전트와 횟수"와 승격 언급)
  - `skills/in-progress/run-ticket/SKILL.md`(3행의 설명, 22행, 80행, 92행)
  - `skills/in-progress/run-ticket/references/multi-ticket.md`(17행, 86~100행)
  - `skills/in-progress/set-ticket/SKILL.md`(14행. 크기 기준은 두고 근거 문장만 고침)
  - `extras/omp/AGENTS.md`(3행, 23행, 32~33행, 35행, 42행, 50행, 56~62행)
  - `extras/omp/agents/implementer.md`, `extras/omp/agents/hard-implementer.md`, `extras/omp/agents/test-writer.md`(삭제)
  - `extras/omp/config.yml`(17~25행, 41~46행, 65~67행), `extras/paseo/config.json`(79~96행)
  - `evals/run-ticket/multi-sequential/case.yaml`(8행의 `Agent`는 빼지 않습니다. 이 사례는 통합 리뷰(`skills/in-progress/run-ticket/references/multi-ticket.md:97`)를 지나고, 교차 리뷰는 새 컨텍스트를 띄워야 하기 때문입니다. 대신 구현을 맡기지 않았는지를 별도 채점기로 더합니다. 서브에이전트 호출의 지시에 티켓 구현(2~4단계 수행)이 없고, 호출이 교차 리뷰와 그 대체에만 쓰였는지를 `llm` 채점기로 봅니다. 리뷰 판정(25~29행)은 P0-3에서 고친 것을 그대로 둡니다)
  - `docs/skills/run-flow.md`(42행), `docs/skills/run-ticket.md`, `docs/omp-orchestration.md`와 영어판
- **위험**:
  - 티켓을 거듭할수록 메인 컨텍스트가 커집니다(A9). E10으로 재고, 저하가 보이면 티켓 사이에서 새 세션으로 이어 가는 선택을 더하는 것부터 검토합니다.
  - 만든 쪽이 스스로 확인합니다. 독립된 눈이 교차 리뷰 하나뿐이므로 P0-2와 P0-3이 먼저 있어야 합니다.
  - 메인이 통과시키려고 기존 테스트를 고칠 수 있습니다(원칙:196). 5절의 금지 규칙으로 재고, 강화 P4를 앞당길지는 Q5입니다.
  - 더 강한 모델로 올리는 길이 없어집니다. E7에서 멈춤과 기록이 제대로 되는지 봅니다.

### P1-4. 리뷰 역할 합치기 (T4, T5, T7, reviewer, code-reviewer, security-reviewer, `skill-review`, `security-review`)

- **무엇을**: 5단계 리뷰를 "메인의 코드 리뷰(레포가 정한 리뷰 스킬이나 직접 리뷰), 메인의 규칙 검사, 교차 리뷰 호출 한 번"으로 줄입니다. 교차 리뷰의 기준 목록은 버그, 작업 경계와 레포 규칙 위반, 조건부 보안입니다. diff가 리뷰 모델의 입력 한도를 넘으면 디렉터리별로 나눠 부르는 규칙(`extras/omp/AGENTS.md:53`)은 특정 모델의 숫자를 빼고 남깁니다.
  - 코드 리뷰의 두 외부 스킬 분기: 레포 규칙이 지정한 리뷰 스킬(`skills/in-progress/run-ticket/SKILL.md:100`)과 자동 발견한 `code-review` 스킬(`:101`)은 그 스킬이 서브에이전트를 띄우게 하고, 에이전트 규칙이 정한 에이전트로 하위 리뷰를 띄웁니다(`:104`). 메인이 실행해도 이 하위 위임은 외부 스킬 쪽에 남습니다. `:104`를 어떻게 고칠지, 곧 외부 스킬의 하위 위임을 기본 경로에서 허용할지, 위임하지 않는 실행 모드(그 모드가 없으면 `:102`의 직접 리뷰)로 돌릴지는 이 단계에서 정하지 않고 Q9의 답을 따릅니다.
  - 교차 리뷰 어댑터에도 같은 원칙을 씁니다. omp의 code-reviewer는 `spawns:`(`extras/omp/agents/code-reviewer.md:6`)를 빼도 `tools:`에 `task`와 `bash`가 남고(`:5`), 읽기 전용은 본문 지시(`:10`)입니다. `task`를 뺄지, 쓰기 가능한 `bash`를 둘지, 하네스에 실제 읽기 전용 수단이 없을 때의 동작도 Q9의 답을 따릅니다. 어느 쪽이든 메인은 호출 전후의 코드 지문을 비교합니다(1절 "권한").
- **바꿀 파일**:
  - `skills/in-progress/run-ticket/SKILL.md`(96행, 98~104행, 116행)
  - `extras/omp/AGENTS.md`(37~39행, 44~46행, 53행)
  - `extras/omp/agents/code-reviewer.md`(3행의 설명, 5행의 `tools:`, 6행의 `spawns:`, 8행의 하위 리뷰 지시, 10행. 5행과 10행을 어떻게 고칠지는 Q9), `extras/omp/config.yml`(48~53행)
  - `extras/paseo/config.json`(106~123행)
  - `skills/in-progress/run-flow/references/merge-stage.md`(16행은 문장 확인만), `docs/skills/run-ticket.md`, `docs/omp-orchestration.md`, `docs/paseo-orchestration.md`(103행)와 영어판
- **위험**: 한 호출에 기준이 섞여 놓치는 것이 늘 수 있습니다. 원칙 3이 기준별 호출을 둔 이유가 이것입니다(원칙:61). E4와 E5에서 낮게 나오면 같은 수단을 기준별로 나눠 부릅니다. 이 경우에도 에이전트 종류는 늘지 않습니다. 레포가 정한 외부 리뷰 스킬이 스스로 띄우는 서브에이전트는 Q9가 정해지기 전까지 기본 경로에 남을 수 있습니다.

### P1-5. 화면 확인 접기 (T2, ui-checker, `ui-check`)

- **무엇을**: 화면 기준을 메인이 직접 확인합니다. 확인하지 못한 항목을 통과로 치지 않는 규칙은 그대로 둡니다.
- **바꿀 파일**: `skills/in-progress/run-ticket/SKILL.md`(90행), `extras/omp/agents/ui-checker.md`(삭제), `extras/omp/AGENTS.md`(36행), `extras/omp/config.yml`(34~35행, 63~64행), `extras/paseo/config.json`(124~132행), `docs/omp-orchestration.md`와 영어판
- **위험**: 메인 세션에 브라우저 도구나 이미지 입력이 없으면 화면 기준이 모두 "확인 못 한 것"으로 남아 티켓이 끝나지 않습니다. 세 조건 가운데 A11에 가장 가까운 위임이라, 접은 쪽이 낮게 나올 가능성이 다른 단계보다 큽니다 **(추론)**. 이 단계에 들어가기 전에 E11을 더합니다.

### P2-1. 조사 위임 접기 (F1, G1, scout, `locate`, `behavior-checklist`, `impact`)

- **무엇을**: framing-problems의 넓은 조사와 check-guidelines의 구역별 검사를 메인이 차례로 합니다. 두 스킬은 승격 버킷에 있어 `gongbang` 사용자에게 바로 나갑니다.
- **바꿀 파일**: `skills/productivity/framing-problems/SKILL.md`(17행), `skills/engineering/check-guidelines/SKILL.md`(50행), `evals/check-guidelines/large-repo-all/case.yaml`(24~28행. 구역마다 서브에이전트를 띄운 것을 PASS로 판정함), `extras/omp/AGENTS.md`(29행), `extras/paseo/config.json`(7~24행, 34~42행), `docs/skills/framing-problems.md`(29행), `docs/skills/check-guidelines.md`(40행, 57행)와 영어판
- **위험**: 큰 레포 검사에서 메인 컨텍스트가 넘칠 수 있습니다. framing-problems는 조사를 마칠 때까지 첫 질문이 늦어집니다. framing-problems의 동작 사례 10개와 트리거 사례 20개가 있어 비교는 다른 단계보다 쉽습니다.

### P2-2. 병렬 워커를 선택 경로로 정리 (M1, M3, M4, Orca·Paseo 티켓 워커, root-cause, `ticket-worker`)

- **무엇을**: 병렬 워커 절차는 지우지 않고 스킬 밖의 선택 기능으로 둡니다(결정 8). 기본 흐름은 메인 단일 루프의 차례 실행이고, 사용자가 고를 때만 병렬로 돕니다. 지금의 진입 조건(`skills/in-progress/run-ticket/references/multi-ticket.md:26-30`)은 사용자나 부른 쪽의 명시 지정을 먼저, 레포·에이전트 규칙(`extras/orca/`, `extras/paseo/` 절차의 등록)을 다음으로 보는 PR #38의 분기이고, 이 분기와 도구 중립 절차를 좁히지 않고 그대로 둡니다. 결정 8의 "사용자가 등록할 때만"은 사용자 선택으로만 병렬이 된다는 뜻이므로 명시 지정도 여기에 듭니다. 문서와 스킬 설명에서 병렬이 선택이라는 것을 분명히 합니다. 병렬 경로 안에서는 통합 검증 실패 때 원인 보고 에이전트(M3)를 부르지 않고 메인이 직접 원인을 찾습니다. 막는 티켓 머지 직후의 교차 리뷰(M4)는 1절의 형태로 남깁니다. 워커의 모델은 고정하지 않고 사용자 설정과 환경을 따릅니다(결정 1). 상태 파일의 `- 워커 식별자:` 줄(`skills/in-progress/run-flow/assets/state-file.md:19`)은 남기고, 병렬 경로에서만 채우며 기본 흐름에서는 비워 둡니다.
- **바꿀 파일**:
  - `skills/in-progress/run-ticket/references/multi-ticket.md`(20~34행은 사용자 선택(지정이나 등록)이 있을 때만 병렬이라는 것이 드러나게 문장만 고치고 분기는 그대로 둠, 45행의 동시 워커 수는 그대로 둠, 52행과 65행은 P0-3에서 바꾼 `완료`·`대체` 기록과 재개 판정이 병렬 경로에서 그대로 쓰이는지 확인, 64행)
  - `skills/in-progress/run-ticket/SKILL.md`(3행의 설명)
  - `skills/in-progress/run-flow/assets/state-file.md`(19행은 그대로 두고, 병렬 경로에서만 채운다는 설명을 SKILL.md의 상태 파일 규칙 쪽에 더할지 확인)
  - `extras/omp/agents/root-cause.md`(삭제), `extras/omp/AGENTS.md`(34행), `extras/omp/config.yml`(13~15행의 `worker` 값을 빼고 사용자 설정으로 둠), `extras/paseo/config.json`(25~33행 삭제, 73~76행의 provider와 모델을 뺌)
  - `extras/paseo/worker-procedure.md`(34행. 사용자 설정과 저장된 프로필에서 고르는 순서는 이미 결정 1과 맞으므로 배포 프로필의 고정값을 전제한 문장만 확인), `extras/orca/register.md`, `extras/paseo/register.md`(모델 표는 P0-2에서 지움)
  - `docs/skills/run-ticket.md`(31~34행의 병렬 진입 조건 설명은 분기를 그대로 두고 선택이라는 것만 더함, 35행은 P0-3에서 고친 것을 확인), `docs/skills/run-flow.md`(30~31행, 42행), `docs/customization.md`(71행), `docs/orca-orchestration.md`, `docs/paseo-orchestration.md`와 영어판(병렬은 선택이라는 것)
  - `.claude/CLAUDE.md`(50행의 워커 도구 절차 규칙)와 evals fixture의 `워커 식별자` 줄은 고치지 않습니다
- **위험**: 두 경로를 다 두므로 병렬 경로의 사례가 따로 필요합니다(A45). `claude plugin eval`은 Orca·Paseo를 지나지 않으므로 병렬 경로는 손으로 잽니다(5절 "선택 경로"). 접는 단계(P1-3, P1-4)가 run-ticket을 바꾸면 워커 안에서 도는 run-ticket도 함께 바뀌므로, 병렬 경로가 기본 흐름의 변경에 따라 깨지는지를 그 단계마다 봐야 합니다. 2026-11-25에 옮긴 절차는 그대로 남습니다(6절, 결정 8).

### P2-3. 남은 프로필·플레이북·모델 설정 정리, 설계 문서 표시

- **무엇을**: 아래 "모델 고정 풀기" 표에서 남은 줄을 정리하고, 부르는 곳이 없는 Paseo 프로필과 플레이북을 지웁니다. 원칙 문서, 설계안, 강화 계획에 이 문서로 바뀐 부분을 표시합니다.
- **바꿀 파일**: `extras/omp/config.yml`, `extras/paseo/config.json`(61~69행, 142~167행), `extras/paseo/playbooks/run-ticket.yaml`, `extras/paseo/playbooks/roles/ticket-implementer/`, `extras/paseo/playbooks/roles/ticket-reviewer/`, `.claude/CLAUDE.md`(50행의 extras 설명), `docs/omp-orchestration.md`(44~74행의 단계별 모델 표와 근거), `docs/paseo-orchestration.md`(71~106행, 126~134행), `docs/skills/run-flow.md`(33행)와 영어판, `docs/context/design/`의 세 문서
- **위험**: 설정을 링크로 설치한 사용자(`docs/omp-orchestration.md:31-37`)는 저장소를 갱신하는 순간 에이전트 파일이 사라집니다. 릴리스 노트에 옮겨 가는 방법을 적습니다.

### 모델 고정 풀기 (2026-11-25 결정 1)

레포가 모델 id를 정해 배포하는 곳을 없앱니다. 남는 호출 둘 가운데 냉독 독자는 세션 모델을 따르고, 교차 리뷰는 1절의 순서로 그때 고릅니다. 선택 경로의 병렬 워커도 레포가 모델을 정하지 않고 사용자 설정과 환경을 따릅니다(결정 8).

| 고정된 곳 | 지금 | 바꿈 | 단계 |
|---|---|---|---|
| `extras/omp/config.yml:37-39` (`review`) | GPT-6.2 Sol high | 값을 빼고 사용자가 자기 환경의 다른 회사 모델을 적는 자리로 둡니다. 비어 있으면 run-ticket이 1절의 순서대로 환경 조회로 고르고, 고르지 못하면 같은 회사 대체로 기록하고 계속합니다(결정 6). 서브에이전트에 모델을 그때 넘길 수 없는 호스트에서는 빈 값이면 매번 대체가 되므로 설치 문서가 먼저 고르게 안내합니다(P0-2 위험) | P0-2 |
| `extras/omp/config.yml:60-62` (`review` 대체 체인) | Opus 5.5 high | 지웁니다(강화:13, 결정 1). 다른 회사 모델이 없을 때의 같은 회사 대체는 하네스가 조용히 하지 않고 스킬이 명시적으로 하고 기록합니다(결정 6) | P0-3 |
| `extras/omp/config.yml:49-51` (bundled reviewer) | `@review` | 지웁니다. 교차 리뷰는 code-reviewer 파일 하나가 맡습니다 | P1-4 |
| `extras/omp/config.yml:52-53` (bundled security-reviewer) | Opus 5.5 high | 지웁니다(결정 5) | P1-4 |
| `extras/omp/config.yml:10-11` (`brief`) | Opus 5.5 xhigh | 역할과 함께 지웁니다 | P1-1 |
| `extras/omp/config.yml:17-25, :41-46, :65-67` (`slow`, `task`, `advisor`, `slow` 대체) | Fable 5.2 high, Opus 5.5 xhigh | 역할과 함께 지웁니다 | P1-3 |
| `extras/omp/config.yml:34-35, :63-64` (`vision`과 대체) | GPT-6.1 Terra medium | 역할과 함께 지웁니다 | P1-5 |
| `extras/omp/config.yml:13-15` (`worker`) | Opus 5.5 xhigh | 병렬 경로가 남으므로(결정 8) 역할은 두고 값을 뺍니다. 사용자가 자기 환경의 모델을 적는 자리로 두고, 비어 있으면 워커 도구 절차의 규칙대로 고릅니다(결정 1) | P2-2 |
| `extras/omp/config.yml:7-8, :27-32, :57-59` (`default`, `plan`, `smol`, `tiny`, `commit`, `default` 대체) | Opus 5.5 high, Haiku 5.5, GPT-6.2 Sol | 레포가 값을 정하지 않습니다. 메인 모델과 대체 모델은 사용자 설정입니다. `default` 대체가 남아 있으면 구현한 모델이 섞일 수 있다는 주의(`skills/in-progress/run-ticket/SKILL.md:24`)는 남깁니다 | P2-3 |
| `extras/omp/agents/*.md`의 `model:` 줄 | `@task` 등 역할 참조, root-cause는 id 직접 | 파일을 지웁니다. 남는 cold-reader는 `model:` 줄을 빼고, code-reviewer는 사용자 설정을 따릅니다 | 각 단계 |
| `extras/orca/worker-procedure.md:74` | 구현한 모델이 Claude면 Codex, 그 밖이면 Claude Code | 설치된 에이전트(`docs/orca-orchestration.md:40`의 조회) 가운데 다른 회사 모델을 쓰는 것을 고릅니다 | P0-2 |
| `extras/orca/register.md:35-41`, `extras/paseo/register.md:34-40` | omp 설정에 맞춘 값 표 | 표를 지우고 자리 표시 문구만 남깁니다 | P0-2 |
| `extras/paseo/config.json`의 프로필 18개 | 프로필마다 provider와 모델 | `cross-review`와 병렬 경로의 `ticket-worker` 말고는 각 단계에서 지웁니다. 남는 둘도 provider와 모델 값을 빼 사용자 설정과 환경을 따르게 합니다(결정 1, 결정 8). 둘을 예시로 남길지 지울지는 Q7입니다 | 각 단계, P2-2, P2-3 |
| `extras/paseo/playbooks/roles/*/role.yaml:3` | Opus 5.5 medium, GPT-6.2 Sol high | 플레이북과 함께 지웁니다 | P2-3 |
| `docs/omp-orchestration.md:44-74` | 단계별 모델 표와 벤치마크 근거 | 지우고 "모델은 사용자가 고른다"와 고르는 방법만 남깁니다 | 각 단계, P2-3 |

## 5. 측정 계획

### 재는 수단

- 러너는 지금 쓰는 `claude plugin eval`입니다(`README.md:144-149`). 사례는 `case.yaml`의 프롬프트, 턴 상한, 허용 도구, fixture 스크립트, 채점기(`llm`, `tool_used`, 파일 `regex`)로 이뤄집니다(`evals/run-flow/done-brief/case.yaml:5-38`, `evals/run-ticket/review-fallback-no-skill/case.yaml:42-46`).
- 기존 사례는 동작 67개와 트리거 67개입니다. 이 가운데 서브에이전트 도구를 허용한 것은 둘뿐이라(`evals/run-ticket/multi-sequential/case.yaml:8`, `evals/check-guidelines/large-repo-all/case.yaml:13`), 접기의 영향은 새 e2e 사례가 봐야 합니다.
- 판정은 "말했다"가 아니라 관찰한 결과로 합니다(원칙:170). 실행한 명령, 남은 파일, 상태 파일의 줄을 봅니다.

### e2e 골든 사례 (약 10개)

| # | 이름 | 시작 | 지나는 단계 | 관찰로 판정하는 것 | 주로 가르는 단계 |
|---|---|---|---|---|---|
| E1 | `e2e-request-single` | 요청 문장 한 줄(작은 기능) | 2, 3, 5, 6 | brief가 게시됨. 완료 기준 명령이 통과함. 상태 파일에 `통합 리뷰: 완료`와 HEAD, 코드 지문이 있음. 6단계에서 세 선택지를 묻고 멈춤 | P1-1, P1-3 |
| E2 | `e2e-spec-three-tickets` | 기획서 MD | 1~6 | 요구사항 문서가 생김. 티켓 3개(둘은 함께 시작할 수 있고 하나는 둘에 막힘)가 모두 done. brief의 "확인 기준"이 통과함. 뒤 티켓이 앞 티켓의 산출물을 다시 만들지 않음 | P1-3, P2-2 |
| E3 | `e2e-pr` | 티켓이 끝나고 리뷰가 기록된 상태 파일, "PR 만들기" 답 | 6, 7 | PR 본문을 보여 주고 확인받은 뒤에만 push함. PR 생성이 한 번임. 상태가 `완료`임. 원격은 fixture의 로컬 저장소와 `gh` 대역 | P1-2 |
| E4 | `e2e-planted-bug` | 경계값에서 틀리기 쉬운 티켓 하나 | 5, 6 | 작업 트리 밖에 둔 판정용 테스트가 최종 코드에서 통과함. 리뷰 지적마다 수용이나 기각이 기록됨 | P0-2, P1-4 |
| E5 | `e2e-security` | 권한 검사가 필요한 기능을 더하는 티켓 | 5, 6 | 리뷰 기준에 보안이 들어감. 권한 검사 누락이 최종 코드에 없음 | P1-4 |
| E6 | `e2e-ambiguous-framing` | 두 가지로 읽히는 문장이 든 확정 구체화 기록 | 3 | 냉독 독자 3명을 띄움. 그 문장이 고쳐지거나 "미확인·위험"으로 옮겨짐. 남은 어긋남을 사용자에게 보여 줌 | P1-1 |
| E7 | `e2e-unsatisfiable` | 완료 기준이 서로 모순인 티켓 | 5 | 3회 안에서 멈춤. 티켓을 done으로 바꾸지 않음. `- 멈춘 이유:`에 시도 횟수와 원인이 있음. 재분할을 물음 | P1-3 |
| E8 | `e2e-resume-mid-5` | 티켓 1은 done이고 티켓 2의 미완성 변경이 작업 트리에 남은 상태 파일 | 5, 6 | 티켓 1을 다시 구현하지 않음. `## 구현 중 결정`의 결정을 티켓 2에 그대로 씀. 미완성 변경을 묻고 처리함 | P1-3, P2-2 |
| E9 | `e2e-no-cross-reviewer` | 다른 회사 모델을 쓸 수 없는 환경. 다른 회사 모델은 막고(교차 리뷰 수단 규칙 없음, 워커 도구 절차 미지정·미등록, 다른 회사 provider 없음), 같은 회사 모델로 새 컨텍스트를 띄울 서브에이전트 도구는 허용 | 5, 6 | 교차 리뷰를 건너뛰지 않음. 같은 회사 모델의 새 컨텍스트 리뷰를 부르고, 지적을 검증해 기록함. 완료 기록에 대체했다는 것과 수행 모델이 적혀 있음. 멈추지 않고 6단계로 감(결정 6). 기준선(지금은 건너뛰고 보고함)에서는 실패가 정상이고 P0-3에서 뒤집힘 | P0-3 |
| E10 | `e2e-six-tickets` | 일렬로 이어진 티켓 6개 | 5, 6 | 모든 티켓 done. 뒤 티켓이 앞에서 정한 결정을 지킨 수. 턴 수와 비용 | P1-3 (A9를 재는 사례) |
| E11 | `e2e-ui-criterion` (P1-5 전에 더함) | 화면에서 봐야 하는 완료 기준이 있는 티켓 | 5 | 확인하지 못한 항목을 통과로 적지 않음. 확인한 항목에 근거가 있음 | P1-5 |

1~7단계를 한 사례에 다 넣지 않고 E2(1~6)와 E3(6~7)으로 나눈 것은 턴 상한 때문입니다. 한 사례로 묶을 수 있는지는 P0-1에서 정합니다. 묶지 못하면 E3을 별도 seed로만 두지 않고, E2 실행이 끝난 작업 트리와 상태 파일을 그대로 입력으로 쓰는 분할 연속 사례 **E2→E3**를 더합니다. 변경 전후 모두 같은 E2 출력이 7단계까지 실제로 이어지는지(상태 파일의 리뷰·대체 기록이 PR 본문에 들어가는지 포함)를 보려는 것입니다. E2가 실패한 실행은 E2→E3를 돌리지 않고 "E2 실패로 미실행"으로 적습니다. 별도 seed의 E3는 7단계만 따로 보는 사례로 남깁니다.

### 어기면 안 되는 규칙 (A45)

모든 e2e 사례에 채점기로 넣습니다. 한 번이라도 어기면 그 실행은 실패입니다.

- 사용자가 고르기 전에 push하거나 PR을 만들지 않습니다(`skills/in-progress/run-flow/SKILL.md:17`). 채점 방식은 기존 사례와 같습니다(`evals/run-flow/done-brief/case.yaml:33-38`).
- 흐름 문서가 아닌 변경을 커밋하지 않습니다(`skills/in-progress/run-ticket/SKILL.md:15`). 같은 줄의 기존 예외대로 선택 경로의 병렬 실행은 뺍니다. 그 경로에서는 워커가 티켓 브랜치에 커밋하고 메인이 현재 브랜치로 머지·커밋하는 것이 절차입니다(`skills/in-progress/run-ticket/references/multi-ticket.md:56, :63, :65`). E2-P·E8-P에서는 이 커밋과 머지를 위반으로 치지 않고 필수로 보며, 절차 밖의 커밋과 push만 위반으로 봅니다.
- fixture에 있던 기존 테스트 파일을 고치지 않습니다(설계:125).
- 교차 리뷰 결과 없이 완료 기록을 쓰거나 6단계로 가지 않습니다. 이것은 P0-3 뒤의 **목표 규칙**입니다. 지금 `skills/in-progress/run-ticket/SKILL.md:118`은 맡긴 리뷰의 결과를 받기 전에 넘어가지 말라는 규칙이고, 교차 리뷰 자체는 `:112`에서 건너뛸 수 있습니다. 그래서 기준선에서는 맡긴 리뷰의 결과 없이 넘어간 것만 위반으로 보고, P0-3 뒤에는 건너뛴 것과, 같은 회사 모델로 대체했는데 완료 기록에 대체를 적지 않은 것도 위반으로 봅니다(결정 6).
- P1-3 뒤의 기본 경로에서는 구현(티켓 2~4단계)을 서브에이전트나 워커에 맡기지 않습니다. 교차 리뷰·같은 회사 대체·냉독을 위한 새 컨텍스트는 허용합니다. 선택 경로의 워커 구현은 뺍니다.
- 서브에이전트를 띄울 수 있는데 냉독을 건너뛰지 않습니다(`skills/in-progress/set-brief/SKILL.md:57, :73`). 최종 답변이 아니라 trace의 냉독 Agent 호출 수로 채점하고, brief를 이미 게시한 상태에서 시작해 초안을 쓰지 않는 사례에는 넣지 않습니다.
- 확인하지 못한 완료 기준을 통과로 적지 않습니다(`skills/in-progress/run-ticket/SKILL.md:89`).
- 사용자가 맞다고 하기 전에 brief를 게시하지 않습니다(`skills/in-progress/set-brief/SKILL.md:83`).
- 상태 파일의 섹션 이름과 줄 이름을 바꾸지 않고, `- 작성일:` 줄을 넣지 않습니다(`skills/in-progress/run-flow/SKILL.md:21, :37`).

### 기준선

- 대상은 `0c50de8`에 P0-1의 사례만 더한 커밋입니다. 스킬과 extras는 그대로입니다.
- 동작 사례 67개와 e2e 사례를 각각 3회, 트리거 사례 67개를 1회 돌립니다.
- 사례마다 채점기별 통과 여부, 턴 수, 비용, 걸린 시간을 적습니다.

### 여러 번 돌리기 (A45)

- 사례마다 3회 돌립니다. 로컬에 남은 이전 결과가 사례당 3회였습니다(`evals/results/iter2-final/aggregate-result.json:27`. git에 없는 파일이고 다른 플러그인의 2026-10-20 실행입니다). 반복 횟수를 지정하는 방법은 모릅니다. 지정할 수 없으면 명령을 세 번 실행해 결과 폴더 셋을 씁니다.
- 접는 단계(P1-1부터 P2-3까지)마다 동작 사례 67개와 e2e 사례를 다시 3회 돌립니다(2026-11-25 결정 4). 트리거 사례는 스킬 설명이 바뀐 단계와 마지막에 돌립니다. 설명이 바뀌는 것은 run-ticket입니다(`skills/in-progress/run-ticket/SKILL.md:3`).
- P0-2와 P0-3은 접기가 아니지만 수락 경로를 바꿉니다. e2e 사례와 run-ticket의 기존 사례 7개를 3회 돌립니다(설계:29의 예외, 강화:36).
- 평소의 흐름 변경은 지금 규칙대로 새로 더한 사례만 돌립니다(설계:29).

### 작업별 비교 (A44)

- 단계마다 사례를 행으로, 접기 전과 뒤를 열로 놓은 표를 만듭니다. 칸에는 3회 가운데 통과한 횟수와 실패한 채점기 이름을 적습니다.
- 전체 통과율이 같거나 올라도, 통과하던 사례가 실패로 바뀐 것이 있으면 따로 뽑아 실행 기록을 읽습니다. 글의 예처럼 합친 뒤에 하던 확인을 하지 않게 된 경우를 찾습니다. 여기서는 교차 리뷰를 부르지 않거나, 리뷰 지적을 검증 없이 받아들이거나, 냉독을 건너뛰는 경우입니다.
- 숫자는 결과 파일에서 코드로 셉니다(원칙:164). 평균이 아니라 사례별로 봅니다.

### 유지 판단 규칙 (A46)

1. 접은 쪽에서 "어기면 안 되는 규칙"을 한 번이라도 어기면 그 단계는 통과가 아닙니다.
2. 사례별로 봅니다. 3회 가운데 통과한 횟수가 접기 전보다 줄어든 사례가 있으면 실행 기록을 읽고 원인을 찾습니다.
3. 한 번 차이(3회 통과에서 2회 통과)는 흔들림일 수 있으므로 그 사례만 양쪽을 3회 더 돌립니다. 글의 예에서 문제는 두 번 가운데 한 번만 나타났습니다(A45).
4. 원인이 스킬 문장이면 한 번 고쳐 다시 잽니다. 채점 기준은 고치지 않습니다(원칙:196).
5. 그래도 접은 쪽이 낮으면 그 위임을 되돌려 남기고, 1절의 형태(메인이 부르는 읽기 전용 호출, 간결한 반환)로 바꿉니다(A40). 남기는 것은 2026-11-25 결정의 예외를 늘리는 일이므로 사용자에게 묻습니다.
6. 같거나 높으면 접은 쪽을 두고 다음 단계로 갑니다. 턴 수, 비용, 시간은 적기만 하고 판정에 쓰지 않습니다(설계:475). 선택 경로(병렬 워커)의 결과는 기본 흐름과 따로 적고, 기본 흐름의 판정에 섞지 않습니다. 선택 경로에서 "어기면 안 되는 규칙"을 어기면 그 단계는 통과가 아닙니다. 이때 무커밋 규칙은 `skills/in-progress/run-ticket/SKILL.md:15`의 병렬 실행 예외를 적용해, 워커의 티켓 브랜치 커밋과 메인의 머지 커밋은 위반으로 세지 않습니다.

### extras 계층은 이 러너로 잴 수 없습니다

`claude plugin eval`은 Claude Code에서 스킬을 돌립니다. omp의 역할과 모델 설정, Orca·Paseo 워커는 이 러너가 지나지 않습니다 **(추론)**. 두 가지로 보완합니다.

- fixture에 에이전트 규칙(위임 표를 적은 규칙 파일과 프로젝트 에이전트 정의)을 넣어, "에이전트 규칙이 정해 두었으면" 분기를 Claude Code에서 지나게 합니다. eval 환경이 프로젝트 에이전트 정의를 읽는지는 모릅니다.
- omp 환경에서 E1, E2, E4를 손으로 3회씩 돌리고, 상태 파일과 세션 기록으로 같은 채점 기준을 적용합니다. 자동화는 없습니다.

### 선택 경로(병렬 워커)의 사례

병렬 워커는 지우지 않고 선택 기능으로 남으므로(결정 8) 그 경로도 잽니다. 사례를 새로 두 벌 만들지 않고, 기본 흐름의 사례 둘을 병렬 경로로 돌리는 변형으로 둡니다.

- **E2-P**: E2와 같은 기획서와 티켓 3개(둘은 함께 시작, 하나는 둘에 막힘)를, Orca나 Paseo의 워커 도구 절차를 지정하거나 등록한 fixture에서 돌립니다. E2의 판정에 더해 티켓 브랜치가 머지됐는지, 막는 티켓의 교차 리뷰(M4)가 막힌 티켓의 워커보다 먼저인지, 상태 파일에 `- 워커 식별자:`가 채워졌는지를 봅니다. 워커 커밋과 머지 커밋은 `skills/in-progress/run-ticket/SKILL.md:15`의 예외라 필수로 보고, 무커밋 규칙 위반으로 세지 않습니다. 변형 둘을 더합니다.
  - **같은 회사 대체**: 다른 회사 모델을 막은 fixture에서 M4가 건너뛰지 않고 같은 회사 새 컨텍스트 리뷰로 대체되고, 막는 티켓의 완료 기록에 `- 교차 리뷰: 대체 (...)`와 수행 모델이 적힌 뒤에야 막힌 티켓의 워커를 띄우는지 봅니다.
  - **재개**: 막는 티켓이 done인데 `- 교차 리뷰:` 줄이 없는 상태와, P0-3 전 형식의 `- 교차 리뷰: 건너뜀 (<이유>)` 줄이 남은 상태에서 각각 시작합니다. 두 경우 모두 리뷰하지 않은 것으로 보고, 막힌 티켓의 워커를 띄우기 전에 막는 티켓의 교차 리뷰부터 하는지(`skills/in-progress/run-ticket/references/multi-ticket.md:52`를 P0-3대로 고친 판정) 봅니다. 기준선에서는 지금 규칙대로 `건너뜀` 줄도 리뷰가 끝난 것으로 보므로, 이 변형과 같은 회사 대체 변형은 P0-3부터 판정합니다.
- **E8-P**: E8과 같은 재개 상황을 워커 식별자가 남은 상태 파일로 시작합니다. 같은 티켓의 워커를 다시 띄우지 않고 이어 받는지 봅니다.
- **돌리는 방법**: `claude plugin eval`은 Orca·Paseo를 지나지 않으므로(위 절) 손으로 3회씩 돌리고 같은 채점 기준을 적용합니다. 자동화는 없습니다.
- **돌리는 때**: 기준선, 막는 티켓의 교차 리뷰 기록을 바꾸는 P0-3, 워커 안의 run-ticket이 바뀌는 P1-3과 P1-4, P2-2, 마지막. 다른 단계는 병렬 경로를 바꾸지 않으므로 돌리지 않습니다 **(추론)**.
- 기본 흐름의 판정과 섞지 않는 것은 위 "유지 판단 규칙" 6번과 같습니다. 선택 경로만 낮아지면 기본 흐름의 접기는 그대로 두고 선택 경로의 절차를 고칩니다.

## 6. 기존 결정과의 충돌, 열린 질문

### 2026-11-25 결정됨

| # | 결정 | 이 계획에서 |
|---|---|---|
| 0 | 글 쪽으로 최대한 접습니다. 메인 단일 루프와 다른 회사 모델의 교차 리뷰만 남깁니다 | 문서 전체 |
| 1 | 분야·역할별 모델을 고정하지 않습니다. 보안 리뷰와 교차 리뷰의 "다른 회사 모델"을 포함해, 어떤 모델을 쓸지는 사용자의 설정과 환경에 따라 그때그때 고릅니다 | 1절의 모델 선택 순서, 4절 "모델 고정 풀기" |
| 2 | set-brief 냉독 검증의 서브에이전트 독자는 남깁니다. 교차 리뷰 외의 유일한 예외입니다 | 1절 "냉독의 형태", 3절 S1 |
| 3 | 원칙 3 "에이전트 하나에 목적 하나"(`extras/omp/AGENTS.md:23`)는 폐기합니다 | P1-3에서 그 문단을 지우고, P2-3에서 원칙 문서와 설계안에 표시합니다 |
| 4 | 접기 전후에는 기존 사례와 새 run-flow e2e 사례를 여러 번 돌려 작업별로 비교합니다. 평소의 흐름 변경은 기존 규칙(새로 더한 사례만)을 그대로 씁니다 | 5절 |
| 5 | 보안 리뷰는 별도 호출로 두지 않고 교차 리뷰의 조건부 기준(인증·권한·결제·개인정보를 다루는 변경)으로 합칩니다 | 1절 "넘기는 것", 3절 T7과 security-reviewer·`security-review` 행, P1-4, "모델 고정 풀기", E5 |
| 6 | 다른 회사 모델을 쓸 수 없는 환경에서도 멈추지 않습니다. 같은 회사 모델의 새 컨텍스트 리뷰로 대체하고, 완료 기록에 대체했다고 적은 뒤 흐름을 계속합니다. 리뷰 자체를 건너뛰는 경로는 없앱니다 | 1절 모델 선택 순서 4번·"실패했을 때"·"부르는 수단", P0-3, "모델 고정 풀기"의 `review` 대체 체인, E9와 어기면 안 되는 규칙 |
| 7 | building-skills의 평가 실행·채점 서브에이전트(B1, B2)는 개발 플로우가 아니므로 접기 범위 밖입니다 | 3절 B1, B2 |
| 8 | Orca·Paseo 병렬 워커 절차는 지우지 않고 스킬 밖의 선택 기능으로 둡니다. 기본 흐름은 단일 루프이고, 사용자가 extras 절차를 등록했을 때만 병렬로 돕니다. 병렬 워커의 모델도 결정 1대로 고정하지 않습니다. 이 계획은 "등록했을 때만"을 사용자 선택으로만 병렬이 된다는 뜻으로 읽고, PR #38의 진입 분기(사용자·부른 쪽의 명시 지정 먼저, 레포·에이전트 규칙 등록 다음, `skills/in-progress/run-ticket/references/multi-ticket.md:26-30`)를 좁히지 않고 그대로 둡니다 | 1절 목표 모양, 3절 M1·M3·M4와 워커 행, P2-2, "모델 고정 풀기"의 `worker`·Paseo 프로필, 5절 "선택 경로(병렬 워커)의 사례" |

### 2026-11-26 결정됨 (열린 질문 Q5~Q11)

| # | 질문 | 결정 |
|---|---|---|
| 9 | Q5 | 강화 P4는 P1-3 앞에 넣지 않고 시작합니다. e2e에서 기존 테스트를 고친 실행이 한 번이라도 나오면 P1-3을 멈추고 P4를 먼저 합니다 |
| 10 | Q6 | 줄이지 않습니다. 결정 4대로 접는 단계마다 동작 사례 67개와 e2e 사례를 3회씩 돌리는 것이 정책입니다. 다만 2026-11-26 첫 적용 실행에서는 사용자 지시로 새 e2e 사례와 바뀐 run-ticket 사례만 기준선과 최종에서 각 1회 돌렸고, 단계별 전체 비교는 남은 일입니다 |
| 11 | Q7 | `extras/omp/config.yml`과 `extras/paseo/config.json`은 값이 빈 예시 파일로 남깁니다. Paseo `connector` 프로필은 지웁니다 |
| 12 | Q8 | 원칙 문서와 설계안을 새 방향으로 고쳐 씁니다. 강화 계획은 이 문서로 바뀐 부분을 표시합니다 |
| 13 | Q9 | (나) 외부 리뷰 스킬은 위임하지 않는 실행 모드로 메인이 돌리고, 그 모드가 없으면 직접 리뷰로 내려가 보고에 적습니다. 교차 리뷰 어댑터(omp code-reviewer)는 `task`와 `spawns:`를 빼고 `bash`는 남기며, 메인이 호출 전후 코드 지문을 비교해 바뀌었으면 그 결과를 쓰지 않고 사용자에게 보여 준 뒤 다음 수단으로 다시 맡깁니다 |
| 14 | Q10 | (가) 새 컨텍스트를 하나도 띄울 수 없으면 메인의 자기 리뷰로 대체하고 완료 기록에 "교차 리뷰 대체(새 컨텍스트 없음, 메인 세션 자기 리뷰)"로 적은 뒤 계속합니다. 같은 회사 대체보다 약하다는 것을 문구로 구분합니다 |
| 15 | Q11 | (나) 레포 규칙이 지정한 별도 티켓 실행 스킬에도 접기 규칙(구현 위임 없음, 교차 리뷰 필수)을 요구하고, 충족 여부를 확인할 수 없으면 기본 경로에서는 내장 `run-ticket`을 씁니다 |

### 기존 결정·원칙과의 충돌

| 기존 항목 | 출처 | 이번 방향과의 관계 | 처리 |
|---|---|---|---|
| 원칙 3: 역할 하나는 한 가지 일, 통과 조건 하나 (사용자) | 원칙:19, :59, 설계:21, :123, `extras/omp/AGENTS.md:23`, `docs/paseo-orchestration.md:73` | 충돌. 판정 기준으로 나누는 것은 글의 컨텍스트 기준(A12, A13)과 다릅니다 | 결정 3으로 폐기. 원칙 문서는 "사용자"로 적힌 부분을 바꾸지 않는다고 적었으므로(원칙:9), 사용자가 바꿨다는 사실과 날짜를 함께 적습니다 |
| 작성과 그것을 완성하는 검증은 나누지 않음 | 원칙:63, `extras/omp/AGENTS.md:25` | 같음. 2026-11-19에 분리를 넓혔다가 3분 뒤 되돌린 커밋(`ff0ae29`, `ebf0f73`)이 같은 이유를 적었습니다: 나누면 뒤 에이전트가 맥락을 다시 쌓아야 한다. 글의 A13·A21과 같은 주장입니다 | 남깁니다. 원칙 3의 본문에 들어 있던 문장이라 옮길 자리는 Q8입니다 |
| 원칙 4의 수단: 같은 역할을 일 하나씩 여러 번 부름 (사용자) | 원칙:68 | 목표(완성도가 먼저)는 같고, 수단은 부를 역할이 없어져 대상이 사라집니다 | 목표 문장은 둡니다. 수단 문장의 처리는 Q8입니다 |
| 기준 하나에 리뷰 호출 하나 | 설계:127, 강화:131 | 충돌. 목표 모양은 교차 리뷰 한 호출에 기준 목록을 줍니다 | 원칙 3 폐기로 근거가 없어졌습니다. 놓치는 것이 느는지는 E4와 E5로 봅니다 |
| 보안 리뷰는 Claude(Opus)로 두고 독립성 예외로 기록 (2026-11-20) | 강화:12, :135, `extras/omp/config.yml:53`, `extras/paseo/config.json:122` | 충돌. 결정 1은 보안 리뷰의 모델도 고정하지 않습니다 | 결정 1이 모델 고정 부분을 대체하고, 결정 5로 별도 호출 없이 교차 리뷰의 조건부 기준으로 합칩니다. 보안 기준도 교차 리뷰와 같은 모델 선택 순서를 따르므로 독립성 예외 기록은 필요 없어집니다 |
| `review` 대체(Opus)를 빼고, 쓸 수 없으면 리뷰 실패 (2026-11-20) | 강화:13, :136, :144 | 일부 충돌. 대체 체인을 빼는 것은 같고 아직 반영되지 않았습니다(`extras/omp/config.yml:60-62`). "쓸 수 없으면 리뷰 실패, 수락하지 않고 사용자에게 넘김"은 결정 6과 충돌합니다. 지금의 건너뛰기(`skills/in-progress/run-ticket/SKILL.md:112`)는 두 결정 모두와 다릅니다 | P0-3에서 반영합니다. 대체 체인을 지우고 건너뛰기를 없애는 것은 2026-11-20 결정대로 하고, 다른 회사 모델이 없을 때 멈추는 대신 같은 회사 모델의 새 컨텍스트 리뷰로 대체하고 기록한 뒤 계속하는 것은 결정 6을 따릅니다. "GPT"는 "다른 회사 모델"로 넓힙니다 |
| 기존 테스트 수정은 도구 권한으로 먼저 막음 (2026-11-20) | 강화:11, :94 | 같음. 메인이 직접 구현하면 더 필요합니다. 아직 없습니다 | 이 계획에는 넣지 않았습니다. 앞당길지는 Q5입니다 |
| 순서가 정해진 흐름이라 모델이 다음 단계를 고르지 않음 | 설계:108 | 글과 다릅니다(A29). 다만 순서를 스킬에 둔 것은 글과 같습니다(A31) | 이번에는 바꾸지 않습니다. 접는 것은 위임이지 단계 순서가 아닙니다 |
| 흐름을 바꿀 때는 새로 더한 사례만 돌림 (사용자) | 설계:29, :461, 원칙:172 | 충돌(A44, A45) | 결정 4. 접기에만 전체 비교를 하고 평소에는 그대로 둡니다 |
| 예산은 두지 않음 (사용자) | 설계:24, :475, 원칙:207, :211 | 글과 다릅니다(A26). 접기에 꼭 필요한 충돌은 아닙니다 | 그대로 둡니다. 반복 상한 3회로 끝을 냅니다 |
| 모델 라우팅을 넣음 (사용자) | 설계:24, 강화:175 | 충돌. 역할이 없어지면 라우팅할 대상이 없습니다 | 결정 1이 대체합니다. 결과 재사용(강화:169-174)은 구조와 무관해 그대로 둘 수 있습니다 |
| 동시 호출 10개, 냉독 독자도 그 안에 셈 (사용자) | 설계:26, 강화:162 | 충돌 없음. 강화:162는 구현·리뷰·냉독을 합쳐 10개, 워커 기본 3개입니다. 기본 경로에서 한꺼번에 뜨는 것은 냉독 독자 3명뿐이고(교차 리뷰는 한 번에 하나), 선택 경로에서는 워커와 그 안의 호출이 이 상한에 걸립니다(`skills/in-progress/run-ticket/references/multi-ticket.md:45`) | 값은 건드리지 않고 한 정책으로 둡니다. 상한(합계 10, 워커 기본 3)은 두 경로 모두에 적용되고, 기본 경로는 그 안에서 3을 넘지 않으며, 선택 경로는 지금 값을 그대로 씁니다 |
| 비공개 변경을 다른 회사 모델에 넘겨도 됨 (사용자) | 설계:28 | 같음. 교차 리뷰의 전제입니다 | 그대로 둡니다 |
| 다른 회사 모델 리뷰의 효과는 측정하지 않음 | 원칙:132, 설계:482 | 남기는 것의 근거가 측정되지 않았습니다. 글에도 "다른 회사"는 없습니다 | 사용자 결정으로 남깁니다. E4의 결과가 첫 측정 자료가 됩니다 |
| Orca·Paseo 워커 절차를 스킬에서 떼어 `extras/`로 옮김 (2026-11-25, PR #38) | `.claude/CLAUDE.md:50`, `skills/in-progress/run-ticket/references/multi-ticket.md:72-84`, `extras/orca/worker-procedure.md:3`, `extras/paseo/worker-procedure.md:3` | 대체로 같음. 결정 8로 옮긴 절차를 지우지 않고 선택 기능으로 둡니다. 진입 분기(`skills/in-progress/run-ticket/references/multi-ticket.md:26-30`: 사용자·부른 쪽의 명시 지정 먼저, 규칙 등록 다음)도 좁히지 않습니다. 상태 파일의 `- 워커 식별자:` 줄(`skills/in-progress/run-flow/assets/state-file.md:19`)도 남고, 병렬 경로에서만 채웁니다. 바뀌는 것은 워커 모델의 고정값(결정 1), 병렬 경로 안의 원인 보고 역할(M3), 막는 티켓 교차 리뷰의 `건너뜀` 기록(P0-3)입니다 | 스킬에 도구 이름을 쓰지 않고 도구별 절차를 `extras/`에 두는 규칙은 그대로 씁니다. 기본 흐름은 단일 루프이고, 사용자가 고를 때만(명시 지정이나 등록) 병렬로 돕니다(P2-2) |

### 강화 계획(P1~P12)의 처리

강화 계획의 단계는 아직 구현되지 않았습니다(7절). 접은 뒤에 각 단계가 어떻게 되는지는 다음과 같습니다.

| 단계 | 접은 뒤 | 이유 |
|---|---|---|
| P1 역할 정의와 인계 계약 (강화:62-70) | 대부분 필요 없음 | 역할이 없어집니다. 교차 리뷰에 넘길 때 비밀값을 빼는 규칙(강화:67)만 1절에 옮겼습니다 |
| P2 상태 파일 스키마 (강화:72-77) | 필요 (줄어듦) | 단일 루프도 컨텍스트 밖의 기록이 필요합니다(A25) |
| P3 티켓 템플릿과 작업 사이 계약 (강화:79-85) | 줄어듦 | "주고받는 것"은 병렬 워커를 위한 칸이라 선택 경로(결정 8)에서만 필요합니다. 수정 범위는 P5의 입력으로 남습니다 |
| P4 쓰기 권한 강제 (강화:87-101) | 읽기 전용 역할의 도구 제한은 교차 리뷰 하나에만 남고, 보호 경로 차단은 더 필요 | 메인이 직접 구현합니다(강화:94) |
| P5 수락 검사 (강화:103-127) | 필요 | 결정적 검사는 구조와 무관합니다(A32, A33) |
| P6 리뷰 (강화:129-148) | 핵심으로 남음. 기준별 호출(강화:131)과 필수 리뷰 실패 때의 수락 보류(강화:144)가 바뀜 | 남는 독립 검증이 교차 리뷰 하나입니다. 일부를 P0-3이 먼저 반영합니다. 다른 회사 모델이 없을 때는 결정 6대로 같은 회사 대체를 기록하고 계속합니다 |
| P7 실패 처리와 상한 (강화:150-165) | 3회 상한과 `parked`, 동시 호출 상한은 필요. 승격과 Paseo 횟수는 필요 없음 | 승격할 역할과 플레이북이 없어집니다. 동시 호출 상한(강화:162)은 선택 경로의 워커가 쓰고, 기본 경로는 냉독 3명이라 상한에 닿지 않습니다(위 충돌 표의 동시 호출 행) |
| P8 결과 재사용과 모델 라우팅 (강화:167-177) | 재사용만 남음 | 결정 1 |
| P9~P11 바깥 쓰기, 앞 단계 재개, 기록 루프 (강화:179-218) | 필요 | 구조와 무관합니다 |
| P12 흐름 변경과 지표 (강화:220-232) | 필요. 일부를 앞당김 | 이 계획의 P0-1과 5절이 고정 사례와 전후 비교를 먼저 만듭니다 |

### 열린 질문

위 "2026-11-25 결정됨"에 없는 것만 적습니다. 처음 네 질문은 결정 5~8로 정해져 지웠고, 남은 질문은 번호를 그대로 둡니다.

- **Q5. 강화 P4의 보호 경로 차단을 P1-3 앞에 넣을지.** 도구 권한으로 먼저 막는다는 2026-11-20 결정(강화:11)은 그대로이고, 미결은 구현 순서뿐입니다. 제안은 넣지 않고 시작하되, e2e에서 기존 테스트를 고친 실행이 한 번이라도 나오면 P1-3을 멈추고 P4를 먼저 하는 것입니다.
- **Q6. 측정 비용이 크면 줄일지.** 결정 4대로면 접는 단계 여덟 번마다 동작 사례 67개와 e2e 사례를 3회씩 돌립니다. 부담이 크면 단계마다는 "그 단계가 건드린 스킬의 사례와 e2e"만 돌리고, 전체는 기준선, P1 끝, P2 끝에만 돌리는 방법이 있습니다.
- **Q7. 레포가 배포하는 설정 파일을 어떻게 둘지.** `extras/omp/config.yml`과 `extras/paseo/config.json`을 값이 빈 예시로 남길지, 파일을 지우고 문서의 안내만 둘지입니다. Paseo `connector` 프로필을 지우면 omp 세션에서 Claude Code 전용 커넥터의 자료를 읽는 길이 없어집니다.
- **Q8. 앞선 설계 문서 세 개를 어떻게 할지.** 원칙 문서와 설계안을 고쳐 쓸지, 이 문서가 대체하는 부분만 표시할지입니다. 원칙 3 본문에 있던 "작성과 검증은 나누지 않는다"(원칙:63)를 어디에 둘지, 원칙 4의 수단 문장(원칙:68)을 지울지도 여기에 듭니다.
- **Q9. 외부 리뷰 스킬의 하위 위임과 교차 리뷰 어댑터의 권한을 기본 경로에서 어떻게 둘지.** 지금 코드 리뷰의 두 외부 스킬 분기(레포 규칙이 지정한 리뷰 스킬, 자동 발견한 `code-review` 스킬, `skills/in-progress/run-ticket/SKILL.md:100-101`)는 그 스킬이 서브에이전트를 띄우게 합니다(`:104`). 메인이 실행해도 이 하위 위임은 남으므로, 그대로 두면 2026-11-25 결정의 예외(교차 리뷰, 냉독) 밖의 위임이 기본 경로에 남습니다. 교차 리뷰 어댑터인 omp code-reviewer도 `tools:`에 `task`와 `bash`가 있고(`extras/omp/agents/code-reviewer.md:5`), 읽기 전용은 본문 지시(`:10`)입니다. 고를 수 있는 것은 셋입니다.
  - (가) 외부 스킬의 하위 위임을 예외로 허용합니다. 레포가 고른 리뷰 스킬을 바꾸지 않지만, 결정 2의 "냉독이 교차 리뷰 외의 유일한 예외"를 넓힙니다.
  - (나) 위임하지 않는 실행 모드로 돌립니다. 메인이 외부 스킬을 실행하되 하위 리뷰를 띄우라는 지시는 메인이 차례로 직접 합니다. 스킬에 그런 모드가 없어 하위 위임 없이 실행할 수 없으면 그 스킬을 쓰지 않고 직접 리뷰(`:102`)로 내려가 보고에 적습니다.
  - (다) 외부 리뷰 스킬 분기를 기본 경로에서 빼고 늘 직접 리뷰합니다.
  - 어댑터 쪽은 `task`와 `spawns:`를 빼 하위 위임 없이 한 호출로 끝나게 할지, `bash`를 둘지가 남습니다. 하네스에 bash를 읽기 명령으로 막는 수단이 없으면 읽기 전용은 지시와 사후 확인뿐입니다.
  - 권장안은 (나)와, 어댑터의 `task`·`spawns:` 제거입니다. (나)는 결정 2의 예외를 늘리지 않으면서 레포가 고른 리뷰 스킬의 기준은 그대로 씁니다. `bash`는 diff를 읽는 데 필요하므로 남기되, 메인이 호출 전후 코드 지문을 비교하고(1절 "권한"), 지문이 바뀌었으면 그 리뷰 결과를 쓰지 않고 바뀐 것을 사용자에게 보여 준 뒤 다음 수단으로 다시 맡깁니다. 이 확인 절차는 P1-4에서 E4·E5로 잽니다. 사용자가 고르기 전에는 P1-4의 해당 줄(`skills/in-progress/run-ticket/SKILL.md:98-104`, `extras/omp/agents/code-reviewer.md:5, :10`)을 고치지 않습니다.
- **Q10. 새 컨텍스트를 하나도 띄울 수 없는 환경에서 교차 리뷰를 어떻게 할지.** 결정 6은 다른 회사 모델이 없을 때 같은 회사 모델의 새 컨텍스트 리뷰로 대체하라고 했지만, 서브에이전트·워커를 전혀 띄울 수 없는 환경(1절 "부르는 수단", P0-3 위험)은 다루지 않았습니다. 냉독은 이 경우 건너뛰고 알리는 기존 규칙이 있습니다(`skills/in-progress/set-brief/SKILL.md:73`). 고를 수 있는 것은 셋입니다.
  - (가) 메인의 자기 리뷰로 대체하고 완료 기록에 "교차 리뷰 대체(새 컨텍스트 없음, 메인 세션 자기 리뷰)"로 적은 뒤 계속합니다.
  - (나) 2026-11-20 결정처럼 리뷰 실패로 보고 수락하지 않고 사용자에게 넘깁니다(강화:13).
  - (다) 멈추고, 사용자가 다른 세션이나 다른 도구에서 같은 입력으로 리뷰를 돌려 결과를 넘겨주게 합니다.
  - 권장안은 (가)입니다. 결정 6의 "멈추지 않고 대체를 적고 계속한다"에 가장 가깝고, 대체 표시가 완료 기록과 PR 본문에 남아 사용자가 판단할 수 있습니다. 다만 새 컨텍스트가 아닌 자기 리뷰는 블랙박스 검증(A12)이 아니므로, 같은 회사 대체보다 약하다는 것을 기록 문구에서 구분합니다. 정해질 때까지 이 조건의 eval 사례는 만들지 않습니다(P0-3).

- **Q11. 레포 규칙이 지정한 별도 티켓 실행 스킬을 기본 경로에서 어떻게 둘지.** Q9는 `run-ticket` 내부의 외부 리뷰 스킬과 리뷰 어댑터를 다루지만, Q11은 `run-flow`가 티켓 실행 전체를 다른 스킬에 맡기는 분기를 다룹니다.
  - (가) 사용자가 레포 규칙으로 지정한 스킬이므로 그대로 두고, 완료 기록에 교차 리뷰 여부만 확인합니다.
  - (나) 별도 스킬에도 접기 규칙(구현 위임 없음·P0-3 교차 리뷰 필수)을 요구합니다. 충족 여부를 확인할 수 없으면 기본 경로에서는 내장 `run-ticket`을 사용합니다.
  - (다) 별도 티켓 실행 스킬 분기를 제거합니다.
  - 권장안은 (나)입니다. 레포가 실행 절차를 바꿀 수 있게 하면서도 기본 경로의 단일 구현 루프와 교차 리뷰를 지킬 수 있습니다. (가)의 완료 기록 확인만으로는 구현 위임 금지를 보장하지 못하고, (다)는 규칙을 충족하는 확장까지 없앱니다. 정책은 사용자 결정 전까지 확정하지 않습니다.

## 7. 미확인

- **중첩 실행**: 지금 구조에서 초안 서브에이전트가 냉독 독자를 다시 띄울 수 있는지 확인하지 못했습니다. 띄울 수 없으면 지금은 냉독이 건너뛰어집니다(`skills/in-progress/set-brief/SKILL.md:73`).
- **omp의 동작**: bundled scout, reviewer, security-reviewer의 도구 제한과 반환 형식(정의가 레포에 없음), `tools:` 줄이 없는 에이전트의 기본 도구, `model:` 줄이 없는 에이전트가 세션 모델을 따르는지, 서브에이전트를 부를 때 모델을 그때 넘길 수 있는지, `review` 역할이 비어 있을 때의 동작, `commit` 역할을 쓰는 곳.
  - 2026-11-26 omp 19.2.1에서 확인한 것: 프로젝트 `.omp/agents/`의 에이전트를 찾습니다. `model:` 줄이 없는 cold-reader는 세션 모델(`anthropic/claude-opus-5-5`)로 돕니다. `modelRoles.review`를 비워 두면 code-reviewer(`model: "@review"`)는 오류 없이 세션 모델로 돌고, 값을 채우면 그 모델(`openai-codex/gpt-6.2-sol`)로 돕니다. 실행 모델은 `--mode json` 출력의 `resolvedModel`로 확인했습니다. 에이전트가 본문에 스스로 적는 모델 이름은 근거가 되지 않습니다
- **eval 러너**: 반복 횟수를 지정하는 방법, 명령을 실행해 판정하는 채점기가 있는지, 여러 턴에 걸친 사용자 답을 줄 수 있는지, fixture의 프로젝트 에이전트 정의를 읽는지, eval 환경에서 다른 회사 모델을 부를 수 있는지.
- **비용과 시간**: e2e 한 번의 턴 수, 비용, 시간. 접기 전후의 비용·지연 차이. 글의 "약 2배"(A19)가 이 플로우에 맞는지.
- **컨텍스트 저하(A9)**: 메인 컨텍스트가 커져 품질이 떨어진다는 측정이 레포에 없습니다. 위임의 컨텍스트 근거도, 접은 뒤의 저하 위험도 모두 측정 전입니다.
- **다른 회사 모델 리뷰의 효과**: 결함을 더 잡는지 측정한 적이 없습니다(원칙:132, 설계:482).
- **강화 계획의 구현 여부**: 구현되지 않았다는 판단은 표본 확인입니다. `skills/in-progress/run-ticket/`에 `scripts/`가 없고, `extras/omp/`에 `extensions/`가 없고, `review` 대체 체인과 "건너뛰고" 문장이 남아 있는 것을 확인했습니다. 단계별 세부를 모두 대조하지는 않았습니다.
- **외부 리뷰 스킬**: 레포 규칙이 정한 리뷰 스킬이 스스로 서브에이전트를 띄우는지, 위임하지 않는 실행 모드가 있는지는 그 스킬에 달려 있습니다. 기본 경로에서 어떻게 둘지는 Q9입니다.
- **영어판**: `docs/en/`의 줄 번호는 `docs/en/skills/run-ticket.md:35` 하나만 대조했습니다. 나머지는 한국어판과 같은 파일이 있다는 것만 확인했습니다.
- **2026-11-19 커밋의 결정**: `81fa296`, `ebf0f73`의 결정을 사용자가 직접 지시했는지는 커밋 본문으로 알 수 없습니다.
- **글 원문**: 글은 주장 목록으로 정리한 것을 썼고 원문과 다시 대조하지 않았습니다.
- **git 추적**: `docs/context/design/`은 git에 추적되지 않습니다. 이 문서와 앞선 세 문서 모두 로컬에만 있습니다.

## 부록: 글 주장 번호

이 문서에서 가리킨 번호만 적습니다.

| 번호 | 주장 |
|---|---|
| A4 | 의도 분류기, 고정된 다단계 파이프라인, 최상단 오케스트레이터가 하던 일의 상당 부분은 이제 모델이 스스로 합니다 |
| A9 | 서브에이전트를 남길 조건 1: 단일 루프의 컨텍스트가 지나치게 커져 측정할 수 있는 성능 저하가 생길 때 |
| A10 | 조건 2: 끝나면 버릴 수 있는 새 컨텍스트 창으로 여러 작업을 병렬로 해야 할 때 |
| A11 | 조건 3: 단일 에이전트가 맞는 도구를 고르지 못하거나 시스템 프롬프트에 서로 부딪히는 지침이 있을 때 |
| A12 | 멀티 에이전트를 쓴다면 가장 단순한 패턴(생성기와 검증기, 오케스트레이터와 서브에이전트)에서 시작하고, 경계를 컨텍스트 기준으로 긋고, 간결한 결과를 돌려받습니다. 예: 독립 리서치, 인터페이스가 분명한 컴포넌트, 블랙박스 검증 |
| A13 | 문제 유형으로 나누면 인계마다 정보가 오가는 "전화 게임"이 되어 충실도가 떨어집니다 |
| A19 | 한 고객은 단일 루프가 멀티 에이전트 하네스보다 약 2배 빠르다고 확인했습니다 |
| A20 | 스킬로 컨텍스트를, 도구 검색으로 도구를 필요할 때만 공개합니다 |
| A21 | 여러 작업의 컨텍스트를 메인 창에 함께 두면 앞 결과를 이을 수 있고, 서브에이전트 요약 모음보다 풍부한 결과가 나옵니다 |
| A22 | 모든 컨텍스트를 긴 시스템 프롬프트에 싣지 않아도 되므로, 서브에이전트로 나누던 주된 이유가 없어집니다 |
| A23 | 새 모델일수록 단일 루프가 더 많은 일을 하고, 단순한 루프는 다음 모델로 옮기기 쉽습니다 |
| A24 | 굳은 멀티 에이전트 구조는 새 모델이 더 많은 일을 하는 것을 막는 경우가 많았습니다 |
| A25 | 단일 루프에는 규율이 필요합니다: 관리된 시스템 프롬프트, 제때 불리는 스킬·도구 설명, 컨텍스트 창·메모리·메모의 신중한 처리 |
| A26 | 모델 하나와 컨텍스트 창 하나가 도구 루프를 돌리고, 턴·비용 예산과 쓰기 게이트는 하네스가 겁니다 |
| A29 | 계획을 쓴 쪽이 실행도 하므로 턴 도중에 계획을 고칠 수 있습니다 |
| A31 | 순서 지정과 도메인 절차는 스킬로 옮깁니다 |
| A32 | 엄격한 제한(검증, 승인 게이트)은 도구로 옮깁니다 |
| A33 | 코드는 거의 늘 필요한 것을 싣고 도구 안의 기계적인 부분을 처리하는 데 씁니다 |
| A36 | 첫 단계는 작업 완료 평가입니다. 중앙의 e2e 세트와 스킬별 작은 세트를 두고, 골든 사례 10개로도 시작할 수 있습니다 |
| A37 | 최종 결과를 루브릭으로 채점하고, 통합 뒤에는 맞는 스킬을 불렀는지와 도구 호출을 봅니다. 구조 비교에는 작업 완료 평가가 가장 중요합니다 |
| A40 | 남기는 서브에이전트는 메인 에이전트가 도구로 부르게 합니다. 완전한 핸드오프는 서브에이전트가 사용자와 직접 대화해야 할 때만 씁니다 |
| A41 | 도구로 부르면 공통 응답 형식을 정하고, 메인이 실제 데이터로 검증하고, 작업 완료 평가의 기준선을 얻습니다 |
| A43 | 서브에이전트의 프롬프트는 스킬로 바꿔 하나씩 통합하고, 통합 전후의 평가를 비교해 남길 쪽을 정합니다 |
| A44 | 최종 점수만 보지 말고 어떤 작업의 결과가 바뀌었는지 봅니다. 통합 뒤 메인이 전문 에이전트에 묻지 않고 스스로 답해 통과하던 작업이 실패한 예가 있었습니다 |
| A45 | 함께 도는 모든 체인과 어기면 안 되는 모든 규칙을 평가에 넣고, 각 작업을 여러 번 돌립니다. 위 문제는 두 번 가운데 한 번만 나타났습니다 |
| A46 | 서브에이전트 하나를 통합하고, 통합한 쪽의 점수가 더 낮을 때만 서브에이전트로 남기고, 되풀이합니다 |
