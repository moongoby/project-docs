# CUR-V41-DESK543-FRACTAL-RESEARCH-001-20260301

**문서 ID**: CUR-V41-DESK543-FRACTAL-RESEARCH-001  
**작성일**: 2026-03-01  
**상태**: Task 0~4 실행 완료 (60일 샘플)  
**선행 문서**: HANDOVER.md, CEO-DIRECTIVES.md, DESK-FRACTAL-ARCHITECTURE-v2.0-20260301.md  

---

## 1. 개요

DESK5/4/3 프랙탈 추세추종 — **일봉 트리거 실증 연구** 1차 결과 및 실행 가이드.

- **최종 목표**: 일봉 파동(1파→2파→3파) 직접 보유 + 비중 피라미딩, DESK2 분봉 수확과의 이중 수확·복리 순환 실증.
- **트리거 = 매수 신호** (풀에 넣는 것이 아니라 돈을 넣는다).
- **금지**: V4.1 backend/ 수정, 기존 테이블 스키마 변경, look-ahead 사용.

---

## 2. Task 0 — 사전 데이터 검증 결과 (완료)

실행: `python3 /tmp/task0_data_validation.py`  
결과 파일: `/tmp/task0_data_validation.json`  
**판정: PASS**

### 2.1 v4_investor_daily

| 항목 | 결과 |
|------|------|
| 기관 컬럼 | `institution_net_qty` 존재 |
| 외인 컬럼 | `foreign_net_qty` 존재 |
| 총 행 수 | 261,410 |
| institution_net_qty NULL 건수 | 0 |
| foreign_net_qty NULL 건수 | 0 |
| NULL 비율 | 0% |

→ T5-2(기관/외인 15/20일 순매수) 조건 사용 가능. **대안 설계 불필요.**

### 2.2 go100_news_items

| 항목 | 결과 |
|------|------|
| category_code | 존재 |
| is_disclosure | 존재 |
| 총 행 수 | 2,148,278 |
| 공시(is_disclosure=true) 건수 | 102,143 |
| 실적(category_code='04') 건수 | 127,913 |

→ T3-3/T3-6(공시/실적·뉴스 burst) 분류 가능. **대안 설계 불필요.**

### 2.3 ohlcv_daily — 급등 정의 확정

| 항목 | 결과 |
|------|------|
| 급등 정의 | 당일 종가 기준 전일 대비 +10% 이상 |
| 기준 구간 | 최근 241거래일 (window_start: 2025-03-05, last_date: 2026-02-27) |
| 급등(+10% 이상) 건수 | 9,483 |

---

## 3. Task 1~4 실행 결과 (60일 샘플)

**실행 환경**: SIM_DAYS=60, DB 연동(환경변수 DATABASE_URL_SYNC/DATABASE_URL).

### 3.1 Task 1 — DESK5 트리거 실증

| 항목 | 값 |
|------|-----|
| 스크립트 | `/tmp/task1_desk5_bulk.py` (벌크 최적화) |
| 출력 | `/tmp/task1_desk5_results.json` |
| 시뮬 거래일 | 60일 |
| 진입 건수 | 9,958 |
| 일평균 풀 크기 | 166 (목표 10~20 초과) |
| D+20 승률 | 23.0% |
| D+40 승률 | 36.0% |
| D+60/D+90/D+120 | 60일 샘플 한계로 미측정(n=0) |
| False Positive | — |
| **PASS** | **미판정** (D+60 데이터 부재로 241일 전수 실행 필요) |

→ 60일만으로는 D+60 기준(승률≥40%, 중앙값≥15%) 검증 불가. **241일 실행 권장.**

### 3.2 Task 2 — DESK4 트리거 실증

| 항목 | 값 |
|------|-----|
| 스크립트 | `/tmp/task2_desk4_empirical.py` |
| 출력 | `/tmp/task2_desk4_results.json` |
| 시뮬 거래일 | 60일 |
| 진입 건수 | 53,136 |
| 일평균 풀 크기 | 885.6 (목표 20~30 대비 과다) |
| D+20 승률 | 11.5% |
| D+40 승률 | 28.0% |
| **PASS** | **FAIL** (D+20 승률 45% 미달) |

→ 풀 크기·조건 완화 필요 시 T4-1~T4-4 중 3개 충족 등 **조건 강화 검토.**

### 3.3 Task 3 — DESK3 트리거 실증

| 항목 | 값 |
|------|-----|
| 스크립트 | `/tmp/task3_desk3_empirical.py` |
| 출력 | `/tmp/task3_desk3_results.json` |
| 시뮬 거래일 | 60일 |
| 진입 건수 | 2,747 |
| 일평균 풀 크기 | 45.8 |
| D+5 승률 | 0.6% |
| D+10 승률 | 0.4% |
| **PASS** | **FAIL** (D+5 승률 55% 미달) |

