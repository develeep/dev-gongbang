# in-progress

만드는 중인 스킬. 플러그인에 포함되지 않는다. 다듬어지면 `engineering/`이나 `productivity/`로 옮긴다.

## User-invoked

- [set-brief](./set-brief/SKILL.md): 구체화 기록이나 세션 결과를 맥락 없는 작업자도 그대로 이어받을 수 있는 작업 지시서로 정리해 GitHub 이슈나 `docs/context/`에 남긴다.
- [set-ticket](./set-ticket/SKILL.md): set-brief 이슈나 문서가 클 때 혼자 검증할 수 있는 티켓으로 나눠 sub-issue나 docs 파일로 남기고 brief에 연결한다.
- [run-ticket](./run-ticket/SKILL.md): set-brief·set-ticket의 brief와 티켓을 새 세션에서 받아 티켓 하나를 구현·리뷰하고 티켓 상태와 brief 체크박스를 갱신한다. 커밋은 하지 않는다.

## Model-invoked

- [analyzing-requirements](./analyzing-requirements/SKILL.md): 링크나 PDF·PPT·MD로 받은 기획서를 읽고 요구사항과 서비스·개발 영역별 개발 범위를 마크다운 문서로 정리한다. 기획서에 없는 내용은 채우지 않고 묻는다.

## 설치

`gongbang` 플러그인에는 들어 있지 않다. 두 방법 중 하나로 설치한다.

### 플러그인으로 설치

```bash
claude plugin install gongbang-dev@dev-gongbang
```

`gongbang`과 함께 설치한다. 호출 이름은 `/gongbang:set-brief`처럼 `gongbang:` 접두사가 붙는다. GitHub에서 설치하면 `plugin.json`의 `version`이 바뀔 때만 갱신된다.

### 링크로 설치

저장소를 클론한 뒤 직접 연결한다.

```bash
scripts/link-in-progress.sh
```

`skills/in-progress/`의 스킬마다 `~/.claude/skills/<스킬 이름>`에 심볼릭 링크를 건다. 모든 프로젝트에서 쓸 수 있다. 저장소에서 고치면 다음 세션부터 바로 반영되고, 플러그인처럼 버전을 올릴 필요가 없다. 새 스킬을 추가했으면 다시 실행한다.

일부 스킬만 설치하려면 스킬 이름을 뒤에 적는다. 이름을 적지 않으면 전부 설치한다. `skills/in-progress/set-brief/`처럼 경로로 적어도 된다.

```bash
scripts/link-in-progress.sh set-brief set-ticket
```

특정 프로젝트에서만 쓰려면 그 프로젝트 폴더에서 `--project`로 실행한다.

```bash
cd <프로젝트>
<dev-gongbang 경로>/scripts/link-in-progress.sh --project
```

현재 디렉터리의 `.claude/skills/`에 링크를 건다. 링크는 내 컴퓨터의 절대 경로를 가리키므로, 현재 디렉터리가 git 저장소 안이면 링크 경로를 그 저장소의 `.git/info/exclude`에 추가해 커밋되지 않게 한다. `.gitignore`는 건드리지 않는다.

- 호출 이름에 `gongbang:` 접두사가 붙지 않는다. `/set-brief`처럼 부른다.
- 같은 이름의 폴더가 이미 있고 링크가 아니면 덮어쓰지 않고 건너뛴다.

### 해제

```bash
scripts/link-in-progress.sh --remove
```

이 저장소를 가리키는 링크만 지운다. 스킬 이름을 적으면 그 스킬만 지운다. project 범위로 설치했으면 같은 폴더에서 `--project --remove`로 실행한다. `.git/info/exclude`에 넣은 줄은 남지만 영향은 없다. 스킬을 승격 버킷으로 옮기기 전에 실행한다. 옮긴 뒤에 실행하면 링크가 깨진 채 남으므로 `~/.claude/skills/`에서 직접 지운다.
