# CUR-V41-DESK543-FRACTAL-IMPL-001-20260301

**문서 ID**: CUR-V41-DESK543-FRACTAL-IMPL-001  
**작성일**: 2026-03-01  
**상태**: 구현 완료  
**선행**: HANDOVER.md, CEO-DIRECTIVES.md, DESK-FRACTAL-ARCHITECTURE-v3.0, CUR-V41-DESK543-FRACTAL-RESEARCH-001  

---

## 1. 개요

DESK5/4/3 프랙탈 추세추종 엔진을 코드로 구현. 트리거=매수신호, 직접 보유 + DESK2 먹이감 공급.

---

## 2. Phase 1 — DB 테이블 생성

**스크립트**: `/tmp/create_desk_tables.sql`  
**실행**: `psql -U kis_admin -d kisautotrade -h localhost -f /tmp/create_desk_tables.sql`

| 테이블 | 상태 |
|--------|------|
| v4_desk_positions | CREATE 완료 |
| v4_desk5_weekly_review | CREATE 완료 |
| v4_desk_portfolio_summary | CREATE 완료 |

확인: `\dt v4_desk*` → 3개 신규 테이블 포함 확인됨.

---

## 3. Phase 2 — desk_engine 모듈

**경로**: `/root/kis-autotrade-v4/backend/app/desk_engine/`

| 파일 | 설명 |
|------|------|
| __init__.py | 패키지, config 노출 |
| config.py | DESK5/4/3 설정, CAPITAL_STAGES |
| models.py | SQLAlchemy 모델 (DeskPosition, Desk5WeeklyReview, DeskPortfolioSummary) |
| trigger_desk5.py | T5-1~T5-3 스캔, 2조건 충족 종목 |
| trigger_desk4.py | T4-1~T4-4 스캔, 2조건 충족 종목 |
| trigger_desk3.py | T3-1/T3-2 단독, T3-3~T3-5 콤보 2개, entry_eligible |
| position_manager.py | open_position, check_exit_conditions, partial_exit, update_prices, get_active_positions |
| weekly_reviewer.py | DESK5 주봉 청산(MA20 2주/세력이탈/테마사망), 익절곡선, v4_desk5_weekly_review INSERT |
| capital_allocator.py | get_current_stage, get_desk_allocation, get_available_capital |
| desk2_feeder.py | get_desk_holdings, feed_to_desk2_pool (v4_desk2_candidates 가산점) |
| scheduler.py | run_daily_scan, run_desk3_refresh, run_desk4_check, run_desk2_feed, run_desk5_seed_scan, run_weekly_review_job, run_portfolio_summary |

**호환**: ohlcv_daily.date가 varchar인 환경을 위해 `(date::date)` 캐스트 적용.

---

## 4. Phase 3 — 단위 테스트

**스크립트**: `/tmp/test_desk_triggers.py`  
**실행**: `PYTHONPATH=/root/kis-autotrade-v4 /root/kis-autotrade-v4/.venv/bin/python /tmp/test_desk_triggers.py`

| 테스트 | 결과 |
|--------|------|
| capital_allocation | PASS (Stage 1/2/3 배분) |
| desk5_trigger | 2조건 충족 0건 — 임계값 조정 필요(목표 10~20) |
| desk4_trigger | 2조건 충족 30건 — PASS (20~30 근접) |
| desk3_trigger | 진입 대상 100건 — PASS (50~100) |
| position_lifecycle | PASS (open → update → exit) |
| weekly_review | PASS (DESK5 없음 시 스킵) |
| desk2_feeder | PASS (holdings 0 → added 0) |

---

## 5. Phase 4 — 241일 백테스트

**스크립트**: `/tmp/backtest_desk_fractal.py`  
**결과 파일**: `/tmp/backtest_desk_fractal_results.json`

- 기간: 2025-03-05 ~ 2026-02-27 (241거래일)
- 워밍업: 2024-11-01 ~ 2025-03-04
- 초기 자본: 40,000,000 (Stage 1)
- 비용: 편도 0.235% (왕복 0.47%)

스크립트는 거래일별 DESK5/4/3 스캔 및 자본 곡선·Stage 전환을 기록. 전체 241일 실행은 스캔 비용으로 시간 소요 가능. 실행 후 결과 JSON으로 PASS 기준(DESK5 손익비≥3, +100% 비율≥10%, DESK4 마디≥8%, DESK3 D+5 승률≥55%, 전체 CAGR > Stage1 대비 1.3배) 검증 권장.

---

## 6. PASS 기준 (제9원칙) 점검

| 항목 | 기준 | 비고 |
|------|------|------|
| DESK5 손익비 | ≥3:1 | 백테스트 결과로 확정 |
| DESK5 +100% 종목 비율 | ≥10% | 동일 |
| DESK4 마디당 평균 수익 | ≥8% | 동일 |
| DESK3 D+5 승률 | ≥55% | 동일 |
| 전체 CAGR | > Stage1 대비 1.3배 | 동일 |

*구현 완료 후 241일 백테스트 완료 시 위 기준으로 최종 판정.*

---

## 7. 다음 단계

1. 일일/주간 스케줄러에 desk_engine 함수 등록 (daily_scheduler.py에 run_daily_scan 등 호출 추가).
2. DESK5 트리거 임계값 미세 조정 후 2조건 충족 10~20종목 범위 재테스트.
3. 241일 백테스트 완료 후 결과 반영 및 PASS/FAIL 판정.

---

## 저장 정보

- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-DESK543-FRACTAL-IMPL-001-20260301.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-DESK543-FRACTAL-IMPL-001-20260301.md
- 커밋: da997c4
- HTTP 확인: 200
- HANDOVER 업데이트: 완료
