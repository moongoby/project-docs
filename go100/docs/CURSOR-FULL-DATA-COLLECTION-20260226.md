# V3.0 전체 데이터 수집 — Cursor 지시서

> **작성일**: 2026-02-26
> **기준 문서**: `RPT-GO100-BAEKOGI-V3-MASTER-PLAN-20260226.md` Section 7
> **용도**: 아래 내용을 Cursor에 붙여넣어 실행

---

## 기획서 vs 현재 DB 대조 결과

| # | 기획서 요구 데이터 | 현재 상태 | 조치 |
|---|-------------------|-----------|------|
| 1 | 상장폐지 OHLCV | `go100_delisted_stocks` 100건, `go100_delisted_ohlcv` 24,127건 | **수집 완료** — 스킵 |
| 2 | 과거 분봉 1년 | `v4_ohlcv_minute` 14개월 파티션 (2025-01~2026-03), 각 750MB~1.1GB | **수집 완료** — 스킵 |
| 3 | 과거 틱 3개월(50종목) | `v4_tick_data` 0건 | **미수집** — 키움 REST ka10079 필요 (대용량 3~5GB, 별도 진행) |
| 4 | 투자자별 매매동향 3년 | `v4_investor_daily` 261,410건, 3,943종목 | **수집 완료** — 스킵 |
| 5 | PIT 재무제표 5년 | `go100_fundamentals_pit` 테이블 없음 | **미수집** → 블록 8 |
| 6 | 오버나이트 갭 MV | `go100_overnight_gap` 없음 | **미생성** → 블록 2 |
| 7 | go100_global_market 1년 | 66건 (3개월, 2025-11-27~) | **부족** → 블록 1 |
| 8 | go100_sector_price | 테이블 없음 | **미생성** → 블록 3 |
| 9 | go100_sector_correlation | 테이블 없음 | **미생성** → 블록 3, 9 |
| 10 | go100_cross_market_signals | 테이블 없음 | **미생성** → 블록 4 |
| 11 | go100_signal_performance | 테이블 없음 | **미생성** → 블록 4 |
| 12 | go100_experience_log | 테이블 없음 | **미생성** → 블록 5 |
| 13 | go100_gap_analysis | 테이블 없음 | **미생성** → 블록 5 |
| 14 | go100_calibration_params | 테이블 없음 | **미생성** → 블록 5 |
| 15 | go100_trading_cost_params | 테이블 없음 | **미생성** → 블록 6 |
| 16 | go100_orderbook_daily_stats | 테이블 없음 | **미생성** → 블록 7 |
| 17 | go100_tick_daily_stats | 테이블 없음 | **미생성** → 블록 7 |
| 18 | go100_fundamentals_pit | 테이블 없음 | **미생성** → 블록 8 |

### 스키마 주의사항 (Cursor 실행 전 필수 확인)

1. **go100_global_market**: 지시서 블록 1의 `symbol/date/open/high/low/close` 구조가 **실제 스키마와 다름**
   - 실제 컬럼: `data_date, usd_krw, vix, sp500, sp500_change_pct, nasdaq, nasdaq_change_pct, dow, dow_change_pct, us10y_yield, sox, sox_change_pct, csi300, csi300_change_pct, wti_crude, wti_crude_change_pct, copper, copper_change_pct`
   - UNIQUE 제약: `data_date` (날짜당 1행, 심볼별 아님)
   - **블록 1 스크립트를 실제 컬럼에 맞게 수정 필요**

2. **ohlcv_daily.date**: `varchar(8)` 타입 (예: `'20260226'`), DATE 타입 아님
   - 블록 2 MV에서 날짜 비교 시 문자열 비교 또는 캐스팅 필요

3. **v4_ohlcv_minute**: 파티션 테이블 (월별). 직접 SELECT 시 파티션 키 필수

4. **v4_sector_stock_mapping**: `sector_name` 컬럼 확인 필요 (실제: `sector_code`일 수 있음)

---

## 전체 데이터 수집 — 미수집분 일괄 처리

V3.0 기획서에서 계획한 모든 데이터를 점검하고, 이미 수집된 것은 스킵, 없는 것만 수집한다.
에러 시 해당 블록만 스킵하고 다음 블록으로 진행. 전체 완료 후 종합 보고.

---

### 블록 0: 전체 현황 점검 (반드시 먼저 실행)

