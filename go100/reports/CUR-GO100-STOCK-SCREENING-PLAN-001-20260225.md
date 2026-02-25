# CUR-GO100-STOCK-SCREENING-PLAN-001 — 종목 스크리닝 기능 기획서

**작성일**: 2026-02-25 12:00 KST
**문서 버전**: v1.0
**우선순위**: P2 (Goal 파이프라인 안정화 후 진행)
**상태**: 기획 완료, 구현 대기

---

## 1. 기능 개요

사용자가 백억이에게 "내일 오르는 종목 추천해줘", "요즘 외국인이 많이 사는 종목 뭐야?",
"AI 관련주 알려줘" 같은 질문을 하면, 시스템 내부 DB 데이터를 실시간으로 분석하여
조건에 맞는 종목 리스트를 카드 형태로 제시하고, 선택하면 해당 종목 기반 전략카드
자동 생성으로 연결하는 기능.

**핵심 원칙 (백억이 V2 설계 철학 준수)**:
모든 대화의 끝에는 실행 가능한 "다음 액션"이 있어야 한다.
종목 정보만 던져주고 끝나는 것이 아니라, "이 종목으로 전략을 만들어볼까요?"로 연결.

---

## 2. 사용자 시나리오

### 시나리오 A: "내일 오르는 종목 추천해줘"

```
사용자: 내일 오르는 종목 추천해줘

백억이: 오늘 시장 데이터를 분석해봤어요!
현재 시장 레짐은 '약한 상승(MILD_TREND_UP)'이고,
다음 조건에 해당하는 종목들을 찾았어요.

📊 상승 모멘텀 종목 TOP 5
━━━━━━━━━━━━━━━━━━━━━
[종목카드 1] 삼성SDI (006400)
  · 현재가: 425,000원 | 전일대비: +3.2%
  · 5일 외국인 순매수: +127억
  · 기술: MA5 > MA20 골든크로스 (2일전)
  · 거래량: 평균 대비 2.3배

[종목카드 2] 에코프로비엠 (247540)
  · 현재가: 182,300원 | 전일대비: +5.1%
  · 5일 기관 순매수: +89억
  · 기술: RSI 62, MACD 매수 시그널
  · 거래량: 평균 대비 3.1배

⚠️ 종목 추천이 아닌 데이터 분석 결과예요.
   투자 판단은 본인의 책임입니다.

👉 관심 있는 종목을 선택하면,
   해당 종목 기반 전략카드를 자동으로 만들어드려요!
```

### 시나리오 B: "외국인이 많이 사는 종목"

```
사용자: 요즘 외국인이 많이 사는 종목 뭐야?

백억이: 최근 5거래일 외국인 순매수 상위 종목을 분석했어요.

📊 외국인 순매수 TOP 5 (최근 5일 누적)
━━━━━━━━━━━━━━━━━━━━━
[종목카드 1] SK하이닉스 (000660)
  · 5일 외국인 순매수: +2,341억
  · 현재가: 178,500원 | 5일 수익률: +4.7%
  · 외국인 보유비중: 52.3% (+0.8%p)

👉 이 종목들로 수급 추종 전략을 만들어볼까요?
```

### 시나리오 C: "AI 관련주 알려줘"

```
사용자: AI 관련주 알려줘

백억이: AI/반도체 테마에 해당하는 종목을 분석했어요.

📊 AI 테마 종목 분석 (12개 중 상위 5개)
━━━━━━━━━━━━━━━━━━━━━
[종목카드 1] 한미반도체 (042700)
  · 테마: AI 반도체 후공정
  · 현재가: 98,700원 | 월간 수익률: +12.3%

👉 AI 테마 종목으로 포트폴리오를 구성해볼까요?
```

---

## 3. 인텐트 분류

### 새로운 인텐트: `stock_screening`

| 패턴 | 예시 |
|------|------|
| `(추천\|알려줘\|찾아줘\|골라줘)` + 종목 맥락 | "종목 추천해줘" |
| `(오르는\|상승\|급등\|유망\|좋은)` + `종목` | "내일 오르는 종목" |
| `(외국인\|기관)` + `(매수\|순매수\|사는)` | "외국인이 많이 사는 종목" |
| `(관련주\|테마주\|섹터)` | "AI 관련주" |
| `(거래량\|급등\|신고가\|돌파)` | "거래량 급증 종목" |
| `(배당\|고배당)` | "배당 좋은 종목" |
| `(저평가\|PER\|PBR)` + `(낮은\|저)` | "PER 낮은 종목" |

**우선순위**: goal_setup > stock_screening > stock_info > strategy_create > free_chat

---

## 4. 스크리닝 엔진 설계

### 4.1 스크리닝 카테고리

