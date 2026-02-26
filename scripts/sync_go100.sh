#!/bin/bash
# CUR-GO100-SYNC-CLEANUP, 2026-02-23
# GO100 문서 동기화: kis-autotrade-v4/docs/ → project-docs/go100/
# 사용법: bash /root/project-docs/scripts/sync_go100.sh

set -e

SOURCE="/root/kis-autotrade-v4/docs"
DEST="/root/project-docs/go100"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== GO100 문서 동기화 시작: $TIMESTAMP ==="

mkdir -p "$DEST"

DOCS="CONTEXT PLANNING ARCHITECTURE DB_SCHEMA API_SPEC HANDOVER CHANGELOG ISSUES ROADMAP"

for f in $DOCS; do
  if [ -f "$SOURCE/${f}.md" ]; then
    cp "$SOURCE/${f}.md" "$DEST/${f}.md"
    echo "✅ ${f}.md"
  else
    echo "⚠️ ${f}.md 없음"
  fi
done

# .cursorrules 참고용
if [ -f "/root/kis-autotrade-v4/.cursorrules" ]; then
  cp "/root/kis-autotrade-v4/.cursorrules" "$DEST/CURSORRULES.md"
  echo "✅ CURSORRULES.md"
fi

# 보고서 동기화 (GO100 전용만 — V4.1 중복 방지)
REPORT_SRC="/root/kis-autotrade-v4/report"
REPORT_DEST="/root/project-docs/go100/reports"

if [ -d "$REPORT_SRC" ]; then
  mkdir -p "$REPORT_DEST"
  for f in "$REPORT_SRC/"*.md; do
    [ -f "$f" ] || continue
    BASENAME=$(basename "$f")
    case "$BASENAME" in
      GO100-*|CUR-GO100-*|*HOTFIX-SAVE-500*|*PHASE2-STABILIZE*)
        cp "$f" "$REPORT_DEST/$BASENAME"
        echo "  ✅ $BASENAME"
        ;;
      *)
        echo "  ⏭️ SKIP (V4.1): $BASENAME"
        ;;
    esac
  done
  n=$(find "$REPORT_DEST" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l)
  echo "✅ GO100 보고서 동기화 (${n}건)"
else
  echo "⚠️ report/ 없음"
fi

# project-docs 커밋 + push
cd /root/project-docs
git add -A
if git diff --cached --quiet; then
  echo "변경 없음"
else
  git commit -m "sync: GO100 문서 동기화 ($TIMESTAMP)"
  git push origin master
  echo "✅ push 완료"
fi

echo ""
echo "=== Public URLs ==="
for f in $DOCS; do
  echo "  ${f}: https://raw.githubusercontent.com/moongoby/project-docs/master/go100/${f}.md"
done
