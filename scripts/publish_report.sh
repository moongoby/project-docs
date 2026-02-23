#!/bin/bash
# ===========================================
# 작업 보고서 발행 스크립트
# [방식 1] 일반 프로젝트: bash $0 [프로젝트명] [보고서파일경로]
#   예: bash $0 shortflow /data/shortflow/docs/reports/20260224_작업명.md
# [방식 2] KIS AutoTrade: bash $0 [작업명]
#   예: bash $0 MINUTE-COLLECTOR-STATUS
# ===========================================

set -e
TS=$(date '+%Y-%m-%d %H:%M:%S')

# 방식 1: 프로젝트명 + 파일경로 (2개 인자)
if [ -n "$2" ]; then
    PROJECT=$1
    REPORT_FILE=$2
    if [ ! -f "$REPORT_FILE" ]; then
        echo "ERROR: 파일 없음: $REPORT_FILE"
        exit 1
    fi
    DST="/root/project-docs/${PROJECT}/reports"
    if [ ! -d /root/project-docs ]; then
        DST="/data/project-docs/${PROJECT}/reports"
    fi
    mkdir -p "$DST"
    FILENAME=$(basename "$REPORT_FILE")
    cp "$REPORT_FILE" "${DST}/${FILENAME}"
    echo "[publish] ${PROJECT}/reports/${FILENAME} 복사 완료"
    cd /root/project-docs 2>/dev/null || cd /data/project-docs
    git add -A
    if git diff --cached --quiet; then
        echo "=== 변경 없음: push 스킵 ==="
    else
        git commit -m "[report] ${PROJECT}: ${FILENAME}"
        git push origin master
        echo "=== 발행 완료 ==="
        echo "https://raw.githubusercontent.com/moongoby/project-docs/master/${PROJECT}/reports/${FILENAME}"
    fi
    exit 0
fi

# 방식 2: KIS AutoTrade — 작업명만 (1개 인자)
TASK_NAME="$1"
SRC_DIR="/root/kis-autotrade-v4/report"
DST_DIR="/root/project-docs/kis-autotrade-v4/reports"

if [ -z "$TASK_NAME" ]; then
    echo "사용법 (KIS): bash $0 작업명"
    echo "예시:   bash $0 MINUTE-COLLECTOR-STATUS"
    echo ""
    echo "사용법 (일반): bash $0 프로젝트명 보고서파일경로"
    echo ""
    echo "사용 가능한 KIS 보고서:"
    ls -1 "$SRC_DIR/"*.md 2>/dev/null | tail -20
    exit 1
fi

REPORT_FILE=$(find "$SRC_DIR" -maxdepth 2 -name "*${TASK_NAME}*" -type f | sort | tail -1)

if [ -z "$REPORT_FILE" ]; then
    echo "ERROR: '$TASK_NAME' 보고서를 찾을 수 없음"
    echo "검색 경로: $SRC_DIR"
    exit 1
fi

BASENAME=$(basename "$REPORT_FILE")
echo "=== 보고서 배포: $BASENAME ==="

echo "[1/4] 보안 점검..."
if grep -qiE 'app_key|app_secret|appsecret|password|passwd|token.*=.*[A-Za-z0-9]{20}|account.*number|계좌번호' "$REPORT_FILE"; then
    echo "!!! 경고: 보고서에 민감 정보 의심 패턴 감지 — 배포 중단 !!!"
    exit 1
fi
echo "    통과"

echo "[2/4] 복사..."
mkdir -p "$DST_DIR"
cp "$REPORT_FILE" "$DST_DIR/$BASENAME"
echo "    $BASENAME → reports/"

echo "[3/4] Git 커밋 & 푸시..."
cd /root/project-docs
git add -A
if git diff --cached --quiet; then
    echo "    변경 없음"
else
    if git diff --cached --name-only | grep -qiE '\.env|\.key|\.pem|credential|secret|\.py$'; then
        echo "!!! 민감 파일 — 취소 !!!"
        git reset HEAD
        exit 1
    fi
    git commit -m "report: $BASENAME ($TS)"
    git push origin master
    echo "    푸시 완료"
fi

echo ""
echo "[4/4] Public URL:"
echo "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/$BASENAME"
echo "=== 배포 완료 ==="
