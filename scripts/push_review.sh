#!/bin/bash
set -e

TASK_ID="${1:?사용법: push_review.sh <작업ID>}"
PUBLIC_ROOT="/root/project-docs"

echo "=== 검수 파일 업로드: $TASK_ID ==="

# review/ 디렉토리에 REVIEW 파일 존재 확인
V41_COUNT=$(find "$PUBLIC_ROOT/kis-autotrade-v4/review" -name "*__REVIEW__${TASK_ID}*" 2>/dev/null | wc -l)
GO100_COUNT=$(find "$PUBLIC_ROOT/go100/review" -name "*__REVIEW__${TASK_ID}*" 2>/dev/null | wc -l)
TOTAL=$((V41_COUNT + GO100_COUNT))

if [ "$TOTAL" -eq 0 ]; then
  echo "❌ __REVIEW__${TASK_ID} 파일이 없습니다."
  exit 1
fi

echo "  검수 파일 $TOTAL개 발견 (V4.1: $V41_COUNT, GO100: $GO100_COUNT)"

# 보안 검사
echo "[보안 검사]"
FOUND_SECRETS=0
for f in $(find "$PUBLIC_ROOT" -path "*/review/*__REVIEW__*" \( -name "*.py" -o -name "*.md" \) 2>/dev/null); do
  if grep -qiE "appkey|appsecret|password|api_key|secret_key|REAL_TOKEN|DB_PASSWORD" "$f"; then
    echo "  ❌ 민감정보 발견: $f"
    FOUND_SECRETS=1
  fi
done

if [ "$FOUND_SECRETS" -eq 1 ]; then
  echo "❌ 민감정보가 포함된 파일이 있습니다. 제거 후 재실행하세요."
  exit 1
fi
echo "  ✓ 보안 검사 통과"

# 검수 헤더 존재 확인
for f in $(find "$PUBLIC_ROOT" -path "*/review/*__REVIEW__*" 2>/dev/null); do
  if ! grep -q "CODE REVIEW REQUEST" "$f"; then
    echo "  ⚠️ 검수 헤더 누락: $(basename $f) — 헤더를 추가하세요"
  fi
done

# Git 커밋 & 푸시
cd "$PUBLIC_ROOT"
git add -A
if git diff --cached --quiet; then
  echo "  변경사항 없음"
else
  git commit -m "review: ${TASK_ID} 검수 요청"
  git push origin master
  echo "  ✓ 푸시 완료"
fi

# 검수 URL 출력
echo ""
echo "=== 검수 URL (CEO에게 전달) ==="
for f in $(find "$PUBLIC_ROOT" -path "*/review/*__REVIEW__${TASK_ID}*" 2>/dev/null); do
  REL_PATH="${f#$PUBLIC_ROOT/}"
  echo "  https://raw.githubusercontent.com/moongoby/project-docs/master/$REL_PATH"
done
echo "=== 검수 요청 완료. 승인 대기 중 ==="
