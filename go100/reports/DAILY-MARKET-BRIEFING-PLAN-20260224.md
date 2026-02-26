# 당일 투자 환경 브리핑 기획 보고

**작성일**: 2026-02-24  
**목적**: 로그인·대시보드 진입 시 “오늘의 투자 환경”을 한눈에 보여주는 브리핑(레짐, 지수, 환율, 코인, 주요 지수 등)을 기획하고, 현재 보유 데이터·부족 데이터·노출 위치·API를 정리한다.

---

## 1. 브리핑에 넣을 항목 (목표)

| 순위 | 항목 | 설명 | 예시 문장/표시 |
|------|------|------|----------------|
| 1 | **시장 레짐** | 당일(또는 최신) 시장 국면 | "오늘 레짐: 횡보(SIDEWAYS)" / "상승 추세(MILD_TREND_UP)" |
| 2 | **국내 주요 지수** | KOSPI, KOSDAQ 전일 대비 | "KOSPI 2,580 (+0.3%), KOSDAQ 850 (-0.2%)" |
| 3 | **환율** | USD/KRW 등 | "환율 1,380원 (전일 대비 +5원)" |
| 4 | **코인(가상자산)** | 비트코인 등 대표 1~2종 | "BTC 98,000달러 (+1.2%)" |
| 5 | **해외 주요 지수** | S&P500, 나스닥, VIX 등 | "S&P500 5,100 (+0.5%), VIX 14" |

- 1·2는 **현재 시스템 내 DB로 제공 가능**, 3·4·5는 **외부 API 또는 신규 수집**이 필요하다.

---

## 2. 현재 데이터 현황

### 2.1 보유 데이터 (즉시 활용 가능)

| 데이터 | 테이블/소스 | 내용 | 비고 |
|--------|-------------|------|------|
| **시장 레짐** | `v4_market_regime_daily` | 일자별 regime, regime_score. 5단계: STRONG_TREND_UP, MILD_TREND_UP, SIDEWAYS, MILD_TREND_DOWN, STRONG_TREND_DOWN | PRE_MARKET·오케스트레이터에서 갱신. 최신 1건 조회 가능 |
| **국내 지수** | `index_daily` | index_code(0001=KOSPI, 1001=KOSDAQ 등), date, open, high, low, close, volume | `collect_index_daily.sh` 등으로 수집. 최신 일자 close + 전일 close로 전일 대비 % 계산 가능 |

- **레짐**: `backend/app/services/market/regime_detector.py`, `backend/app/routers/v4_dashboard.py`(overview) 등에서 이미 조회 중.
- **지수**: `backend/app/routers/v4_chart.py` — `GET /api/v4/chart/index/{index_code}`. `index_daily` 최신 N일 조회로 “오늘” 또는 “최신 거래일” 기준 종가·전일대비 제공 가능.

### 2.2 부족 데이터 (신규 수집 또는 외부 API 필요)

| 데이터 | 현재 상태 | 확보 방안 (예) |
|--------|-----------|----------------|
| **환율** | 프로젝트 내 전용 테이블·API 없음 (감사 리포트에서 “금리·환율·VIX 등 외부 지표 테이블 없음” 명시) | 한국투자증권 API(해외주식/환율)·공공데이터·또는 무료 환율 API(일 1회 수집 후 테이블 저장) |
| **코인(가상자산)** | 없음 (crypto는 암호화 모듈만 존재) | CoinGecko / Binance 등 무료 API로 BTC·ETH 종가·전일대비 수집, 일 1회 저장 테이블 |
| **해외 주요 지수** | 없음 | Yahoo Finance API, 공공데이터, 또는 KIS 해외지수 API(지원 시)로 S&P500·나스닥·VIX 수집, 일 1회 저장 테이블 |

- 금리·VIX·put/call 등은 레짐 판정·고급 브리핑에서 활용 가능하나, 1차 브리핑에서는 “레짐 + 국내 지수”만으로도 의미 있는 한 줄 요약 가능.

---

## 3. 노출 위치 제안

| 위치 | 설명 | 우선순위 |
|------|------|----------|
| **로그인 직후 “오늘의 브리핑” 카드** | 기존 `TodayBriefingCard`에 “투자 환경” 블록 추가. 레짐 한 줄 + 국내 지수 한 줄(최소). 환율·코인·해외지수는 데이터 확보 후 추가 | 1단계: 레짐+국내지수만 |
| **대시보드 상단 “오늘의 시장” 위젯** | 백억이 배너 아래 또는 메트릭 카드 옆에 별도 카드. 레짐·KOSPI·KOSDAQ·(선택)환율·코인·해외지수 요약 | 2단계: 카드 전용 |
| **백억이 음성/채팅** | “오늘 시장 어때?” 질문 시 브리핑 문장 생성에 활용 (이미 로그인 브리핑 기획에서 “시장 한줄” 언급) | 3단계 |

