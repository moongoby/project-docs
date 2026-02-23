#!/bin/bash
# KIS AutoTrade V4.1 문서 + 보고서 동기화
# Private → Public (화이트리스트: .md만)
set -e

SRC="/root/kis-autotrade-v4/docs"
SRC_REPORT="/root/kis-autotrade-v4/report"
DST="/root/project-docs/kis-autotrade-v4"
TS=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== KIS AutoTrade 동기화: $TS ==="

# 디렉토리 확보
mkdir -p "$DST/architecture" "$DST/handover" "$DST/plan" "$DST/reports" "$DST/rules"

# 1. CONTEXT.md
echo "[1/7] CONTEXT.md..."
[ -f "$SRC/CONTEXT.md" ] && cp "$SRC/CONTEXT.md" "$DST/" && echo "    완료"

# 2. 아키텍처
echo "[2/7] architecture/"
for f in "$SRC/architecture/"*.md; do
    [ -f "$f" ] && cp "$f" "$DST/architecture/" && echo "    $(basename $f)"
done

# 3. 인계서
echo "[3/7] handover/"
for f in "$SRC/handover/"*.md; do
    [ -f "$f" ] && cp "$f" "$DST/handover/" && echo "    $(basename $f)"
done

# 4. 기획서
echo "[4/7] plan/"
for f in "$SRC/plan/"*.md; do
    [ -f "$f" ] && cp "$f" "$DST/plan/" && echo "    $(basename $f)"
done

# 5. Cursor 규칙 파일
echo "[5/7] rules/"
SRC_CLAUDE="/root/kis-autotrade-v4/CLAUDE.md"
SRC_RULES="/root/kis-autotrade-v4/.cursor/rules"
[ -f "$SRC_CLAUDE" ] && cp "$SRC_CLAUDE" "$DST/rules/CLAUDE.md" && echo "    CLAUDE.md"
for f in "$SRC_RULES/"*.md; do
    [ -f "$f" ] || continue
    BASENAME=$(basename "$f")
    if grep -qiE 'app_key|app_secret|password|계좌번호' "$f"; then
        echo "    SKIP (민감정보): $BASENAME"
        continue
    fi
    cp "$f" "$DST/rules/" && echo "    $BASENAME"
done

# 6. 보고서 (.md만)
echo "[6/7] reports/"
for f in "$SRC_REPORT/"*.md; do
    [ -f "$f" ] || continue
    BASENAME=$(basename "$f")
    # 보안 점검 — 개별 파일
    if grep -qiE 'app_key|app_secret|password|passwd|계좌번호' "$f"; then
        echo "    SKIP (민감정보): $BASENAME"
        continue
    fi
    cp "$f" "$DST/reports/" && echo "    $BASENAME"
done

# 6b. report/v41/ 하위폴더 .md
if [ -d "$SRC_REPORT/v41" ]; then
    for f in "$SRC_REPORT/v41/"*.md; do
        [ -f "$f" ] || continue
        BASENAME=$(basename "$f")
        if grep -qiE 'app_key|app_secret|password|passwd|계좌번호' "$f"; then
            echo "    SKIP (민감정보): $BASENAME"
            continue
        fi
        cp "$f" "$DST/reports/" && echo "    [v41] $BASENAME"
    done
fi

# 7. 보안 점검 (전체)
echo "[7/7] 보안 점검..."
DANGER=$(find "$DST" \
    -name ".env" -o -name "*.key" -o -name "*.pem" \
    -o -name "*credential*" -o -name "*secret*" \
    -o -name "*.py" -o -name "*.pyc" 2>/dev/null)
if [ -n "$DANGER" ]; then
    echo "!!! 민감 파일 감지 — 중단 !!!"
    echo "$DANGER"
    exit 1
fi
echo "    통과"

# Git
echo "[+] Git..."
cd /root/project-docs
git add -A
if git diff --cached --quiet; then
    echo "    변경 없음"
else
    if git diff --cached --name-only | \
       grep -qiE '\.env|\.key|\.pem|credential|secret|\.py$'; then
        echo "!!! 민감 파일 — 취소 !!!"
        git reset HEAD
        exit 1
    fi
    git commit -m "sync: KIS AutoTrade docs + reports ($TS)"
    git push origin master
    echo "    푸시 완료"
fi

echo "=== 완료: $(date '+%Y-%m-%d %H:%M:%S') ==="
