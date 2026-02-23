# V41-RULES-ENHANCE — 작업 보고서 (2026-02-23)

## 개요
- **작업명**: V41-RULES-ENHANCE
- **목적**: GO100 PM 규칙 분리 후 kis-v41-rules.md를 V4.1 전용으로 전면 보강
- **DB/서비스 변경**: 없음 (규칙 파일만 수정)
- **수정 대상**: `.cursor/rules/kis-v41-rules.md` 만 (CLAUDE.md, go100-rules.md 수정 금지)

---

## 1. 사전 확인 결과

| 항목 | 기대값 | 결과 |
|------|--------|------|
| strategy_cards | 62 | **62** |
| v4_positions OPEN | 5 | **5** |
| kis-v41-api | active | **active** |
| kis-v41-monitor | active | **active** |
| kis-v41-scheduler | active | **active** |

---

## 2. GO100 PM 분리 확인 결과

- **CLAUDE.md**: 211서버 멀티 프로젝트 공통 규칙 형태. 프로젝트 식별(go100 / KIS·V4.1 → 해당 rules 적용), 공유 테이블·파일, 공통 절대 규칙만 기재.
- **GO100 컨텍스트 /api/go100/** grep: **0건** → GO100 API 엔드포인트 목록 제거됨.
- **.cursor/rules/** : `go100-rules.md`, `kis-v41-rules.md` 존재 확인.
- **.cursorrules**: rules 디렉토리 참조문 확인 (GO100 → go100-rules.md, KIS V4.1 → kis-v41-rules.md, 공통 → CLAUDE.md).
- **CLAUDE.md 잔존 사항**: 서버 공통 정보에 백엔드 8002 (go100), 프론트 3000 (go100-frontend), 재시작/헬스체크 규칙에 go100 서비스명 포함. 공통 문서이므로 GO100 측 정보로 보이며, **직접 수정 금지**에 따라 변경하지 않음. V4.1 전용 서비스(8003, kis-v41-*)는 kis-v41-rules.md에만 명시.

---

## 3. kis-v41-rules.md 보강 내역

| 구분 | 내용 |
|------|------|
| **globs 확장** | trading, fund, adaptive, market, data_pipeline, scheduler, backend/app/api/v4_*.py, scripts/backtest, scripts/collection, scripts/analysis |
| **절대 규칙** | 7항 (재시작 금지, strategy_cards/v4_positions/backtest_engine_v2 제한, 검수 필수, 사전 확인 62/5, 보고서 필수) |
| **환경** | Python 3.12, FastAPI, asyncpg, PostgreSQL 16, Redis, PYTHONPATH, DB명 kisautotrade |
| **코드 규칙** | utcnow 금지, v4_* INSERT/SELECT만, Depends(get_db)·인증, 로깅·타입·import |
| **아키텍처 계층** | CEO → Adaptive → Fund → DESK1~5 → Strategy Cards → Pipeline → Signal → Risk → Order → Position → Promotion/Transfer |
| **DESK 정의** | DESK1~5 테이블 (역할, max_hold, 라이브/전체, 상태) |
| **서비스 상태** | kis-v41-api 8003, monitor, scheduler active; minute/orderbook collector inactive |
| **DB 무결성 기준값** | strategy_cards 62건, OPEN 5건(ID 49,51,55,58,61), DB 크기, v4_ohlcv_minute 등 |
| **DB 스키마** | users, v4_trade_analysis, v4_system_heartbeat, v4_backtest_trades 16컬럼 추가 스키마 |
| **ORM 모델** | position.py, system.py, market.py, execution.py |
| **핵심 파일 경로** | main, pipeline, strategy_engine, risk_manager, order_executor, position_manager, split_transfer, lifecycle, fund/, adaptive/, regime_detector, backtest_engine_v2, collector_minute, orderbook_collector, v4_desk_recommend |
| **백테스트 실행 명령** | run_backtest.py --desk-strategies JSON (--desk-id 없음) |
| **커밋 컨벤션** | feat/fix/refactor/test/docs, V4.1 형식 CUR-{작업ID} |
| **작업 절차** | 백업 → 테스트 → 재시작 절대 금지 명시 → 보고서 → 동기화 |
| **코드 검수 프로세스** | review/ 업로드, push_review.sh, 승인 후 적용, clean_review.sh |
| **실패 교훈** | 대시보드 덮어쓰기, DESK2 분봉 LIVE 전환, 프로모션 단일 조건, DESK 간 중복 매수 Guard |
| **작업 큐** | P0 MINUTE-COLLECTOR-STATUS ~ P5 DESK1-LIVE-PREP |
| **CEO 결정 대기** | 5건 (중복 매수, 레짐 DESK2, 레짐 48h, strategy_cards 61·62, index_daily OHLC=0) |
| **공유 파일 주의사항** | strategy_card_service.py, main.py, layout.tsx, backtest/page.tsx, strategy-cards/page.tsx (GO100 PM 알림) |

- **제거/정리**: 기존 GO100 수정 금지 4항(go100_*, 라우터, 서비스, 프론트)은 별도 go100-rules.md로 이관된 전제 하에, V4.1 전용 절대 규칙·globs·경로로 통합. 공유 파일 주의사항으로 GO100 PM 알림만 유지.

---

## 4. CLAUDE.md 수정 필요 사항 (GO100 PM 협의)

- **직접 수정 금지** 준수로 CLAUDE.md는 변경하지 않음.
- V4.1 전용 서비스(kis-v41-api 8003, kis-v41-monitor, kis-v41-scheduler) 및 사전 확인값(strategy_cards=62, OPEN=5)은 **kis-v41-rules.md에만** 명시됨.
- 협의 필요 시: CLAUDE.md에 "V4.1 서비스는 kis-v41-rules.md 참조" 한 줄 추가 가능 (선택).

---

## 5. 영향

- **DB**: 없음  
- **서비스**: 없음 (재시작 없음)  
- **백업**: `/root/backups/v41_rules_enhance_20260223/kis-v41-rules.md.bak` 생성됨.

---

## 6. Public URL 검증

| 검증 항목 | 결과 |
|-----------|------|
| kis-v41-rules.md HTTP 상태 | **200** |
| "62건" 문구 포함 | **1건 이상** |
| "재시작은 절대 금지" 포함 | **1건** |

---

## 7. 컴플라이언스

- .env / .bak 미포함 커밋 확인 완료.
- strategy_cards 62건, v4_positions OPEN 5건 유지 확인.

---

## 8. 보고서 동기화

- `sync_reports.sh`는 `/root/project-docs/scripts/`에 없음. 필요 시 `sync_kis.sh` 또는 수동 동기화 적용.
- 보고서 위치: `report/v41/V41-RULES-ENHANCE-20260223.md`
