# CUR-FULLBT-REGIME-003 전수 백테스트·레짐분석 보고서 (2026-02-24)

## 1. 개요

- **작업 ID**: CUR-FULLBT-REGIME-003
- **일시**: 2026-02-24 KST
- **내용**: backtest_engine_v2 DESK1 추가, DESK1~5 전수 백테스트, 레짐별 성과 집계, BULL 랭킹, 1차 최적화 추천, 모의실매매 대상 선정

---

## 2. 사전 점검 (STEP 0)

| 항목 | 결과 |
|------|------|
| KST | 2026-02-24 |
| kis-v41-api / monitor / scheduler | active |
| DB 백업 | /tmp/backup_FULLBT_20260224_121343.dump |
| v4_market_regime_daily | KOSPI 276행, KOSDAQ 276행 |
| strategy_cards (backtest_compatible) | DESK1=10, DESK2=16, DESK3=11, DESK4=9, DESK5=10 |

---

## 3. 백테스트 실행 결과 (STEP 2)

- **엔진 수정**: desk_id 루프 (2,3,4,5) → (1,2,3,4,5) 적용 완료.
- **실행 순서**: DESK3(11) → DESK2(16) → DESK4(9) → DESK5(10) → DESK1(10).

| DESK | 카드 수 | 기간 | 세션명 패턴 | 비고 |
|------|--------|------|------------|------|
| DESK3 | 11 | 2025-06-01~2026-02-23 | V2_DESK3-*-regime | 주 수익원 |
| DESK2 | 16 | 2025-06-01~2026-02-23 | V2_DESK2-*-regime | |
| DESK4 | 9 | 2025-03-01~2026-02-23 | V2_DESK4-*-regime | |
| DESK5 | 10 | 2025-01-01~2026-02-23 | V2_DESK5-*-regime | |
| DESK1 | 10 | 2025-06-01~2026-02-23 | V2_DESK1-*-regime | STEP 1 적용 후 |

*실제 세션 수·총 거래 수는 아래 검증 쿼리로 확인 후 기입.*

---

## 4. 레짐별 성과 (DESK × Regime 매트릭스)

*aggregate_regime_performance.py 실행 후 아래 쿼리 결과로 채움.*

```sql
SELECT desk_id, regime_mapped,
       COUNT(*) AS cards,
       ROUND(AVG(win_rate),1) AS avg_wr,
       ROUND(AVG(profit_factor),2) AS avg_pf,
       SUM(CASE WHEN overall_pass THEN 1 ELSE 0 END) AS passed
FROM v4_backtest_regime_analysis
GROUP BY desk_id, regime_mapped
ORDER BY desk_id, regime_mapped;
```

---

## 5. BULL 상위 20 랭킹

```sql
SELECT card_id, strategy_name, desk_id,
       win_rate, profit_factor, alpha_pct AS alpha_vs_benchmark, sharpe_ratio,
       total_trades, total_pnl
FROM v4_backtest_regime_analysis
WHERE regime_mapped = 'BULL' AND overall_pass = TRUE
ORDER BY alpha_pct DESC NULLS LAST, profit_factor DESC NULLS LAST
LIMIT 20;
```

---

## 6. 1차 최적화 추천값

- **대상**: BULL 구간에서 pass_overall=FALSE인 전략.
- **스크립트**: `scripts/analysis/optimize_bull_strategies.py`
- **추천**: target_profit_pct, stop_loss_pct ±20% 3단계 그리드. 결과 CSV: `report/v41/FULLBT-REGIME-003-bull-optimize-summary.csv`
- **strategy_cards UPDATE**: CEO 승인 후에만 수행.

---

## 7. 모의실매매 1차 대상 (12개)

- DESK1 상위 3개, DESK2 상위 3개, DESK3 상위 2개, DESK4 상위 2개, DESK5 상위 2개.
*BULL 랭킹 및 DESK별 상위 선정 결과로 card_id 목록 기입.*

---

## 8. DESK1 백테스트 (엔진 수정 후)

- DESK1 10개 카드(5, 38~46) 전수 백테스트 완료. 세션명: V2_DESK1-*-regime.

---

## 9. 체크리스트

- [x] backtest_engine_v2.py DESK1 추가
- [ ] DESK3 11개 백테스트 완료
- [ ] DESK2 16개 백테스트 완료
- [ ] DESK4 9개 백테스트 완료
- [ ] DESK5 10개 백테스트 완료
- [ ] DESK1 10개 백테스트 완료
- [ ] regime_at_entry 매핑
- [x] v4_backtest_regime_analysis 테이블·regime_mapped
- [ ] 전략×레짐 매트릭스·BULL 랭킹
- [ ] 1차 최적화 추천값
- [ ] 모의실매매 12개 선정
- [x] DB-SCHEMA.md 업데이트
- [ ] project-docs 보고서 push (GitHub raw 200)

---

## 10. 검증 쿼리 참조

- **세션·거래 수**: `SELECT session_name, COUNT(*) FROM v4_backtest_trades t JOIN v4_backtest_sessions s ON t.session_id = s.session_id WHERE session_name LIKE '%DESK%-regime' AND s.created_at::date = CURRENT_DATE GROUP BY session_name;`
- **regime_at_entry 분포**: 지시서 STEP 3-2.
- **매트릭스**: 지시서 STEP 6-1.
- **BULL 랭킹**: 지시서 STEP 6-2.
