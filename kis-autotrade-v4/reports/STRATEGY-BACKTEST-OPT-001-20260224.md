# STRATEGY-BACKTEST-OPT-001 전략 백테스트 & 1차 최적화 보고서

**작업 ID:** CUR-STRATEGY-BACKTEST-OPT-001  
**작성일:** 2026-02-24 (KST)  
**서버:** root@[SERVER-IP]  
**프로젝트:** /root/kis-autotrade-v4  
**브랜치:** phase-2c-command-center  

---

## 1. 요약

| 항목 | 결과 |
|------|------|
| AUDIT 보고서 | project-docs 참조 가능. 카드 목록은 DB(v4_desk_strategy_mapping + strategy_cards) 기준으로 확정 |
| backtest_engine_v2.py | **수정 없음** (절대 규칙 준수) |
| DESK1 백테스트 | **엔진 구조 한계**: 매매 루프가 `desk_id in (2,3,4,5)` 만 순회 → DESK1 단독/카드별 실행 시 **거래 0건** |
| DESK1 backtest_compatible | 10건(5, 38~46) **true** 로 UPDATE 완료 (DESK1 전용 백테스트 가능 시 대비) |
| DESK2~5 카드별 백테스트 | 실행 명령·기간·산출물 경로 정리 완료. 샘플 DESK2-6 실행 검증됨(시그널·포지션 발생) |
| 1차 최적화 | 기준(승률 45%+, PF 1.2+, MDD -15% 이내, 최소 거래 횟수) 및 그리드서치 방안 문서화 |

---

## 2. 선행 작업

### 2.1 DB 현황 (2026-02-24 기준)

- **strategy_cards**: DESK1 카드 10건(5, 38~46) `backtest_compatible = true` 로 변경 완료.
- **v4_desk_strategy_mapping** (stage_id=1, is_active=true) + **strategy_cards** (backtest_compatible=true) 기준 카드 수:
  - DESK1: 10
  - DESK2: 18
  - DESK3: 11
  - DESK4: 10
  - DESK5: 11

### 2.2 DESK1 한계 (엔진 구조)

- `backtest_engine_v2.py` 내 매일 매매 로직:
  - `_try_buy()`: `for desk_id in (2, 3, 4, 5)` 만 순회 (923행 근처).
  - 분봉 경로(`_run_minute_*`): 동일하게 `desk_id in (2, 3, 4, 5)` (1210행 근처).
- 따라서 **desk_id=1(DESK1)은 매매 루프에 포함되지 않음**.
- `--desk-strategies '[{"desk_id":1,"card_id":5}]'` 로 DESK1만 넘겨도:
  - 전략/자금은 DESK1만 로드·정규화(100%)되나,
  - 진입/청산은 2~5만 수행 → **DESK1 거래 0건**.
- **권장**: DESK1 스캘핑 검증은 실거래/분봉 파이프라인 또는 엔진 확장(CEO 승인 시)으로 진행.

---

## 3. ROUND별 실행 명령 및 기간

### 공통

- **Python**: `source /root/kis-autotrade-v4/venv/bin/activate`
- **PYTHONPATH**: `/root/kis-autotrade-v4:/root/kis-autotrade-v4/backend`
- **엔진**: `--engine v2` (run_backtest.py, backtest_engine_v2 미수정)

### ROUND 1: DESK1 스캘핑

- **기간**: `--start 20260101 --end 20260223`
- **결과**: 위 한계로 **카드별 실행 시에도 거래 0건**. 실행만 해도 결과는 0건이므로, ROUND 1은 “DESK1 한계 문서화”로 대체.

### ROUND 2: DESK2 단타

- **기간**: `--start 20251201 --end 20260223` (약 3개월)
- **카드**: 6, 7, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27 (18개)
- **예시 (카드 6)**  
  ```bash
  cd /root/kis-autotrade-v4 && source venv/bin/activate
  PYTHONPATH=/root/kis-autotrade-v4:/root/kis-autotrade-v4/backend python scripts/backtest/run_backtest.py \
    --start 20251201 --end 20260223 --capital 1000000 \
    --name "DESK2-6-class_a" --engine v2 \
    --desk-strategies '[{"desk_id":2,"card_id":6}]'
  ```
