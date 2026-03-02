작업 ID: DESK2-BT-DEEP-DIAGNOSIS-001
우선순위: P0
선행: DESK2-BT-STRATEGY-FIX-001 (수정 후 20건, -227,135원)
목적: 수정 후 20건 거래 + 발굴 데이터를 직접 조회·분석하여 정밀 진단 보고서 작성
주의: 이 작업은 코드 수정 없음. 순수 분석·조회만 수행.

═══════════════════════════════════════════════════════════
절대 규칙
═══════════════════════════════════════════════════════════
1. 코드 수정 없음 (순수 분석만)
2. go100_* 테이블 SELECT만
3. v4_bt_* 외 테이블 INSERT/UPDATE/DELETE 금지
═══════════════════════════════════════════════════════════

환경:
- 서버: root@211.188.51.113
- DB: localhost:5432/kisautotrade (kis_admin)
- 가상환경: source /root/kis-autotrade-v4/.venv/bin/activate
- PYTHONPATH: /root/kis-autotrade-v4:/root/kis-autotrade-v4/backend

═══════════════════════════════════════════════════════════
SECTION 1: TARGET_PROFIT 손실 거래 4건 정밀 분석
═══════════════════════════════════════════════════════════

수정 후 20건 중 exit_reason=TARGET_PROFIT이면서 pnl<0인 거래 4건:
- #5: 319660 GOLF_REVERSAL 02-19 entry=62762.70 exit=62662.28 pnl=-0.35%
- #9: 272210 GOLF_REVERSAL 02-20 entry=115415.30 exit=115526.86 pnl=-0.10%
- #10: 458870 GOLF_REVERSAL 02-20 entry=149349.20 exit=149260.59 pnl=-0.25%
- #14: 403870 DELTA_VWAP 02-24 entry=41441.40 exit=41363.91 pnl=-0.38%

각 거래에 대해:

(a) 해당 전략의 target_price 계산 로직을 코드에서 확인하고 기록
    - GOLF_REVERSAL: target = bb_middle (볼린저 중간선)
    - DELTA_VWAP: target = current + (current - vwap) × 2

(b) 진입 시점의 실제 지표값 확인 (가능하면 로그에서, 없으면 분봉으로 추정)
    - entry 시점의 vwap, bb_middle, bb_lower, rsi, current_price

(c) target_price를 역산:
    - 만약 target_price < entry_price라면 목표가 설정 오류 확정

(d) 분봉 조회로 진입~청산 구간의 실제 가격 흐름 확인:

각 종목에 대해 실행:
psql -U kis_admin -d kisautotrade -c "
SELECT bar_datetime, open, high, low, close, volume
FROM v4_ohlcv_minute
WHERE stock_code = '{종목코드}'
  AND trade_date = '{날짜}'
ORDER BY bar_datetime;
" > /tmp/diag_{종목코드}_{날짜}.txt

진입 시점 전후 10봉 + 청산 시점 전후 10봉을 보고서에 기록.

(e) 결론: target_price < entry_price 버그인지, 슬리피지로 인한 것인지, 
    또는 다른 원인인지 판정.

═══════════════════════════════════════════════════════════
SECTION 2: C1~C7 발굴 비활성 원인 진단
═══════════════════════════════════════════════════════════

4일간 GOLF_REVERSAL(C7)이 85%를 차지. C1~C6는 거의 비활성.
각 조건이 왜 발굴되지 않는지 gate별로 진단한다.

--- STEP 2-1: 각 C 조건의 gate 통과 현황 확인 ---

4일 각각(02-19, 02-20, 02-24, 02-25)에 대해 아래 파이썬 스크립트를 실행:

cat << 'PYEOF' > /tmp/discovery_diagnosis.py
import sys
import psycopg2
from datetime import datetime, timedelta

DB = "dbname=kisautotrade user=kis_admin host=localhost"
conn = psycopg2.connect(DB)
cur = conn.cursor()

dates = ['2026-02-19', '2026-02-20', '2026-02-24', '2026-02-25']

