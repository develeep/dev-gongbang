<p align="center">
  <img src="./assets/gongbang-logo.gif" alt="Gongbang" width="800">
</p>

<h1 align="center">
    dev-gongbang
</h1>

<p align="center">
    개발 과정에서 쓰는 Claude Code 스킬 모음.
</p>

## 설치

```bash
claude plugin marketplace add develeep/dev-gongbang
claude plugin install gongbang@dev-gongbang
```

만드는 중인 `in-progress/` 스킬도 쓰려면 `gongbang-dev`를 함께 설치한다.

```bash
claude plugin install gongbang-dev@dev-gongbang
```

## 스킬

### User-invoked

- [prompt-builder](skills/productivity/prompt-builder/SKILL.md): 모델별 가이드에 맞춰 시스템 프롬프트, CLAUDE.md, SKILL.md를 인터뷰로 설계하거나 초안을 고친다. `/gongbang:prompt-builder [초안 경로 또는 설명]`
- [building-skills](skills/productivity/building-skills/SKILL.md): prompt-builder가 만든 SKILL.md 초안이나 대화 기록·런북·코드 같은 자료로 스킬을 완성하고, 정적 검사·실행 테스트·사람 리뷰·수정 반복까지 진행한다. `/gongbang:building-skills [스킬 폴더 경로, SKILL.md 초안, 또는 만들 스킬 설명]`
- [write-docs](skills/productivity/write-docs/SKILL.md): 분야·독자·목적·톤·자료를 질문으로 정한 뒤 글 초안을 쓰거나, 가져온 초안과 기존 문서를 고친다. `/gongbang:write-docs [쓰거나 고칠 글에 대한 요청]`
- [set-guidelines](skills/engineering/set-guidelines/SKILL.md): awesome-guidelines에서 레포에 맞는 가이드와 도구를 골라 `.claude/rules/` 규칙 파일, CLAUDE.md/AGENTS.md, 린터·포매터 설정 중 고른 것을 작성한다. `/gongbang:set-guidelines`

### Model-invoked

- [framing-problems](skills/productivity/framing-problems/SKILL.md): 바로 실행하지 않고 의도·원인·제약을 정리한 구체화 기록을 사용자와 확정한 뒤 작업한다. 명시적으로 요청할 때만 동작한다. `/gongbang:framing-problems [요청]`
- [check-guidelines](skills/engineering/check-guidelines/SKILL.md): 규칙 파일, CLAUDE.md/AGENTS.md, 린터·포매터 설정을 기준으로 고른 범위의 코드를 검사해 규칙별로 보고하고, 고른 위반을 고친 뒤 다시 검사한다. `/gongbang:check-guidelines [all | diff | branch | 경로]`

한 번 쓸 프롬프트는 `/gongbang:framing-problems`로 작업을 먼저 구체화하고, 확정된 구체화 기록을 초안으로 `/gongbang:prompt-builder`에 넘긴다. 재사용 템플릿이나 사람과 대화하는 에이전트 프롬프트는 prompt-builder에서 실행할 때마다 framing-problems를 호출하게 할 수 있다.

## Eval

```bash
claude plugin eval . --scaffold --allow-tools Edit WebSearch WebFetch --no-publish
claude plugin eval . --eval-dir evals-trigger --ablation none --no-publish
```
