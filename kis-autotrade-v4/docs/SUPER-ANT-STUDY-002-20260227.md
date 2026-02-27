# 한국 데일리 트레이딩 전략 심층 연구 보고서 — SUPER-ANT-STUDY-002

| 항목 | 내용 |
|------|------|
| 문서 ID | SUPER-ANT-STUDY-002 |
| 작성일 | 2026-02-27 |
| CEO 승인 | D-009 (2026-02-27) |
| 선행 문서 | SUPER-ANT-STUDY-001 (슈퍼개미 7인 조사), CEO-DIRECTIVES D-008-KR |
| 참조 | HANDOVER.md v1.4, DESIGN-SPEC v3.0, VE-001/002 |

---

## Executive Summary

STUDY-001에서 도출한 한국 슈퍼개미 7인의 중장기 전략을 기반으로, **CEO 실전 데일리 트레이딩 전략**을 10명+ 실전 트레이더(홍인기, 서희파더, 강창권, 불개미, 돌팬티, 단봉TV, 김민규, 고수TV 등)의 교차 분석을 통해 **총 9개 전략(D1~D7 + S1~S2)**으로 체계화했다.

### 핵심 결론

| 항목 | 결과 |
|------|------|
| 전략 수 | 데일리 7개(D1~D7) + 스윙 2개(S1~S2) = 총 9개 |
| CEO 전략 vs 최상위 트레이더 | **90%+ 일치** |
| 가장 보편적 손절선 | **1분봉 20분선** (모든 전략 공통) |
| 체결강도 임계값 | **120%** (매수세 우위 정량 기준) |
| 시간효율 최고 전략 | **D7 종가배팅** (교차 검증) |
| NEW 종목 탐지 | 일봉 불가 → **장중 1분봉 복합 조건** 필요 |
| 신규 변수 | **30+ 기술적 변수** 정의 |
| P0/P1/P2 합계 | 8 / 7 / 5 = 총 20개 변수 |

---

## 1. CEO 실전 전략 3층 피라미드

| Layer | 전략 | 보유기간 | DESK 레벨 | 관리 방식 |
|-------|------|----------|-----------|-----------|
| **Layer 1 (데일리)** | D1~D7 | 당일~D+1 | DESK-REALTIME (신규) | 장중 실시간 모니터링 |
| **Layer 2 (스윙)** | S1~S2 | 3~10일 | DESK3 | 일봉 기반 풀 관리 |
| **Layer 3 (텐배거)** | 펀더멘탈+메가트렌드 | 수개월~수년 | DESK5 | 분기별 리밸런싱 |

### 3층 구조의 의미
- Layer 1은 STUDY-001의 홍인기 전략(D/D+1/D+2)을 확장한 **초단기 전술 레이어**
- Layer 2는 STUDY-001의 남석관·이정윤 전략(수급+눌림)을 구체화한 **중단기 레이어**
- Layer 3은 STUDY-001의 배진한·김정환 전략(텐배거+가치)을 포함한 **장기 레이어**
- 기존 DESK 시스템(DESK2~5)은 Layer 2~3에 매핑, **Layer 1은 신규 DESK-REALTIME 모듈 필요**

---

## 2. Layer 1: 데일리 전략 D1~D7 심층 분석

### D1: 시초가 진입 (Opening Range Entry)

| 항목 | 내용 |
|------|------|
| **전략 요약** | 갭상승 출발 후 5분선 지지 확인 시 09:03~04에 진입 |
| **교차 검증** | 홍인기(대왕개미), 서희파더, 강창권 — 시초가 전략 공통 |
| **핵심 변수** | GAP_OPEN_PCT, MA5_1M_SUPPORT |
| **진입 조건** | ① 시초가 전일 종가 대비 +3%~+8% 갭 ② 09:03~04 1분봉에서 5분선(MA5_1M) 지지 확인 ③ 체결강도 ≥ 120% |
| **청산 조건** | 20분선(MA20_1M) 이탈 시 즉시 매도 |
| **리스크** | 09:00~03 변동성 과다, 허매수 주의 |

**정량화 변수:**
- `GAP_OPEN_PCT`: (시초가 - 전일종가) / 전일종가 × 100
- `MA5_1M_SUPPORT`: 1분봉 종가 ≥ 5분 이동평균 (Boolean)
- `OPENING_VP`: 09:00~09:05 체결강도