```bash
sudo -u postgres psql -d kisautotrade <<'SQL'

-- 기본 데이터
SELECT '01_ohlcv_daily' as tbl, count(*) as rows, count(DISTINCT stock_code) as stocks, min(date) as from_dt, max(date) as to_dt FROM ohlcv_daily
UNION ALL SELECT '02_v4_ohlcv_minute', count(*), count(DISTINCT stock_code), min(date)::text, max(date)::text FROM v4_ohlcv_minute
UNION ALL SELECT '03_v4_investor_daily', count(*), count(DISTINCT stock_code), min(trade_date)::text, max(trade_date)::text FROM v4_investor_daily
UNION ALL SELECT '04_stock_fundamentals', count(*), count(DISTINCT stock_code), min(date)::text, max(date)::text FROM stock_fundamentals
UNION ALL SELECT '05_go100_global_market', count(*), 0, min(data_date)::text, max(data_date)::text FROM go100_global_market
UNION ALL SELECT '06_v4_sector_stock_mapping', count(*), count(DISTINCT stock_code), '', '' FROM v4_sector_stock_mapping
UNION ALL SELECT '07_go100_delisted_stocks', count(*), count(DISTINCT stock_code), '', '' FROM go100_delisted_stocks
UNION ALL SELECT '08_go100_delisted_ohlcv', count(*), count(DISTINCT stock_code), min(date)::text, max(date)::text FROM go100_delisted_ohlcv
UNION ALL SELECT '09_go100_news_items', count(*), 0, '', '' FROM go100_news_items
UNION ALL SELECT '10_go100_strategy_cards', count(*), 0, '', '' FROM go100_strategy_cards
UNION ALL SELECT '11_go100_backtest_runs', count(*), 0, '', '' FROM go100_backtest_runs
ORDER BY tbl;

-- 틱/호가/실시간 테이블
SELECT '12_v4_tick_data' as tbl, count(*) as rows FROM v4_tick_data
UNION ALL SELECT '13_v4_orderbook_realtime', count(*) FROM v4_orderbook_realtime;

-- 신규 테이블 존재 여부
SELECT table_name FROM information_schema.tables
WHERE table_schema='public' AND table_name IN (
    'go100_cross_market_signals', 'go100_signal_performance',
    'go100_experience_log', 'go100_gap_analysis', 'go100_calibration_params',
    'go100_trading_cost_params', 'go100_overnight_gap',
    'go100_orderbook_daily_stats', 'go100_tick_daily_stats',
    'go100_fundamentals_pit', 'go100_sector_price', 'go100_sector_correlation'
) ORDER BY table_name;

-- 디스크
SQL
df -h /data /

echo "=== 블록 0 완료: 위 결과를 기반으로 수집 범위 결정 ==="
```

---

### 블록 1: 글로벌 지표 히스토리 확장 (3개월 → 1년)

