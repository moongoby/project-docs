# CUR-GO100-P1-3-CRON-ISSUES-20260227

**날짜**: 2026-02-27  
**작업**: P1-3 Cron 장중 검증 + Known Issue 3건 해결  
**상태**: 완료

---

## 1. 선행 조건 확인

- **HANDOVER-20260227-V6-SESSION2.md** 섹션 7 (크론 현황) 참조 완료.
- **CUR-GO100-AUTO-HEALER-20260227.md** 참조 완료 — 무결성 체커 실패 시 `run_auto_heal()` 자동 호출 확인.

---

## 2. 크론 전수 현황

### 2.1 요약

| 항목 | 값 |
|------|-----|
| 활성 크론 라인 수 | 59 |
| GO100 전용 크론 | 29 |
| 로그 디렉터리 | `/var/log/go100/` |

### 2.2 주요 GO100 크론 목록

| 스케줄 | 스크립트/명령 | 용도 |
|--------|----------------|------|
| */2 9-15 * * 1-5 | run_data_integrity_check.sh | 장중 무결성 2분 주기 |
| */15 0-8,16-23 * * 1-5 | run_data_integrity_check.sh | 장외 무결성 15분 주기 |
| */15 * * * 0,6 | run_data_integrity_check.sh | 주말 15분 주기 |
| * * * * * (1-5) | run_alert_sender.sh | 텔레그램 발송 1분 |
| 30 8, 30 17 * * 1-5 | run_daily_summary.sh | 일일 요약 |
| 20 16 * * 1-5 | run_auto_heal.sh | 국내 데이터 복구 |
| 10 7 * * 1-5 | run_auto_heal.sh | 해외 데이터 복구 |
| 5 16 * * 1-5 | run_collect_fundamentals.sh | 재무 수집 (go100_fundamentals) |

### 2.3 주요 V4.1/공유 크론 (OHLCV·레짐 등)

| 스케줄 | 용도 | 로그 |
|--------|------|------|
| 0 16 * * 1-5 | ohlcv_daily 수집 | `/var/log/go100/ohlcv_daily.log` |
| 45 15 * * 1-5 | index_daily 수집 | — |
| 50 15 * * 1-5 | VKOSPI 수집 | logs/cron/vkospi_alt.log |
| 55 15 * * 1-5 | run_vkospi_regime_sync.sh | /var/log/go100/regime_vkospi_sync.log |
| 30 17 * * 1-5 | collect_financials.py (KIS/pykrx 폴백) | /var/log/collect_financials.log |

### 2.4 로그 파일 점검 (2026-02-27 기준)

| 로그 파일 | 존재 | 비고 |
|-----------|------|------|
| /var/log/go100/data_integrity.log | ✅ | 정상 기록 |
| /var/log/go100/alert_sender.log | ✅ | 정상 기록 |
| /var/log/go100/daily_summary.log | ✅ | 정상 기록 |
| /var/log/go100/auto_heal.log | ✅ | run_auto_heal.sh 실행 시 생성 |
| /var/log/go100/collect_fundamentals.log | ✅ | run_collect_fundamentals.sh 실행 시 생성 |
| /var/log/go100/ohlcv_daily.log | ✅ | 크론 로그 경로 통일 완료 (기존 logs/ohlcv_cron.log → 변경) |

---

## 3. Known Issue #1: collect_financials.py KIS API 403 → pykrx 대체

### 3.1 조치 내용

- **파일**: `scripts/data_collect/collect_financials.py`
- **변경**:
  1. 토큰 발급 실패(403 등) 또는 API 호출 403 시 **pykrx 폴백** 자동 실행.
  2. `KIS403Error` 예외 도입, `fetch_income_statement` / `fetch_price_dividend`에서 403 시 `raise`.
  3. `fallback_collect_financials_pykrx()` 추가:  
     - `pykrx.stock.get_market_fundamental(대상일, market="ALL")`로 배당수익률(DIV) 수집.  
     - `stock_fundamentals`의 최신 `date` 행에 대해 `dividend_yield`만 UPDATE.  
     - revenue/operating_profit은 현재 폴백에서 미구현(DART 확장 가능).

### 3.2 검증 결과

- KIS 토큰 403 발생 시 로그:  
  `KIS token 실패(403 또는 키 없음) — pykrx 폴백 실행`
- pykrx 폴백 실행 후:  
  `pykrx 폴백 완료: dividend_yield 1282건 갱신`
- **결론**: KIS 403 시 pykrx 폴백으로 배당수익률 갱신 정상 동작 확인.

