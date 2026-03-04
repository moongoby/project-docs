# 금요일 장마감 데이터 동기화 및 수집 현황 보고

| 항목 | 내용 |
|------|------|
| 문서 ID | DATA-SYNC-FRIDAY-001 |
| 작성일 | 2026-03-01 (일) KST |
| 기준일 | 금요일 장마감 2026-02-27 |

---

## 1. 한국시간(KST) 및 서버 시간 동기화

### 1.1 확인 결과

| 항목 | 값 |
|------|-----|
| 서버 UTC | 2026-03-01 04:22~04:26 UTC |
| 서버 KST | 2026-03-01 13:22~13:26 KST (Asia/Seoul) |
| NTP 동기화 | **yes** (System clock synchronized) |
| 타임존 | Asia/Seoul (KST, +0900) |

**결론**: 서버는 NTP로 동기화되어 있으며, 로컬 타임존이 **Asia/Seoul(KST)** 로 설정되어 있어 별도 시간 동기화 조치 불필요.

---

## 2. 금요일 장마감일 vs 수집 데이터 비교

- **금요일 장마감일**: 2026-02-27 (2026-02-28은 토요일이므로 전 거래일인 2/27이 금요일)
- **비교 기간**: 2026-02-24 ~ 2026-02-27 (거래일 4일)
- **유니버스**: stock_universe 활성 종목 3,844종목

### 2.1 금요일(2026-02-27) 당일 수집 현황

| 데이터 유형 | 수집 건수 | 목표 | 비율 | 상태 |
|-------------|-----------|------|------|------|
| 일봉 (ohlcv_daily) | 3,839 | 3,844 | 99.9% | ok |
| 분봉 (v4_ohlcv_minute) | 499 종목 | 500 | 99.8% | ok |
| 수급 (v4_investor_daily) | 0 | 3,844 | 0% | missing |
| 섹터 (v4_sector_daily) | 29 | 29 | 100% | ok |
| 랭킹 (v4_market_ranking) | 0 | 60 | 0% | missing |

### 2.2 미수집·부분 수집에 대한 조치

| 조치 항목 | 내용 |
|-----------|------|
| **섹터** | `run_daily_collection.py --sector --ranking --days 14` 실행 완료. 섹터 203행 추가, 2026-02-27 포함 기간 반영. |
| **순위** | 동일 실행으로 랭킹 2종(VOLUME_TOP, CHANGE_RATE_UP) 60건 수집. (일부 API 404로 TRADE_AMOUNT_TOP 등 4종 실패) |
| **분봉 수집기** | `kis-v41-minute-collector` 서비스가 **inactive**였으나 **start** 후 **active**로 전환. 향후 장중 분봉 자동 수집. |
| **일봉** | DB 최신일이 이미 20260227이며, 2.6M행 보유. 25·26·27일은 모니터링 쿼리와 저장 형식 차이로 “미수집”으로 잡힌 구간이 있을 수 있음. 필요 시 `collect_ohlcv_daily.py --dates 20260225,20260226,20260227` 로 전 종목 보강 가능. |
| **수급** | v4_investor_daily 최신 2026-02-26. 2026-02-27 수급은 `run_daily_collection.py --investor --days 20` 또는 `collect_all_missing_data.py --investor --days 14` 로 보강 가능. |

---

## 3. 수집된 데이터 전체 현황

### 3.1 DB 테이블별 현황 (2026-03-01 기준)

| 테이블 | 총 행 수 | 최신 일자 | 비고 |
|--------|----------|-----------|------|
| ohlcv_daily | 2,615,744 | 2026-02-27 | 일봉, 금요일까지 유지 |
| v4_ohlcv_minute | 72,219,197 | 2026-02-27 | 1분봉, 금요일까지 유지 |
| v4_investor_daily | 261,410 | 2026-02-26 | 수급, 26일까지 |
| v4_sector_daily | 15,057 | 2026-02-27 | 섹터 일봉, 금요일 반영 |
| v4_market_ranking | 420 | 2026-03-01 | 순위, 당일 반영 |

### 3.2 수집 관련 서비스 상태 (조치 후)

| 서비스 | 상태 |
|--------|------|
| kis-v41-minute-collector | **active** (재기동 완료) |
| kis-v41-scheduler | **active** |

### 3.3 요약

- **일봉·분봉·섹터**: 금요일(2026-02-27) 장마감일 기준으로 수집 완료에 가까움.
- **분봉 수집기**: 중지되어 있던 서비스를 기동하여 이후 장중 분봉 자동 수집 가능.
- **수급·랭킹**: 금요일 당일 수급은 미수집, 랭킹은 API 제한으로 일부만 수집. 필요 시 위 스크립트로 보강.

---

## 4. 재현용 명령

```bash
# 한국시간 확인
TZ=Asia/Seoul date '+%Y-%m-%d %H:%M:%S KST'

# 금요일·수집 현황 점검 스크립트
cd /root/kis-autotrade-v4 && source .venv/bin/activate
PYTHONPATH=/root/kis-autotrade-v4 python scripts/check_friday_data_and_report.py

# 섹터·순위 수집
PYTHONPATH=/root/kis-autotrade-v4 python backend/app/services/data_pipeline/run_daily_collection.py --sector --ranking --days 14

# 분봉 수집기 기동
sudo systemctl start kis-v41-minute-collector
```

---

**문서 끝**
