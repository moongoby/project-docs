# MINUTE-BAR-VERIFY-AND-CHART-001 1분봉 확인 및 차트 전환 보고서
**작성일:** 2026-02-25
**우선순위:** P1

## 1. 분봉 데이터 확인
- **bar 간격:** 005930, 2026-02-03 기준 `trade_time`이 09:00, 09:01, 09:02, … 1분 단위로 확인됨 → **1분봉 확정**
- **일일 bar 수:** 005930·2026-02-03 `bar_count = 381` (기대 ~380 bars/일과 일치)
- **다종목 샘플:** 2026-02-03 기준 상위 10종목 모두 `bar_count = 381` → 전 종목 1분봉
- **결론:** `v4_ohlcv_minute`는 1분봉 데이터임. 5분봉 전환 불필요.

## 2. CandleResampler 수정
- **현황:** 이미 1분봉 기반 동작 (`resample(..., 1)` → 원본 반환, `resample_tf(..., '1d')` → 빈 리스트, 일봉은 ohlcv_daily 별도 조회)
- **변경 사항:** 지시서 전략별 추천 타임프레임에 맞춰 `STRATEGY_RECOMMENDED_TIMEFRAMES` 수정
  - C4_VWAP_RECOVERY: 5m, C5_PULLBACK: 5m, C6_SECTOR_LAG: 10m, C7_OVERSOLD_REBOUND: 5m 추가
  - DELTA_VWAP: 5m, ECHO_ABCD: 3m, FOXTROT_SECTOR: 10m 반영
  - C7_OVERSOLD → C7_OVERSOLD_REBOUND 매핑 유지, 하위 호환용 `C7_OVERSOLD` 별칭 유지
- **AST 검증:** 통과

## 3. bt_chart.py 수정
- **캔들 로드:** 기존 `_load_1m_bars`(v4_ohlcv_minute) + `_load_daily_bars`(ohlcv_daily) 유지, 변경 없음
- **default_timeframe:** 이미 `DEFAULT_TIMEFRAME = "1m"`, `AVAILABLE_TIMEFRAMES`에 1m 포함
- **변경 사항:**
  - `get_multi_timeframe` 기본 쿼리: `timeframes` default `"5m,30m,1d"` → `"1m,5m,1d"`
  - 전략 미매칭 시 기본 타임프레임: `["5m", "1d"]` → `["1m", "5m", "1d"]`
  - `get_strategy_compare_chart`: 캔들 로드 시 하드코드 `"5m"` → `DEFAULT_TIMEFRAME`(1m) 사용
- **전략별 추천:** `candle_resampler.STRATEGY_RECOMMENDED_TIMEFRAMES` import 사용, 위 2번 매핑과 동일
- **AST 검증:** 통과

## 4. 프론트엔드 수정
- **TimeframeSelector:** 이미 `DEFAULT_TIMEFRAME = "1m"`, `AVAILABLE_TIMEFRAMES`에 `"1m"` 포함 → 변경 없음
- **거래 차트 페이지** `app/(protected)/admin/backtest/trades/[tradeId]/page.tsx`: 초기 상태 `useState("1m")` 유지
- **발굴/일일 차트:** API 기본 1분봉 응답 사용, 페이지별 타임프레임 state 없음 → 별도 수정 없음
- **빌드:** `npm run build` 실행 결과 에러 0, 정상 완료

## 5. 검증 결과
- **리샘플 테스트:** 1분봉 10개 → 3분봉 4개, 5분봉 2개, 1분봉 10개 그대로. 기대값 일치.
- **API:** `default_timeframe: '1m'`, `v4_ohlcv_minute` 1분봉 기반 응답 확인 (실거래 데이터 존재 시 `/api/v1/backtest/chart/trade/{TRADE_ID}` 응답에 candles 시간 간격 1분 반영)

## 완료 체크리스트
| # | 항목 | 확인 |
|---|------|------|
| 1 | v4_ohlcv_minute bar 간격 확인 (1분) | ✓ |
| 2 | CandleResampler 1분봉 기반 수정 | ✓ |
| 3 | bt_chart.py 기본 1분봉 + 일봉 별도 로드 | ✓ |
| 4 | 전략별 추천 타임프레임 매핑 | ✓ |
| 5 | 프론트 기본 타임프레임 1m | ✓ |
| 6 | npm run build 에러 0 | ✓ |
| 7 | 리샘플 테스트 통과 | ✓ |
| 8 | 보고서 push + URL 200 | (project-docs push 후 확인) |
| 9 | 실거래 파일 변경 0건 | ✓ (kis-v41-api/monitor/scheduler 재시작 없음) |
