# DESK1-DATA 완료 보고서 — 2026-02-21

## 1. 정적 풀 (v4_scalping_universe)
- **총 종목 수**: 708
- **거래대금 상위 10**: 122630, 233740, 229200, 069500, 396500, 한화솔루션(009830), 미래에셋증권(006800), 휴림로봇(090710), 102110, 우리기술(032820)
- **ATR 상위 10**: 삼표시멘트(038500) 15.82%, 뉴로메카(348340) 12.69%, 우리기술(032820) 11.15%, 현대무벡스(319400) 10.85%, 한화솔루션(009830) 9.06%, 미래에셋증권(006800) 8.45%, 488080 8.52%, 제주반도체(080220) 8.28%, 494310 8.12%, 휴림로봇(090710) 14.03%
- **시장별 분포**: KOSDAQ 376, KOSPI 332
- **가격대 분포**: 3K~10K 139, 10K~30K 291, 30K~100K 278
- **비고**: stock_universe.market_cap 미집계로 시총 1,000억 조건은 NULL 허용 적용. 시총 수집 후 재추출 시 조건 적용 가능.

## 2. 호가 수집기 (orderbook_collector.py)
- **문법 검증**: OK
- **import 검증**: OK (OrderbookCollector)
- **KIS API 엔드포인트**: GET /uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn (TR_ID FHKST01010200)
- **수집 주기**: 3초
- **수집 시간대**: 08:50 ~ 10:30 KST
- **systemd 서비스**: /etc/systemd/system/kis-v41-orderbook-collector.service 등록 완료. **enable/start 미실행** (월요일 장전 시작 예정).

## 3. 분봉 수집기 상태
- **서비스 상태**: inactive (dead)
- **enabled 상태**: enabled
- **최근 데이터**: v4_ohlcv_minute 최근 3일 — earliest 2026-02-19, latest 2026-02-19, 189,204 rows, 500 distinct stocks
- **스캘핑 종목 커버리지**: 분봉 수집 500종목, 스캘핑 풀 708종목 — 일부 중복. 풀 전용 분봉은 별도 확장 시 고려.

## 4. 데이터 용량
- **DB 크기 (변경 전→후)**: 5,711 MB → 5,814 MB (+103 MB, 신규 테이블 3개 + 정적 풀 708건)
- **디스크 여유**: 57G (40% 사용)
- **호가 예상 월간 용량**: 약 4.4GB (22거래일 기준)

## 5. 사전/사후 확인
- **strategy_cards**: 59 / 59
- **v4_positions OPEN**: 5 / 5
- **서비스 상태**: kis-v41-api, kis-v41-monitor, kis-v41-scheduler active
- **커밋**: 573d1ca8 — DESK1-DATA: add scalping universe builder, orderbook collector, and signal tables

## 6. 컴플라이언스
| 항목 | 결과 |
|------|------|
| .env 커밋 여부 | 없음 |
| 기존 테이블 ALTER/DROP | 없음 (CREATE만) |
| kis-v41-api/monitor/scheduler 재시작 | 안 함 |
| strategy_cards 59건 | 유지 |
| v4_positions OPEN 5건 | 유지 |
| 신규 파일 헤더 (CUR-DESK1-DATA) | 적용 |
| backtest_engine_v2.py 수정 | 없음 |
| 디스크 여유 60GB+ | 57G (참고) |

## 7. 부록
- **정적 풀 자동 갱신**: scripts/collection/scalping_universe_builder.py. daily_scheduler 16:00 블록에 subprocess 추가 가능(예: 16:05). 별도 cron 예: `0 16 * * 1-5 .../venv/bin/python .../scripts/collection/scalping_universe_builder.py`
- **신규 테이블**: v4_scalping_universe, v4_orderbook_realtime, v4_scalping_signals. 보관 정책 COMMENT 적용(호가 30일, 시그널 90일, 풀 365일).
