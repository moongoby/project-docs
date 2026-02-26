# DESK2-STRATEGY-REDESIGN-001 전략 재설계 보고서

**일자:** 2026-02-26  
**커서 ID:** DESK2-STRATEGY-REDESIGN-001  
**브랜치:** phase-2c-command-center  
**우선순위:** P0  

---

## 1. 개요

DESK2 Layer2 전략을 **watchlist 기반 stalking** 구조로 재설계하였다.  
발굴(Layer 1)에서 DiscoverySignal을 수신하면 즉시 진입하지 않고 watchlist에 등록하고, 매 봉마다 `stalk(stock_code, bar_data)`로 진입 조건을 판단한다.  
진입 조건 충족 시 CS Score를 계산해 TradeSignal을 Layer 3에 전달한다.

---

## 2. 변경된 파일 목록 (8개)

| 파일 | 변경 유형 |
|------|------------|
| `backend/app/services/trading/desk2/layer2_strategy/base_strategy.py` | 재설계 (watchlist, receive_discovery, stalk, WatchItem) |
| `backend/app/services/trading/desk2/layer2_strategy/alpha_gap.py` | 재설계 (check_entry_conditions, calculate_cs_score) |
| `backend/app/services/trading/desk2/layer2_strategy/bravo_orb.py` | 재설계 (check_entry_conditions, calculate_cs_score) |
| `backend/app/services/trading/desk2/layer2_strategy/charlie_vi.py` | 재설계 (check_entry_conditions, calculate_cs_score) |
| `backend/app/services/trading/desk2/layer2_strategy/delta_vwap.py` | 재설계 (check_entry_conditions, calculate_cs_score) |
| `backend/app/services/trading/desk2/layer2_strategy/echo_abcd.py` | 재설계 (check_entry_conditions, calculate_cs_score) |
| `backend/app/services/trading/desk2/layer2_strategy/foxtrot_sector.py` | 재설계 (check_entry_conditions, calculate_cs_score) |
| `backend/app/services/trading/desk2/layer2_strategy/golf_reversal.py` | 재설계 (check_entry_conditions, calculate_cs_score) |

**미수정:** `layer1_discovery/` 디렉토리 전체 (Cursor A 영역)

---

## 3. 설계 요약

### BaseStrategy (v2.0)

- **receive_discovery(signal)**  
  `eligible_strategies`에 본 전략이 포함되면 watchlist에 등록.  
  최대 20종목, TTL 120분, 가득 차면 가장 낮은 desk_score 종목 제거.

- **stalk(stock_code, bar_data)**  
  watchlist에 있는 종목에 대해 TTL 체크 후 `check_entry_conditions` → `calculate_cs_score`(≥50) 시 TradeSignal 반환 후 watchlist에서 제거.

- **WatchItem**  
  `signal`, `registered_at`, `stalking_count`, `last_checked` 보유.

### 전략별 진입·CS 요약

| 전략 | 진입 조건 요약 | CS 구성 요약 |
|------|----------------|--------------|
| ALPHA-GAP | 시가 유지, 체결강도>110, 스프레드<0.3%, 5분 추세 2/3 양봉, VWAP 위 | 체결강도(30)+스프레드(20)+양봉(20)+VWAP이격(15)+RVOL(15) |
| BRAVO-ORB | 09:00~09:15 박스, 1.5% 이상 돌파, 돌파봉 거래량≥평균×1.5, 4% 이내, VWAP 위 | 돌파율(30)+거래량비(30)+박스크기(20)+VWAP(20) |
| CHARLIE-VI | VI 해제, 발동가 이상 유지, bid/ask≥1.5, 해제 후 양봉 | 호가비(40)+발동가대비(30)+양봉(30) |
| DELTA-VWAP | VWAP 크로스 또는 지지 반등, RSI 40~60, 수급 양수, 거래량≥직전10봉×1.3 | RSI(25)+VWAP이격(25)+수급(25)+거래량(25) |
| ECHO-ABCD | 피보 38.2~61.8%, VWAP·MTF 필수, 3중 확인 2/3 (캔들·거래량·EMA) | 피보(25)+확인(35)+캔들(20)+VWAP(20) |
| FOXTROT-SECTOR | 상관≥0.7, 거래량 급증(×2), EMA 돌파, 대장주 상승 유지 | 상관(30)+대장주상승(35)+거래량(35) |
| GOLF-REVERSAL | BB 하단 터치 후 복귀·수급 양전환·반전캔들·거래량 급증 중 3/4 | 확인수(40)+RSI(30)+캔들(30) |

---

## 4. 테스트 결과

- **선행 조건:** DiscoverySignal v2.0 (`eligible_strategies`, `state_data`) 확인 완료.
- **AST 구문 검증:** 8개 파일 통과.
- **임포트 테스트:** BaseStrategy, WatchItem, AlphaGapStrategy, BravoOrbStrategy, CharlieViStrategy, DeltaVwapStrategy, EchoAbcdStrategy, FoxtrotSectorStrategy, GolfReversalStrategy — 전체 성공.

---

## 5. 체크리스트 (14항목)

| # | 항목 | 완료 |
|---|------|------|
| 1 | DiscoverySignal v2.0 확인 (선행 조건) | ✅ |
| 2 | BaseStrategy watchlist+stalking 구조 | ✅ |
| 3 | ALPHA-GAP 재설계 | ✅ |
| 4 | BRAVO-ORB 재설계 | ✅ |
| 5 | CHARLIE-VI 재설계 | ✅ |
| 6 | DELTA-VWAP 재설계 | ✅ |
| 7 | ECHO-ABCD 재설계 | ✅ |
| 8 | FOXTROT-SECTOR 재설계 | ✅ |
| 9 | GOLF-REVERSAL 재설계 | ✅ |
| 10 | AST 구문 검증 8파일 통과 | ✅ |
| 11 | 임포트 테스트 8클래스 성공 | ✅ |
| 12 | 코드 커밋 | ✅ |
| 13 | 보고서 push (200 확인) | 진행 예정 |
| 14 | layer1_discovery/ 미수정 확인 | ✅ |

---

## 6. 참고 사항

- **TradeSignal:** 기존 필드(ticker, strategy_code, condition_code, target_prices 등) 유지.  
  composite_score·desk_score·discovery_type은 metadata에 포함.
- **호출 측:** 기존 `evaluate(discovery_signal, indicators)`를 사용하던 코드(예: desk2_backtester)는 `receive_discovery` + `stalk(stock_code, bar_data)` 방식으로 전환 필요.  
  bar_data는 봉 데이터·지표·state_data 보강치를 담은 dict로 공급하면 된다.
