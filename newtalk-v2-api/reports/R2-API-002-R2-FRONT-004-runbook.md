# R2-API-002 + R2-FRONT-004 서버 실행 순서

작업 디렉터리: `/srv/newtalk-v2/` (서버 기준)

## Phase A (API) — 서버에서

```bash
cd /srv/newtalk-v2
git checkout develop 2>/dev/null || git checkout main
git pull
git checkout -b feature/R2-API-002-brand-page

# 마이그레이션 (이미 로컬에 파일 있음)
docker compose --env-file .env.docker exec app php artisan migrate --force
# 확인: mysql -u newtalk_v2_user -p -h 127.0.0.1 -P 3307 newtalk_v2 -e "DESCRIBE brand_pages;"

# 시드
docker compose --env-file .env.docker exec app php artisan db:seed --class=BrandPageSeeder

# API 테스트 (비밀번호는 .env.docker 참조)
TOKEN=$(curl -s -X POST http://127.0.0.1:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"wholesale@newtalk.kr","password":"[비밀번호]"}' | jq -r '.token')
curl -s http://127.0.0.1:8080/api/brands | head -c 300
curl -s http://127.0.0.1:8080/api/brands/test-wholesale | head -c 400

# API만 커밋 후 푸시
git add -A
grep -rIiE "(password|secret|token=)" app/ database/ routes/ --include="*.php" || true
git commit -m "[R2-API-002] 브랜드 페이지 API — brand_pages 테이블, BrandPageController 6 EP"
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin feature/R2-API-002-brand-page
```

## Phase B (Frontend) — 서버에서

```bash
cd /srv/newtalk-v2
docker compose --env-file .env.docker up -d --build frontend
docker compose --env-file .env.docker logs frontend --tail 30

curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86:3000/brand/test-wholesale
curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86:3000/brands

git add -A
grep -rIiE "(password|secret|token=)" frontend/src/ --include="*.ts" --include="*.tsx" || true
git commit -m "[R2-FRONT-004] 브랜드 페이지 UI — 헤더, 상품 그리드, 피드, 브랜드 탐색"
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin feature/R2-API-002-brand-page
```

## Phase C (문서·동기화) — 서버에서

```bash
cd /srv/newtalk-v2
# SHA 기록 후 CONTEXT/CHANGELOG/HANDOVER 내 SHA 플레이스홀더 치환 권장

git add docs/
git commit -m "[DOCS] R2-API-002 + R2-FRONT-004 보고서·문서 갱신 v1.6.0"
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin feature/R2-API-002-brand-page

# project-docs 동기화
cp /srv/newtalk-v2/docs/CONTEXT.md /data/project-docs/newtalk-v2-api/CONTEXT.md
cp /srv/newtalk-v2/docs/CHANGELOG.md /data/project-docs/newtalk-v2-api/CHANGELOG.md
cp /srv/newtalk-v2/docs/handover/HANDOVER.md /data/project-docs/newtalk-v2-api/handover/HANDOVER.md
cp /srv/newtalk-v2/.cursorrules /data/project-docs/newtalk-v2-api/cursorrules.md
mkdir -p /data/project-docs/newtalk-v2-api/reports
cp /srv/newtalk-v2/docs/reports/R2-API-002-report.md /data/project-docs/newtalk-v2-api/reports/
cp /srv/newtalk-v2/docs/reports/R2-FRONT-004-report.md /data/project-docs/newtalk-v2-api/reports/
mkdir -p /data/project-docs/newtalk-v2-api/review
cp /srv/newtalk-v2/app/Http/Controllers/Api/BrandPageController.php /data/project-docs/newtalk-v2-api/review/R2-API-002_BrandPageController.php
cp /srv/newtalk-v2/frontend/src/lib/brand-api.ts /data/project-docs/newtalk-v2-api/review/R2-FRONT-004_brand-api.ts
cp "/srv/newtalk-v2/frontend/src/app/(retail)/brand/[slug]/page.tsx" /data/project-docs/newtalk-v2-api/review/R2-FRONT-004_brand-page.tsx
# REVIEW_REQUEST.md 작성 및 sed 민감정보 제거 후
cd /data/project-docs && git add -A && git commit -m "[sync] R2-API-002 + R2-FRONT-004 브랜드 페이지 v1.6.0 + review" && GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin master
```
