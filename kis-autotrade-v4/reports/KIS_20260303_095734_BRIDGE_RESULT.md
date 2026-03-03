---
project: KIS-AutoTrade-V4.1
task_id: CUR-V41-DESK2-DATA-GAP-FIX-001
completed_at: 2026-03-03T10:15:00+09:00
---

# DESK2 DATA GAP FIX 실행 결과 보고

## Phase 1 — 02-28 백필 결과

### 핵심 발견: 2026-02-28은 토요일(비거래일)
- 지시서의 `--date 2026-02-28` 기반 백필은 비거래일로 0건이 정상

### 실행한 스크립트 및 결과

| 스크립트 | 지시서 명칭 | 실행 결과 |
|---------|-----------|---------|
| `collect_ohlcv_daily.py --dates 20260228` | collect_ohlcv_daily.py --date 2026-02-28 | 비거래일 — 0건 |
| `collect_market_investor.py --date 20260228` | collect_investor_daily.py (파일 없음) | v4_market_investor_daily +600행 (KSP/KSQ) |
| `backfill_regime_history.py --from 20260228` | collect_market_regime.py (파일 없음) | 처리 0건 (비거래일) |
| `collect_vkospi.py --start 20260227 --end 20260228` | collect_vkospi.py --date 2026-02-28 | 저장 0건 (API 응답 없음) |

> ⚠️ 지시서 스크립트명 불일치:
> - `collect_investor_daily.py` → 실제: `collect_market_investor.py`
> - `collect_market_regime.py` → 실제: `backfill_regime_history.py`

### 각 테이블 최신 날짜 (현재 상태)

| 테이블 | 최신 날짜 | 상태 |
|-------|---------|------|
| ohlcv_daily | 20260227 (금) | ✅ 최신 |
| v4_investor_daily | 2026-02-27 (금) | ✅ 최신 |
| v4_market_regime_daily | 2026-02-27 (금) | ✅ 최신 |
| v4_vkospi_daily | **20260226 (목)** | ❌ 20260227(금) 갭 |

### 실제 갭 분석
- **v4_vkospi_daily**: 20260227(금) 데이터 미수집
  - collect_vkospi.py(KIS API): 저장 0건
  - collect_vkospi_alt.py(공공데이터 API): 접근 시도 결과 totalCount=0
  - 공공데이터 API는 20260225까지만 확인됨 (API 데이터 지연 현상)
  - 해결 방법: 수일 후 `collect_vkospi_alt.py --start 20260227 --end 20260227` 재실행

---

## Phase 2 — 03월 분봉 파티션 결과

| 항목 | 결과 |
|-----|------|
| v4_ohlcv_minute_2026_03 rows | **1,323건** |
| 오늘(2026-03-03) 최신 분봉 시각 | 10:02 |
| 파티션 상태 | ✅ 정상 (장 중 수집 정상) |

---

## Phase 3 — DESK2 P0 피처 구현 상태

| 피처 | 구현 여부 | 파일:라인 |
|-----|---------|---------|
| THEME_CYCLE | ✅ 구현됨 | feature_engine.py:221 `compute_theme_cycle`, feature_store.py:57, ai_scorer.py:308-320 |
| SMALL_CAP_QUALITY | ✅ 구현됨 | feature_engine.py:146 `compute_small_cap_quality`, feature_store.py:56 |
| DUAL_FLOW (DUAL_FLOW_20D) | ✅ 구현됨 | feature_engine.py:99 `compute_dual_flow_20d`, supply_demand_gate.py:159 |
| SEC_LEADER_FLAG | ✅ 구현됨 | trigger_desk4.py:5, feature_store.py:59, desk_engine/config.py:30 |

**→ 4개 P0 피처 모두 구현 완료**

---

## Phase 4 — DESK2 전용 테이블 사용 여부

DB에 존재하는 테이블: v4_desk2_candidates, v4_desk2_signals, v4_desk2_trades, v4_desk2_daily_summary

| 테이블 | DB 존재 | 코드 사용 | 사용 파일 |
|-------|--------|---------|---------|
| v4_desk2_candidates | ✅ | ✅ | desk_engine/desk2_feeder.py:45 (INSERT score/score_rank) |
| v4_desk2_signals | ✅ | ❌ | 미사용 (backend/app 내 참조 없음) |
| v4_desk2_trades | ✅ | ❌ | 미사용 (backend/app 내 참조 없음) |
| v4_desk2_daily_summary | ✅ | ❌ | 미사용 (v4_desk2_backtest API 라우터에서 간접 사용 가능성) |

---

## 다음 단계 (미구현/잔여 항목)

1. **vkospi 20260227 갭 해소**: 공공데이터 API 업데이트 확인 후 재수집
   ```bash
   python3 scripts/collect_vkospi_alt.py --start 20260227 --end 20260227
   ```

2. **v4_desk2_signals / desk2_trades / desk2_daily_summary 미활용**:
   - 테이블은 존재하나 backend 코드에서 미참조
   - desk2_signals 생성 로직, desk2_trades 기록 로직, daily_summary 집계 로직 구현 필요

3. **지시서-실제 스크립트명 불일치 문서화**:
   - 지시서 업데이트 필요: collect_investor_daily.py → collect_market_investor.py

---

## 실행 환경 노트

- claudebot 권한으로 실행 (쓰기 권한 제한)
- collect_vkospi_alt.py: 로그 파일 권한 에러 (`/root/kis-autotrade-v4/logs/cron/vkospi_alt.log` PermissionDenied) → root 실행 필요
- collect_ohlcv_daily.py: `PYTHONPATH=/root/kis-autotrade-v4/backend` 필요