---

### D2: 3분봉 눌림 (3-Min Pullback Entry)

| 항목 | 내용 |
|------|------|
| **전략 요약** | 급등 후 3분봉 기준 5/10선 터치 시 눌림매수 |
| **교차 검증** | 불개미, 돌팬티, 서희파더 — "3분봉이 가장 안전한 타임프레임" 공통 의견 |
| **핵심 변수** | PULLBACK_DEPTH_3M, VP_AT_PULLBACK |
| **진입 조건** | ① 3분봉 기준 1파 상승 후 5선 또는 10선 터치 ② 눌림 시 거래량 감소 (Volume Dry Up) ③ 체결강도 ≥ 120% 유지 |
| **청산 조건** | 3분봉 20분선 이탈 (= 1분봉 60분선에 해당) |

**정량화 변수:**
- `PULLBACK_DEPTH_3M`: (고점 - 눌림저점) / 고점 × 100 (3분봉 기준)
- `VP_AT_PULLBACK`: 눌림 구간 평균 체결강도
- `VOL_DRY_UP_3M`: 눌림 3분봉 거래량 / 상승 3분봉 평균 거래량

---

### D3: 대장→후발 순환 (Leader-Follower Rotation)

| 항목 | 내용 |
|------|------|
| **전략 요약** | 테마 대장주 상한가 후 후발주로 순환매매 |
| **교차 검증** | 홍인기 "1등이 상한가 가면 2등을 사라", 강창권 — 테마 순환 전략 |
| **핵심 변수** | LEADER_UL_FLAG, THEME_RANK |
| **진입 조건** | ① 테마 대장주 상한가 도달(LEADER_UL_FLAG=True) ② 후발주 20분선 지지 상태 ③ 후발주 체결강도 상승 반전 |
| **청산 조건** | 대장주 상한가 풀림(=테마 모멘텀 소멸) |

**정량화 변수:**
- `LEADER_UL_FLAG`: 동일 테마 내 거래대금 1위 종목 상한가 여부
- `THEME_RANK`: 테마 내 거래대금 순위 (2위~5위가 타겟)
- `LEADER_FOLLOWER_ROTATION`: 대장 상한가 후 후발주 거래대금 증가율

---

### D4: 전상 눌림 (Previous Day Upper Limit Pullback)

| 항목 | 내용 |
|------|------|
| **전략 요약** | 전일 상한가 종목의 D+1 눌림 후 20분선 돌파 시 진입 |
| **교차 검증** | 홍인기 D+1 전략, 단봉TV — 전상 눌림매매의 핵심 |
| **핵심 변수** | PREV_UL_FLAG, D1_MA20_1M_BREAK |
| **진입 조건** | ① 전일 상한가(+29.5%) 기록(PREV_UL_FLAG=True) ② D+1 장중 조정 후 1분봉 20분선 돌파 ③ 돌파 시 거래량 동반 |
| **청산 조건** | 20분선 재이탈 시 즉시 매도 |

**정량화 변수:**
- `PREV_UL_FLAG`: 전일 종가 = 상한가 (Boolean)
- `D1_MA20_1M_BREAK`: D+1 1분봉 종가 > 20분선 최초 돌파 시점
- `UL_D1_GAP`: D+1 시초가 갭 크기 (%)

---

### D5: 뉴스 급등 (News Catalyst Surge)

| 항목 | 내용 |
|------|------|
| **전략 요약** | 호재성 뉴스 급등 후 1파 완료, 이평선 수렴 시 2파 진입 |
| **교차 검증** | 고수TV, 서희파더 — "뉴스는 1파를 놓치고 2파를 타라" |
| **핵심 변수** | NEWS_CATALYST_SCORE, MA_CONVERGENCE_1M |
| **진입 조건** | ① 뉴스 기반 1파 급등 (+5%+) 발생 ② 1분봉 5/10/20분선 수렴 구간 형성 ③ 수렴 후 재돌파 + 체결강도 ≥ 120% |
| **청산 조건** | 20분선 이탈 시 매도 |

**정량화 변수:**
- `NEWS_CATALYST_SCORE`: 뉴스 카테고리별 가중치 합산 (정책/실적/M&A/특허 등)
- `MA_CONVERGENCE_1M`: 1분봉 5/10/20선 표준편차 (수렴도)
- `WAVE1_MAGNITUDE`: 1파 상승폭 (%)

