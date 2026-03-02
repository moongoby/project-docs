# CUR-GO100-P1-5 — 데이터 Freshness Warning + Agent Core 응답 품질 강화

- **날짜**: 2026-02-27
- **레포**: kis-autotrade-v4 (branch: phase-2c-command-center)
- **커밋**: `f532a2f7`
- **서비스**: GO100 (백억이 AI 채팅)

## 개요

Agent Core 경로(GO100_AGENT_MODE=true)에서 도구 결과의 **데이터 신선도 경고**(freshness warning) 시스템을 구현하고, LLM 시스템 프롬프트를 개선하여 **응답 품질(숫자 포맷, 정보 계층 구조, 누락 데이터 처리)**을 강화.

## 수정 파일

| 파일 | 변경 | 내용 |
|------|------|------|
| `backend/app/services/go100/ai/tool_executors.py` | +56/-4 | `_check_freshness()` 함수 추가 + 6개 도구에 freshness_warning 통합 |
| `backend/app/services/go100/ai/agent_core.py` | +22 | 시스템 프롬프트에 숫자 포맷/정보 계층/freshness 규칙 추가 |

## 작업 1: `_check_freshness()` 함수

### 로직

```python
def _check_freshness(data_date) -> Optional[str]:
    # 입력: date, datetime, str("20260226" or "2026-02-26")
    # 반환: None (신선) | "📅 ..." (2~4일) | "⚠️ ..." (5일+)
```

| 케이스 | delta | 결과 |
|--------|-------|------|
| 당일 데이터 | 0 | None (신선) |
| 전일 데이터 (평일) | 1 | None (신선) |
| 금요일 데이터, 토~월 조회 | 1~3 | None (주말 grace) |
| 2~4일 전 | 2~4 | `📅 데이터 기준일: YYYY-MM-DD (N일 전)` |
| 5일 이상 | 5+ | `⚠️ 데이터가 N일 전(YYYY-MM-DD) 기준입니다...` |
| None / 빈 문자열 | - | `⚠️ 데이터 날짜를 확인할 수 없습니다.` |

### 적용 대상 (6개 도구)

| # | 도구 | freshness 소스 |
|---|------|---------------|
| 1 | `get_market_overview` | ohlcv_daily max(date) |
| 2 | `get_market_regime` | v4_market_regime_daily.date |
| 3 | `get_stock_price` | ohlcv_daily 최신 row date |
| 4 | `get_stock_fundamentals` | stock_fundamentals.date |
| 5 | `get_investor_flow` | v4_investor_daily 최신 trade_date |
| 6 | `get_stock_ohlcv` | ohlcv_daily 최신 row date |

도구 반환 dict에 `freshness_warning` 필드가 조건부 추가됨 (신선하면 필드 없음).

## 작업 2: Agent Core 시스템 프롬프트 개선

기존 프롬프트에 4개 섹션 추가:

### 숫자 포맷 규칙
- 금액: 천 단위 쉼표 (55,300원, 1,234,567백만원)
- 퍼센트: 소수점 2자리, 부호 (+2.35%, -1.20%)
- 거래량: 천 단위 쉼표 (12,345,678주)
- 큰 금액: 억/조 단위 변환 (약 4조 1,235억원)

### Freshness Warning 처리
- `freshness_warning` 필드가 있으면 응답 맨 위에 표시
- 없으면 별도 언급 불필요

### 데이터 없음 처리
- 빈 배열/에러 → "해당 데이터가 현재 없습니다"
- 추측/일반론 대체 금지

### 정보 우선순위
1. 경고/신선도 → 2. 핵심 수치 → 3. 변화/추세 → 4. 맥락/분석 → 5. 참고사항

## 테스트 결과

### _check_freshness 단위 테스트

| 입력 | 결과 |
|------|------|
| 당일 (2026-02-27) | None |
| 전일 (2026-02-26) | None |
| 3일 전 (2026-02-24) | 📅 데이터 기준일: 2026-02-24 (3일 전) |
| 7일 전 (2026-02-20) | ⚠️ 데이터가 7일 전... |
| YYYYMMDD 포맷 | None (정상 파싱) |
| date 객체 | None (정상 처리) |
| None | ⚠️ 데이터 날짜를 확인할 수 없습니다. |

### 6개 도구 실제 실행 테스트

| 도구 | 데이터 날짜 | freshness |
|------|-----------|-----------|
| get_market_overview | 20260226 | NONE (신선) |
| get_market_regime | 2026-02-26 | NONE (신선) |
| get_stock_price | 20260226 | NONE (신선) |
| get_stock_fundamentals | 20260224 | 📅 데이터 기준일: 2026-02-24 (3일 전) |
| get_investor_flow | (최신) | NONE (신선) |
| get_stock_ohlcv | (최신) | NONE (신선) |

### API 엔드투엔드 테스트 (Agent Core 경로)

#### "삼성전자 현재가 알려줘"
```
📊 삼성전자 현재가 정보입니다.
- 현재가: 218,000원
- 전일 대비: +7.13%
- 거래량: 29,904,932주
- 시가총액: 약 1,183조 9,276억원
```
→ **PASS** — 숫자 쉼표 포맷 정확, 억/조 변환 정상

#### "삼성전자 PER, ROE 재무지표 알려줘"
```
📅 데이터 기준일: 2026-02-24 (3일 전)

삼성전자 재무지표입니다.
- PER: 30.47배
- ROE: 10.26%
```
→ **PASS** — freshness 경고가 응답 상단에 정확히 표시

#### "오늘 시장 어때?"
```
📊 2026년 2월 26일 시장 현황입니다.
- KOSPI: 6,241.53, 거래량 256,809,141주
- KOSDAQ: 1,181.40, 거래량 308,296,460주
- 상승 1,156 / 하락 2,465 / 보합 218
⚠️ 현재 거래대금 데이터는 제공되지 않고 있습니다.
```
→ **PASS** — 데이터 없음 처리 정상, 숫자 포맷 정확

## 서비스 상태

- `systemctl status go100` → active (running)
- 프론트엔드 변경 없음 (빌드 불필요)
