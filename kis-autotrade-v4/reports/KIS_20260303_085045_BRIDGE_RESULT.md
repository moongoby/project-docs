---
project: KIS V4.1
task_id: CUR-V41-PREMARKET-CHECK-001
completed_at: 2026-03-03T08:52:41 KST
---

# PREMARKET CHECK 결과 보고 — 2026-03-03 장 시작 전

## 1. Premarket Cron 실행 여부

**정상 실행 확인** ✅

- scheduler.log에서 `2026-03-03 07:59:34` 스코어링 INSERT 확인
- v4_mock_trades에 2026-03-03 기준 **7건** 등록됨 (premarket cron 정상 동작)

| ticker | strategy_id | approved | blocking_reason |
|--------|-------------|----------|-----------------|
| 182487 | D6 | ✅ 통과 | NONE (cs_score:86, eqs:54) |
| 884760 | D2 | ✅ 통과 | NONE (cs_score:74, eqs:62) |
| 645820 | D-ORB | ✅ 통과 | NONE (cs_score:59, eqs:68) |
| 529671 | D5 | ❌ 미통과 | GATE: 반등확인 게이트 미통과 |
| 702721 | D4 | ❌ 미통과 | L3.3_SUPPLY: 수급 차단 |
| 196979 | S1 | ❌ 미통과 | L3.3_SUPPLY: 수급 차단 |
| 956527 | D7 | ❌ 미통과 | L3.3_SUPPLY: 수급 차단 |

**승인 종목: 3건 / 미통과: 4건**

## 2. 데이터 수집 상태

- **ohlcv_daily max date**: 20260227 (02-27 금요일 — 주말 미수집 정상)
- **v4_investor_daily max trade_date**: 2026-02-27 (정상, 03-03 당일 미수집)
- 판정: 정상 ✅ (03-03 당일 데이터는 장 마감 후 수집 예정)

## 3. ATR 1.5 적용 확인

```
NET_RR_RATIO = 1.5  # CEO 옵션B 승인 적용 (WF 3-Fold ALL PASS)
```

위치: `/root/kis-autotrade-v4/backend/app/services/trading/cte/atr_dynamic_exit.py`

**적용 확인** ✅ (2.0 → 1.5 변경 완료)

## 4. 에러 로그 확인

- `unified_engine.log` 파일 없음 (해당 서비스 미사용 또는 다른 경로)
- `app_2026-03-03.log`: ERROR 없음 (07:54:36 Session cleanup INFO만 존재)
- `scheduler.log`: ERROR 없음 (07:59:34 premarket scoring 정상 완료)
- `error_2026-03-03.log`: 내용 없음

**에러 없음** ✅

## 5. 서비스 상태

| 서비스 | 상태 |
|--------|------|
| kis-unified-engine | inactive (별도 systemd 서비스 — 현재 미구동) |
| go100 (FastAPI) | **active** ✅ |
| go100-frontend (Next.js) | **active** ✅ |

## 6. 주의사항 (alert_cron 경고)

- **디스크 사용률 81%** ⚠️ — 지속 모니터링 필요
- **포지션 손절선 도달 경고**:
  - 088350, 003530, 373110, 152550 종목 손절선 도달
  - → 트레이더 확인 필요

## 종합 판정

| 항목 | 결과 |
|------|------|
| Premarket cron 실행 | ✅ 정상 (07:55 실행, 7건 등록) |
| 승인 후보 | ✅ 3건 (D6, D2, D-ORB) |
| OHLCV 최신 데이터 | ✅ 02-27 (주말 미수집 정상) |
| ATR 1.5 적용 | ✅ NET_RR_RATIO = 1.5 확인 |
| 에러 로그 | ✅ 없음 |
| 핵심 서비스 | ✅ go100/go100-frontend active |
| 디스크 | ⚠️ 81% (주의) |
| 손절선 경고 | ⚠️ 4종목 (트레이더 확인 요망) |

**장 시작(09:00) 준비 완료. 승인 종목 3건 모니터링 시작.**
