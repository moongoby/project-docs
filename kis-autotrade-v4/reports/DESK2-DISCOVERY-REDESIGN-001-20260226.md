# DESK2-DISCOVERY-REDESIGN-001 실행 보고서

**일자:** 2026-02-26  
**커서 ID:** DESK2-DISCOVERY-REDESIGN-001  
**브랜치:** phase-2c-command-center  
**우선순위:** P0  

---

## 1. 변경된 파일 목록 (7개 + config + manager)

| 파일 | 변경 유형 |
|------|------------|
| `backend/app/services/trading/desk2/models/discovery_signal.py` | 재설계 |
| `backend/app/services/trading/desk2/layer1_discovery/base_condition.py` | 시그널 빌더 시그니처 변경 |
| `backend/app/services/trading/desk2/layer1_discovery/c1_gap_discovery.py` | 재설계 (GapDiscovery) |
| `backend/app/services/trading/desk2/layer1_discovery/c2_opening_strong.py` | 신규 (기존 c2_range_breakout 대체) |
| `backend/app/services/trading/desk2/layer1_discovery/c3_vi_explosion.py` | 재설계 (VIExplosionDiscovery) |
| `backend/app/services/trading/desk2/layer1_discovery/c4_intraday_surge.py` | 신규 (기존 c4_vwap_recovery 대체) |
| `backend/app/services/trading/desk2/layer1_discovery/c5_pullback_discovery.py` | 신규 (기존 c5_pullback 대체) |
| `backend/app/services/trading/desk2/layer1_discovery/c6_sector_lag.py` | 재설계 (SectorLagDiscovery) |
| `backend/app/services/trading/desk2/layer1_discovery/c7_oversold_rebound.py` | 재설계 (OversoldReboundDiscovery) |
| `backend/app/services/trading/desk2/layer1_discovery/discovery_manager.py` | 7개 조건 통합, 새 클래스 import |
| `backend/app/services/trading/desk2/config/desk2_config.yaml` | discovery_redesign 섹션 추가 |

**삭제된 파일:** `c2_range_breakout.py`, `c4_vwap_recovery.py`, `c5_pullback.py`

---

## 2. 파일별 제거/추가 항목 요약

### discovery_signal.py
- **제거:** `ticker`, `condition_code`, `detail_scores`, `discovered_at` (필드), `primary_strategy`/`cross_strategies` (기존 명세 기준)
- **추가:** `stock_code`, `condition_id`, `timestamp`, `market_state`, `eligible_strategies: list[str]`, `state_data: dict`, `time_slot`, `discovery_type`
- **호환:** `ticker`, `condition_code`, `discovered_at` 프로퍼티로 하위 호환 유지

### C1 (c1_gap_discovery.py)
- **제거:** 체결강도·호가 스프레드 기반 점수, primary_strategy='ALPHA_GAP' 하드코딩
- **추가:** Gate (gap 3~15%, RVOL≥2, 시총≥3000억), 갭(25)+RVOL(25)+시장(15)+뉴스(15)+품질(10)+ADX(10), state_data, eligible_strategies, discovery_type=GAP_UP, time_slot=OPENING

### C2 (c2_opening_strong.py, 신규)
- **제거:** 15분 박스·돌파 판단 전체 (기존 c2_range_breakout)
- **추가:** Gate (09:00~09:30 등락률≥1.5%, RVOL≥1.5), 상승률(25)+거래대금순위(25)+시장(15)+수급(15)+품질(10)+ADX(10), OPENING_STRONG, eligible_strategies

### C3 (c3_vi_explosion.py)
- **제거:** 매수호가 잔량 비중 점수, primary_strategy='CHARLIE_VI' 하드코딩
- **추가:** Gate (vi_triggered, pre_rvol≥3, 시총≥2000억, daily_vi_count≤3), RVOL(25)+발동전상승률(25)+시장(15)+뉴스(15)+품질(10)+VI특성(10), state_data에 호가 잔량 포함

### C4 (c4_intraday_surge.py, 신규)
- **제거:** VWAP 상향 돌파·RSI 구간·수급 판단 (기존 c4_vwap_recovery)
- **추가:** Gate (직전 10분 대비 상승≥2%, 해당 10분 거래량≥직전 30분 평균×2, 시총≥3000억), 급등속도(25)+RVOL(25)+시장(15)+수급(15)+품질(10)+ADX(10), INTRADAY_SURGE, state_data에 VWAP/RSI/수급 포함

### C5 (c5_pullback_discovery.py, 신규)
- **제거:** 피보나치 되돌림 비율·양봉 확인·반등 거래량 비교·시간 비율, primary_strategy='ECHO_ABCD'
- **추가:** Gate (day_high_gain≥5%, current_pullback≥1.5%, adx≥25, regime≠STRONG_TREND_DOWN, 조정 거래량 위축), 초기상승(25)+상승RVOL(25)+조정위축(15)+시장(15)+품질(10)+ADX(10), PULLBACK_READY, state_data에 day_high/day_low/surge 가격/고가시각 등

