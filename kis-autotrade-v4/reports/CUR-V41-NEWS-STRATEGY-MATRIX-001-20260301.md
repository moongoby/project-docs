# CUR-V41-NEWS-STRATEGY-MATRIX-001-20260301
**작성일**: 2026-03-01
**작성자**: Claude Code (Cursor #24)
**상태**: DESIGN COMPLETE
**선행 문서**: WAVE-OUTER-RESEARCH-001 (R20), SURGE-CAUSE-ANALYSIS-001, SUPER-ANT-STUDY-001/002

---

## 1. 뉴스-파동 연구 기반 (R20 결과)

### 1.1 핵심 발견
- **χ² = 249.4**: 뉴스 타입과 파동 패턴 간 강한 통계적 연관성 (p < 0.001)
- **실적/공시 릴레이율 48.4%**: 가장 높은 전략 연속성 (테마 대비 +7.2pp)
- **테마 릴레이율 41.2%**: 테마 뉴스 Type-E(허위파) 비율 50.8%로 상대적으로 높음
- **뉴스 보유량**: 2,148,278건 (2025-02-27 ~ 2026-02-27, 366일)
- **뉴스 매칭**: 전체 급등 3,000건 중 2,193건(73.1%)에 관련 뉴스 존재
- **뉴스 선행 시간 중앙값**: -6.5분 (뉴스가 급등보다 약간 먼저 발생)

### 1.2 뉴스 분류 현황 (DB 실측: go100_news_items)

**테이블 구조**:
- 테이블명: `go100_news_items`
- 컬럼: `category_code`, `is_disclosure`, `stock_code1~3`, `title`, `data_date`, `data_time`
- 종목 연결: 4,701개 종목, 618,769건 종목연결 뉴스

**8대 카테고리 분류 (DB 조회 결과)**:

| 분류 | category_code | 건수 | 비율 | 비고 |
|------|--------------|------|------|------|
| 기업일반뉴스 | 01, 05, 06 | 883,259 | 41.1% | is_disclosure=false 기업뉴스 |
| 시장/지수 | 10, 11, 12, 18, 20 | 397,283 | 18.5% | 시장 전반, 선물, 채권, 환율, 정책 |
| 테마/산업 | 02, 06, 07 | 226,479 | 10.5% | 산업/업종, 제품/기술, 경영전략 |
| 공시계열/수주 | 03, 08, 09 | 189,899 | 8.8% | 공시계열, 계약/수주, 지분/M&A |
| 기타 | (나머지) | 139,207 | 6.5% | 분류 불명확 |
| 해외뉴스 | H1, H2 | 106,063 | 4.9% | 미국, 아시아 시장 |
| 실적/재무 | 04 | 103,945 | 4.8% | 영업이익, 매출, 실적발표 |
| 공시(법정) | is_disclosure=true | 102,143 | 4.8% | 거래소/코스닥 공시, 금감원 |
| **합계** | | **2,148,278** | **100%** | |

**공시 구분 상세** (is_disclosure=true: 102,143건):
- category_code 01 (기업뉴스 + 공시): 44,043건 (43.1%)
- category_code 04 (실적/재무 공시): 23,968건 (23.5%)
- category_code 03 (공시계열): 21,584건 (21.1%)
- category_code 20 (정책/경제): 5,383건 (5.3%)

**주요 뉴스 제공사**: 인포스탁, 헤럴드경제, 연합뉴스, 한국경제신문, 코스닥 공시, 거래소 공시

---

## 2. 뉴스 8분류 × 전략 적합도 매트릭스

### 2.1 뉴스 분류 체계 (R20 + SURGE-CAUSE 기반 재정의)

| 분류 | 설명 | 대표 category_code | R20 릴레이율 | R20 Type-E율 |
|------|------|-------------------|------------|------------|
| **공시** | 거래소/금감원 공식 공시 | is_disclosure=true | **48.4%** | 44.5% |
| **실적** | 실적 발표/예측/어닝서프라이즈 | 04 | **48.4%** | 40.9% |
| **수급** | 기관/외국인 순매수 동반 | (수급주도 판단) | **82.2%** (SURGE-CAUSE) | **29.7%** |
| **테마/산업** | 섹터 테마, AI, 반도체, 2차전지 | 02, 07 | 41.2% | 50.8% |
| **계약/수주** | 신규 계약, 수주, M&A | 08, 09 | 36.8% | 47.5% |
| **시장** | 코스피, 금리, 환율, 정책 | 10, 11, 12, 18, 20 | 낮음 (추정) | 높음 (추정) |
| **해외** | 미국/중국 뉴스, Fed, 나스닥 | H1, H2 | 낮음 (추정) | 높음 (추정) |
| **기타** | 인사/조직, 분류 불가 | 05, 나머지 | 40.9% (기타) | 54.4% |

*참고: 수급 릴레이율/Type-E율은 SURGE-CAUSE-ANALYSIS-001 S04 결과 (뉴스 분류가 아닌 수급 원인 기준)*

### 2.2 전략-뉴스 적합도 매트릭스

| 전략 | 공시 | 실적 | 수급 | 테마/산업 | 계약/수주 | 시장 | 해외 | 기타 |
|------|------|------|------|----------|----------|------|------|------|
| **D6** (종가 갭업/상따) | ★★★ | ★★★ | ★★★ | ★★ | ★★ | ★ | ★ | ★ |
| **D7** (갭다운 필터) | ★★ | ★★★ | ★★★ | ★★ | ★★ | ★★★ | ★★ | ★ |
| **D5** (뉴스 급등 2파) | ★★★ | ★★★ | ★★ | ★★★ | ★★★ | ★ | ★ | ★ |
| **D2** (RSI 눌림) | ★★★ | ★★★ | ★★★ | ★★ | ★★ | ★ | ★ | ★ |
| **S1** (폭발+눌림 스윙) | ★★★ | ★★ | ★★★ | ★★★ | ★★ | ★ | ★ | ★ |
| **D4** (전상 눌림) | ★★★ | ★★★ | ★★ | ★★ | ★★ | ★ | ★ | ★ |
| **D3** (대장→후발 순환) | ★ | ★ | ★★ | ★★★ | ★ | ★ | ★ | ★ |

*★★★: 높은 적합도 (진입 우선) / ★★: 중간 (표준 진입) / ★: 낮음 (진입 보류)*

**매트릭스 설계 근거**:
- R20: 실적/공시 릴레이율 48.4% — 최고 (D6/D7/D5/D2 모두 우선)
- SURGE-CAUSE S04: 수급주도 허위파율 29.7% — 전체 최저, 릴레이율 82.2%
- R20: 테마 뉴스 Type-E율 50.8% — 허위파 비중 높음, 2파 전략(D5/D3)에 적합
- SURGE-CAUSE S02: 전일 상한가 연속(prev_ul_cont) 허위파율 86.0% — 진입 금지

---

## 3. D6/D7 뉴스 타입 필터 설계

### 3.1 D6 (상따→갭 전략) 뉴스 필터

**현황**: D6 백테스트 PF 13.63 (VE-003-PHASE-A PASS), 갭리스크 16.7%
**목표**: 뉴스 필터 적용으로 갭리스크 감소 + PF 유지

**뉴스 타입별 D6 적용 조건**:
```
D6 진입 조건 + 뉴스 필터:
  뉴스 타입 = '공시' (is_disclosure=true)
    → 진입 우선 허용 (릴레이율 48.4%, 갭업 가능성 높음)
  뉴스 타입 = '실적' (category_code=04)
    → 진입 우선 허용 (실적 호재 D+1 갭업 확률 높음)
  뉴스 타입 = '수급' (기관+외국인 동시 매수)
    → 진입 우선 허용 (허위파율 29.7% — 가장 안전)
  뉴스 타입 = '테마/산업'
    → 표준 진입 (Type-E 50.8%, 수익 기대 있으나 허위파 주의)
  뉴스 타입 = '시장' (전체 시장 악재)
    → 갭다운 리스크 고려, 진입 보류
  뉴스 타입 = '해외' (미국/중국 악재)
    → 갭다운 리스크 고려, 진입 보류
  뉴스 없음
    → 수급 조건(기관 매수 D-1~D-3) 기반으로만 판단
```

**예상 PF 변화 (추정)**:

| 뉴스 필터 적용 시나리오 | 적용 전 PF | 적용 후 PF (추정) | 신호 감소율 |
|----------------------|----------|-----------------|-----------|
| 공시+실적+수급만 허용 | 13.63 | +15~20% 개선 기대 | ~30% 감소 |
| 해외+시장 악재 제외 | 13.63 | +8~12% 개선 기대 | ~15% 감소 |
| 전일 상한가 연속 제외 | 13.63 | 갭리스크 16.7%→10% | ~5% 감소 |

*추정 근거: SURGE-CAUSE S04 원인별 허위파율 차이 (수급주도 -19.5pp, 실적 -8.2pp)*

### 3.2 D7 (종가배팅→갭 전략) 뉴스 조건

**현황**: D7 PF 1.98 (CONDITIONAL), 갭다운 리스크 43.4% (EXIT-RULE-FINALIZE-001)
**목표**: 갭다운 리스크 43.4% → 24% 목표 (종가위치≥0.80+Top10 이미 개선됨)

**D7 뉴스 필터 v2 설계**:
```
D7 갭다운 필터 v2 (기존 필터 위에 뉴스 레이어 추가):

  [갭업 확률 강화]
  시장/해외 뉴스 = 악재 AND 개별 종목 공시/실적 뉴스 없음
    → 진입 차단 (시장 전체 하락 리스크)

  [갭업 기회 포착]
  개별 종목 공시/실적 뉴스 존재 AND 갭다운 우려 없음
    → 표준 진입 허용

  [릴레이 부스트]
  수급주도 원인 (is_disclosure=true + 기관 매수 D-1~D-3)
    → D7 포지션 크기 1.2배 허용 (허위파율 29.7%)

  [진입 차단]
  뉴스 타입 = 전일 상한가 연속 (category_code 관련)
    → 진입 금지 (허위파율 86.0% — SURGE-CAUSE S04)
```

---

## 4. D5 부스트 조건 — 실적/공시 릴레이율 48.4% 활용

### 4.1 릴레이 패턴 분석 (R20 + SURGE-CAUSE 교차)

| 뉴스 유형 | 릴레이가능률 | Type-E율 | D5 적합도 | 출처 |
|-----------|------------|---------|---------|------|
| 실적 | **48.4%** | 40.9% | 최고 | R20 + SURGE-CAUSE S04 |
| 공시 | **48.4%** | 44.5% | 최고 | R20 |
| 수급주도 | **82.2%** | 29.7% | 최고 | SURGE-CAUSE S04 |
| 테마 | 41.2% | 50.8% | 중간 | R20 |
| 계약/수주 | 36.8% | 47.5% | 중간 | R20 |
| 기타 | 40.9% | 54.4% | 낮음 | R20 |

**D5 뉴스스파이크 릴레이 잠재력** (R20): D5 후보 1,513건 중 릴레이가능 621건 (41.1%)

### 4.2 D5 부스트 설계

```
D5 부스트 조건:
  기본 D5 신호 = True (뉴스 급등 1파 완료 + 이평선 수렴)
  AND 최근 3일 내 뉴스 조건:
    CASE A: 실적/공시 뉴스 존재 (해당 종목)
      → 포지션 크기 1.5배 허용
      → 목표 수익률 +0.5%p 상향
    CASE B: 수급주도 원인 (기관 D-1~D-3 순매수)
      → 포지션 크기 1.3배 허용
      → 트레일링 스톱 강화 (손절 -1.5% → -2.0%)
    CASE C: 테마/산업 뉴스만 존재
      → 표준 포지션 (부스트 없음)
      → 이평선 수렴 조건 강화 (MA_CONVERGENCE_1M 임계값 ↓10%)
    CASE D: 전일 상한가 연속
      → D5 진입 금지 (허위파율 86.0%)
```

**기대 효과 (추정)**:

| 항목 | 현재 D5 | D5 + 부스트 |
|------|---------|------------|
| PF | 4.21 (VE-003-PHASE-B) | 4.5~5.0 추정 |
| 부스트 발동률 | — | ~25% (전체 D5 신호 중) |
| 부스트 건당 PF | — | 기존 × 1.3~1.5 추정 |
| 전체 D5 PF 개선 | 기준 | +5~8% 추정 |

---

## 5. SEC_LEADER_FLAG v2 — 뉴스 빈도 변수 추가

### 5.1 현재 SEC_LEADER_FLAG 현황

**SUPER-ANT-STUDY-001에서 정의된 v2 조건**:
- 거래대금 기준 테마 내 1위 (홍인기 "1등만 매매")
- 지수 폭락 후 최초 돌파 종목 (남석관 "새 대장주")
- 지수 대비 상대강도 RS > 80 (미너비니 기준)

**R15 연구 결과**:
- SEC_LEADER_FLAG(Leader 종목, 3회+ 급등) 릴레이율: **44.43%** vs 비Leader: 31.55%
- 차이: +12.9pp — 반복 급등 종목의 릴레이 우위 통계적으로 확인

**SURGE-CAUSE S19 결과**:
- Leader 종목 Top-5 평균 AUC: **0.712** (R15의 0.638 대비 +0.074)
- Leader 종목: 2,041개 (전체 급등의 96.8%)
- 급등 간격 중앙값: 38일 (약 2개월마다 재급등)

### 5.2 v2 뉴스 빈도 변수 추가 설계

**추가 변수 정의**:

```python
# SEC_LEADER_FLAG v2.1 — 뉴스 빈도 변수 추가
news_variables = {
    'news_frequency_3d': {
        'definition': '최근 3일 뉴스 건수 (go100_news_items 기준)',
        'source': 'go100_news_items WHERE stock_code1 = :stock AND data_date >= CURRENT_DATE - 3',
        'threshold': '>= 3건 시 활성',
        'weight': 0.15,
        'priority': 'P0 — 구현 용이, 즉각 효과'
    },
    'news_category_weight': {
        'definition': '카테고리별 가중치 합산 점수',
        'formula': '''
          SUM(
            CASE category_code
              WHEN is_disclosure THEN 3.0   -- 공시
              WHEN '04' THEN 3.0            -- 실적
              WHEN '08' THEN 2.0            -- 계약/수주
              WHEN '03' THEN 2.0            -- 공시계열
              WHEN '02' THEN 1.5            -- 산업/업종
              WHEN '07' THEN 1.5            -- 제품/기술
              WHEN 'H1' THEN -1.0           -- 해외 악재 (부정적)
              ELSE 1.0
            END
          )
        ''',
        'threshold': '>= 3.0 시 활성',
        'weight': 0.20,
        'priority': 'P1 — 분류 기반 점수화'
    },
    'news_sentiment_3d': {
        'definition': '최근 3일 뉴스 긍/부정 점수 (제목 키워드 기반)',
        'positive_keywords': ['호재', '급등', '수주', '영업이익', '증가', '신고가', '돌파', '매수'],
        'negative_keywords': ['악재', '급락', '손실', '적자', '감소', '하락', '매도', '소송'],
        'score_range': '-1.0 ~ +1.0',
        'threshold': '>= +0.3 시 활성',
        'weight': 0.15,
        'priority': 'P1 — 키워드 사전 구축 필요'
    },
    'relay_probability': {
        'definition': '종목별 과거 릴레이 확률 (go100_news_items + ANATOMY 샘플 결합)',
        'formula': 'leader_relay_count / leader_total_surges (최근 1년)',
        'threshold': '>= 0.40 시 활성',
        'weight': 0.10,
        'priority': 'P2 — 통계 계산 필요 (중기 과제)'
    },
    'news_burst_flag': {
        'definition': 'D-5일 내 뉴스 급증 패턴 (burst 패턴)',
        'reference': 'SURGE-CAUSE S07: burst 패턴 — 급등 8.4% vs 대조군 4.9%',
        'formula': 'd5_news_count >= 3 AND d5_news_count / d10_news_count >= 0.6',
        'weight': 0.10,
        'priority': 'P1 — D-5 뉴스 건수만으로 구현 가능'
    }
}
```

**SEC_LEADER_FLAG v2.1 종합 점수**:

```python
def calc_sec_leader_flag_v2(stock_code, analysis_date):
    # 기존 v2 조건 (SUPER-ANT-STUDY-001)
    base_score = (
        is_trade_amount_rank1(stock_code) * 0.30 +     # 거래대금 1위
        is_first_breakout(stock_code) * 0.20 +          # 최초 돌파
        calc_rs_score(stock_code) >= 80 * 0.20          # RS > 80
    )

    # v2.1 뉴스 빈도 추가
    news_score = (
        min(news_frequency_3d(stock_code, analysis_date) / 5.0, 1.0) * 0.15 +
        min(news_category_weight(stock_code, analysis_date) / 6.0, 1.0) * 0.15
    )

    total_score = base_score + news_score
    return total_score >= 0.5  # 0.5 이상 시 SEC_LEADER_FLAG = True
```

### 5.3 도입 우선순위

| 우선순위 | 변수 | 구현 난이도 | 예상 효과 | 근거 |
|---------|------|-----------|---------|------|
| P0 (즉시) | `news_frequency_3d` | 하 — SQL 1줄 | 즉각 신호 보강 | SURGE-CAUSE S07: AUC 0.670 |
| P1 (1주) | `news_category_weight` | 중 — 분류 필요 | 카테고리별 차별화 | R20: 카테고리별 릴레이율 차이 확인 |
| P1 (1주) | `news_burst_flag` | 하 — 기존 데이터 | 급등 전조 포착 | SURGE-CAUSE S07: burst 패턴 1.7배 |
| P2 (2주) | `news_sentiment_3d` | 고 — 키워드 사전 | 감성 정보 반영 | 정성적 개선, 정량 검증 필요 |
| P2 (2주+) | `relay_probability` | 고 — 통계 계산 | 종목별 정밀 예측 | SURGE-CAUSE S19: Leader AUC 0.712 |

---

## 6. 전략 간 교차 분석 — 뉴스 연동 개선 포인트

### 6.1 SURGE-CAUSE × R20 교차 발견

**공시 뉴스의 이중 효과**:
- SURGE-CAUSE: 공시(disclosure) 릴레이율 74.5%, 허위파율 50.6% (전체 최다 원인 40.8%)
- R20: 공시 뉴스 릴레이가능률 48.4% (뉴스 유형 중 최고)
- **결론**: 공시 뉴스 = 가장 신뢰도 높은 진입 신호 (건수 많고, 릴레이율 높음)

**실적 뉴스의 복합 효과**:
- SURGE-CAUSE: 실적(earnings) 허위파율 40.9% (전체 49.2% 대비 -8.2pp)
- R20: 실적 뉴스 릴레이가능률 48.4% (공시와 동급)
- S11: 실적 급등 최적 전조 = `d5_news_count(AUC 0.788)` — **뉴스 빈도가 실적 급등 핵심 전조**
- **결론**: 실적 발표 5일 전부터 뉴스 증가 → 급등 확률 높아짐

**수급 원인의 역설**:
- R22: D0 DUAL_FLOW(기관+외국인 동시 매수) 릴레이율 24.1% — **역전 발견 (최저!)**
- R22: D-1~D-3 기관 매수 → 릴레이 우위 (R15 계수 +0.286)
- SURGE-CAUSE: 수급주도 급등 허위파율 29.7%, 릴레이율 82.2%
- **결론**: 수급은 "당일(D0)"이 아닌 "D-1~D-3 축적" 기준으로 판단해야 함

### 6.2 R20 × S07 교차 발견 (뉴스 빈도 × 급등 원인)

| SURGE-CAUSE S07 발견 | R20 결과 | 통합 시사점 |
|---------------------|---------|-----------|
| d10_news_count AUC=0.670 | 뉴스 있는 급등 73.1% | 뉴스 빈도 = 급등 전조 지표로 유효 |
| d5_news_count AUC=0.663 | 장 전 뉴스 19.8% | 5일 전 뉴스 급증 → 장 전 모니터링 강화 |
| burst 패턴: 급등 8.4% vs 대조군 4.9% | 뉴스 없는 급등 26.9% | burst 패턴 = 73.1% 중 선별 도구 |
| 실적 급등 전조: d5_news_count 1위 | 실적 릴레이율 48.4% | 실적 + 5일 뉴스 급증 = 최강 조합 |

---

## 7. 즉시 실행 가능 SQL 쿼리

### 7.1 종목별 최근 3일 뉴스 건수 조회 (news_frequency_3d)

```sql
-- SEC_LEADER_FLAG v2.1: news_frequency_3d 계산
SELECT
    stock_code1 as stock_code,
    COUNT(*) as news_frequency_3d,
    COUNT(CASE WHEN is_disclosure = true THEN 1 END) as disclosure_count_3d,
    COUNT(CASE WHEN category_code = '04' THEN 1 END) as earnings_count_3d,
    SUM(
        CASE
            WHEN is_disclosure = true THEN 3.0
            WHEN category_code = '04' THEN 3.0
            WHEN category_code IN ('08', '09') THEN 2.0
            WHEN category_code IN ('03') THEN 2.0
            WHEN category_code IN ('02', '07') THEN 1.5
            WHEN category_code IN ('H1', 'H2') THEN -1.0
            ELSE 1.0
        END
    ) as news_category_weight
FROM go100_news_items
WHERE
    stock_code1 IS NOT NULL
    AND stock_code1 != ''
    AND data_date >= CURRENT_DATE - INTERVAL '3 days'
GROUP BY stock_code1
ORDER BY news_frequency_3d DESC;
```

### 7.2 공시/실적 뉴스 당일 D6/D7 신호 비교 쿼리 (설계)

```sql
-- D6/D7 뉴스 타입별 PF 비교 (백테스트 연동 필요)
-- go100_news_items × 급등 이벤트 테이블 조인
SELECT
    CASE
        WHEN n.is_disclosure = true THEN '공시'
        WHEN n.category_code = '04' THEN '실적'
        WHEN n.category_code IN ('02', '07') THEN '테마/산업'
        WHEN n.category_code IN ('H1', 'H2') THEN '해외'
        WHEN n.category_code IN ('10', '11', '12') THEN '시장'
        ELSE '기타'
    END as news_type,
    COUNT(*) as signal_count,
    AVG(gap_next_day) as avg_gap,  -- D+1 갭 수익률 (백테스트 테이블 필요)
    COUNT(CASE WHEN gap_next_day > 0 THEN 1 END) * 100.0 / COUNT(*) as gap_up_rate
FROM go100_news_items n
-- JOIN 백테스트 결과 테이블 (구현 필요)
GROUP BY 1
ORDER BY avg_gap DESC;
```

### 7.3 뉴스 burst 패턴 탐지 (news_burst_flag)

```sql
-- SURGE-CAUSE S07: D-5일 내 뉴스 급증 패턴 탐지
WITH news_counts AS (
    SELECT
        stock_code1,
        COUNT(CASE WHEN data_date >= CURRENT_DATE - 5 THEN 1 END) as d5_count,
        COUNT(CASE WHEN data_date >= CURRENT_DATE - 10 THEN 1 END) as d10_count
    FROM go100_news_items
    WHERE stock_code1 IS NOT NULL AND stock_code1 != ''
      AND data_date >= CURRENT_DATE - 10
    GROUP BY stock_code1
)
SELECT
    stock_code1,
    d5_count,
    d10_count,
    d5_count::float / NULLIF(d10_count, 0) as burst_ratio,
    CASE
        WHEN d5_count >= 3 AND d5_count::float / NULLIF(d10_count, 0) >= 0.6
        THEN true ELSE false
    END as news_burst_flag
FROM news_counts
WHERE d5_count >= 3
ORDER BY burst_ratio DESC;
```

---

## 8. 구현 로드맵

| 단계 | 작업 | 예상 소요 | 우선순위 | 담당 |
|------|------|---------|---------|------|
| **P0-1** | `news_frequency_3d` SQL 구현 + SEC_LEADER_FLAG 연동 | 0.5일 | 최고 | 즉시 |
| **P0-2** | D6 뉴스 타입 필터 백테스트 (공시/실적 vs 전체) | 1~2일 | 최고 | 즉시 |
| **P1-1** | `news_category_weight` 가중치 계산 함수 구현 | 1일 | 높음 | 1주 |
| **P1-2** | D7 갭다운 필터 뉴스 레이어 추가 (시장/해외 악재 차단) | 1일 | 높음 | 1주 |
| **P1-3** | `news_burst_flag` 구현 + D5 진입 조건 연동 | 1일 | 높음 | 1주 |
| **P1-4** | D5 부스트 조건 백테스트 (공시/실적 뉴스 × D5 PF 비교) | 2~3일 | 중간 | 1주 |
| **P2-1** | `news_sentiment_3d` 키워드 사전 구축 | 2~3일 | 중간 | 2주 |
| **P2-2** | SEC_LEADER_FLAG v2.1 전체 통합 테스트 | 1~2일 | 중간 | 2주 |
| **P2-3** | `relay_probability` 종목별 과거 통계 계산 | 3~5일 | 낮음 | 3주 |
| **P3** | 전체 통합 백테스트 + 모의매매 연동 | 2~3일 | 낮음 | 4주 |

---

## 9. 즉시 실행 체크리스트

1. [x] DB에서 뉴스 8분류 현황 확인 (2,148,278건, 139개 category_code)
2. [ ] `news_frequency_3d` SQL 함수 구현 및 HAV 변수 공간 추가
3. [ ] D6 뉴스 타입 필터 백테스트 쿼리 작성 (공시/실적만 허용 시 PF 변화)
4. [ ] D7 시장/해외 악재 뉴스 필터 설계 및 검증
5. [ ] SEC_LEADER_FLAG에 `news_frequency_3d` 변수 추가 (P0 즉시)
6. [ ] SURGE-CAUSE S07 burst 패턴을 DESK5 편입 조건에 반영

---

## 10. 참조 문서 및 핵심 수치 요약

| 출처 문서 | 핵심 수치 | 본 보고서 활용 |
|---------|---------|--------------|
| WAVE-OUTER-RESEARCH-001 R20 | χ²=249.4, 실적/공시 릴레이율 48.4%, 테마 41.2% | 섹션 1, 2, 3, 4 전략-뉴스 매트릭스 |
| SURGE-CAUSE-ANALYSIS-001 S04 | 수급주도 허위파율 29.7%, 전상 허위파율 86.0% | 섹션 2, 3 진입 차단 규칙 |
| SURGE-CAUSE-ANALYSIS-001 S07 | d5_news_count AUC 0.670, burst 패턴 1.7배 | 섹션 5 news_burst_flag |
| SURGE-CAUSE-ANALYSIS-001 S11 | 실적 전조: d5_news_count AUC 0.788 | 섹션 6 교차 분석 |
| SUPER-ANT-STUDY-001 | SEC_LEADER_FLAG v2 조건 (3개) | 섹션 5 v2.1 설계 |
| SUPER-ANT-STUDY-002 D5 | NEWS_CATALYST_SCORE (P1 변수) | 섹션 4 D5 부스트 |
| WAVE-OUTER-RESEARCH-001 R15 | SEC_LEADER 릴레이율 44.43% vs 비Leader 31.55% | 섹션 5.1 |
| WAVE-OUTER-RESEARCH-001 R22 | D0 DUAL_FLOW 릴레이율 24.1% (역전!) | 섹션 6.1 수급 역설 |
| VE-003-PHASE-A | D6 PF 13.63 (PASS), 갭리스크 16.7% | 섹션 3.1 |
| EXIT-RULE-FINALIZE-001 | D7 갭다운 리스크 43.4%→24% | 섹션 3.2 |
| VE-003-PHASE-B | D5 PF 4.21 (CONDITIONAL) | 섹션 4.2 |
| go100_news_items (DB 직접 조회) | 2,148,278건, 139개 category_code | 섹션 1.2 |

---

## 11. 전략적 판정

**즉시 효과가 가장 큰 항목 (순서)**:

1. **D6 뉴스 타입 필터** — PF 13.63에서 추가 개선 여지, 갭리스크 직접 감소
2. **news_frequency_3d → SEC_LEADER_FLAG** — SQL 1줄로 즉시 구현 가능
3. **D5 공시/실적 부스트** — PF 4.21 → 4.5~5.0 기대
4. **D7 시장/해외 악재 필터** — 갭다운 리스크 추가 감소

**중기 과제 (2~4주)**:
- news_category_weight 가중치 체계 구축
- SEC_LEADER_FLAG v2.1 통합 백테스트
- relay_probability 종목별 통계 계산

**검증 필요 가설**:
- H-NEWS-01: "공시/실적 뉴스 동반 D6 신호의 갭업율이 전체 D6 대비 10%p+ 높다"
- H-NEWS-02: "news_frequency_3d >= 3인 종목의 SEC_LEADER 릴레이율이 전체 평균 대비 +5%p"
- H-NEWS-03: "D7에서 시장/해외 악재 뉴스 필터 적용 시 갭다운 발생율 -10%p 감소"

---

*판정: 뉴스 필터를 D6/D7에 통합하는 것이 가장 즉각적인 PF 개선 효과를 낼 것으로 판단. DB에 2,148,278건의 뉴스가 이미 category_code + is_disclosure 형태로 구조화되어 있어 추가 수집 없이 즉시 활용 가능.*

*다음 세션 권장 작업: P0-2 D6 뉴스 타입 필터 백테스트 — go100_news_items와 급등 이벤트 테이블 조인 쿼리 작성 후 공시/실적 뉴스 유무별 D+1 갭 수익률 비교*
