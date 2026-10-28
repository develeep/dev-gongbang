<p align="center">
  <img src="./assets/gongbang-logo.gif" alt="Gongbang" width="800">
</p>

<h1 align="center">
    dev-gongbang
</h1>

<p align="center">
    개발 과정에서 쓰는 Claude Code 스킬 모음.
</p>

<p align="center">
    <b>한국어</b> · <a href="./README.en.md">English</a>
</p>

요청을 구체화하고, 프롬프트와 스킬을 만들고, 문서를 쓰고, 코드 규칙을 정하고 검사하는 일을 Claude Code 스킬로 돕습니다. 플러그인 하나로 설치하고, 필요하면 스킬을 복사해 내 상황에 맞게 고쳐 쓸 수 있습니다. 스킬 파일은 한국어로 쓰여 있습니다.

**목차**: [설치](#설치) · [스킬](#스킬) · [만드는 중인 스킬](#만드는-중인-스킬) · [상황별로 고르기](#상황별로-고르기) · [커스텀](#커스텀) · [기여](#기여) · [전체 문서 목록](docs/README.md)

## 설치

마켓플레이스를 추가하고 `gongbang` 플러그인을 설치하세요.

```bash
claude plugin marketplace add develeep/dev-gongbang
claude plugin install gongbang@dev-gongbang
```

설치한 스킬은 `/gongbang:<스킬 이름>`으로 부릅니다. 예: `/gongbang:prompt-builder`

만드는 중인 스킬도 쓰려면 `gongbang-dev`를 함께 설치하세요.

```bash
claude plugin install gongbang-dev@dev-gongbang
```

### 업데이트

플러그인은 `plugin.json`의 `version`이 바뀔 때만 갱신됩니다. 버전마다 바뀐 내용은 [Releases](https://github.com/develeep/dev-gongbang/releases)에서 볼 수 있습니다. 마켓플레이스를 갱신한 뒤 플러그인을 업데이트하고 Claude Code를 다시 시작하세요.

```bash
claude plugin marketplace update dev-gongbang
claude plugin update gongbang@dev-gongbang
```

## 스킬

스킬은 호출 방식에 따라 둘로 나뉩니다.

- **User-invoked**: 사용자가 `/gongbang:<스킬 이름>`을 입력할 때만 실행됩니다.
- **Model-invoked**: 사용자가 이름을 입력해도 되고, 요청이 스킬 설명과 맞으면 Claude가 스스로 골라 실행하기도 합니다.

스킬 이름을 누르면 사용 문서로, `SKILL.md`를 누르면 스킬 원문으로 갑니다. 모든 문서는 [문서 목록](docs/README.md)에서 찾을 수 있습니다.

### User-invoked

- [prompt-builder](docs/skills/prompt-builder.md): 모델별 가이드에 맞춰 시스템 프롬프트, CLAUDE.md, SKILL.md를 인터뷰로 설계하거나 초안을 고칩니다. `/gongbang:prompt-builder [초안 경로 또는 설명]` · [SKILL.md](skills/productivity/prompt-builder/SKILL.md)
- [building-skills](docs/skills/building-skills.md): SKILL.md 초안이나 대화 기록·런북·코드 같은 자료로 스킬을 완성하고, 정적 검사·실행 테스트·사람 리뷰·수정을 반복합니다. `/gongbang:building-skills [스킬 폴더 경로, SKILL.md 초안, 또는 만들 스킬 설명]` · [SKILL.md](skills/productivity/building-skills/SKILL.md)
- [write-docs](docs/skills/write-docs.md): 분야·독자·목적·톤·자료를 질문으로 정한 뒤 글 초안을 쓰거나, 가져온 초안과 기존 문서를 고칩니다. `/gongbang:write-docs [쓰거나 고칠 글에 대한 요청]` · [SKILL.md](skills/productivity/write-docs/SKILL.md)
- [set-guidelines](docs/skills/set-guidelines.md): awesome-guidelines에서 레포에 맞는 가이드와 도구를 골라 `.claude/rules/` 규칙 파일, CLAUDE.md/AGENTS.md, 린터·포매터 설정 중 고른 것을 작성합니다. `/gongbang:set-guidelines` · [SKILL.md](skills/engineering/set-guidelines/SKILL.md)

### Model-invoked

- [framing-problems](docs/skills/framing-problems.md): 바로 실행하지 않고 의도·원인·제약을 정리한 구체화 기록을 사용자와 확정한 뒤 작업합니다. 명시적으로 요청할 때만 동작합니다. `/gongbang:framing-problems [요청]` · [SKILL.md](skills/productivity/framing-problems/SKILL.md)
- [check-guidelines](docs/skills/check-guidelines.md): 규칙 파일, CLAUDE.md/AGENTS.md, 린터·포매터 설정을 기준으로 고른 범위의 코드를 검사해 규칙별로 보고하고, 고른 위반을 고친 뒤 다시 검사합니다. `/gongbang:check-guidelines [all | diff | branch | 경로]` · [SKILL.md](skills/engineering/check-guidelines/SKILL.md)

## 만드는 중인 스킬

`gongbang-dev`를 설치하면 쓸 수 있습니다. 동작이 자주 바뀝니다.

### User-invoked

- [set-brief](docs/skills/set-brief.md): 구체화 기록이나 세션 결과를 맥락 없는 작업자도 이어받을 수 있는 작업 지시서(brief)로 정리해 GitHub 이슈나 `docs/context/` 문서로 남깁니다. `/gongbang:set-brief [남길 작업 요약]` · [SKILL.md](skills/in-progress/set-brief/SKILL.md)
- [set-ticket](docs/skills/set-ticket.md): 큰 brief를 혼자 검증할 수 있는 티켓으로 나눠 GitHub sub-issue나 docs 파일로 남기고 brief에 연결합니다. `/gongbang:set-ticket [brief 이슈 번호·URL 또는 docs 경로]` · [SKILL.md](skills/in-progress/set-ticket/SKILL.md)
- [run-ticket](docs/skills/run-ticket.md): 새 세션에서 티켓 하나를 구현·리뷰하고 티켓 상태와 brief 체크박스를 갱신합니다. 커밋은 하지 않습니다. `/gongbang:run-ticket [티켓·brief 경로, 이슈 번호·URL] [여러 티켓이면 범위]` · [SKILL.md](skills/in-progress/run-ticket/SKILL.md)

### Model-invoked

- [analyzing-requirements](docs/skills/analyzing-requirements.md): 링크나 PDF·PPT·MD로 받은 기획서를 읽고 요구사항과 서비스·개발 영역별 개발 범위를 마크다운 문서로 정리합니다. `/gongbang:analyzing-requirements [기획서 링크 또는 파일 경로]` · [SKILL.md](skills/in-progress/analyzing-requirements/SKILL.md)

## 상황별로 고르기

| 상황 | 스킬 |
|---|---|
| 요청이 모호해서 바로 작업하기 불안할 때 | framing-problems |
| 시스템 프롬프트, 에이전트 프롬프트, CLAUDE.md를 만들거나 고칠 때 | prompt-builder |
| 스킬을 만들고, 실제로 돌려 보며 다듬을 때 | building-skills |
| README, 가이드, 설명글을 쓰거나 고칠 때 | write-docs |
| 레포에 코딩 규칙과 린터·포매터 설정이 없을 때 | set-guidelines |
| 커밋·PR 전에 변경분이 팀 규칙을 지키는지 볼 때 | check-guidelines |
| 기획서를 개발 범위와 요구사항으로 정리할 때 | analyzing-requirements |
| 한 세션에서 끝나지 않는 작업을 다른 세션·에이전트에 넘길 때 | set-brief → set-ticket → run-ticket |

스킬끼리 이어 쓰는 흐름은 다음과 같습니다.

- **프롬프트 만들기**: `/gongbang:framing-problems`로 작업을 먼저 구체화하고, 확정된 구체화 기록을 초안으로 `/gongbang:prompt-builder`에 넘기세요. 사람과 대화하는 에이전트 프롬프트나 재사용 템플릿은 실행할 때마다 framing-problems를 호출하게 만들 수 있습니다.
- **스킬 만들기**: `/gongbang:prompt-builder`로 SKILL.md 초안을 만들고, 그 결과를 `/gongbang:building-skills`에 넘겨 테스트하고 다듬으세요.
- **코드 규칙**: `/gongbang:set-guidelines`로 규칙을 만들고, `/gongbang:check-guidelines`로 코드를 검사하세요.
- **큰 작업 넘기기**: framing-problems로 구체화한 결과를 `/gongbang:set-brief`로 남기고, 크면 `/gongbang:set-ticket`으로 나눈 뒤, 새 세션에서 `/gongbang:run-ticket`으로 티켓을 하나씩 실행하세요.

## 커스텀

스킬을 복사해 고치는 방법, 스킬마다 자주 고치는 파일, 고친 스킬을 시험하는 방법은 [커스텀 가이드](docs/customization.md)에 있습니다.

## 기여

이슈, PR, 커밋 규칙은 [기여 가이드](CONTRIBUTING.md)를 보세요. 이 프로젝트에 참여하는 모든 사람은 [행동 강령](CODE_OF_CONDUCT.md)을 따르고, 보안 문제는 [보안 정책](SECURITY.md)에 따라 비공개로 알려 주세요.

스킬을 추가하거나 옮길 때 지킬 규칙은 [.claude/CLAUDE.md](.claude/CLAUDE.md)에 있습니다. 변경한 뒤 `scripts/check.py`를 실행해 통과시키세요. PyYAML이 필요합니다.

스킬 eval은 다음 명령으로 실행합니다.

```bash
claude plugin eval . --scaffold --allow-tools Edit WebSearch WebFetch --no-publish
claude plugin eval . --eval-dir evals-trigger --ablation none --no-publish
```

## 라이선스

[MIT](LICENSE)
