# HANDOVER-KIS-V41-DESK2-RESEARCH-20260228

**문서 ID**: HANDOVER-KIS-V41-DESK2-RESEARCH-20260228
**작성일시**: 2026-02-28 KST
**작성자**: Claude Opus 4.6
**인계 대상**: 새 Claude Code 세션
**목적**: DESK2 발굴 연구(Phase 1 → 2 → 2B)의 전체 맥락을 인계하여 3차 테스트 즉시 착수 가능하도록 함

---

## PART 1. 프로젝트 개요

KIS AutoTrade V4.1 — 한국투자증권 API 기반 AI 자동매매 시스템. DESK1~5 멀티 전략 62개 카드 운영. 서버 root@211.188.51.113, 브랜치 phase-2c-command-center, DB PostgreSQL 16 (kisautotrade), Python 3.12, FastAPI.

GO100(백억이) — 동일 서버·DB에서 운영되는 AI 투자 플랫폼. 두 프로젝트가 DB를 공유하므로 GO100 데이터(뉴스, 펀더멘탈 등)를 DESK2 연구에서 즉시 활용 가능.

**필수 규칙**: `kis-v41-*`, `kis-v41-frontend` 서비스 절대 재시작 금지. 실계좌 account_id 5, 6 사용 금지. DB 접근은 `sudo -u postgres python3` 또는 `sudo -u postgres psql -d kisautotrade`.

---

## PART 2. 연구 완료 현황

### 2-1. Phase 1: DESK2-DISCOVERY-PHASE1-001 (02-27)

30일(01-12~02-25) TOP-20 × 30일 = 600건 역추적 분석.

| STEP | 내용 | 핵심 결과 |
|------|------|-----------|
| 1 | TOP-20 추출 | 600건, max_profit 기준, volume≥50K, bars≥60 |
| 2 | 패턴 안정성 | 7/8 메트릭 3%p 이내 — 안정 |
| 3 | 생애주기 분석 | TREND(peak@190min), REVERSAL(130min), BORDER(210min) |
| 4 | 클러스터링 | k=4, silhouette 0.153 |
| 5 | 가설 검증 | TOP-20 WR 78.7% vs Random 45.9% — **발굴이 수익 결정** |

산출물: `/tmp/discovery_p1_top600.json`, `/tmp/discovery_p1_lifecycle.json`, `/tmp/discovery_p1_clusters.json`, `/tmp/discovery_p1_hypothesis.json`

### 2-2. Phase 2: DESK2-DISCOVERY-PHASE2-001 (02-28)

19변수 확장 스코어카드, 1,192건(TOP 594 + CTRL 598).

| STEP | 결과 |
|------|------|
| 2 | 11변수 선별 (AUC ≥ 0.55), M2 AUC 0.752 최강 |
| 3 | In-sample TOP-10 precision 74.7% |
| 4 | OOS TOP-10 precision **76.0%**, WR 61.3% |
| 5 | TREND WR 67.7%, REVERSAL WR 55.2% |
| 6 | Extended vs Original: precision +15.3%p |

결론: 2/5 PASS (FAIL). WR 병목은 09:05 고정 진입.

산출물: `/tmp/discovery_p2_features.json`, `/tmp/discovery_p2_outsample_summary.json`

### 2-3. Phase 2B: DESK2-DISCOVERY-PHASE2B-001 (02-28)

5개 PART 심층 연구.

**PART A — DB 전수 조사**: 225 테이블 카탈로그. Phase 2에서 "없다"고 보고된 데이터 3건 모두 존재 확인:
- 외국인/기관 순매수: `v4_investor_daily` (261K행, 2010~현재)
- 시장 레짐: `v4_market_regime_daily` (822행, KOSPI/KOSDAQ별)
- 장전 뉴스: `go100_news_items` (data_time < 09:00, 15K건)

**PART B — 추가 변수 12개**: 6개 선별. X9(섹터 TOP-20 수) AUC **0.851** 압도적. 외국인/기관(X11/X12) AUC 0.50 무효.

**PART C — REVERSAL 원인 분류**:
- A(전일과열→이익실현) 20%, B(갭업→기대미달) 14%, C(시장동반) 28%, D(기타) 39%
- **모든 원인에서 MFE≥5% 93~100%** — REVERSAL은 "문제가 아니라 기회"

**PART D — 정밀도 90% 달성**:
- L3(30일 TOP-20 등장 횟수) 단독 랭킹: OOS 8.3/10 (83%)
- **L3 + X9(섹터 TOP-20 ≥ 1) 필터: OOS 9.0/10 (90%)**
- 핵심: 11변수 가중합(76%) < L3 단독(83%) < L3+X9(90%)

**PART E — 생애주기 150건 분석**:
- **Birth+1min 진입**: 전체 WR 95.3%, avg PnL +2.27%
  - TREND: WR 91%, PnL +2.07%
  - REVERSAL: WR **100%**, PnL +2.57%
  - BORDER: WR **100%**, PnL +2.40%
- 실패 종목의 birth가 압도적으로 늦음 (REVERSAL: 성공 1.2분 vs 실패 44.1분)

산출물: `/tmp/discovery_p2b_extra_features.json`, `/tmp/discovery_p2b_reversal_analysis.json`, `/tmp/discovery_p2b_precision90.json`, `/tmp/discovery_p2b_lifecycle.json`

---

## PART 3. 현재 설계 (DESIGN-SPEC v3.0)

### 3-1. 발굴 파이프라인

