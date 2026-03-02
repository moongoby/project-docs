# CUR-GO100-P4-2-GAP-CALIBRATOR-20260227

**작업일**: 2026-02-27  
**목표**: 장 시작 갭(갭업/갭다운) 패턴 분석 엔진 구축 — 갭 메움 확률·클러스터별 통계·Agent 도구·스크리닝 필터

---

## 1. 요약

- **DB**: `go100_gap_calibrator` 테이블 신규 생성 (기존 `go100_gap_analysis`는 전략 대조용으로 유지)
- **엔진**: `backend/app/services/go100/gap_calibrator.py` — `scan_gaps`, `get_gap_statistics`, `get_gap_probability`, `generate_gap_signals`, `get_today_gaps_list`
- **Agent 도구**: `get_gap_analysis`, `get_today_gaps` 등록
- **스크리닝**: `gap_up_today`, `gap_down_today` 필터 추가 (실시간 갭 탐지)
- **크론**: 장 시작 직후 09:05 갭 탐지 스크립트 및 cron 등록

---

## 2. 갭 백필 결과 (2025-09-01 ~ 2026-02-27, min_gap_pct=1.0%)

| 항목 | 값 |
|------|-----|
| **백필 건수** | **108,574건** |
| 기간 | 약 6개월 |
| 갭 판정 | \|(시가−전일종가)/전일종가×100\| ≥ 1% |

---

## 3. 전체 갭 메움 확률 및 통계 (6개월)

| 지표 | 값 |
|------|-----|
| **전체 갭 메움 확률** | **55.02%** |
| 평균 갭 크기(%) | 0.97 (부호 포함 평균) |
| 당일 평균 수익률(%) | -0.23 |
| 익일 평균 수익률(%) | 0.36 |

---

## 4. 클러스터별 통계

| 클러스터 | 건수 | 갭 메움 확률(%) | 평균 갭 크기(%) | 당일 평균 수익률(%) |
|----------|------|------------------|------------------|----------------------|
| small_gap (1~3%) | 88,608 | **58.79** | 0.53 | -0.16 |
| medium_gap (3~5%) | 13,867 | 41.52 | 1.03 | -0.24 |
| large_gap (5%+) | 6,099 | 30.91 | 7.19 | -1.33 |

- 갭이 클수록 당일 메움 확률 감소, 당일 평균 수익률 하락.
- small_gap 구간에서 메움 확률이 가장 높음.

---

## 5. 대표 종목 사례: 삼성전자(005930)

- **6개월 갭 발생 건수**: 65건  
- **갭 메움 확률**: 38.46%  
- **당일 평균 수익률**: 0.37%  
- **익일 평균 수익률**: 1.00%  
- **클러스터별**: small_gap 44건(메움 50%), medium_gap 19건(메움 15.79%), large_gap 2건(메움 0%)

**get_gap_probability(005930, 3.0)**  
- 3% 갭업 대역(2~4%) 샘플 18건, 메움 4건 → **메움 확률 22.22%**

---

## 6. 구현 내역

| 구분 | 내용 |
|------|------|
| 마이그레이션 | `backend/migrations/040_go100_gap_analysis.sql` → `go100_gap_calibrator` 테이블·인덱스 |
| 갭 엔진 | `gap_calibrator.py`: scan_gaps, get_gap_statistics, get_gap_probability, generate_gap_signals, get_today_gaps_list |
| Agent 도구 | `get_gap_analysis(ticker=None, months=6)`, `get_today_gaps(min_gap_pct=2.0)` |
| 스크리닝 | `gap_up_today`, `gap_down_today` (go100_gap_calibrator 최신일 기준) |
| 크론 | `scripts/go100/run_gap_calibrator_signals.sh`, `docs/cron/go100_gap_calibrator.cron` (09:05 평일) |

---

## 7. 검증

- 마이그레이션 040 적용 완료 (`go100_gap_calibrator` 생성)
- 6개월 백필 108,574건 적재
- `get_gap_statistics()` 전체/종목별 통계 확인
- `get_gap_probability("005930", 3.0)` 메움 확률 반환 확인
- Agent 도구 `get_gap_analysis`, `get_today_gaps` 호출 정상

---

## 8. 체크리스트

- [ ] 코드 레포 커밋 완료 (kis-autotrade-v4)
- [ ] project-docs 보고서 push 완료 (본 문서)
