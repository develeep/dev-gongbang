mkdir -p docs
cat > docs/draft-onboarding.md <<'MD'
# 로컬 개발 환경 띄우기

## 문제가 생기면
포트 3000이 이미 사용 중이라는 오류가 발생하는 경우에는 `lsof -i :3000`을 통해 프로세스를 확인하는 작업을 수행합니다.

## 준비물
Node.js 20 버전과 pnpm 9 버전의 설치가 필요합니다.

## 설치하기
`pnpm install`을 통해 의존성 설치를 수행합니다. 그 다음으로 `.env.example`을 `.env.local`로 복사하는 작업을 진행합니다.

## 기타
`pnpm dev`를 실행하면 http://localhost:3000 에서 화면을 확인하실 수 있게 됩니다.
MD