```bash
# 현재 go100_global_market에 66일(3개월)만 있음. 1년치로 확장.
# 이미 있는 날짜는 ON CONFLICT DO NOTHING으로 스킵.
#
# ★ 주의: go100_global_market 스키마는 날짜당 1행, 심볼별이 아님
#   컬럼: data_date, usd_krw, vix, sp500, sp500_change_pct, nasdaq, nasdaq_change_pct,
#          dow, dow_change_pct, us10y_yield, sox, sox_change_pct, csi300, csi300_change_pct,
#          wti_crude, wti_crude_change_pct, copper, copper_change_pct

cat > /tmp/expand_global_history.py << 'PYTHON'
import psycopg2
from datetime import datetime, timedelta

def expand_global():
    try:
        import FinanceDataReader as fdr
    except:
        import subprocess
        subprocess.run(["pip", "install", "finance-datareader", "--quiet"])
        import FinanceDataReader as fdr

    conn = psycopg2.connect(dbname="kisautotrade", user="postgres", host="localhost")
    cur = conn.cursor()

    # 현재 수집 범위 확인
    cur.execute("SELECT min(data_date), max(data_date), count(*) FROM go100_global_market")
    row = cur.fetchone()
    print(f"현재 범위: {row[0]} ~ {row[1]} ({row[2]}건)")

    # 1년 전부터 수집
    start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    end = datetime.now().strftime("%Y-%m-%d")

    # 심볼 → 컬럼 매핑 (go100_global_market 실제 스키마에 맞춤)
    symbols = {
        "^GSPC": ("sp500", "sp500_change_pct"),
        "^IXIC": ("nasdaq", "nasdaq_change_pct"),
        "^DJI": ("dow", "dow_change_pct"),
        "^VIX": ("vix", None),
        "^TNX": ("us10y_yield", None),
        "USDKRW=X": ("usd_krw", None),
        "^SOX": ("sox", "sox_change_pct"),
        "ASHR": ("csi300", "csi300_change_pct"),
        "CL=F": ("wti_crude", "wti_crude_change_pct"),
        "HG=F": ("copper", "copper_change_pct"),
    }

    # 날짜별로 데이터를 모아서 한 행으로 INSERT
    from collections import defaultdict
    daily_data = defaultdict(dict)

    for sym, (col, chg_col) in symbols.items():
        try:
            df = fdr.DataReader(sym, start, end)
            if df is None or df.empty:
                print(f"  {sym}: 데이터 없음")
                continue

            prev_close = None
            for date_idx, row in df.iterrows():
                dt = date_idx.strftime("%Y-%m-%d")
                close = float(row.get('Close', 0))
                daily_data[dt][col] = close

                if chg_col and prev_close and prev_close > 0:
                    change_pct = (close - prev_close) / prev_close * 100
                    daily_data[dt][chg_col] = round(change_pct, 4)
                prev_close = close

            print(f"  {sym} ({col}): {len(df)}일")
        except Exception as e:
            print(f"  {sym} 에러: {e}")

    # 날짜별 INSERT/UPDATE
    total_inserted = 0
    total_updated = 0
    for dt in sorted(daily_data.keys()):
        data = daily_data[dt]

        # 이미 존재하는 날짜인지 확인
        cur.execute("SELECT id FROM go100_global_market WHERE data_date = %s", (dt,))
        existing = cur.fetchone()

        if existing:
            # 기존 행에서 NULL인 컬럼만 업데이트
            updates = []
            values = []
            for col_name, val in data.items():
                updates.append(f"{col_name} = COALESCE(go100_global_market.{col_name}, %s)")
                values.append(val)

            if updates:
                values.append(existing[0])
                cur.execute(f"""
                    UPDATE go100_global_market
                    SET {', '.join(updates)}
                    WHERE id = %s
                """, values)
                total_updated += 1
        else:
            # 새 행 INSERT
            cols = ['data_date'] + list(data.keys())
            vals = [dt] + list(data.values())
            placeholders = ', '.join(['%s'] * len(vals))
            cur.execute(f"""
                INSERT INTO go100_global_market ({', '.join(cols)})
                VALUES ({placeholders})
                ON CONFLICT (data_date) DO NOTHING
            """, vals)
            if cur.rowcount > 0:
                total_inserted += 1

        conn.commit()

    # 결과 확인
    cur.execute("SELECT count(*), min(data_date), max(data_date) FROM go100_global_market")
    row = cur.fetchone()
    print(f"\n결과: 총 {row[0]}건 ({row[1]} ~ {row[2]})")
    print(f"  신규: {total_inserted}건, 업데이트: {total_updated}건")

    cur.close()
    conn.close()

if __name__ == "__main__":
    print("=== 글로벌 지표 1년 확장 ===")
    expand_global()
PYTHON

cd /root/kis-autotrade-v4 && source venv/bin/activate
python /tmp/expand_global_history.py
```

---

### 블록 2: 오버나이트 갭 Materialized View 생성

```bash
sudo -u postgres psql -d kisautotrade <<'SQL'

-- 이미 존재하면 스킵
-- ★ 주의: ohlcv_daily.date는 varchar(8) 타입 (예: '20260226')
DO $
BEGIN
    IF NOT EXISTS (SELECT FROM pg_matviews WHERE matviewname = 'go100_overnight_gap') THEN
        EXECUTE '
        CREATE MATERIALIZED VIEW go100_overnight_gap AS
        SELECT
            t.stock_code,
            t.date,
            t.open AS today_open,
            t.close AS today_close,
            prev.close AS prev_close,
            CASE WHEN prev.close > 0
                 THEN ROUND(((t.open::numeric - prev.close::numeric) / prev.close::numeric * 100), 2)
                 ELSE 0 END AS gap_pct,
            t.volume
        FROM ohlcv_daily t
        JOIN ohlcv_daily prev
            ON t.stock_code = prev.stock_code
            AND prev.date = (
                SELECT MAX(p.date) FROM ohlcv_daily p
                WHERE p.stock_code = t.stock_code AND p.date < t.date
            )
        WHERE t.date >= to_char(NOW() - INTERVAL ''1 year'', ''YYYYMMDD'')
        ';

        CREATE INDEX IF NOT EXISTS idx_overnight_gap_code ON go100_overnight_gap(stock_code);
        CREATE INDEX IF NOT EXISTS idx_overnight_gap_date ON go100_overnight_gap(date);
        CREATE INDEX IF NOT EXISTS idx_overnight_gap_pct ON go100_overnight_gap(gap_pct);

        RAISE NOTICE 'go100_overnight_gap 생성 완료';
    ELSE
        REFRESH MATERIALIZED VIEW go100_overnight_gap;
        RAISE NOTICE 'go100_overnight_gap 이미 존재 — REFRESH 완료';
    END IF;
END $;

SELECT count(*) as total, count(DISTINCT stock_code) as stocks FROM go100_overnight_gap;

SQL
```

---

### 블록 3: 섹터 가격 시계열 + 상관계수 테이블