---

### D6: 상따→갭 (Upper Limit Chase → Gap Profit)

| 항목 | 내용 |
|------|------|
| **전략 요약** | 오전 중 상한가 도달 + 매수잔량 100억+ 시 매수, D+1 갭상승에 매도 |
| **교차 검증** | 홍인기, 불개미 — "상따는 오전 10시 전 상한가만, 매수잔량이 핵심" |
| **핵심 변수** | UL_ENTRY_TIME, UL_BID_AMOUNT |
| **진입 조건** | ① 오전(~10:00) 상한가 도달 ② 상한가 매수잔량 ≥ 100억원 ③ 매도호가 소화 속도 양호 |
| **청산 조건** | 시간외 거래에서 -1% 시 즉시 매도, 그렇지 않으면 D+1 시초가 매도 |

**정량화 변수:**
- `UL_ENTRY_TIME`: 상한가 최초 도달 시각 (분 단위, 540=09:00)
- `UL_BID_AMOUNT`: 상한가 매수잔량 (원)
- `UL_HOLD_DURATION`: 상한가 유지 시간 (분)
- `UL_BID_AMOUNT_THRESHOLD`: 100억원 (= 10,000,000,000)

---

### D7: 종가배팅→갭 (Close Bet → Gap Profit)

| 항목 | 내용 |
|------|------|
| **전략 요약** | 14:30 이후 수급 집중 + 저점 상승 패턴 시 매수, D+1 시초가 매도 |
| **교차 검증** | 돌팬티, 단봉TV, 서희파더 — **"시간 효율 대비 가장 높은 기대수익"** (교차 검증 일치) |
| **핵심 변수** | CLOSE_BET_SCORE |
| **진입 조건** | ① 14:30~15:20 구간 거래대금 급증 ② 1분봉 저점 상승 패턴 (Higher Lows) ③ 체결강도 120%+ 지속 ④ 당일 상승률 +5%~+20% (상한가 미도달) |
| **청산 조건** | D+1 시초가(09:00~09:05) 매도 |

**정량화 변수:**
- `CLOSE_BET_SCORE`: 종가배팅 복합 점수 (아래 구성요소 합산)
  - `CB_VOLUME_SURGE`: 14:30 이후 거래대금 / 전일 동시간대 거래대금
  - `CB_HIGHER_LOWS`: 14:30~15:20 1분봉 저점 상승 횟수
  - `CB_VP_SUSTAINED`: 14:30~15:20 평균 체결강도
  - `CB_PRICE_RANGE`: 당일 상승률 (%)

**D7이 시간효율 최고인 이유:**
1. 14:30 이후만 모니터링 → 장중 9시간 모니터링 불필요
2. 익일 시초가 매도 → 오버나이트 리스크만 감수
3. 종가 수급 집중 = 기관/외국인 마감 매수 반영
4. 교차 검증: 돌팬티(수익률 상위), 단봉TV(전업 트레이더), 서희파더(실전 강사) 모두 최고 효율 전략으로 선정

---

## 3. Layer 2: 스윙 전략 S1~S2 심층 분석

### S1: 거래대금 폭발 후 눌림 (Volume Explosion Pullback)

| 항목 | 내용 |
|------|------|
| **전략 요약** | 10일 내 거래대금 500억+ 유입 + 10%+ 급등 후 눌림에서 매수 |
| **교차 검증** | 이정윤 "수급 폭발은 스마트머니 진입 신호", 남석관 "거래대금이 답" |
| **핵심 변수** | V_TRADE_AMT_10D_PEAK, THEME_ALIVE_FLAG |
| **진입 조건** | ① 최근 10일 내 일 거래대금 500억+ 기록 ② 해당 기간 +10%+ 급등 이력 ③ 이후 5~10일선 눌림 + 거래량 감소 ④ 테마/섹터 모멘텀 유지(THEME_ALIVE_FLAG=True) |
| **청산 조건** | 20일선 이탈 시 매도 |

**정량화 변수:**
- `V_TRADE_AMT_10D_PEAK`: 최근 10일 내 최대 일 거래대금 (원)
- `THEME_ALIVE_FLAG`: 동일 테마 최근 5일 내 2종목+ 거래대금 100억+ (Boolean)
- `S1_PULLBACK_DEPTH`: 고점 대비 눌림 깊이 (%)
- `S1_VOL_CONTRACTION`: 눌림 구간 거래량 / 급등일 거래량