for d in dates:
    print(f"\n{'='*60}")
    print(f"날짜: {d}")
    print(f"{'='*60}")

    # 시장 레짐
    cur.execute("""
        SELECT regime FROM v4_market_regime_daily WHERE trade_date = %s
    """, (d,))
    regime_row = cur.fetchone()
    regime = regime_row[0] if regime_row else 'UNKNOWN'
    print(f"시장 레짐: {regime}")

    # KOSPI 등락률
    cur.execute("""
        SELECT close FROM index_daily
        WHERE index_code = '0001' AND trade_date <= %s
        ORDER BY trade_date DESC LIMIT 2
    """, (d,))
    idx_rows = cur.fetchall()
    if len(idx_rows) == 2:
        kospi_chg = (idx_rows[0][0] - idx_rows[1][0]) / idx_rows[1][0] * 100
        print(f"KOSPI 등락률: {kospi_chg:.2f}%")
    else:
        kospi_chg = 0
        print(f"KOSPI 등락률: 데이터 부족")

    # 분봉 종목 수
    cur.execute("""
        SELECT COUNT(DISTINCT stock_code) FROM v4_ohlcv_minute
        WHERE trade_date = %s
    """, (d,))
    stock_cnt = cur.fetchone()[0]
    print(f"분봉 보유 종목 수: {stock_cnt}")

    # C1 갭급등 진단: 시가 vs 전일종가 갭 ≥ 3% 종목 수
    cur.execute("""
        WITH first_bar AS (
            SELECT stock_code, open AS open_price
            FROM v4_ohlcv_minute
            WHERE trade_date = %s
              AND bar_datetime::time BETWEEN '09:00' AND '09:05'
        ),
        prev_close AS (
            SELECT stock_code, close AS prev_close
            FROM ohlcv_daily
            WHERE trade_date = (
                SELECT MAX(trade_date) FROM ohlcv_daily WHERE trade_date < %s
            )
        )
        SELECT COUNT(*) AS gap_up_cnt,
               COUNT(*) FILTER (WHERE (fb.open_price - pc.prev_close) / pc.prev_close * 100 >= 3
                                  AND (fb.open_price - pc.prev_close) / pc.prev_close * 100 <= 15) AS c1_candidates
        FROM first_bar fb
        JOIN prev_close pc ON fb.stock_code = pc.stock_code
        WHERE pc.prev_close > 0
    """, (d, d))
    row = cur.fetchone()
    print(f"C1 갭급등: 전체 갭 종목={row[0]}, 3~15% 갭={row[1]}")

    # C2 장초반강세 진단: 09:00~09:30 사이 +1.5% 이상 종목
    cur.execute("""
        WITH morning AS (
            SELECT stock_code,
                   MIN(open) AS first_open,
                   MAX(high) AS max_high,
                   SUM(volume) AS total_vol
            FROM v4_ohlcv_minute
            WHERE trade_date = %s
              AND bar_datetime::time BETWEEN '09:00' AND '09:30'
            GROUP BY stock_code
        )
        SELECT COUNT(*) FILTER (
            WHERE (max_high - first_open) / NULLIF(first_open, 0) * 100 >= 1.5
        ) AS c2_candidates
        FROM morning
    """, (d,))
    c2 = cur.fetchone()[0]
    print(f"C2 장초반강세: +1.5% 이상 종목={c2}")

    # C4 장중급등 진단: 10분간 +2% 이상 급등 종목
    cur.execute("""
        WITH bars AS (
            SELECT stock_code, bar_datetime, close, volume,
                   LAG(close, 10) OVER (PARTITION BY stock_code ORDER BY bar_datetime) AS close_10ago
            FROM v4_ohlcv_minute
            WHERE trade_date = %s
              AND bar_datetime::time BETWEEN '09:30' AND '14:30'
        )
        SELECT COUNT(DISTINCT stock_code) AS c4_candidates
        FROM bars
        WHERE close_10ago > 0
          AND (close - close_10ago) / close_10ago * 100 >= 2.0
    """, (d,))
    c4 = cur.fetchone()[0]
    print(f"C4 장중급등: 10분 +2% 급등 종목={c4}")

    # C5 급등후조정: 당일 고가 ≥ +5%, 현재 고가 대비 -1.5% 이상 조정
    cur.execute("""
        WITH day_stats AS (
            SELECT stock_code,
                   MIN(open) FILTER (WHERE bar_datetime::time = '09:00:00') AS day_open,
                   MAX(high) AS day_high,
                   (array_agg(close ORDER BY bar_datetime DESC))[1] AS last_close
            FROM v4_ohlcv_minute
            WHERE trade_date = %s
              AND bar_datetime::time BETWEEN '10:00' AND '14:30'
            GROUP BY stock_code
        )
        SELECT COUNT(*) AS c5_candidates
        FROM day_stats
        WHERE day_open > 0
          AND (day_high - day_open) / day_open * 100 >= 5
          AND (day_high - last_close) / day_high * 100 >= 1.5
    """, (d,))
    c5 = cur.fetchone()[0]
    print(f"C5 급등후조정: 후보 종목={c5}")

    # C7 과매도: 고가 대비 -3.5% + 시장 하락
    cur.execute("""
        WITH day_stats AS (
            SELECT stock_code,
                   MAX(high) AS day_high,
                   (array_agg(close ORDER BY bar_datetime DESC))[1] AS last_close
            FROM v4_ohlcv_minute
            WHERE trade_date = %s
              AND bar_datetime::time BETWEEN '10:00' AND '15:00'
            GROUP BY stock_code
        ),
        mkt AS (
            SELECT sf.stock_code, sf.market_cap
            FROM stock_fundamentals sf
        )
        SELECT COUNT(*) AS c7_raw,
               COUNT(*) FILTER (
                   WHERE m.market_cap >= 500000000000
                   AND (ds.day_high - ds.last_close) / NULLIF(ds.day_high,0) * 100 >= 3.5
               ) AS c7_with_gate
        FROM day_stats ds
        LEFT JOIN mkt m ON ds.stock_code = m.stock_code
        WHERE ds.day_high > 0
          AND (ds.day_high - ds.last_close) / ds.day_high * 100 >= 3.0
    """, (d,))
    c7_row = cur.fetchone()
    print(f"C7 과매도: raw(-3%)={c7_row[0]}, gate적용(-3.5%+시총5천억)={c7_row[1]}")

conn.close()
PYEOF