- 1단계: **로그인 브리핑 카드**에 “오늘 레짐: OOO”, “KOSPI xxx (전일대비 ±x.x%), KOSDAQ xxx (±x.x%)” 한두 줄 추가.
- 2단계: 데이터가 늘어나면 **대시보드 전용 “오늘의 시장” 카드**로 분리해 레짐·지수·환율·코인·해외지수 표 형식 또는 짧은 문장으로 노출.

---

## 4. API 설계 제안

### 4.1 옵션 A: 전용 브리핑 API (권장)

- **엔드포인트**: `GET /api/v1/dashboard/market-briefing`  
  (또는 `GET /api/v1/dashboard/briefing` 로 로그인 브리핑 문장과 통합)
- **응답 예시** (1단계: 레짐 + 국내 지수만):

```json
{
  "date": "2026-02-24",
  "market_regime": {
    "regime": "SIDEWAYS",
    "regime_label_ko": "횡보",
    "regime_score": 3.0,
    "as_of_date": "2026-02-23"
  },
  "indices": [
    { "code": "0001", "name": "KOSPI", "close": 2580.5, "change_pct": 0.3, "prev_close": 2572.8 },
    { "code": "1001", "name": "KOSDAQ", "close": 850.2, "change_pct": -0.2, "prev_close": 851.9 }
  ],
  "fx": null,
  "crypto": null,
  "global_indices": null
}
```

- **2단계 이후**: `fx`(환율), `crypto`(BTC 등), `global_indices`(S&P500, VIX 등) 필드 추가. 데이터 없으면 `null` 또는 빈 배열.
- **백엔드**:  
  - 레짐: `v4_market_regime_daily` ORDER BY date DESC LIMIT 1.  
  - 지수: `index_daily`에서 최신 2거래일(오늘·전일) 조회해 close 기준 전일대비 % 계산. index_code IN ('0001','1001').

### 4.2 옵션 B: 기존 summary 확장

- `GET /api/v1/dashboard/summary` 응답에 `market_briefing` 객체 추가.
- 장점: 요청 1회. 단점: summary 용량·응답 시간 증가. 브리핑만 필요한 경우 비효율.

**권장**: **옵션 A**. 로그인 직후·대시보드 상단에서 “브리핑만” 가져올 때 전용 API가 적합.

---

## 5. 레짐 한글 라벨

- 브리핑 문장에 그대로 노출할 때 사용.

| regime | regime_label_ko |
|--------|-----------------|
| STRONG_TREND_UP | 강한 상승 |
| MILD_TREND_UP | 약한 상승 |
| SIDEWAYS | 횡보 |
| MILD_TREND_DOWN | 약한 하락 |
| STRONG_TREND_DOWN | 강한 하락 |

---

## 6. 단계별 정리

| 단계 | 내용 | 산출물 |
|------|------|--------|
| **1단계** | 레짐 + 국내 지수(KOSPI, KOSDAQ)만. 전용 API `GET /api/v1/dashboard/market-briefing` 추가. 로그인 브리핑 카드에 “오늘 레짐: OOO”, “KOSPI xxx (±x.x%), KOSDAQ xxx (±x.x%)” 한두 줄 추가 | 백엔드 market-briefing API, 프론트 TodayBriefingCard 확장 또는 “오늘의 시장” 1줄 |
| **2단계** | 대시보드에 “오늘의 시장” 전용 카드(위젯) 추가. 표 또는 문장으로 레짐·지수 표시. (선택) 환율·코인·해외지수용 테이블·수집 스크립트 설계 | 위젯 컴포넌트, (선택) fx/crypto/global_indices 수집 설계 |
| **3단계** | 환율·코인·해외 주요 지수 데이터 수집 및 저장. market-briefing API에 fx, crypto, global_indices 필드 추가. 브리핑 카드/위젯에 반영 | 수집 스크립트·테이블·API 확장·UI 반영 |

---

## 7. 요약

- **당일 투자 환경 브리핑**에 넣을 항목: (1) 시장 레짐, (2) 국내 주요 지수(KOSPI, KOSDAQ), (3) 환율, (4) 코인, (5) 해외 주요 지수.
- **지금 바로 쓸 수 있는 것**: 레짐(`v4_market_regime_daily`), 국내 지수(`index_daily`). 이 둘만으로 1단계 브리핑 문장 구성 가능.
- **추가 확보 필요**: 환율·코인·해외 지수는 외부 API 또는 신규 수집 후 테이블·API 확장 필요.
- **노출**: 1단계는 로그인 직후 “오늘의 브리핑” 카드에 레짐·국내 지수 한두 줄 추가. 2단계에서 “오늘의 시장” 전용 카드 및 환율·코인·해외지수 반영 권장.

이상으로 당일 투자 환경 브리핑 기획을 정리하였다.
