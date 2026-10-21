# in-progress

만드는 중인 스킬. 플러그인에 포함되지 않는다. 다듬어지면 `engineering/`이나 `productivity/`로 옮긴다.

## User-invoked

- [set-brief](./set-brief/SKILL.md): 구체화 기록이나 세션 결과를 맥락 없는 작업자도 그대로 이어받을 수 있는 작업 지시서로 정리해 GitHub 이슈나 `docs/context/`에 남긴다.
- [set-ticket](./set-ticket/SKILL.md): set-brief 이슈나 문서가 클 때 혼자 검증할 수 있는 티켓으로 나눠 sub-issue나 docs 파일로 남기고 brief에 연결한다.
- [skill-reviewer](./skill-reviewer/SKILL.md): SKILL.md를 Claude Code 규칙, 공식 best practice, 저장소 운영 규칙으로 검사해 스킬별 보고서와 수정 계획을 낸다.

## 설치

플러그인에 들어 있지 않으므로 저장소를 클론한 뒤 직접 연결한다.

```bash
scripts/link-in-progress.sh
```

`skills/in-progress/`의 스킬마다 `~/.claude/skills/<스킬 이름>`에 심볼릭 링크를 건다. 저장소에서 고치면 다음 세션부터 바로 반영되고, 플러그인처럼 버전을 올릴 필요가 없다. 새 스킬을 추가했으면 다시 실행한다.

- 호출 이름에 `gongbang:` 접두사가 붙지 않는다. `/set-brief`처럼 부른다.
- 같은 이름의 폴더가 이미 있고 링크가 아니면 덮어쓰지 않고 건너뛴다.
- 다른 위치에 걸려면 `CLAUDE_SKILLS_DIR`를 지정한다. 예: 프로젝트 전용이면 `CLAUDE_SKILLS_DIR=<프로젝트>/.claude/skills scripts/link-in-progress.sh`

### 해제

```bash
scripts/link-in-progress.sh --remove
```

이 저장소를 가리키는 링크만 지운다. 스킬을 승격 버킷으로 옮기기 전에 실행한다. 옮긴 뒤에 실행하면 링크가 깨진 채 남으므로 `~/.claude/skills/`에서 직접 지운다.
