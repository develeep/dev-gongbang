# 테스트 작성·실행·채점

## 목차
- 테스트 케이스 형식
- 작업 폴더 구조
- 실행 띄우기
- assertion 쓰기
- 채점
- 집계와 패턴 분석
- 진단표

## 테스트 케이스 형식

스킬 폴더의 `evals/<case-name>/`에 케이스 하나씩 둔다. 작업 중인 저장소의 CLAUDE.md가 eval 위치를 정해 두었으면(예: 저장소 루트 `evals/<스킬 이름>/`) 그 위치를 쓴다. `claude plugin eval`이 읽는 형식이라, Claude Code 사용자는 나중에 같은 테스트를 CLI나 CI에서 돌릴 수 있다. 형식이 엄격해서 틀리면 CLI가 케이스를 읽지 못한다.

```
evals/<case-name>/
├── prompt.md       # 설정 블록 + 사용자 요청
├── case.yaml       # 이름과 성공의 모습
├── graders/        # assertion 하나당 파일 하나
└── files/          # 입력 파일 (필요할 때만)
```

**case-name**: 소문자·숫자·하이픈, 글자로 시작, 무엇을 시험하는지 몇 단어(`flags-negative-quantity`). `results`, `mocks`, `node_modules`, `files`, `true`, `false`, `null`은 쓰지 않는다.

**prompt.md**: 설정 블록은 그대로 복사하고, 그 아래에 사용자가 입력할 문장 그대로 쓴다. 설정 블록에는 아래 키만 둔다(모르는 키가 있으면 케이스 로드 실패). 설명 문장은 블록 밖 `case.yaml`에 둔다.

```markdown
---
tags: [building-skills]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

사용자 요청 문장
```

**case.yaml**: 버전은 따옴표로 감싼다(숫자로 읽히면 로드 실패). `name`은 폴더 이름과 같게.

```yaml
schema_version: "1.1"
name: flags-negative-quantity
expected_outcome: |
  성공한 결과의 모습을 사람이 읽을 문장으로
```

**graders/NN-few-words.md**: 번호로 순서를 유지한다. 위 블록은 항상 같고, 본문이 assertion 문장이다.

```markdown
---
type: llm
focus: trace
weight: 1
---

summary.md에 총매출 693.5가 적혀 있다
```

assertion이 아직 없으면 자리표시자 `graders/01-expected-output.md`를 둔다(본문: `The result matches this description: <expected_outcome>`). grader가 없는 케이스는 CLI가 읽지 못하기 때문이다. 자리표시자는 채점하지 않는다. 사람이 쓴 다른 `type`(`regex`, `file_exists`, `tool_used` 등) grader가 있으면 그대로 두고, 설명된 내용을 출력과 기록으로 최대한 채점한다.

**입력 파일**: `files/`에 두고, 프롬프트 끝에 `Input files: a.csv, b.txt` 줄을 넣고, `prompt.md` 옆에 `place-files.sh`(`#!/usr/bin/env bash` / `set -eu` / `cp -R "$(dirname "$0")/files/." .`)를 두고, `case.yaml`에 `context:` / `  scaffold_script: place-files.sh`를 적는다.

**기존 `evals/evals.json`**(옛 형식)이 있으면 읽기만 하고 고치지 않는다. 그 테스트도 함께 돌리고, 바꿔야 하면 같은 이름의 케이스 폴더로 새로 쓴다.

**케이스 고르기**: K8 대표 요청에서 시작한다. 말투(격식/구어), 상세도(짧은 요청/경로·컬럼명·배경이 있는 요청), 경계 상황(잘못된 입력, 지시가 모호해지는 경우)이 섞이게 한다. 처음에는 2~3개면 충분하다.

## 작업 폴더 구조

스킬 폴더의 형제인 `<name>-workspace/`에 둔다. 반복마다 `iteration-N/`, 그 안에 케이스 이름 폴더. 반복 사이에 케이스 이름을 바꾸지 않는다. 리뷰 페이지가 이름으로 이전 결과와 맞춘다.

