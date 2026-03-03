---
project: KIS V4.1
task_id: CUR-V41-DESK2-SIGNAL-CODE-001
completed_at: "2026-03-03T11:26:00 KST"
status: SUCCESS
---

# RESULT: CUR-V41-DESK2-SIGNAL-CODE-001 — BRIDGE 코드 분석

## 작업1: 테이블 구조 확인

### v4_desk2_signals (11 컬럼)
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | integer | PK, auto-increment |
| signal_date | date | NOT NULL |
| stock_code | varchar(10) | NOT NULL |
| stock_type | varchar(10) | NOT NULL (TREND/REVERSAL/BORDER) |
| signal_name | varchar(20) | NOT NULL (T5/S1) |
| signal_time | timestamp | NOT NULL |
| signal_price | numeric(12,2) | NOT NULL |
| dip_pct | numeric(6,3) | nullable |
| entry_price | numeric(12,2) | nullable (매수 체결 후 세팅) |
| status | varchar(10) | default='NEW' |
| created_at | timestamp | default=now() |
- 인덱스: PK(id), idx_desk2_sig_date(signal_date)

### v4_desk2_trades (21 컬럼)
| 주요 컬럼 | 비고 |
|-----------|------|
| id, trade_date | PK |
| stock_code, stock_type, signal_name | 종목·유형 |
| entry_time, entry_price | 매수 정보 |
| exit_time, exit_price, exit_reason | 청산 정보 |
| quantity | 수량 |
| gross_pnl, net_pnl, gross_pnl_pct, net_pnl_pct | 손익 |
| commission | 수수료 |
| holding_minutes | 보유 시간 |
| score, score_rank | 후보 스코어 |
| metadata | jsonb |
- 인덱스: PK(id), idx_desk2_trade_date(trade_date)

### v4_desk2_daily_summary (15 컬럼)
| 주요 컬럼 | 비고 |
|-----------|------|
| id, trade_date | PK (trade_date UNIQUE) |
| total_trades, win_count, loss_count | 거래 집계 |
| win_rate, avg_pnl_pct, max_loss_pct | 성과 지표 |
| gross_pnl, net_pnl | 손익 |
| trend_count, reversal_count, border_count | 유형별 건수 |
| market_regime | 시장 국면 (varchar 10) |

---

## 작업2: 코드 참조 확인

```
scripts/desk2/desk2_realtime_signal.py  → v4_desk2_signals  INSERT (T5/S1 신호)
scripts/desk2/desk2_auto_trader.py      → v4_desk2_signals  SELECT(NEW) + UPDATE
                                        → v4_desk2_trades   INSERT + UPDATE(청산)
scripts/desk2/desk2_monitor.py          → 4개 테이블 전체 참조 (모니터링)
scripts/desk2_live_data_gen.py          → v4_desk2_signals, trades, daily_summary SELECT
```

총 4개 파일이 해당 테이블 참조. 모두 desk2 엔진 내부 코드.

---

## 작업3: desk2_realtime_signal.py 분석

### 파일 구조 (223줄)
```python
# 주요 함수:
_load_config()              # desk2_config.yaml 로드
_get_candidates(conn, date) # v4_desk2_candidates 조회
_get_minute_bars(conn, code, date)  # v4_ohlcv_minute 분봉 조회
_classify_type(dip_pct, ...)  # TREND/REVERSAL/BORDER 분류
_already_signaled(...)         # 중복 신호 방지 (당일 중복 INSERT 차단)
run(signal_date, as_of_time)   # 메인 실행 → 삽입된 신호 수 반환
```

### 신호 감지 로직
```
dip_pct = (open_price - low_so_far) / open_price * 100.0  # 당일 낙폭%

TREND 분류:  dip_pct < trend_dip_max (기본 1.0%)
REVERSAL 분류: dip_pct >= reversal_dip_min (기본 2.0%)
BORDER: 그 사이

T5 신호 (TREND):  close >= open*(1 + threshold_pct/100) AND bars >= delay_min+1
S1 신호 (REVERSAL): dip_pct >= 2.0% AND lookback 봉 close위치 0.4~0.6 사이
```

### INSERT 로직 (정상 확인)
- `_already_signaled()` 로 당일 동일(종목·유형·신호명) 중복 방지 ✅
- INSERT 후 마지막에 `conn.commit()` 1회 처리 ✅
- `entry_price` 는 INSERT 시 NULL (auto_trader에서 매수 후 UPDATE 예정) ✅
- S1: lookback_bars 루프 + `break` 으로 첫 매치만 삽입 ✅

### 잠재적 주의사항
- `db_url` 기본값: `"dbname=kisautotrade user=kis_admin host=localhost"` — 환경변수 `DATABASE_URL` 없으면 패스워드 없이 연결 시도 (pg_hba.conf trust 설정 의존)
- `as_of_time` 기본값 `15:30` — 장 중 실행 시 명시적 전달 필요

---

## 작업4: 현재 상태 스냅샷 (2026-03-03 11:26 KST)

| 테이블 | 행 수 |
|--------|-------|
| v4_desk2_candidates | **10** |
| v4_desk2_signals | **0** |
| v4_desk2_trades | **0** |
| v4_desk2_daily_summary | **0** |

> 오늘(2026-03-03) 후보 10종목 존재. 아직 신호 0건 — 신호 엔진 미실행 상태.

---

## 종합 진단

| 항목 | 상태 |
|------|------|
| 테이블 스키마 정합성 | ✅ 정상 (signals ↔ auto_trader 컬럼 일치) |
| INSERT 로직 | ✅ 정상 (중복방지, commit 1회) |
| 코드 참조 | ✅ 4개 파일이 올바른 테이블명 사용 |
| 당일 신호 | ⚠️ 0건 (신호 엔진 미실행 또는 조건 미충족) |
| DB 연결 | ⚠️ 직접 psql 연결 불가 (pg_hba 설정), Python psycopg2는 정상 |

## 조치 불필요 항목
- 코드 버그 없음 — 수정 불필요
- 스키마 구조 정상 — 마이그레이션 불필요

echo "DONE: code analysis only - no script execution"
