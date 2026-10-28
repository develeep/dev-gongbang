<p align="right"><b>한국어</b> · <a href="./CONTRIBUTING.en.md">English</a></p>

# 기여 가이드

dev-gongbang에 버그를 알리거나, 스킬을 고치거나, 새 스킬을 제안하는 방법을 설명합니다. 이슈와 PR은 한국어와 영어 모두 받습니다.

**목차**: [이슈 올리기](#이슈-올리기) · [개발 환경](#개발-환경) · [스킬 고치기와 추가하기](#스킬-고치기와-추가하기) · [검사하기](#검사하기) · [커밋 메시지](#커밋-메시지) · [PR 보내기](#pr-보내기) · [행동 강령](#행동-강령)

## 이슈 올리기

[새 이슈](https://github.com/develeep/dev-gongbang/issues/new/choose)에서 양식을 고르세요.

- **버그 신고**: 스킬이 문서와 다르게 동작하거나 스크립트가 실패할 때
- **스킬 제안**: 새 스킬이나 기존 스킬의 새 동작을 제안할 때

보안 문제는 공개 이슈로 올리지 말고 [보안 정책](SECURITY.md)에 따라 비공개로 알려 주세요.

## 개발 환경

| 도구 | 쓰는 곳 |
|---|---|
| Python 3.9 이상, PyYAML | `scripts/validate.py`, `scripts/test_validate.py` |
| Claude Code CLI | `scripts/check.py`(`claude plugin validate`를 실행), 스킬 실행, eval |

저장소를 포크하고 클론한 뒤 PyYAML을 설치하세요.

```bash
git clone https://github.com/<내 계정>/dev-gongbang.git
cd dev-gongbang
pip install pyyaml
```

## 스킬 고치기와 추가하기

스킬을 추가·이동·이름 변경할 때 지킬 규칙은 [.claude/CLAUDE.md](.claude/CLAUDE.md)에 있습니다. 버킷, 호출 방식, 사용 문서, 커밋 규칙이 모두 이 파일에 있습니다. 이 저장소에서 Claude Code로 작업하면 Claude Code가 이 파일을 읽고 규칙을 따릅니다.

자주 놓치는 것은 다음과 같습니다.

- 스킬을 바꾸면 사용 문서 `docs/skills/<스킬 이름>.md`와 영어판 `docs/en/skills/<스킬 이름>.md`도 함께 고칩니다.
- 사용자에게 배포할 변경이면 `.claude-plugin/plugin.json`의 `version`을 올립니다. 설치된 플러그인은 버전이 바뀔 때만 갱신됩니다.

고친 스킬을 내 Claude Code에서 시험하는 방법은 [커스텀 가이드](docs/customization.md)에 있습니다.

## 검사하기

PR을 보내기 전에 저장소 규칙 검사를 실행하세요.

```bash
python3 scripts/check.py
```

`scripts/validate.py`를 고쳤으면 검사기 자체의 테스트도 실행하세요.

```bash
python3 scripts/test_validate.py
```

PR을 올리면 GitHub Actions가 `test_validate.py`와 `validate.py`를 자동으로 실행합니다. `claude plugin validate`는 CI에서 실행하지 않으니 로컬에서 `check.py`로 확인하세요.

스킬의 동작을 바꿨다면 eval도 실행해 보세요. eval은 모델을 실제로 호출합니다.

```bash
claude plugin eval . --scaffold --allow-tools Edit WebSearch WebFetch --no-publish
claude plugin eval . --eval-dir evals-trigger --ablation none --no-publish
```

## 커밋 메시지

제목은 `<유형>: <작업 요약>` 형식으로 쓰고, 빈 줄 다음에 작업 내역을 `- ` 목록으로 적습니다. 한국어와 영어 모두 받습니다.

```
fix: check-guidelines에서 paths 없는 규칙 파일 누락 수정

- paths가 없는 규칙 파일을 모든 대상 파일에 적용
```

유형은 `feature`, `fix`, `docs`, `refactor`, `eval`, `chore` 중 하나입니다. 커밋 하나에는 유형 하나만 담습니다. 유형별 뜻과 세부 형식은 [.claude/CLAUDE.md](.claude/CLAUDE.md)의 "커밋" 절에 있습니다.

## PR 보내기

1. `master`에서 브랜치를 만들어 작업합니다.
2. PR을 열면 나오는 확인 목록을 채웁니다.
3. CI 검사가 통과해야 머지할 수 있습니다.
4. 관리자가 리뷰한 뒤 merge commit으로 머지합니다. 커밋 메시지가 그대로 남으므로 커밋을 정리한 뒤 PR을 보내 주세요.

## 행동 강령

이 프로젝트에 참여하는 모든 사람은 [행동 강령](CODE_OF_CONDUCT.md)을 따릅니다.