| 카테고리 ID | 이름 | 조건 | DB 소스 | 데이터 상태 |
|------------|------|------|---------|------------|
| `momentum_up` | 상승 모멘텀 | MA5>MA20 + 거래량2배↑ + 양봉3일↑ | ohlcv_daily | 🟢 GREEN |
| `foreign_buy` | 외국인 순매수 | 5일 순매수 누적 상위 | v4_investor_daily | 🟢 GREEN |
| `institution_buy` | 기관 순매수 | 5일 순매수 누적 상위 | v4_investor_daily | 🟢 GREEN |
| `volume_surge` | 거래량 급증 | 당일/20일평균 >= 3배 | ohlcv_daily | 🟢 GREEN |
| `new_high` | 신고가 | 52주 신고가 돌파 | ohlcv_daily | 🟢 GREEN |
| `theme` | 테마/섹터 | 테마 키워드 매칭 | v4_theme_daily | 🟡 YELLOW |
| `undervalued` | 저평가 | PER<10 & PBR<1 & ROE>10% | v4_financial_ratios | 🟢 GREEN |
| `high_dividend` | 고배당 | 배당수익률 상위 | v4_financial_ratios | 🟡 YELLOW |
| `breakout` | 돌파 | 볼린저밴드 상단 돌파 + 거래량 | ohlcv_daily | 🟢 GREEN |
| `regime_fit` | 레짐 적합 | 현재 레짐에서 과거 수익률 높은 종목군 | v4_market_regime_daily | 🟡 YELLOW |

### 4.2 스크리닝 쿼리 예시 (momentum_up)

```sql
WITH recent AS (
  SELECT stock_code,
         close, volume,
         AVG(close) OVER (PARTITION BY stock_code ORDER BY date ROWS 4 PRECEDING) as ma5,
         AVG(close) OVER (PARTITION BY stock_code ORDER BY date ROWS 19 PRECEDING) as ma20,
         AVG(volume) OVER (PARTITION BY stock_code ORDER BY date ROWS 19 PRECEDING) as avg_vol_20,
         ROW_NUMBER() OVER (PARTITION BY stock_code ORDER BY date DESC) as rn
  FROM ohlcv_daily
  WHERE date >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT r.stock_code, su.stock_name, r.close, r.volume,
       r.ma5, r.ma20, r.volume::float / NULLIF(r.avg_vol_20, 0) as vol_ratio
FROM recent r
JOIN stock_universe su ON r.stock_code = su.stock_code
WHERE r.rn = 1 AND r.ma5 > r.ma20 AND r.volume > r.avg_vol_20 * 2
  AND su.market_cap > 100000000000
ORDER BY vol_ratio DESC LIMIT 10;
```

### 4.3 LLM 질문→카테고리 매핑

```python
# screening_classifier.py
SCREENING_PATTERNS = {
    'momentum_up': [r'오르는|상승|급등|모멘텀|올라가는'],
    'foreign_buy': [r'외국인.*(매수|사는|순매수|사고)'],
    'institution_buy': [r'기관.*(매수|사는|순매수|사고)'],
    'volume_surge': [r'거래량.*(급증|폭발|많은|증가)'],
    'new_high': [r'신고가|52주.*최고|역대.*최고'],
    'theme': [r'관련주|테마주|섹터|관련.*종목'],
    'undervalued': [r'저평가|PER.*낮|PBR.*낮|가치주'],
    'high_dividend': [r'배당|고배당|배당.*좋은'],
    'breakout': [r'돌파|브레이크아웃|저항.*돌파'],
}
```

---

## 5. 백엔드 API 설계

### 5.1 신규 엔드포인트

**POST /api/go100/screening/search**

Request:
```json
{
  "category": "momentum_up",
  "theme": "AI",
  "limit": 5,
  "filters": { "min_market_cap": 100000000000 }
}
```

Response:
```json
{
  "category": "momentum_up",
  "category_name": "상승 모멘텀",
  "market_regime": "MILD_TREND_UP",
  "results": [
    {
      "rank": 1, "stock_code": "006400", "stock_name": "삼성SDI",
      "current_price": 425000, "change_pct": 3.2, "volume_ratio": 2.3,
      "signals": ["MA5>MA20 골든크로스", "거래량 2.3배"],
      "foreign_5d_net": 12700000000, "market_cap": 29300000000000
    }
  ],
  "disclaimer": "본 데이터는 과거 시장 데이터 분석 결과이며, 투자 권유가 아닙니다."
}
```

**POST /api/go100/screening/to-strategy** (종목 선택 → 전략카드 변환)

```json
{
  "stock_codes": ["006400", "247540"],
  "strategy_type": "swing",
  "user_message": "이 종목들로 스윙 전략 만들어줘"
}
```

### 5.2 신규 파일 구조

```
backend/app/
├── services/go100/screening/
│   ├── __init__.py
│   ├── screening_engine.py      # 스크리닝 쿼리 실행 엔진
│   ├── screening_classifier.py  # 자연어 → 카테고리 매핑
│   └── screening_formatter.py   # 결과 포맷팅 (카드 데이터)
├── routers/go100/
│   └── screening_router.py      # /api/go100/screening/* 엔드포인트
```

