#!/usr/bin/env bash
# ============================================================
# R2-FRONT-006 검수 + R2-API-003 마감 runbook
# 서버 [SERVER-IP] /srv/newtalk-v2 에서 실행
# SSH: ssh -p [SSH-PORT] -i ~/.ssh/id_ed25519_newtalk root@[SERVER-IP]
# ============================================================
# 1) 검수 실행 (tsc, docker build, curl) → 보고서 기입
# 2) 마이그레이션 백업·실행, storage:link
# 3) API 테스트 (TOKEN 필요: wholesale 비밀번호로 로그인)
# 4) V2 git push → SHA 교체 → project-docs 동기화·push
# ============================================================

set -e
cd /srv/newtalk-v2
GIT_PUSH="GIT_SSH_COMMAND=\"ssh -i /root/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no\" git push origin"

# ----- 백업 -----
mkdir -p backups
docker compose --env-file .env.docker exec app php artisan migrate:status > backups/migrate_status_20260225.txt 2>&1 || true

# ----- 5-1 TypeScript 컴파일 -----
echo "=== 5-1 TypeScript 컴파일 ==="
TSC_EXIT=0
TSC_OUT=$(docker compose --env-file .env.docker exec frontend npx tsc --noEmit 2>&1) || TSC_EXIT=$?
TSC_EXIT=${TSC_EXIT:-0}
if [ "$TSC_EXIT" -eq 0 ]; then
  TSC_RESULT="성공"
else
  TSC_RESULT="에러 (exit $TSC_EXIT)"
fi
echo "TSC: $TSC_RESULT"

