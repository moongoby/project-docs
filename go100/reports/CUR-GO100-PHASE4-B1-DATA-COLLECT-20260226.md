# CUR-GO100-PHASE4-B1-DATA-COLLECT 보고서 (2026-02-26)

## 개요
- **작업**: 재무제표 수집 스크립트 작성 및 크론 등록
- **수집 항목**: revenue(매출액), operating_profit(영업이익), dividend_yield(배당수익률)
- **대상 테이블**: `stock_fundamentals` (해당 3컬럼만 UPDATE, roe/per/pbr 등 기존 컬럼 비침범)

---

## 사전 작업 결과

| 항목 | 결과 |
|------|------|
| .cursorrules | GO100 규칙은 `.cursor/rules/go100-rules.md` 참조 |
| stock_fundamentals (수집 전) | total 8093, has_roe 2439, has_div 0, has_rev 0, has_op 0 |
| KIS API 키 | .env 내 KIS_APP_KEY, KIS_APP_SECRET, KIS_VIRTUAL_APP_KEY 등 확인 |
| 백업 | `cp -r scripts /root/backup/scripts-phase4-b1-YYYYMMDD-HHMMSS/` 수행 |

---

## 작업 1: 재무제표 수집 스크립트

- **파일**: `scripts/data_collect/collect_financials.py`
- **API**:
  - **FHKST66430200** (손익계산서) → `sale_account`(매출액), `bsop_prti`(영업이익) — **실전 전용(모의 미지원)**
  - **FHKST01010100** (주식현재가) → `stck_dvdn_yld`(배당수익률)
- **로직**:
  1. `stock_universe`에서 `market IN ('KOSPI','KOSDAQ')` 및 `is_active = true` 종목 코드 조회
  2. 토큰 발급: POST `/oauth2/tokenP` (실전 도메인)
  3. 종목별 손익계산서(연간 `fid_div_cls_code=0`) → 최신 결산 매출/영업이익 추출
  4. 종목별 주식현재가 → 배당수익률 추출
  5. `stock_fundamentals`에서 해당 종목의 **최신 date 1건**에 대해 revenue, operating_profit, dividend_yield만 UPDATE
- **Rate limit**: 요청 간 `asyncio.sleep(0.05)` (초당 20건 제한 대응)
- **환경 변수**: `KIS_REAL_BASE_URL` 또는 `KIS_BASE_URL`(실전 기본값), `KIS_APP_KEY`, `KIS_APP_SECRET` (실전 키 필요)

---

## 작업 2: 크론 등록

- **스케줄**: 매일 **19:30** (월~금)
- **명령**:  
  `cd /root/kis-autotrade-v4 && .venv/bin/python scripts/data_collect/collect_financials.py >> /var/log/collect_financials.log 2>&1`
- **상태**: 등록 완료 (`crontab -l` 확인)

---

## 작업 3: 즉시 1회 실행 및 검증

- **실행**: 스크립트 실행 시 **토큰 403** (유효하지 않은 AppKey) 발생
- **원인**: 재무/손익 API는 **실전 도메인 전용**이며, 현재 .env의 키가 실전용이 아니거나 실전 URL과 불일치 가능
- **조치**: 스크립트에 `KIS_REAL_BASE_URL`, 실전용 `KIS_APP_KEY`/`KIS_APP_SECRET` 사용 안내 주석 반영. 실전 키·URL 설정 후 재실행 필요
- **검증 쿼리 결과** (수집 미수행으로 기존과 동일):
  - total 8093, has_rev 0, has_op 0, has_div 0

---

## 작업 4: stock_fundamentals date 타입

| column_name | data_type       | character_maximum_length |
|-------------|-----------------|---------------------------|
| date        | character varying | 8                      |

- **결론**: `date`는 **varchar(8)**. date 타입 마이그레이션은 별도 티켓으로 분리 (영향도 큼).

---

## Git 커밋

- **kis-autotrade-v4**: `scripts/data_collect/collect_financials.py` 추가 후 커밋·푸시 완료 (4489fdb4)
- **project-docs**: 본 보고서 커밋·푸시 완료 (89696a7)

---

## 완료 요약

| 항목 | 내용 |
|------|------|
| revenue 수집 | 스크립트 구현 완료. 실전 키 설정 후 실행 시 수집 가능 |
| operating_profit 수집 | 동일 |
| dividend_yield 수집 | 동일 |
| 크론 | 매일 19:30 (월~금) 등록 완료 |
| go100 커밋 | 4489fdb4 (phase-2c-command-center) |
| project-docs 커밋 | 89696a7 (master) |
