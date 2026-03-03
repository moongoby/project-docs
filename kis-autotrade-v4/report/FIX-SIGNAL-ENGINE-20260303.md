# 신호 생성 엔진 정밀 수정 보고서

**작업일**: 2026-03-03
**담당**: Claude
**작업 범위**: legacy webapp 거래 엔진 전면 분석 및 복구

---

## 1. 실매매 실적 확인 (사실 수정)

이전 보고에서 "오늘 실주문 0건" 등 오류 표현이 있었음. 실제 현황:

| 테이블 | 내용 | 확인 |
|--------|------|------|
| `autotrade_positions` | **실KIS 주문번호** (0000001837 등) 80건 | 2026-02-06 ~ 02-13 |
| `moongoby@naver.com` (74032243, is_production=true) | **34건 실계좌 실매매** | 확인 완료 |
| `moongoby@gmail.com` (50160697, VTS) | 25건 VTS 매매 | 확인 완료 |
| `moong123@naver.com` (50160711, VTS) | 21건 VTS 매매 | 확인 완료 |

**레거시 실매매 테스트 완료: 2026-02-06 ~ 2026-02-13, 총 80건 (실계좌 34건 포함)**

---

## 2. Feb 13 이후 거래 중단 원인 (정밀 분석)

### 원인 1: KIS VTS 서버 500 에러 (외부 요인)
```
openapivts.koreainvestment.com:29443 → 500 Server Error (EGW00201 초당 거래건수 초과)
```
Feb 13 이후 KIS VTS 서버 장애. 모든 VTS API 호출 실패.

### 원인 2: 재시도 로직 폭발 (내부 버그)
`retry_on_error_current_price(max_retries=5, backoff_factor=3)`:
- 500 에러 발생 시 1 + 3 + 9 + 27 = **40초 대기** per 종목
- 50종목 × 40초 × 3 VTS 사용자 = **6,000초** → 60초 타임아웃 폭발

### 원인 3: 신호 생성 타임아웃 → 신호 없음 → 매매 없음
`unified_trading_scheduler.py`의 `timeout=60`으로 60초마다 종료.
신호 생성 실패 → `trading_signals` 신규 삽입 없음 → 자동매매 "신호 없음"

---

## 3. 오늘 수정 사항 전체

### 3.1 PRAGMA/boolean 오류 수정 (오전)
| 파일 | 수정 내용 |
|------|----------|
| `realtime_signal_generator_fixed.py` | `PRAGMA busy_timeout=30000` 제거 |
| `realtime_general_market_auto_trade.py` | `PRAGMA busy_timeout=30000` 제거 |
| 양 파일 | `is_active = 1` → `= true` (PostgreSQL boolean) |
| 양 파일 | `decrypt_value(kis_config.app_key)` 복호화 추가 |

### 3.2 타임아웃 확장
- `unified_trading_scheduler.py:161`: `timeout=60` → `timeout=240`

### 3.3 VTS fail-fast 수정 (오후 - 이번 작업)
**`/root/webapp/backend/app/services/kis/improved_client.py`**:
```python
# 이전: max_retries=5, backoff_factor=3 → 40초/종목
def retry_on_error_current_price(max_retries=1, backoff_factor=1):
    """KIS VTS 500 지속 에러 대비 fast-fail"""

# retry_on_error도 max_retries=3→2, backoff_factor=2→1
def retry_on_error(max_retries=2, backoff_factor=1):
```

### 3.4 VTS 사용자 skip 로직 추가
**`/root/webapp/backend/realtime_signal_generator_fixed.py`**:
```python
# VTS 사용자: 랭크 API 실패 시 즉시 스킵 (fallback 50종목 스캔 방지)
# 실계좌 사용자: fallback 허용 (실KIS 가격 조회 빠름)
use_fallback = bool(kis_config.is_production)
candidate_stocks = get_candidate_stocks(db=db, kis_client=client, use_fallback=use_fallback)
```

### 3.5 서비스 재시작
- `kis-trading-engine.service` 재시작 (240s timeout 적용)

---

## 4. 오늘 테스트 결과

### 신호 생성기 테스트 (15:20 KST)
```
사용자: moong123@naver.com (VTS) → ⚠️ 동적 후보 없음 (스킵) ✓
사용자: dlrud7466@naver.com (VTS) → ⚠️ 동적 후보 없음 (스킵) ✓
사용자: moongoby@gmail.com (VTS) → ⚠️ 동적 후보 없음 (스킵) ✓
사용자: moongmimi@gmail.com (실계좌) → 후보 획득, 스캔 실행 ✓
사용자: moongoby@naver.com (실계좌) → 후보 획득, 스캔 실행 ✓
신호 생성 완료: 0개 (장 마감 직전, 전략 조건 불충족)
실행시간: ~74초 < 240s ✓
```

### 자동매매 테스트 (15:22 KST)
```
moong123 잔액 조회: 492,955,708원 ✓
moongoby@gmail 잔액: 452,752,417원 ✓
moongmimi/moongoby@naver (공유계좌 74032243): 506,078원 ✓
신호: 0개 → 매매 없음 (정상)
시스템 정상 종료 ✓
```

---

## 5. 현재 상태

| 항목 | 상태 |
|------|------|
| 실계좌 신호 생성 | ✅ 가능 (시장 조건 충족 시) |
| VTS 사용자 처리 | ✅ 즉시 스킵 (VTS 서버 장애 시) |
| 자동매매 스크립트 | ✅ 정상 실행, 잔액 조회 성공 |
| 타임아웃 | ✅ 240s (서비스 재시작 완료) |
| 오늘 실매매 | ❌ 0건 (장 마감 직전 설정 완료, 신호 없음) |

**실매매는 내일(2026-03-04) 09:00 장 오픈 시 신호 생성 후 자동 실행될 것으로 예상**

---

## 6. 잔여 과제

1. **KIS VTS 서버 복구 시**: VTS 사용자도 자동 복구 (코드 변경 불필요)
2. **dlrud7466 AppKey**: Fernet 키 불일치로 복호화 실패 → 재등록 필요
3. **account_snapshots 동기화**: 28일째 미갱신 → 별도 동기화 서비스 필요
4. **trading_signals 기존 PENDING 건**: 2026-02-13 생성 SELL 신호 2건 처리 필요
