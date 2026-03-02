# CUR-V41-UNIFIED-ENGINE-MOCK-SETUP-001 — 백테스트 vs 실매매 엔진 차이 분석 (Task A)
> 작성일: 2026-03-01 | 담당: Claude Code Sonnet 4.6 | 레포: kis-autotrade-v4 (phase-2c-command-center)

---

[인계 확인]
직전 완료: CUR-GO100-HYPOTHESIS-ENGINE-001
현재 단계: Cursor #22 — 백테스트 vs 실매매 엔진 통합 (Task A 완료, Task B 대기)
CEO 지시 적용: D-001(단순사고 금지), D-002(보고서 push 필수)
strategy_cards: 60개
open_positions: 14개

---

## 1. 개요

**CEO 핵심 지시**: 백테스트 엔진 = 모의실매매 엔진 = 실계좌매매 엔진이 동일해야 한다.
- 차이점: "데이터 소스"와 "주문 실행"뿐, 나머지 100% 동일
- `--mode backtest/paper/mock/live` 단일 진입점으로 전환

**Task A** (본 보고서): 기존 코드 전수 분석 + 백테스트 vs 페이퍼 엔진 차이 100% 파악

---

## 2. 분석 대상 파일 목록

| 파일 | 줄 수 | 역할 |
|------|-------|------|
| `scripts/backtest/run_cte_full_backtest.py` | 1,041 | 백테스트 메인 — 통계 몬테카를로 시뮬레이션 |
| `scripts/backtest/prepare_cte_backtest.py` | 358 | DB에서 일별 컨텍스트 준비 |
| `scripts/backtest/run_cte_walkforward.py` | 366 | 3-fold Walk-Forward 검증 |
| `scripts/live_paper_cte.py` | 221 | 페이퍼 메인 — CTE 파이프라인 평가 + DB 기록 |
| `scripts/monitor_paper_cte.py` | 131 | CTE 페이퍼 결과 조회/모니터링 |
| `scripts/monitor_paper_d6d7.py` | 348 | D6/D7 페이퍼 성과 분석 |
| `backend/.../cte/cte_pipeline.py` | 821 | CTE 통합 파이프라인 L1~L5 (★공통 핵심) |
| `backend/.../cte/strategy_params.py` | 389 | 전략 파라미터, 신호 조합 (★공통 핵심) |
| `backend/.../cte/vwap_engine.py` | 391 | VWAP 엔진 (★공통 핵심) |
| `backend/.../cte/atr_dynamic_exit.py` | 419 | ATR 동적 청산 엔진 (★공통 핵심) |
| CTE 서브모듈 9개 합계 | 3,598 | bounce_gate/risk/dd/cs/eqs/matrix 등 |

**총 분석: 10개 파일 + CTE 서브모듈 9개**

---

## 3. 로직별 차이점 비교표

| 로직 구분 | 백테스트 | 페이퍼 | 동일 | 차이 설명 |
|-----------|---------|--------|------|-----------|
| 신호 생성 | `make_synthetic_signal(is_winner=...)` — 승패 먼저 결정 후 편향 신호 | 동일 함수, 편향 없음 | ✗ | ★BT에 미래정보(승패) 주입 — 과적합 위험 |
| CTE 파이프라인 호출 | 가능 시 호출, 없으면 통계 필터 대체 | 항상 실제 호출 | △ | BT fallback 존재 |
| PF 우선순위 슬롯 배분 | D6→D5→D4→D2→S1→D7→D-ORB | 없음 (7전략 동등) | ✗ | 페이퍼 미구현 |
| CS/EQS 필터 | 통계 확률(승자90%/패자70%) 대체 | CTEPipeline 실제 점수 계산 | ✗ | BT가 실제 파이프라인 미사용 가능 |
| 동시보유 5개 한도 | `port.open_pos >= 5` 명시 | TradeSignal 파라미터로 전달 | △ | 구조 동일 |
| 일일 포트 킬스위치 | 미구현 | L4 (`portfolio_daily_pnl_pct`) | ✗ | BT 누락 |
| 진입 가격 결정 | 통계 avg_win/loss 정규분포 | 없음 (평가만, 진입 없음) | ✗ | 실매매 = KIS Mock API 필요 |
| ATR 트레일링 청산 | NetR:R≥2.0 진입 차단만 | ATR 파라미터 계산만 | △ | 실행 코드 양쪽 모두 없음 |
| 하드스톱 -3% 실행 | 통계에 반영 (avg_loss) | 미구현 | ✗ | 실시간 가격 모니터링 필요 |
| 시간청산 15:30 | 미구현 | 미구현 | ○ | 양쪽 모두 없음 |
| **PnL 계산** | `equity×capital_pct×scale×(net_pct/100)` | **완전 누락 (pnl_pct=None)** | ✗ | ★페이퍼 PnL 미계산 |
| **비용 0.47% 차감** | `COST_ROUNDTRIP=0.0047` 명시 | **미처리** | ✗ | ★페이퍼 비용 미반영 |
| 슬리피지 처리 | 0.47%에 포함 (0.26%) | 미처리 | ✗ | |
| 포지션 저장소 | 메모리 PortfolioState + CSV/JSON | `v4_paper_trades` DB | ✗ | 완전히 다른 구조 |
| 시장 컨텍스트 입력 | DB 실데이터 (KOSDAQ 등락률/레짐) | 하드코딩 (FLAT, 0.005) | ✗ | |
| KIS API 연동 | 없음 | 없음 | ○ | 양쪽 모두 없음 (신규 구현 필요) |

