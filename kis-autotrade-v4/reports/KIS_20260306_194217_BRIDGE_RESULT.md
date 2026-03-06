---
project: kis-autotrade-v4
task_id: T-192
completed_at: 2026-03-06 KST
---

# KIS_20260306_194217_BRIDGE RESULT

## 지시서 내용
Task T-192: DESK별 전략 성과 주간 리뷰 + 파라미터 최적화 방향 우선순위
- 우선순위: P2-MEDIUM
- 선행조건: T-187, T-189
- 브랜치: phase-2c-command-center

---

## 실행 단계 및 결과

### 1. 사전 읽기 (CLAUDE.md 필수)

#### HANDOVER.md 읽기
```
cat /root/project-docs/kis-autotrade-v4/HANDOVER.md
```
결과: 정상 읽기 완료. 현재 v10.20 (T-186 Redis 연결 복구). strategy_cards=60, DESK5 20/WATCHING, DESK4 11/WATCHING+7/EXPIRED, DESK3 401/ACTIVE 확인.

[인계 확인]
직전 완료: T-184 (v10.19 — 인프라확인+리서치수집+RES-301~306 시딩)
현재 단계: Phase 2c (Command Center)
CEO 지시 적용: D-001, D-002, D-003, D-004, D-005, D-006
strategy_cards: 60
open_positions: 139 (미청산 모의매매 포지션)

#### CEO-DIRECTIVES.md 읽기
```
cat /root/project-docs/kis-autotrade-v4/CEO-DIRECTIVES.md
```
결과: 정상 읽기 완료. D-001~D-008-KR 지시사항 확인.

---

### 2. 기존 주간 리뷰 보고서 확인

```bash
ls /root/project-docs/kis-autotrade-v4/reports/*WEEKLY* /root/project-docs/kis-autotrade-v4/reports/*REVIEW*20260306* 2>/dev/null
```

결과:
```
/root/project-docs/kis-autotrade-v4/reports/WEEKLY-20260304.md
---EXIT:2
```

→ WEEKLY-20260304.md 존재 (이전 주간 리뷰). 금주(20260306) 리뷰 미수행 확인 → 주간 리뷰 수행

---

### 3. DB 쿼리 실행 결과

#### 3.1 DESK별 현재 풀 상태
```sql
SELECT 'DESK5' as desk, count(*), status FROM v4_desk5_watchlist GROUP BY status
UNION ALL
SELECT 'DESK4', count(*), status FROM v4_desk4_watchlist GROUP BY status
UNION ALL
SELECT 'DESK3', count(*), status FROM v4_desk3_pool GROUP BY status
ORDER BY desk, status;
```

결과:
```
 desk  | count |  status
-------+-------+----------
 DESK3 |   401 | ACTIVE
 DESK3 |     5 | EXPIRED
 DESK4 |     7 | EXPIRED
 DESK4 |    11 | WATCHING
 DESK5 |    20 | WATCHING
```

#### 3.2 v4_mock_trades 테이블 스키마 확인
(strategy_name 컬럼 없음 → strategy_id 컬럼 사용)
```
 id, trade_date, ticker, strategy_id, direction, quantity, entry_price, exit_price, pnl_pct, cost_pct, slippage_pct, kis_order_id, notes, created_at
```

#### 3.3 전략별 7일 성과 (2026-02-28~, 청산건 기준)
```sql
SELECT strategy_id,
       count(*) as trades,
       count(*) FILTER (WHERE exit_price IS NOT NULL) as closed,
       count(*) FILTER (WHERE exit_price IS NOT NULL AND pnl_pct > 0) as wins,
       round(avg(pnl_pct) FILTER (WHERE exit_price IS NOT NULL)::numeric, 3) as closed_avg_pnl,
       round(sum(pnl_pct) FILTER (WHERE exit_price IS NOT NULL)::numeric, 3) as total_pnl
FROM v4_mock_trades
WHERE trade_date >= '2026-02-28'
GROUP BY strategy_id
ORDER BY closed_avg_pnl DESC NULLS LAST;
```