```
<name>-workspace/
├── skill-snapshot/              # 모드 B의 수정 전 사본
└── iteration-1/
    ├── <case-name>/
    │   ├── eval_metadata.json   # {"eval_name", "prompt", "assertions": [...]}
    │   ├── with_skill/
    │   │   ├── outputs/         # 실행이 만든 파일 + transcript.md
    │   │   ├── grading.json
    │   │   └── timing.json
    │   └── without_skill/       # 또는 old_skill/ (모드 B)
    ├── benchmark.json
    ├── benchmark.md
    └── review.html
```

한 설정을 여러 번 돌리면 `with_skill/run-1/`, `run-2/`처럼 실행마다 폴더를 둔다. `eval_metadata.json`은 반복마다 새로 쓴다. 리뷰 페이지는 프롬프트를 여기서 읽는다(설정 블록 제외한 본문).

## 실행 띄우기

한 턴에 모든 실행을 띄운다. 검증 1단계면 `with_skill`만, 2단계 이상이면 기준 실행도 같은 턴에. 따로 띄우면 끝나는 시점이 어긋난다. 각 실행은 깨끗한 컨텍스트에서 시작해야 스킬에 적힌 것만 따르므로 서브에이전트를 쓴다. 서브에이전트가 없는 환경이면 케이스를 하나씩 직접 수행하되, 스킬을 쓴 사람이 스스로 실행하는 것이라 엄밀하지 않다고 알리고 기준 실행은 건너뛴다.

```
Execute this task:
- Skill path: <skill-folder>        (기준 실행: without_skill이면 이 줄을 빼고, old_skill이면 스냅숏 경로)
- Task: <prompt.md 본문>
- Input files: <files/ 경로들 또는 none>
- If the task asks the user a question, answer with: <확인받은 예상 답변 또는 "none">
- Save outputs to: <workspace>/iteration-<N>/<case-name>/<config>/outputs/
- Outputs to save: <스킬이 만들기로 한 결과물>
- Also write outputs/transcript.md: the steps you took in order, files you read, questions you would have asked, and your final reply to the user.
```

`transcript.md`는 채점(절차 확인)과 진단(어디서 헤맸는지)에 쓴다. K7에 모델이 여럿이고 2단계 이상이면 Agent 도구의 `model` 옵션으로 모델마다 실행하고 설정 이름에 붙인다(`with_skill-sonnet`).

완료 알림이 올 때마다 바로 실행 폴더에 `timing.json`을 쓴다: `{"total_tokens": N, "duration_ms": N, "total_duration_seconds": N}`.

## assertion 쓰기

실행이 도는 동안 쓴다. 아래 순서로 뽑고, 각각의 근거 줄을 사용자에게 함께 보여 준다.

1. **K9 gotcha 하나당 하나.** "이 함정을 피했다". 스킬이 없으면 실패할 가능성이 커서 차이가 가장 잘 드러난다
2. **출력 형식.** 스킬이 정한 구조, 파일, 섹션이 있다
3. **고정 절차(K5).** 순서가 중요한 단계를 지켰다 (transcript로 확인)
4. **K8 시나리오의 기대 결과**

좋은 assertion은 객관적으로 확인되고, 이름만 봐도 무엇을 보는지 안다. "출력이 좋다"는 너무 모호하고, "정확히 'Total: $X'라는 문구를 쓴다"는 너무 깨지기 쉽다. 결과 자체에 대해 쓴다("summary.md에 X가 있다"), 이 작업 폴더 경로에 대해 쓰지 않는다. 문체, 설계의 좋고 나쁨처럼 판단이 필요한 것은 assertion으로 만들지 말고 사람 리뷰에 맡긴다.

`graders/`에 한 파일씩 쓰고 자리표시자를 지운 뒤, 같은 문장을 `eval_metadata.json`의 `assertions`에 넣는다.

## 채점

실행 폴더마다 `grading.json`을 쓴다. 서브에이전트에 맡겨도 되고 직접 해도 된다. 기계로 확인할 수 있는 것(파일 존재, JSON 유효성, 행 수, 특정 값)은 스크립트로 확인한다. 빠르고 반복 가능하다.