python3 /tmp/discovery_diagnosis.py 2>&1 | tee /tmp/discovery_diagnosis_result.txt

--- STEP 2-2: C3 VI발동 데이터 확인 ---

psql -U kis_admin -d kisautotrade -c "
SELECT trade_date, COUNT(*) AS vi_count
FROM v4_vi_occurrences
WHERE trade_date IN ('2026-02-19','2026-02-20','2026-02-24','2026-02-25')
GROUP BY trade_date
ORDER BY trade_date;
"
→ 테이블 없으면 "v4_vi_occurrences 없음" 기록.
   VI 데이터가 없으면 C3는 구조적으로 비활성.

--- STEP 2-3: C6 업종동반 데이터 확인 ---

psql -U kis_admin -d kisautotrade -c "
SELECT COUNT(DISTINCT sector_code) AS sectors,
       COUNT(*) AS total_mappings
FROM v4_stock_sector;
"

psql -U kis_admin -d kisautotrade -c "
SELECT sector, COUNT(*) AS cnt
FROM stock_universe
WHERE sector IS NOT NULL AND sector != ''
GROUP BY sector
ORDER BY cnt DESC
LIMIT 20;
"
→ 섹터 매핑 현황. 매핑이 부족하면 C6 작동 불가.

═══════════════════════════════════════════════════════════
SECTION 3: 수정 후 20건 거래의 청산 후 주가 변동 확인
═══════════════════════════════════════════════════════════

각 거래에 대해 청산 이후 주가를 확인하여 "너무 일찍 나갔는가"를 판단.

cat << 'PYEOF' > /tmp/post_exit_analysis.py
import psycopg2

DB = "dbname=kisautotrade user=kis_admin host=localhost"
conn = psycopg2.connect(DB)
cur = conn.cursor()

trades = [
    ('2026-02-19', '272290', 36479.98, 360),
    ('2026-02-19', '322000', 86614.10, 360),
    ('2026-02-19', '348340', 80789.13, 1260),
    ('2026-02-19', '319400', 26876.85, 600),
    ('2026-02-19', '319660', 62662.28, 120),
    ('2026-02-20', '440110', 50049.90, 1800),
    ('2026-02-20', '295310', 84433.88, 1620),
    ('2026-02-20', '322000', 88663.75, 1380),
    ('2026-02-20', '272210', 115526.86, 60),
    ('2026-02-20', '458870', 149260.59, 60),
    ('2026-02-24', '440110', 52160.29, 180),
    ('2026-02-24', '403870', 41072.64, 120),
    ('2026-02-24', '347700', 43536.96, 3420),
    ('2026-02-24', '403870', 41363.91, 60),
    ('2026-02-24', '491000', 90453.91, 900),
    ('2026-02-25', '000720', 153369.85, 780),
    ('2026-02-25', '319400', 35428.54, 300),
    ('2026-02-25', '032820', 17077.01, 300),
    ('2026-02-25', '130660', 25524.45, 780),
    ('2026-02-25', '241520', 17494.49, 780),
]

print(f"{'#':>2} | {'date':10} | {'code':6} | {'exit_price':>10} | {'+30m_high':>10} | {'+60m_high':>10} | {'close':>10} | {'missed%':>8}")
print("-" * 90)

for i, (d, code, exit_px, hold_sec) in enumerate(trades, 1):
    # 진입 시점 추정 (09:00 + hold_sec 기준은 부정확하므로 exit 시점 이후를 봄)
    # 청산 이후 30분, 60분, 장마감(15:20) 고가·종가
    cur.execute("""
        WITH all_bars AS (
            SELECT bar_datetime, high, close,
                   ROW_NUMBER() OVER (ORDER BY bar_datetime) AS rn
            FROM v4_ohlcv_minute
            WHERE stock_code = %s AND trade_date = %s
            ORDER BY bar_datetime
        ),
        exit_bar AS (
            SELECT MIN(rn) AS exit_rn, MIN(bar_datetime) AS exit_time
            FROM all_bars
            WHERE close <= %s OR high >= %s
            -- 대략적 exit 시점 추정
        )
        SELECT
            MAX(high) FILTER (WHERE rn BETWEEN eb.exit_rn AND eb.exit_rn + 30) AS high_30m,
            MAX(high) FILTER (WHERE rn BETWEEN eb.exit_rn AND eb.exit_rn + 60) AS high_60m,
            (array_agg(close ORDER BY bar_datetime DESC))[1] AS day_close
        FROM all_bars ab, exit_bar eb
    """, (code, d, exit_px * 0.999, exit_px * 1.001))
    
    row = cur.fetchone()
    if row and row[0]:
        h30 = row[0]
        h60 = row[1] or row[0]
        dc = row[2] or exit_px
        missed = max(0, (max(h30, h60, dc) - exit_px) / exit_px * 100)
        print(f"{i:2} | {d} | {code} | {exit_px:10.2f} | {h30:10.2f} | {h60:10.2f} | {dc:10.2f} | {missed:7.2f}%")
    else:
        # fallback: 단순 장마감 종가
        cur.execute("""
            SELECT MAX(high) AS day_high,
                   (array_agg(close ORDER BY bar_datetime DESC))[1] AS day_close
            FROM v4_ohlcv_minute
            WHERE stock_code = %s AND trade_date = %s
        """, (code, d))
        row2 = cur.fetchone()
        if row2:
            dh = row2[0] or exit_px
            dc = row2[1] or exit_px
            missed = max(0, (max(dh, dc) - exit_px) / exit_px * 100)
            print(f"{i:2} | {d} | {code} | {exit_px:10.2f} | {'N/A':>10} | {'N/A':>10} | {dc:10.2f} | {missed:7.2f}%")
        else:
            print(f"{i:2} | {d} | {code} | {exit_px:10.2f} | {'NO DATA':>10} | {'NO DATA':>10} | {'NO DATA':>10} | {'N/A':>8}")

