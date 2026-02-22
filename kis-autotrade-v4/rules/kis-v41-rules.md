---
description: KIS AutoTrade V4.1 프로젝트 공통 규칙
globs: ["backend/**/*.py", "scripts/**/*.py"]
---

# KIS AutoTrade V4.1 — Cursor Project Rules

## 환경
- Python 3.12, FastAPI, SQLAlchemy (asyncpg), PostgreSQL 16, Redis 7.x
- 프로젝트 루트: /root/kis-autotrade-v4
- 가상환경: source venv/bin/activate
- PYTHONPATH: /root/kis-autotrade-v4/backend
- DB명: kisautotrade (NOT kis_autotrading)
- 테스트 명령: python -m pytest scripts/ -v --tb=short

## 코드 필수 규칙
- datetime.utcnow() 절대 사용 금지 → datetime.now(timezone.utc) 사용
- v4_* 테이블: INSERT/SELECT만 허용, TRUNCATE/DROP/ALTER 절대 금지
- 레거시 테이블(ohlcv_1m, daily_investor_stats, stock_universe): SELECT만 허용
- DB 세션: 반드시 Depends(get_db) 사용, AsyncSessionLocal 직접 사용 금지
- 인증: Depends(get_current_user) 또는 Depends(get_optional_user) 필수
- 시크릿 값 하드코딩 금지 (os.getenv 사용)
- f-string 로거 금지 → logger.info("msg %s", var) 형식
- 타입 힌트: any 금지 → typing.Any 사용
- 미사용 import 금지

## DB 스키마 참고
- users: id, email, name(NOT NULL), is_active, is_admin, is_verified, created_at
  - username 컬럼 없음, email_verified 컬럼 없음
- v4_trade_analysis: exit_date(date), realized_pnl(bigint), realized_pnl_pct(numeric(5,2)) 존재
- v4_system_heartbeat: cycle_count(int), cycle_id(int) 둘 다 존재, module_status(jsonb)
- v4_backtest_results: 테이블 미존재

## ORM 모델 (backend/app/models/)
- V4Position, V4PositionExtended (position.py)
- SystemStateLog, SystemHeartbeat (system.py)
- MarketRegimeDaily, MarketCalendar (market.py)
- Reservation (execution.py)

## 커밋 컨벤션
- feat: 신규 기능
- fix: 버그 수정
- refactor: 리팩토링
- test: 테스트 추가/수정
- docs: 문서 변경

## 작업 절차
1. 수정 전 백업 생성
2. 한 파일 수정 후 관련 테스트 즉시 실행
3. 전체 수정 완료 후 python -m pytest scripts/ -v --tb=short
4. 테스트 실패 시 롤백 후 원인 분석
5. 커밋 후 systemctl restart kis-webapp-api → health 확인
