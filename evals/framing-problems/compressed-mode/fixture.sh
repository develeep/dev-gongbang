mkdir -p docs scripts
cat > docs/deploy-checklist.md <<'MD'
# 배포 체크리스트
- [ ] 마이그레이션 실행
- [ ] 기능 플래그 확인
- [ ] 슬랙 #release 공지
- [ ] 롤백 계획 작성
MD
cat > scripts/deploy.sh <<'SH'
#!/bin/sh
# 체크리스트 확인 없이 바로 배포한다
./build.sh && kubectl apply -f k8s/
SH
