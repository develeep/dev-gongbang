mkdir -p docs/context src
cat > src/slug.py <<'PY'
def slugify(title):
    return title.strip().lower()
PY
cat > docs/context/2026-10-23-slug-hyphen.md <<'MD'
# 글 제목으로 만든 slug에 공백 대신 하이픈을 쓴다

- 기준 커밋: `d4e5f6a`
- 작성일: 2026-10-23

## 요약
`slugify`가 공백을 그대로 남겨 URL에 `%20`이 들어간다.

## 최종 목적
`slugify("Hello World")`가 `hello-world`를 돌려준다.

## 합의한 작업
- 해법: 연속 공백을 하이픈 하나로 바꾼다
- 완료한 일: 소문자 변환 (`d4e5f6a`)
- 남은 일:
  - [ ] 공백을 하이픈으로 바꾼다

## 작업 경계
- 바꾸는 범위: `slugify`
- 바꾸지 않는 범위: 특수문자 처리

## 확인 기준
- [ ] `python3 -c "import sys; sys.path.insert(0,'src'); from slug import slugify; print(slugify('Hello  World'))"` → `hello-world`

## 미확인·위험
- 한글 제목 처리 방식은 정하지 않았다
MD
cat > docs/context/README.md <<'MD'
# Context

- [2026-10-23 글 제목으로 만든 slug에 공백 대신 하이픈을 쓴다](./2026-10-23-slug-hyphen.md): slug 공백 처리
MD
git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init