- **결과 저장**:  
  `PYTHONPATH=... python scripts/backtest/export_session_to_json.py --session-name "DESK2-6" --out /tmp/backtest_2_6_results.json`

### ROUND 3: DESK3 단기스윙

- **기간**: `--start 20251001 --end 20260223` (약 5개월)
- **카드**: 8, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37 (11개)
- **예시 (카드 8)**  
  `--name "DESK3-8-class_d"`  
  `--desk-strategies '[{"desk_id":3,"card_id":8}]'`

### ROUND 4: DESK4 중기스윙

- **기간**: `--start 20250601 --end 20260223` (약 9개월)
- **카드**: 9, 11, 47, 48, 49, 50, 51, 52, 53 (10개)
- **예시 (카드 9)**  
  `--name "DESK4-9-class_e"`  
  `--desk-strategies '[{"desk_id":4,"card_id":9}]'`

### ROUND 5: DESK5 장기 + WaveRider

- **기간**: `--start 20250101 --end 20260223` (약 14개월)
- **카드**: 10, 12, 13, 54, 55, 56, 57, 58, 59, 60 (11개)
- **예시 (카드 10)**  
  `--name "DESK5-10-class_f"`  
  `--desk-strategies '[{"desk_id":5,"card_id":10}]'`

---

## 4. 산출물

- **백테스트 결과 JSON**: `/tmp/backtest_{desk_id}_{card_id}_results.json`
- **내보내기**:  
  `scripts/backtest/export_session_to_json.py --session-name "DESK{N}-{card_id}" --out /tmp/backtest_{N}_{card_id}_results.json`
- **DB**: `v4_backtest_sessions`, `v4_backtest_summary`, `v4_backtest_trades` (session_id로 조회 가능)

---

## 5. 최적화 기준 (지시서)

| 지표 | 기준 |
|------|------|
| 최소 승률 | 45% |
| 최소 PF | 1.2 |
| 최대 MDD | -15% |
| 최소 거래 횟수 | DESK1 100회, DESK2 50회, DESK3 30회, DESK4 15회, DESK5 5회 |

### 1차 최적화 (그리드서치)

- **대상 파라미터**: target_pct ±0.5%, stop_loss_pct ±0.3%, trailing_pct 조정.
- **방법**: 카드별 기본값 대비 그리드 탐색 후, 위 기준 충족 여부·PF/MDD 비교 → CEO 보고용 비교표 작성.

---

## 6. 체크리스트

- [x] AUDIT 보고서 참조 시도 (경로 없음 → DB 기준으로 카드 목록 확정)
- [x] DESK1 backtest_compatible 활성화
- [x] DESK1 한계(엔진 매매 루프 2~5만) 문서화
- [ ] DESK2 카드별 백테스트 완료 (실행 명령·export 절차 정리됨)
- [ ] DESK3 카드별 백테스트 완료
- [ ] DESK4 카드별 백테스트 완료
- [ ] DESK5 카드별 백테스트 완료
- [ ] 1차 최적화 결과 정리 및 모의실매매 대상 전략 선정
- [ ] 코드 커밋 (필요 시)
- [ ] 보고서 project-docs 복사 및 push (HTTP 200)

---

## 7. 참조

- STRATEGY-FULL-AUDIT-001: /root/project-docs/kis-autotrade-v4/reports/STRATEGY-FULL-AUDIT-001-20260224.md
- kis-v41-rules.md: 백테스트 실행 명령, backtest_engine_v2 수정 금지
- DESK1-MAPPING-BT-20260223.md: DESK1 매핑·backtest_compatible 원인
- DB: v4_backtest_trades 36컬럼, v4_backtest_summary

---

*CUR-STRATEGY-BACKTEST-OPT-001 보고서 끝.*
