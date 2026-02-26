# TIMEFRAME-BT-MEDIUM-001 — 10일/15일/1개월 단위 백테스트 + 최적화

**일시:** 2026-02-24 KST  **우선순위:** P0  **자체승인:** O

---

## 1. 설정
- 구간: 2025-01-02 ~ 2026-02-21
- 10D: 14일 캘린더 슬라이딩, 15D: 21일, 1M: 31일
- 엔진: v2, 자본 1천만원, full_compound, 이관 5거래일
- DESK-전략: strategy_cards is_active & backtest_compatible

## 2. 10일 단위 성과
```
   tf   | windows | total_trades | avg_win_rate | sum_pnl 
--------+---------+--------------+--------------+---------
 TF-10D |      29 |         6636 |        20.96 |  677830
(1 row)

```

## 3. 15일 단위 성과
```
   tf   | windows | total_trades | avg_win_rate | sum_pnl 
--------+---------+--------------+--------------+---------
 TF-15D |      19 |         6368 |        21.33 | 1423242
(1 row)

```

## 4. 1개월 단위 성과
```
  tf   | windows | total_trades | avg_win_rate | sum_pnl 
-------+---------+--------------+--------------+---------
 TF-1M |      13 |         6446 |        20.50 |  732586
(1 row)

```

## 5. 시간축 비교 매트릭스
*(STEP 5 콘솔 출력 참조)*

## 6. DESK × 시간축 최적 조합
*(STEP 5 DESK별 출력 참조)*

## 7. 카드 등급표 (A/B/C/D)
*(STEP 5 카드 TOP 10 및 PF 기반)*

## 8. 폐기 후보 / 신규 전략 제안
*(모든 시간축 PF<1.0 카드 폐기 후보, 빈 DESK·시간축 조합 신규 제안)*

## 9. CEO 목표 대비 분석
*(목표 지표 대비 10D/15D/1M 성과)*

---
*(보고서 동기화: cp 본 파일 → project-docs/reports, git commit & push)*
