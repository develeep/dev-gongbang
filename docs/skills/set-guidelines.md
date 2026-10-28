<p align="right"><b>한국어</b> · <a href="../en/skills/set-guidelines.md">English</a></p>

[README](../../README.md) › [문서](../README.md) › set-guidelines

# set-guidelines

레포의 언어와 프레임워크에 맞는 코딩 가이드를 [awesome-guidelines](https://github.com/Kristories/awesome-guidelines) 목록에서 골라 원문에서 규칙을 뽑습니다. 뽑은 규칙으로 `.claude/rules/` 규칙 파일, CLAUDE.md/AGENTS.md, 린터·포매터 설정 중 고른 것을 만듭니다. 파일은 최종 승인을 받은 뒤에만 씁니다.

| 항목 | 값 |
|---|---|
| 버킷 | engineering |
| 호출 방식 | User-invoked |
| 호출 | `/gongbang:set-guidelines` |
| 원문 | [SKILL.md](../../skills/engineering/set-guidelines/SKILL.md) |

**목차**: [언제 쓰나](#언제-쓰나) · [준비물](#준비물) · [진행 과정](#진행-과정) · [결과물](#결과물) · [커스텀](#커스텀) · [함께 쓰는 스킬](#함께-쓰는-스킬)

## 언제 쓰나

- 레포에 코딩 규칙이나 린터·포매터 설정이 없어 새로 만들 때
- 이미 있는 규칙을 고치거나 보탤 때
- 기존 규칙을 걷어 내고 새로 정할 때

## 준비물

- 가이드 원문을 읽으려면 웹에 접근할 수 있어야 합니다. 링크가 깨졌거나 읽을 수 없는 가이드는 건너뜁니다.
- 린터·포매터 설정을 만들면 그 도구로 설정을 확인합니다. 도구가 설치돼 있지 않으면 설치해서 확인할지 묻습니다.

## 진행 과정

1. 레포의 언어와 프레임워크를 파악해 확인받습니다. 이미 있는 컨벤션 문서, CLAUDE.md/AGENTS.md, `.claude/rules/`, 린터·포매터 설정도 찾습니다.
2. 기존 규칙이 있으면 처리 방식을 고릅니다.
   - **개선·추가**: 기존 규칙을 유지하고 고칠 점과 더할 규칙을 추천합니다.
   - **초기화**: 기존 규칙을 걷어 내고 새로 정합니다.
3. 가이드와 린터·포매터를 추천받아 고릅니다. 목록에 없는 도구를 추천하면 "awesome-guidelines 목록 밖"이라고 표시합니다.
4. 고른 가이드의 원문을 읽어 규칙을 뽑습니다. 가이드끼리 충돌하는 규칙은 나란히 보여 주고 하나를 고르게 합니다.
5. 만들 산출물과 경로를 고르고, 만들거나 바꾸거나 지울 파일 목록을 보고 최종 승인합니다.
6. 승인한 파일만 씁니다. 린터·포매터 설정은 도구를 실행해 오류 없이 읽히는지 확인합니다.

팀 규칙은 가이드에서 뽑은 규칙보다 앞섭니다. 팀 규칙이란 레포에 이미 있는 규칙과, 산출물을 만든 뒤 CLAUDE.md/AGENTS.md의 "팀 규칙" 절에 추가하는 규칙입니다.

## 결과물

고른 것만 만듭니다.

- **분야별 규칙 파일** `.claude/rules/<분야>.md`: `paths`에 적용할 파일 패턴을 적으면 그 파일을 다룰 때만 로드됩니다. `paths`가 없으면 CLAUDE.md처럼 세션마다 로드됩니다.
- **CLAUDE.md / AGENTS.md**: 핵심 규칙만 두고 세부는 규칙 파일로 옮깁니다. 둘 다 만들면 CLAUDE.md에 `@AGENTS.md` 줄을 넣습니다. Claude Code는 둘이 함께 있으면 CLAUDE.md만 읽기 때문입니다.
- **린터·포매터 설정**: 고른 도구의 문서를 따릅니다.

## 커스텀

| 바꾸고 싶은 것 | 고칠 파일 |
|---|---|
| 추천할 가이드와 도구 목록 | `reference/guides-index.md` (awesome-guidelines README 스냅샷, 2026-10-28) |
| 규칙 파일 양식 | `templates/rule.md` |
| CLAUDE.md / AGENTS.md 양식 | `templates/agent-instructions.md` |

사내 가이드를 추천 후보에 넣으려면 `reference/guides-index.md`에서 그 언어나 도구의 절에 링크를 추가하세요. 복사해서 고치는 방법은 [커스텀 가이드](../customization.md)를 보세요.

## 함께 쓰는 스킬

- **check-guidelines**: 만든 규칙으로 코드를 검사합니다.

---

← 이전: [write-docs](write-docs.md) · [문서 목록](../README.md) · 다음: [framing-problems](framing-problems.md) →