conn.close()
PYEOF

python3 /tmp/post_exit_analysis.py 2>&1 | tee /tmp/post_exit_result.txt

═══════════════════════════════════════════════════════════
SECTION 4: desk2_config.yaml 현재 전략 파라미터 전체 덤프
═══════════════════════════════════════════════════════════

cat /root/kis-autotrade-v4/backend/app/services/trading/desk2/desk2_config.yaml

→ 전체 내용을 보고서에 포함. 특히 strategy_params, exit_strategy, 
  discovery_redesign 섹션.

═══════════════════════════════════════════════════════════
SECTION 5: 발굴 코드의 실제 gate 조건 확인
═══════════════════════════════════════════════════════════

각 C 조건 파일에서 실제 gate 체크 부분을 추출한다.

for f in /root/kis-autotrade-v4/backend/app/services/trading/desk2/layer1_discovery/c*.py; do
    echo "========== $(basename $f) =========="
    grep -n -A5 "gate\|MIN_\|MAX_\|MARKET_CAP\|market_cap\|RVOL\|rvol\|drop\|surge\|gap\|RSI\|rsi" "$f" | head -60
    echo ""
done 2>&1 | tee /tmp/discovery_gates.txt

═══════════════════════════════════════════════════════════
SECTION 6: backtest_runner.py의 Phase D 청산 로직 확인
═══════════════════════════════════════════════════════════

grep -n -A30 "Phase D\|phase_d\|stop_loss\|target_profit\|first_target\|trailing\|TIMEOUT\|exit_reason" \
  /root/kis-autotrade-v4/backend/app/services/trading/desk2/backtest/backtest_runner.py \
  | head -200 > /tmp/phase_d_logic.txt

cat /tmp/phase_d_logic.txt

═══════════════════════════════════════════════════════════
SECTION 7: 보고서 작성
═══════════════════════════════════════════════════════════

파일명: report/v41/DESK2-BT-DEEP-DIAGNOSIS-001-20260227.md

보고서 구조:

# DESK2-BT-DEEP-DIAGNOSIS-001 — 정밀 진단 보고서

## 1. TARGET_PROFIT 손실 거래 분석
4건 각각: target_price 역산, 분봉 데이터, 버그 여부 판정.

## 2. C1~C7 발굴 비활성 원인
날짜별:
- 시장 레짐, KOSPI 등락률
- C1: 갭 3~15% 후보 수 + RVOL 미달? 시총 미달? 시간대 불일치?
- C2: +1.5% 후보 수 + 거래대금 top100 미달?
- C3: VI 데이터 존재 여부
- C4: 10분 +2% 후보 수 + 시총/거래량 gate
- C5: 급등후조정 후보 수 + ADX 미달?
- C6: 섹터 매핑 현황 + 대장주 +4% 조건
- C7: raw 후보 vs gate 적용 후 후보

각 조건별 "발굴 안 되는 핵심 원인" 1줄 결론.

## 3. 청산 후 주가 변동 (기회손실 분석)
20건 테이블: exit_price, +30분 고가, +60분 고가, 장마감, 기회손실%.
"너무 일찍 나간" 거래 vs "적절한 타이밍" 거래 분류.

## 4. desk2_config.yaml 현재 파라미터
전략별 파라미터 전체 표.

## 5. 발굴 gate 조건 코드 요약
C1~C7 각각의 실제 gate 조건 표.

## 6. Phase D 청산 로직 요약
2분할 매도 포함 현재 청산 흐름 정리.

## 7. 종합 진단 및 개선 의견
- 문제별 원인·영향·제안 정리

═══════════════════════════════════════════════════════════
문서 레포 푸시
═══════════════════════════════════════════════════════════

cp report/v41/DESK2-BT-DEEP-DIAGNOSIS-001-20260227.md \
   /root/project-docs/kis-autotrade-v4/reports/

cd /root/project-docs
git add kis-autotrade-v4/reports/DESK2-BT-DEEP-DIAGNOSIS-001-20260227.md
git commit -m "docs: DESK2 정밀 진단 (발굴 비활성 원인 + 청산 분석 + 기회손실)

DESK2-BT-DEEP-DIAGNOSIS-001
- TARGET_PROFIT 손실 4건 원인 분석
- C1~C7 gate별 발굴 비활성 원인 진단
- 20건 청산 후 주가 변동 (기회손실 분석)
- config 파라미터 + 발굴 gate + Phase D 로직 덤프

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
git push origin master

curl -s -o /dev/null -w "%{http_code}" \
  https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/DESK2-BT-DEEP-DIAGNOSIS-001-20260227.md
