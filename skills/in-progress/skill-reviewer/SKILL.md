---
name: skill-reviewer
description: SKILL.md를 Claude Code 규칙, 공식 best practice, 이 저장소의 스킬 운영 규칙으로 검사해 스킬별 보고서와 수정 계획을 낸다.
disable-model-invocation: true
argument-hint: "[스킬 이름 또는 경로 ...]"
---

# Skill Reviewer

스킬을 두 갈래로 검사한다. 정해진 규칙은 스크립트가 판정하고, 품질은 루브릭으로 판단한다. 결과를 보고하고 수정 계획을 설명한다. 파일은 고치지 않는다. 사용자가 계획을 보고 고칠 항목을 정하기 때문이다.

검사 대상: $ARGUMENTS (비어 있으면 저장소의 모든 스킬)

## 알아 둘 함정

- Claude Code는 frontmatter YAML이 깨져도 스킬을 로드하고 모든 필드를 버린다. 모르는 키(`disable-model-invokation` 같은 오타)도 경고 없이 무시한다. 그래서 스킬이 "동작하는 것처럼 보여도" 스크립트의 E1·E2·E6 결과를 그대로 믿는다.
- `claude plugin validate`와 `scripts/check.py`는 SKILL.md frontmatter 값을 검사하지 않는다. 그 결과로 이 검사를 대신하지 않는다.
- 기준은 Claude Code다. `argument-hint`, `disable-model-invocation` 같은 CC 전용 키는 정상이다. claude.ai나 API로 배포할 스킬은 스펙 키 6개(`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`)만 쓸 수 있다고 수정 계획에 한 줄 덧붙인다.

## 단계

```
검사 진행:
- [ ] 1. 스크립트 실행
- [ ] 2. 판단 검사
- [ ] 3. 보고서와 수정 계획
```

### 1. 스크립트 실행

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/validate.py $ARGUMENTS
```

- 저장소 루트에서 실행한다. `.claude-plugin/plugin.json`과 `skills/`가 있는 저장소를 찾으면 저장소 규칙(E10~E13, W7, W8)도 검사하고, 못 찾으면 일반 규칙만 검사한다.
- 출력은 JSON이다. `skills[].errors`, `skills[].warnings`, `repo_findings`, `not_found`를 읽는다. 종료 코드 1은 오류가 있다는 뜻이고 실행 실패가 아니다.
- 종료 코드 2는 실행 실패다. stderr 메시지대로 조치하고 다시 실행한다. PyYAML이 없으면 설치해도 되는지 사용자에게 묻는다.
- `not_found`에 이름이 있으면 그 스킬을 찾지 못했다고 알리고 나머지만 계속한다.
- 스크립트 판정은 그대로 보고한다. 오탐이 의심되면 판정을 바꾸지 말고 보고서에 "오탐 의심"과 이유를 붙인다.

### 2. 판단 검사

[reference/rubric.md](reference/rubric.md)를 읽고, 검사 대상 스킬마다 SKILL.md와 참조 파일을 끝까지 읽은 뒤 L1~L16을 판정한다.

- 호출 방식은 frontmatter로 정한다. `disable-model-invocation: true`면 User-invoked라서 L3을 보고, 아니면 Model-invoked라서 L2를 본다.
- E2 같은 frontmatter 오류로 description을 읽을 수 없으면 L1~L3은 "판정 불가"로 둔다.
- 미흡 판정에는 원문 인용을 붙인다. 인용할 원문이 없으면 미흡으로 판정하지 않는다.

### 3. 보고서와 수정 계획

아래 형식으로 보고한다. 스킬 순서는 오류가 많은 스킬부터다. 비어 있는 절은 쓰지 않는다.

````markdown
## skill-reviewer 결과: 스킬 N개 · 오류 X · 경고 Y · 판단 미흡 Z

### <스킬 이름>: 실패 | 통과(경고 있음) | 통과
**오류**
- `파일:줄` · E3 · 메시지
**경고**
- `파일:줄` · W1 · 메시지
**판단 미흡**
- L1 · `파일:줄` "인용" · 무엇이 부족한지 한 문장

### 저장소 전체
- `파일:줄` · E11 · 메시지

## 수정 계획
1. <스킬>: <무엇을 어떻게 고칠지> (해결: E3, L1)
2. ...

트리거율·기준선 대비 개선은 이 검사로 알 수 없으니 `evals/`와 `evals-trigger/` 실행 결과로 확인한다.
````

수정 계획 규칙:

- 오류를 먼저, 그다음 판단 미흡, 경고 순서로 둔다. 오류는 스킬을 로드하거나 배포하는 단계에서 실제로 문제를 일으키기 때문이다.
- 같은 원인의 지적은 한 항목으로 묶고, 해결되는 규칙 ID를 괄호에 적는다.
- 항목마다 고칠 파일과 바꿀 내용을 구체적으로 쓴다. 예: "`description`에서 '~할 때 사용' 문장을 지우고 한 줄 요약만 남긴다".
- 끝에 어느 항목부터 고칠지 묻는다. 사용자가 고르기 전에는 파일을 수정하지 않는다.

## 참조 파일

- [reference/rubric.md](reference/rubric.md): 판단 검사 L1~L16의 기준. 2단계에서 읽는다.
- `scripts/validate.py`: 1단계에서 실행한다. 읽을 필요 없다. 규칙 ID와 메시지는 출력에 들어 있다. PyYAML이 필요하다.
- `scripts/test_validate.py`: `validate.py`를 고친 뒤 실행하는 자체 검사다. 검사 중에는 실행하지 않는다.