```bash
sudo -u postgres psql -d kisautotrade <<'SQL'

-- 3-1. 섹터 가격 테이블
CREATE TABLE IF NOT EXISTS go100_sector_price (
    id SERIAL PRIMARY KEY,
    sector_name VARCHAR(50) NOT NULL,
    date VARCHAR(8) NOT NULL,
    avg_change_pct NUMERIC(8,4),
    total_volume BIGINT,
    stock_count INT,
    top_gainer_code VARCHAR(20),
    top_gainer_pct NUMERIC(8,2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(sector_name, date)
);
CREATE INDEX IF NOT EXISTS idx_sector_price_date ON go100_sector_price(date);

-- 3-2. 섹터 상관계수 테이블
CREATE TABLE IF NOT EXISTS go100_sector_correlation (
    id SERIAL PRIMARY KEY,
    sector_a VARCHAR(50) NOT NULL,
    sector_b VARCHAR(50) NOT NULL,
    period VARCHAR(10) NOT NULL,  -- '1m', '3m', '6m', '1y'
    correlation NUMERIC(6,4),
    calculated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(sector_a, sector_b, period)
);

SQL

# 3-3. 섹터 가격 시계열 생성 (ohlcv_daily + sector_mapping 조인)
# ★ 주의: v4_sector_stock_mapping 컬럼명 확인 후 sector_name 또는 sector_code 사용
cat > /tmp/generate_sector_price.py << 'PYTHON'
import psycopg2
from datetime import datetime, timedelta

def generate():
    conn = psycopg2.connect(dbname="kisautotrade", user="postgres", host="localhost")
    cur = conn.cursor()

    # 매핑 테이블 컬럼명 확인
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name='v4_sector_stock_mapping'
        ORDER BY ordinal_position
    """)
    columns = [r[0] for r in cur.fetchall()]
    print(f"v4_sector_stock_mapping 컬럼: {columns}")

    # sector_name 또는 sector_code 자동 감지
    sector_col = 'sector_name' if 'sector_name' in columns else 'sector_code'
    print(f"섹터 컬럼: {sector_col}")

    # 이미 있는 날짜 확인
    cur.execute("SELECT max(date) FROM go100_sector_price")
    last_date = cur.fetchone()[0]

    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
    if last_date and last_date > start_date:
        start_date = last_date
        print(f"기존 데이터 {last_date}까지 존재, 이후만 생성")

    # 섹터별 일간 수익률 계산
    cur.execute(f"""
        INSERT INTO go100_sector_price (sector_name, date, avg_change_pct, total_volume, stock_count, top_gainer_code, top_gainer_pct)
        SELECT
            sm.{sector_col},
            o1.date,
            ROUND(AVG(
                CASE WHEN o2.close > 0
                THEN ((o1.close::numeric - o2.close::numeric) / o2.close::numeric * 100)
                ELSE 0 END
            ), 4) as avg_change_pct,
            SUM(o1.volume::bigint) as total_volume,
            COUNT(DISTINCT o1.stock_code) as stock_count,
            (ARRAY_AGG(o1.stock_code ORDER BY
                CASE WHEN o2.close > 0
                THEN ((o1.close::numeric - o2.close::numeric) / o2.close::numeric)
                ELSE 0 END DESC))[1] as top_gainer_code,
            ROUND(MAX(
                CASE WHEN o2.close > 0
                THEN ((o1.close::numeric - o2.close::numeric) / o2.close::numeric * 100)
                ELSE 0 END
            ), 2) as top_gainer_pct
        FROM ohlcv_daily o1
        JOIN v4_sector_stock_mapping sm ON o1.stock_code = sm.stock_code
        JOIN ohlcv_daily o2 ON o1.stock_code = o2.stock_code
            AND o2.date = (SELECT MAX(p.date) FROM ohlcv_daily p WHERE p.stock_code = o1.stock_code AND p.date < o1.date)
        WHERE o1.date > %s
        GROUP BY sm.{sector_col}, o1.date
        ON CONFLICT (sector_name, date) DO NOTHING
    """, (start_date,))

    inserted = cur.rowcount
    conn.commit()

    # 결과 확인
    cur.execute("SELECT count(*), count(DISTINCT sector_name), min(date), max(date) FROM go100_sector_price")
    row = cur.fetchone()
    print(f"섹터 가격: 총 {row[0]}건, {row[1]}개 섹터, {row[2]} ~ {row[3]}")
    print(f"이번 적재: {inserted}건")

    cur.close()
    conn.close()

if __name__ == "__main__":
    print("=== 섹터 가격 시계열 생성 ===")
    generate()
PYTHON

cd /root/kis-autotrade-v4 && source venv/bin/activate
python /tmp/generate_sector_price.py
```

---

### 블록 4: 크로스마켓 시그널 + 성과 추적 테이블 생성

