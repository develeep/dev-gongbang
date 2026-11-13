mkdir -p notes
cat > notes/rollback-memo.md <<'MD'
# 배포 롤백 메모
- 롤백 명령: `./scripts/deploy.sh rollback <릴리스 태그>`
- 직전 릴리스 태그는 `git tag --sort=-creatordate | sed -n 2p`로 찾는다
- 롤백은 약 3분 걸린다
- 롤백 뒤 `/healthz`가 200을 돌려주면 끝난 것이다
- 200이 아니면 #deploy-alert 채널에 알리고 당직자를 부른다
- DB 마이그레이션이 포함된 릴리스는 이 명령으로 되돌리지 않는다. 당직자에게 넘긴다
MD