원칙:
- **통과에는 구체적 증거가 필요하다.** 애매하면 실패다. "요약을 포함한다"인데 "요약" 제목 아래 모호한 한 문장뿐이면 실패
- 증거는 출력이나 기록을 인용하거나 가리킨다. 의견만 적지 않는다
- 출력 파일을 직접 열어 본다. transcript의 "만들었다"는 말만 믿지 않는다
- assertion 자체도 비판한다: 스킬과 상관없이 늘 통과할 것(너무 쉬움), 좋은 출력도 실패할 것(너무 어려움), 출력만으로 확인할 수 없는 것

```json
{
  "expectations": [
    {"text": "summary.md에 총매출 693.5가 적혀 있다", "passed": true, "evidence": "summary.md 3행: '총매출: 693.5'"}
  ],
  "summary": {"passed": 1, "failed": 0, "total": 1, "pass_rate": 1.0},
  "assertion_notes": ["02번은 스킬 없이도 통과할 것으로 보임"]
}
```

필드 이름은 `text`, `passed`, `evidence`를 그대로 쓴다. 집계·리뷰 스크립트가 이 이름을 읽는다.

## 집계와 패턴 분석

2단계 이상이면 `python3 scripts/aggregate.py <workspace>/iteration-N`. `benchmark.json`과 `benchmark.md`가 생긴다. 설정별 통과율·시간·토큰의 평균과 표준편차, 설정 간 차이, assertion별 판별력(스킬 있을 때만 통과 / 둘 다 통과 / 둘 다 실패)이 들어간다.

숫자가 숨기는 것을 본다:
- **둘 다 늘 통과하는 assertion**: 판별력이 없다. 빼거나 바꾼다
- **둘 다 늘 실패하는 assertion**: assertion이 틀렸거나 케이스가 너무 어렵다
- **스킬 있을 때만 통과**: 스킬이 값을 더하는 곳. 어떤 지시 덕분인지 확인한다
- **같은 케이스에서 결과가 흔들림**: 지시가 모호하다. 예시나 구체 지침을 더한다
- **시간·토큰이 튀는 케이스**: transcript에서 병목을 찾는다

stddev는 같은 케이스를 여러 번 돌렸을 때만 의미가 있다. 초기에는 통과 개수와 차이를 본다.

## 진단표

실패한 assertion, 피드백, transcript를 하나씩 원인에 대응시킨다. 원인이 사양 항목으로 이어지면 그 항목을 다시 묻는 편이 빠를 때가 많다.

| 증상 | 의심할 항목 | 고치는 방향 |
|---|---|---|
| "주의할 점"의 함정에 빠짐 | K9 | 함정이 생기는 상황과 이유를 더 구체적으로 (형식 수정) |
| 단계를 건너뛰거나 순서가 틀림 | K5, K4 | 체크리스트와 검증 루프. 자유도가 실제보다 높게 잡혔는지 확인 |
| 경직되어 상황에 안 맞게 행동 | K4 | 규칙 대신 판단 기준과 이유 |
| 출력 형식이 어긋남 | 출력 형식 | 템플릿 (예시 추가는 내용 수정) |
| 기준 없이 판단해서 결과가 흔들림 | 판단 기준 | prompt-builder "다음 단계"의 미승인 제안부터 대조 |
| 스킬 없는 실행과 차이 없음 | K3, 간결성 | 모델이 아는 설명을 빼고 이 작업에만 필요한 지식에 집중 |
| 여러 방법을 시도하다 헤맴 | 지시 모호, 선택지 과다 | 기본값 하나 + 예외 하나 |
| 관련 없는 지시를 따라감 | 상세도 과다 | 그 지시를 지우거나 조건부 참조 파일로 |
| 참조 파일을 안 읽거나 늦게 읽음 | 점진적 공개 | 링크에 읽을 조건을 분명히. 자주 필요하면 SKILL.md로 |
| 실행마다 비슷한 보조 스크립트를 새로 씀 | K6 | 그 스크립트를 `scripts/`에 넣고 쓰게 함 |

지시를 더해도 통과율이 오르지 않으면 과잉 제약일 수 있다. 지시를 빼고 결과가 유지되는지 본다.