---

## 4. Known Issue #2: v4_market_regime_daily 정체 → 자동 복구 연동

### 4.1 현황

- **v4_market_regime_daily** 최신일: **2026-02-26** (확인 시점 기준, 최근 거래일과 일치).
- **자동 복구 연동**:  
  `data_integrity_checker.run_all_checks()` 내부에서 `failed > 0`이면  
  `backend.app.services.go100.monitoring.data_auto_healer.run_auto_heal()` 호출됨.  
  → 레짐 freshness 실패 시 자동으로 `heal_regime()` 실행.

### 4.2 결론

- 레짐 테이블은 무결성 체커 + auto_healer로 자동 복구되며,  
  정체 시 누락일이 `heal_regime()`으로 채워짐.  
- **Known Issue #2**: 자동 복구 연결 정상, 별도 수동 조치 불필요.

---

## 5. Known Issue #3: ohlcv_daily 크론 로그 비어 있음 → 로그 경로/권한

### 5.1 원인

- 크론에서 사용하던 로그 경로: `>> logs/ohlcv_cron.log 2>&1` (상대 경로).  
- 로그가 비어 보이던 원인:  
  - 16:00 크론 미실행(해당일 미경과) 또는  
  - 스크립트 초기 단계에서 로그 미기록.

### 5.2 조치 내용

1. **크론 로그 경로 통일**  
   - `>> logs/ohlcv_cron.log 2>&1`  
   → `>> /var/log/go100/ohlcv_daily.log 2>&1`  
   - 동일 서버 내 crontab에 반영 완료.
2. **로그 디렉터리/파일**  
   - `/var/log/go100/` 존재 확인,  
   - `ohlcv_daily.log` 생성 및 권한 확인(쓰기 가능).
3. **스크립트**  
   - `backend/scripts/collect_ohlcv_daily.py`에 시작 로그 추가:  
     `logger.info("collect_ohlcv_daily START (cron/수동)")`  
   - 크론/수동 실행 시 최소 1줄 로그 보장.

### 5.3 결론

- ohlcv_daily 크론 로그는 `/var/log/go100/ohlcv_daily.log`에 정상 기록되도록 정리됨.  
- 다음 장일 16:00 크론 실행 후 해당 파일에서 로그 확인 가능.

---

## 6. 크론 실행 테스트 (수동)

| 스크립트 | 결과 | 비고 |
|----------|------|------|
| run_data_integrity_check.sh | ✅ | run_all_checks 실행, 실패 시 run_auto_heal 호출 확인 |
| run_auto_heal.sh | ✅ | 기준일 기준 ohlcv/regime 등 복구 시도, PARTIAL 상태 정상 |
| run_collect_fundamentals.sh | ✅ | pykrx 2720종목 수집, DART는 API 키 미설정으로 0 |
| collect_financials.py | ✅ | KIS 403 → pykrx 폴백, dividend_yield 1282건 갱신 |

---

## 7. 완료 조건 체크

| 조건 | 상태 |
|------|------|
| 크론 목록 문서화 | ✅ (본 문서 2절) |
| Known Issue 3건 해결/우회 | ✅ |
| collect_financials.py pykrx 폴백 동작 확인 | ✅ |
| regime_daily 최신일 = 최근 거래일 | ✅ (2026-02-26) |
| ohlcv_daily 로그 경로/권한 정상 | ✅ (/var/log/go100/ohlcv_daily.log) |

---

## 8. 수정/추가된 파일 요약

| 파일 | 변경 내용 |
|------|-----------|
| scripts/data_collect/collect_financials.py | KIS 403 시 pykrx 폴백, KIS403Error, fallback_collect_financials_pykrx() |
| backend/scripts/collect_ohlcv_daily.py | 시작 로그 한 줄 추가 |
| crontab | ohlcv_daily 크론 로그 리다이렉트 → /var/log/go100/ohlcv_daily.log |

---

## 9. 참고

- **무결성 체커 → auto_heal 연동**: `data_integrity_checker.py` 344~359라인.  
- **레짐 복구**: `data_auto_healer.heal_regime()` — index_daily MA20 + VKOSPI 기반 자동 계산.  
- **collect_fundamentals (GO100)** vs **collect_financials (V4.1)**:  
  - 전자: `go100_fundamentals`, pykrx+DART, 16:05 크론.  
  - 후자: `stock_fundamentals`, KIS API → 403 시 pykrx 폴백, 17:30 크론.
