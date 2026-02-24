# GO100 Git 운영 규칙
> 최종 갱신: 2026-02-24
> 모든 커서 세션은 이 규칙을 반드시 따른다

## 1. 브랜치 전략

### 브랜치 구조
```
phase-2c-command-center  (메인 개발 브랜치, 직접 커밋 금지)
├─ feat/CUR-GO100-{TASK-ID}    (기능 개발)
├─ fix/CUR-GO100-{TASK-ID}     (버그 수정)
└─ hotfix/CUR-GO100-{TASK-ID}  (긴급 수정)
```

### 작업 시작 시 (필수)
```bash
cd /root/kis-autotrade-v4
git checkout phase-2c-command-center
git pull origin phase-2c-command-center
git checkout -b {type}/CUR-GO100-{TASK-ID}
# 예: git checkout -b fix/CUR-GO100-TRADE-CARD-REVERT-FIX-001
```

### 작업 완료 시 (필수)
```bash
git checkout phase-2c-command-center
git pull origin phase-2c-command-center
git merge {type}/CUR-GO100-{TASK-ID} --no-ff
# 충돌 발생 시 반드시 수동 해결 후 검증
git push origin phase-2c-command-center
```

## 2. 커밋 전 필수 체크 (절대 규칙)

### 변경 파일 영향도 확인
```bash
# 커밋 전 반드시 실행
git diff --name-only

# 아래 보호 파일이 변경 목록에 있으면 반드시 확인
# 변경 의도가 없는 파일이 포함되었으면 git checkout -- {file}로 복원
```

### 보호 파일 목록 (변경 시 명시적 승인 필요)
```
frontend/src/app/(protected)/trade/page.tsx        # GO100 카드 지원
frontend/src/components/trade/ScheduleForm.tsx      # card_source 처리
backend/app/services/auto_trade_engine.py           # GO100 엔진 분기
backend/app/routers/trade_router.py                 # card_source 저장
frontend/src/lib/api/client.ts                      # 인증 refresh
frontend/src/lib/store/auth-store.ts                # 인증 상태
backend/app/api/v1/social_auth_router.py            # 소셜 로그인
```

### 보호 파일 변경 시 절차
```bash
# 1. 변경 전 백업
cp {file} {file}.protect-backup

# 2. 변경 후 diff로 의도한 변경만 포함 확인
git diff {file}

# 3. 보호 기능이 유지되는지 grep 확인
# trade/page.tsx: GO100 카드 포함 확인
grep -c "go100\|GO100\|card_source" frontend/src/app/\(protected\)/trade/page.tsx
# 0이면 GO100 지원이 삭제된 것 → 복원 필요

# auth-store.ts: refresh 로직 확인
grep -c "refreshToken\|refresh_token" frontend/src/lib/store/auth-store.ts
# 0이면 refresh 기능이 삭제된 것 → 복원 필요
```

## 3. 커밋 메시지 규칙

```
{type}: CUR-GO100-{TASK-ID} - {설명}

type:
  feat     새 기능
  fix      버그 수정
  hotfix   긴급 수정
  refactor 리팩토링
  docs     문서
  test     테스트
  chore    빌드/설정

예시:
  feat: CUR-GO100-AI-BACKTEST-OPT-001 - 백억이 백테스트 자동 최적화
  fix: CUR-GO100-TRADE-CARD-REVERT-FIX-001 - GO100 카드 드롭다운 재적용
```

## 4. 커밋 전 검증 스크립트 (필수 실행)

```bash
#!/bin/bash
# /root/kis-autotrade-v4/scripts/pre-commit-check.sh
# 커밋 전 반드시 실행

echo "=== GO100 Pre-Commit Check ==="

# 1. 보호 파일 변경 확인
PROTECTED_FILES=(
  "frontend/src/app/(protected)/trade/page.tsx"
  "frontend/src/components/trade/ScheduleForm.tsx"
  "backend/app/services/auto_trade_engine.py"
  "frontend/src/lib/api/client.ts"
  "frontend/src/lib/store/auth-store.ts"
)

CHANGED=$(git diff --cached --name-only)
for pf in "${PROTECTED_FILES[@]}"; do
  if echo "$CHANGED" | grep -q "$pf"; then
    echo "⚠️  보호 파일 변경됨: $pf"
    echo "   → 의도한 변경인지 확인하세요"
    echo "   → git diff --cached $pf"
  fi
done

# 2. GO100 카드 지원 확인
GO100_COUNT=$(grep -c "go100\|GO100\|card_source" \
  frontend/src/app/\(protected\)/trade/page.tsx 2>/dev/null || echo "0")
if [ "$GO100_COUNT" -lt "2" ]; then
  echo "❌ FAIL: trade/page.tsx에 GO100 카드 지원 코드가 없습니다!"
  echo "   → ENGINE-GO100-CARD-SUPPORT-001 수정이 삭제된 것 같습니다"
  exit 1
fi

# 3. 인증 refresh 확인
REFRESH_COUNT=$(grep -c "refreshToken\|refresh_token" \
  frontend/src/lib/store/auth-store.ts 2>/dev/null || echo "0")
if [ "$REFRESH_COUNT" -lt "2" ]; then
  echo "❌ FAIL: auth-store.ts에 refresh 로직이 없습니다!"
  echo "   → AUTH-REFRESH-v1 수정이 삭제된 것 같습니다"
  exit 1
fi

# 4. .env/.bak 커밋 방지
if echo "$CHANGED" | grep -qE "\.env|\.bak"; then
  echo "❌ FAIL: .env 또는 .bak 파일이 커밋에 포함되었습니다!"
  exit 1
fi

# 5. 빌드 확인
echo "--- Python syntax check ---"
find backend/app -name "*.py" -newer .git/index -exec python3 -m py_compile {} \; 2>&1

echo "--- TypeScript check ---"
cd frontend && npx tsc --noEmit 2>&1 | tail -5
cd ..

echo ""
echo "=== Pre-Commit Check 완료 ==="
```

## 5. 작업 충돌 방지

### 동시 작업 시
- 한 작업이 수정하는 파일 목록을 커밋 메시지 또는 보고서에 명시
- 다른 작업이 같은 파일을 수정해야 하면 먼저 병합 후 분기

### 파일 수정 후 회귀 확인
```bash
# 작업 완료 후 반드시 실행
bash /root/kis-autotrade-v4/scripts/pre-commit-check.sh
```
