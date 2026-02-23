# DESK5-CARD-BT 백테스트 보고서
> 날짜: 2026-02-23
> 작업자: Cursor

## DESK5 카드 현황

| card_id | strategy_name | desk_id | strategy_type | is_active | is_live |
|---------|---------------|---------|---------------|-----------|---------|
| 10 | DESK5_장기스윙_class_f | 5 | BUILTIN | t | f |
| 12 | DESK5_가치투자 | 5 | BUILTIN | t | f |
| 13 | DESK5_성장주모멘텀 | 5 | BUILTIN | t | f |
| 54 | DESK5_배당포착 | 5 | BUILTIN | t | f |
| 55 | DESK5_계절성추세 | 5 | BUILTIN | t | f |
| 56 | DESK5_거시경제테마 | 5 | BUILTIN | t | f |
| 57 | DESK5_섹터리더십 | 5 | BUILTIN | t | f |
| 58 | DESK5_퀄리티팩터 | 5 | BUILTIN | t | f |
| 59 | DESK5_저변동성 | 5 | BUILTIN | t | f |
| 60 | DESK5_모멘텀팩터 | 5 | BUILTIN | t | t |

- 전체 10장, 활성 10장, 라이브 1장(card_id 60).

## 백테스트 조건
- 기간: 2025-11-01 ~ 2026-02-21 (90일)
- 자본: 5,000,000 KRW
- 엔진: v2
- 세션명: V2_DESK5-BT-20260223 (또는 DESK5-BT-20260223)

## 결과

| 카드(card_id) | 거래수 | 승률 | 총 PnL | 평균 보유일 |
|---------------|--------|------|--------|------------|
| (해당 없음) | 0 | - | - | - |

- **요약**: DESK5만 단독 실행 시 **card_entries 모드**에서 전 기간(74 거래일) **시그널 0건** 발생 → 거래 0건.  
- 원인: entry_rules(예: sma60_above_sma120, sma120_trend_up, volume_20d_above_avg 등) 조건이 엄격하고, 기간 중 레짐(RISK_OFF/NEUTRAL) 및 후보 종목이 조건 미충족.
- 기존 다른 세션(51, 55, 56, 57, 58)에서는 card_id 59·60으로 거래 발생·실적 있음.

## CEO 판단 필요
- **DESK5 카드 추가 여부**: 현재 10/10으로 카드 수는 충족. 추가 필수 카드 수 0장.
- **DESK4 → DESK5 프로모션 후보**: DESK4 카드(9장) 중 max_hold_days 등 장기 파라미터 보강 후 DESK5 이관 후보 별도 백테스트 권장.  
- **진입 조건 검토**: DESK5 card_entries 진입 조건(entry_rules/indicators) 완화 또는 레짐별 가중 검토 시 시그널 발생률 재확인 권장.

## 사전 확인 (2026-02-23)
- strategy_cards: 62
- v4_positions OPEN: 5
- 서비스 재시작/ALTER/직접 수정 없음. v4_backtest_trades INSERT만 수행.
