---
description: KIS AutoTrade V4.1 자동매매 시스템 전용 규칙
globs: [
  "backend/app/services/trading/**",
  "backend/app/services/fund/**",
  "backend/app/services/adaptive/**",
  "backend/app/services/market/**",
  "backend/app/services/data_pipeline/**",
  "backend/app/services/scheduler/**",
  "backend/app/api/v4_*.py",
  "scripts/backtest/**",
  "scripts/collection/**",
  "scripts/analysis/**"
]
---

# KIS AutoTrade V4.1 — 전용 규칙

## 절대 규칙 (CLAUDE.md 공통 규칙보다 V4.1 전용이 우선)
1. kis-v41-api / kis-v41-monitor / kis-v41-scheduler 재시작 금지 (CEO 승인 + 지시서 명시 시에만 1회)
2. strategy_cards 테이블: ALTER/DROP/DELETE 절대 금지, UPDATE는 CEO 승인 후에만
3. v4_positions 직접 수정(UPDATE/DELETE) 절대 금지
4. backtest_engine_v2.py 수정은 CEO 승인 후에만
5. 핵심 파일 수정 시 검수 필수 (review/ 업로드 → CEO+Claude 승인 후 적용):
   - v4_pipeline_orchestrator.py, strategy_engine.py, risk_manager.py
   - order_executor.py, position_manager.py, split_transfer_engine.py
   - lifecycle.py, fund/*, adaptive/*, regime_detector.py
   - backtest_engine_v2.py, collector_minute.py, main.py
6. 사전 확인 필수: strategy_cards = 62, v4_positions OPEN = 5
7. 작업 완료 시 보고서 필수: report/v41/{작업ID}-{YYYYMMDD}.md
   보고서 동기화: bash /root/project-docs/scripts/sync_reports.sh

## 환경
- Python 3.12, FastAPI, SQLAlchemy (asyncpg), PostgreSQL 16, Redis 7.x
- 프로젝트 루트: /root/kis-autotrade-v4
- 가상환경: source venv/bin/activate
- PYTHONPATH: /root/kis-autotrade-v4:/root/kis-autotrade-v4/backend
- DB명: kisautotrade (NOT kis_autotrading)
- 테스트: python -m pytest scripts/ -v --tb=short

## 코드 규칙
- datetime.utcnow() 절대 금지 → datetime.now(timezone.utc)
- v4_* 테이블: INSERT/SELECT만, TRUNCATE/DROP/ALTER 절대 금지
- 레거시 테이블(ohlcv_1m, daily_investor_stats, stock_universe): SELECT만
- DB 세션: Depends(get_db) 필수
- 인증: Depends(get_current_user) 또는 Depends(get_optional_user)
- 시크릿 하드코딩 금지 → os.getenv
- 로깅: logger.info("msg %s", var) (f-string 금지)
- 타입 힌트: typing.Any (bare Any 금지)
- 미사용 import 금지

## 아키텍처 계층
CEO → Adaptive Engine → Fund Commander → DESK1~5 Commander
→ Strategy Cards → Pipeline Orchestrator → Signal Engine
→ Risk Manager → Order Executor → Position Manager
→ Promotion/Transfer Engine

## DESK 정의
| DESK | 역할 | max_hold | 라이브/전체 | 상태 |
|------|------|----------|------------|------|
| DESK1 | 초단타/스캘핑 | 0-1일 | 10/10 | 미검증, 인프라 구축 완료 |
| DESK2 | 단타 | 1-3일 | 10/16 | 분봉 진입 최적화 필요 (-23.25%) |
| DESK3 | 단기스윙 | 3-10일 | 9/11 | 주 수익원 (+32.23%) |
| DESK4 | 중기스윙 | 20-40일 | 6/9 | 운영 중 |
| DESK5 | 장기 | 90-120일 | 1/10 | 카드 부족 |

## 서비스 상태
| 서비스 | 포트 | 상태 | 비고 |
|--------|------|------|------|
| kis-v41-api | 8003 | active | nginx 프록시 |
| kis-v41-monitor | — | active | |
| kis-v41-scheduler | — | active | |
| kis-v41-minute-collector | — | inactive | 월요일 장전 활성화 |
| kis-v41-orderbook-collector | — | inactive | 월요일 장전 활성화 |

## DB 무결성 기준값
- strategy_cards: 62건
- v4_positions OPEN: 5건 (ID 49, 51, 55, 58, 61)
- DB 크기: 6,152 MB
- v4_ohlcv_minute: 19,468,781행
- v4_scalping_universe: 708종목
- v4_market_regime_daily: 59행
- 디스크: 53% 사용 (45GB 여유)

## DB 스키마 주요 테이블
- users: id, email, name(NOT NULL), is_active, is_admin, is_verified, created_at
  (username 없음, email_verified 없음)
- v4_trade_analysis: exit_date(date), realized_pnl(bigint), realized_pnl_pct(numeric(5,2))
- v4_system_heartbeat: cycle_count(int), cycle_id(int), module_status(jsonb)
- v4_backtest_results: 테이블 미존재 (참조 금지)
- v4_backtest_trades (BT-ENGINE-UPGRADE 2026-02-23):
  기존: session_id, stock_code, trade_type, price, quantity, pnl, trade_date, card_id,
        exit_reason, entry_date, exit_date, hold_days
  추가 16컬럼: entry_datetime(timestamp), exit_datetime(timestamp),
        entry_price(numeric), exit_price(numeric), mfe_pct(numeric), mae_pct(numeric),
        mfe_price(numeric), mae_price(numeric), regime_at_entry(varchar),
        indicator_snapshot(jsonb), slippage_pct(numeric), commission(numeric),
        sector(varchar), strategy_name(varchar), entry_volume(bigint),
        entry_spread_pct(numeric)
  주의: indicator_snapshot·sector INSERT 로직 미구현

## ORM 모델 (backend/app/models/)
- V4Position, V4PositionExtended (position.py)
- SystemStateLog, SystemHeartbeat (system.py)
- MarketRegimeDaily, MarketCalendar (market.py)
- Reservation (execution.py)

## 핵심 파일 경로
- FastAPI 진입점: backend/app/main.py
- 파이프라인: backend/app/services/trading/v4_pipeline_orchestrator.py
- 전략 엔진: backend/app/services/trading/strategy_engine.py
- 리스크 관리: backend/app/services/trading/risk_manager.py
- 주문 실행: backend/app/services/trading/order_executor.py
- 포지션 관리: backend/app/services/trading/position_manager.py
- 프로모션: backend/app/services/trading/split_transfer_engine.py
- 라이프사이클: backend/app/services/trading/lifecycle.py
- 펀드 서비스: backend/app/services/fund/
- 어댑티브: backend/app/services/adaptive/
- 레짐 감지: backend/app/services/market/regime_detector.py
- 백테스트: scripts/backtest/backtest_engine_v2.py
- 분봉 수집: backend/app/services/data_pipeline/collector_minute.py
- 호가 수집: scripts/collection/orderbook_collector.py
- DESK 추천 API: backend/app/api/v4_desk_recommend.py

## 백테스트 실행 명령
cd /root/kis-autotrade-v4 && source venv/bin/activate
PYTHONPATH=/root/kis-autotrade-v4/backend python scripts/backtest/run_backtest.py \
  --start YYYYMMDD --end YYYYMMDD --capital 1000000 --name "설명" --engine v2 \
  --desk-strategies '[{"desk_id":3,"card_id":8}]'
주의: --desk-id 없음, --desk-strategies JSON 사용

## 커밋 컨벤션
- feat: 신규 기능
- fix: 버그 수정
- refactor: 리팩토링
- test: 테스트 추가/수정
- docs: 문서 변경
- V4.1 커밋 형식: feat: CUR-{작업ID} {설명}

## 작업 절차
1. 수정 전 백업: sudo -u postgres pg_dump -d kisautotrade -Fc -f /tmp/backup_{작업명}_{TS}.dump
2. 한 파일 수정 후 관련 테스트 실행
3. 전체 수정 후: python -m pytest scripts/ -v --tb=short
4. 테스트 실패 시 롤백 후 원인 분석
5. 서비스 상태 확인: systemctl is-active kis-v41-api kis-v41-monitor kis-v41-scheduler
   (재시작은 절대 금지 — CEO/지시서 명시 시에만)
6. 보고서 작성: report/v41/{작업ID}-{YYYYMMDD}.md
7. 보고서 동기화: bash /root/project-docs/scripts/sync_reports.sh

## 코드 검수 프로세스
핵심 파일 수정 시:
1. cp {수정파일} /root/project-docs/kis-autotrade-v4/review/{파일명}__REVIEW__{작업ID}.py
2. 파일 상단에 CODE REVIEW REQUEST 헤더 삽입
3. bash /root/project-docs/scripts/push_review.sh {작업ID}
4. 사용자에게 검수 URL 보고 → 작업 일시 중단
5. 승인 후 적용, bash /root/project-docs/scripts/clean_review.sh

## 실패 교훈 (반복 금지)
- 대시보드 덮어쓰기(2/20): 신규 UI 별도 파일, 레거시 보존
- DESK2 분봉 -23.25%: 분봉 진입 로직 검증 없이 LIVE 전환 금지
- 프로모션 단일 조건: min_profit_pct만 체크 → 다중 조건 필요
- DESK 간 중복 매수(19종목): Guard 미구현, CEO 정책 대기

## 현재 작업 큐
| 순위 | 작업 | 상태 |
|------|------|------|
| P0 | MINUTE-COLLECTOR-STATUS | Cursor 결과 대기 |
| P1 | DESK2-MINUTE-REBT | P0 후 |
| P2 | DESK5-CARD-BT | P1 후 |
| P3 | OVERLAP-GUARD | CEO 정책 대기 |
| P4 | REGIME-FILTER | CEO 승인 대기 |
| P5 | DESK1-LIVE-PREP | 월요일 09:00 전 |

## CEO 결정 대기
1. DESK 간 중복 매수 정책
2. 레짐 기반 DESK2 진입 제한
3. 레짐 전환 방어 모드 48h
4. strategy_cards 61, 62 처리
5. index_daily OHLC=0 재수집

## 공유 파일 주의사항 (GO100과 공유)
아래 파일은 GO100 프로젝트와 공유됨. 수정 시 GO100 PM에게 알릴 것:
- backend/app/services/trading/strategy_card_service.py
- backend/app/main.py
- frontend/src/app/layout.tsx
- frontend/src/app/backtest/page.tsx
- frontend/src/app/strategy-cards/page.tsx
