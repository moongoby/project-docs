# DESK1 라이브 사전 체크리스트
> 날짜: 2026-02-23 (월요일 09:00 대비)
> 작업자: Cursor
> 서버: root@211.188.51.113 | 프로젝트: /root/kis-autotrade-v4 | 브랜치: phase-2c-command-center

## DESK1 전략카드 현황
| card_id | 이름 | 타입 | active | live |
|---------|------|------|--------|------|
| 5 | DESK1_스캘핑_class_b | BUILTIN | t | t |
| 38 | DESK1_초단타모멘텀 | BUILTIN | t | t |
| 39 | DESK1_갭메우기 | BUILTIN | t | t |
| 40 | DESK1_뉴스반응스캘핑 | BUILTIN | t | t |
| 41 | DESK1_S01_호가불균형 | BUILTIN | t | t |
| 42 | DESK1_S02_고래추적 | BUILTIN | t | t |
| 43 | DESK1_S03_스프레드갭 | BUILTIN | t | t |
| 44 | DESK1_S04_플래시크래시 | BUILTIN | t | t |
| 45 | DESK1_M03_이격도숏 | BUILTIN | t | t |
| 46 | DESK1_H01_시장센서 | BUILTIN | t | t |

- **DESK1 라이브 카드 수**: 10
- **DESK1 전체 카드 수**: 10 (10/10 라이브)

## 사전 체크리스트
- [x] strategy_cards = 62
- [x] v4_positions OPEN = 5 (ID: 49, 51, 53, 55, 61)
- [x] kis-v41-api active
- [x] kis-v41-monitor active
- [x] kis-v41-scheduler active
- [ ] 분봉 수집기 활성화 (CEO 승인 필요) — 현재 inactive
- [ ] 호가 수집기 활성화 (CEO 승인 필요) — 현재 inactive
- [ ] 분봉 데이터 최신 확인 (금요일 종가 15:30) — **최신: 2026-02-19 16:00** (월요일 장전 갱신 필요)
- [x] 스캘핑 유니버스 708종목 확인 (is_active=true 708건)
- [x] DESK1 카드 10/10 확인
- [x] 리스크 매니저 설정 확인 (max_positions, desk_limits 등)
- [x] API 헬스 정상 — `{"status":"ok","version":"4.1.0","orchestrator_state":"IDLE","database":"connected","redis":"connected"}` (8003)

## CEO 결정 필요
1. 분봉/호가 수집기 시작 시점 (08:50 권장)
2. DESK1 초기 투자금액 설정
3. DESK1 max_position 설정
4. DESK 간 중복 매수 정책

## DESK1 현재 포지션 (진단 시점)
| id | ticker | desk_id | status | entry_price | current_price |
|----|--------|---------|--------|-------------|---------------|
| 49 | 221800 | 1 | OPEN | 19070 | 24750.00 |
| 40, 41, 47, 50 | (기타) | 1 | CLOSED | — | — |

## 백테스트 결과 요약
- DESK1 카드(card_id IN 5,38~46)에 대한 **v4_backtest_trades 결과 0건** — DESK1 전용 백테스트 미실행 또는 테이블 미사용.

## 파이프라인/리스크/주문 실행기 진단 요약
- **v4_pipeline_orchestrator.py**: DESK1 전용 `run_desk1_cycle`, Desk1Commander, desk_id=1 스캘핑/class_b 로직 존재. stop_loss=-0.03, target=0.07, trailing=-0.02 (desk_id==1).
- **strategy_engine.py** (backend/app/services/strategy/): "scalping", "DESK1" 문자열 없음 — DESK1 전용 진입 로직은 파이프라인/Desk1Commander 쪽에 있음.
- **risk_manager.py** (execution): max_positions, desk_limits(desk_id), 최대 포지션 수 검사 존재.
- **order_executor.py**: KISApiInterface(kis_api), get_current_price, buy_market, sell_market, cancel_order 사용 — KIS API 연동 정상 구조.

## 리스크
- DESK1 미검증 상태 — 소액 테스트 권장
- 분봉 진입 DESK2 교훈: -23.25% → 검증 없이 풀 투입 금지

---
*DESK1-LIVE-PREP (P5) 읽기 전용 진단 완료. 코드/DB/서비스 변경 없음.*
