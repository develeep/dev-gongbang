# Orca 워커 절차 등록

run-ticket 스킬은 워커 도구 절차가 지정돼 있을 때만 여러 티켓을 워커로 병렬 실행하고 교차 리뷰를 워커에 맡깁니다. 지정된 절차가 없으면 티켓을 서브에이전트로 차례로 실행합니다. 이 문서는 Orca 절차([worker-procedure.md](worker-procedure.md))를 에이전트 규칙 파일(`CLAUDE.md`, `AGENTS.md`)에 지정하는 방법을 설명합니다. Orca 설치와 확인 방법은 [Orca 오케스트레이션 설정](../../docs/orca-orchestration.md)에 있습니다.

## 등록하기

1. **절차 문서의 경로를 정합니다.** 조정자 세션(run-ticket이나 run-flow를 실행하는 세션)이 읽을 수 있는 경로여야 합니다.
   - 이 저장소를 클론해 두었으면 `<dev-gongbang 경로>/extras/orca/worker-procedure.md`의 절대 경로를 씁니다. 저장소를 갱신하면 절차도 함께 갱신됩니다.
   - 팀이 함께 쓰는 레포면 `worker-procedure.md`를 그 레포에 복사해 커밋하고(예: `docs/agents/orca-worker-procedure.md`) 레포 기준 경로를 씁니다. 이 저장소의 절차가 바뀌면 다시 복사합니다.
2. **규칙 파일에 아래 "붙일 문구"를 넣고 경로를 바꿉니다.**
   - 모든 프로젝트에서 쓰려면 사용자 전역 규칙 파일에 넣습니다. Claude Code는 `~/.claude/CLAUDE.md`, Codex는 `~/.codex/AGENTS.md`, omp는 `~/.omp/agent/AGENTS.md`입니다.
   - 한 레포에서만 쓰려면 그 레포 루트의 `CLAUDE.md`나 `AGENTS.md`에 넣습니다.
   - 경로는 글로만 적습니다. `@<경로>`처럼 파일을 가져오는 줄로 넣으면 워커를 쓰지 않는 세션도 절차 전문을 읽습니다.
   - omp에서 `~/.omp/agent/AGENTS.md`가 이 저장소의 `extras/omp/AGENTS.md`를 가리키는 링크면, 그 파일에 문구를 넣는 것은 클론한 저장소의 파일을 고치는 것입니다. 저장소를 갱신할 때 충돌하지 않게 하려면 링크 대신 복사본을 두고 고치거나, 레포의 `AGENTS.md`에 넣습니다.
3. **확인합니다.** 새 세션에서 "run-ticket의 워커 도구 절차가 무엇인지 알려 줘"라고 물어 1번에서 정한 경로가 나오는지 봅니다. 여러 티켓을 실행할 때 병렬 실행 조건을 만족하고 이 절차가 선택되면, run-ticket이 계획 승인을 받을 때 워커를 띄울 도구로 Orca를 보여 줍니다.

## 붙일 문구

```markdown
## 워커 도구 절차

run-ticket의 워커 도구 절차는 Orca 절차입니다. 여러 티켓을 병렬로 실행하거나 교차 리뷰를 워커에 맡길 때 `<worker-procedure.md 경로>`를 읽고 따릅니다.
```

## 워커 모델 정하기 (선택)

절차는 구현 워커와 교차 리뷰 워커의 모델과 effort를 에이전트 규칙에서 찾습니다. 정하려면 위 문구 아래에 다음 줄을 더하고 값을 바꿉니다. 정하지 않으면 구현 워커는 모델 인자 없이 조정자 세션과 같은 에이전트로 뜹니다.

```markdown
- 티켓 구현 워커는 `--model <모델> --effort <effort>`로 띄웁니다.
- 교차 리뷰 워커는 구현한 모델이 Claude면 Codex 워커를 `--model <모델> --effort <effort>`로, Claude가 아니면 Claude Code 워커를 `--model <모델> --effort <effort>`로 띄웁니다. 구현한 모델과 같은 회사의 워커는 교차 리뷰가 되지 않습니다.
- 사용자가 워커의 대화를 이어 쓰려고 하면 `--keep-open`으로 띄웁니다.
```

omp 설정(`extras/omp/`)의 역할별 모델을 쓰면 값은 다음과 같습니다.

| 워커 | 인자 |
|---|---|
| 티켓 구현 워커 (조정자 세션과 같은 omp 에이전트) | `--model @worker`. Effort는 omp 역할 `worker`에 들어 있으므로 `--effort`를 붙이지 않습니다 |
| 교차 리뷰 워커, 구현한 모델이 Claude일 때 (Codex) | `--model gpt-6.2-sol --effort high` |
| 교차 리뷰 워커, 구현한 모델이 Claude가 아닐 때 (Claude Code) | `--model claude-opus-5-5 --effort medium` |

## Paseo 절차와 함께 지정할 때

두 절차를 함께 지정하면 run-ticket은 규칙에 적힌 순서로 사용 조건을 확인해 처음 되는 절차를 씁니다. 먼저 쓸 도구를 위에 적습니다. 요청에 "Paseo로"처럼 도구를 적으면 순서와 상관없이 그 도구의 절차를 먼저 확인합니다. 사용 조건을 만족하지 못하면 규칙에 적힌 다음 절차를 봅니다.

```markdown
## 워커 도구 절차

run-ticket의 워커 도구 절차는 아래 순서로 씁니다. 여러 티켓을 병렬로 실행하거나 교차 리뷰를 워커에 맡길 때, 위에서부터 사용 조건을 확인해 처음 되는 절차의 파일을 읽고 따릅니다.

1. Orca: `<dev-gongbang 경로>/extras/orca/worker-procedure.md`
2. Paseo: `<dev-gongbang 경로>/extras/paseo/worker-procedure.md`
```