→ 200 확인. URL 보고.작업 ID: DESK2-BT-DEEP-DIAGNOSIS-001
우선순위: P0
선행: DESK2-BT-STRATEGY-FIX-001 (수정 후 20건, -227,135원)
목적: 수정 후 20건 거래 + 발굴 데이터를 직접 조회·분석하여 정밀 진단 보고서 작성
주의: 이 작업은 코드 수정 없음. 순수 분석·조회만 수행.

═══════════════════════════════════════════════════════════
절대 규칙
═══════════════════════════════════════════════════════════
1. 코드 수정 없음 (순수 분석만)
2. go100_* 테이블 SELECT만
3. v4_bt_* 외 테이블 INSERT/UPDATE/DELETE 금지
═══════════════════════════════════════════════════════════

환경:
- 서버: root@211.188.51.113
- DB: localhost:5432/kisautotrade (kis_admin)
- 가상환경: source /root/kis-autotrade-v4/.venv/bin/activate
- PYTHONPATH: /root/kis-autotrade-v4:/root/kis-autotrade-v4/backend

═══════════════════════════════════════════════════════════
SECTION 1: TARGET_PROFIT 손실 거래 4건 정밀 분석
═══════════════════════════════════════════════════════════

수정 후 20건 중 exit_reason=TARGET_PROFIT이면서 pnl<0인 거래 4건:
- #5: 319660 GOLF_REVERSAL 02-19 entry=62762.70 exit=62662.28 pnl=-0.35%
- #9: 272210 GOLF_REVERSAL 02-20 entry=115415.30 exit=115526.86 pnl=-0.10%
- #10: 458870 GOLF_REVERSAL 02-20 entry=149349.20 exit=149260.59 pnl=-0.25%
- #14: 403870 DELTA_VWAP 02-24 entry=41441.40 exit=41363.91 pnl=-0.38%

각 거래에 대해:

(a) 해당 전략의 target_price 계산 로직을 코드에서 확인하고 기록
    - GOLF_REVERSAL: target = bb_middle (볼린저 중간선)
    - DELTA_VWAP: target = current + (current - vwap) × 2

(b) 진입 시점의 실제 지표값 확인 (가능하면 로그에서, 없으면 분봉으로 추정)
    - entry 시점의 vwap, bb_middle, bb_lower, rsi, current_price

(c) target_price를 역산:
    - 만약 target_price < entry_price라면 목표가 설정 오류 확정

(d) 분봉 조회로 진입~청산 구간의 실제 가격 흐름 확인:

각 종목에 대해 실행:
psql -U kis_admin -d kisautotrade -c "
SELECT bar_datetime, open, high, low, close, volume
FROM v4_ohlcv_minute
WHERE stock_code = '{종목코드}'
  AND trade_date = '{날짜}'
ORDER BY bar_datetime;
" > /tmp/diag_{종목코드}_{날짜}.txt

진입 시점 전후 10봉 + 청산 시점 전후 10봉을 보고서에 기록.

(e) 결론: target_price < entry_price 버그인지, 슬리피지로 인한 것인지, 
    또는 다른 원인인지 판정.

═══════════════════════════════════════════════════════════
SECTION 2: C1~C7 발굴 비활성 원인 진단
═══════════════════════════════════════════════════════════

4일간 GOLF_REVERSAL(C7)이 85%를 차지. C1~C6는 거의 비활성.
각 조건이 왜 발굴되지 않는지 gate별로 진단한다.

--- STEP 2-1: 각 C 조건의 gate 통과 현황 확인 ---

4일 각각(02-19, 02-20, 02-24, 02-25)에 대해 아래 파이썬 스크립트를 실행:

cat << 'PYEOF' > /tmp/discovery_diagnosis.py
import sys
import psycopg2
from datetime import datetime, timedelta

DB = "dbname=kisautotrade user=kis_admin host=localhost"
conn = psycopg2.connect(DB)
cur = conn.cursor()

dates = ['2026-02-19', '2026-02-20', '2026-02-24', '2026-02-25']

