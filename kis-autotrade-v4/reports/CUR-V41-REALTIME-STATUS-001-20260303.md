# CUR-V41-REALTIME-STATUS-001 — KIS 실시간 계좌 데이터 갱신 현황 보고

- **작업일**: 2026-03-03 14:25 KST
- **커밋**: 742841f5 (kis-autotrade-v4, phase-2c-command-center)
- **대상 계정**: moongoby@naver.com (user_id=3)

---

## 1. 계좌 동기화 현황

| account_id | 브로커 | 계좌번호 | 종류 | 예수금 | 평가금 | 최종 sync |
|-----------|--------|---------|------|--------|--------|----------|
| 1 | KIS | 50160711 | 모의 | 480,093,693원 | 499,830,993원 | 2026-02-24 |
| 4 | KIWOOM | 81201280 | **모의** | **500,003,015원** | **201,000원** | **2026-03-03 14:14 ✅** |
| 5 | KIWOOM | 52568156 | 실계좌 | - | - | 잠금 (is_locked=true) |
| 6 | KIWOOM | 63109343 | 실계좌 | - | - | 잠금 (is_locked=true) |

> account_id=4 (키움 모의계좌): 오늘 14:14 sync 완료. 삼성전자(005930) 1주 보유 중 (평가금 201,000원)

---

## 2. 페이퍼 트레이딩 현황

| portfolio_id | 카드 | 상태 | 현금 | 평가금 | 총자산 |
|-------------|-----|------|------|--------|--------|
| 6 | #15 [단기스윙] 섹터모멘텀 | ACTIVE | 8,002,525원 | 1,997,175원 | **9,999,700원** |
| 8 | #14 [데일리] 대형 우량주 | ACTIVE | 5,000,000원 | 0원 | **5,000,000원** |

- 포트폴리오 #6: 대원강업(000430) 465주 보유 (오늘 실행 시 sold=0 유지)
- 포트폴리오 #8: 신규 시작, 포지션 없음 (장 마감으로 매매 없음)
- **총 페이퍼 자산**: 14,999,700원

---

## 3. 라이브 트레이딩 현황 (키움 모의계좌)

| 항목 | 값 |
|------|-----|
| 카드 | #25 [스캘핑] 데이트레이딩 거래량 돌파 |
| account_id | 4 (KIWOOM 81201280 모의) |
| schedule_id | 5 |
| 투자금 | 3,000,000원 |
| 상태 | ✅ ACTIVE |
| 마지막 실행 | 2026-03-03 13:06:36 |
| 다음 실행 | 2026-03-04 13:06:36 |

### 최근 주문 이력

| 주문ID | 종목 | 방향 | 수량 | 가격 | 상태 | 시각 |
|-------|------|------|------|------|------|------|
| 14 | 삼성전자(005930) | SELL | 1 | 216,500 | FILLED ✅ | 10:06:08 |
| 13 | 삼성전자(005930) | BUY | 1 | 216,500 | FILLED ✅ | 10:06:08 |
| 12 | 삼성전자(005930) | SELL | 1 | - | ERROR | 10:05:46 |
| 11 | 삼성전자(005930) | BUY | 1 | - | ERROR | 10:05:45 |
| 10 | 삼성전자(005930) | BUY | 1 | - | REJECTED | 전일 |

---

## 4. 시장 데이터 현황

| 항목 | 상태 | 비고 |
|------|------|------|
| ohlcv_daily 최신 | 2026-03-03 ✅ | 3,839종목 종가 확보 |
| DESK2 realtime_signal | ✅ 실행 중 (매 5분) | inserted=0 (장 외 시간 정상) |
| 시장 레짐 | MILD_TREND_UP | KOSPI 6,241 / VKOSPI 54.67 |

---

## 5. 수정 이슈: FundPool invariant CRITICAL 오류 해소 [FIXED]

| 항목 | 내용 |
|------|------|
| **증상** | go100 서비스 매 1분 사이클마다 `FundPool invariant: desk_used[3]={N} > limit=0` CRITICAL 로그 반복 |
| **원인 1** | `rebuild_from_db()`에서 `positions` 테이블에 `desk_id` 컬럼 없을 때 `desk_used_db = dict(self.desk_used)` 사용 — 기존 in-memory 값 유지 |
| **원인 2** | 2026-02-13 생성된 stale 예약(id=rb-test-24b2eadc, desk_id=3, amount=200,000)이 `ORDER_SUBMITTED` 상태로 방치 |
| **누적 메커니즘** | 매 rebuild마다 stale 200,000원이 기존 desk_used에 더해짐: 5.4M→6.6M→7.0M 누적 증가 |
| **수정 1 (코드)** | `backend/app/services/execution/fund_pool.py:512` — `dict(self.desk_used)` → `{1:0,2:0,3:0,4:0,5:0}` 초기화 |
| **수정 2 (DB)** | `v4_reservations` — `rb-test-24b2eadc` 상태 → `EXPIRED` |
| **결과** | `desk_used={1:0,2:0,3:0,4:0,5:0}` 정상화, CRITICAL 로그 소멸 ✅ |
| **커밋** | 742841f5 |

---

## 6. 잔존 경고 (WARNING, 기능 영향 없음)

| # | 경고 | 설명 |
|---|------|------|
| W-1 | `positions lacks desk_id column` | Phase 3 마이그레이션 예정 (TODO). 현재 v4_reservations 기반으로 대체 동작 |
| W-2 | `available 음수 감지` | FundPool total_capital=0으로 초기화 → invested=2,098,369으로 보정 처리 (기능 영향 없음) |
| W-3 | R-4 키움 WebSocket 미연동 | REST polling 기반 동작 중 (구조적 한계, 미처리) |

---

## 7. 전체 시스템 상태 요약

```
dashboard summary (moongoby@naver.com):
  paper_status: active  ✅
  live_status:  active  ✅
  total_asset:  14,999,700원  ✅

키움 모의계좌 (account_id=4):
  예수금: 500,003,015원  ✅
  평가금: 201,000원 (삼성전자 1주)  ✅
  최종 sync: 2026-03-03 14:14 KST  ✅

go100 서비스:
  FundPool CRITICAL 오류: 해소 ✅
  heartbeat: TRADING 상태, cycle_id=2  ✅

go100.newtalk.kr: HTTP 200  ✅
```

---

## 변경 파일

**백엔드**:
- `backend/app/services/execution/fund_pool.py` — desk_used 초기화 버그 수정

**DB**:
- `v4_reservations`: rb-test-24b2eadc → EXPIRED

**커밋**: 742841f5 (kis-autotrade-v4, phase-2c-command-center)