```bash
sudo -u postgres psql -d kisautotrade <<'SQL'

CREATE TABLE IF NOT EXISTS go100_cross_market_signals (
    id SERIAL PRIMARY KEY,
    signal_date DATE NOT NULL,
    signal_type VARCHAR(50) NOT NULL,
    source_market VARCHAR(50) NOT NULL,
    target_market VARCHAR(50),
    direction VARCHAR(10),
    strength NUMERIC(5,2),
    description TEXT,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(signal_date, signal_type, source_market)
);
CREATE INDEX IF NOT EXISTS idx_cross_signal_date ON go100_cross_market_signals(signal_date);

CREATE TABLE IF NOT EXISTS go100_signal_performance (
    id SERIAL PRIMARY KEY,
    signal_id INT REFERENCES go100_cross_market_signals(id),
    signal_type VARCHAR(50),
    predicted_direction VARCHAR(10),
    actual_direction VARCHAR(10),
    predicted_magnitude NUMERIC(8,4),
    actual_magnitude NUMERIC(8,4),
    is_correct BOOLEAN,
    evaluated_at TIMESTAMP DEFAULT NOW()
);

SQL
```

---

### 블록 5: 경험 DB + 괴리 분석 + 보정 파라미터 테이블 생성

```bash
sudo -u postgres psql -d kisautotrade <<'SQL'

CREATE TABLE IF NOT EXISTS go100_experience_log (
    id SERIAL PRIMARY KEY,
    source VARCHAR(20) NOT NULL DEFAULT 'backtest',  -- backtest/paper/live
    strategy_card_id INT,
    stock_code VARCHAR(20),
    action VARCHAR(20),
    entry_date DATE,
    exit_date DATE,
    entry_price NUMERIC,
    exit_price NUMERIC,
    return_pct NUMERIC(8,4),
    regime VARCHAR(20),
    sector VARCHAR(50),
    market_snapshot JSONB,
    slippage_expected NUMERIC(6,4),
    slippage_actual NUMERIC(6,4),
    fill_rate NUMERIC(5,2),
    time_to_fill_sec INT,
    overnight_gap_pct NUMERIC(6,4),
    volume_participation_pct NUMERIC(6,4),
    market_impact_pct NUMERIC(6,4),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_exp_log_source ON go100_experience_log(source);
CREATE INDEX IF NOT EXISTS idx_exp_log_stock ON go100_experience_log(stock_code);
CREATE INDEX IF NOT EXISTS idx_exp_log_date ON go100_experience_log(entry_date);

CREATE TABLE IF NOT EXISTS go100_gap_analysis (
    id SERIAL PRIMARY KEY,
    strategy_card_id INT,
    period_start DATE,
    period_end DATE,
    backtest_return NUMERIC(8,4),
    paper_return NUMERIC(8,4),
    live_return NUMERIC(8,4),
    gap_pct NUMERIC(8,4),
    gap_source VARCHAR(50),
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS go100_calibration_params (
    id SERIAL PRIMARY KEY,
    param_name VARCHAR(50) NOT NULL,
    param_value NUMERIC(10,6),
    stock_type VARCHAR(20),  -- large/mid/small
    last_calibrated TIMESTAMP DEFAULT NOW(),
    notes TEXT,
    UNIQUE(param_name, stock_type)
);

-- 초기 보정 파라미터 시드 데이터
INSERT INTO go100_calibration_params (param_name, param_value, stock_type, notes) VALUES
    ('slippage_pct', 0.10, 'large', '대형주 슬리피지'),
    ('slippage_pct', 0.30, 'mid', '중형주 슬리피지'),
    ('slippage_pct', 0.50, 'small', '소형주 슬리피지'),
    ('volume_limit_pct', 10.0, 'large', '대형주 거래량 한도'),
    ('volume_limit_pct', 5.0, 'mid', '중형주 거래량 한도'),
    ('volume_limit_pct', 3.0, 'small', '소형주 거래량 한도'),
    ('commission_pct', 0.015, 'large', '수수료'),
    ('commission_pct', 0.015, 'mid', '수수료'),
    ('commission_pct', 0.015, 'small', '수수료'),
    ('tax_pct', 0.18, 'large', '세금'),
    ('tax_pct', 0.18, 'mid', '세금'),
    ('tax_pct', 0.18, 'small', '세금')
ON CONFLICT (param_name, stock_type) DO NOTHING;

SQL
```

---

### 블록 6: 트레이딩 비용 파라미터 테이블

```bash
sudo -u postgres psql -d kisautotrade <<'SQL'

CREATE TABLE IF NOT EXISTS go100_trading_cost_params (
    id SERIAL PRIMARY KEY,
    broker VARCHAR(20) NOT NULL,
    account_type VARCHAR(20),  -- real/paper
    commission_buy NUMERIC(8,6) DEFAULT 0.00015,
    commission_sell NUMERIC(8,6) DEFAULT 0.00015,
    tax_sell NUMERIC(8,6) DEFAULT 0.0018,
    slippage_default NUMERIC(8,6) DEFAULT 0.001,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(broker, account_type)
);

INSERT INTO go100_trading_cost_params (broker, account_type, commission_buy, commission_sell, tax_sell, slippage_default) VALUES
    ('KIS', 'real', 0.00015, 0.00015, 0.0018, 0.001),
    ('KIS', 'paper', 0.00015, 0.00015, 0.0018, 0.001),
    ('KIWOOM', 'real', 0.00015, 0.00015, 0.0018, 0.001)
ON CONFLICT (broker, account_type) DO NOTHING;

SQL
```

