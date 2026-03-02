# CUR-GO100-EXTERNAL-DATA-001 보고서

**작업 ID**: CUR-GO100-EXTERNAL-DATA-001  
**작성일**: 2026-02-25 (KST)  
**브랜치**: feat/CUR-GO100-EXTERNAL-DATA-001 → phase-2c-command-center  
**서버**: root@[SERVER-IP]  
**DB**: kisautotrade (PostgreSQL)

---

## 1. 사전 백업

- **경로**: `/root/backup/pre-external-data-schema-20260225-090532.sql`
- **방식**: `pg_dump -U kis_admin -h localhost -d kisautotrade --schema-only`
- **상태**: 완료

---

## 2. DDL 실행

지시서 DDL 실행 시 **테이블 3개는 이미 존재**하여 `CREATE TABLE IF NOT EXISTS`로 스킵됨.  
기존 스키마는 아래와 같음 (컬럼명이 지시서와 상이: `date`/`currency_pair` 등).

| 테이블 | UNIQUE | 비고 |
|--------|--------|------|
| data_fx_daily | (currency_pair, date) | open, high, low, close, change_pct, source |
| data_global_index_daily | (index_code, date) | index_name, open, high, low, close, volume, change_pct, source |
| data_crypto_daily | (symbol, date) | open, high, low, close, volume, market_cap, change_pct, source |

- 인덱스 `idx_fx_daily_pair_date` 등은 소유권 이슈로 생성 실패 (테이블 기존 소유자 유지).
- 수집 스크립트는 **현재 DB 스키마에 맞춰** 동작하도록 구현됨.

---

## 3. 수집 스크립트 구현

| 파일 | 소스 | 대상 테이블 | 옵션 |
|------|------|-------------|------|
| scripts/collect_fx_daily.py | yfinance (USDKRW=X, JPYKRW=X, EURKRW=X, CNYKRW=X) | data_fx_daily | --days 5 (기본), --full (1년) |
| scripts/collect_global_index.py | yfinance (^GSPC→SPX, ^IXIC→NDX, ^DJI→DJI, ^N225→NIKK, ^HSI→HSI, 000001.SS→SSEC, ^VIX→VIX) | data_global_index_daily | --days 5 (기본), --full (1년) |
| scripts/collect_crypto_daily.py | CoinGecko API (bitcoin, ethereum, ripple, solana) | data_crypto_daily | --days 5 (기본), --full (365일) |

- **공통**: 헤더 `# CUR-GO100-EXTERNAL-DATA-001, 2026-02-25`, argparse, psycopg2, .env 로드, UPSERT(ON CONFLICT DO UPDATE), logging.
- **암호화폐**: 코인 간 `time.sleep(1.5)` 적용 (CoinGecko rate limit 대응).

---

## 4. 패키지 설치

- `yfinance`, `pycoingecko` 설치 완료 (pip, .venv).
- crypto 스크립트는 CoinGecko REST API를 **requests**로 호출 (market_chart/range).

---

## 5. cron 등록

- **프로젝트 내**: `docs/cron/external_data_collection.cron`
- **시스템 반영**: `sudo cp .../external_data_collection.cron /etc/cron.d/external_data_collection` 실행 완료.

| 작업 | 스케줄 | 로그 |
|------|--------|------|
| 환율 | 월–금 18:00 KST | /var/log/collect_fx.log |
| 해외 지수 | 월–금 09:30 KST | /var/log/collect_global_index.log |
| 암호화폐 | 매일 08:00 KST | /var/log/collect_crypto.log |

---

## 6. 초기 백필 실행 결과

| 테이블 | 행 수 | 비고 |
|--------|-------|------|
| data_fx_daily | 776 | 1년 백필 (USDKRW, JPYKRW, EURKRW, CNYKRW) |
| data_global_index_daily | 2,724 | 1년 백필 (SPX, NDX, DJI, NIKK, HSI, SSEC, VIX) |
| data_crypto_daily | 731 | 기존 + BTC 위주 수집 (CoinGecko 429 시 일부 코인 스킵) |

- **검증 쿼리** (실행 완료):
  ```sql
  SELECT 'data_fx_daily' AS tbl, COUNT(*) FROM data_fx_daily
  UNION ALL SELECT 'data_global_index_daily', COUNT(*) FROM data_global_index_daily
  UNION ALL SELECT 'data_crypto_daily', COUNT(*) FROM data_crypto_daily;
  ```

---

## 7. 에러·특이 사항

- **CoinGecko**: 무료 구간에서 429 Too Many Requests 발생 가능. BTC 수집은 정상, ETH/XRP/SOL은 호출 간격(1.5s) 확대 또는 API 키 사용 시 안정화 권장.
- **서비스 재시작**: 없음 (kis-v41-* 미재시작).
- **헬스**: `curl -s http://localhost:8002/health` → status ok, database/redis connected.

---

## 8. 커밋·푸시

- **커밋**: `feat: CUR-GO100-EXTERNAL-DATA-001 - FX/해외지수/크립토 수집 + 1년 백필 + cron`
- **브랜치**: phase-2c-command-center에 반영 후 `git push origin phase-2c-command-center` 완료.

---

## 9. 수정·신규 파일 요약

| 구분 | 경로 |
|------|------|
| 신규 | scripts/collect_fx_daily.py |
| 신규 | scripts/collect_global_index.py |
| 신규 | scripts/collect_crypto_daily.py |
| 신규 | docs/cron/external_data_collection.cron |
| DB | data_fx_daily, data_global_index_daily, data_crypto_daily (기존 테이블 사용) |

- 보호 파일 변경 없음. 백엔드/프론트 코드 변경 없음.