for d in dates:
    print(f"\n{'='*60}")
    print(f"날짜: {d}")
    print(f"{'='*60}")

    # 시장 레짐
    cur.execute("""
        SELECT regime FROM v4_market_regime_daily WHERE trade_date = %s
    """, (d,))
    regime_row = cur.fetchone()
    regime = regime_row[0] if regime_row else 'UNKNOWN'
    print(f"시장 레짐: {regime}")

    # KOSPI 등락률
    cur.execute("""
        SELECT close FROM index_daily
        WHERE index_code = '0001' AND trade_date <= %s
        ORDER BY trade_date DESC LIMIT 2
    """, (d,))
    idx_rows = cur.fetchall()
    if len(idx_rows) == 2:
        kospi_chg = (idx_rows[0][0] - idx_rows[1][0]) / idx_rows[1][0] * 100
        print(f"KOSPI 등락률: {kospi_chg:.2f}%")
    else:
        kospi_chg = 0
        print(f"KOSPI 등락률: 데이터 부족")

    # 분봉 종목 수
    cur.execute("""
        SELECT COUNT(DISTINCT stock_code) FROM v4_ohlcv_minute
        WHERE trade_date = %s
    """, (d,))
    stock_cnt = cur.fetchone()[0]
    print(f"분봉 보유 종목 수: {stock_cnt}")

    # C1 갭급등 진단: 시가 vs 전일종가 갭 ≥ 3% 종목 수
    cur.execute("""
        WITH first_bar AS (
            SELECT stock_code, open AS open_price
            FROM v4_ohlcv_minute
            WHERE trade_date = %s
              AND bar_datetime::time BETWEEN '09:00' AND '09:05'
        ),
        prev_close AS (
            SELECT stock_code, close AS prev_close
            FROM ohlcv_daily
            WHERE trade_date = (
                SELECT MAX(trade_date) FROM ohlcv_daily WHERE trade_date < %s
            )
        )
        SELECT COUNT(*) AS gap_up_cnt,
               COUNT(*) FILTER (WHERE (fb.open_price - pc.prev_close) / pc.prev_close * 100 >= 3
                                  AND (fb.open_price - pc.prev_close) / pc.prev_close * 100 <= 15) AS c1_candidates
        FROM first_bar fb
        JOIN prev_close pc ON fb.stock_code = pc.stock_code
        WHERE pc.prev_close > 0
    """, (d, d))
    row = cur.fetchone()
    print(f"C1 갭급등: 전체 갭 종목={row[0]}, 3~15% 갭={row[1]}")

    # C2 장초반강세 진단: 09:00~09:30 사이 +1.5% 이상 종목
    cur.execute("""
        WITH morning AS (
            SELECT stock_code,
                   MIN(open) AS first_open,
                   MAX(high) AS max_high,
                   SUM(volume) AS total_vol
            FROM v4_ohlcv_minute
            WHERE trade_date = %s
              AND bar_datetime::time BETWEEN '09:00' AND '09:30'
            GROUP BY stock_code
        )
        SELECT COUNT(*) FILTER (
            WHERE (max_high - first_open) / NULLIF(first_open, 0) * 100 >= 1.5
        ) AS c2_candidates
        FROM morning
    """, (d,))
    c2 = cur.fetchone()[0]
    print(f"C2 장초반강세: +1.5% 이상 종목={c2}")

    # C4 장중급등 진단: 10분간 +2% 이상 급등 종목
    cur.execute("""
        WITH bars AS (
            SELECT stock_code, bar_datetime, close, volume,
                   LAG(close, 10) OVER (PARTITION BY stock_code ORDER BY bar_datetime) AS close_10ago
            FROM v4_ohlcv_minute
            WHERE trade_date = %s
              AND bar_datetime::time BETWEEN '09:30' AND '14:30'
        )
        SELECT COUNT(DISTINCT stock_code) AS c4_candidates
        FROM bars
        WHERE close_10ago > 0
          AND (close - close_10ago) / close_10ago * 100 >= 2.0
    """, (d,))
    c4 = cur.fetchone()[0]
    print(f"C4 장중급등: 10분 +2% 급등 종목={c4}")

    # C5 급등후조정: 당일 고가 ≥ +5%, 현재 고가 대비 -1.5% 이상 조정
    cur.execute("""
        WITH day_stats AS (
            SELECT stock_code,
                   MIN(open) FILTER (WHERE bar_datetime::time = '09:00:00') AS day_open,
                   MAX(high) AS day_high,
                   (array_agg(close ORDER BY bar_datetime DESC))[1] AS last_close
            FROM v4_ohlcv_minute
            WHERE trade_date = %s
              AND bar_datetime::time BETWEEN '10:00' AND '14:30'
            GROUP BY stock_code
        )
        SELECT COUNT(*) AS c5_candidates
        FROM day_stats
        WHERE day_open > 0
          AND (day_high - day_open) / day_open * 100 >= 5
          AND (day_high - last_close) / day_high * 100 >= 1.5
    """, (d,))
    c5 = cur.fetchone()[0]
    print(f"C5 급등후조정: 후보 종목={c5}")

    # C7 과매도: 고가 대비 -3.5% + 시장 하락
    cur.execute("""
        WITH day_stats AS (
            SELECT stock_code,
                   MAX(high) AS day_high,
                   (array_agg(close ORDER BY bar_datetime DESC))[1] AS last_close
            FROM v4_ohlcv_minute
            WHERE trade_date = %s
              AND bar_datetime::time BETWEEN '10:00' AND '15:00'
            GROUP BY stock_code
        ),
        mkt AS (
            SELECT sf.stock_code, sf.market_cap
            FROM stock_fundamentals sf
        )
        SELECT COUNT(*) AS c7_raw,
               COUNT(*) FILTER (
                   WHERE m.market_cap >= 500000000000
                   AND (ds.day_high - ds.last_close) / NULLIF(ds.day_high,0) * 100 >= 3.5
               ) AS c7_with_gate
        FROM day_stats ds
        LEFT JOIN mkt m ON ds.stock_code = m.stock_code
        WHERE ds.day_high > 0
          AND (ds.day_high - ds.last_close) / ds.day_high * 100 >= 3.0
    """, (d,))
    c7_row = cur.fetchone()
    print(f"C7 과매도: raw(-3%)={c7_row[0]}, gate적용(-3.5%+시총5천억)={c7_row[1]}")

conn.close()
PYEOF

