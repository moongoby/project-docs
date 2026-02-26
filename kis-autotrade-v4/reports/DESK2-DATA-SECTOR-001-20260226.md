# DESK2-DATA-SECTOR-001 업종 데이터 수집 보고서

**작성일**: 2026-02-26  
**프로젝트**: KIS AutoTrade V4.1, 브랜치 phase-2c-command-center  
**목표**: D1 업종 일봉, D2 종목-업종 매핑, D6 상관계수 매트릭스 수집·적재 (Cursor A)

---

## 1. 수행 내용

| 단계 | 내용 | 스크립트/리소스 |
|------|------|------------------|
| A-1 | 환경 확인, 신규 테이블 생성 | `run_desk2_sector_a1.sh`, `DESK2_DATA_COLLECT_001_tables.sql` |
| A-2 | 업종 지수 일봉 수집 (pykrx) | `collect_sector_daily.py` |
| A-3 | 종목-업종 매핑 수집 | `collect_sector_mapping.py` |
| A-4 | 상관계수 산출 (D1+D2 완료 후) | `calc_sector_correlation.py` |

---

## 2. 구현 파일 경로 (레포 기준)

| 구분 | 경로 |
|------|------|
| 마이그레이션 | `backend/migrations/DESK2_DATA_COLLECT_001_tables.sql` |
| A-1 실행 스크립트 | `scripts/data_collect/run_desk2_sector_a1.sh` |
| 업종 일봉 수집 | `scripts/data_collect/collect_sector_daily.py` |
| 종목-업종 매핑 | `scripts/data_collect/collect_sector_mapping.py` |
| 상관계수 산출 | `scripts/data_collect/calc_sector_correlation.py` |
| VI 이력 수집 (Cursor B) | `scripts/data_collect/collect_vi_history.py` |
| 본 보고서 (코드레포) | `report/DESK2-DATA-SECTOR-001-20260226.md` |
| 본 보고서 (문서레포) | `kis-autotrade-v4/reports/DESK2-DATA-SECTOR-001-20260226.md` |

---

## 3. 신규 테이블

- **v4_sector_stock_mapping**: 종목코드–업종코드 매핑, 시총순위
- **v4_sector_correlation**: 동일 업종 내 종목쌍 60일 롤링 상관계수
- **v4_vi_history**: VI 발동 이력 (Cursor B용, A-1에서 생성)

---

## 4. 검증 쿼리

```sql
SELECT market, COUNT(DISTINCT sector_code) AS sectors, COUNT(*) AS rows,
       MIN(trade_date) AS min_date, MAX(trade_date) AS max_date
FROM v4_sector_price GROUP BY market;

SELECT market, COUNT(DISTINCT sector_code) AS sectors,
       COUNT(DISTINCT stock_code) AS stocks, COUNT(*) AS mappings
FROM v4_sector_stock_mapping GROUP BY market;

SELECT sector_code, COUNT(*) AS pairs FROM v4_sector_correlation GROUP BY sector_code;

-- 최종 건수
SELECT 'v4_sector_price' AS tbl, COUNT(*) FROM v4_sector_price
UNION ALL SELECT 'v4_sector_stock_mapping', COUNT(*) FROM v4_sector_stock_mapping
UNION ALL SELECT 'v4_sector_correlation', COUNT(*) FROM v4_sector_correlation;
```

---

## 5. C6(업종) 활성화 여부

- **조건**: `v4_sector_price > 0` AND `v4_sector_stock_mapping > 0`
- **결과**: A-2·A-3 실행 후 위 검증 쿼리로 확인

---

## 6. 비고

- `v4_sector_price`는 기존 스키마(close_price, volume, trade_amount 등)만 사용. open/high/low 미수집.
- 상관계수는 `ohlcv_daily` 60일 close 기반 일별 수익률 피어슨 상관계수.
- 보고서: 코드레포 `report/` 및 문서레포 `kis-autotrade-v4/reports/` 반영 후 push.
