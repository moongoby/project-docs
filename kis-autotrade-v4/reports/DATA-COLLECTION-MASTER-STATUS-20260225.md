# 데이터 수집 현황 총괄 기술문서

**작성일**: 2026-02-25
**프로젝트**: kis-autotrade-v4
**DB 크기**: 13 GB (PostgreSQL `kisautotrade`)
**목적**: 전체 데이터 수집 파이프라인의 현황·구조·운영 상태를 종합 정리

**작업·반영 이력**

| 일자 | 내용 |
|------|------|
| 2026-02-25 | 최초 작성: 전체 데이터 수집 현황 총괄 기술문서 |
| 2026-02-25 | CUR-GO100-DATA-ENGINE-INTEGRATION 반영: 수급/신용잔고 크론 자동화, 신규 필터 5종 엔진 연동, 거래정지 차단 |

---

## 목차

1. [데이터 인벤토리 총괄](#1-데이터-인벤토리-총괄)
2. [데이터 소스별 상세](#2-데이터-소스별-상세)
3. [수집 파이프라인 아키텍처](#3-수집-파이프라인-아키텍처)
4. [컬렉터 상세 목록](#4-컬렉터-상세-목록)
5. [스케줄러 구조](#5-스케줄러-구조)
6. [수집 스크립트 목록](#6-수집-스크립트-목록)
7. [DB 테이블 스키마 요약](#7-db-테이블-스키마-요약)
8. [데이터 갭 및 미수집 항목](#8-데이터-갭-및-미수집-항목)
9. [운영 가이드](#9-운영-가이드)
10. [향후 과제](#10-향후-과제)

---

## 1. 데이터 인벤토리 총괄

### 1.1 주요 데이터 테이블 현황

| 구분 | 테이블 | 행 수 | 크기 | 기간 | 엔티티 수 | 소스 | 상태 |
|------|--------|------:|-----:|------|----------:|:---:|:---:|
| **가격(일봉)** | `ohlcv_daily` | 2,604,226 | 672 MB | 2023-01-02 ~ 2026-02-24 | 3,844 종목 | KIS | ✅ |
| **가격(주봉)** | `ohlcv_weekly` | 357,381 | 50 MB | 2024-03-04 ~ 2026-02-09 | 3,844 종목 | KIS | ✅ |
| **가격(월봉)** | `ohlcv_monthly` | 89,307 | 13 MB | 2024-02-29 ~ 2026-02-11 | 3,844 종목 | KIS | ✅ |
| **가격(분봉)** | `v4_ohlcv_minute_*` | 41,665,605 | **10 GB** | 2025-02 ~ 2026-02 | ~3,800 종목 | KIS | ✅ |
| **투자자(종목별)** | `v4_investor_daily` | 171,261 | 172 MB | 2010-01-28 ~ 2026-02-24 | 3,943 종목 | KIS | ✅ |
| **투자자(시장)** | `v4_market_investor_daily` | 3,614 | 1.7 MB | 2018-10-15 ~ 2026-02-24 | 2 시장 | KIS | ✅ |
| **업종지수** | `v4_sector_daily` | 14,999 | 9.3 MB | 2018-10-19 ~ 2026-02-25 | 32 업종 | KIS | ✅ |
| **종목-업종매핑** | `v4_stock_sector` | 4,225 | 472 KB | - | 4,225 종목 | KIS | ✅ |
| **시장 레짐** | `v4_market_regime_daily` | 819 | 280 KB | 2022-09-07 ~ 2026-02-23 | 1 | 산출 | ✅ |
| **VKOSPI** | `v4_vkospi_daily` | 1,506 | 400 KB | 2020-01-02 ~ 2026-02-20 | 1 | 공공데이터 | ✅ |
| **지수(KOSPI 등)** | `index_daily` | 1,476 | 432 KB | 2024-02-13 ~ 2026-02-23 | 3 지수 | KIS | ✅ |
| **체결강도(일별)** | `v4_trade_strength_history` | 219,892 | 29 MB | 2025-11-26 ~ 2026-02-24 | 3,757 종목 | **키움** | ✅ |
| **테마 마스터** | `v4_theme_master` | 100 | 64 KB | 2026-02-25 | 100 테마 | **키움** | ✅ |
| **테마-종목매핑** | `v4_theme_stock` | 569 | 200 KB | 2026-02-25 | 100 테마, 472 종목 | **키움** | ✅ |
| **테마 상세** | `v4_theme_detail` | 100 | 80 KB | 2026-02-25 | 100 테마 | **키움** | ✅ |
| **재무비율** | `financial_ratios` | 45,870 | 6.6 MB | - | 2,612 종목 | KIS | ✅ |
| **기업 기본정보** | `stock_fundamentals` | 8,093 | 1.7 MB | - | 4,225 종목 | KIS | ✅ |
| **종목 유니버스** | `stock_universe` | 3,844 | 1.7 MB | - | 3,844 종목 | KIS | ✅ |
| **시장 캘린더** | `v4_market_calendar` | 129 | 96 KB | 2025~2026 | - | 수동 | ✅ |
| **거래대금 상위** | `market_turnover_daily` | 26,148 | 3.2 MB | 2025-02-05 ~ 2026-02-05 | 98 종목 | KIS | ✅ |
| **시장 랭킹** | `v4_market_ranking` | 300 | 296 KB | - | 117 종목 | KIS | ✅ |
| **스캘핑 유니버스** | `v4_scalping_universe` | 708 | 216 KB | - | - | 산출 | ✅ |
| **프로그램매매** | `v4_program_trades` | 0 | 24 KB | - | - | **키움** | ⏳ (cron 16:30) |
| **신용잔고** | `v4_credit_balance` | 0 | 24 KB | - | - | KIS | ⏳ (cron 16:45) |
| **업종가격** | `v4_sector_price` | 0 | 24 KB | - | - | KIS | ⏳ |
| **회원사매매** | `v4_broker_trades` | 0 | 24 KB | - | - | KIS | ⏳ |
| **조건검색** | `v4_condition_search` | 0 | 24 KB | - | - | **키움** | ⏳ |
| **틱데이터** | `v4_tick_data` | 0 | 16 KB | - | - | **키움** | ⏳ |

> ✅ = 수집 완료 (데이터 존재) / ⏳ = 컬렉터 준비 완료, 장중 수집 예정

### 1.2 총괄 수치

| 항목 | 수치 |
|------|-----:|
| 전체 테이블 수 (public) | 170 |
| 데이터 보유 테이블 (>0행) | 126 |
| 빈 데이터 테이블 | 44 |
| 전체 DB 크기 | **13 GB** |
| 분봉 데이터 크기 | **10 GB** (77%) |
| 일봉 데이터 크기 | 672 MB |
| 투자자 데이터 크기 | 172 MB |
| 활성 종목 수 | 3,844 |
| 총 데이터 행 수 (주요 테이블) | **~45,100,000** |

---

## 2. 데이터 소스별 상세

### 2.1 KIS (한국투자증권) REST API

| API TR ID | 이름 | 대상 테이블 | 수집 방식 | 상태 |
|:---:|------|------|:---:|:---:|
| FHKST03010100 | 주식 일봉 | `ohlcv_daily` | 일 1회 + 이력 백필 | ✅ |
| FHKST03010100 | 주식 주봉·월봉 | `ohlcv_weekly`, `ohlcv_monthly` | 백필 스크립트 | ✅ |
| FHKST03010230 | 주식 분봉 (1분) | `v4_ohlcv_minute_*` | 장후 배치 | ✅ |
| FHKST01010900 | 종목별 투자자 | `v4_investor_daily` | **cron 16:50** (상위 500) | ✅ |
| FHPTJ04040000 | 시장 투자자 | `v4_market_investor_daily` | cron 18:40 | ✅ |
| FHKUP03500100 | 업종 지수 | `v4_sector_daily` | 일 1회 + 이력 백필 | ✅ |
| CTPF1002R | 기업 기본정보 | `stock_fundamentals` | 필요시 | ✅ |
| FHKST01010100 | 현재가 조회 | `stock_fundamentals.shares_outstanding` | 필요시 | ✅ |
| FHKST01010600 | 회원사 매매 | `v4_broker_trades` | Phase 2: 16:00 | ⏳ |
| FHPUP02120000 | 업종 현재가 | `v4_sector_price` | Phase 2: 15:45 | ⏳ |
| FHKST17010000 | 신용잔고 | `v4_credit_balance` | **cron 16:45** | ✅ (크론등록) |

### 2.2 키움증권 REST API

| API ID | 이름 | 대상 테이블 | 수집 방식 | 상태 |
|:---:|------|------|:---:|:---:|
| ka90001 | 테마그룹별요청 | `v4_theme_master` | 스크립트 수동 | ✅ |
| ka90002 | 테마구성종목요청 | `v4_theme_stock`, `v4_theme_detail` | 스크립트 수동 + Phase 3: 17:00 | ✅ |
| ka10047 | 체결강도추이일별 | `v4_trade_strength_history` | 스크립트 수동 + Phase 2: 5분 | ✅ |
| ka90004 | 종목별프로그램매매 | `v4_program_trades` | **cron 16:30** | ✅ (크론등록) |
| ka10046 | 체결강도추이시간별 | (v4_trade_strength_history) | Phase 2: 장중 5분 | ⏳ |
| ka10079 | 틱데이터 | `v4_tick_data` | Phase 3: 장중 1분 | ⏳ |
| - | 조건검색 | `v4_condition_search` | Phase 3: 장중 5분 | ⏳ |

### 2.3 외부 데이터

| 소스 | 데이터 | 대상 테이블 | 상태 |
|------|--------|------|:---:|
| 공공데이터포털 | VKOSPI | `v4_vkospi_daily` | ✅ |
| 내부 산출 | 시장 레짐 | `v4_market_regime_daily` | ✅ |
| 수동 입력 | 시장 캘린더 | `v4_market_calendar` | ✅ |

### 2.4 키움 API 인증 체계

```
인증 흐름:
  ┌─ 환경변수 (KIWOOM_APP_KEY / KIWOOM_APP_SECRET)
  │   └─ 비어있으면 ↓
  └─ DB accounts 테이블 (enc_app_key / enc_app_secret)
       └─ CryptoService(Fernet) 복호화 → KiwoomBrokerClient

계정 현황 (accounts 테이블):
  account_id=4  모의계좌  81201280  (is_mock=true)
  account_id=5  실거래    52568156  (is_mock=false) ← 사용 중
  account_id=6  실거래    63109343  (is_mock=false)

토큰: Redis 캐시 (token:kiwoom:*), 23시간 TTL
API 엔드포인트:
  실거래: https://api.kiwoom.com
  모의:   https://mockapi.kiwoom.com
```

공통 모듈: `backend/app/services/data/kiwoom_credentials.py`

---

## 3. 수집 파이프라인 아키텍처

### 3.1 전체 데이터 흐름

```
┌─────────────────────────────────────────────────────────────────────┐
│                    kis-autotrade-v4 데이터 수집 파이프라인              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌── 실시간 수집 (장중 09:00~15:30) ────────────────────────────┐  │
│  │                                                               │  │
│  │  Phase 2 스케줄러 (async, 60초 루프):                        │  │
│  │  ├─ 매 5분: 체결강도 (키움 ka10047)                          │  │
│  │  ├─ 15:45: 업종 현재가 (KIS FHPUP02120000)                  │  │
│  │  ├─ 16:00: 회원사 매매 (KIS FHKST01010600)                  │  │
│  │  └─ 16:30: 신용잔고 (KIS FHKST17010000)                     │  │
│  │                                                               │  │
│  │  Phase 3 스케줄러 (async, 60초 루프):                        │  │
│  │  ├─ 매 1분: 틱데이터 Top20 (키움 ka10079)                    │  │
│  │  ├─ 매 5분: 조건검색 (키움)                                   │  │
│  │  ├─ 16:25~16:40: 프로그램매매 (키움 ka90004)                 │  │
│  │  ├─ 16:55~17:10: 테마 상세 (키움 ka90002)                    │  │
│  │  └─ 03:00: 틱데이터 정리 (7일 보존)                           │  │
│  │                                                               │  │
│  │  계좌 동기화 (동적 간격):                                      │  │
│  │  └─ 08:00~09:00: 5분 / 09:00~15:30: 3분 / 장후: 10분        │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌── 일간 스케줄 (Cron/서비스) ──────────────────────────────────┐  │
│  │                                                               │  │
│  │  07:50  투자자·업종·랭킹 수집 (daily_scheduler)              │  │
│  │  15:40  일봉 OHLCV 수집 + 리포트 생성                         │  │
│  │  18:30  지수(KOSPI/KOSDAQ/200) (cron)                       │  │
│  │  18:40  시장투자자 (cron)                                     │  │
│  │  장후   분봉 이력 배치 (minute_batch_cron.sh)                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌── 이력 백필 (수동 스크립트) ───────────────────────────────────┐  │
│  │                                                               │  │
│  │  collect_ohlcv_daily_history.py     → ohlcv_daily            │  │
│  │  collect_historical_daily.py        → 복수 테이블             │  │
│  │  collect_sector_history.py          → v4_sector_daily        │  │
│  │  collect_market_investor_history.py → v4_market_investor     │  │
│  │  collect_minute_historical.py       → v4_ohlcv_minute_*     │  │
│  │  collect_all_missing_data.py        → P0~P3 자동 백필        │  │
│  │  collect_kiwoom_theme.py            → v4_theme_*            │  │
│  │  collect_kiwoom_strength.py         → v4_trade_strength     │  │
│  │  collect_shares_outstanding.py      → stock_fundamentals    │  │
│  │  collect_vkospi.py / _alt.py        → v4_vkospi_daily       │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 기술 스택

| 구성요소 | 기술 |
|----------|------|
| 데이터베이스 | PostgreSQL 14+ (kisautotrade) |
| 백엔드 | FastAPI (Python 3.12) |
| 비동기 HTTP | httpx (async) |
| 토큰 캐시 | Redis (23h TTL) |
| 암호화 | Fernet (cryptography) |
| 스케줄링 | APScheduler + 커스텀 async 루프 |
| 분봉 파티셔닝 | PostgreSQL RANGE 파티션 (월별) |

---

## 4. 컬렉터 상세 목록

### 4.1 서비스 컬렉터 (`backend/app/services/data/`)

| 파일 | API 소스 | 대상 테이블 | 스케줄 | 비고 |
|------|:---:|------|------|------|
| `trade_strength_history_collector.py` | 키움 ka10047 | v4_trade_strength_history | Phase 2: 장중 5분 | 체결강도 |
| `broker_trades_collector.py` | KIS FHKST01010600 | v4_broker_trades | Phase 2: 16:00 | 회원사 매매 |
| `sector_price_collector.py` | KIS FHPUP02120000 | v4_sector_price | Phase 2: 15:45 | 업종 현재가 |
| `credit_balance_collector.py` | KIS FHKST17010000 | v4_credit_balance | Phase 2: 16:30 | 신용잔고 |
| `tick_data_collector.py` | 키움 ka10079 | v4_tick_data | Phase 3: 장중 1분 | 틱데이터 Top20 |
| `condition_search_collector.py` | 키움 조건검색 | v4_condition_search | Phase 3: 장중 5분 | 조건검색 |
| `program_trades_collector.py` | 키움 ka90004 | v4_program_trades | Phase 3: 16:25~16:40 | 프로그램매매 |
| `theme_detail_collector.py` | 키움 ka90002 | v4_theme_detail | Phase 3: 16:55~17:10 | 테마 상세 |
| `investor_collector.py` | KIS FHKST01010900 | v4_investor_daily | daily_scheduler | 종목별 투자자 |
| `kis_api_interface.py` | KIS | - | - | KIS API 래퍼 (공통) |
| `kiwoom_credentials.py` | 키움 | - | - | 키움 자격증명 로더 (공통) |
| `base_provider.py` | - | - | - | 데이터 프로바이더 베이스 |
| `live_provider.py` | - | - | - | 실시간 데이터 조회 |
| `backtest_provider.py` | - | - | - | 백테스트 데이터 조회 |

### 4.2 키움 컬렉터 공통 모듈 의존 구조

```
kiwoom_credentials.py (공통 자격증명: env → DB 폴백)
  │
  ├── trade_strength_history_collector.py  (ka10047)
  ├── program_trades_collector.py          (ka90004)
  ├── theme_detail_collector.py            (ka90002)
  ├── tick_data_collector.py               (ka10079)
  └── condition_search_collector.py        (조건검색)
```

---

## 5. 스케줄러 구조

### 5.1 스케줄러 서비스

| 스케줄러 | 파일 | 시작 | 동작 방식 |
|----------|------|:---:|------|
| **Phase 2 Data** | `backend/app/services/phase2_data_scheduler.py` | FastAPI lifespan | async 루프 (60초 체크) |
| **Phase 3 Data** | `backend/app/services/phase3_data_scheduler.py` | 수동/옵션 | async 루프 (60초 체크) |
| **Account Sync** | `backend/app/services/account_sync_scheduler.py` | FastAPI lifespan | async (동적 간격) |
| **Daily Scheduler** | `backend/app/services/scheduler/daily_scheduler.py` | v41_scheduler.py | 시간대별 상태 전환 |

### 5.2 일간 스케줄 타임라인

```
시간     이벤트                                    수집 대상
─────────────────────────────────────────────────────────────
07:50    오전 수집                                 투자자, 업종, 랭킹
08:00    계좌 동기화 시작                           5분 간격
08:30    헬스 체크
08:50    PRE_MARKET 전환                           (수집 일시 정지)
09:00    장 시작 → TRADING 상태                    Phase 2/3 수집 시작
         ├─ 매 1분: 틱데이터 (Phase 3)
         ├─ 매 3분: 계좌 동기화
         └─ 매 5분: 체결강도, 조건검색
15:15    장마감 경고
15:20    CLOSING 전환
15:30    장 종료
15:35    POST_MARKET 전환
15:40    일봉 수집 + 리포트 생성                    ohlcv_daily
15:45    업종 현재가 (Phase 2)                      v4_sector_price
16:00    회원사 매매 (Phase 2)                      v4_broker_trades
16:25    프로그램매매 (Phase 3)                     v4_program_trades
16:30    프로그램매매 (cron)                        v4_program_trades
16:35    체결강도 일별 (cron)                       v4_trade_strength_history
16:45    신용잔고/공매도 (cron) ★신규              v4_credit_balance
16:50    투자자 수급 (cron) ★신규                  v4_investor_daily (상위 500)
16:55    테마 상세 (Phase 3)                        v4_theme_detail
17:00    테마 수집 (cron)                           v4_theme_master/stock
18:00    일봉 OHLCV (cron)                         ohlcv_daily
18:30    지수 수집 (cron)                           index_daily
18:30    VKOSPI (cron)                             v4_vkospi_daily
18:40    시장 투자자 (cron)                         v4_market_investor_daily
19:00    종목 유니버스 (cron)                       stock_universe
03:00    DB 백업
```

### 5.3 Systemd 서비스

| 서비스 | 설정 파일 | 실행 명령 |
|--------|----------|----------|
| v41-scheduler | `docs/v41-scheduler.service` | `scripts/v41_scheduler.py` |
| go100-backend | (별도) | FastAPI uvicorn |
| go100-frontend | (별도) | Next.js |

---

## 6. 수집 스크립트 목록

### 6.1 이력 백필 스크립트 (`scripts/`)

| 스크립트 | API | 대상 테이블 | 용도 |
|----------|:---:|------|------|
| `collect_ohlcv_daily.py` | KIS | ohlcv_daily | 당일 일봉 수집 |
| `collect_ohlcv_daily_history.py` | KIS | ohlcv_daily | 이력 일봉 백필 (100일 청크) |
| `collect_historical_daily.py` | KIS | 복수 테이블 | 1년 배치 수집 (OHLCV+업종+투자자) |
| `collect_minute_historical.py` | KIS | v4_ohlcv_minute_* | 분봉 이력 수집 (자동 이어받기) |
| `collect_sector_history.py` | KIS | v4_sector_daily | 업종지수 이력 백필 |
| `collect_market_investor.py` | KIS | v4_market_investor_daily | 일간 시장 투자자 (cron) |
| `collect_market_investor_history.py` | KIS | v4_market_investor_daily | 시장 투자자 이력 백필 |
| `collect_stock_industry.py` | KIS | stock_industry | 종목 업종분류 |
| `collect_shares_outstanding.py` | KIS | stock_fundamentals | 상장주식수 수집 |
| `collect_vkospi.py` | 공공데이터 | v4_vkospi_daily | VKOSPI 수집 |
| `collect_vkospi_alt.py` | 공공데이터/pykrx | v4_vkospi_daily | VKOSPI 대안 수집 |
| `collect_all_missing_data.py` | KIS | 복수 테이블 | P0~P3 자동 백필 코디네이터 |
| `collect_kiwoom_theme.py` | **키움** | v4_theme_master/stock | 테마 수집 (ka90001+ka90002) |
| `collect_kiwoom_strength.py` | **키움** | v4_trade_strength_history | 체결강도 60일 이력 (ka10047) |

### 6.2 셸 크론 스크립트

| 스크립트 | 용도 | 크론 | 상태 |
|----------|------|------|:---:|
| `cron/collect_program_trades.sh` | 프로그램매매 (키움 ka90004) | 평일 16:30 | ✅ |
| `cron/collect_strength_daily.sh` | 체결강도 일별 (키움 ka10047) | 평일 16:35 | ✅ |
| `cron/collect_credit_balance.sh` | 신용잔고/공매도 (KIS) | **평일 16:45** | **✅ 신규** |
| `cron/collect_investor_daily.sh` | 투자자 수급 (KIS, 상위 500) | **평일 16:50** | **✅ 신규** |
| `cron/collect_theme.sh` | 테마 (키움 ka90001+ka90002) | 평일 17:00 | ✅ |
| `cron/collect_strength_intraday.sh` | 체결강도 장중 증분 | 장중 매 5분 | ✅ |
| `collect_index_daily.sh` | KOSPI/KOSDAQ/200 지수 | 평일 18:30 | ✅ |
| `minute_batch_cron.sh` | 분봉 배치 수집 | 평일 16:00~ | ✅ |
| `collection_scheduler.sh` | 수집 일시정지/재개 | 08:50/15:40 | ✅ |

### 6.3 실행 방법 (공통)

```bash
cd /root/kis-autotrade-v4
source .venv/bin/activate
PYTHONPATH=/root/kis-autotrade-v4 python scripts/<스크립트명>.py [옵션]
```

---

## 7. DB 테이블 스키마 요약

### 7.1 가격 데이터

**`ohlcv_daily`** — 일봉 OHLCV (varchar(8) 날짜, real 가격)
```
stock_code VARCHAR(10) | date VARCHAR(8) | open/high/low/close REAL | volume BIGINT
UNIQUE(stock_code, date)
```

**`v4_ohlcv_minute_*`** — 분봉 OHLCV (RANGE 파티션, 월별 15개)
```
stock_code VARCHAR(10) | trade_date DATE | trade_time TIME | open/high/low/close_price INT | volume/trade_amount BIGINT
PK(stock_code, trade_date, trade_time) — 15 파티션 (2025-01 ~ 2026-03)
```

### 7.2 투자자·기관

**`v4_investor_daily`** — 종목별 투자자 매매 (외국인/기관/개인)
```
stock_code VARCHAR(12) | trade_date DATE
foreign_buy/sell/net_qty BIGINT | institution_buy/sell/net_qty BIGINT | individual_net_qty BIGINT
foreign_hold_qty BIGINT | foreign_hold_ratio NUMERIC(8,4)
program_buy/sell_amount BIGINT
UNIQUE(stock_code, trade_date)
```

**`v4_market_investor_daily`** — 시장 전체 투자자 (KOSPI/KOSDAQ)
```
market VARCHAR(10) | trade_date DATE
index_close NUMERIC(12,2) | foreign/institution/individual_net_qty BIGINT
```

### 7.3 업종·지수

**`v4_sector_daily`** — 업종별 일간 지수
```
sector_code VARCHAR(20) | sector_name VARCHAR(100) | trade_date DATE
open/high/low/close_index NUMERIC(12,2) | change_rate NUMERIC(8,4)
volume BIGINT | trade_amount BIGINT | change_rate_5d/20d | sector_rank INT
UNIQUE(sector_code, trade_date)
```

**`v4_stock_sector`** — 종목-업종 매핑 (4,225건)

### 7.4 테마 (키움)

**`v4_theme_master`** — 테마 마스터
```
theme_code VARCHAR(20) UNIQUE | theme_name VARCHAR(100) | is_active BOOLEAN | first_seen_date DATE
```

**`v4_theme_stock`** — 테마-종목 매핑
```
theme_code VARCHAR(20) | stock_code VARCHAR(12) | stock_name | is_leader BOOLEAN | mapped_date DATE
UNIQUE(theme_code, stock_code, mapped_date)
```

**`v4_theme_detail`** — 테마 상세 (JSONB)
```
theme_code VARCHAR(20) PK | theme_name | detail JSONB | collected_at
```

### 7.5 체결강도·매매

**`v4_trade_strength_history`** — 체결강도 일별 이력
```
stock_code | recorded_at TIMESTAMPTZ | strength NUMERIC(8,2) | buy_count | sell_count | buy_amount | sell_amount
```

**`v4_program_trades`** — 프로그램매매 (장중 수집)
```
stock_code VARCHAR(10) | trade_date DATE
program_buy/sell/net_amount BIGINT | arbitrage_buy/sell_amount | non_arbitrage_buy/sell_amount
UNIQUE(stock_code, trade_date)
```

### 7.6 기업 기본정보

**`stock_fundamentals`** — 기업 기본정보 (PER/PBR/EPS/BPS/시총/상장주식수)
```
stock_code VARCHAR(10) | date VARCHAR(8) | per/pbr/eps/bps REAL | market_cap BIGINT
shares_outstanding BIGINT | face_value REAL | capital BIGINT | loan_remain_rate REAL
UNIQUE(stock_code, date)
```

**`financial_ratios`** — 재무비율 (분기별)
```
stock_code VARCHAR(10) | stac_yymm VARCHAR(6) | grs(매출총이익률) | bsop_prfi_inrt(영업이익률)
ntin_inrt(순이익률) | roe_val | eps | sps | bps | rsrv_rate(유보율) | lblt_rate(부채비율)
UNIQUE(stock_code, stac_yymm)
```

### 7.7 기타

**`v4_market_regime_daily`** — 시장 레짐 (산출)
```
date DATE UNIQUE | regime VARCHAR(30) | regime_score NUMERIC(5,2) | kospi_ret_20d | ma5 | ma20
```

**`v4_vkospi_daily`** — VKOSPI 변동성 지수
```
date VARCHAR(8) UNIQUE | open/high/low/close REAL | change_rate REAL
```

**`v4_market_calendar`** — 시장 캘린더 (휴장일·이벤트)
```
date DATE | event_type VARCHAR(50) | event_name | bet_modifier NUMERIC(3,2)
desk1~5_active BOOLEAN | class_restrictions JSON | note TEXT
UNIQUE(date, event_type)
```

---

## 7b. 수집 데이터 → 엔진 연동 현황 (CUR-GO100-DATA-ENGINE-INTEGRATION)

### 유니버스 필터 연동

| # | 필터 | 데이터 소스 | 기능 | 파이프라인 |
|---|------|-----------|------|-----------|
| 13 | `filter_credit_short` | v4_credit_balance | 신용잔고율/공매도잔고율 과열 종목 제외 | daily, swing |
| 14 | `filter_by_theme` | v4_theme_master/stock | 특정 테마 소속 종목 선별 | AI 전략 |
| 15 | `filter_trade_strength` | v4_trade_strength_history | 체결강도 >= 기준값 종목 (매수세 우위) | AI 전략 |
| 16 | `filter_program_trading` | v4_program_trades | 프로그램매매 순매수/순매도 필터 | AI 전략 |
| 17 | `filter_supply_demand` | 복합 (수급+강도+신용) | 수급 강도 복합 필터 (교집합) | AI 전략 |

### 데이터 활용 매트릭스

| 데이터 | 백테스트 | 유니버스 필터 | AI 전략생성 | 수집 |
|--------|---------|-------------|------------|------|
| ohlcv_daily | **사용** | **사용** | 간접 | 자동 |
| stock_universe | **사용** | **사용** | 간접 | 자동 |
| v4_investor_daily | - | **사용** | **사용** | **자동** (cron 16:50) |
| v4_credit_balance | - | **사용** (신규) | **사용** (신규) | **자동** (cron 16:45) |
| v4_theme_master/stock | - | **사용** (신규) | **사용** (신규) | 자동 (cron 17:00) |
| v4_trade_strength | - | **사용** (신규) | **사용** (신규) | 자동 (cron 16:35) |
| v4_program_trades | - | **사용** (신규) | **사용** (신규) | 자동 (cron 16:30) |

### AI DESIGN 프롬프트 반영

- `ADVANCED_FILTER_SPEC` (prompts.py): 12개 → **17개** 필터로 확장
- 신규 필터 활용 가이드: 테마 전략, 수급 모멘텀, 프로그램 추종

---

## 8. 데이터 갭 및 미수집 항목

### 8.1 크론 등록 완료, 데이터 적재 대기

| 테이블 | 컬렉터 | API | 크론 | 상태 |
|--------|--------|:---:|------|:---:|
| `v4_program_trades` | program_trades_collector.py | 키움 ka90004 | **cron 16:30** | 크론 등록, 다음 거래일 적재 예정 |
| `v4_credit_balance` | credit_balance_collector.py | KIS FHKST17010000 | **cron 16:45** | 크론 등록, 다음 거래일 적재 예정 |

### 8.1b 장중 수집 예정 (스케줄러 의존, 크론 미등록)

| 테이블 | 컬렉터 | API | 필요 조건 |
|--------|--------|:---:|------|
| `v4_sector_price` | sector_price_collector.py | KIS FHPUP02120000 | Phase 2 스케줄러 장후 15:45 |
| `v4_broker_trades` | broker_trades_collector.py | KIS FHKST01010600 | Phase 2 스케줄러 장후 16:00 |
| `v4_condition_search` | condition_search_collector.py | 키움 조건검색 | Phase 3 장중 5분 |
| `v4_tick_data` | tick_data_collector.py | 키움 ka10079 | Phase 3 장중 1분 |

### 8.2 구조만 존재하는 테이블 (컬렉터 미구현 또는 비활성)

| 테이블 | 상태 | 비고 |
|--------|:---:|------|
| `v4_theme_daily` | 빈 테이블 | 테마 일간 변동 — 수집기 미구현 |
| `v4_theme_activity_daily` | 빈 테이블 | 테마 활동 지표 — 수집기 미구현 |
| `v4_theme_stock_mapping` | 빈 테이블 | v4_theme_stock과 중복? 확인 필요 |
| `v4_orderbook_realtime` | 빈 테이블 | 실시간 호가 — WebSocket 필요 |
| `v4_scalping_signals` | 빈 테이블 | 스캘핑 시그널 — 엔진 연동 |

### 8.3 분봉 파티션 미수집 기간

| 파티션 | 행 수 | 상태 |
|--------|------:|:---:|
| `v4_ohlcv_minute_2025_01` | 0 | 미수집 |
| `v4_ohlcv_minute_2025_02` | 986,894 | 부분 수집 |
| `v4_ohlcv_minute_2025_03` ~ `2026_02` | 2.5M~4.1M/월 | ✅ 완료 |
| `v4_ohlcv_minute_2026_03` | 0 | 미래 (파티션만 생성) |

---

## 9. 운영 가이드

### 9.1 일상 운영 체크리스트

| 시간 | 확인 항목 | 명령 |
|------|----------|------|
| 08:00 | v41-scheduler 서비스 정상 | `systemctl status v41-scheduler` |
| 09:10 | Phase 2/3 스케줄러 가동 확인 | 로그 확인: `tail -f logs/scheduler.log` |
| 16:00 | 일봉 수집 완료 | `SELECT max(date) FROM ohlcv_daily;` |
| 17:30 | 프로그램매매·테마 수집 완료 | `SELECT count(*) FROM v4_program_trades WHERE trade_date = CURRENT_DATE;` |
| 19:00 | 시장 투자자·지수 수집 완료 | `SELECT max(trade_date) FROM v4_market_investor_daily;` |

### 9.2 수동 백필 명령

```bash
# 일봉 이력 백필 (100일씩)
PYTHONPATH=. python scripts/collect_ohlcv_daily_history.py --start-date 20230102

# 분봉 이력 백필 (상위 500종목)
PYTHONPATH=. python scripts/collect_minute_historical.py --top-n 500

# 키움 테마 전체 수집
PYTHONPATH=. python scripts/collect_kiwoom_theme.py

# 키움 체결강도 60일 이력
PYTHONPATH=. python scripts/collect_kiwoom_strength.py

# 자동 갭 백필 (P0~P3)
PYTHONPATH=. python scripts/collect_all_missing_data.py
```

### 9.3 데이터 품질 확인 SQL

```sql
-- 최근 수집 현황 요약
SELECT 'ohlcv_daily' as tbl, max(date) as latest FROM ohlcv_daily
UNION ALL SELECT 'v4_investor_daily', max(trade_date)::text FROM v4_investor_daily
UNION ALL SELECT 'v4_sector_daily', max(trade_date)::text FROM v4_sector_daily
UNION ALL SELECT 'v4_trade_strength', max(recorded_at::date)::text FROM v4_trade_strength_history
UNION ALL SELECT 'v4_theme_master', max(last_updated)::text FROM v4_theme_master
ORDER BY tbl;

-- 분봉 파티션별 행 수
SELECT relname, n_live_tup FROM pg_stat_user_tables
WHERE relname LIKE 'v4_ohlcv_minute_20%' ORDER BY relname;

-- 빈 데이터 테이블
SELECT relname, n_live_tup FROM pg_stat_user_tables
WHERE schemaname='public' AND n_live_tup = 0 AND relname LIKE 'v4_%'
ORDER BY relname;
```

### 9.4 Rate Limit 참고

| API | 제한 | 대응 |
|:---:|------|------|
| KIS REST | 20 req/s | 0.05s sleep |
| 키움 REST | ~10 req/s | 0.12~0.15s sleep |

---

## 10. 향후 과제

### 10.1 단기 (P0~P1)

| 우선순위 | 항목 | 상태 |
|:---:|------|:---:|
| P0 | Phase 3 스케줄러 main.py lifespan 등록 | 미착수 |
| P0 | 프로그램매매 장중 자동 수집 검증 (ka90004) | **cron 등록 완료**, 데이터 적재 확인 대기 |
| P1 | 테마 데이터 일 1회 자동 수집 cron 설정 (17:00) | **완료** (cron 17:00) |
| P1 | 체결강도 이력 증분 수집 (신규 데이터만) | **완료** (cron 16:35) |
| P1 | 분봉 2025-01 백필 | 미착수 |
| P1 | **투자자 수급 자동 수집 (상위 500종목)** | **완료** (cron 16:50) |
| P1 | **신용잔고/공매도 자동 수집** | **완료** (cron 16:45) |
| P1 | **수집 데이터 → 엔진 필터 연동 (5종)** | **완료** (advanced_filters.py) |
| P1 | **거래정지 종목 백테스트 진입 차단** | **완료** (simulator.py) |

### 10.2 중기 (P2)

| 항목 | 비고 |
|------|------|
| 체결강도 시간별 (ka10046) 장중 수집 | 장시간 내에만 데이터 반환 |
| v4_theme_daily / v4_theme_activity_daily 수집기 구현 | 테마 일간 변동 추적 |
| 데이터 수집 모니터링 대시보드 (관리자) | 수집 상태 실시간 확인 |
| v4_sector_price / v4_broker_trades 크론 전환 | Phase 2 스케줄러 → 독립 크론 |

### 10.3 장기 (P3)

| 항목 | 비고 |
|------|------|
| 실시간 호가 (v4_orderbook_realtime) | WebSocket 필요 |
| 뉴스·공시 데이터 | 외부 API 필요 |
| VI 발동 이력 | KRX 데이터 |
| 분봉 데이터 아카이브 (S3 등) | 10GB+ 증가 관리 |

---

## 보고 요약

| 항목 | 수치 |
|------|-----:|
| **DB 크기** | 13 GB |
| **주요 데이터 테이블** | 27개 |
| **총 데이터 행** | ~45,100,000 |
| **수집 완료 테이블** | 21개 (✅) |
| **크론 등록, 적재 대기** | 2개 (v4_credit_balance, v4_program_trades) |
| **장중 수집 예정 (스케줄러)** | 4개 (⏳) |
| **데이터 소스** | KIS REST + 키움 REST + 공공데이터 |
| **서비스 컬렉터** | 14개 |
| **수집 스크립트** | 14개 |
| **크론 등록 셸 스크립트** | **9개** (기존 7 + 신규 2) |
| **스케줄러** | 4개 (Phase2 + Phase3 + AccountSync + Daily) |
| **활성 종목** | 3,844개 |
| **분봉 데이터** | 10 GB (41.6M행, 13개월) |
| **일봉 데이터** | 672 MB (260만행, 3년) |
| **키움 테마** | 100 테마, 472 종목 매핑 |
| **키움 체결강도** | 219,892건 (60일, 3,757종목) |
| **유니버스 필터** | **17개** (기존 12 + 신규 5) |
| **엔진 연동 데이터** | **7종** (ohlcv, universe, investor, credit, theme, strength, program) |