### 5.3 ai_router 연동

```python
elif intent == "stock_screening":
    category, theme = screening_classifier.classify_screening(message)
    results = await screening_engine.search(category, theme, limit=5)
    return {
        "response": screening_formatter.format_chat_response(results),
        "status": "screening_result",
        "data": {
            "type": "stock_screening",
            "category": category,
            "results": results,
            "actions": [
                {"label": "이 종목으로 전략 만들기", "action": "create_strategy"},
                {"label": "더 많은 종목 보기", "action": "load_more"},
                {"label": "다른 조건으로 검색", "action": "new_search"}
            ]
        }
    }
```

---

## 6. 프론트엔드 UI 설계

### 6.1 신규 컴포넌트

**StockScreeningCards.tsx** — 종목 카드 리스트
- 종목명, 현재가, 등락률, 핵심 시그널, 수급 바 차트
- 카드 선택 시 체크 표시
- 하단 "선택 종목으로 전략 만들기" 버튼

**StockDetailMini.tsx** — 종목 상세 미니 팝업
- 최근 20일 미니 차트
- PER, PBR, 시총
- 최근 5일 수급 요약

### 6.2 ChatWidget 연동

```typescript
{m.data?.type === 'stock_screening' && (
  <StockScreeningCards
    results={m.data.results}
    actions={m.data.actions}
    onStockSelect={(codes) => handleScreeningAction('create_strategy', codes)}
    onAction={(action) => handleScreeningAction(action)}
  />
)}
```

### 6.3 타입 정의 (types/ai.ts 추가)

```typescript
interface StockScreeningResult {
  rank: number;
  stock_code: string;
  stock_name: string;
  sector: string;
  current_price: number;
  change_pct: number;
  volume_ratio: number;
  signals: string[];
  foreign_5d_net: number;
  institution_5d_net: number;
  market_cap: number;
  per: number;
  pbr: number;
}

interface StockScreeningData {
  type: 'stock_screening';
  category: string;
  results: StockScreeningResult[];
  actions: { label: string; action: string }[];
}
```

---

## 7. 규제 준수

**금지**: 특정 종목 매매 시점/가격 예측, "이 종목을 사세요" 직접적 투자 권유
**허용**: 과거 데이터 기반 조건 매칭 결과, "이런 조건에 해당하는 종목입니다" 형태 정보 제공
**필수 고지**: 모든 스크리닝 결과에 면책 문구 + "AI 생성 분석 결과" 표시

---

## 8. 성능 목표

| 항목 | 목표 |
|------|------|
| 스크리닝 응답 시간 | 2초 이내 |
| 캐시 TTL | 장중 5분, 장 마감 후 1시간 |
| 결과 수 | 기본 5, 최대 10 |

필요 인덱스:
```sql
CREATE INDEX IF NOT EXISTS idx_ohlcv_daily_date_code ON ohlcv_daily(date, stock_code);
CREATE INDEX IF NOT EXISTS idx_investor_daily_date_code ON v4_investor_daily(date, stock_code);
CREATE INDEX IF NOT EXISTS idx_financial_ratios_code ON v4_financial_ratios(stock_code);
```

---

## 9. 구현 단계

| Phase | 내용 | 예상 소요 | 의존성 |
|-------|------|----------|--------|
| A | 인텐트 stock_screening 추가 + 분류기 | 2h | Goal 핫픽스 완료 |
| B | screening_engine 코어 (3개 카테고리) | 4h | Phase A |
| C | screening_router API + 포맷터 | 2h | Phase B |
| D | StockScreeningCards UI + ChatWidget 연동 | 3h | Phase C |
| E | 나머지 카테고리 (theme, undervalued 등) | 4h | Phase D |
| F | to-strategy 연동 (종목→전략 자동 생성) | 3h | Phase E |
| G | 캐시, 인덱스, 성능 최적화 | 2h | Phase F |
| **합계** | | **~20h (2.5일)** | |

---

## 10. 향후 확장

- KIS API 실시간 연동 (현재가, 호가, 체결강도)
- 뉴스 키워드 기반 테마 자동 감지
- 레짐 변화 시 자동 스크리닝 알림
- 사용자 관심 종목 워치리스트 자동 모니터링
- 스크리닝 결과 기반 자동 전략 포트폴리오 구성

---

## 보고 요약

- **기능**: 백억이 자연어 → DB 기반 종목 스크리닝 → 카드 UI → 전략 자동 생성 연결
- **DB 활용**: ohlcv_daily(260만건), v4_investor_daily(17만건), v4_financial_ratios(4.6만건)
- **10개 카테고리**: 모멘텀, 수급(외국인/기관), 거래량, 신고가, 테마, 저평가, 배당, 돌파, 레짐적합
- **구현 소요**: 약 2.5일 (Goal 파이프라인 안정화 후)
- **규제 준수**: 면책 문구 필수, 투자 권유 금지