결과:
```
 strategy_id | trades | closed | wins | closed_avg_pnl | total_pnl
-------------+--------+--------+------+----------------+-----------
 D5          |     34 |      1 |    0 |          0.000 |     0.000
 D6          |     34 |     13 |    2 |         -0.433 |    -5.630
 S1          |     16 |      5 |    0 |         -0.470 |    -2.350
 D2          |     16 |      3 |    0 |         -0.470 |    -1.410
 D7          |     34 |      7 |    0 |         -0.788 |    -5.516
 D-ORB       |     34 |     12 |    1 |         -0.801 |    -9.612
 D4          |     16 |      4 |    0 |         -1.021 |    -4.083
```

#### 3.4 전체 모의매매 현황
```
 total_mock_trades | closed | open | wins | losses | pnl_zero
-------------------+--------+------+------+--------+----------
               184 |     45 |  139 |    3 |     39 |        3
```

기간: 2026-03-02 ~ 2026-03-06 (영업일 5일)

#### 3.5 T-096 백테스트 승자 (PF > 2.0, 상위 20건)
```sql
SELECT desk_level, param_key, profit_factor, win_rate, avg_pnl_pct, max_drawdown_pct, backtest_start, backtest_end
FROM v4_desk_backtest_results
WHERE profit_factor > 2.0
ORDER BY profit_factor DESC LIMIT 20;
```

결과:
```
 desk_level |              param_key              | profit_factor | win_rate | avg_pnl_pct | max_drawdown_pct | backtest_start | backtest_end
------------+-------------------------------------+---------------+----------+-------------+------------------+----------------+--------------
 DESK5      | H08_8week_hold_scenario_B           |       25.9327 |   0.8758 |     29.2219 |          92.0257 | 2023-01-02     | 2026-03-04
 DESK5      | H08_8week_hold_scenario_D           |       19.6243 |   0.7895 |     25.8072 |          67.5293 | 2023-01-02     | 2026-03-04
 DESK5      | H08_8week_hold_scenario_C           |       18.8534 |   0.8376 |     33.9175 |          91.3480 | 2023-01-02     | 2026-03-04
 DESK5      | H08_8week_hold_scenario_A           |       10.0000 |   1.0000 |     20.0000 |           0.0000 | 2023-01-02     | 2026-03-04
 3          | task085_scenario_b                  |        4.8843 |  40.0000 |     13.0570 |           4.7736 | 2025-09-06     | 2026-03-05
 0          | T094_SCENARIO_A                     |        4.2620 |   0.5550 |      0.2580 |           0.0010 | 2023-01-01     | 2025-12-31
 0          | T094_SCENARIO_A                     |        4.2620 |   0.5550 |      0.2580 |           0.0010 | 2023-01-01     | 2025-12-31
 3          | phase1_desk3_120d                   |        3.9886 |  43.3000 |      9.3259 |          70.5696 | 2025-09-15     | 2026-03-04
 ...
 DESK5      | H12_pipeline_hold_extend_scenario_D |        3.1461 |   0.6605 |      6.4301 |          99.9911 | 2023-01-02     | 2026-03-04
```

#### 3.6 DESK2 시그널 현황 (2026-03-01 이후)
```sql
SELECT signal_name, count(*) as signal_count, round(avg(dip_pct)::numeric, 3) as avg_dip
FROM v4_desk2_signals WHERE signal_date >= '2026-03-01' GROUP BY signal_name;
```

결과:
```
 signal_name | signal_count | avg_dip
-------------+--------------+---------
 S1          |            3 |   2.233
 T5          |            3 |   0.533
```

날짜별:
```
 2026-03-03 | 6건 | 6종목
 2026-02-27 | 10건 | 2종목
```

