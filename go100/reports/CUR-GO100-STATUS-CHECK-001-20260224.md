# CUR-GO100-STATUS-CHECK-001 — 미확인 작업 상태 점검 보고서

**발행:** 2026-02-24 14:30 KST  
**우선순위:** P1

## 1. AI-BACKTEST-OPT-001
- **브랜치:** 없음 (phase-2c-command-center 등 현재 브랜치에 코드 반영된 상태)
- **관련 커밋:** 없음 (BACKTEST-OPT 키워드 커밋 없음)
- **코드 파일:** 존재
  - `backend/app/services/go100/optimizer/` — backtest_optimizer.py, fit_engine.py, optimizer_service.py, schemas.py, __init__.py
  - `backend/app/routers/go100/optimizer_router.py`
  - CUR-GO100-AI-BACKTEST-OPT 참조: schemas.py, optimizer_service.py, fit_engine.py, backtest_optimizer.py, optimizer_router.py, ai_router.py, intent_router.py
- **DB 테이블:** 확인 불가 (본 점검 환경에서 psql Peer authentication 실패. 서버 [SERVER-IP]에서 직접 `PGPASSWORD='...' psql -U kis_admin -d kisautotrade` 로 재확인 권장)
- **보고서:** 존재 — `/root/project-docs/go100/reports/CUR-GO100-AI-BACKTEST-OPT-001-20260224.md`
- **판정:** **완료** (코드·보고서 반영됨, DB는 서버에서 별도 확인)

## 2. MARKET-REGIME-001
- **브랜치:** 없음 (별도 MARKET-REGIME 브랜치 없음)
- **관련 커밋:** 있음 — REGIME/레짐 관련 커밋 다수 (예: CUR-STRATEGY-REGIME-BT-VIZ-001, CUR-REGIME-BACKFILL-002, regime 백테스트/알림 등)
- **코드 파일:** 존재 — go100 내 regime 참조: `backend/app/services/go100/ai/prompts.py`, `backend/app/services/go100/universe/advanced_filters.py`
- **DB 테이블:** 확인 불가 (동일하게 psql 연결 실패. 서버에서 regime 관련 테이블 직접 조회 권장)
- **보고서:** 없음 (*MARKET-REGIME* 이름의 보고서 파일 없음)
- **판정:** **진행중** (레짐 관련 코드·커밋은 있으나, MARKET-REGIME-001 전용 보고서 및 브랜치 없음)

## 3. TRADE-CARD-REVERT-FIX-002
- **브랜치:** 없음
- **관련 커밋:** 없음 (TRADE-CARD-REVERT/CARD-REVERT 키워드 커밋 없음)
- **/trade GO100 카드 지원:** 유지 — `frontend/src/app/(protected)/trade/page.tsx` 에서 `source: "go100"`, 카탈로그 GO100 카드 처리 및 CUR-GO100-TRADE-SCHEDULE-CARD-FIX-001 주석 존재 (4건 참조)
- **보고서:** 없음 (*TRADE-CARD-REVERT* 이름의 보고서 파일 없음)
- **판정:** **완료/불필요** (GO100 카드 지원 코드 유지됨, Revert-Fix 전용 브랜치/보고서는 없음)

## 4. VAPID 키
- **.env 등록:** 완료 — `.env` 내 VAPID 관련 항목 4건 존재 (값은 보안상 미출력)

## 5. 미해결 이슈
- **ISS-012 (ChatWidget DEFAULT_USER_ID):** 미해결 — `frontend/src/go100/components/ChatWidget.tsx` 27행 `const DEFAULT_USER_ID = 1;`, 94행 `user_id: DEFAULT_USER_ID` 하드코딩 존재
- **ISS-011 (/go100/chat redirect):** 미해결 — `frontend/src/app/(protected)/go100/chat/page.tsx` 10행 `router.replace("/llm");` 존재

## 6. 서버 보고서 목록
- 디렉토리: `/root/project-docs/go100/reports/` 존재
- CUR-GO100-*, GO100-* 등 90개 이상 보고서 파일 보유 (예: CUR-GO100-AI-BACKTEST-OPT-001-20260224.md, CUR-GO100-DOC-SYNC-AND-VAPID-001-20260224.md, GO100-ACCOUNTS-PAGE-TUTORIAL-REFLECTION-REPORT.md 등)
- 전체 목록: `ls -la /root/project-docs/go100/reports/` 로 확인 가능

---
*CUR-GO100-STATUS-CHECK-001 점검 완료. DB 항목은 실제 서버([SERVER-IP])에서 psql로 재확인 권장.*