```
D-1 장 마감 후:
  1. L3(30일 TOP-20 등장 횟수) 전 종목 계산
  2. L3 TOP-50 추출
  3. X9(동일 섹터 TOP-20 수 ≥ 1) 필터
  4. TOP-10 확정 → v4_desk2_candidates
```

### 3-2. 진입 파이프라인

```
D-day 09:00~09:30:
  1. 10종목 1분봉 실시간 모니터링
  2. 양봉 전환(close > open) 감지 = Birth 근접
  3. 양봉 확인 → +1분 시장가 진입
  4. 09:30까지 미감지 → SKIP
```

### 3-3. 청산 규칙

| 유형 | TP | SL | TIME |
|------|----|----|------|
| TREND | +3% (또는 trailing -2%) | -3% | 14:30 |
| REVERSAL | **+5%** (MFE 26.6%) | -3% | 14:30 |
| BORDER | +3% | -3% | 14:30 |

---

## PART 4. 다음 세션 우선 작업

### 4-1. 3차 테스트 (최우선)

30일이 아닌 **3개월(2025-12 ~ 2026-02)** 순방향 시뮬레이션:
- L3+X9 발굴 → Birth+1min 진입 → 유형별 청산
- 매일 10종목 × ~60 거래일 = ~600 trades
- 목표: WR ≥ 80%, avg PnL ≥ +1.5%, 정밀도 ≥ 85%

### 4-2. Birth 감지 정확도 측정

양봉 전환(1분봉 close > open)이 실제 Birth Point에 얼마나 근접한지 150건으로 오차 측정.

### 4-3. 엔진 코드 구현

- `scripts/desk2/desk2_prescoring.py` — L3+X9 발굴
- `scripts/desk2/desk2_birth_detector.py` — Birth Point 감지
- `scripts/desk2/desk2_config.yaml` — v3.0 설정

---

## PART 5. 주요 파일 위치

### 보고서 (project-docs)
| 파일 | 경로 |
|------|------|
| Phase 1 보고서 | `kis-autotrade-v4/reports/DESK2-DISCOVERY-PHASE1-001-20260227.md` |
| Phase 2 보고서 | `kis-autotrade-v4/reports/DESK2-DISCOVERY-PHASE2-001-20260228.md` |
| Phase 2B 보고서 | `kis-autotrade-v4/reports/DESK2-DISCOVERY-PHASE2B-001-20260228.md` |
| DESIGN-SPEC v2.0 | `kis-autotrade-v4/design/DESK2-DESIGN-SPEC-v2.0-20260227.md` |
| DESIGN-SPEC v3.0 | `kis-autotrade-v4/design/DESK2-DESIGN-SPEC-v3.0-20260228.md` |
| ROLE-DEFINITION | `kis-autotrade-v4/design/DESK-ROLE-DEFINITION-v1.0-20260227.md` |
| DB 카탈로그 | `kis-autotrade-v4/design/DB-TABLE-CATALOG-v1.0-20260228.md` |
| BLANK-SLATE | `kis-autotrade-v4/reports/DESK2-BT-BLANK-SLATE-001-20260227.md` |

### 분석 스크립트 (/tmp/)
| 파일 | 내용 |
|------|------|
| `discovery_p1_step1~5.py` | Phase 1 STEP 1~5 |
| `discovery_p2_step1.py` | Phase 2 STEP 1 (19변수 추출) |
| `discovery_p2_step2to6.py` | Phase 2 STEP 2~6 통합 |
| `discovery_p2b_partB.py` | Phase 2B PART B (추가 변수) |
| `discovery_p2b_partC.py` | Phase 2B PART C (REVERSAL 원인) |
| `discovery_p2b_partD.py` | Phase 2B PART D (정밀도 90%) |
| `discovery_p2b_partE.py` | Phase 2B PART E (생애주기) |

### JSON 산출물 (/tmp/)
| 파일 | 내용 |
|------|------|
| `discovery_p1_top600.json` | 30일 TOP-20 600건 |
| `discovery_p1_lifecycle.json` | 600건 생애주기 |
| `discovery_p2_features.json` | 1,192건 × 19변수 |
| `discovery_p2b_extra_features.json` | 1,192건 × 추가 12변수 |
| `discovery_p2b_reversal_analysis.json` | REVERSAL 111건 원인 분석 |
| `discovery_p2b_precision90.json` | 정밀도 90% 시뮬레이션 |
| `discovery_p2b_lifecycle.json` | OOS 150건 생애주기 |

---

## PART 6. 핵심 인사이트 (새 세션 필독)

1. **"복잡한 모델보다 단순한 규칙이 낫다"**: 4변수(56%) < 11변수(76%) < **L3 단독(83%)** < **L3+X9(90%)**
2. **"발굴은 해결됐다, 진입이 병목이었다"**: 정밀도 90% 달성해도 09:05 고정 진입 WR 63%. Birth+1min으로 95%.
3. **"REVERSAL은 문제가 아니라 최고의 기회"**: Phase 2에서 FAIL 판정했으나, Birth+1min 시 WR 100%, PnL +2.57%.
4. **"외국인/기관 매매는 당일 급등 예측에 무관"**: AUC 0.50 — 전일 수급은 정보가 아니다.
5. **"실패 종목은 birth가 늦다"**: 09:30 데드라인으로 대부분 실패 종목 자동 SKIP.

---

*HANDOVER-KIS-V41-DESK2-RESEARCH-20260228 작성 완료*
