# CUR-GO100-AUTO-HEALER-20260227

**날짜**: 2026-02-27  
**상태**: 구현 완료

## 개요
백억이 자율 복구 엔진. 데이터 문제 감지 시 스스로 조치하고 최신화.

## 복구 흐름
```
무결성 체커 (2분/15분) → FAIL 감지 → 자율 복구 엔진 호출
  → 1차: DB 내부 보정
  → 2차: pykrx (무료, 즉시)
  → 3차: FinanceDataReader
  → 4차: KIS API (증권사)
  → 5차: 수동 조치 알림
  → 복구 후 재검증
  → 텔레그램 보고 (성공/실패)
```

## 테이블별 복구 전략

| 테이블 | 1차 | 2차 | 3차 |
|--------|-----|-----|-----|
| ohlcv_daily | pykrx (전종목) | KIS API (종목별) | 수동 |
| index_daily | pykrx (KOSPI/KOSDAQ/KOSPI200) | - | 수동 |
| v4_vkospi_daily | pykrx | FDR | DATA_GO_KR |
| v4_investor_daily | pykrx | - | 수동 |
| v4_market_regime_daily | 자동 계산 (MA20+VKOSPI) | - | - |
| go100_global_market | v4_vkospi_daily 동기화 | - | - |
| WS 서비스 | systemctl restart | - | 수동 |

## 크론 스케줄
- 무결성 체커 내 자동 호출 (장중 2분, 장외 15분)
- 16:20 Mon-Fri: V4.1 수집 완료 후 전용 복구
- 07:10 Mon-Fri: 해외 데이터 수집 후 복구

## 파일
- `backend/app/services/go100/monitoring/data_auto_healer.py`
- `scripts/go100/run_auto_heal.sh`
- `backend/app/services/go100/monitoring/data_integrity_checker.py` (수정: auto_heal 연동)

## 스키마 대응 (적용 사항)
- `DATABASE_URL_SYNC`의 `postgresql+psycopg2://` → `postgresql://` 자동 치환
- `index_daily.date`, `v4_vkospi_daily.date` 등 varchar(8) 컬럼은 `YYYYMMDD` 문자열로 INSERT/비교
- `v4_investor_daily`: 최신일 조회는 `MAX(trade_date)` 사용
- `go100_global_market`: `symbol` 없음, `data_date`당 1행 기준으로 VKOSPI 동기화 (vkospi 컬럼 없으면 SKIP)
- WS 테이블 컬럼 오류 시 rollback 후 계속 진행