python3 /tmp/discovery_diagnosis.py 2>&1 | tee /tmp/discovery_diagnosis_result.txt

--- STEP 2-2: C3 VI발동 데이터 확인 ---

psql -U kis_admin -d kisautotrade -c "
SELECT trade_date, COUNT(*) AS vi_count
FROM v4_vi_occurrences
WHERE trade_date IN ('2026-02-19','2026-02-20','2026-02-24','2026-02-25')
GROUP BY trade_date
ORDER BY trade_date;
"
→ 테이블 없으면 "v4_vi_occurrences 없음" 기록.
   VI 데이터가 없으면 C3는 구조적으로 비활성.

--- STEP 2-3: C6 업종동반 데이터 확인 ---

psql -U kis_admin -d kisautotrade -c "
SELECT COUNT(DISTINCT sector_code) AS sectors,
       COUNT(*) AS total_mappings
FROM v4_stock_sector;
"

psql -U kis_admin -d kisautotrade -c "
SELECT sector, COUNT(*) AS cnt
FROM stock_universe
WHERE sector IS NOT NULL AND sector != ''
GROUP BY sector
ORDER BY cnt DESC
LIMIT 20;
"
→ 섹터 매핑 현황. 매핑이 부족하면 C6 작동 불가.

═══════════════════════════════════════════════════════════
SECTION 3: 수정 후 20건 거래의 청산 후 주가 변동 확인
═══════════════════════════════════════════════════════════

각 거래에 대해 청산 이후 주가를 확인하여 "너무 일찍 나갔는가"를 판단.

cat << 'PYEOF' > /tmp/post_exit_analysis.py
import psycopg2

DB = "dbname=kisautotrade user=kis_admin host=localhost"
conn = psycopg2.connect(DB)
cur = conn.cursor()

trades = [
    ('2026-02-19', '272290', 36479.98, 360),
    ('2026-02-19', '322000', 86614.10, 360),
    ('2026-02-19', '348340', 80789.13, 1260),
    ('2026-02-19', '319400', 26876.85, 600),
    ('2026-02-19', '319660', 62662.28, 120),
    ('2026-02-20', '440110', 50049.90, 1800),
    ('2026-02-20', '295310', 84433.88, 1620),
    ('2026-02-20', '322000', 88663.75, 1380),
    ('2026-02-20', '272210', 115526.86, 60),
    ('2026-02-20', '458870', 149260.59, 60),
    ('2026-02-24', '440110', 52160.29, 180),
    ('2026-02-24', '403870', 41072.64, 120),
    ('2026-02-24', '347700', 43536.96, 3420),
    ('2026-02-24', '403870', 41363.91, 60),
    ('2026-02-24', '491000', 90453.91, 900),
    ('2026-02-25', '000720', 153369.85, 780),
    ('2026-02-25', '319400', 35428.54, 300),
    ('2026-02-25', '032820', 17077.01, 300),
    ('2026-02-25', '130660', 25524.45, 780),
    ('2026-02-25', '241520', 17494.49, 780),
]

print(f"{'#':>2} | {'date':10} | {'code':6} | {'exit_price':>10} | {'+30m_high':>10} | {'+60m_high':>10} | {'close':>10} | {'missed%':>8}")
print("-" * 90)

for i, (d, code, exit_px, hold_sec) in enumerate(trades, 1):
    # 진입 시점 추정 (09:00 + hold_sec 기준은 부정확하므로 exit 시점 이후를 봄)
    # 청산 이후 30분, 60분, 장마감(15:20) 고가·종가
    cur.execute("""
        WITH all_bars AS (
            SELECT bar_datetime, high, close,
                   ROW_NUMBER() OVER (ORDER BY bar_datetime) AS rn
            FROM v4_ohlcv_minute
            WHERE stock_code = %s AND trade_date = %s
            ORDER BY bar_datetime
        ),
        exit_bar AS (
            SELECT MIN(rn) AS exit_rn, MIN(bar_datetime) AS exit_time
            FROM all_bars
            WHERE close <= %s OR high >= %s
            -- 대략적 exit 시점 추정
        )
        SELECT
            MAX(high) FILTER (WHERE rn BETWEEN eb.exit_rn AND eb.exit_rn + 30) AS high_30m,
            MAX(high) FILTER (WHERE rn BETWEEN eb.exit_rn AND eb.exit_rn + 60) AS high_60m,
            (array_agg(close ORDER BY bar_datetime DESC))[1] AS day_close
        FROM all_bars ab, exit_bar eb
    """, (code, d, exit_px * 0.999, exit_px * 1.001))
    
    row = cur.fetchone()
    if row and row[0]:
        h30 = row[0]
        h60 = row[1] or row[0]
        dc = row[2] or exit_px
        missed = max(0, (max(h30, h60, dc) - exit_px) / exit_px * 100)
        print(f"{i:2} | {d} | {code} | {exit_px:10.2f} | {h30:10.2f} | {h60:10.2f} | {dc:10.2f} | {missed:7.2f}%")
    else:
        # fallback: 단순 장마감 종가
        cur.execute("""
            SELECT MAX(high) AS day_high,
                   (array_agg(close ORDER BY bar_datetime DESC))[1] AS day_close
            FROM v4_ohlcv_minute
            WHERE stock_code = %s AND trade_date = %s
        """, (code, d))
        row2 = cur.fetchone()
        if row2:
            dh = row2[0] or exit_px
            dc = row2[1] or exit_px
            missed = max(0, (max(dh, dc) - exit_px) / exit_px * 100)
            print(f"{i:2} | {d} | {code} | {exit_px:10.2f} | {'N/A':>10} | {'N/A':>10} | {dc:10.2f} | {missed:7.2f}%")
        else:
            print(f"{i:2} | {d} | {code} | {exit_px:10.2f} | {'NO DATA':>10} | {'NO DATA':>10} | {'NO DATA':>10} | {'N/A':>8}")

