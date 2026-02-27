# CUR-GO100-SCREENING-V2 — 자체 스크리닝 엔진 V2: 조건식 조합 검색

- **날짜**: 2026-02-27
- **레포**: kis-autotrade-v4 (branch: phase-2c-command-center)
- **커밋**: `652ebe97`
- **서비스**: GO100 (백억이 AI 채팅)

## 개요

기존 3개 필터(momentum_up, foreign_buy, theme)만 지원하던 채팅 스크리닝 엔진을 **13개 필터 + 조합 검색**으로 확장. 백테스트용 `universe/` 모듈의 필터 SQL 로직을 참조하되, 채팅용으로 종목 상세정보(이름, 가격 등)를 함께 반환하도록 구현.

## 수정 파일

| 파일 | 변경 | 내용 |
|------|------|------|
| `backend/app/services/go100/screening_engine.py` | +639/-19 | 10개 신규 필터 + combined + detect/run/format 확장 |
| `backend/app/services/go100/ai/intent_router.py` | +11 | STOCK_SCREENING_KEYWORDS 22개 키워드 추가 |
| `backend/app/services/go100/ai/response_formatter.py` | +1/-1 | screening_unavailable 에러 메시지 업데이트 |

## 신규 필터 목록

| # | 필터 ID | 조건 | 데이터 소스 |
|---|---------|------|------------|
| 1 | `golden_cross` | 5일선 > 20일선 돌파 (전일 5MA<20MA → 금일 5MA>20MA) | ohlcv_daily |
| 2 | `death_cross` | 5일선 < 20일선 돌파 | ohlcv_daily |
| 3 | `ma_align_bull` | 5일 > 20일 > 60일 정배열 | ohlcv_daily |
| 4 | `rsi_oversold` | RSI(14) < 30 과매도 | ohlcv_daily |
| 5 | `rsi_overbought` | RSI(14) > 70 과매수 | ohlcv_daily |
| 6 | `value_low_per` | PER < 10 AND ROE > 5% | stock_fundamentals |
| 7 | `institution_buy` | 기관 연속 순매수 >= 3일 | v4_investor_daily |
| 8 | `volume_surge` | 거래량 > 20일 평균 x 3 | ohlcv_daily |
| 9 | `gap_up` | 시가 > 전일종가 x 1.03 | ohlcv_daily |
| 10 | `trade_strength` | 체결강도 평균 > 120 | v4_trade_strength_history |

## 조합 검색 (combined)

사용자가 2개 이상 필터 키워드를 한 문장에 넣으면 자동으로 교집합 검색:

- "외국인 매수 저PER 종목" → `foreign_buy ∩ value_low_per`
- "골든크로스 거래량 폭발 종목" → `golden_cross ∩ volume_surge`

빈 결과 필터도 교집합에 포함하여 정확한 결과 보장 (빈 집합 버그 수정 완료).

## 테스트 결과

### detect_screening_type 매칭 테스트

| 입력 메시지 | 감지 타입 | 결과 |
|------------|----------|------|
| "골든크로스 종목 찾아줘" | golden_cross | OK |
| "RSI 과매도 종목" | rsi_oversold | OK |
| "외국인 매수 저PER 종목" | combined (value_low_per, foreign_buy) | OK |
| "정배열 종목" | ma_align_bull | OK |
| "모멘텀 상승 종목" | momentum_up | OK (하위호환) |
| "거래량 폭발 종목 보여줘" | volume_surge | OK |
| "갭상승 종목" | gap_up | OK |
| "기관매수 종목" | institution_buy | OK |
| "체결강도 높은 종목" | trade_strength | OK |
| "데드크로스 종목" | death_cross | OK |
| "과매수 종목" | rsi_overbought | OK |

### DB 쿼리 실행 테스트 (12개 필터)

| 필터 | 결과 건수 | 첫 번째 종목 |
|------|----------|-------------|
| golden_cross | 10 | 코리아써우 (007815) |
| death_cross | 10 | 와이제이링크 (209640) |
| ma_align_bull | 10 | 현대ADM (187660) |
| rsi_oversold | 10 | 인크레더블버즈 (064090) |
| rsi_overbought | 10 | 삼익THK (004380) |
| value_low_per | 10 | DH오토넥스 (000300) |
| institution_buy | 0 | (데이터 부재) |
| volume_surge | 10 | 오픈놀 (440320) |
| gap_up | 10 | 젠큐릭스 (229000) |
| trade_strength | 10 | 363510 |
| momentum_up | 10 | 오픈놀 (440320) |
| foreign_buy | 0 | (데이터 부재) |

### 조합 검색 테스트

| 조합 | 결과 건수 |
|------|----------|
| golden_cross + volume_surge | 6 |
| volume_surge + rsi_oversold | 2 |
| foreign_buy + value_low_per | 0 (foreign_buy 빈 결과 → 교집합 0, 정상) |

### API 통합 테스트 (curl → /api/go100/ai/chat)

- "골든크로스 종목 찾아줘" → 정상 응답 (10건, 포맷 정상)
- "RSI 과매도 종목" → 정상 응답 (10건)
- "거래량 폭발 골든크로스 종목" → combined 정상 (6건)
- "저PER 가치주 찾아줘" → 정상 응답 (10건)
- "체결강도 높은 종목" → 정상 응답 (10건)
- "모멘텀 상승 종목 찾아줘" → 기존 필터 하위호환 정상

### Intent Router 검증

모든 테스트 메시지가 `stock_screening` 인텐트로 정확히 라우팅됨.

## 설계 결정

1. **단일 SQL CTE 쿼리**: 각 필터는 window function + CTE로 한 번의 쿼리로 결과 반환
2. **교집합 방식**: combined 모드에서 각 필터 결과의 stock_code 교집합 → 상세정보 조회
3. **기존 3개 필터 유지**: momentum_up, foreign_buy, theme 100% 하위호환
4. **_REQUEST_LABEL_MAP 축소**: 실제 지원 조건은 mismatch 경고하지 않도록 변경

## 서비스 상태

- `systemctl status go100` → active (running)
- 프론트엔드 변경 없음 (빌드 불필요)
