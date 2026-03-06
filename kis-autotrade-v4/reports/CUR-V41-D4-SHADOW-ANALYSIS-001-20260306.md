# CUR-V41-D4-SHADOW-ANALYSIS-001-20260306

## 프로젝트: KIS AutoTrade V4.1
## 날짜: 2026-03-06
## 작성자: Claude Code (T-190)
## 태스크: D4 Shadow Trading 결과 분석 + 실전 전환 판단

---

[인계 확인]
직전 완료: T-192 (DESK별 전략 성과 주간 리뷰)
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: CEO 승인 2026-03-05 (D4 눌림확인 전환+Shadow 해제)
strategy_cards: 60
open_positions: 0 (SELL_FAILED 10건)

---

## 1. 현황 확인 결과

### 1.1 Shadow JSONL 파일 존재 여부
```
ls -la /root/kis-autotrade-v4/logs/shadow/shadow_d4_*.jsonl
→ 파일 0건

ls -la /root/kis-autotrade-v4/logs/shadow/
→ total 24 (디렉토리만 존재, 파일 없음)
→ 디렉토리 생성일: Mar 3 09:54
```

**결론: Shadow JSONL 데이터 없음**

### 1.2 Shadow 로깅 코드 확인 (unified_engine)
```
unified_engine/config.py:52 → SHADOW_STRATEGIES: set = set()
unified_engine/config.py:51 → # D4: CEO 승인 2026-03-05 — 눌림확인 전환 완료 → Shadow 해제, 실전 가동
unified_engine/engine.py:127 → if sig.strategy_id in SHADOW_STRATEGIES: self._log_shadow(sig)
unified_engine/engine.py:224 → SHADOW_LOG_DIR = Path("/root/kis-autotrade-v4/logs/shadow")
```

**현재 상태**: `SHADOW_STRATEGIES = set()` — D4 Shadow 완전 해제, 실전 가동 중

### 1.3 monitor_virtual_run.py Section7 D4 Shadow 섹션
```
line 308: shadow_d4 = self._read_shadow_d4()
line 471: ## 7. D4 Shadow Trading 요약
line 473: > D4: SIG3+SIG6 관찰 모드 (실행 차단) — 2주 누적 후 분봉 리플레이 검증 예정
line 488: def _read_shadow_d4(self) -> dict:
line 491: shadow_dir = Path("/root/kis-autotrade-v4/logs/shadow")
```

Section7 인프라는 정상 구현됨. 그러나 shadow 데이터가 없으므로 `count=0` 출력.

### 1.4 WF-Step1/Step2 / SHADOW 관련 보고서
```
project-docs/kis-autotrade-v4/reports/:
  CUR-V41-ATR-WF-VALIDATION-001-20260302.md    (WF 3-Fold 검증)
  CUR-V41-ATR-NETRR-D4-PIPELINE-ANALYSIS-001-20260302.md
  CUR-V41-D4-ACTIVATION-PREANALYSIS-001-20260302.md
  CUR-V41-EQS-D4-PAPER-ACTIVATE-001-20260301.md
```

---

## 2. Shadow 비활성화 원인 규명

### 2.1 Shadow 활성 기간 이력 (git 커밋 기반)

| 날짜 | 커밋 | 변경 내용 |
|------|------|-----------|
| 2026-03-02 18:45 | `8ff10196` | Shadow 인프라 구축: `SHADOW_STRATEGIES: set = set()` 추가 (기본 비활성) |
| 2026-03-02 18:48 | `610b1b43` | **`SHADOW_STRATEGIES = {"D4"}` 활성화** — WF-Step1 SIG3+SIG6 + Shadow Mode |
| 2026-03-05 05:57 | `7b2bc115` | **`SHADOW_STRATEGIES = set()` — D4 Shadow 해제, 실전 가동 (CEO 승인)** |

**Shadow 활성 거래일**: 2026-03-03(월), 2026-03-04(화) — 2일간

### 2.2 Shadow JSONL 미생성 원인

Shadow JSONL은 `unified_engine/engine.py`의 `run_signal()` 경로를 통해서만 생성됨.
v4_mock_trades 데이터(VIRTUAL_KIS_MOCK 소스)는 별도 mock trading 시스템에서 생성된 것으로,
unified_engine shadow flow와 다른 경로임.

**원인**: Shadow 활성 기간(03-03, 03-04)에 unified_engine이 D4 신호를 발생시키지 않았음
→ unified_engine.log 및 앱 로그에서 [SHADOW] 태그 기록 없음 확인

---

## 3. v4_mock_trades 기반 D4 분석 (VIRTUAL_KIS_MOCK)

Shadow JSONL이 없으므로 v4_mock_trades(source=VIRTUAL_KIS_MOCK)의 D4 데이터로 분석 진행.

### 3.1 전체 현황 (2026-03-02 ~ 2026-03-06, 5일간)

| 항목 | 수치 |
|------|------|
| 총 신호 발생 | 16건 |
| 실행 승인 (approved=true) | 4건 (25%) |
| 실행 차단 (approved=false) | 12건 (75%) |
| 승리 거래 | 0건 |
| **승률 (WR)** | **0.0%** |
| **평균 PnL** | **-1.021%** |
| **Profit Factor (PF)** | **0 (승리 없음)** |
| 최대 손실 | -2.673% |

### 3.2 실행 승인 거래 상세 (4건)

