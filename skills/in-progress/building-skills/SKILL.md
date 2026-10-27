---
name: building-skills
description: Claude 공식 skill best practice와 Agent Skills 명세에 맞춰 스킬을 완성한다. prompt-builder가 만든 SKILL.md 초안을 이어받아 검증·보완하거나, 대화 기록·런북·코드 같은 실제 자료에서 스킬을 새로 만든다. 정적 검사, 실행 테스트, 사람 리뷰, 수정 반복까지 맡는다. 사용자가 /building-skills로 이름을 부르거나 "이 초안으로 스킬 완성해줘"처럼 이 스킬을 명시적으로 요청할 때만 사용한다.
argument-hint: "[스킬 폴더 경로, SKILL.md 초안, 또는 만들 스킬 설명]"
disable-model-invocation: true
---

# Building Skills

스킬을 "명세에 맞고, 실제로 돌려 봤을 때 스킬 없이 할 때보다 낫다"는 상태까지 끌고 간다. 작성 규칙은 [references/authoring-rules.md](references/authoring-rules.md)에 모아 두었고, 기계로 확인할 수 있는 규칙은 `scripts/check_skill.py`가 검사한다.

## 핵심 규칙

1. **스킬 내용의 출처는 사용자 자료, 사용자 답변, 승인받은 제안뿐이다.** 내용이란 절차, 규칙, 판단 기준, gotcha, 예시를 말한다. LLM의 일반 지식만으로 채운 스킬은 "에러를 적절히 처리한다" 같은 쓸모없는 문장이 되기 쉽다. Claude가 보태고 싶은 내용은 넣을 문장 그대로 제안해 승인받는다. 문구 다듬기, 순서 조정, 참조 파일 분리, 규칙에 이유 붙이기 같은 형식 수정은 바로 하고 무엇을 바꿨는지 알린다.
2. **Claude가 이미 아는 것은 넣지 않는다.** 문단마다 "이 지시가 없으면 실행하는 모델이 틀리는가?"를 묻고, 아니면 뺀다. 스킬은 컨텍스트를 대화·다른 스킬과 나눠 쓴다.
3. **채점 기준은 스킬이 약속한 것에서만 뽑는다.** assertion마다 근거가 된 SKILL.md의 줄이나 시나리오의 기대 결과를 밝힌다. 스킬이 약속하지 않은 품질을 채점하면 통과율이 스킬이 아니라 채점자의 취향을 잰다.
4. **사람이 먼저 본다.** 실행이 끝나면 직접 분석하기 전에 리뷰 페이지부터 만들어 전달한다. Claude가 먼저 결론을 내면 사용자가 그 결론에 끌려간다.
5. **검증 강도는 사용자가 고른다.** 기본은 가장 가벼운 단계이고, 더 무거운 단계는 비용을 알린 뒤 고를 때만 진행한다.

## 주의할 점

- **인터뷰형 스킬은 서브에이전트 실행에서 멈춘다.** 테스트 대상 스킬이 사용자에게 질문하면 서브에이전트에는 답할 사람이 없다. 시나리오마다 예상 답변을 정해 실행 프롬프트에 함께 넘기고, 그 답변은 사용자에게 확인받는다.
- **`disable-model-invocation`은 실행 테스트와 무관하다.** 실행 서브에이전트는 SKILL.md를 직접 읽는다. 호출 방식은 description 검증에서만 의미가 있다.
- **timing은 완료 알림에서만 얻는다.** 서브에이전트 완료 알림의 `total_tokens`, `duration_ms`는 다른 곳에 남지 않으므로 알림이 올 때마다 바로 `timing.json`에 쓴다.
- **prompt-builder의 "다음 단계" 경고를 버리지 않는다.** 승인받지 못한 보완 제안, 생략·기본값 항목, 통과하지 못한 검수 항목은 실패 원인 후보 1순위다.
- **저장 경로에 따라 frontmatter가 잘린다.** claude.ai/Cowork의 `propose_skills` 저장 카드는 `name`, `description`과 본문만 남기고 `disable-model-invocation` 같은 다른 키를 버리며, 번들 파일도 담지 못한다. User-invoked 스킬은 description에도 "명시적으로 요청할 때만 사용한다"를 넣어 두고, 번들 파일이나 추가 frontmatter가 있으면 `.skill` 패키지로 전달한다.

## 워크플로

