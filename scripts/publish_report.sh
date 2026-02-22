#!/bin/bash
# ===========================================
# 작업 보고서 발행 스크립트
# 사용법: bash /data/project-docs/scripts/publish_report.sh [프로젝트명] [보고서파일경로]
# 예: bash /data/project-docs/scripts/publish_report.sh shortflow /data/shortflow/docs/reports/20260224_작업명.md
# ===========================================

PROJECT=$1
REPORT_FILE=$2

if [ -z "$PROJECT" ] || [ -z "$REPORT_FILE" ]; then
    echo "사용법: $0 [프로젝트명] [보고서파일경로]"
    echo "예: $0 shortflow /data/shortflow/docs/reports/20260224_youtube_oauth.md"
    exit 1
fi

DST="/data/project-docs/${PROJECT}/reports"
mkdir -p ${DST}

FILENAME=$(basename "$REPORT_FILE")
cp "$REPORT_FILE" "${DST}/${FILENAME}"

echo "[publish] ${PROJECT}/reports/${FILENAME} 복사 완료"

cd /data/project-docs
git add -A
CHANGED=$(git diff --cached --name-only)
if [ -n "$CHANGED" ]; then
    git commit -m "[report] ${PROJECT}: ${FILENAME}"
    git push origin master
    echo "=== 발행 완료: push 성공 ==="
    echo "확인 URL: https://raw.githubusercontent.com/moongoby/project-docs/master/${PROJECT}/reports/${FILENAME}"
else
    echo "=== 변경 없음: push 스킵 ==="
fi
