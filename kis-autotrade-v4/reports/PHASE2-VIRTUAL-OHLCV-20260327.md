# Phase 2: 가상매매 모드 기술지표 실제 OHLCV 교체 보고서

> 작성일: 2026-03-27
> 커밋: `d2df117c`
> 브랜치: phase-2c-command-center

---

[인계 확인]
직전 완료: PHASE1-RUNNER (b63fce90)
현재 단계: Phase 2
CEO 지시 적용: D-001, D-002, D-006, D-007
strategy_cards: 7 DESK + 10 HYPOTHESIS
open_positions: 0 (가상매매 모드)

---

## 구현 목표

가상매매 모드(`--mode virtual --action signal`)의 기술지표를 **랜덤값(make_neutral_signal) → 실제 OHLCV 기반(make_real_signal)**으로 교체.

## 수정 내용

### 1. `_load_ohlcv_sync()` — OHLCV 동기 캐시 (L596-652)
- ohlcv_daily 테이블에서 최근 120일 일봉을 psycopg2로 일괄 로드
- `indicator_precompute()` 호출하여 MA5/MA20/MA60, RSI14, MACD, ADX, BB, Stoch 등 사전계산
- 종목별 DataFrame으로 분리하여 `_virtual_ohlcv_cache` dict에 캐시
- 장 시작 시 1회 프리로드, 장중 재사용 패턴

### 2. `make_real_signal()` — 실제 OHLCV 기반 TradeSignal (L655-848)
- OHLCV 캐시에서 종목의 최신 행 추출
- **실제 지표값**: RSI14, MA5/MA20/MA60, MACD_line/signal, ADX, BB, Stoch_K
- **ATR14**: 최근 14일 True Range 평균으로 계산
- **거래량비율**: 당일 거래량 / 20일 평균
- **가격 위치**: (close - low) / (high - low)
- **시장 레짐**: MA20 vs MA60 위치 기반 판단 (BULL/FLAT/BEAR)
- **CS 등급**: 가격 vs MA 위치 기반 (A/B/C/D)
- **기술 등급**: RSI + MACD + ADX 종합 (TOP3/TOP5/TOP10/LOWER)
- CandleData, VwapData 모두 실제 OHLCV 기반으로 생성

### 3. 가상매매 루프 교체 (action_signal)
- 기존: `_LEGACY_make_neutral_signal(sid, rng)` → 랜덤 지표
- 변경: `make_real_signal(code, price, sid, cache)` → 실제 OHLCV 지표
- **실패 시 legacy 폴백 유지** (OHLCV 데이터 없는 종목 대비)

### 4. NXT 신호도 동일하게 교체
- `action_nxt_signal()` 루프에서도 `_load_ohlcv_sync()` + `make_real_signal()` 적용

## 검증 체크리스트

- [x] 구현 목표: 가상매매 기술지표를 랜덤→실제 OHLCV 기반으로 교체
- [x] 검증 방법: Python 단위 테스트 (DESK 종목 5건 × 전략 2종 = 10건)
- [x] 완료 기준: make_real_signal() 성공률 100%, 실제 RSI/vol_ratio/regime 반환
- [x] 실패 기준: make_real_signal() 실패 시 legacy 폴백 → 0건 (모두 성공)
- [x] 서비스 재시작 확인: 가상매매 모드 전용, 서비스 독립 실행
- [x] 에러 로그 0건: import 정상, syntax OK

## 검증 결과

```
=== Phase 2 검증 결과 ===
테스트 종목: 5건
실제 OHLCV 신호: 10건
레거시 폴백: 0건
성공률: 100%

샘플 신호:
  0004V0: price=21,650, RSI=59.2, vol=3.18, regime=BEAR, cs=B
  013000: price=1,549, RSI=61.6, vol=6.71, regime=FLAT, cs=A
  014160: price=1,636, RSI=73.9, vol=12.87, regime=FLAT, cs=A
```

## Before/After 비교

| 지표 | Before (랜덤) | After (실제) |
|------|--------------|-------------|
| RSI14 | `rng.uniform(30, 70)` | `indicator_precompute()` RSI14 |
| 거래량비율 | `rng.uniform(0.8, 2.5)` | 당일 거래량 / 20일 평균 |
| MACD | 없음 | MACD line, signal 실제값 |
| ADX | 없음 | ADX(14) 실제값 |
| MA 정배열 | 없음 | MA5/MA20/MA60 실제 비교 |
| 시장레짐 | 랜덤 가중치 | MA20 vs MA60 실제 위치 |
| CS 등급 | 랜덤 가중치 | 가격-MA 위치 기반 |
| 가격위치 | `rng.uniform(0.15, 0.65)` | (close-low)/(high-low) |
| ATR14 | `price * rng.uniform(0.008, 0.02)` | 14일 TR 평균 |

## 향후 Phase 연결

- **Phase 3**: 가설엔진 HYPOTHESIS 카드 → 통합엔진 연결 (이미 완료)
- **Phase 4**: 실매매 모드에서 동일 `make_real_signal()` 사용 예정
- **TODO**: KOSDAQ 등락률은 별도 API 연결 필요 (현재 임시값)
