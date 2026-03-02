#!/bin/bash
# PATH-001 셀프 검증 스크립트
# 사용법: ./path_check.sh <보고서파일명>
# 예: ./path_check.sh CUR-GO100-P5-3-PORTFOLIO-OPTIMIZER-001-20260227.md

set -e
REPORT_FILE="$1"

if [ -z "$REPORT_FILE" ]; then
    echo "사용법: $0 <보고서파일명>"
    exit 1
fi

echo "━━━ PATH-001 검증 시작: $REPORT_FILE ━━━"

# 1) 프로젝트 판별 및 경로 확인
echo ""
echo "[1/5] 프로젝트 경로 확인"
if [[ "$REPORT_FILE" == CUR-GO100-* ]] || [[ "$REPORT_FILE" == *-GO100-* ]]; then
    PROJECT="go100"
    EXPECTED_DIR="/root/project-docs/go100/reports/"
elif [[ "$REPORT_FILE" == CUR-V41-* ]] || [[ "$REPORT_FILE" == DESK2-* ]]; then
    PROJECT="kis-autotrade-v4"
    EXPECTED_DIR="/root/project-docs/kis-autotrade-v4/reports/"
else
    echo "  ❌ 파일명에서 프로젝트 식별 불가: $REPORT_FILE"
    echo "  → CUR-GO100-* 또는 CUR-V41-* 또는 DESK2-* 형식 필요"
    exit 1
fi

if [ -f "${EXPECTED_DIR}${REPORT_FILE}" ]; then
    echo "  ✅ 파일 존재: ${EXPECTED_DIR}${REPORT_FILE}"
else
    echo "  ❌ 파일 없음: ${EXPECTED_DIR}${REPORT_FILE}"
    echo "  → 올바른 경로에 보고서를 저장하세요"
fi

# 2) 파일명 규칙 검증
echo ""
echo "[2/5] 파일명 규칙 검증"
if echo "$REPORT_FILE" | grep -qP '^(CUR-(GO100|V41)-[A-Z0-9]+-([A-Z0-9]+-)*\d{3}-\d{8}|DESK2-[A-Z0-9]+-([A-Z0-9]+-)*\d{3}-\d{8})\.md$'; then
    echo "  ✅ 파일명 규칙 준수"
else
    echo "  ⚠️  파일명 규칙 불일치 (엄격 검증 실패, 수동 확인 권장)"
    echo "  → 형식: CUR-{GO100|V41}-TASK-SEQ-YYYYMMDD.md"
fi

# 3) 교차 저장 검사
echo ""
echo "[3/5] 교차 저장 검사"
CROSS=$(git diff --cached --name-only 2>/dev/null | grep -E "^go100/.*(DESK2|CUR-V41)|^kis-autotrade-v4/.*CUR-GO100" || true)
if [ -z "$CROSS" ]; then
    echo "  ✅ 교차 저장 없음"
else
    echo "  ❌ 교차 저장 발견:"
    echo "  $CROSS"
fi

# 4) HANDOVER.md 업데이트 확인
echo ""
echo "[4/5] HANDOVER.md 업데이트 확인"
HANDOVER_CHANGED=$(git diff --cached --name-only 2>/dev/null | grep "${PROJECT}/HANDOVER.md" || true)
if [ -n "$HANDOVER_CHANGED" ]; then
    echo "  ✅ ${PROJECT}/HANDOVER.md 변경 감지"
else
    echo "  ⚠️  ${PROJECT}/HANDOVER.md 미변경 — 업데이트 필요!"
fi

# 5) HTTP 확인 안내
echo ""
echo "[5/5] push 후 HTTP 확인 명령어"
GH_PATH="${EXPECTED_DIR#/root/project-docs/}${REPORT_FILE}"
echo "  git push origin master"
echo "  sleep 5"
echo "  curl -s -o /dev/null -w '%{http_code}' https://raw.githubusercontent.com/moongoby/project-docs/master/${GH_PATH}"
echo "  → 200이면 정상"

echo ""
echo "━━━ PATH-001 검증 완료 ━━━"