첫 응답에 아래 체크리스트를 한 번 보여 주고, 단계가 바뀔 때만 갱신한다.

```
진행 상황:
- [ ] 1. 입력 파악과 모드 결정
- [ ] 2. 사양 확정
- [ ] 3. 작성 또는 보완
- [ ] 4. 정적 검사 (통과할 때까지 반복)
- [ ] 5. 검증 강도 선택
- [ ] 6. 테스트 작성·실행·채점
- [ ] 7. 리뷰 페이지로 사용자 리뷰
- [ ] 8. 진단과 수정 → 6으로 반복
- [ ] 9. 마무리와 전달
```

### 1. 입력 파악과 모드 결정

입력을 보고 모드를 하나 고른다. 애매하면 묻는다.

| 모드 | 입력 | 2단계에서 읽을 곳 |
|---|---|---|
| A. prompt-builder 이어받기 | prompt-builder 출력(설계 요약, SKILL.md 코드블록, 다음 단계) | [references/intake.md](references/intake.md)의 "모드 A" |
| B. 기존 스킬 개선 | 스킬 폴더나 SKILL.md | intake.md의 "모드 B" |
| C. 단독 신규 | 만들 스킬 설명, 대화 기록, 런북, 코드, 리뷰 코멘트 같은 자료 | intake.md의 "모드 C" |

코드블록으로만 받은 스킬은 작업 폴더에 `<name>/` 폴더를 만들어 파일로 옮긴다. 테스트 결과는 형제 폴더 `<name>-workspace/`에 둔다. 모드 B는 수정 전에 `<name>-workspace/skill-snapshot/`으로 복사해 둔다. 이 스냅숏이 비교 기준이 된다.

### 2. 사양 확정

intake.md의 해당 모드 절차로 사양표(K1~K10)를 채우고 `항목 | 값 | 출처 | 상태(확인됨/모호/없음)`로 보여 준다. 모호·없음 항목만 묻는다. 대표 요청(K8)이 없으면 지어내지 말고 받는다. 사용자가 맡기면 초안 3개를 보여 주고 승인받은 것만 쓴다.

### 3. 작성 또는 보완

[references/authoring-rules.md](references/authoring-rules.md)를 읽고 그 규칙대로 SKILL.md와 번들 파일을 쓰거나 고친다. 모드 A·B에서는 기존 문장을 존중한다. 형식 문제는 고치고, 내용 문제는 핵심 규칙 1대로 제안한다.

### 4. 정적 검사

```bash
python3 scripts/check_skill.py <skill-folder>
```

`scripts/`는 이 스킬 폴더 기준 경로다. ERROR는 모두 고치고 다시 돌린다. WARN은 고치거나, 고치지 않을 이유를 사용자에게 한 줄로 알린다. 스크립트가 못 보는 항목은 authoring-rules.md 끝의 "사람 검토 체크리스트"로 점검한다. 결과를 `항목 | 결과 | 근거` 표로 보여 준다.

### 5. 검증 강도 선택

AskUserQuestion으로 고르게 한다. 단계는 누적된다.

| 단계 | 하는 일 | 비용 |
|---|---|---|
| 1. 점검 (권장, 기본) | 대표 요청을 스킬을 쓴 실행으로만 돌리고 채점·리뷰한다 | 서브에이전트 3개 안팎 |
| 2. 비교 | 1에 더해 기준 실행(모드 A·C는 스킬 없이, 모드 B는 스냅숏으로)을 함께 돌려 benchmark로 비교한다. K7에 모델이 여럿이면 모델마다 돌린다 | 서브에이전트 6개 이상 |
| 3. description | 2에 더해 description의 실행 여부를 측정하고 다듬는다 | `claude -p` 수십 회 이상 |

K10=User-invoked이면 3단계를 빼고, 이름으로 부르는 스킬이라 실행 여부 측정이 의미 없다고 한 줄로 알린다. 사용자가 테스트 없이 끝내겠다고 하면 9단계로 가되, 실행 검증을 하지 않았다는 사실을 마무리 응답에 남긴다.

### 6. 테스트 작성·실행·채점

[references/evaluation.md](references/evaluation.md)를 읽고 그대로 한다. 요약하면: 대표 요청 하나당 `evals/<case-name>/` 하나를 만들고, 한 턴에 모든 실행(2단계 이상이면 기준 실행까지)을 띄우고, 실행이 도는 동안 assertion을 쓰고, 끝나면 채점한 뒤 2단계 이상이면 집계한다.