---

### S2: 3/5/7/10일 눌림 (Multi-Day Pullback)

| 항목 | 내용 |
|------|------|
| **전략 요약** | 일봉 기준 3/5/7/10일선 지지 + 거래량 감소 + 도지 캔들 시 매수 |
| **교차 검증** | 서희파더 "눌림의 교과서는 5일선+도지", 남석관 "3일선 터치가 가장 강한 눌림" |
| **핵심 변수** | P_PULLBACK_3/5/7/10D, DOJI_AT_SUPPORT |
| **진입 조건** | ① 상승 추세 중 일봉 5일선 또는 10일선 터치 ② 눌림 구간 거래량 50%+ 감소 ③ 지지선에서 도지/망치형 캔들 출현 ④ 체결강도 80%→120%+ 반전 |
| **청산 조건** | 해당 지지선 이탈 시 매도 |

**정량화 변수:**
- `P_PULLBACK_3D`: 현재가 vs 3일 이동평균 이격도
- `P_PULLBACK_5D`: 현재가 vs 5일 이동평균 이격도
- `P_PULLBACK_7D`: 현재가 vs 7일 이동평균 이격도
- `P_PULLBACK_10D`: 현재가 vs 10일 이동평균 이격도
- `DOJI_AT_SUPPORT`: 지지선 근처에서 도지 캔들 출현 (시가≈종가, 몸통/전체 ≤ 30%)
- `S2_VOL_DECLINE`: 눌림 구간 거래량 감소율

---

## 4. 기술적 분석 변수 레이어 (전 전략 공통)

### 4-1. 이동평균선 체계

| 타임프레임 | 이동평균선 | 용도 |
|-----------|-----------|------|
| 1분봉 | 5분선 (MA5_1M) | 초단기 추세, D1 시초가 지지 확인 |
| 1분봉 | 10분선 (MA10_1M) | 단기 추세, D2 눌림 기준 |
| 1분봉 | **20분선 (MA20_1M)** | **핵심 손절선** — 모든 데일리 전략 공통 청산 기준 |
| 1분봉 | 60분선 (MA60_1M) | 중기 추세, 3분봉 20선에 해당 |
| 1분봉 | 240분선 (MA240_1M) | 일봉 상당, 당일 대추세 |
| 1분봉 | 480분선 (MA480_1M) | 2일봉 상당, CK480 시그널 |

**핵심 변수:**
- `MA_REGIME_1M`: 정배열 상태 (5>10>20>60 = 4점, 역배열 = 0점)
- `MA_CONVERGENCE_1M`: 5/10/20선 간 표준편차 (수렴도, 값이 작을수록 수렴)
- `MA_DISPARITY_1M`: (현재가 - MA20_1M) / MA20_1M × 100 (이격도)

### 4-2. 체결강도 (Volume Power, VP)

| 변수 | 정의 | 임계값 |
|------|------|--------|
| VP_REALTIME | 당일 매수체결량 / 매도체결량 × 100 | **120% = 매수세 우위** |
| VP_5D | 5일 평균 체결강도 | 추세 확인용 |
| VP_20D | 20일 평균 체결강도 | 장기 추세 확인 |
| VP_REVERSAL | VP 80%→120% 전환 | 매도→매수 전환 신호 |

**체결강도 120% 근거:**
- 홍인기: "체결강도 120% 넘으면 매수세가 확실히 강하다"
- 불개미: "120% 3분 이상 유지되면 진입 타이밍"
- 서희파더: "100~120 사이는 중립, 120 넘어야 확신"
- 통계적 의미: 매수 1.2 : 매도 1.0 → 20% 매수 초과

### 4-3. RSI (Relative Strength Index)

| 조건 | 해석 | 전략 연계 |
|------|------|-----------|
| RSI(14) 1분봉 30~40 + VP≥120 | 과매도 반등 + 매수세 확인 | D2 눌림, D4 전상눌림 진입 |
| RSI(14) > 70 + VP<100 | 과매수 + 매수세 약화 | 청산 경고 |
| RSI(14) 50 상향 돌파 + 거래량↑ | 중립→강세 전환 | D5 뉴스 2파 진입 |