→ T3-3/T3-6(뉴스) 미적용·T3-5 단순화 적용. **뉴스 조건 및 진입 필터 재검토 권장.**

### 3.4 Task 4 — 이중 수확 시뮬레이션

| 항목 | 값 |
|------|-----|
| 스크립트 | `/tmp/task4_dual_harvest.py` |
| 출력 | `/tmp/task4_dual_harvest_results.json` |
| DESK2 241일 | 수익 +1.5%, MDD 7.8% (CROSS-RELAY-PRESIM 기준) |
| Stage1 연수익(근사) | 2.27% (DESK2만) |
| Stage2 연수익(근사) | 5.31% (D2 60%+D3 30%+D4 10%) |
| Stage3 연수익(근사) | 13.52% (전 DESK) |
| **PASS** | **PASS** (Stage2 > Stage1×1.3) |

→ 자본 단계별 이중 수확 구조(Stage2 > Stage1×1.3) **충족.**

---

## 4. Task 1~4 스크립트 및 재실행 가이드

분석 스크립트는 **backend 수정 없이** `/tmp/` 에 배치.

| Task | 스크립트 | 결과 JSON | 비고 |
|------|----------|-----------|------|
| 0 | `/tmp/task0_data_validation.py` | `/tmp/task0_data_validation.json` | 사전 검증 |
| 1 | `/tmp/task1_desk5_bulk.py` | `/tmp/task1_desk5_results.json` | SIM_DAYS=60 또는 241 |
| 2 | `/tmp/task2_desk4_empirical.py` | `/tmp/task2_desk4_results.json` | SIM_DAYS=60 |
| 3 | `/tmp/task3_desk3_empirical.py` | `/tmp/task3_desk3_results.json` | SIM_DAYS=60 |
| 4 | `/tmp/task4_dual_harvest.py` | `/tmp/task4_dual_harvest_results.json` | Task 1~3 결과 의존 |

---

## 5. PASS 기준 종합표

| DESK | 측정 | 기준 | 의미 |
|------|------|------|------|
| DESK5 | D+60 승률 | ≥ 40% | 1파 바닥 진입 유효 |
| DESK5 | D+60 중앙값 | ≥ +15% | 장기 보유 가치 |
| DESK5 | False Positive | < 50% | 절반 이상 실제 상승 |
| DESK4 | D+20 승률 | ≥ 45% | 2파 추매 유효 |
| DESK4 | 피라미딩 MDD | < 단일 × 1.3 | 추매 리스크 과도하지 않음 |
| DESK3 | D+5 승률 | ≥ 55% | 3파 폭발 포착 정확 |
| DESK3 | 피라미딩 Sharpe | ≥ 1.5 | 3단계 피라미딩 유효 |
| 이중수확 | Stage2 > Stage1×1.3 | 연수익 비교 | 일봉+분봉 이중구조 우위 |

### 60일 샘플 판정 요약

| Task | PASS 기준 | 60일 결과 | 판정 |
|------|----------|----------|------|
| Task 1 DESK5 | D+60 승률≥40%, 중앙값≥15% | D+60 미측정 | 미판정 |
| Task 2 DESK4 | D+20 승률≥45% | 11.5% | FAIL |
| Task 3 DESK3 | D+5 승률≥55% | 0.6% | FAIL |
| Task 4 이중수확 | Stage2 > Stage1×1.3 | 5.31% > 2.95% | **PASS** |

---

## 6. Task 0 산출물 요약

- `/tmp/task0_data_validation.json`: v4_investor_daily·go100_news_items·ohlcv_daily 검증 결과, pass=true, fail_reasons=null.

---

## 7. 다음 단계

1. **Task 1 241일 전수 실행**: `SIM_DAYS=241 python3 /tmp/task1_desk5_bulk.py` 로 D+60 승률·중앙값·False Positive 확정.
2. **Task 2 조건 강화**: T4 4개 중 3개 충족 또는 풀 크기 20~30 목표에 맞게 필터 조정 후 재실행.
3. **Task 3 뉴스·필터**: T3-3/T3-6(go100_news_items) 연동 및 T3-5 정교화 후 D+5 승률 재측정.
4. **Task 5**: 본 보고서 갱신분 커밋·push (이미 D-012·HANDOVER 반영 완료).

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-DESK543-FRACTAL-RESEARCH-001-20260301.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-DESK543-FRACTAL-RESEARCH-001-20260301.md
- 커밋: 1218831 (Task 1~4 결과 반영)
- HTTP 확인: 200
- HANDOVER 업데이트: 완료
