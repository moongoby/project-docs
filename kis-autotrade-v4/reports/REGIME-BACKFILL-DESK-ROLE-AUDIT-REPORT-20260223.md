# REGIME-BACKFILL + DESK-ROLE-AUDIT 결과

**작업명:** REGIME-BACKFILL + DESK-ROLE-AUDIT (레짐 히스토리 백필 + DESK별 역할 충분성 점검)  
**서버:** 211.188.51.113  
**경로:** /root/kis-autotrade-v4  
**작성일:** 2026-02-23  
**규칙 준수:** 백업 수행, 기존 파일 수정 없음, INSERT만 사용, strategy_cards UPDATE 없음

---

## 사전 확인 (작업 전)

| 항목 | 결과 |
|------|------|
| strategy_cards COUNT | 62 |
| v4_positions OPEN | 5 |
| kis-v41-api / kis-v41-monitor | active (running) |
| df -h / | 52% 사용, 46G 가용 |

---

## [PART A: 레짐 백필]

| 항목 | 내용 |
|------|------|
| 백필 전 건수 | 2 |
| 백필 후 건수 | 59 |
| 레짐별 분포 | SIDEWAYS 21, STRONG_TREND_DOWN 20, MILD_TREND_DOWN 16, MILD_TREND_UP 2 |
| 백필 범위 | 2025-11-20 ~ 2026-02-13 |

**조치 요약**
- 백업: `sudo -u postgres pg_dump -d kisautotrade -t v4_market_regime_daily > /root/backups/bt_engine_upgrade_20260223/v4_market_regime_daily.sql`
- 신규 스크립트: `scripts/backfill_regime_history.py` (regime_detector 로직을 날짜별 as_of 기준으로 재현, INSERT만, ON CONFLICT (date) DO NOTHING)
- 실행: `--from 20251120` 기준 59거래일 처리, 57건 신규 삽입(기존 2건은 DO NOTHING으로 유지)

---

## [PART B: DESK별 역할 충분성]

| DESK | 종목발굴 | 시간축적합성 | 전략다양성 | 수익구조 | Promotion연계 | 종합 |
|------|----------|-------------|-----------|---------|-------------|------|
| DESK1 | 유니버스 708종목, 10카드 라이브, commander_scan·호가불균형·고래추적 등 | max_hold 0~1일, time_window 09:01~15:20 — 스캘핑에 부합 | 10종 시그널 조합(갭메우기·뉴스반응·플래시크래시 등) | 백테스트 세션 57/61에 DESK1 매매 없음 — 실적 검증 필요 | split_transfer_engine에 DESK1→2 promotion_target 정의 있음 | **미흡** (실거래/백테스트 커버리지 부족) |
| DESK2 | Commander CLASS-A/V/C, 10카드 라이브, 종가·레인지돌파·3분봉눌림 등 | max_hold 1~3일, time_window·장초/종가 구간 명시 — 데이트레이딩 부합 | 10카드, 일봉/분봉 혼재 | 일봉(7,22,27) 양호·분봉 부진 — 기존 리포트와 일치 | 2→3 promotion_target·criteria 정의 | **충분** |
| DESK3 | Commander CLASS-D/K, 9카드 라이브, 눌림반등·박스돌파·MACD·지지저항 등 | max_hold 10일, 3~10일 단기스윙에 부합 | 9카드, 일봉 기술지표 다양 | 핵심 수익원(40~68%) — daily_alpha 4~7일 구간과 정합 | run_desk3_cycle·_desk3_receive_transfers·phase2 매수 | **충분** |
| DESK4 | 6카드 라이브, 중기스윙·피보·엘리어트·일목·Parabolic·켈트너 | max_hold 20~40일, 2~8주 역할 부합 | 6카드, 추세·채널·파동 다양 | 세션 61 기준 172종목 344건 — 역할 수행 | 4→5 promotion_target 정의 | **충분** |
| DESK5 | 10카드 중 is_live=1(모멘텀팩터), 나머지 9은 비라이브 | max_hold 90~120일, 장기 역할 부합 | 전략 다양(가치·성장·배당·계절·테마·섹터·퀄리티·저변동·모멘텀) | 라이브 1개만 — 장기 엔진 활용도 낮음 | promotion_target 없음(최상위) | **부족** (라이브 1개, 장기 역할 미활용) |

**DESK 간 종목 중복**
- 세션 57: 동일일·동일종목이 DESK2–DESK3, DESK2–DESK4 등 복수 DESK에서 BUY 발생(예: 010140, 009520). Promotion/다중 전략 진입으로 해석 가능.

**DESK별 커버리지(세션 61)**
- DESK2 269종목 960건, DESK3 263종목 710건, DESK4 172종목 344건, DESK5 38종목 48건. (세션 61에 DESK1 BUY 없음.)

---

## [PART C: DESK별 개선 방향]

- **DESK1**  
  - 스캘핑 유니버스(708종목, 평균 거래대금 42.4B, ATR 6.49%)는 확보됨.  
  - exit_rules: max_hold_days 0~1일 적절하나, stop_loss/take_profit/trailing_stop 비어 있는 카드 다수 → 스캘핑용 손절/익절/타임아웃 명시 권장.  
  - 백테스트·라이브에서 DESK1 매매가 수행되도록 세션/파이프라인 포함 여부 점검 및 Commander 스캔 → 카드 시그널 연동 검증.  
  - Promotion: DESK1→2 연계는 엔진에 정의되어 있음. 실제 인계 발생 여부·조건 모니터링.

- **DESK2**  
  - 종목 발굴·시간축·전략 다양성·Promotion 연계 양호.  
  - 분봉 카드 수익 부진: 진입 시간대 필터·유동성 필터·분봉 전용 조건(time_window, volume_surge 등) 강화 검토.  
  - 일봉 카드(7,22,27) 유지·모니터링.

- **DESK3**  
  - 핵심 수익원으로 역할 충분.  
  - 보유 기간 4~7일이 최적 구간과 일치하는지 지속 모니터링.  
  - 전략 간 중복 최소화·시장 레짐별 성과 분석(백필된 v4_market_regime_daily 활용).

- **DESK4**  
  - 중기 시간축·전략 구성 적절.  
  - 레짐별·섹터별 성과 분석으로 카드 가중/축소 검토.

- **DESK5**  
  - is_live=1인 카드가 1개(모멘텀팩터)뿐이라 장기 DESK 역할이 제한적.  
  - 가치·성장·배당·계절성 등 비라이브 카드의 백테스트·리스크 검토 후 단계적 라이브 전환 여부 검토.  
  - 장기 포지션 모니터링·리밸런싱 주기와 max_hold 90~120일 정합성 점검.

---

## 최종 확인

| 항목 | 값 |
|------|-----|
| strategy_cards COUNT | 62 |
| v4_positions OPEN | 5 |

--- 보고 끝 ---
