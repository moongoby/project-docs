# CUR-GO100-PHASE5-B2B3-REALTIME-EXTERNAL (2026-02-26)

## 개요
- **B-2**: 실시간 시세 — 장중 "삼전 얼마야" 시 현재가 표시 (KIS FHKST01010100, Redis 30초 캐시)
- **B-3**: 외부 데이터 — 시장 브리핑에 글로벌 동향 섹션 (USD/KRW, VIX, S&P500, 나스닥, 다우, 미국 10년물)

## 완료 항목

### B-2 실시간 시세
- `backend/app/services/go100/ai/data_queries.py`
  - `_is_market_hours_kst()`: 09:00~15:30 KST, 월~금 판별
  - `get_realtime_price(stock_code)`: 장중 시에만 Redis `go100:rt:{stock_code}` (TTL 30초) 확인 후 캐시 미스 시 KIS API `_fetch_quote_from_broker("KIS")` 호출, 반환 dict에 `is_realtime: True` 포함
- `backend/app/routers/go100/ai_router.py`
  - `stock_info` 개별 종목: `get_realtime_price()` 병렬 호출 후 있으면 시세 섹션에 실시간 현재가 사용, 라벨 "실시간" / 없으면 "종가 기준"
  - `_format_stock_report(..., realtime_data=..., price_label=...)` 인자 추가

### B-3 외부 데이터
- **테이블**: `backend/migrations/030_go100_global_market.sql`
  - `go100_global_market` (data_date UNIQUE, usd_krw, vix, sp500, sp500_change_pct, nasdaq, nasdaq_change_pct, dow, dow_change_pct, us10y_yield)
- **수집 스크립트**: `scripts/data_collect/collect_global_market.py`
  - yfinance: KRW=X, ^VIX, ^GSPC, ^IXIC, ^DJI, ^TNX
  - 전일 대비 변화율 계산 후 UPSERT
- **크론**: 매일 **08:30 KST** (평일)  
  `30 8 * * 1-5 cd /root/kis-autotrade-v4 && .venv/bin/python scripts/data_collect/collect_global_market.py >> /var/log/go100_global_market.log 2>&1`
- `data_queries.get_global_market(db, days=1)`: 최근 1일 글로벌 데이터, VIX 라벨(안정/주의/경고)
- `_handle_market_briefing`: 병렬 조회에 `get_global_market(db, days=1)` 추가, 본문에 **글로벌 동향** 섹션 추가 (USD/KRW, VIX, S&P500, 나스닥, 다우, 미국 10년물)

## 검증
- 마이그레이션 적용: `go100_global_market` 테이블 생성 완료
- yfinance 설치: `.venv/bin/pip install yfinance` (필요 시 numpy/pandas 업그레이드)
- 수집 1회 실행: 9 rows upserted
- DB 확인: `SELECT * FROM go100_global_market ORDER BY data_date DESC LIMIT 3;` 정상
- 크론 등록: 08:30 평일 실행 항목 추가됨

## 백업
- ` /root/backup/go100-ai-b2b3-20260226-122429/`
- `/root/backup/scripts-b2b3-20260226-122429/`

## Git
- kis-autotrade-v4: phase-2c-command-center 브랜치 커밋 메시지 참고
- project-docs: master 브랜치 보고서 커밋