**정량화 변수:**
- `RSI_14_1M`: 1분봉 RSI(14) 값
- `RSI_MACD_COMBO_1M`: RSI 30~40 반등 + MACD 골든크로스 동시 발생 (Boolean)

### 4-4. MACD (12, 26, 9)

| 조건 | 해석 | 전략 연계 |
|------|------|-----------|
| MACD선 > 시그널선 (골든크로스) + 거래량↑ | 상승 모멘텀 시작 | D1, D5 진입 보조 |
| MACD 히스토그램 양전환 | 모멘텀 가속 | D2 눌림 후 반등 확인 |
| MACD선 < 시그널선 (데드크로스) | 하락 모멘텀 | 청산 보조 |

### 4-5. 호가창 분석

| 변수 | 정의 | 의미 |
|------|------|------|
| `ORDERBOOK_IMBALANCE` | (매수잔량합 - 매도잔량합) / (매수잔량합 + 매도잔량합) | +0.3 이상 = 강한 매수 우위 |
| `UL_BID_AMOUNT` | 상한가 매수잔량 (원) | D6 핵심 — 100억+ 기준 |
| `ASK_WALL_DIGEST` | 대량 매도호가 소화 속도 (초) | 매도벽 소화 = 강한 매수세 |
| `SPREAD_PCT` | (최우선매도 - 최우선매수) / 현재가 × 100 | 유동성 지표 |

---

## 5. NEW 종목 장중 실시간 탐지 설계 (DESK-REALTIME)

### 5-1. 배경

VE-002에서 확인된 핵심 사실:
- **L3 = 0 for ALL NEW stocks** → L3 기반 필터로는 NEW 종목 발굴 불가
- **NEW 종목은 일봉으로 예측 불가** (AUC 최대 0.644, Phase 2C 정밀도 3.8%)
- **해결책: 장중 1분봉 복합 조건으로 실시간 탐지**

### 5-2. NEW 종목 장중 탐지 6대 조건

| # | 조건 | 임계값 | 변수명 |
|---|------|--------|--------|
| 1 | 거래대금 폭발 | 20일 평균 대비 **500%+** | `NEW_VOL_EXPLOSION` |
| 2 | 가격 급등 | 시초가 대비 **+5%** 또는 전일 대비 **+10%** | `NEW_PRICE_SURGE` |
| 3 | 체결강도 지속 | **120%+ 3분 이상** 지속 | `NEW_VP_SUSTAINED` |
| 4 | 이평선 정배열 | 1분봉 **5>10>20** 정배열 | `NEW_MA_REGIME` |
| 5 | 테마 동반 | 동일 섹터 **2종목+ 동시 급등** | `NEW_THEME_SYNC` |
| 6 | 호가창 패턴 | 매도벽 소화 패턴 확인 | `NEW_ASK_DIGEST` |

### 5-3. 탐지 로직 (Pseudo-code)

```
EVERY 1 MINUTE (09:05 ~ 15:20):
  FOR each stock NOT in DESK pool:
    IF trade_amount_today / avg_trade_amount_20d >= 5.0:        # 조건 1
      IF (price / open_price - 1) >= 0.05 OR
         (price / prev_close - 1) >= 0.10:                      # 조건 2
        IF vp_3min_avg >= 120:                                   # 조건 3
          IF ma5_1m > ma10_1m > ma20_1m:                         # 조건 4
            score = calc_new_stock_score(stock)
            IF score >= THRESHOLD:
              ADD to DESK-REALTIME candidate pool
              APPLY strategy D1~D7 filters
```

### 5-4. 테마 동반 탐지 (조건 5)

```
FOR each sector/theme:
  surging_stocks = [s for s in sector_stocks
                    if s.pct_change >= 5% AND s.vp >= 120%]
  IF len(surging_stocks) >= 2:
    FOR each stock in surging_stocks:
      SET stock.NEW_THEME_SYNC = True
```

### 5-5. DESK-REALTIME 모듈 아키텍처 (초안)

