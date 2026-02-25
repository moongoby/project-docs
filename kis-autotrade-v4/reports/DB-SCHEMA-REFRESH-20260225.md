# DB 스키마 문서 최신화 보고서 (2026-02-25)

## 작업 요약
- **작업일**: 2026-02-25
- **목적**: 문서 레포(project-docs) 내 DB 스키마 및 관련 자료 최신화 후 푸시

## 반영 내용

### 1. database/DB-SCHEMA.md
- 최종 업데이트 일자: 2026-02-23 → **2026-02-25**
- **신규 테이블/섹션**
  - V4.1 백테스트 대시보드(DESK2): v4_bt_sessions, v4_bt_discoveries, v4_bt_trades, v4_bt_discovery_log, v4_bt_daily_risk_log, v4_bt_versions
  - 섹션 2-9 추가: 백테스트 대시보드 테이블 상세 (BT-DASHBOARD-IMPL-001, DESK2-BT-LIVE-PARITY-001)
- **GO100**
  - v4_trade_schedules.card_source (CUR-GO100-TRADE-MODAL-IMPL-001)
  - go100_backtest_runs.params_hash (CUR-GO100-OPTIMIZER-CORE-FIX-001)
- **무결성 기준**
  - strategy_cards: 65 → **60**, v4_positions OPEN: 5 → **11** (CONTEXT.md 기준)
- **변경 이력**: 2026-02-25 항목 4건 추가

### 2. CONTEXT.md
- 문서 체계(§10)에 **DB 스키마** 경로 추가:  
  `https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/database/DB-SCHEMA.md`

### 3. 본 보고서
- `kis-autotrade-v4/reports/DB-SCHEMA-REFRESH-20260225.md`

## 산출물 경로 (project-docs 기준)

| 구분 | 경로 |
|------|------|
| **KIS V4.1 DB 스키마 (메인)** | `kis-autotrade-v4/database/DB-SCHEMA.md` |
| 스키마 갱신 보고서 | `kis-autotrade-v4/reports/DB-SCHEMA-DOC-001-20260223.md` |
| 스키마 export 보고서 | `kis-autotrade-v4/reports/DB-SCHEMA-EXPORT-20260223.md` |
| 본 최신화 보고서 | `kis-autotrade-v4/reports/DB-SCHEMA-REFRESH-20260225.md` |
| **GO100 스키마 요약** | `go100/docs/DB-SCHEMA-GO100.md` |
| 프로젝트 컨텍스트 | `kis-autotrade-v4/CONTEXT.md` |

## 푸시
- 저장소: project-docs (origin master)
- 커밋 메시지: `docs: DB 스키마 최신화 (2026-02-25) — 백테스트 대시보드·GO100·무결성 기준 반영`
