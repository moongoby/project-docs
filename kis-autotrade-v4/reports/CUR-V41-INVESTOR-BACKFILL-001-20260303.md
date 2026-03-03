---
task_id: CUR-V41-INVESTOR-BACKFILL-001
project: KIS
date: 2026-03-03
author: Cursor Claude
status: completed
---

# CUR-V41-INVESTOR-BACKFILL-001 — v4_investor_daily 2026-03-03 수동 백필

> 작업일: 2026-03-03 KST  
> 완료: 2026-03-03 13:31 KST

---

## 배경

- `v4_investor_daily` max(trade_date) = **2026-02-27** (03-03 수집 누락)
- 장중 L3.3 SupplyDemandGate 수급 게이트가 최신 데이터 없이 동작 중
- `collect_all_missing_data.py --investor --days 1 --stock-limit 4000` 수동 실행

## 실행 결과

| 항목 | 값 |
|------|-----|
| 실행 스크립트 | `scripts/collect_all_missing_data.py --investor --days 1 --stock-limit 4000` |
| 시작 시각 | 2026-03-03 12:41 KST |
| 완료 시각 | 2026-03-03 13:31 KST |
| 소요 시간 | 약 50분 |
| 대상 종목 | 3,844종목 |
| 성공 | 3,844건 (실패 0건) |
| INSERT 행수 | **230,554행** |
| EXIT 코드 | **0 (정상)** |

## DB 최종 확인

```sql
SELECT max(trade_date), count(*) FROM v4_investor_daily WHERE trade_date='2026-03-03';
-- 결과: 2026-03-03 / 3,839종목
```

수집 결과 검증 (최종 로그):
```
v4_investor_daily: rows=279,685 / stocks=3,943 / range=2010-01-28~2026-03-03 / trading_days=807
```

## 효과

- L3.3 SupplyDemandGate: 오늘 날짜 수급 데이터 정상 반영
- 외인연속매수, 수급궤적 계산 정상화
- DESK2 신호 생성 시 당일 수급 조건 활용 가능