---

### 블록 7: 호가/틱 통계 집계 테이블

```bash
sudo -u postgres psql -d kisautotrade <<'SQL'

CREATE TABLE IF NOT EXISTS go100_orderbook_daily_stats (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    date VARCHAR(8) NOT NULL,
    avg_spread_pct NUMERIC(6,4),
    avg_bid_depth BIGINT,
    avg_ask_depth BIGINT,
    max_spread_pct NUMERIC(6,4),
    snapshot_count INT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_code, date)
);

CREATE TABLE IF NOT EXISTS go100_tick_daily_stats (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    date VARCHAR(8) NOT NULL,
    tick_count INT,
    avg_trade_size NUMERIC,
    large_trade_count INT,
    vwap NUMERIC,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_code, date)
);

SQL
```

---

### 블록 8: PIT 재무제표 전용 테이블 (DART 기반, 기존 stock_fundamentals 보강)

```bash
sudo -u postgres psql -d kisautotrade <<'SQL'

CREATE TABLE IF NOT EXISTS go100_fundamentals_pit (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    report_date DATE NOT NULL,
    fiscal_year INT,
    fiscal_quarter INT,
    revenue BIGINT,
    operating_profit BIGINT,
    net_income BIGINT,
    total_assets BIGINT,
    total_equity BIGINT,
    total_debt BIGINT,
    per NUMERIC(10,2),
    pbr NUMERIC(10,2),
    roe NUMERIC(10,2),
    debt_ratio NUMERIC(10,2),
    source VARCHAR(20) DEFAULT 'DART',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_code, report_date, fiscal_quarter)
);
CREATE INDEX IF NOT EXISTS idx_fund_pit_code ON go100_fundamentals_pit(stock_code);
CREATE INDEX IF NOT EXISTS idx_fund_pit_date ON go100_fundamentals_pit(report_date);

SQL

# PIT 데이터 수집 (DART API키가 있으면 OpenDartReader 사용, 없으면 pykrx fallback)
cat > /tmp/collect_pit_fundamentals.py << 'PYTHON'
import psycopg2
from datetime import datetime
import os

def collect_pit():
    conn = psycopg2.connect(dbname="kisautotrade", user="postgres", host="localhost")
    cur = conn.cursor()

    # 이미 수집된 건수 확인
    cur.execute("SELECT count(*) FROM go100_fundamentals_pit")
    existing = cur.fetchone()[0]
    print(f"기존 PIT 데이터: {existing}건")

    if existing > 1000:
        print("이미 충분한 PIT 데이터 존재. 스킵.")
        cur.close()
        conn.close()
        return

    # DART API키 확인
    dart_key = os.environ.get("DART_API_KEY", "")

    if dart_key:
        print("DART API키 발견. OpenDartReader로 수집...")
        try:
            import OpenDartReader
            dart = OpenDartReader(dart_key)

            # 주요 종목 재무제표 수집
            cur.execute("SELECT DISTINCT stock_code FROM v4_sector_stock_mapping ORDER BY stock_code LIMIT 500")
            stocks = [r[0] for r in cur.fetchall()]

            total = 0
            for i, code in enumerate(stocks):
                try:
                    for year in range(2021, 2026):
                        for quarter in [1, 2, 3, 4]:
                            reprt = {1: '11013', 2: '11012', 3: '11014', 4: '11011'}
                            try:
                                df = dart.finstate(code, year, reprt_code=reprt[quarter])
                                if df is not None and not df.empty:
                                    revenue = df[df['account_nm'].str.contains('매출', na=False)]['thstrm_amount'].values
                                    op = df[df['account_nm'].str.contains('영업이익', na=False)]['thstrm_amount'].values
                                    ni = df[df['account_nm'].str.contains('당기순이익', na=False)]['thstrm_amount'].values

                                    cur.execute("""
                                        INSERT INTO go100_fundamentals_pit
                                        (stock_code, report_date, fiscal_year, fiscal_quarter, revenue, operating_profit, net_income, source)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, 'DART')
                                        ON CONFLICT DO NOTHING
                                    """, (
                                        code, f"{year}-{quarter*3:02d}-28", year, quarter,
                                        int(revenue[0].replace(',','')) if len(revenue) > 0 else None,
                                        int(op[0].replace(',','')) if len(op) > 0 else None,
                                        int(ni[0].replace(',','')) if len(ni) > 0 else None
                                    ))
                                    total += 1
                            except:
                                continue
                    conn.commit()
                    if (i+1) % 50 == 0:
                        print(f"  진행: {i+1}/{len(stocks)} ({total}건)")
                except:
                    conn.rollback()

            print(f"DART 수집 완료: {total}건")
        except Exception as e:
            print(f"DART 수집 실패: {e}")
    else:
        print("DART API키 없음. pykrx fallback으로 PER/PBR/EPS만 수집...")
        try:
            from pykrx import stock as pykrx_stock
            import time

            # 분기별 기준일
            dates = [
                "20210331", "20210630", "20210930", "20211231",
                "20220331", "20220630", "20220930", "20221231",
                "20230331", "20230630", "20230930", "20231231",
                "20240331", "20240630", "20240930", "20241231",
                "20250331", "20250630", "20250930", "20251231",
            ]

            total = 0
            for dt in dates:
                try:
                    df = pykrx_stock.get_market_fundamental(dt, dt, market="ALL")
                    if df is None or df.empty:
                        continue

                    year = int(dt[:4])
                    quarter = (int(dt[4:6]) - 1) // 3 + 1

                    for ticker, row in df.iterrows():
                        try:
                            cur.execute("""
                                INSERT INTO go100_fundamentals_pit
                                (stock_code, report_date, fiscal_year, fiscal_quarter, per, pbr, roe, source)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, 'pykrx')
                                ON CONFLICT DO NOTHING
                            """, (
                                ticker, f"{dt[:4]}-{dt[4:6]}-{dt[6:8]}",
                                year, quarter,
                                float(row.get('PER', 0)) if row.get('PER', 0) != 0 else None,
                                float(row.get('PBR', 0)) if row.get('PBR', 0) != 0 else None,
                                None,  # ROE는 pykrx에서 직접 제공 안 함
                                ))
                            total += 1
                        except:
                            conn.rollback()
                            continue

                    conn.commit()
                    print(f"  {dt}: {len(df)}종목 (누적 {total}건)")
                    time.sleep(1)
                except Exception as e:
                    print(f"  {dt} 실패: {e}")

            print(f"pykrx fallback 완료: {total}건")
        except Exception as e:
            print(f"pykrx 수집도 실패: {e}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    print("=== PIT 재무제표 수집 ===")
    collect_pit()
PYTHON

cd /root/kis-autotrade-v4 && source venv/bin/activate
python /tmp/collect_pit_fundamentals.py
```

