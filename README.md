# gongbang

개발 과정에서 쓰는 Claude Code 스킬 모음.

## 설치

```bash
claude plugin marketplace add /path/to/ClaudeMe
claude plugin install gongbang@dev-gongbang
```

## 스킬

### User-invoked

- [prompt-builder](skills/productivity/prompt-builder/SKILL.md): 모델별 가이드에 맞춰 시스템 프롬프트, CLAUDE.md, SKILL.md를 인터뷰로 설계하거나 초안을 고친다. `/gongbang:prompt-builder [초안 경로 또는 설명]`

### Model-invoked

- [framing-problems](skills/productivity/framing-problems/SKILL.md): 바로 실행하지 않고 의도·원인·제약을 정리한 구체화 기록을 사용자와 확정한 뒤 작업한다. 명시적으로 요청할 때만 동작한다. `/gongbang:framing-problems [요청]`

## Eval

```bash
claude plugin eval . --scaffold --allow-tools Edit WebSearch WebFetch --no-publish
claude plugin eval . --eval-dir evals-trigger --ablation none --no-publish
```