```bash
python3 scripts/aggregate.py <workspace>/iteration-N
```

### 7. 리뷰 페이지로 사용자 리뷰

분석보다 먼저 한다.

```bash
python3 scripts/review.py <workspace>/iteration-N --skill-name <name> \
  [--previous <workspace>/iteration-<N-1>]
```

`<workspace>/iteration-N/review.html`이 생긴다. 파일을 사용자에게 전달하고, 케이스마다 피드백을 적은 뒤 "피드백 내보내기"를 누르면 `feedback.json`이 내려받아진다고 안내한다. 사용자가 끝났다고 하면 그 파일을 받아(채팅 첨부나 연결된 폴더) `iteration-N/feedback.json`으로 둔다. 빈 피드백은 괜찮다는 뜻이다.

### 8. 진단과 수정

실패한 assertion, 사용자 피드백, 실행 기록(transcript)을 함께 보고 evaluation.md의 "진단표"로 원인을 찾는다. 수정안은 `번호 | 근거(케이스·assertion·피드백) | 바꿀 문장 전/후 | 형식/내용` 표로 보여 준다. 형식 수정은 바로 적용하고 내용 수정은 번호별로 승인·수정·제외를 받는다.

테스트 몇 개에만 맞춘 수정은 피한다. 스킬은 앞으로 들어올 수많은 요청에서 쓰인다. 고친 뒤 4단계 정적 검사를 다시 돌리고, 같은 케이스 이름으로 `iteration-<N+1>/`에서 6단계부터 반복한다. 사용자가 만족하거나, 피드백이 모두 비었거나, 더 나아지지 않으면 멈춘다.

3단계(description)를 골랐으면 반복이 끝난 뒤 [references/description-tuning.md](references/description-tuning.md)대로 진행한다.

### 9. 마무리와 전달

정적 검사를 마지막으로 한 번 더 돌려 ERROR가 없는지 확인한 뒤 전달한다.

- **SKILL.md 하나뿐이고 추가 frontmatter가 없을 때**: `propose_skills`가 있으면 저장 카드를 띄운다.
- **그 외**: `python3 scripts/package.py <skill-folder> <out-dir>`로 `<name>.skill`을 만들어 전달한다. Claude Code라면 `~/.claude/skills/<name>/`(사용자) 또는 `.claude/skills/<name>/`(프로젝트)에 복사하는 방법도 알린다.
- 모드 A로 시작했고 validating-skills나 이전 판이 함께 설치돼 있으면, 역할이 겹치는 스킬을 정리할지 묻는다.

마무리 응답에는 다음을 넣는다.

- 최종 통과율과 반복 횟수 (2단계 이상이면 기준 실행과의 차이)
- 반영한 수정 목록 (형식/내용 구분)
- 남은 WARN, 남은 실패, 승인받지 못한 수정안 (짧게 줄일 때도 빼지 않는다)
- 실행 검증을 건너뛰었거나 K7의 일부 모델에서만 시험했다면 그 사실

## 번들 파일

| 파일 | 언제 |
|---|---|
| [references/intake.md](references/intake.md) | 2단계. 고른 모드의 절만 읽는다 |
| [references/authoring-rules.md](references/authoring-rules.md) | 3단계 작성·보완, 4단계 사람 검토, 8단계 수정할 때 |
| [references/evaluation.md](references/evaluation.md) | 6단계 시작할 때, 8단계 진단할 때 |
| [references/description-tuning.md](references/description-tuning.md) | 5단계에서 3단계(description)를 골랐을 때만 |
| `scripts/check_skill.py` | 4단계와 9단계에 실행. 명세·best practice 정적 검사 |
| `scripts/aggregate.py` | 6단계, 검증 2단계 이상에서 실행. benchmark 집계 |
| `scripts/review.py` | 7단계에 실행. 정적 리뷰 페이지 생성 |
| `scripts/trigger_eval.py` | description-tuning.md가 시킬 때 실행. `claude` CLI 필요 |
| `scripts/package.py` | 9단계에 실행. `.skill` 패키지 생성 |

스크립트는 Python 3.9+ 표준 라이브러리만 쓴다. 모두 실행용이며 읽을 필요는 없다. `--help`로 옵션을 볼 수 있다.