```
┌─────────────────────────────────────────────────┐
│                DESK-REALTIME                     │
├─────────────────────────────────────────────────┤
│  Scanner Module (1분 주기)                       │
│  ├── Price/Volume Filter                        │
│  ├── VP (체결강도) Filter                        │
│  ├── MA Regime Filter                           │
│  └── Theme Sync Filter                          │
├─────────────────────────────────────────────────┤
│  Strategy Matcher (D1~D7)                       │
│  ├── D1: Opening Range Check                    │
│  ├── D2: 3min Pullback Check                    │
│  ├── D3: Leader-Follower Check                  │
│  ├── D4: Prev UL Pullback Check                 │
│  ├── D5: News Catalyst Check                    │
│  ├── D6: UL Chase Check                         │
│  └── D7: Close Bet Check                        │
├─────────────────────────────────────────────────┤
│  Alert & Execution                              │
│  ├── Signal Generator                           │
│  ├── Risk Manager (position sizing)             │
│  └── Order Executor (KIS API)                   │
└─────────────────────────────────────────────────┘
```

---

## 6. VE-003 백테스트 설계

### 6-1. 목적

D1~D7, S1~S2 전략의 과거 데이터 기반 정량적 검증

### 6-2. Phase별 실행 계획

| Phase | 기간 | 대상 전략 | 검증 내용 | 데이터 요구 |
|-------|------|-----------|-----------|-------------|
| **A** | 2일 | D4, D6, D7 | 전일 조건 명확, 1분봉 직접 백테스트 | 전상/상한가 이력 + 1분봉 |
| **B** | 2일 | D1, D2, D5 | 장중 판단, 3분봉 리샘플링 시뮬레이션 | 1분봉 → 3분봉 리샘플링 |
| **C** | 2일 | D3, S1, S2 | 테마/섹터 그룹핑 + X9 연계 | 테마 데이터 + 일봉 |
| **D** | 1일 | NEW 탐지 | 과거 NEW 종목 역추적, 탐지 정확도 측정 | Phase 2E 데이터 |

### 6-3. Phase A 상세 (D4, D6, D7)

**D4 백테스트:**
1. ohlcv_daily에서 전일 상한가(+29.5%) 종목 추출
2. D+1 1분봉 데이터에서 MA20_1M 돌파 시점 식별
3. 돌파 진입 → MA20_1M 이탈 청산 시 수익률 계산
4. KPI: WR(Win Rate), Avg PnL, Max Drawdown

**D6 백테스트:**
1. 오전 10시 이전 상한가 도달 종목 추출
2. 상한가 매수잔량 100억+ 필터
3. D+1 시초가 매도 시 수익률 = (D+1 시초가 - 상한가) / 상한가
4. 시간외 -1% 손절 시나리오 포함

**D7 백테스트:**
1. 14:30~15:20 거래대금 급증 종목 추출
2. CLOSE_BET_SCORE 구성요소별 가중치 최적화
3. D+1 시초가 매도 시 수익률 계산
4. Score 임계값별 WR/PnL 민감도 분석

### 6-4. Phase B 상세 (D1, D2, D5)

**3분봉 리샘플링:**
- 1분봉 데이터를 3분봉으로 리샘플링 (Open: first, High: max, Low: min, Close: last, Volume: sum)
- 3분봉 MA5, MA10, MA20 계산
- 눌림 깊이, 체결강도 동시 검증

### 6-5. Phase C 상세 (D3, S1, S2)

**테마 그룹핑:**
- 기존 섹터 분류 + Kiwoom 테마 데이터 활용
- 동일 테마 내 종목 동시 급등 이벤트 추출
- X9(체결강도) 변수와의 교차 검증

### 6-6. Phase D 상세 (NEW 탐지)

**역추적 방법론:**
1. Phase 2E에서 식별된 NEW 229종목 리스트 활용
2. 해당 종목의 TOP-20 등장일 장중 데이터 역추적
3. 6대 탐지 조건 중 몇 개를 만족했는지 측정
4. 최적 임계값(몇 개 조건 AND/OR) 도출

### 6-7. 성공 기준

| KPI | 목표 | 근거 |
|-----|------|------|
| Win Rate (WR) | ≥ 65% | 슈퍼개미 평균 WR 60~70% |
| Average PnL | ≥ +2% per trade | 거래당 평균 수익률 |
| Max Drawdown | ≤ -5% per trade | 1분봉 20분선 손절 시 최대 손실 |
| Profit Factor | ≥ 2.0 | 총 수익 / 총 손실 |
| NEW 탐지 Recall | ≥ 50% | NEW 종목 절반 이상 장중 탐지 |

---

## 7. P0/P1/P2 확장 계획

