# DESK2-BT-FULL-RUN-001 3차 최적화 full 구간 백테스트 보고서

**지시서:** DESK2-BT-FULL-RUN-001  
**프로젝트:** KIS AutoTrade V4.1  
**브랜치:** phase-2c-command-center  
**작성일:** 2026-02-25 (KST)  
**우선순위:** P0  

---

## 1. 3차 최적화 파라미터 요약

| 구분 | 설정 위치 | 값 | 비고 |
|------|-----------|-----|------|
| ECHO_ABCD | `desk2_config.yaml` + `echo_abcd.py` | `desk_score_min: 70`, `bc_range_min_pct: 0.3` | YAML·코드 일치 |
| DELTA_VWAP | `delta_vwap.py` | `VWAP_ENTRY_MAX_RATIO: 0.998` | 상수 |
| BRAVO_ORB | `bravo_orb.py` | `breakout_pct` 0.3~3.0 검사 | config `breakout_pct_min: 0.5` (discovery) |

- **desk2_config.yaml**  
  - `strategy_params.ECHO_ABCD.desk_score_min: 70`, `bc_range_min_pct: 0.3`  
  - `strategy_params.DELTA_VWAP` (stop_loss_pct, target_profit_pct, hold_timeout_sec)  
  - `strategy_params.BRAVO_ORB.breakout_pct_min: 0.5`, orb_period_bars, volume_ratio_min  

---

## 2. STEP 1~3 실행 결과

### STEP 1 – 기존 프로세스 확인
- **결과:** 실행 중인 `desk2_backtester` 프로세스 없음 → STEP 2 진행.

### STEP 2 – 3차 최적화 파라미터 확인
- **결과:** 적용 설정이 3차 최적화와 일치함 (위 §1 참고).

### STEP 3 – full 구간 백테스트 실행
- **명령:**  
  `PYTHONPATH=backend .venv/bin/python backend/app/services/trading/desk2/tests/desk2_backtester.py --start 2025-06-01 --end 2026-02-21 --capital 10000000 --strategy ALL`
- **출력 파일:** `report/v41/desk2-bt/full_bt_result_v3.txt`
- **실행 시각:** 2026-02-25 15:27 KST  
- **PID:** 3640397 (nohup 자식 프로세스)
- **상태:** 실행 중 (예상 소요 ~2시간)

**진행 확인 명령:**
```bash
tail -f /root/kis-autotrade-v4/report/v41/desk2-bt/full_bt_result_v3.txt
grep -c 'DESK2-BT \[' /root/kis-autotrade-v4/report/v41/desk2-bt/full_bt_result_v3.txt
ps aux | grep desk2_backtester | grep -v grep
```

---

## 3. full 구간 결과 (전략별 매트릭스)

**full 완료 후 아래 항목을 채울 것.**

| 전략 | 거래수 | 승률 | 평균 PnL% | PF | Calmar | 일손실 | 기준 충족 |
|------|--------|------|-----------|-----|--------|--------|-----------|
| ALPHA_GAP | - | - | - | - | - | - | - |
| BRAVO_ORB | - | - | - | - | - | - | - |
| DELTA_VWAP | - | - | - | - | - | - | - |
| ECHO_ABCD | - | - | - | - | - | - | - |
| GOLF_REVERSAL | - | - | - | - | - | - | - |
| **전체** | - | - | - | - | - | - | - |

- **수집 명령 (full 완료 후):**
```bash
tail -50 /root/kis-autotrade-v4/report/v41/desk2-bt/full_bt_result_v3.txt
grep -iE "result|total|pass|fail|return|trades|calmar|profit_factor|by_strategy" \
  /root/kis-autotrade-v4/report/v41/desk2-bt/full_bt_result_v3.txt
```

---

## 4. 성공 기준 충족 여부

- **기준:** E > +0.3%, Calmar > 1.5, PF > 1.3, 일손실 ≤ -3%, 거래수 2~5/일  
- **판정:** full 완료 후 `result["pass"]`, `result["criteria"]` 반영하여 기입.

---

## 5. BtDataWriter 연동 결과

- **상태:** full 완료 후 수행 예정 (~15분)
- **방법:**  
  - `bt_data_writer.py`로 세션 생성 (`create_session` → `update_session_result`)  
  - `full_bt_result_v3.txt` 내 `TRADE_DETAIL` 라인 파싱 후 `write_trade` 호출  
  - 또는 `desk2_backtester.py`에 BtDataWriter 주입 후 재실행 시 자동 기록 (BT-DASHBOARD-IMPL-001 권장 사항)
- **테이블:** `v4_bt_sessions`, `v4_bt_trades`  
- **결과:** 연동 완료 후 대시보드에서 세션·거래 확인 가능.

---

## 6. PAPER 카드 등록 대상 전략

- full 결과 및 성공 기준 충족 여부 확정 후, PF·Calmar·승률·일손실 기준을 만족하는 전략을 PAPER 카드 등록 대상으로 기입.

---

## 7. 모의매매 전환 권장 사항

- PAPER 등록 대상 확정 후, 동일 파라미터로 모의매매 전환 일정·리스크 정책 반영하여 권장 사항 기입.

---

## 8. 완료 체크리스트

| 항목 | 상태 |
|------|------|
| 기존 프로세스 없음 확인 | ✅ |
| 3차 최적화 파라미터 적용 확인 | ✅ |
| full 구간 nohup 실행 (PID 기록) | ✅ PID 3640397 |
| full 완료 후 결과 수집 | ⏳ 대기 |
| BtDataWriter 대시보드 연동 | ⏳ full 완료 후 |
| 전략별 매트릭스 완성 | ⏳ full 완료 후 |
| PAPER 카드 등록 대상 확정 | ⏳ full 완료 후 |
| 보고서 push curl 200 | ⏳ STEP 6 시 |

---

## 9. full 완료 후 실행 순서 (STEP 4→5→6)

1. **STEP 4** – 결과 수집: `tail`, `grep`로 요약·전략별 지표 추출 후 §3·§4 보완  
2. **STEP 5** – BtDataWriter 연동: 세션 생성 → 결과 파싱 → trades INSERT → 대시보드 확인  
3. **STEP 6** – 보고서 최종화 후 저장·push:  
   - 보고서: `/root/kis-autotrade-v4/report/v41/DESK2-BT-FULL-RUN-001-20260225.md`  
   - GitHub 문서: `/root/project-docs/kis-autotrade-v4/reports/DESK2-BT-FULL-RUN-001-20260225.md`  
   - kis-autotrade-v4: `git add -A` → commit → `git push origin phase-2c-command-center`  
   - project-docs: `cp` → `git add -A` → commit → `git push origin master`  
   - `curl` 200 확인:  
     `https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/DESK2-BT-FULL-RUN-001-20260225.md`

---

**문서 끝**
