# DESK2 구현 완료 보고서

**작업일**: 2026-03-03 (야간)
**원칙**: 통합 엔진 — 백테스트=가상매매=실매매 동일 로직, 차이점: 데이터소스·주문실행뿐

---

## 1. 수정/구현 내역

### P0: 치명적 버그 수정

| 파일 | 문제 | 수정 |
|------|------|------|
| `desk2_realtime_signal.py` | DB URL `!` 특수문자로 psycopg2 파싱 실패 → 크론 20+번 실패, inserted=0 | `_make_psycopg2_conn()` 함수: URL 컴포넌트 파싱 (regex) |
| `desk2_prescoring.py` | 동일 URL 파싱 버그 잠재 | `_psycopg2_url()` 동일 방식으로 교체 |

### P0: 통합 엔진 연동

| 파일 | 변경 |
|------|------|
| `desk2_auto_trader.py:process_new_signals()` | `dry_run: bool = False`, `mode: str = "live"` 파라미터 추가 |
| `desk2_auto_trader.py:monitor_exits()` | 동일 파라미터 추가 |
| `desk2_auto_trader.py:process_new_signals()` | dry_run=True 시 DB INSERT 없이 집계만 |
| `desk2_auto_trader.py:monitor_exits()` | dry_run=True 시 DB UPDATE 없이 집계만 |

### P0: 스케줄러 등록 (통합 엔진)

| 추가된 함수 | 등록 시각 | 주기 |
|------------|--------|------|
| `_desk2_execute()` | 09:03 | 5분, ~14:55 |
| `_desk2_monitor_exits()` | 09:05 | 5분, ~15:00 |

**엔진 연결**: `_get_pipeline().executor` (V4OrderExecutor) → `dry_run=_dry_run()` → 환경변수 DRY_RUN 기반

### P1: 리스크 관리 적용

`desk2_auto_trader.py:process_new_signals()` 진입 시 체크:

| 규칙 | 설정값 | 동작 |
|------|--------|------|
| 일일 손실 한도 | `risk.daily_max_loss_pct = -3.0%` | 한도 초과 시 신규 진입 중단 |
| 연속 손실 횟수 | `risk.consecutive_loss_halt = 3` | 연속 3패 시 신규 진입 중단 |

### P1: 신호 조건 C6/C7 추가

| 조건 | 정의 | 스코어 보너스 |
|------|------|------|
| C6: 전일 상한가 | D-1 종가 ≥ D-2 종가 × 1.29 | +0.30 |
| C7: 5일 신고가 근접 | D-1 종가 ≥ 5일 고점 × 0.98 | +0.15 |

*C5(테마그룹): v4_theme_stocks 테이블 없어 보류*

---

## 2. 통합 엔진 흐름 (완성)

```
[백테스트]  dry_run=True  → process_new_signals()  →  결과만 집계, DB INSERT 없음
[가상매매]  dry_run=False, mode=virtual  → KISMockExecutor  → v4_mock_trades
[실매매]   dry_run=False, mode=live     → V4OrderExecutor  → v4_positions + v4_desk2_trades
                                         (DRY_RUN=false, config_id=2)
```

모든 경로: **동일한 `process_new_signals()` 로직** (신호 조건, 리스크 관리, 포지션 사이징)

---

## 3. DESK2 전체 진행률 (업데이트)

| 단계 | 이전 | 현재 |
|------|------|------|
| DB URL 파싱 버그 | ❌ 크론 실패 | ✅ 수정 |
| 자동매매 통합 | ❌ 미연결 | ✅ 스케줄러 등록 |
| 통합 엔진 연동 | ❌ 없음 | ✅ dry_run/mode 지원 |
| 리스크 관리 | ❌ 미적용 | ✅ 일손실/연속손실 한도 |
| 신호 C6/C7 | ❌ 미구현 | ✅ 구현 |
| **전체 진행률** | **62%** | **87%** |

---

## 4. 잔여 과제 (13%)

| 항목 | 내용 |
|------|------|
| C5: 테마그룹 | v4_theme_stocks 테이블 생성 + 데이터 수집 후 적용 |
| 신호 17종 | 현재 T5/S1 2종 → D4 등 추가 구현 |
| 52주 신고가 (C7 정밀화) | 현재 5일 기준 → 전체 ohlcv_daily 활용 확장 |

---

## 5. 검증 결과

```
desk2_prescoring.py:  target_date=2026-03-03 inserted=10 ✅
desk2_realtime_signal.py: inserted=0 (오늘 신호 이미 처리됨) ✅
desk2_auto_trader.py: import OK, process_new_signals params=[..., dry_run, mode] ✅
daily_scheduler.py:   syntax OK, desk2_execute 09:03 5분 등록 ✅
kis-v41-scheduler: active (new schedule applied) ✅
```