---

### 블록 9: 섹터 상관계수 계산

```bash
cat > /tmp/calc_sector_correlation.py << 'PYTHON'
import psycopg2
import numpy as np
from itertools import combinations

def calc_correlation():
    conn = psycopg2.connect(dbname="kisautotrade", user="postgres", host="localhost")
    cur = conn.cursor()

    # 섹터 가격 데이터 확인
    cur.execute("SELECT count(*) FROM go100_sector_price")
    cnt = cur.fetchone()[0]
    if cnt < 100:
        print(f"섹터 가격 데이터 {cnt}건 — 부족. 블록 3 완료 후 재실행 필요.")
        cur.close()
        conn.close()
        return

    # 섹터별 일간 수익률 가져오기
    cur.execute("""
        SELECT sector_name, date, avg_change_pct
        FROM go100_sector_price
        WHERE avg_change_pct IS NOT NULL
        ORDER BY sector_name, date
    """)

    from collections import defaultdict
    sector_returns = defaultdict(dict)
    for sector, date, pct in cur.fetchall():
        sector_returns[sector][date] = float(pct)

    sectors = sorted(sector_returns.keys())
    print(f"섹터 {len(sectors)}개 상관계수 계산...")

    # 기간별 계산
    for period, days in [('1m', 22), ('3m', 66), ('6m', 132), ('1y', 252)]:
        total = 0
        for sa, sb in combinations(sectors, 2):
            dates_a = sorted(sector_returns[sa].keys())[-days:]
            dates_b = sorted(sector_returns[sb].keys())[-days:]
            common = sorted(set(dates_a) & set(dates_b))

            if len(common) < 10:
                continue

            vals_a = [sector_returns[sa][d] for d in common]
            vals_b = [sector_returns[sb][d] for d in common]

            if np.std(vals_a) == 0 or np.std(vals_b) == 0:
                continue

            corr = np.corrcoef(vals_a, vals_b)[0][1]

            try:
                cur.execute("""
                    INSERT INTO go100_sector_correlation (sector_a, sector_b, period, correlation)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (sector_a, sector_b, period) DO UPDATE SET
                        correlation = EXCLUDED.correlation,
                        calculated_at = NOW()
                """, (sa, sb, period, round(float(corr), 4)))
                total += 1
            except:
                conn.rollback()

        conn.commit()
        print(f"  {period}: {total}건")

    cur.close()
    conn.close()

if __name__ == "__main__":
    print("=== 섹터 상관계수 계산 ===")
    calc_correlation()
PYTHON

cd /root/kis-autotrade-v4 && source venv/bin/activate
python /tmp/calc_sector_correlation.py
```

