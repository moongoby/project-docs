# BT-ENGINE-UPGRADE 결과 보고 (2026-02-23)

## [PHASE 0: strategy_cards 변경 추적]

- **현재 건수**: 62건 (기준 59에서 3건 증가 확인)
- **추가된 3건 (card_id 기준 60, 61, 62)**  
  - card_id 60: DESK5_모멘텀팩터, desk_id=5, is_live=t, created_at=2026-02-20 21:43:24  
  - card_id 61: 시초가매매, desk_id=NULL, created_at=2026-02-21 06:39:39  
  - card_id 62: 제시해주신 조건들을 바탕으로..., desk_id=NULL, created_at=2026-02-22 10:59:03  
- **추가 원인**: GO100/전략 저장·카드 통합 등 관련 커밋 (CUR-GO100-UNIFIED-SAVE, MY-STRATEGY-FIX, 카드 설계 변경 등)으로 사용자/GO100 전략 카드 추가. card_id 63, 64는 그 이후 추가로 현재 총 62건.

---

## [PHASE 1: 백업]

| 항목 | 결과 | 경로 |
|------|------|------|
| backtest_engine_v2.py 백업 | Y | /root/backups/bt_engine_upgrade_20260223/backtest_engine_v2.py.bak |
| 스키마 백업 | Y | /root/backups/bt_engine_upgrade_20260223/v4_backtest_trades_schema.sql |
| 기존 거래 건수 | 169,114 | (검증용 기록) |

---

## [PHASE 2: ALTER TABLE]

- **추가 컬럼 수**: 16  
  - entry_datetime, exit_datetime, entry_price, exit_price  
  - mfe_pct, mae_pct, mfe_price, mae_price  
  - regime_at_entry, indicator_snapshot, slippage_pct, commission  
  - sector, strategy_name, entry_volume, entry_spread_pct  
- **기존 데이터 영향**: 없음 (신규 컬럼 NULL 허용, 기존 행은 NULL 유지)  
- **건수 변화**: 변동 없음 (169,114건 유지)

---

## [PHASE 3: 엔진 수정]

| 항목 | 결과 |
|------|------|
| _record_trade 수정 | Y (파라미터·INSERT 확장) |
| _run_minute 시간 전달 | Y (_current_minute_time, entry_datetime/exit_datetime) |
| MFE/MAE 추적 | Y (Position.trough_price 추가, 일봉/분봉 루프에서 갱신) |
| entry_price/exit_price | Y (BUY/SELL 시 명시 기록) |
| strategy_name | Y (run()에서 _card_name_map 로드, card_id→strategy_name) |
| commission | Y (price×qty×FEE_RATE 기록) |
| 문법 검증 | PASS (python -m py_compile) |

- **수정 파일**: `scripts/backtest/backtest_engine_v2.py`  
- **원칙 준수**: 매매 판단·시그널·손절/익절 로직 미변경, 기록 데이터만 확장.

---

## [PHASE 4: 검증]

| 항목 | 결과 |
|------|------|
| 테스트 세션 ID | 63 |
| 테스트 거래 건수 | 94 (BUY+SELL 포함, SELL 47건) |
| entry_datetime 기록 | N (일봉 모드라 분봉 시간 없음 → NULL) |
| exit_datetime 기록 | N (동일) |
| MFE/MAE 기록 | Y (SELL 건별 mfe_pct, mae_pct 확인) |
| strategy_name 기록 | Y (DESK2_..., DESK3_... 등) |
| entry_price/exit_price/commission | Y |
| 기존 세션 영향 | 없음 (세션 47, 61, 62: has_entry_price=0, has_mfe=0 유지) |

---

## [PHASE 5: 최종]

| 항목 | 값 |
|------|-----|
| strategy_cards COUNT | 62 |
| v4_positions OPEN | 5 |
| 커밋 해시 | 556ddb175192f7fc9a72a667045cb4918b32130a |

---

## 요약

- **v4_backtest_trades**: 16개 컬럼 추가, 기존 169,114건 무변경.  
- **backtest_engine_v2.py**: _record_trade 확장, Position에 trough_price(MAE), _card_name_map·_current_minute_time 반영, MFE/MAE·entry/exit 가격·strategy_name·commission 기록.  
- **검증**: 세션 63 일봉 백테스트로 새 컬럼 기록 및 기존 세션 무영향 확인.  
- **백업**: 엔진 파일·스키마·건수 백업 완료.  
- **커밋**: BT-ENGINE-UPGRADE 적용 완료 (1 file changed, 84 insertions, 4 deletions).
