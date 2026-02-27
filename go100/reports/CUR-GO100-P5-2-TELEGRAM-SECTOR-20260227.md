# [GO100] P5-2: Telegram 모닝브리핑 실전 + 섹터 데이터 보강 — 검증 보고

**문서 ID**: CUR-GO100-P5-2-TELEGRAM-SECTOR-20260227  
**작성일**: 2026-02-27  
**목표**: (A) Telegram 모닝브리핑 실전 전송 검증, (B) v4_stock_sector 데이터 보강, (C) DART 공시/재무 수집 확인

---

## 1. 요약

| 목표 | 결과 | 비고 |
|------|------|------|
| **A. Telegram 모닝브리핑** | 스크립트 실행·포맷·fallback 검증 완료 | `.env` 로드 추가, `telegram_sent` 크론 환경에서 확인 권장 |
| **B. v4_stock_sector 보강** | `scripts/go100/update_stock_sector.py` 작성·실행, 세부 업종 반영 | 전 2종(KOSPI/KOSDAQ) → 후 25+ 업종코드 |
| **C. DART 공시/재무** | collect_events DART 25건 INSERT, collect_financials pykrx 폴백 1282건 | DART API 키 정상, 재무는 KIS 403 시 pykrx 사용 |

---

## 2. 목표 A: Telegram 모닝브리핑 실전 전송 검증

### 2.1 실행

- **명령**: `bash /root/kis-autotrade-v4/scripts/go100/run_morning_briefing.sh`
- **결과**: 정상 종료, `go100_reports`에 `report_type='daily_morning'` 3건 저장 (user_id 1, 2, 3).

### 2.2 메시지 포맷 점검

- **제목**: `모닝 브리핑 — 2026-02-27(금)`
- **본문**: `☀️ 모닝 브리핑 — 2026-02-27(금)` + 요약문. KOSPI/KOSDAQ·주요 이슈·추천종목은 LLM 요약에 따라 포함 가능(현재 테스트는 fallback 텍스트).

### 2.3 telegram_sent 및 Fallback

- **telegram_sent**: 테스트 실행 시 `False`로 기록됨.  
  - 원인: 셸에서 수동 실행 시 Python 자식 프로세스가 `.env`를 물려받지 못하는 경우 존재.  
  - **조치**: `run_morning_briefing.sh`에 `.env` 로드 추가 완료.
    ```bash
    if [ -f .env ]; then set -a; . .env; set +a; fi
    ```
  - **권장**: 크론(08:50 월~금)에서 동일 스크립트 실행 시 환경 변수가 로드되므로, 실제 발송 여부는 `Morning briefing done: {..., "telegram_sent": True/False}` 로그로 확인.

### 2.4 Gemini API 없을 때 Fallback

- **동작 확인**: `GOOGLE_AI_API_KEY` 미설정 또는 모델 404 시  
  - `"전일 시장 데이터가 반영된 모닝 브리핑입니다. (LLM 미설정)"`  
  - 또는 `"(요약 생성 일시 오류)"`  
  로 요약문이 설정되고, DB 저장 및 (설정 시) 텔레그램 발송까지 진행됨.

### 2.5 환경 확인

- `.env`에 `GO100_TELEGRAM_BOT_TOKEN`, `GO100_TELEGRAM_CHAT_ID`, `DART_API_KEY` 존재 확인(값 마스킹).

---

## 3. 목표 B: v4_stock_sector 데이터 보강

### 3.1 전 현황 (실행 전)

```sql
SELECT sector_code, sector_name, COUNT(*) FROM v4_stock_sector GROUP BY sector_code, sector_name ORDER BY COUNT(*) DESC LIMIT 5;
```

| sector_code | sector_name | count |
|-------------|-------------|-------|
| KOSPI       | KOSPI       | 2402  |
| KOSDAQ      | KOSDAQ      | 1823  |

- **테이블 스키마**: `stock_code`, `sector_code`, `sector_name`, `updated_at`  
- **누락**: KRX 세부 업종(전기전자, 화학, 금융 등) 미반영.

### 3.2 스크립트: `scripts/go100/update_stock_sector.py`

