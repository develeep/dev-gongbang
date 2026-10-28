<p align="right"><b>한국어</b> · <a href="./en/customization.md">English</a></p>

# 스킬 커스텀하기

dev-gongbang의 스킬을 복사해 팀 규칙, 쓰는 모델, 문서 양식에 맞게 고치는 방법을 설명한다. 이 문서를 읽으면 스킬을 어디에 복사해 어떤 파일을 고치고, 고친 스킬을 어떻게 검사하고 시험하는지 알 수 있다.

## 고칠 위치 정하기

플러그인으로 설치한 스킬 파일은 고치지 않는다. 플러그인은 `~/.claude/plugins/cache/dev-gongbang/gongbang/<버전>/`처럼 버전별 폴더에 설치되므로, 새 버전으로 업데이트하면 고친 내용이 새 폴더에 따라오지 않는다.

고치려면 스킬 폴더를 아래 둘 중 한 곳에 복사한다.

| 위치 | 쓰는 범위 | 부르는 이름 |
|---|---|---|
| `~/.claude/skills/<스킬 이름>/` | 모든 프로젝트 | `/<스킬 이름>` |
| `<프로젝트>/.claude/skills/<스킬 이름>/` | 그 프로젝트. 커밋하면 팀이 함께 쓴다 | `/<스킬 이름>` |

복사본은 `gongbang:` 접두사 없이 부른다. 플러그인도 함께 설치돼 있으면 같은 스킬이 `/gongbang:<스킬 이름>`과 `/<스킬 이름>` 두 개로 등록된다. Model-invoked 스킬은 둘 다 Claude가 고를 후보가 되므로, 복사본만 쓰려면 플러그인을 지우거나 복사본의 이름을 바꾼다.

## 스킬 복사해서 고치기

1. 저장소를 클론한다.

   ```bash
   git clone https://github.com/develeep/dev-gongbang.git
   ```

2. 고칠 스킬 폴더를 통째로 복사한다. 번들 파일(`reference/`, `templates/`, `scripts/`)도 함께 옮겨야 한다. 아래 명령은 write-docs를 사용자 스킬로 복사한다.

   ```bash
   cp -r dev-gongbang/skills/productivity/write-docs ~/.claude/skills/
   ```