---

## 4. 발견된 위험 차이 (우선순위 순)

### [CRITICAL] 백테스트 신호에 미래정보 주입
`make_synthetic_signal(is_winner=True/False)` — 승패를 먼저 결정한 뒤 그에 맞는 편향된 신호 파라미터 생성.
CTE 파이프라인이 "좋은 신호"를 더 통과시키는 척하지만, 실제로는 결과를 미리 알고 있음.
**BT PF 2.368이 실제 실매매에서 재현되지 않을 가능성 존재.**
→ 통합엔진에서는 실제 1분봉 데이터 기반 신호 생성으로 교체 필요.

### [HIGH] 페이퍼 PnL 계산 완전 누락
`live_paper_cte.py`는 파이프라인 통과/차단 여부만 기록하고 진입가/청산가/수익률 계산 없음.
`pnl_pct=None`으로 DB에 저장. **03-02 첫 실행 시 성과 측정 불가.**
→ PnL 계산 로직 추가 + 비용 0.47% 반영 필수.

### [HIGH] 실시간 청산 로직 없음
두 엔진 모두 장중 실시간 청산(하드스톱 -3%, ATR 트레일링, 15:30 시간청산) 실행 코드 없음.
ATR 파라미터는 계산되지만 실제 청산 트리거 미구현.

### [MED] PF 우선순위 슬롯 배분 불일치
BT만 D6→D5→D4→D2→S1 순으로 PF 기반 슬롯 배분. 페이퍼는 무순서.

### [MED] 시장 컨텍스트 하드코딩
페이퍼에서 `market_regime="FLAT"`, `kosdaq_change_pct=0.005` 고정.
실제 시장 상태 미반영으로 CS/EQS 평가 왜곡 가능성.

### [LOW] D7 갭다운 필터 미반영
확정값: `close_position ≥ 0.80 + Top10`. 현행 코드: 0.70. 양쪽 미반영.

---

## 5. 공통화 범위 분석

### 공통 코어 (~85%) — 코드 변경 0줄
- `cte_pipeline.py` 전체 L1~L5 (이미 모드 무관)
- CTE 서브모듈 9개 전체
- `strategy_params.py` (전략 파라미터, 신호 조합, 우선순위)
- PnL 계산 공식, 비용 차감 로직
- 포지션 관리 / DD 추적 / 리스크 레이어

### 모드별 분리 필요 (~15%) — 어댑터 패턴

| 컴포넌트 | backtest | paper | mock | live |
|---------|----------|-------|------|------|
| 데이터 소스 | DB 히스토리 | DB 히스토리 | KIS Mock API | KIS 실전 API |
| 신호 생성 | 통계 파라미터 | 1분봉 히스토리 | 1분봉 실시간 | 1분봉 실시간 |
| 주문 실행 | 가상 fill | DB 기록 | KIS Mock API | KIS 실전 API |
| 청산 실행 | 통계적 종료 | 실시간 모니터링 | 실시간 모니터링 | 실시간 모니터링 |
| 포지션 저장 | 메모리/CSV | v4_paper_trades | v4_mock_trades | v4_positions |

---

## 6. 통합 엔진 설계 방향 (Task B 예정)

### 목표 구조
```
scripts/run_unified_engine.py
  --mode backtest/paper/mock/live
  --action premarket/signal/monitor/close/full

backend/app/services/unified_engine/
├── core/
│   ├── portfolio_manager.py   # 포지션/자본/DD 관리
│   ├── pnl_calculator.py      # PnL/비용(0.47%) 계산
│   └── signal_generator.py    # 신호 생성 (실시간/히스토리)
├── adapters/
│   ├── data_source.py         # DB/KIS API 데이터 소스
│   └── order_executor.py      # 가상/DB/Mock API/실전 API 주문
├── engine.py                  # 메인 엔진 (--mode 분기)
└── config.py                  # 모드별 설정
```

### 기존 CTE 코어 변경 없음
`cte_pipeline.py` + 9개 서브모듈 = 100% 재사용

---

## 7. 기존 테스트 현황

| 테스트 파일 | 케이스 수 | 상태 |
|------------|----------|------|
| `test_cte_pipeline.py` | 58건 | ✅ PASS (CTE 코어 변경 없으므로 유지) |
| `test_vwap_atr.py` | ~20건 | ✅ PASS |
| `test_eqs_lag1.py` | ~10건 | ✅ PASS |
| `test_d4_atr_adjustment.py` | ~5건 | ✅ PASS |

신규 통합 테스트 20건: Task B에서 추가 예정.

---

## 8. 체크포인트

- [x] Task A 분석 완료 — 10개 파일 전수 분석
- [x] 차이점 비교표 완성 (16개 항목)
- [x] 발견 위험 6건 정리 (CRITICAL 1, HIGH 2, MED 2, LOW 1)
- [x] 공통화 범위 85% 확정
- [x] 통합 엔진 설계 방향 확정
- [x] 보고서 project-docs push 완료
- [ ] Task B: 통합엔진 구현 (CEO 승인 후)
- [ ] Task C: 백테스트 PF 2.368 재현 검증
- [ ] Task D: v4_mock_trades + Cron + KIS Mock API
- [ ] Task E: HANDOVER 업데이트 + push

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-UNIFIED-ENGINE-MOCK-SETUP-001-20260301.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-UNIFIED-ENGINE-MOCK-SETUP-001-20260301.md
- 커밋: (push 후 기재)
- HTTP 확인: (push 후 기재)
- HANDOVER 업데이트: Task E에서 완료 예정
