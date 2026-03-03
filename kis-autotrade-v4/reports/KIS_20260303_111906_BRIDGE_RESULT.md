---
project: KIS
task_id: CUR-V41-DESK2-PRESCORING-001
completed_at: 2026-03-03T11:25:00+09:00
status: SUCCESS
---

[인계 확인]
직전 완료: CUR-V41-DESK2-ACTIVATE-001
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: D-003, D-010, D-013
strategy_cards: 60
open_positions: 0

# CUR-V41-DESK2-PRESCORING-001 실행 결과

## 1. prescoring 실행 결과

```
INFO __main__ desk2_prescoring target_date=2026-03-03 inserted=10 top_n=10 sample=['307750', '027360', '001020']
INSERTED=10
```

- **target_date**: 2026-03-03
- **삽입 건수**: 10개
- **상태**: SUCCESS

## 2. DB 검증 결과

| item | count | 비고 |
|------|-------|------|
| ohlcv_0228 | 0 | 2026-02-28 토요일 (휴장일, 정상) |
| desk2_cand | 10 | 오늘(2026-03-03) prescoring 삽입 완료 |
| desk2_sig | 0 | 장중 시그널 미발생 (장 시작 전/후) |
| mock_today | 56 | 오늘 mock_trades 누적 56건 |

## 3. 오늘 desk2 후보 상위 10개 (score DESC)

| rank | stock_code | stock_name | score | sector |
|------|-----------|------------|-------|--------|
| 1 | 307750 | 국전약품 | 2.0298 | 의약품 제조업 |
| 2 | 027360 | 아주IB투자 | 1.8572 | 기타 금융업 |
| 3 | 001020 | 페이퍼코리아 | 1.8442 | 펄프, 종이 및 판지 제조업 |

## 4. 특이사항

- ohlcv_0228=0 은 2026-02-28(토)이 주말 휴장일이므로 정상
- desk2_sig=0 은 아직 장중 시그널 생성 전(장전 or 장후) 상태로 정상
- prescoring 10건 정상 삽입 완료

## 5. 실행 명령

```bash
cd /root/kis-autotrade-v4
source venv/bin/activate && set -a && source .env && set +a
PYTHONPATH=/root/kis-autotrade-v4/backend python3 scripts/desk2/desk2_prescoring.py
```

---
## 체크포인트
- [x] prescoring 실행 완료 (inserted=10)
- [x] DB 검증 쿼리 완료
- [ ] project-docs 보고서 push (done_watcher.sh 자동 처리 예정)
