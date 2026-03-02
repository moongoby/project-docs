#!/bin/bash
# 5개 프로젝트 공통 검증 스크립트
# 사용법: ./verify.sh [보고서파일명 또는 프로젝트]
# 예: ./verify.sh CUR-V41-GENSPARK-POC-001-20260303.md
# 예: ./verify.sh kis-autotrade-v4

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [ -n "${1:-}" ]; then
    if [[ "$1" == *.md ]]; then
        "$SCRIPT_DIR/path_check.sh" "$1"
    else
        case "$1" in
            go100|kis-autotrade-v4|shortflow|nas-image|newtalk-v2-api)
                echo "━━━ 프로젝트: $1 ━━━"
                ls -la "$1/reports/" 2>/dev/null | head -20 || echo "  (reports 없음)"
                [ -f "$1/HANDOVER.md" ] && echo "  HANDOVER.md 존재" || echo "  HANDOVER.md 없음"
                ;;
            *)
                echo "사용법: $0 <보고서파일명.md> 또는 <프로젝트폴더명>"
                echo "프로젝트: go100, kis-autotrade-v4, shortflow, nas-image, newtalk-v2-api"
                exit 1
                ;;
        esac
    fi
else
    echo "━━━ 5개 프로젝트 경로·보고서 존재 확인 ━━━"
    for proj in go100 kis-autotrade-v4 shortflow nas-image newtalk-v2-api; do
        if [ -d "$REPO_ROOT/$proj" ]; then
            count=$(ls "$REPO_ROOT/$proj/reports/"*.md 2>/dev/null | wc -l)
            echo "  $proj: reports $count건"
        else
            echo "  $proj: 폴더 없음"
        fi
    done
    echo ""
    echo "보고서 검증: $0 <보고서파일명.md>"
fi