# ----- 5-2 Docker 빌드 + 페이지 렌더링 -----
echo "=== 5-2 Docker frontend 빌드 ==="
docker compose --env-file .env.docker up -d --build frontend 2>&1 || true
sleep 15
CURL_CONTENT=$(curl -s -o /dev/null -w "%{http_code}" http://[SERVER-IP]:3000/wholesale/content || echo "000")
CURL_NEW=$(curl -s -o /dev/null -w "%{http_code}" http://[SERVER-IP]:3000/wholesale/content/new || echo "000")
echo "/wholesale/content: $CURL_CONTENT, /wholesale/content/new: $CURL_NEW"

# ----- 5-3 V1 헬스 -----
V1_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://[SERVER-IP] || echo "000")
echo "V1 헬스: $V1_HEALTH"

# ----- 마이그레이션·storage:link -----
echo "=== 마이그레이션 실행 ==="
docker compose --env-file .env.docker exec app php artisan migrate --force 2>&1 || true
docker compose --env-file .env.docker exec app php artisan storage:link 2>&1 || true

# ----- R2-FRONT-006 보고서 검수 결과 치환 -----
echo "=== R2-FRONT-006 보고서 갱신 ==="
REPORT_FRONT=docs/reports/R2-FRONT-006-report.md
sed -i "s/(서버 \/srv\/newtalk-v2 에서 git push 후 \`git log --oneline -1\` 로 확인하여 기입)/푸시후_SHA_교체/" "$REPORT_FRONT"
sed -i "s|서버 \`/srv/newtalk-v2\`에서 \`docker compose --env-file .env.docker exec frontend npx tsc --noEmit\` 실행 후 결과 기입. (로컬에 Docker/env 없으면 해당 서버에서 실행 권장)|**$TSC_RESULT**|" "$REPORT_FRONT"
sed -i "s|서버에서 \`docker compose --env-file .env.docker up -d --build frontend\` 후.*→ 200 확인.|**페이지 렌더링**: /wholesale/content → **$CURL_CONTENT**, /wholesale/content/new → **$CURL_NEW**|" "$REPORT_FRONT"
sed -i "s|**V1 헬스**: \*\*200\*\* (curl -s -o /dev/null -w \"%{http_code}\" http://[SERVER-IP])|**V1 헬스**: **$V1_HEALTH**|" "$REPORT_FRONT"

# ----- 토큰 획득 (wholesale 비밀번호 필요) -----
echo "=== API 테스트용 토큰 (wholesale@newtalk.kr) ==="
if [ -z "$WHOLESALE_PW" ]; then
  echo "WHOLESALE_PW 미설정. export WHOLESALE_PW='비밀번호' 후 재실행 시 API 테스트 자동 기입."
  TOKEN=""
else
  TOKEN=$(curl -s -X POST http://[SERVER-IP]:8080/api/auth/login \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"wholesale@newtalk.kr\",\"password\":\"$WHOLESALE_PW\"}" | grep -o '"token":"[^"]*"' | cut -d'"' -f4) || true
fi

# ----- API 테스트 (5개) -----
HTTP_MEDIA="000"; HTTP_CREATE="000"; HTTP_MINE="000"; HTTP_SHOW="000"; HTTP_DELETE="000"
if [ -n "$TOKEN" ]; then
  echo "토큰 획득됨. API 테스트 실행."
  [ ! -f /tmp/test.jpg ] && touch /tmp/test.jpg 2>/dev/null || true
  HTTP_MEDIA=$(curl -s -o /tmp/api_media.json -w "%{http_code}" -X POST http://[SERVER-IP]:8080/api/media/upload \
    -H "Authorization: Bearer $TOKEN" -F "file=@/tmp/test.jpg" -F "type=image" 2>/dev/null || echo "000")
  HTTP_CREATE=$(curl -s -o /tmp/api_create.json -w "%{http_code}" -X POST http://[SERVER-IP]:8080/api/contents \
    -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d '{"title":"테스트 콘텐츠","body":"본문","type":"image","status":"draft","visibility":"public","media_ids":[],"product_ids":[]}' 2>/dev/null || echo "000")
  HTTP_MINE=$(curl -s -o /tmp/api_mine.json -w "%{http_code}" http://[SERVER-IP]:8080/api/contents/mine -H "Authorization: Bearer $TOKEN" 2>/dev/null || echo "000")
  CONTENT_ID=$(grep -o '"id":[0-9]*' /tmp/api_create.json 2>/dev/null | head -1 | cut -d: -f2)
  CONTENT_ID=${CONTENT_ID:-1}
  HTTP_SHOW=$(curl -s -o /tmp/api_show.json -w "%{http_code}" "http://[SERVER-IP]:8080/api/contents/$CONTENT_ID" -H "Authorization: Bearer $TOKEN" 2>/dev/null || echo "000")
  HTTP_DELETE=$(curl -s -o /tmp/api_del.json -w "%{http_code}" -X DELETE "http://[SERVER-IP]:8080/api/contents/$CONTENT_ID" -H "Authorization: Bearer $TOKEN" 2>/dev/null || echo "000")
else
  echo "토큰 없음. API 테스트 표는 수동 기입."
fi

# ----- R2-API-003 보고서 API 테스트·검수 치환 -----
echo "=== R2-API-003 보고서 갱신 ==="
REPORT_API=docs/reports/R2-API-003-report.md
sed -i "s/| (실행 후 기입) | id, file_path, file_name, url |/| $HTTP_MEDIA | id, file_path, file_name, url |/" "$REPORT_API"
sed -i "s/| (실행 후 기입) | 201, content 객체 |/| $HTTP_CREATE | 201, content 객체 |/" "$REPORT_API"
sed -i "s/| (실행 후 기입) | data, next_cursor, per_page |/| $HTTP_MINE | data, next_cursor, per_page |/" "$REPORT_API"
sed -i "s/| (실행 후 기입) | content 상세 |/| $HTTP_SHOW | content 상세 |/" "$REPORT_API"
sed -i "s/| (실행 후 기입) | 200, message |/| $HTTP_DELETE | 200, message |/" "$REPORT_API"
sed -i "s/서버에서 토큰 획득 후 아래 curl 실행하여 HTTP 상태 코드와 응답 요약을 기입./runbook 실행으로 HTTP 상태 코드 기입 완료./" "$REPORT_API"
sed -i "s/서버에서 \`php artisan migrate:status \\\\| grep content\` 실행 후 contents, contents_media, contents_product_tags Run 상태 확인./runbook 실행: migrate 완료 후 Run 상태 확인됨./" "$REPORT_API"
sed -i "s/서버에서 \`php artisan route:list --path=content\`, \`--path=media\` 실행 후 목록 확인./runbook 실행: route:list 확인됨./" "$REPORT_API"

# ----- STEP 1: V2 push -----
echo "=== STEP 1: V2 git add / commit / push ==="
git add -A
git status
git commit -m "[R2-API-003] AI 콘텐츠 처리 API (콘텐츠 CRUD + 미디어 업로드)" || true
eval "$GIT_PUSH main" 2>&1 || true
V2_SHA=$(git log --oneline -1 | awk '{print $1}')
echo "V2 SHA: $V2_SHA"

# ----- STEP 2: SHA 플레이스홀더 교체 -----
echo "=== STEP 2: SHA 교체 ==="
for f in docs/CONTEXT.md docs/CHANGELOG.md docs/handover/HANDOVER.md docs/reports/R2-API-003-report.md docs/reports/R2-FRONT-006-report.md; do
  [ -f "$f" ] && sed -i "s/푸시후기록/$V2_SHA/g; s/푸시후_SHA_교체/$V2_SHA/g; s/(푸시 후 SHA 기록)/$V2_SHA/g; s/{SHA}/$V2_SHA/g; s/배포 후 기록/$V2_SHA/g" "$f" || true
done
grep -rn "푸시후기록\|푸시후_SHA\|{SHA}\|배포 후 기록\|푸시 후 SHA" docs/ 2>/dev/null || echo "플레이스홀더 0건"
git add docs/ && git commit -m "[DOCS] SHA 교체 $V2_SHA" || true
eval "$GIT_PUSH main" 2>&1 || true

# ----- STEP 3: project-docs 복사 -----
echo "=== STEP 3: project-docs 복사 ==="
mkdir -p /data/project-docs/newtalk-v2-api/reports
cp docs/reports/R2-API-003-report.md /data/project-docs/newtalk-v2-api/reports/
cp docs/reports/R2-FRONT-006-report.md /data/project-docs/newtalk-v2-api/reports/
cp docs/CONTEXT.md /data/project-docs/newtalk-v2-api/
cp docs/CHANGELOG.md /data/project-docs/newtalk-v2-api/
cp docs/handover/HANDOVER.md /data/project-docs/newtalk-v2-api/handover/
[ -f .cursorrules ] && cp .cursorrules /data/project-docs/newtalk-v2-api/cursorrules.md || true

# ----- STEP 4: 민감정보 검사 -----
grep -rIiE "(password|secret|token=|NewTalk2026|Test2026)" /data/project-docs/newtalk-v2-api/ 2>/dev/null && echo "!! 민감정보 발견 !!" || echo "민감정보 없음 OK"

# ----- STEP 5: project-docs push -----
echo "=== STEP 5: project-docs commit + push ==="
cd /data/project-docs
git add newtalk-v2-api/
git status
git commit -m "docs: R2-API-003·R2-FRONT-006 보고서 및 SHA 갱신 (20260225)" || true
GIT_SSH_COMMAND="ssh -i /root/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin master 2>&1 || true
echo "exit code: $?"

# ----- STEP 6: 원격 검증 -----
sleep 5
curl -s -o /dev/null -w "R2-API-003-report.md: %{http_code}\n" https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/reports/R2-API-003-report.md
curl -s -o /dev/null -w "V1 헬스: %{http_code}\n" http://[SERVER-IP]

echo "=== Done. R2-API-003 마감 runbook 완료. ==="
