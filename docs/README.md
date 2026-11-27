<p align="right"><b>한국어</b> · <a href="./en/README.md">English</a></p>

[README](../README.md) › 문서

# 문서

dev-gongbang의 사용 문서 목록입니다. 쓸 스킬의 사용법, mod 설치, 스킬 커스텀, 에이전트·워커 도구 설정 문서를 여기서 찾을 수 있습니다. 스킬 페이지에는 언제 쓰는지, 준비물, 진행 과정, 결과물, 커스텀 방법, 함께 쓰는 스킬이 같은 순서로 있습니다.

## 스킬

`gongbang`을 설치하면 쓸 수 있습니다.

### User-invoked

- [prompt-builder](skills/prompt-builder.md): Claude·GPT 모델별 가이드에 맞춰 시스템·에이전트 프롬프트, CLAUDE.md, SKILL.md를 인터뷰로 설계하거나, 기존 초안을 고치고 리뷰합니다.
- [building-skills](skills/building-skills.md): SKILL.md 초안이나 대화 기록·런북·코드 같은 자료로 스킬을 완성하고, 정적 검사·실행 테스트·사람 리뷰·수정을 반복합니다.
- [write-docs](skills/write-docs.md): 분야·독자·목적·톤·자료를 질문으로 정한 뒤 글 초안을 쓰거나, 가져온 초안과 기존 문서를 고칩니다.
- [set-guidelines](skills/set-guidelines.md): awesome-guidelines에서 레포의 언어·프레임워크에 맞는 가이드를 골라, `.claude/rules/` 규칙 파일, CLAUDE.md/AGENTS.md, 린터·포매터 설정 중 고른 것을 작성합니다.

### Model-invoked

- [framing-problems](skills/framing-problems.md): 작업 전에 의도·원인·제약을 정리한 구체화 기록을 사용자와 확정합니다.
- [check-guidelines](skills/check-guidelines.md): 레포의 규칙 파일과 린터·포매터 설정으로 고른 범위의 코드를 검사하고, 고른 위반을 고칩니다.

## 만드는 중인 스킬

`gongbang-dev`를 설치해야 쓸 수 있습니다. 동작이 자주 바뀝니다.

### User-invoked

- [run-flow](skills/run-flow.md): 기획서, 요청, brief 중 하나로 요구사항 정리부터 PR 생성까지 단계 스킬을 차례로 불러 진행합니다.

### Model-invoked

- [set-brief](skills/set-brief.md): 구체화 기록이나 세션 결과를 맥락 없는 작업자도 이어받을 수 있는 작업 지시서(brief)로 남깁니다.
- [set-ticket](skills/set-ticket.md): 큰 brief를 혼자 검증할 수 있는 티켓으로 나눕니다.
- [run-ticket](skills/run-ticket.md): brief와 티켓 문서를 받아 티켓 하나를 구현·리뷰합니다. 여러 티켓은 차례로 실행하고, 워커 도구 절차가 지정되거나 등록돼 있을 때만 워커로 병렬 실행합니다.
- [analyzing-requirements](skills/analyzing-requirements.md): 기획서를 요구사항과 개발 범위 문서로 정리합니다.

## Mod

- [gongbang-mods](mods.md): Claude Code 화면에서 도구 호출을 한 줄로 접고, 메시지를 카드로 나누고, 세션 목표와 컨텍스트 사용량을 우측 패널에 보여 줍니다. run-flow 보호 경로 쓰기 차단, 함께 쓰면 좋은 외부 mod, 상태줄 스크립트, `extras/setup.sh`도 이 문서에 있습니다.

## 가이드

- [스킬 커스텀하기](customization.md): 스킬을 복사해 고치고, 검사하고, 시험하는 방법
- [omp 멀티에이전트 설정](omp-orchestration.md): omp(oh-my-pi)에 교차 리뷰·brief 냉독 에이전트, 위임 규칙, 보호 경로 차단 extension을 설치하고 모델을 고르는 방법
- [Orca 오케스트레이션 설정](orca-orchestration.md): run-ticket이 여러 티켓을 Orca 워커로 병렬 실행하도록 Orca를 설치하고 워커 절차를 규칙 파일에 등록하는 선택 설정과, Orca 방식의 동작
- [Paseo 오케스트레이션 설정](paseo-orchestration.md): run-ticket이 여러 티켓을 Paseo 워커로 병렬 실행하도록 Paseo 에이전트 프로필과 워크스페이스 스크립트를 설치하고 워커 절차를 규칙 파일에 등록하는 선택 설정과, Paseo 방식의 동작
- [상황별로 고르기](../README.md#상황별로-고르기): 상황에 맞는 스킬과 스킬을 이어 쓰는 흐름
