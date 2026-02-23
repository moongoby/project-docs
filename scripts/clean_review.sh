#!/bin/bash
set -e

PUBLIC_ROOT="/root/project-docs"

echo "=== 검수 파일 정리 ==="

# README.md를 제외한 review/ 파일 삭제
V41_FILES=$(find "$PUBLIC_ROOT/kis-autotrade-v4/review" -name "*__REVIEW__*" 2>/dev/null)
GO100_FILES=$(find "$PUBLIC_ROOT/go100/review" -name "*__REVIEW__*" 2>/dev/null)

if [ -z "$V41_FILES" ] && [ -z "$GO100_FILES" ]; then
  echo "  정리할 검수 파일 없음"
  exit 0
fi

for f in $V41_FILES $GO100_FILES; do
  echo "  삭제: $(basename $f)"
  rm "$f"
done

cd "$PUBLIC_ROOT"
git add -A
if git diff --cached --quiet; then
  echo "  변경사항 없음"
else
  git commit -m "review: 검수 완료 파일 정리"
  git push origin master
  echo "  ✓ 정리 완료, 푸시됨"
fi
echo "=== 검수 디렉토리 클린 ==="