#### 3.7 DESK5 프랙탈 트리거 현황
```sql
SELECT stock_code, stock_name, scan_date, total_score, triggers_met, trigger_t5_1, trigger_t5_2, trigger_t5_3
FROM v4_desk5_watchlist ORDER BY total_score DESC LIMIT 10;
```

결과:
```
 383220 | F&F          | 2026-03-03 | 0.6750 | 0 | f | f | f
 0005A0 | 0005A0       | 2026-03-03 | 0.6700 | 0 | f | f | f
 008730 | 율촌화학     | 2026-03-03 | 0.6700 | 0 | f | f | f
 028300 | HLB          | 2026-03-03 | 0.6700 | 0 | f | f | f
 ...
```
→ 20종목 전원 trigger_t5_1/t5_2/t5_3 = false, triggers_met = 0

#### 3.8 DESK4 EXPIRED 7건 상세
```
 084990 | 헬릭스미스         | EXPIRED | triggers_met=2 | score=0.5625
 083420 | 그린케미칼         | EXPIRED | triggers_met=2 | score=0.5425
 104460 | 디와이피엔에프     | EXPIRED | triggers_met=2 | score=0.5250
 012450 | 한화에어로스페이스 | EXPIRED | triggers_met=2 | score=0.5125
 475580 | 에이럭스           | EXPIRED | triggers_met=2 | score=0.5000
 036010 | 아비코전자         | EXPIRED | triggers_met=2 | score=0.4750
 026960 | 동서               | EXPIRED | triggers_met=1 | score=0.4500
```
→ 7건 중 6건이 triggers_met=2 (T4_3 트리거 직전 TTL 만료)

#### 3.9 DESK3 통계
```
 ACTIVE  | 401 | avg_score=0.433 | max=0.699
 EXPIRED |   5 | avg_score=0.231
```
promoted_to_d2 = 0 (파이프라인 미연결)
sec_leader_flag=true: 0건, dual_flow_score>0: 0건

#### 3.10 S1 전략 청산 거래 상세
```
 2026-03-04 | 888604 | S1 | entry=40677 | exit=40677 | pnl=-0.47 | FORCED_CLOSE_EOD
 2026-03-03 | 255707 | S1 | entry=40426 | exit=40426 | pnl=-0.47 | FORCED_CLOSE_EOD
 2026-03-03 | 356628 | S1 | entry=130920| exit=130920| pnl=-0.47 | FORCED_CLOSE_EOD
 2026-03-03 | 199231 | S1 | entry=44401 | exit=44401 | pnl=-0.47 | FORCED_CLOSE_EOD
 2026-03-02 | 187066 | S1 | entry=26735 | exit=26735 | pnl=-0.47 | FORCED_CLOSE_EOD
```
→ 전건 진입=청산 가격, 거래비용(-0.47%)만 발생

#### 3.11 수익 발생 거래 (전체 3건)
```
 2026-03-05 | D6    | 0005G0 | entry=29085 | exit=29345 | pnl=+0.424 | TIMEOUT(60min) @ 17:14:02
 2026-03-05 | D6    | 0005G0 | entry=29100 | exit=29345 | pnl=+0.372 | TIMEOUT(60min) @ 17:30:02
 2026-03-05 | D-ORB | 0005G0 | entry=29150 | exit=29345 | pnl=+0.199 | TIMEOUT(60min) @ 16:46:02
```
→ 전건 2026-03-05 삼성전자우선주(0005G0), VIRTUAL_NXT_PM 세션

---

### 4. 보고서 작성

보고서 파일 생성:
```
/root/kis-autotrade-v4/report/v41/CUR-V41-WEEKLY-DESK-REVIEW-001-20260306.md
```
결과: File created successfully

---

### 5. project-docs 보고서 push

```bash
cp /root/kis-autotrade-v4/report/v41/CUR-V41-WEEKLY-DESK-REVIEW-001-20260306.md \
   /root/project-docs/kis-autotrade-v4/reports/CUR-V41-WEEKLY-DESK-REVIEW-001-20260306.md
```
결과: COPY OK

