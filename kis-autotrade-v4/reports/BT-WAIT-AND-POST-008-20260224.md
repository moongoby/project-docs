# BT-WAIT-AND-POST-008 백테스트 완료 대기 → 후처리 실행 보고서

**작업ID:** BT-WAIT-AND-POST-008  
**일시:** 2026-02-24 KST  
**서버:** [SERVER-IP]  

---

## 1. 백테스트 최종 상태

- **완료 시각:** 로그 기준 2026-02-24 14:20:47 KST (Backtest completed, session_id=75).  
  메인 전수 백테스트는 세션 70 (`V2_REGIME-BT-ALL-52`)에서 완료.
- **프로세스:** `run_regime_bt` 프로세스 없음 확인 후 STEP 2~4 진행.
- **로그:** `/tmp/regime_bt_34.log` — session_id=75 완료 후 리포트 생성 단계에서  
  `numeric field overflow` 발생하여 스크립트 종료. 백테스트 엔진 자체는 정상 완료로 간주.

### 오늘(2026-02-24) REGIME-BT 세션 요약

| session_id | session_name                 | status   | trades |
|------------|------------------------------|----------|--------|
| 70         | [DB] V2_REGIME-BT-ALL-52     | COMPLETED | 6,638 |
| 71         | [DB] V2_REGIME-BT-DESK1-CARD39    | COMPLETED | 0     |
| 72         | [DB] V2_REGIME-BT-VIZ-TEST-CARD39 | RUNNING   | 0     |
| 75         | [DB] V2_REGIME-BT-DESK1-CARD39    | COMPLETED | 0     |

- **세션 수:** 4건 (REGIME-BT 이름 포함).
- **총 trades:** 6,638건 (주요 데이터는 세션 70).

---

## 2. post 스크립트 실행 결과

- **스크립트:** `scripts/backtest/post_regime_bt_exec_005.sh`
- **결과:** **성공**
- **소요시간:** 약 5초
- **비고:**  
  - `scripts/backtest/regime_analysis.py` 미존재로 1회 실패 후, 동일 로직으로 `regime_analysis.py` 신규 작성 후 재실행.  
  - 보고서 생성 SQL에서 `MAX(boolean)` 오류 → `BOOL_OR`로 수정, `desk_id` varchar 비교 → `desk_id::int` 캐스트 적용.

---

## 3. v4_backtest_regime_analysis 적재

| 항목           | 값   |
|----------------|------|
| 적재 행 수     | **230행** |

---

## 4. BULL 상위 20 랭킹 (regime_mapped = 'BULL', alpha_pct DESC)

| card_id | strategy_name              | desk_id | win_rate | profit_factor | alpha | sharpe_ratio | total_trades | pass |
|---------|----------------------------|---------|----------|---------------|-------|--------------|--------------|------|
| 14      | DESK2_장초반레인지돌파     | 2       | 100.00   | 5641.00       | -0.58 | (NULL)       | 1            | f    |
| 9       | DESK4_중기스윙_class_e     | 4       | 50.00    | 2.01          | -0.61 | 3.759        | 2            | f    |
| 60      | DESK5_모멘텀팩터           | 5       | 50.00    | 4.17          | -0.62 | 6.880        | 2            | f    |
| 36      | DESK3_이동평균선교차_MID   | 3       | 0.00     | 0.00          | -0.66 | (NULL)       | 1            | f    |
| 52      | DESK4_켈트너채널           | 4       | 0.00     | 0.00          | -0.66 | (NULL)       | 1            | f    |
| …       | (상위 20건 중 일부만 표시) |         |          |               |       |              |              |      |

- BULL 구간 합격(overall_pass=true) 건수: **0건**.

---

## 5. 레짐별 요약 (regime_mapped)

| regime_mapped | cards | avg_wr | avg_pf   | pass_count |
|---------------|-------|--------|----------|------------|
| BEAR          | 56    | 40.09  | 1194.39  | 7          |
| BULL          | 75    | 41.78  | 309.08   | **0**      |
| CRISIS        | 42    | 47.31  | 4276.41  | 5          |
| NEUTRAL       | 57    | 48.11  | 1399.95  | 8          |

---

## 6. 모의실매매 11개 후보 (BULL pass 기준, DESK별 할당)

- **선정 기준:** `regime_mapped = 'BULL'` 이며 `overall_pass = true`, DESK별 상위 N건  
  (DESK1: 2, DESK2: 3, DESK3: 3, DESK4: 2, DESK5: 1).
- **결과:** BULL 합격 건수가 0건이므로 **후보 0건**.

---

## 7. DB 백업

- **파일:** `/tmp/backup_PRE-POST-EXEC-005-FINAL_20260224.dump`
- **완료:** 2026-02-24 14:25 KST 경, 약 3분 30초 소요.

---

## 8. 필수 규칙 준수

- kis-v41-api / monitor / scheduler 재시작 없음.
- strategy_cards ALTER/DROP/DELETE 없음.
- v4_positions 직접 UPDATE/DELETE 없음.
- .env / .bak 커밋 없음.

---

**상세 레짐·전략 매트릭스:** `report/v41/REGIME-BT-EXEC-005-20260224.md`  
**차트 확인:** https://trading41.newtalk.kr/backtest/analysis