---

### 블록 10: 최종 종합 보고

```bash
sudo -u postgres psql -d kisautotrade <<'SQL'

SELECT '=== 전체 데이터 자산 현황 ===' as header;

-- 기존 데이터
SELECT '01_ohlcv_daily' as tbl, count(*) as rows, count(DISTINCT stock_code) as stocks FROM ohlcv_daily
UNION ALL SELECT '02_v4_ohlcv_minute', count(*), count(DISTINCT stock_code) FROM v4_ohlcv_minute
UNION ALL SELECT '03_v4_investor_daily', count(*), count(DISTINCT stock_code) FROM v4_investor_daily
UNION ALL SELECT '04_stock_fundamentals', count(*), count(DISTINCT stock_code) FROM stock_fundamentals
UNION ALL SELECT '05_go100_global_market', count(*), 0 FROM go100_global_market
UNION ALL SELECT '06_v4_sector_stock_mapping', count(*), count(DISTINCT stock_code) FROM v4_sector_stock_mapping
UNION ALL SELECT '07_go100_delisted_stocks', count(*), count(DISTINCT stock_code) FROM go100_delisted_stocks
UNION ALL SELECT '08_go100_delisted_ohlcv', count(*), count(DISTINCT stock_code) FROM go100_delisted_ohlcv
UNION ALL SELECT '09_go100_news_items', count(*), 0 FROM go100_news_items
UNION ALL SELECT '10_go100_strategy_cards', count(*), 0 FROM go100_strategy_cards
UNION ALL SELECT '11_go100_backtest_runs', count(*), 0 FROM go100_backtest_runs

-- 신규 생성 데이터
UNION ALL SELECT '12_go100_overnight_gap', count(*), count(DISTINCT stock_code) FROM go100_overnight_gap
UNION ALL SELECT '13_go100_sector_price', count(*), count(DISTINCT sector_name) FROM go100_sector_price
UNION ALL SELECT '14_go100_sector_correlation', count(*), 0 FROM go100_sector_correlation
UNION ALL SELECT '15_go100_cross_market_signals', count(*), 0 FROM go100_cross_market_signals
UNION ALL SELECT '16_go100_signal_performance', count(*), 0 FROM go100_signal_performance
UNION ALL SELECT '17_go100_experience_log', count(*), 0 FROM go100_experience_log
UNION ALL SELECT '18_go100_gap_analysis', count(*), 0 FROM go100_gap_analysis
UNION ALL SELECT '19_go100_calibration_params', count(*), 0 FROM go100_calibration_params
UNION ALL SELECT '20_go100_trading_cost_params', count(*), 0 FROM go100_trading_cost_params
UNION ALL SELECT '21_go100_orderbook_daily_stats', count(*), 0 FROM go100_orderbook_daily_stats
UNION ALL SELECT '22_go100_tick_daily_stats', count(*), 0 FROM go100_tick_daily_stats
UNION ALL SELECT '23_go100_fundamentals_pit', count(*), count(DISTINCT stock_code) FROM go100_fundamentals_pit
ORDER BY tbl;

-- 디스크
SQL

df -h /data /

echo ""
echo "=== 전체 데이터 수집 완료 ==="
echo ""
echo "보고서를 /root/project-docs/go100/reports/CUR-GO100-FULL-DATA-COLLECTION-20260226.md 로 작성하고"
echo "git add, commit (메시지: 'data(go100): V3.0 전체 데이터 인프라 구축 완료'), push 하라."
```

---

## 주의사항

- 블록 0을 반드시 먼저 실행하여 현재 상태 파악
- 이미 존재하는 테이블/데이터는 ON CONFLICT DO NOTHING 또는 IF NOT EXISTS로 스킵
- Materialized View(블록 2)는 ohlcv_daily의 date 컬럼이 varchar(8)이므로 JOIN 조건 주의
- 블록 3의 섹터 가격 INSERT가 느릴 수 있음 (수백만 행 JOIN) — 타임아웃 시 날짜 범위 축소
- 블록 8 PIT 수집: DART_API_KEY 환경변수 있으면 DART 사용, 없으면 pykrx fallback
- 블록 9는 블록 3이 완료된 후에만 의미 있음
- 각 블록 에러 시 해당 블록만 스킵하고 다음 진행
- 전체 완료 후 블록 10 보고서 반드시 작성
- 기존 테이블 스키마와 컬럼명이 다르면 적절히 수정하여 실행하라
