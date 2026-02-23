#!/bin/bash
# NewTalk V2 API 문서 동기화: newtalk-v2/docs/ → project-docs/newtalk-v2-api/
# 114 서버 기본: SRC=/srv/newtalk-v2/docs
# 로컬: NEWTALK_V2_DOCS=/root/newtalk-v2/docs bash sync_newtalk_v2_api.sh
# 사용법: bash /data/project-docs/scripts/sync_newtalk_v2_api.sh

set -e

SRC="${NEWTALK_V2_DOCS:-/srv/newtalk-v2/docs}"
DST="/data/project-docs/newtalk-v2-api"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== NewTalk V2 API 문서 동기화: $TIMESTAMP ==="
echo "SRC=$SRC"

mkdir -p "$DST/handover" "$DST/reports"

# CONTEXT.md (없으면 인계서 기반 생성은 수동)
cp "$SRC/CONTEXT.md" "$DST/" 2>/dev/null || echo "⚠️ CONTEXT.md 없음 (수동 생성 또는 인계서 기반 작성)"

# cursorrules
cp /srv/newtalk-v2/.cursorrules "$DST/cursorrules.md" 2>/dev/null || cp "${SRC%/docs}/.cursorrules" "$DST/cursorrules.md" 2>/dev/null || echo "⚠️ .cursorrules 없음"

# 기획서, 아키텍처, CHANGELOG
cp "$SRC/planning/NT-V2-PLAN-002-FINAL.md" "$DST/" 2>/dev/null || true
cp "$SRC/architecture/NT-V2-ARCHITECTURE.md" "$DST/" 2>/dev/null || true
cp "$SRC/CHANGELOG.md" "$DST/" 2>/dev/null || true

# 인계서 (최신 3건)
ls -t "$SRC/handover/"*.md 2>/dev/null | head -3 | while read f; do cp "$f" "$DST/handover/"; done

# 보고서
cp "$SRC/reports/"*.md "$DST/reports/" 2>/dev/null || true

# 민감정보 제거
find "$DST" -name "*.md" -exec sed -i 's/NewTalk2026!@#/[REDACTED]/g' {} \;
find "$DST" -name "*.md" -exec sed -i 's/Test2026!@#/[REDACTED]/g' {} \;

# 민감정보 검사 (값 패턴만, 변수명 TOKEN_KEY 등 제외)
SENS_OUT=$(grep -rIiE "(password\s*=|secret\s*=|api_key\s*=|access_token\s*=|bearer [a-z0-9])" "$DST" 2>/dev/null | grep -vEi "ADMIN_TOKEN|RETAIL_TOKEN|TOKEN_KEY|REDACTED|Bearer [A-Z_]+" || true)
if [ -n "$SENS_OUT" ]; then echo "$SENS_OUT"; echo "민감정보 검출 — 동기화 중단"; exit 1; fi
cd /data/project-docs
git add -A
if git diff --cached --quiet; then
  echo "변경 없음"
else
  git diff --cached -- . ":!scripts/" | grep -iE "NewTalk2026" && { echo "민감정보 중단!"; exit 1; }
  git commit -m "[sync] newtalk-v2-api $(date +%Y%m%d_%H%M) — CONTEXT, cursorrules, 기획서, 아키텍처, 보고서"
  GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin master
  echo "✅ push 완료"
fi

echo ""
echo "=== 검증 ==="
curl -sf https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/CONTEXT.md | head -3 && echo "✅ CONTEXT OK" || echo "❌ CONTEXT 실패"
curl -sf https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/cursorrules.md | head -3 && echo "✅ cursorrules OK" || echo "❌ cursorrules 실패"