### C6 (c6_sector_lag.py)
- **제거:** 상관계수·펀더멘탈 유사성, primary_strategy='FOXTROT_SECTOR'
- **추가:** Gate (leader_gain≥4%, follower_change -1.5~1.5%, follower_volume_trend=INCREASING), 대장주상승(25)+후발주미반응(25)+거래량변화(15)+시장(15)+품질(10)+업종내위치(10), SECTOR_FOLLOW, state_data에 대장주코드·업종코드·후발주순위 등

### C7 (c7_oversold_rebound.py)
- **제거:** 볼린저밴드 하단 반등 확인·매수 전환 강도 타이밍, primary_strategy='GOLF_REVERSAL'
- **추가:** Gate (price_drop_from_high≥3%, RSI≤30, market_is_declining, 시총≥5000억), 하락률(25)+RSI깊이(25)+시장동반하락(15)+수급전환(15)+품질(10)+뉴스부재(10), OVERSOLD, state_data에 RSI/볼린저/수급/뉴스 포함

---

## 3. AST·임포트 테스트 결과

- **AST 구문 검증:** 8개 파일 전체 통과 (discovery_signal, c1~c7)
- **임포트 테스트:** DiscoverySignal, GapDiscovery, OpeningStrongDiscovery, VIExplosionDiscovery, IntradaySurgeDiscovery, PullbackDiscovery, SectorLagDiscovery, OversoldReboundDiscovery — 전체 성공

---

## 4. 점수 체계 비교 (v1.0 vs v2.0)

| 구분 | v1.0 | v2.0 |
|------|------|------|
| C1 | gap/volume/market_cap/time_bonus (비표준) | 갭(25)+RVOL(25)+시장(15)+뉴스(15)+품질(10)+ADX(10) |
| C2 | breakout_strength/volume_surge/range_tightness/trend_align | 상승률(25)+거래대금순위(25)+시장(15)+수급(15)+품질(10)+ADX(10) |
| C3 | (미구현) | RVOL(25)+발동전상승(25)+시장(15)+뉴스(15)+품질(10)+VI특성(10) |
| C4 | vwap_proximity/below_duration/volume/rsi_recovery | 급등속도(25)+RVOL(25)+시장(15)+수급(15)+품질(10)+ADX(10) |
| C5 | fib_accuracy/volume_pattern/trend_strength/rsi_level | 초기상승(25)+상승RVOL(25)+조정위축(15)+시장(15)+품질(10)+ADX(10) |
| C6 | (미구현) | 대장주상승(25)+후발주미반응(25)+거래량(15)+시장(15)+품질(10)+업종위치(10) |
| C7 | oversold/volume/rebound_candle | 하락률(25)+RSI깊이(25)+시장동반(15)+수급전환(15)+품질(10)+뉴스부재(10) |

공통: 합계 100점, pass_threshold 60점.

---

## 5. eligible_strategies 매트릭스

| discovery_type | eligible_strategies |
|----------------|---------------------|
| GAP_UP | ALPHA_GAP, BRAVO_ORB, DELTA_VWAP |
| OPENING_STRONG | BRAVO_ORB, ALPHA_GAP, DELTA_VWAP, ECHO_ABCD |
| VI_TRIGGERED | CHARLIE_VI, ALPHA_GAP, DELTA_VWAP |
| INTRADAY_SURGE | DELTA_VWAP, BRAVO_ORB, ECHO_ABCD, CHARLIE_VI |
| PULLBACK_READY | ECHO_ABCD, DELTA_VWAP, BRAVO_ORB, GOLF_REVERSAL |
| SECTOR_FOLLOW | FOXTROT_SECTOR, DELTA_VWAP, BRAVO_ORB |
| OVERSOLD | GOLF_REVERSAL, DELTA_VWAP, ECHO_ABCD |

---

## 6. 기획서 push 및 서비스 확인

- **기획서 3개 파일 push:** 완료 (DESK-ROLE-SEPARATION-FRAMEWORK.md, DESK2-DISCOVERY-STRATEGY-SPEC.md, DESK-ROLE-SEPARATION-ROADMAP.md)
- **원격 200 확인:** 3개 URL 모두 200
- **kis-v41-monitor / kis-v41-scheduler:** 재시작 없음 (절대 규칙 준수)
- **strategy_cards / v4_positions:** ALTER·DROP·DELETE 없음, 직접 수정 없음

---

## 7. 다음 단계

STAGE 2 커서 지시서 **DESK2-STRATEGY-REDESIGN-001** 투입: 전략 7개 파일 watchlist 기반 stalking, 발굴에서 분리된 판단 로직 이관, CS Score 독립 계산.
