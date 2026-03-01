# CUR-V41-DESK543-FRACTAL-RESEARCH-001-20260301

**문서 ID**: CUR-V41-DESK543-FRACTAL-RESEARCH-001  
**작성일**: 2026-03-01  
**상태**: Task 0 완료, Task 1~4 스크립트 준비  
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

## 3. Task 1~4 스크립트 및 실행 가이드

분석 스크립트는 **backend 수정 없이** `/tmp/` 또는 `scripts/research/`에만 배치.

### 3.1 Task 1 — DESK5 트리거 실증

- **스크립트**: `/tmp/task1_desk5_empirical.py`
- **출력**: `/tmp/task1_desk5_results.json`
- **내용**: T5-1(Vol MA60>MA120), T5-2(기관/외인 15/20일), T5-3(52주 하위 30%+BB 스퀴즈) → 2조건 충족 시 진입, D+20/D+40/D+60/D+90/D+120 수익률·승률·False Positive·풀 크기 분포.
- **실행**:  
  `DATABASE_URL_SYNC=... python3 /tmp/task1_desk5_empirical.py`  
  ※ 241일×전종목 기준 쿼리 부하로 **실행 시간 다소 소요**(수십 분 단위 가능). 단축이 필요하면 스크립트 내 `sim_dates`를 60일 등으로 축소 후 테스트 권장.

### 3.2 Task 2 — DESK4 트리거 실증

- T4-1~T4-4 조건 및 SEC_LEADER_FLAG 산출 로직을 **본 Task에서 직접 구현**하여 스캔·추매 효과·피라미딩 시뮬 필요.
- 스크립트는 `/tmp/task2_desk4_empirical.py` (추가 작성 예정).

### 3.3 Task 3 — DESK3 트리거 실증

- T3-1(L3 TOP-20 30일 내 ≥2회), T3-2(전일 기준 동일 WICS·테마 TOP-20 ≥2종목), T3-3+T3-6 통합, T3-4, T3-5 조건 및 3단계 피라미딩·DESK2 먹이감 효과·T3 상관행렬.
- 스크립트는 `/tmp/task3_desk3_empirical.py` (추가 작성 예정).

### 3.4 Task 4 — 이중 수확 시뮬레이션

- 일봉 보유 수익(DESK5/4/3) + 분봉 수확(DESK2) 합산, 자본 단계별 복리(Stage 1/2/3).
- CROSS-RELAY-PRESIM 241거래일 데이터 활용.
- 스크립트는 `/tmp/task4_dual_harvest.py` (추가 작성 예정).

---

## 4. PASS 기준 종합표

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

---

## 5. Task 0 산출물 요약

- `/tmp/task0_data_validation.json`: v4_investor_daily·go100_news_items·ohlcv_daily 검증 결과, pass=true, fail_reasons=null.

---

## 6. 다음 단계

1. **Task 1 완료**: `task1_desk5_empirical.py`를 241거래일(또는 60일 샘플)로 실행 후 `/tmp/task1_desk5_results.json` 확인, PASS 기준 적용.
2. **Task 2~4**: 위 3.2~3.4 스크립트 작성·실행 후 본 보고서에 결과 통합.
3. **Task 5**: 최종 보고서 갱신, CEO-DIRECTIVES D-012 반영, HANDOVER 업데이트, 커밋 및 push.

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-DESK543-FRACTAL-RESEARCH-001-20260301.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-DESK543-FRACTAL-RESEARCH-001-20260301.md
- 커밋: 0fe52ec
- HTTP 확인: 200
- HANDOVER 업데이트: 완료
