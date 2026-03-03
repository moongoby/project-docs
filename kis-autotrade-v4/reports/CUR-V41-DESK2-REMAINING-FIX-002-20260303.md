# CUR-V41-DESK2-REMAINING-FIX-002-20260303

> 작성: 2026-03-03 10:35 KST  
> 작업자: CURSOR-KIS  
> task_id: CUR-V41-DESK2-REMAINING-FIX-002

---

## Phase 1 — 실시간 수집 전수 점검

| 테이블 | rows | 최신 날짜 | 심볼 수 | 상태 |
|--------|------|-----------|---------|------|
| ohlcv_daily | 2,615,744 | 2026-02-27 | 3,844 | ⚠️ 03-02 누락 (백필 실행 중) |
| v4_ohlcv_minute (2026-03) | 1,764 | 2026-03-03 | 21 | ✅ 오늘 수집 중 |
| v4_investor_daily | 275,846 | 2026-02-27 | 3,943 | ✅ |
| v4_trade_strength_history | 234,765 | 2026-03-03 15:30 KST | 3,760 | ✅ 오늘 정상 |
| v4_orderbook_rt | 1,691,073 | 2026-03-03 10:23 KST | 20 | ✅ 실시간 수집 중 |
| v4_tick_data | 1,144,618 | 2026-03-03 10:23 KST | 21 | ✅ 실시간 수집 중 |
| v4_market_regime_daily | 1,116 | 2026-02-27 | — | ✅ |
| v4_vkospi_daily | 1,510 | 2026-02-26 | — | ⚠️ T+3 이상 지연 (API 특성) |
| v4_theme_daily | 34,122 | 2026-02-27 | — | ✅ |
| v4_sector_daily | 15,086 | 2026-03-03 | 32 | ✅ 오늘 갱신 |
| v4_mock_trades | 56 | 2026-03-03 | 56 | ✅ 오늘 신호 기록 |
| go100_news_items | 2,156,079 | 2026-03-02 | — | ✅ |

### 주요 이슈
- **ohlcv_daily 2026-03-02 누락**: 어제(03-02) 16:00 cron 로그에 `완료: 오늘=20260302 저장 3839건` 기록됐으나 DB 미반영. 원인 불명. → 수동 백필 `collect_ohlcv_daily_history.py --start 20260302 --end 20260303` 실행 중 (10:27 KST)
- **vkospi_daily 최신 2026-02-26**: 공공데이터 포털 API T+3 이상 지연 특성 — 02-27 이후 데이터는 현시점 미제공, cron 정상 작동 중

---

## Phase 2 — DESK2 전용 테이블 활성화 방안

### 현황
| 테이블 | rows | 원인 |
|--------|------|------|
| v4_desk2_signals | 0 | prescoring 0건 |
| v4_desk2_trades | 0 | signals 없음 |
| v4_desk2_candidates | 0 | ohlcv_daily 03-02 누락 |
| v4_desk2_daily_summary | 0 | 수동 실행 미구현 |

### 근본 원인

```
desk2_prescoring.py 실행:
  target_date = 2026-03-04 (내일)
  D-1 = 2026-03-03 → ohlcv_daily 미존재 (수집 진행 중)
  → 필터 통과 후보 0건 → candidates 0건 → signals 0건
```

### 활성화 방안 (우선순위 순)

1. **즉시 조치 (오늘)**: ohlcv_daily 03-02~03 백필 완료 후 `desk2_prescoring.py` 수동 재실행
2. **내일부터 자동화**: 아래 cron 등록 필요

```bash
# crontab 추가 제안
55 8 * * 1-5  cd /root/kis-autotrade-v4 && source venv/bin/activate && \
  set -a && source .env && set +a && \
  PYTHONPATH=/root/kis-autotrade-v4/backend \
  python3 scripts/desk2/desk2_prescoring.py >> /root/kis-autotrade-v4/logs/cron/desk2_prescoring.log 2>&1

*/5 9-14 * * 1-5  cd /root/kis-autotrade-v4 && source venv/bin/activate && \
  PYTHONPATH=/root/kis-autotrade-v4/backend \
  python3 scripts/desk2/desk2_realtime_signal.py >> /root/kis-autotrade-v4/logs/cron/desk2_signal.log 2>&1
```

3. **v4_desk2_signals/trades 활성화 필요 추가 조건**: `desk2_prescoring` → candidates 생성 → `desk2_realtime_signal` → signals 생성 → `desk2_auto_trader` → trades 기록

---

## Phase 3 — 오케스트레이터 정상화 + 매매 체결 확인

### 오케스트레이터
```json
{ "state": "IDLE", "is_trading": false, "emergency_mode": false }
```
- production 환경에서 `/transition` API 비활성화 — 정상 설계
- 엔진이 `--action signal` 실행 시 자체 상태 전이

### Unified Engine signal 재실행 (10:21, 10:28 KST)
```
[SIGNAL] 완료: 통과=1~3, 차단=4~6
  10:21 → S1 349605, D7 221455(112,901원), D-ORB 343369(21,897원) 통과
  10:28 → S1 199231(44,401원) 통과
  나머지 → L3.3_SUPPLY synthetic_BLOCK
```

### VTS 주문 체결 확인
```
id=63: D-ORB 942515 entry_price=None (차단)
id=61: S1 199231 entry_price=44,401원 ✅
id=56: D-ORB 343369 entry_price=21,897원 ✅
id=55: D7 221455 entry_price=112,901원 ✅
```
→ **VTS 체결 성공**: 3건 entry_price 기록 확인

### account_sync 500 에러 해소
```
config_id=3 (50160711): actual_cash=492,955,708원 ✅
config_id=4 (74032243): actual_cash=506,078원 ✅
```

### split_transfer_engine.py DESK2/3 FAILED → 0
```
DESK2: 완료: {'positions_checked':7, 'signals':0, 'executed':6, 'failed':0} ✅
DESK3: 완료: {'positions_checked':7, 'signals':0, 'executed':0, 'failed':0} ✅
```
(import json 추가로 해소)

---

## Phase 4 — vkospi 02-27 갭

- `collect_vkospi_alt.py --start 20260224 --end 20260303` → 0건 신규
- `collect_vkospi.py --start 20260226 --end 20260303` → 0건
- **원인**: 공공데이터 포털 VKOSPI(`코스피 200 변동성지수`) T+3 이상 지연
  - 2026-02-26: 54.67 (API 제공) ✅
  - 2026-02-27 이후: API 미제공 (정상적 지연)
- **현재 최신**: 2026-02-26 (54.67)
- 16:00 cron 자동 수집 대기

---

## 매매 정상화 여부

| 항목 | 결과 |
|------|------|
| VTS 500 에러 | ✅ 해소 (토큰 갱신) |
| VTS entry_price 기록 | ✅ 3건 확인 |
| split_transfer FAILED | ✅ 0건 (import json 수정) |
| DESK2 signals | ⚠️ 0건 — ohlcv 백필 후 재실행 필요 |
| account_sync | ✅ 양 계좌 정상 |

**매매 정상화: 부분 YES**  
→ VTS 주문 체결 정상, 스케줄러 오류 0건, DESK2 signals는 오늘 16:00 ohlcv 수집 완료 후 prescoring 재실행 시 활성화 예정

## security_scan: 0건 (신규 파일 기준)
## path_check: PASS