| 날짜 | 종목 | 진입가 | 청산가 | PnL | CS | EQS | 청산 사유 |
|------|------|--------|--------|-----|-----|-----|-----------|
| 2026-03-03 | 612355 | 40,285 | 40,285 | -0.47% | 92 | 72 | FORCED_CLOSE_EOD |
| 2026-03-03 | 437560 | 31,966 | 31,966 | -0.47% | 80 | 63 | FORCED_CLOSE_EOD |
| 2026-03-03 | 220054 | 87,697 | 87,697 | -0.47% | 79 | 43 | FORCED_CLOSE_EOD |
| 2026-03-05 | 001275 | 34,050 | 33,300 | -2.673% | 81 | 61 | SL(2.0%) 16:14 |

**비고**: FORCED_CLOSE_EOD 3건은 당일 가격 변동 없이 거래비용(-0.47%)만 반영됨.

### 3.3 실행 차단 분석 (12건)

| 차단 레이어 | 건수 | 비율 |
|------------|------|------|
| L3.3_SUPPLY (수급 차단: synthetic_BLOCK) | 7건 | 58.3% |
| GATE (반등확인 게이트 미통과) | 3건 | 25.0% |
| SIGNAL_COMBO (신호 조합 미통과 1/2) | 1건 | 8.3% |
| L3.1_FUNNEL (FunnelScore 미달) | 1건 | 8.3% |

**핵심 관찰**: L3.3 수급 차단이 절반 이상(58%)를 차지. GATE 반등확인 미통과 25%는
CEO 승인 2026-03-05의 "눌림확인 전환" 이후 더 강화된 조건.

### 3.4 전략별 비교 (v4_mock_trades 동기간)

| 전략 | 총건수 | 승인건 | 승리 | 평균PnL |
|------|--------|--------|------|---------|
| D2 | 16 | 3 | 0 | -0.470% |
| **D4** | **16** | **4** | **0** | **-1.021%** |
| D5 | 34 | 1 | 0 | 0.000% |
| D6 | 34 | 13 | 2 | -0.433% |
| D7 | 34 | 8 | 0 | -0.691% |
| D-ORB | 34 | 12 | 1 | -0.801% |
| S1 | 16 | 5 | 0 | -0.470% |

---

## 4. 실전 전환 판단

### 4.1 판단 기준 (지시서 기준)
- Shadow PF > 1.5 이고 WR > 30% → 실전 전환 추천

### 4.2 실측값
- Shadow JSONL: **없음 (0건)**
- v4_mock_trades 기반: WR=0%, PF=0 → **수치 기준 미달**

### 4.3 판단: **실전 전환 완료됨 (CEO 선제 승인)**

**이 분석은 "사후 검증" 성격임.**

CEO가 2026-03-05 (커밋 `7b2bc115`)에 이미 D4 실전 전환을 승인하고 파라미터를 재설계하여 배포 완료:
- 진입창: 09:25~10:00 → **09:00~09:30** (전일 상한가 종목 초반 탄력 포착)
- SL: 1% → **2%** (눌림 공간 확보)
- TP: 5% → **3%** (빠른 목표 청산)
- GATE_REQUIRED_STRATEGIES에 D4 추가 (반등게이트 필수화)
- is_pullback_strategy에 D4/D5 추가 (눌림확인 신호 경로)
- ATR 파라미터: SL×1.0/TP×5.0 → **SL×1.5/TP×3.0**

Shadow 데이터가 없었음에도 CEO가 실전 전환을 승인한 근거:
1. WF-Step1 SIG3+SIG6 → 3/3 ALL PASS (2026-03-02 검증)
2. ATR_NETRR=1.5 WF 3-Fold ALL PASS (PF=2.295, MDD=-2.1%)
3. D4 EQS PULLBACK 오분류 버그 수정 (PULLBACK→BREAKOUT, T-130)
4. 눌림확인 전환 파라미터로 구조적 재설계

---

## 5. 종합 권고

| 항목 | 결과 |
|------|------|
| Shadow JSONL 분석 | 불가 (데이터 없음) |
| Mock 거래 실적 | WR=0%, PF=0 (기준 미달) |
| CEO 승인 실전 전환 | **완료** (2026-03-05) |
| 현재 상태 | 실전 가동 중 (`SHADOW_STRATEGIES = set()`) |
| 최종 판단 | **실전 전환 완료 — 사후 모니터링 필요** |

### 5.1 향후 권고사항
1. **1주~2주 실전 실적 모니터링**: D4 눌림확인 전환 후 실제 성과 추적
2. **v4_mock_trades D4 추적 지속**: 현재 WR=0% → 최소 10건 이상 데이터 누적 후 재평가
3. **L3.3 차단 모니터링**: 수급 차단 비율 58% → synthetic_BLOCK 정상화 여부 확인 (T-108 패치 효과)
4. **GATE 통과율 모니터링**: 반등확인 GATE 25% 차단 → 파라미터 조정 여부 검토

---

## 6. 성공 기준 체크

- [x] D4 Shadow 데이터 분석 완료 (데이터 없음 — 원인 규명 포함)
- [x] 실전 전환 판단 근거 제시: **실전 전환 완료 (CEO 선제 승인)**
- [x] 보고서 작성

---

## 부록: 코드 위치 참조

| 항목 | 파일 위치 |
|------|-----------|
| SHADOW_STRATEGIES 설정 | `backend/app/services/unified_engine/config.py:52` |
| Shadow 로깅 구현 | `backend/app/services/unified_engine/engine.py:226` |
| Shadow 집계 함수 | `scripts/monitor_virtual_run.py:488` |
| D4 파라미터 | `backend/app/services/trading/cte/strategy_params.py` |
| D4 신호 매핑 | `backend/app/services/trading/cte/cte_pipeline.py:241` |

HANDOVER.md 업데이트 완료: (push 후 기입 예정)
