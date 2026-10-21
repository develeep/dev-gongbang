# 스킬 모음 운영 규칙

## 버킷

스킬은 `skills/<버킷>/<스킬 이름>/SKILL.md`에 둔다.

- `engineering/`: 매일 하는 코드 작업
- `productivity/`: 코드 밖의 일상 작업
- `in-progress/`: 만드는 중. 플러그인에 넣지 않는다

`engineering/`과 `productivity/`가 승격 버킷이다. 플러그인은 승격 버킷의 스킬만 정확히 담는다. 필요해지면 `deprecated/` 같은 버킷을 같은 방식으로 추가한다.

## 스킬을 추가·이동·이름 변경할 때

1. frontmatter `name`은 폴더 이름과 같게 한다.
2. 버킷 `README.md`에 한 줄 설명과 `SKILL.md` 링크를 넣는다.
3. 승격 버킷이면 `.claude-plugin/plugin.json`의 `skills` 배열과 최상위 `README.md`에도 넣는다. `in-progress/`는 둘 다 넣지 않는다.
4. 사용자에게 배포할 변경이면 `plugin.json`의 `version`을 올린다. 설치된 플러그인은 버전이 바뀔 때만 갱신된다. 버전은 `plugin.json`에만 둔다.
5. `scripts/check.py`를 실행해 통과시킨다.

## 호출 방식

모든 스킬은 둘 중 하나다. `README.md`들도 이 둘로 나눠 적는다.

- **User-invoked**: frontmatter에 `disable-model-invocation: true`. 사람이 이름을 입력할 때만 실행된다. `description`은 사람이 읽는 한 줄 요약으로 쓰고 트리거 문구를 넣지 않는다.
- **Model-invoked**: 기본값. `description`에 언제 쓰는지 트리거 문구를 구체적으로 적어 모델이 스스로 고를 수 있게 한다.

다른 스킬을 쓰게 할 때는 `../다른-스킬/FILE.md` 같은 폴더 간 링크 대신 "Skill 도구로 `<이름>`을 호출한다"고 적는다. User-invoked 스킬은 다른 스킬에서 호출할 수 없으니 사용자에게 실행을 안내한다.

## Eval

스킬마다 `evals/<스킬 이름>/`에 동작 케이스를, `evals-trigger/<스킬 이름>/`에 트리거 케이스를 둔다. 실행 명령은 `README.md`에 있다. eval은 저장소의 스킬을 바로 읽으므로 실행 중에는 `skills/`를 수정하지 않는다.
