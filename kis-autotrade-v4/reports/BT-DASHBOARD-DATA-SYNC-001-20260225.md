# BT-DASHBOARD-DATA-SYNC-001 대시보드 데이터 동기화 보고서
**작성일:** 2026-02-25  
**우선순위:** P0

## 1. 테이블 현황

| 테이블 | 행 수 | 비고 |
|--------|--------|------|
| v4_bt_sessions | 3 | LIVE-PARITY·DESK2 세션 |
| v4_bt_trades | 5 | 동일 테이블에 LIVE-PARITY 확장 컬럼 존재 |
| v4_bt_discoveries | 0 → 6922 | 마이그레이션 후 discovery_log 동기화분 반영 |
| v4_bt_discovery_log | 7033 | LIVE-PARITY 발굴 전수 기록 |
| v4_bt_daily_risk_log | 1 | LIVE-PARITY 일별 리스크 |
| v4_bt_versions | 0 | 버전 이력 |

- **LIVE-PARITY(bt_data_writer)** 사용: `v4_bt_sessions`, `v4_bt_trades`, `v4_bt_discovery_log`, `v4_bt_daily_risk_log`, `v4_bt_versions`, `v4_bt_discoveries`(write_discovery는 백테스터에서 미호출).
- **DASHBOARD(bt_dashboard.py)** 사용: `v4_bt_sessions`, `v4_bt_trades`, `v4_bt_discoveries`, `v4_bt_versions`.

## 2. 스키마 차이 분석

### 판정: CASE A + CASE C

- **CASE A (동일 테이블):**
  - **v4_bt_sessions**: LIVE-PARITY와 DASHBOARD 동일 테이블. `desk_id`는 DB 기본값 `'2'`로 처리됨.
  - **v4_bt_trades**: 동일 테이블. 이미 `regime_at_entry`, `composite_score`, `cs_score`, `gross_pnl_pct`, `fee_amount`, `tax_amount`, `slippage_amount`, `net_pnl_pct`, `slot_name` 등 LIVE-PARITY 확장 컬럼 존재. 대시보드 API가 해당 컬럼을 SELECT에 포함하도록 수정함.

- **CASE C (마이그레이션):**
  - **v4_bt_discoveries**: DASHBOARD는 이 테이블만 참조하나, 백테스터는 `write_discovery_log`만 호출해 `v4_bt_discovery_log`에만 적재됨. `v4_bt_discoveries`는 0건이었음.  
  - **조치:** `v4_bt_discovery_log` + `v4_bt_sessions` 조인으로 `v4_bt_discoveries` 일회성 INSERT 마이그레이션 수행. session_id, trade_date, trade_time, stock_code, condition_code(=condition_id), desk_score, passed_to_strategy, strategy_name(=primary_strategy), reject_reason 등 매핑. **6,922건** INSERT 완료.

## 3. 동기화 조치

### 3-1. bt_dashboard.py 수정 (LIVE-PARITY 컬럼 노출)

- **GET /sessions/{id}/trades**  
  SELECT에 추가: `regime_at_entry`, `composite_score`, `cs_score`, `gross_pnl_pct`, `fee_amount`, `tax_amount`, `slippage_amount`, `net_pnl_pct`, `slot_name`
- **GET /sessions/{id}/trades/{trade_id}**  
  동일 컬럼 추가.
- **GET /sessions/{id}/daily/{date}**  
  SELECT에 추가: `regime_at_entry`, `composite_score`, `cs_score`, `net_pnl_pct`

※ API 재시작 금지 규칙에 따라 서버 재시작은 하지 않음. **배포/재시작 후** 위 필드가 응답에 포함됨.

### 3-2. 기존 데이터 마이그레이션

- **v4_bt_discovery_log → v4_bt_discoveries**  
  - 조건: `v4_bt_sessions`와 조인, 동일 session_id·trade_date·stock_code·condition_code·trade_time 중복 제거용 NOT EXISTS 사용.  
  - 실행 결과: **INSERT 6,922건**.

### 3-3. bt_data_writer.py

- 변경 없음. 이미 `v4_bt_sessions`, `v4_bt_trades`(LIVE-PARITY 확장 컬럼 포함), `v4_bt_discovery_log`, `v4_bt_daily_risk_log`, `v4_bt_versions` 기록 중.  
- 향후 선택 사항: 백테스터에서 발굴 시 `write_discovery`도 호출하면 `v4_bt_discoveries`에 직접 적재 가능(현재는 discovery_log 기반 마이그레이션으로 대시보드 표시 가능).

## 4. API 응답 확인

- **GET /api/v1/backtest/sessions?limit=10**  
  - HTTP 200, `count: 3`, 세션 3건 정상 (DESK2 1건, LIVE-PARITY 2건).
- **GET /api/v1/backtest/readiness**  
  - HTTP 200, checklist·strategies 정상.
- **GET /api/v1/backtest/sessions/{session_id}**  
  - HTTP 200, 세션 상세(parameters, fail_reasons 등) 정상.
- **GET /api/v1/backtest/sessions/{session_id}/discoveries?limit=3**  
  - HTTP 200, 마이그레이션 반영으로 발굴 목록 정상 (condition_code, desk_score, passed_to_strategy 등).
- **GET /api/v1/backtest/sessions/{session_id}/trades**  
  - HTTP 200, 거래 목록 정상. LIVE-PARITY 컬럼은 코드 반영 완료, **재시작 후** 응답에 포함됨.
- **GET /api/v1/backtest/sessions/{session_id}/goal-tracking**  
  - HTTP 200, 목표 달성 기준·diagnostics 정상.

## 5. 대시보드 표시 상태

| 항목 | 상태 |
|------|------|
| 세션 목록 | ✅ 정상 (3건) |
| 세션 상세 | ✅ 정상 |
| 발굴 목록/통계 | ✅ 마이그레이션 후 정상 (v4_bt_discoveries 6,922건) |
| 거래 목록/상세 | ✅ 정상 (LIVE-PARITY 컬럼은 재시작 후 API에 반영) |
| 목표 달성/목표 추적 | ✅ 정상 |
| 실매매 준비도 | ✅ 정상 |

- 프론트엔드(https://trading41.newtalk.kr/admin/backtest) 세션 카드 표시는 동일 API 사용 시 정상 노출 가능.

## 완료 체크리스트

| # | 항목 | 확인 |
|---|------|------|
| 1 | v4_bt_* 테이블 목록/행수 파악 | ✅ |
| 2 | LIVE-PARITY vs DASHBOARD 스키마 차이 분석 | ✅ CASE A + C |
| 3 | 동기화 구현 (API SELECT 확장 + discoveries 마이그레이션) | ✅ |
| 4 | /api/v1/backtest/sessions 정상 응답 | ✅ |
| 5 | 대시보드 세션/발굴/거래/목표 표시 가능 | ✅ |
| 6 | 보고서 push + URL 200 | 진행 예정 |
| 7 | 실거래 파일 변경 0건 | ✅ (v4_positions 등 미변경) |
