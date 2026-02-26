# CUR-GO100-GOAL-ENGINE-001 실행 보고서
**작성일:** 2026-02-25 (KST)  
**브랜치:** feat/CUR-GO100-GOAL-ENGINE-001 → phase-2c-command-center (병합 완료)

## 1. 작업 요약
- **Goal Engine + UserProfile + Intent 확장** (트랙 C)
- 기존 DB 스키마(go100_user_profiles, go100_goals) 유지; 신규 DDL은 이미 테이블 존재로 인덱스만 추가 시도(권한 이슈로 스킵).
- 백엔드 서비스·라우터·인텐트만 지시서 스펙에 맞춰 정리 및 확장.

## 2. 수행 내용

### 2.1 백업 및 브랜치
- `/root/backup/ai-backup-20260225/`, `/root/backup/routers-go100-backup-20260225/` 생성
- 브랜치 `feat/CUR-GO100-GOAL-ENGINE-001` 생성 및 작업

### 2.2 ProfileService (스펙 정렬)
- **파일:** `backend/app/services/go100/user/profile_service.py`
- **추가:** `ProfileService` 클래스 (스펙 alias)
  - `get_or_create_profile(db, user_id)` → dict
  - `update_profile(db, user_id, data)` → dict
  - `get_llm_context(db, user_id)` → str (LLM 프롬프트용 문자열)
  - `increment_stats(db, user_id, field, amount=1)` (total_strategies_created, total_backtests_run, total_trades_executed)
- `UserProfileService` 유지, `__init__.py`에서 `ProfileService` export 추가

### 2.3 GoalEngine
- **파일:** `backend/app/services/go100/goal/goal_engine.py`
- **수정:** `import re` 추가 (`_parse_goal_from_message` 사용처)
- 헤더에 CUR-GO100-GOAL-ENGINE-001 주석 추가
- 기존 DB 컬럼(goal_id, target_capital, risk_appetite 등) 유지

### 2.4 Intent Router 확장
- **파일:** `backend/app/services/go100/ai/intent_router.py`
- **우선순위:** 기존 3개 > 신규 4개  
  `optimize_existing` → `help` → `goal_setup` → `stock_info` → `market_briefing` → `portfolio_status` → `strategy`
- **신규 인텐트 키워드 (지시서 명세):**
  - **goal_setup:** 목표, 계획, 달성, 부자, 은퇴, 연금, CAGR, 수익률 목표, 몇년, 억, 만원 모으, 자산 증식 등
  - **stock_info:** 종목 정보, 주가, 시세, 차트, 재무, 실적, 뉴스, 삼성전자, PER, PBR, ROE 등
  - **market_briefing:** 시장, 오늘 장, 코스피, 코스닥, 환율, 시장 동향, 브리핑, 요약, 장 마감 등
  - **portfolio_status:** 포트폴리오, 내 자산, 수익률, 잔액, 보유 종목, 현황, 계좌 등
- 기존 help / optimize_existing / strategy 키워드 유지

### 2.5 goal_router 및 main
- **파일:** `backend/app/routers/go100/goal_router.py`
  - `get_effective_uid(db, current_user["user_id"])` 적용 (POST/GET 목록/GET 상세/PUT 모두)
  - tags `go100-goals`로 통일
- **파일:** `backend/app/main.py`
  - `from backend.app.routers.go100.goal_router import router as go100_goal_router` 추가 (기존 `app.include_router(go100_goal_router)`와 연결)

### 2.6 ai_router
- **파일:** `backend/app/routers/go100/ai_router.py`
- 헤더에 CUR-GO100-GOAL-ENGINE-001 및 goal_setup/스텁 3개 주석 추가
- 기존 goal_setup / stock_info / market_briefing / portfolio_status 플로우·스텁 유지

## 3. 수정 파일 목록
| 구분 | 경로 |
|------|------|
| 수정 | backend/app/main.py |
| 수정 | backend/app/routers/go100/ai_router.py |
| 수정 | backend/app/routers/go100/goal_router.py |
| 수정 | backend/app/services/go100/ai/intent_router.py |
| 수정 | backend/app/services/go100/goal/goal_engine.py |
| 수정 | backend/app/services/go100/user/__init__.py |
| 수정 | backend/app/services/go100/user/profile_service.py |

## 4. 검증
- **린트:** 해당 파일들 린트 에러 없음
- **Import:** ProfileService, GoalEngine, goal_router import 가능 (환경에 따라 venv/env 필요)
- **Intent:** `route_intent('도움말')=='help'`, `route_intent('전략 만들어줘')=='strategy'`, `route_intent('10억 목표 세우자')=='goal_setup'`, `route_intent('삼성전자 주가')=='stock_info'` 등 로직 검증 완료
- **DB:** go100_user_profiles, go100_goals 기존 스키마 유지 (신규 DDL은 IF NOT EXISTS로 실행, 인덱스 권한 이슈만 존재)

## 5. 커밋 및 병합
- 커밋: `feat: CUR-GO100-GOAL-ENGINE-001 - GoalEngine + UserProfile + Intent 7개 확장`
- `feat/CUR-GO100-GOAL-ENGINE-001` → `phase-2c-command-center` 병합 (--no-ff) 후 `origin/phase-2c-command-center` 푸시 완료

## 6. 비고
- **kis-v41-*** 서비스는 재시작하지 않음 (지시서 준수).
- GO100 서비스 재시작은 필요 시 운영에서 별도 수행.
- pre-commit 시 기존 TS 오류(backtest page `checkBacktestReadiness`) 존재하며, 본 작업과 무관.