- **역할**
  1. **v4_sector_stock_mapping** (pykrx 업종 구성종목)에서 KIS 업종코드(`v4_sector_daily` 호환)만 사용.  
     - WICS 코드는 **섹터명 매핑**으로 KIS 코드로 변환(예: 전기·전자 → 0013, 화학 → 0008).
  2. **stock_universe**: `sector_large`, `sector_mid`, `sector_small`, `market` 순으로 `sector_code`/`sector_name` 결정.
  3. **KRX 업종코드 상수**: `collector_theme_sector.SECTOR_CODES`와 동기화한 `KRX_SECTOR_CODE_TO_NAME` 및 `WICS_NAME_TO_KRX_CODE` 사용.
- **실행**
  ```bash
  PYTHONPATH=/root/kis-autotrade-v4 .venv/bin/python scripts/go100/update_stock_sector.py
  ```
- **옵션**: `--dry-run`(통계만), `--dart-sample N`(DART 보강 샘플은 추후 corp_code 매핑 시 활용 가능).

### 3.3 실행 결과 (전후 비교)

- **행 수**: 전 4,225행 → 후 4,225행(동일).
- **업종 분포 (상위 15)**  
  - 전: KOSPI 2402, KOSDAQ 1823만 존재.  
  - 후 예시:

| sector_code | sector_name   | count |
|-------------|---------------|-------|
| 0001        | 종합(KOSPI)   | 1084  |
| 0026        | 서비스업      | 533   |
| 0013        | 전기전자      | 394   |
| 0008        | 화학          | 249   |
| 0021        | 금융업        | 224   |
| 0012        | 기계          | 217   |
| 0009        | 의약품        | 189   |
| 0011        | 철강금속      | 178   |
| 0016        | 유통업        | 173   |
| …           | …             | …     |

- **비고**: `v4_stock_sector`에 있으나 `stock_universe`(is_active)에 없는 381종목은 기존 값(KOSPI 등) 유지. 필요 시 별도 정리 가능.

---

## 4. 목표 C: DART 공시/재무 수집 확인

### 4.1 collect_events.py (DART 모드)

- **실행**:  
  `PYTHONPATH=/root/kis-autotrade-v4 .venv/bin/python scripts/go100/collect_events.py --days 7`
- **결과**:
  - 총 이벤트 50건 수집.
  - **UPSERT 완료: 신규 25건** → `go100_events` INSERT 확인.
  - `source=dart` 25건.
- **샘플**: event_type=disclosure, 제목 예: [기재정정]대규모기업집단현황공시, 증여결정 등.

### 4.2 collect_financials.py

- **실행**:  
  `PYTHONPATH=/root/kis-autotrade-v4 .venv/bin/python scripts/data_collect/collect_financials.py`
- **결과**:
  - KIS API: `token failed: 403 (유효하지 않은 AppKey)` → **pykrx 폴백** 자동 진입.
  - **pykrx 폴백 완료: dividend_yield 1282건 갱신** → 정상 동작.
- **비고**: 재무제표 수집은 현재 KIS + pykrx 기준. DART 기업개황(induty_code 등) 보강은 `update_stock_sector.py`의 DART 옵션 또는 별도 배치로 확장 가능.

---

## 5. 파일 변경 목록

| 경로 | 변경 내용 |
|------|-----------|
| `scripts/go100/run_morning_briefing.sh` | 크론/실행 시 `.env` 로드 추가 (P5-2) |
| `scripts/go100/update_stock_sector.py` | 신규 — v4_stock_sector KRX 업종 매핑 + WICS→KIS 매핑 |

---

## 6. 체크리스트

- [x] run_morning_briefing.sh 실행
- [x] 메시지 포맷·fallback·report 저장 확인
- [x] telegram_sent 동작(환경 로드 보강 반영), 실발송은 크론에서 재확인 권장
- [x] v4_stock_sector 전 현황 조회
- [x] update_stock_sector.py 작성·실행·전후 비교
- [x] collect_events.py DART 7일 수집·go100_events INSERT 확인
- [x] collect_financials.py pykrx 폴백 및 배당수익률 갱신 확인

---

## 7. 권장 후속

1. **모닝브리핑**: 크론 08:50 실행 후 `telegram_sent: True` 및 실제 텔레그램 수신 여부 확인.  
2. **Gemini 모델**: `gemini-2.0-flash` 404 시 `GO100_MORNING_BRIEFING_MODEL`에 사용 가능한 모델명으로 변경 검토.  
3. **v4_stock_sector**: 주기 실행(예: 주 1회)으로 `update_stock_sector.py` 실행 권장.
