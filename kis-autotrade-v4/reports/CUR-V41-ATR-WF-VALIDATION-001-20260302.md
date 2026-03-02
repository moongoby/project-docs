# CUR-V41-ATR-WF-VALIDATION-001-20260302

## 프로젝트: KIS AutoTrade V4.1
## 날짜: 2026-03-02
## 작성자: Cursor AI
## 태스크: ATR_NETRR 1.5 완화 Walk-Forward 3-Fold 검증 + D4/D7 구조 분석

---

## 1. WF 3-Fold 검증 결과 (ATR_NETRR = 1.5)

```
Walk-Forward 3-Fold (ATR_NETRR=1.5):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fold1: PF=2.175  Sharpe=10.128  MDD=-3.2%  OOS/IS=0.98  PF_Drop=2.0%    ✅
Fold2: PF=2.448  Sharpe=11.004  MDD=-1.4%  OOS/IS=1.22  PF_Drop=-21.6%  ✅
Fold3: PF=2.263  Sharpe=11.967  MDD=-1.7%  OOS/IS=1.03  PF_Drop=-3.1%   ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
평균:  PF=2.295  Sharpe=11.033  MDD=-2.1%
판정:  **GO ✅** (PF≥1.5 기준 충족, 3개 Fold 모두 PF>2.0)
OOS/IS≥0.6: 3/3  PF Drop≤50%: 3/3
```

## 2. ATR 2.0 vs 1.5 최종 비교

| 항목 | 현행(2.0) | 완화(1.5) | 판정 |
|------|-----------|-----------|------|
| 실행 건수 | 731건 | 1,066건 | ✅ +45.8% |
| 일평균 | 3.01건/일 | 4.39건/일 | ✅ |
| WR | 65.7% | 61.3% | ⚠️ -4.4% |
| 전체 PF | 2.398 | 2.248 | ✅ 2.0 이상 유지 |
| WF 3-Fold | - | 3/3 PASS | ✅ |
| MDD | - | -2.1% | ✅ 안정 |
| Sharpe | - | 11.033 | ✅ 우수 |
| ATR 차단 | 849건 | 8건 | ✅ -841건 |

## 3. CEO 승인 요청 사항

**변경 파일**: `backend/app/services/trading/cte/atr_dynamic_exit.py:42`
**변경 내용**: `NET_RR_RATIO = 2.0` → `NET_RR_RATIO = 1.5`
**효과**: 거래수 +46% (3.01→4.39건/일), PF 2.0 이상 유지
**검증**: WF 3-Fold ALL PASS (PF 2.295, Sharpe 11.03, MDD -2.1%)
**복구**: 1줄 복귀로 즉시 원상복구 가능

> **상태: CEO 승인 대기** (코드 레포 직접 수정 → CEO 승인 필요)

---

## 4. D4 전략 구조 분석

### 4.1 차단 구조 (ATR 1.5 적용 후)

D4 80건 (→ ATR 1.5로 43건 해소 후):
```
├─ SIGNAL_COMBO 차단: 35건 (44%) — SIG5(VP_120%) + SIG6(VWAP) min 2/2
│   └─ SIG5(VP_120_RECOVERY): 전상 종목 VP 120일선 대비 고가 → 구조적 미충족
├─ L4.5_EQS 차단: 22건 (28%) — EQS < 35 시 REJECT
│   └─ 전상 종목 매도 압력 → EQS 구조적 저평가
└─ ATR_NETRR 차단: (1.5 적용 후 해소됨)
```

코드 위치:
- `cte_pipeline.py:241`: D4 SIGNAL_MAP = [SIG5_VP_120_RECOVERY, SIG6_VWAP_SUPPORT], min_count=2
- `execution_quality_score.py:398`: EQS REJECT < 35

### 4.2 D4 활성화 방안 (별도 세션)

1. D4 전용 SIGNAL_COMBO: SIG5 제거 또는 전상 종목 특성 신호로 대체
2. D4 전용 EQS 임계값: 35 → 25로 완화
3. 위 조합으로 리플레이 재검증 필요

---

## 5. D7 슬롯 경쟁 분석

- **백테스트 시뮬**: INTRADAY_LIMIT=8, PER_STRATEGY_LIMIT=3 (시간대 미구분)
- **실전 엔진**: CONCURRENT_LIMIT=5
- **핵심 발견**: D7은 14:30 이후 진입(EOD), D2는 09:00~14:00 장중 진입 → 실전에서는 시간대 분리로 경쟁 없음
- **결론**: ATR 1.5 적용 시 D7 -117건 감소는 시뮬레이터 한계(시간대 미구분). 실전에서는 무관.

---

## 6. 대기 항목 정리

| # | 항목 | 상태 | 다음 액션 |
|---|------|------|-----------|
| 1 | ATR 1.5 production 적용 | CEO 승인 대기 | 승인 시 코드 1줄 변경 |
| 2 | D4 활성화 | ATR 적용 후 | SIGNAL_COMBO + EQS 완화 별도 세션 |
| 3 | 03-03 Virtual Run | 자동 실행 | L3.3 실측 데이터 수집 |
| 4 | L3.3 Live 통과율 확인 | Virtual Run 1주 후 | 역사적 17% vs Live 58% 검증 |

---

## 7. 보안 스캔 결과

- security_scan: PASS
- path_check: PASS
- commit SHA: (push 후 기입)

---

*보고서 생성: 2026-03-02 | 태그: [KIS]*