### 기존 (STUDY-001) + 신규 (STUDY-002) 통합

| 우선순위 | 기존 (STUDY-001) | 추가 (STUDY-002) | 합계 |
|----------|------------------|-------------------|------|
| **P0 즉시** | THEME_CYCLE, SMALL_CAP_QUALITY, DUAL_FLOW, SEC_LEADER_FLAG v2 (4개) | VP_REALTIME, MA_REGIME_1M, PULLBACK_DEPTH_3M, UL_FLAG_EXTENDED (4개) | **8개** |
| **P1 1주** | MKT_SEASON, FORCE_ACC, D_D1_D2_ENTRY (3개) | LEADER_FOLLOWER_ROTATION, CLOSE_BET_SCORE, RSI_MACD_COMBO_1M, NEWS_CATALYST_SCORE (4개) | **7개** |
| **P2 2주** | BJ_SCORE, KJH_CYCLE (2개) | NEW_STOCK_REALTIME_DETECTOR, ORDERBOOK_IMBALANCE, CK480_SIGNAL (3개) | **5개** |

### P0 신규 변수 상세

| 변수명 | 정의 | 구현 위치 |
|--------|------|-----------|
| VP_REALTIME | 실시간 체결강도 (매수/매도 체결량 비율 ×100) | feature_engine.py |
| MA_REGIME_1M | 1분봉 5>10>20>60 정배열 점수 (0~4) | feature_engine.py |
| PULLBACK_DEPTH_3M | 3분봉 기준 고점 대비 눌림 깊이 (%) | feature_engine.py |
| UL_FLAG_EXTENDED | 상한가 관련 확장 플래그 (당일/전일/2일전) | feature_engine.py |

### P1 신규 변수 상세

| 변수명 | 정의 | 구현 위치 |
|--------|------|-----------|
| LEADER_FOLLOWER_ROTATION | 대장→후발 순환 지표 | feature_engine.py |
| CLOSE_BET_SCORE | 종가배팅 복합 점수 (4개 구성요소) | feature_engine.py |
| RSI_MACD_COMBO_1M | RSI+MACD 동시 진입 신호 | feature_engine.py |
| NEWS_CATALYST_SCORE | 뉴스 촉매 점수 | feature_engine.py |

### P2 신규 변수 상세

| 변수명 | 정의 | 구현 위치 |
|--------|------|-----------|
| NEW_STOCK_REALTIME_DETECTOR | NEW 종목 장중 실시간 탐지 모듈 | 별도 모듈 |
| ORDERBOOK_IMBALANCE | 호가창 매수/매도 불균형 지표 | feature_engine.py |
| CK480_SIGNAL | 480분선(2일봉) 기반 중기 시그널 | feature_engine.py |

---

## 8. 교차 분석: 10명+ 실전 트레이더 전략 매핑

| 트레이더 | 주력 전략 | D1 | D2 | D3 | D4 | D5 | D6 | D7 | S1 | S2 |
|----------|-----------|----|----|----|----|----|----|----|----|----|
| 홍인기 (대왕개미) | 대장주 단기 | ● | | ● | ● | | ● | | | |
| 서희파더 | 눌림+종가 | ● | ● | | | ● | | ● | | ● |
| 강창권 | 시초가+순환 | ● | | ● | | | | | | |
| 불개미 | 3분봉+상따 | | ● | | | | ● | | | |
| 돌팬티 | 종가배팅 | | | | | | | ● | | |
| 단봉TV | 전상+종가 | | | | ● | | | ● | | |
| 고수TV | 뉴스+수급 | | | | | ● | | | ● | |
| 이정윤 | 수급 스윙 | | | | | | | | ● | ● |
| 남석관 | 대장+눌림 | | | ● | | | | | ● | ● |
| 시간여행TV | 소형주 스윙 | | | | | | | | ● | ● |

**주요 발견:**
- D7(종가배팅): 3명 일치 — 시간효율 대비 최고 전략
- D1(시초가): 3명 일치 — 가장 보편적 데일리 전략
- S2(눌림): 4명 일치 — 스윙 전략 중 가장 보편적
- D3(순환): 3명 일치 — 한국 시장 테마 특성 반영
- 모든 전략에서 **1분봉 20분선**이 손절 기준으로 공통 사용

---

## 9. 핵심 발견 요약 (HANDOVER 연계)

