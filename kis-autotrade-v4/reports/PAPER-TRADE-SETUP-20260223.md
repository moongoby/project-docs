# PAPER-TRADE-SETUP 보고서

**날짜:** 2026-02-23  
**서버:** root@211.188.51.113  
**프로젝트:** /root/kis-autotrade-v4  
**브랜치:** phase-2c-command-center  
**우선순위:** P0 (장중 — 15:30 장마감 전 모의 테스트 준비)

---

## 1. 계좌 현황 (마스킹)

| 구분 | 환경변수 키 | 계좌(앞3자리) | 앱키 존재 | 앱시크릿 존재 | API 도메인 | 비고 |
|------|-------------|---------------|-----------|----------------|------------|------|
| 실전 | KIS_REAL_* 등 | 미설정 | N | N | openapi | 실계좌 미사용 |
| 모의1 | KIS_VIRTUAL_* 등 | 247*** | Y | Y | openapivts | 현재 사용 중 |

- **v4_account_config** (DB): virtual 1건, 계좌 앞3자리 501***, base_url 도메인 openapivts.
- 모의계좌는 **.env**의 KIS_VIRTUAL_* 세트로 설정됨. DB v4_account_config는 별도 보조 설정용.
- 실전 계좌는 KIS_REAL_* (앱키/앱시크릿/계좌변수) 미설정 상태.

**모의계좌 미설정 시:**  
한국투자증권 KIS Developers에서 모의투자(개발용) 앱 신청 후 앱키/앱시크릿 발급, 모의 계좌 개설 후 .env에 KIS_VIRTUAL_앱키, KIS_VIRTUAL_앱시크릿, KIS_VIRTUAL_계좌변수 설정.

---

## 2. 모의/실전 전환 방법

- **전환 방식:** 환경변수 **KIS_ACCOUNT_MODE** (값: `virtual` | `real`).
  - `virtual`: KIS_VIRTUAL_* (앱키/앱시크릿/계좌변수) 사용, API 도메인 **openapivts**.
  - `real`: KIS_REAL_* (앱키/앱시크릿/계좌변수) 사용, API 도메인 **openapi**.
- **구현 위치:** `backend/app/core/kis_config.py` — `load_kis_config(mode_override)` / 환경변수 `KIS_ACCOUNT_MODE`.
- **서비스 재시작:** KIS_ACCOUNT_MODE는 프로세스 기동 시 로드되므로, **모드 변경 시 kis-v41-* 서비스 재시작 필요**. (단, CEO 규칙에 따라 재시작은 CEO 승인 후에만 수행.)

---

## 3. DESK별 자금 배분 구조

- **Fund Commander 전용 테이블/설정:** 코드베이스에 `initial_capital`, `fund_alloc`, `desk_capital` 등 DESK별 통합 자금 테이블은 없음.
- **현재 구조:** `strategy_cards` 테이블의 **allocated_amount** (전략 카드별 할당 금액).  
  - 관련: `backend/app/services/strategy_card_service.py`, `backend/app/services/go100/strategy/schemas.py` (allocation_type, allocation_value, allocated_amount).
- **DESK별 100만원 할당:**  
  - 카드 단위 `allocated_amount`로 조정 가능.  
  - DESK당 총 100만원을 쓰려면 해당 DESK의 전략 카드들 allocated_amount 합이 100만원이 되도록 설정하거나, 향후 Fund Commander/desk_capital 설정 도입 필요.
- **config.py:** 자금 배분 관련 필드 없음 (kis_*, db_*, redis_*, app_* 등만 존재).

---

## 4. 분봉 수집 현황

| trade_date | COUNT(*) |
|------------|----------|
| 2026-02-20 | 36,894   |

- **2026-02-21, 02-22, 02-23:** v4_ohlcv_minute에 **데이터 없음**.
- 당일(02-23) 분봉 적재 **없음**.  
  - kis-v41-minute-collector는 월요일 장전 활성화 예정(CONTEXT.md 기준).  
  - 모의 테스트 전 당일 분봉 수집 가동 여부 확인 권장.

---

## 5. 모의 테스트 가동 조건 체크리스트

- [x] 모의계좌 존재 (KIS_VIRTUAL_* 1세트)
- [x] 모의계좌 앱키/앱시크릿 유효 (존재 Y)
- [x] API 도메인 전환 가능 (KIS_ACCOUNT_MODE=virtual → openapivts)
- [ ] 분봉 데이터 최신화 (당일 02-23 없음, 수집기 가동 후 확인)
- [ ] DESK별 자금 배분 설정 완료 (카드별 allocated_amount 또는 신규 정책 적용)
- [ ] 서비스 재시작 없이 전환 가능 (불가 — 모드 변경 시 재시작 필요, CEO 승인 후 수행)

---

## 6. CEO 결정 필요 사항

1. **모의계좌:** 이미 1개 설정됨. 추가 모의계좌 필요 시 KIS Developers 신청.
2. **전환 승인:** 모의 테스트 시 KIS_ACCOUNT_MODE=virtual 유지 및, 필요 시 서비스 재시작 일정 승인.
3. **자금 배분:** DESK별 100만원 실매매 테스트 시, 전략 카드별 allocated_amount 합산 정책 또는 Fund Commander 도입 여부 결정.

---

## 7. DB 무결성

- **strategy_cards:** 62건 유지.
- **v4_positions OPEN:** 5건 유지.
- (확인 시각: 2026-02-23)

---

*보고서 작성: PAPER-TRADE-SETUP Phase B. 시크릿 값 미포함.*
