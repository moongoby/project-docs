# CARD-BUY 완료 보고서 — 2026-02-21

## 1. 조사 결과

- **run_card_pipeline 현재 구조**: 청산(exit) 전용. `execute_exit_signals`만 호출하고 매수 없이 `# 전략별 연동은 추후` 주석만 존재
- **entry_conditions → entry_rules**: 테이블 컬럼명이 `entry_rules`(JSONB). `min_strength`, `min_conditions`, `indicators` 배열 포함
- **indicator 목록**: `sma5_above_sma20`, `volume_surge_2x`, `rsi_below_70`, `macd_golden_cross`, `bb_lower_touch`, `commander_scan`, `close_price_bet` 등 40여종
- **v4_signals 활용 가능**: **Y**. LiveSignalGenerator가 DESK 1~5별로 당일 BUY 시그널을 적재 (2/19 기준 DESK당 260~465건). 단, Commander 비활성화로 `generate_daily_signals` 호출 주체가 없어짐
- **기존 매수 함수 체인**: `bridge.process_signal(signal, desk_config)` → `risk_manager.can_open_position` → `calculate_position_size` → `executor.place_buy_order` → `_insert_position` → `_insert_trade`

## 2. 구현 내용

- **선택한 방법**: v4_signals + 카드 매칭 (선호 방법)
- **매수 흐름**:
  1. `run_strategy_cards_cycle`: `generate_daily_signals()` 1회 호출 (Commander 대체)
  2. 각 카드의 `run_card_pipeline`: 청산 검사 후 → `_execute_card_buy_signals` 호출
  3. `_execute_card_buy_signals`: v4_signals에서 desk_id + min_strength 기준 BUY 시그널 조회
  4. 안전장치 6종 체크 후 `bridge.process_signal(signal, desk_config)` 호출
  5. bridge 내부에서 risk_manager, KIS API, position/trade INSERT 처리
- **수정 파일**: `backend/app/services/trading/v4_pipeline_orchestrator.py` (246 insertions, 7 deletions)
- **신규 파일**: 없음
- **안전장치**:
  - `max_concurrent_positions`: 데스크별 동시 포지션 상한 (기본 10)
  - `max_capital_usage_pct`: 총 자본 사용률 상한 (기본 80%)
  - `max_single_position_pct`: 단일 종목 최대 비중 (기본 10%)
  - `max_daily_entries`: 일일 최대 매수 건수 (기본 20)
  - 동일 종목 중복 매수 방지 (OPEN 포지션 체크)
  - `max_stocks`: 카드별 최대 종목 수 (strategy_cards.max_stocks)

## 3. 검증

- **py_compile**: OK
- **import 체인**: OK (dotenv 로드 후 정상 import)
- **서비스 재시작**: 성공 (kis-v41-api, scheduler, monitor 모두 active)
- **로그 에러**: 없음

## 4. 월요일 실매매 시나리오

- **09:10** 카드 사이클 시작 → `run_strategy_cards_cycle`
  1. `generate_daily_signals()` 호출 → v4_signals에 당일 BUY 시그널 적재 (DESK1~5, 약 300~400건/데스크)
  2. 58개 카드 순회 → 각 카드별 `run_card_pipeline`
  3. 청산 검사 (기존 로직 유지)
  4. 카드의 desk_id로 v4_signals 필터 + min_strength 이상만 → signal_strength DESC 정렬
  5. 안전장치 통과 종목에 대해 `bridge.process_signal` → KIS API 매수
- **예상 작동**: 각 데스크별 시그널 중 강도 높은 순서대로 매수, 안전장치로 과다 진입 방지
- **청산**: 기존 로직 100% 유지 (execute_exit_signals 변경 없음)

## 5. 리스크/권고

- v4_signals는 **전일 일봉 종가 기반** 기술적 지표로 생성됨. 장중 가격 변동 미반영
- `entry_rules.indicators` 배열은 현재 매칭에 사용하지 않음 (LiveSignalGenerator가 자체 조건으로 평가). 추후 카드별 커스텀 지표 평가기 필요 시 확장 가능
- risk_params가 비어있는 카드(대부분)는 기본값 적용: max_concurrent=10, max_capital=80%, max_single=10%, max_daily=20
- 첫 운영일은 **DRY_RUN=true** 상태로 실행하여 로그만 확인 권장

## 6. 사전/사후 확인

| 항목 | 사전 | 사후 |
|------|------|------|
| strategy_cards | 59 | 59 |
| v4_positions OPEN | 5 | 5 |
| 서비스 | active x3 | active x3 |
| .env/.bak 커밋 | N/A | 없음 |
| V4.1 파일 수정 | v4_pipeline_orchestrator.py | (지시서 허용) |
| DB 스키마 변경 | 없음 | 없음 |
| 커밋 | — | 7b198cc8 |

## 컴플라이언스 체크리스트

| .env/.bak 커밋 | strategy_cards 59건 | v4_positions OPEN 5건 | 파일헤더 | DB스키마변경 | 서비스재시작 | V4.1파일수정 |
|---|---|---|---|---|---|---|
| 없음 | 59 | 5 | CC-CARD-BUY | 없음 | 허가 후 실행 | orchestrator만 (지시서 허용) |
