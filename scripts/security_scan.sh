#!/bin/bash
# project-docs 보안 스캔 — push 전 실행
# 사용법: bash scripts/security_scan.sh
# 목적: 민감정보(IP, 비밀번호, 키, 이메일)가 커밋되기 전 탐지

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ISSUES=0

echo "=== Security Scan Start: $REPO_DIR ==="
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ---------------------------------------------------------
# 1. 구체적 IP 주소 노출 (마스킹 된 [.*-IP] 제외)
# ---------------------------------------------------------
IPS=$(grep -rn '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}' \
  "$REPO_DIR" --include="*.md" --include="*.sh" --include="*.py" \
  | grep -v "\.git/" \
  | grep -v "0\.0\.0\.0\|127\.0\.0\.1\|255\." \
  | grep -v "\[.*-IP\]\|\[ROUTER\]\|\[INTERNAL\]\|\[NAS\]\|\[SERVER\]\|\[CDN\]\|\[ADMIN")
if [ -n "$IPS" ]; then
  echo "[FAIL] IP 주소 노출:"
  echo "$IPS"
  echo ""
  ISSUES=$((ISSUES+1))
fi

# ---------------------------------------------------------
# 2. 비밀번호 / 실제 값이 포함된 키 패턴
# ---------------------------------------------------------
SECRETS=$(grep -rni \
  'password=[A-Za-z0-9!@#$%^&*]\|passwd=[A-Za-z0-9]\|PGPASSWORD='"'"'[A-Za-z0-9]\|APP_KEY=[A-Za-z0-9]\|api_key=[A-Za-z0-9]\|SECRET=[A-Za-z0-9]' \
  "$REPO_DIR" --include="*.md" --include="*.sh" --include="*.py" \
  | grep -v "\.git/" \
  | grep -v "\[DB-PASSWORD\]\|\[REDACTED\]\|example\|placeholder\|=\s*$\|='\.\.\.'")
if [ -n "$SECRETS" ]; then
  echo "[FAIL] 비밀번호/키 실제 값 노출:"
  echo "$SECRETS"
  echo ""
  ISSUES=$((ISSUES+1))
fi

# ---------------------------------------------------------
# 3. .env / .bak / .pem 파일 존재
# ---------------------------------------------------------
ENVS=$(find "$REPO_DIR" \( -name ".env" -o -name ".env.*" -o -name "*.bak" -o -name "*.pem" -o -name "*.key" \) \
  -not -path "*/.git/*" 2>/dev/null)
if [ -n "$ENVS" ]; then
  echo "[FAIL] 민감 파일 발견:"
  echo "$ENVS"
  echo ""
  ISSUES=$((ISSUES+1))
fi

# ---------------------------------------------------------
# 4. 개인 이메일 주소 (Gmail 등)
# ---------------------------------------------------------
EMAILS=$(grep -rn '@gmail\.com\|@naver\.com\|@kakao\.com\|@daum\.net' \
  "$REPO_DIR" --include="*.md" --include="*.sh" \
  | grep -v "\.git/" \
  | grep -v "\[CHANNEL-EMAIL\|REDACTED\|example@\|test@")
if [ -n "$EMAILS" ]; then
  echo "[FAIL] 개인 이메일 주소 노출:"
  echo "$EMAILS"
  echo ""
  ISSUES=$((ISSUES+1))
fi

# ---------------------------------------------------------
# 5. DATABASE_URL에 비밀번호 포함 여부
# ---------------------------------------------------------
DBURLS=$(grep -rni 'DATABASE_URL.*://.*:.*@\|postgresql.*://.*:.*@' \
  "$REPO_DIR" --include="*.md" --include="*.sh" --include="*.py" \
  | grep -v "\.git/" \
  | grep -v "scripts/security_scan\.sh" \
  | grep -v "\[DB-PASSWORD\]\|\[REDACTED\]\|\[DB_CONNECTION_STRING\]")
if [ -n "$DBURLS" ]; then
  echo "[FAIL] DATABASE_URL에 비밀번호 포함:"
  echo "$DBURLS"
  echo ""
  ISSUES=$((ISSUES+1))
fi

# ---------------------------------------------------------
# 결과 요약
# ---------------------------------------------------------
echo "========================================="
if [ $ISSUES -eq 0 ]; then
  echo "[PASS] 보안 스캔 통과 — 민감정보 없음"
  exit 0
else
  echo "[FAIL] $ISSUES 건 보안 이슈 발견 — 커밋 전 마스킹 필요"
  echo "마스킹 방법: sed -i 's/실제값/[MASKED]/g' <파일>"
  exit 1
fi
