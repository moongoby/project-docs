# Phase3 Track-B: 외부 데이터 수집 인프라 — 완료 보고서

**작업일시**: 2026-02-25 (화) KST  
**작업자**: Cursor AI  
**브랜치**: phase-3-autonomous  
**승인**: 자체승인 (신규 테이블 + 신규 스크립트만, 기존 0 영향)

---

## 1. 신규 테이블 3개 생성 결과

| 테이블명 | 용도 | 상태 |
|----------|------|------|
| `data_fx_daily` | 환율 일별 (USD/KRW, JPY/KRW, EUR/KRW, CNY/KRW) | ✅ CREATE 완료 |
| `data_global_index_daily` | 해외 지수 일별 (S&P500, NASDAQ, Dow, HSI, Nikkei, 상해) | ✅ CREATE 완료 |
| `data_crypto_daily` | 코인 일별 (BTC, ETH) | ✅ CREATE 완료 |

- DDL: `sudo -u postgres psql -d kisautotrade -c "CREATE TABLE ..."` 로 각각 실행 완료.
- 기존 테이블/컬럼 수정 없음.

---

## 2. 수집 스크립트 3개 구현 결과

| 스크립트 | 소스 | 대상 테이블 | 옵션 |
|----------|------|-------------|------|
| `scripts/collect_fx_daily.py` | yfinance (USDKRW=X, JPYKRW=X, EURKRW=X, CNYKRW=X) | data_fx_daily | --days 7 (기본), --full (1년) |
| `scripts/collect_global_index.py` | yfinance (^GSPC, ^IXIC, ^DJI, ^HSI, ^N225, 000001.SS) | data_global_index_daily | --days 7 (기본), --full (1년) |
| `scripts/collect_crypto_daily.py` | CoinGecko API (requests, bitcoin/ethereum) | data_crypto_daily | --days 7 (기본), --full (365일) |

- 공통: argparse, psycopg2 직접연결, .env 로드, UPSERT(ON CONFLICT DO UPDATE), logging.
- 패키지: `yfinance` 설치 완료 (pip). CoinGecko는 requests만 사용 (pycoingecko 미사용).

---

## 3. cron 등록 결과

- **파일 위치 (배포용)**: 프로젝트 내 `etc/cron.d/external_data_collection` 생성.
- **실제 서버 반영**: 배포 시 아래로 복사 권장.
  ```bash
  sudo cp /root/kis-autotrade-v4/etc/cron.d/external_data_collection /etc/cron.d/
  ```

| 작업 | 스케줄 | 로그 |
|------|--------|------|
| 환율 | 매 평일 18:00 KST | /var/log/fx_daily.log |
| 해외 지수 | 매 평일 09:30 KST | /var/log/global_index.log |
| 코인 | 매일 08:00 KST (주말 포함) | /var/log/crypto_daily.log |

---

## 4. 백필 실행 결과 (수집 건수)

- 실행: `python scripts/collect_fx_daily.py --full`, `collect_global_index.py --full`, `collect_crypto_daily.py --full`

| 테이블 | 건수 | 비고 |
|--------|------|------|
| data_fx_daily | 772 | 4개 통화쌍 × 약 193일분 |
| data_global_index_daily | 1,485 | 6개 지수 × 약 247일분 |
| data_crypto_daily | 730 | BTC+ETH 365일분 |

검수 쿼리:
```sql
SELECT 'data_fx_daily' as tbl, count(*) FROM data_fx_daily
UNION ALL SELECT 'data_global_index_daily', count(*) FROM data_global_index_daily
UNION ALL SELECT 'data_crypto_daily', count(*) FROM data_crypto_daily;
```

---

## 5. 전체 데이터 인벤토리 갱신 (기존 + 신규)

| 구분 | 테이블 | 건수 (2026-02-25 기준) |
|------|--------|------------------------|
| 기존 활용 | v4_vkospi_daily | 1,506 (VIX 대용) |
| 기존 활용 | index_daily | 1,476 (KOSPI/KOSDAQ/200) |
| 기존 활용 | v4_market_regime_daily | 819 (레짐) |
| 기존 활용 | v4_market_calendar | 129 (캘린더) |
| **신규** | **data_fx_daily** | **772** |
| **신규** | **data_global_index_daily** | **1,485** |
| **신규** | **data_crypto_daily** | **730** |

---

## 6. 기존 시스템 영향도

- **영향 없음.**  
  - 기존 테이블/스키마/서비스 수정 없음.  
  - 신규 테이블 3개, 신규 스크립트 3개, 신규 cron 파일만 추가.  
  - 기존 서비스 재시작 없음.

---

## 요약

- 신규 테이블 3개 생성 완료.
- 수집 스크립트 3개 구현 및 1년/365일 백필 완료.
- cron 파일은 repo 내 `etc/cron.d/external_data_collection` 에 포함; 배포 시 `/etc/cron.d/` 로 복사 필요.
- 보고서 위치:  
  - 로컬: `/root/kis-autotrade-v4/report/PHASE3-TRACK-B-EXTERNAL-DATA-20260225.md`  
  - project-docs: `/root/project-docs/go100/reports/PHASE3-TRACK-B-EXTERNAL-DATA-20260225.md` (동기화 후).