3. 이름을 바꾸려면 폴더 이름과 `SKILL.md` frontmatter의 `name`을 같은 값으로 바꾼다. 둘이 다르면 검사에서 오류가 난다.
4. 파일을 고친다. 스킬마다 자주 고치는 파일은 [스킬별로 고칠 파일](#스킬별로-고칠-파일)에 있다.
5. [고친 스킬을 검사](#고친-스킬-검사하기)하고 새 세션을 시작한다.

## 스킬별로 고칠 파일

경로는 스킬 폴더 기준이다. 자세한 설명은 각 스킬 문서의 "커스텀" 절에 있다.

| 스킬 | 고칠 파일 | 바뀌는 것 |
|---|---|---|
| [prompt-builder](skills/prompt-builder.md) | `reference/models/<모델>.md` | 모델별 가이드. 새 모델을 추가하면 SKILL.md의 "모델 ID 패턴" 표에도 줄을 추가 |
| | `reference/interview.md` | 인터뷰 항목과 빠른 모드 기본값 |
| [building-skills](skills/building-skills.md) | `references/authoring-rules.md` | 스킬 작성 규칙과 사람 검토 체크리스트 |
| | `scripts/check_skill.py` | 기계로 확인하는 규칙 |
| [write-docs](skills/write-docs.md) | `reference/tech-writing.md` | 기술 문서 유형, 권장 구조, 문장 원칙. 기본은 토스 테크니컬 라이팅 가이드 |
| | `reference/clear-writing.md` | 모든 분야에 적용하는 원칙 |
| [set-guidelines](skills/set-guidelines.md) | `reference/guides-index.md` | 추천할 가이드와 도구 목록 |
| | `templates/rule.md`, `templates/agent-instructions.md` | 규칙 파일과 CLAUDE.md/AGENTS.md 양식 |
| [check-guidelines](skills/check-guidelines.md) | `templates/report.md` | 보고서 양식 |
| [framing-problems](skills/framing-problems.md) | `SKILL.md` | 채울 항목(R1~R6)과 질문 형식 |
| [analyzing-requirements](skills/analyzing-requirements.md) | `SKILL.md` | 문서 템플릿 |
| [set-brief](skills/set-brief.md) | `SKILL.md` | brief 템플릿, 저장 경로 |
| [set-ticket](skills/set-ticket.md) | `SKILL.md` | 티켓 템플릿, 분할 기준 |
| [run-ticket](skills/run-ticket.md) | `SKILL.md` | 티켓 고르는 규칙, 리뷰 순서, 완료 기록 |

set-brief, set-ticket, run-ticket은 같은 형식을 주고받는다. brief의 섹션 이름, `- 작성일:` 줄, 티켓의 `- 상태:` 줄을 바꾸면 세 스킬을 함께 고친다.

## 호출 방식 바꾸기

호출 방식은 `SKILL.md` frontmatter로 정한다.

- **User-invoked로 바꾸기**: `disable-model-invocation: true`를 넣는다. 사용자가 이름을 입력할 때만 실행된다.
- **Model-invoked로 바꾸기**: 그 줄을 지운다. Claude가 `description`을 보고 스킬을 고르므로, `description`에 언제 쓰는지 구체적으로 적는다.

User-invoked 스킬은 다른 스킬이 Skill 도구로 부를 수 없다. 예를 들어 set-brief는 set-ticket을 부르지 않고 사용자에게 실행을 안내한다.

## 고친 스킬 검사하기

저장소의 `scripts/validate.py`에 스킬 폴더 경로를 넘기면 frontmatter 키, `name`과 폴더 이름, 깨진 링크 같은 규칙을 검사한다. PyYAML이 필요하다.

```bash
pip install pyyaml
python3 dev-gongbang/scripts/validate.py ~/.claude/skills/write-docs
```

결과는 JSON으로 나온다. `errors`가 비어 있으면 통과다. `warnings`는 고치거나 그대로 둘 이유를 확인한다.

## 고친 스킬 시험하기

고친 스킬이 실제로 잘 동작하는지 보려면 building-skills를 쓴다. 스킬 폴더 경로를 넘기면 "기존 스킬 개선" 모드로 진행한다.

```
/gongbang:building-skills ~/.claude/skills/write-docs
```

고치기 전 원본을 스냅숏으로 두고, 대표 요청으로 테스트를 돌려 리뷰 페이지를 만든다. 검증 강도에서 "비교"를 고르면 원본과 고친 스킬의 결과를 나란히 비교한다. 자세한 과정은 [building-skills 문서](skills/building-skills.md)에 있다.

## 만드는 중인 스킬을 링크로 쓰기

`in-progress/` 스킬은 복사 대신 심볼릭 링크로 연결할 수 있다. 저장소에서 고친 내용이 다음 세션부터 바로 반영되고, 플러그인처럼 버전을 올릴 필요가 없다.

```bash
dev-gongbang/scripts/link-in-progress.sh
```

`~/.claude/skills/`에 스킬마다 링크를 건다. 일부만 연결하려면 스킬 이름을 뒤에 적고, 특정 프로젝트에서만 쓰려면 그 프로젝트 폴더에서 `--project`를 붙여 실행한다. 링크를 지우려면 `--remove`를 붙인다. 자세한 옵션은 [in-progress README](../skills/in-progress/README.md)에 있다.

## 저장소에 기여하기

고친 내용을 모두가 쓰게 하려면 저장소를 포크해 PR을 보낸다. 스킬을 추가하거나 옮길 때 지킬 규칙은 [.claude/CLAUDE.md](../.claude/CLAUDE.md)에 있다. 변경한 뒤 `scripts/check.py`를 실행해 통과시킨다.