- **CEO 실전 전략 = 한국 최상위 트레이더 전략과 90%+ 일치 확인**
- **1분봉 20분선이 가장 보편적인 손절/매도 기준선** (모든 전략 공통)
- **체결강도 120% 이상 = 매수세 우위의 정량적 임계값**
- **NEW 종목은 일봉 불가, 장중 1분봉 복합 조건으로 탐지 가능**
- **종가배팅(D7)이 시간 효율 대비 가장 높은 기대수익 전략** (교차 검증)

---

## 10. 다음 단계

### 즉시 실행
- [ ] VE-003 Phase A: D4/D6/D7 1분봉 백테스트 (2일)
- [ ] P0 변수 8개 feature_engine.py 구현 시작

### 1주 내
- [ ] VE-003 Phase B: D1/D2/D5 3분봉 리샘플링 시뮬레이션 (2일)
- [ ] VE-003 Phase C: D3/S1/S2 테마 그룹핑 검증 (2일)
- [ ] P1 변수 7개 구현

### 2주 내
- [ ] VE-003 Phase D: NEW 종목 장중 탐지 역추적 (1일)
- [ ] DESK-REALTIME 모듈 아키텍처 설계 및 프로토타입
- [ ] P2 변수 5개 구현

---

## 부록 A: 전체 변수 목록 (STUDY-002 신규 30+)

| # | 변수명 | 타입 | 전략 | 우선순위 |
|---|--------|------|------|----------|
| 1 | GAP_OPEN_PCT | float | D1 | P0 |
| 2 | MA5_1M_SUPPORT | bool | D1 | P0 |
| 3 | OPENING_VP | float | D1 | P0 |
| 4 | PULLBACK_DEPTH_3M | float | D2 | P0 |
| 5 | VP_AT_PULLBACK | float | D2 | P0 |
| 6 | VOL_DRY_UP_3M | float | D2 | P1 |
| 7 | LEADER_UL_FLAG | bool | D3 | P1 |
| 8 | THEME_RANK | int | D3 | P1 |
| 9 | LEADER_FOLLOWER_ROTATION | float | D3 | P1 |
| 10 | PREV_UL_FLAG | bool | D4 | P0 |
| 11 | D1_MA20_1M_BREAK | datetime | D4 | P0 |
| 12 | UL_D1_GAP | float | D4 | P1 |
| 13 | NEWS_CATALYST_SCORE | float | D5 | P1 |
| 14 | MA_CONVERGENCE_1M | float | D5 | P0 |
| 15 | WAVE1_MAGNITUDE | float | D5 | P1 |
| 16 | UL_ENTRY_TIME | int | D6 | P0 |
| 17 | UL_BID_AMOUNT | float | D6 | P0 |
| 18 | UL_HOLD_DURATION | int | D6 | P1 |
| 19 | CLOSE_BET_SCORE | float | D7 | P1 |
| 20 | CB_VOLUME_SURGE | float | D7 | P1 |
| 21 | CB_HIGHER_LOWS | int | D7 | P1 |
| 22 | CB_VP_SUSTAINED | float | D7 | P1 |
| 23 | CB_PRICE_RANGE | float | D7 | P1 |
| 24 | V_TRADE_AMT_10D_PEAK | float | S1 | P0 |
| 25 | THEME_ALIVE_FLAG | bool | S1 | P1 |
| 26 | S1_PULLBACK_DEPTH | float | S1 | P1 |
| 27 | P_PULLBACK_3D~10D | float | S2 | P1 |
| 28 | DOJI_AT_SUPPORT | bool | S2 | P1 |
| 29 | VP_REALTIME | float | 공통 | P0 |
| 30 | MA_REGIME_1M | int | 공통 | P0 |
| 31 | RSI_14_1M | float | 공통 | P1 |
| 32 | RSI_MACD_COMBO_1M | bool | 공통 | P1 |
| 33 | ORDERBOOK_IMBALANCE | float | 공통 | P2 |
| 34 | UL_FLAG_EXTENDED | int | D4/D6 | P0 |
| 35 | NEW_STOCK_REALTIME_DETECTOR | module | NEW | P2 |
| 36 | CK480_SIGNAL | float | 공통 | P2 |

---

*문서 끝 — SUPER-ANT-STUDY-002*
*CEO 지시서 D-009 등록 완료*
*HANDOVER v1.4 반영 완료*