```bash
sudo /usr/bin/git -C /root/project-docs add kis-autotrade-v4/reports/CUR-V41-WEEKLY-DESK-REVIEW-001-20260306.md
sudo /usr/bin/git -C /root/project-docs commit -m "docs: T-192 DESK별 전략 성과 주간 리뷰 보고서 push (20260306)"
```
결과:
```
[master 247e6ca] docs: T-192 DESK별 전략 성과 주간 리뷰 보고서 push (20260306)
 1 file changed, 340 insertions(+)
 create mode 100644 kis-autotrade-v4/reports/CUR-V41-WEEKLY-DESK-REVIEW-001-20260306.md
COMMIT OK
```

```bash
sudo /usr/bin/git -C /root/project-docs push origin master
```
결과:
```
To github.com:moongoby/project-docs.git
   cbde986..247e6ca  master -> master
PUSH OK
```

GitHub raw URL 확인:
```bash
curl -s -o /dev/null -w "%{http_code}" \
  "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-WEEKLY-DESK-REVIEW-001-20260306.md"
```
결과: **200** ✅

---

### 6. HANDOVER.md 업데이트

#### 섹션 2 "완료된 작업" 테이블에 T-192 행 추가
- 기존 T-186 행 앞에 T-192 행 삽입 완료

#### 섹션 6 "웹 Claude 인수인계" 최신 상태 추가
- v10.21 섹션 추가: T-192 주요 발견사항 요약

#### 버전 이력 추가
- v10.21 행 추가: T-192 완료 내역

```bash
sudo /usr/bin/git -C /root/project-docs add kis-autotrade-v4/HANDOVER.md
sudo /usr/bin/git -C /root/project-docs commit -m "docs: HANDOVER 업데이트 (T-192 완료) v10.21"
sudo /usr/bin/git -C /root/project-docs push origin master
```

결과:
```
[master f76b9ed] docs: HANDOVER 업데이트 (T-192 완료) v10.21
 1 file changed, 17 insertions(+)
To github.com:moongoby/project-docs.git
   247e6ca..f76b9ed  master -> master
HANDOVER PUSH OK
```

HANDOVER.md GitHub raw URL 확인: **200** ✅

---

## 주요 발견 요약

### DESK 풀 현황 (2026-03-06 기준)
| DESK | 상태 | 건수 | 핵심 |
|------|------|------|------|
| DESK5 | WATCHING | 20 | 프랙탈 트리거 20/20 미발동 |
| DESK4 | WATCHING | 11 | 트리거 전원 미발동 |
| DESK4 | EXPIRED | 7 | triggers_met=2 → T4_3 직전 만료 |
| DESK3 | ACTIVE | 401 | DESK2 진입 0건 (파이프라인 단절) |
| DESK3 | EXPIRED | 5 | 낮은 점수 정상 만료 |

### 7일 모의매매 성과
- 총 신호 184건, 청산 45건(24.5%), 수익 3건(1.6%)
- D6 최선(avg -0.433%), D4 최악(avg -1.021%)
- D5: 34건 중 33건 미청산 — exit_manager 거의 미작동
- S1/D2: 전건 FORCED_CLOSE_EOD (진입=청산 가격)

### 최적화 방향 (5개)
1. **P0**: exit_manager MA20 트레일링 스탑 전면 적용
2. **P1**: D5 hold_weeks 8→4주 단축으로 실전 검증 시작
3. **P1**: DESK3→DESK2 파이프라인 실질 연결 복원
4. **P1**: D-ORB/D4 SL 상한 강제 적용 (최악 -3.612% 방어)
5. **P2**: S1 테마그룹핑(T-143) 실효성 재검증

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (코드 변경 없음, 보고서 작성만)
- [x] project-docs 보고서 push 완료 (GitHub raw URL 200 확인)
  - 보고서: 커밋 247e6ca
  - HANDOVER: 커밋 f76b9ed
  - HTTP: 200 ✅

HANDOVER.md 업데이트 완료: f76b9ed