conn.close()
PYEOF

python3 /tmp/post_exit_analysis.py 2>&1 | tee /tmp/post_exit_result.txt

═══════════════════════════════════════════════════════════
SECTION 4: desk2_config.yaml 현재 전략 파라미터 전체 덤프
═══════════════════════════════════════════════════════════

cat /root/kis-autotrade-v4/backend/app/services/trading/desk2/desk2_config.yaml

→ 전체 내용을 보고서에 포함. 특히 strategy_params, exit_strategy, 
  discovery_redesign 섹션.

═══════════════════════════════════════════════════════════
SECTION 5: 발굴 코드의 실제 gate 조건 확인
═══════════════════════════════════════════════════════════

각 C 조건 파일에서 실제 gate 체크 부분을 추출한다.

for f in /root/kis-autotrade-v4/backend/app/services/trading/desk2/layer1_discovery/c*.py; do
    echo "========== $(basename $f) =========="
    grep -n -A5 "gate\|MIN_\|MAX_\|MARKET_CAP\|market_cap\|RVOL\|rvol\|drop\|surge\|gap\|RSI\|rsi" "$f" | head -60
    echo ""
done 2>&1 | tee /tmp/discovery_gates.txt

═══════════════════════════════════════════════════════════
SECTION 6: backtest_runner.py의 Phase D 청산 로직 확인
═══════════════════════════════════════════════════════════

grep -n -A30 "Phase D\|phase_d\|stop_loss\|target_profit\|first_target\|trailing\|TIMEOUT\|exit_reason" \
  /root/kis-autotrade-v4/backend/app/services/trading/desk2/backtest/backtest_runner.py \
  | head -200 > /tmp/phase_d_logic.txt

cat /tmp/phase_d_logic.txt

═══════════════════════════════════════════════════════════
SECTION 7: 보고서 작성
═══════════════════════════════════════════════════════════

파일명: report/v41/DESK2-BT-DEEP-DIAGNOSIS-001-20260227.md

보고서 구조:

# DESK2-BT-DEEP-DIAGNOSIS-001 — 정밀 진단 보고서

## 1. TARGET_PROFIT 손실 거래 분석
4건 각각: target_price 역산, 분봉 데이터, 버그 여부 판정.

## 2. C1~C7 발굴 비활성 원인
날짜별:
- 시장 레짐, KOSPI 등락률
- C1: 갭 3~15% 후보 수 + RVOL 미달? 시총 미달? 시간대 불일치?
- C2: +1.5% 후보 수 + 거래대금 top100 미달?
- C3: VI 데이터 존재 여부
- C4: 10분 +2% 후보 수 + 시총/거래량 gate
- C5: 급등후조정 후보 수 + ADX 미달?
- C6: 섹터 매핑 현황 + 대장주 +4% 조건
- C7: raw 후보 vs gate 적용 후 후보

각 조건별 "발굴 안 되는 핵심 원인" 1줄 결론.

## 3. 청산 후 주가 변동 (기회손실 분석)
20건 테이블: exit_price, +30분 고가, +60분 고가, 장마감, 기회손실%.
"너무 일찍 나간" 거래 vs "적절한 타이밍" 거래 분류.

## 4. desk2_config.yaml 현재 파라미터
전략별 파라미터 전체 표.

## 5. 발굴 gate 조건 코드 요약
C1~C7 각각의 실제 gate 조건 표.

## 6. Phase D 청산 로직 요약
2분할 매도 포함 현재 청산 흐름 정리.

## 7. 종합 진단 및 개선 의견
- 문제별 원인·영향·제안 정리

═══════════════════════════════════════════════════════════
문서 레포 푸시
═══════════════════════════════════════════════════════════

cp report/v41/DESK2-BT-DEEP-DIAGNOSIS-001-20260227.md \
   /root/project-docs/kis-autotrade-v4/reports/

cd /root/project-docs
git add kis-autotrade-v4/reports/DESK2-BT-DEEP-DIAGNOSIS-001-20260227.md
git commit -m "docs: DESK2 정밀 진단 (발굴 비활성 원인 + 청산 분석 + 기회손실)

DESK2-BT-DEEP-DIAGNOSIS-001
- TARGET_PROFIT 손실 4건 원인 분석
- C1~C7 gate별 발굴 비활성 원인 진단
- 20건 청산 후 주가 변동 (기회손실 분석)
- config 파라미터 + 발굴 gate + Phase D 로직 덤프

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
git push origin master

curl -s -o /dev/null -w "%{http_code}" \
  https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/DESK2-BT-DEEP-DIAGNOSIS-001-20260227.md
→ 200 확인. URL 보고.