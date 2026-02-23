# DESK1-LIVE-PREP 보고서
- 날짜: 2026-02-23
- 작업자: Cursor
- 우선순위: P5 (월요일 09:00 전)

## 사전 확인
- strategy_cards: **62** (기대값 일치)
- v4_positions OPEN: **5** (기대값 일치)
- 서비스: **kis-v41-api active, kis-v41-monitor active, kis-v41-scheduler active** (전부 active)

## DESK1 전략카드 현황
- 전체: **10**/10
- 활성: **10**
- 라이브: **10**
- 카드 목록:

| card_id | strategy_name              | desk_id | is_active | is_live | risk_params (요약) | created_at |
|---------|----------------------------|---------|-----------|---------|--------------------|------------|
| 5       | DESK1_스캘핑_class_b       | 1       | t         | t       | max_single 50%, max_concurrent 2 | 2026-02-20 |
| 38      | DESK1_초단타모멘텀         | 1       | t         | t       | daily_loss -2%, single 30%, concurrent 3 | 2026-02-20 |
| 39      | DESK1_갭메우기             | 1       | t         | t       | daily_loss -2%, single 35%, concurrent 3 | 2026-02-20 |
| 40      | DESK1_뉴스반응스캘핑       | 1       | t         | t       | daily_loss -2%, single 40%, concurrent 2 | 2026-02-20 |
| 41      | DESK1_S01_호가불균형       | 1       | t         | t       | daily_loss -1.5%, single 30%, concurrent 3 | 2026-02-20 |
| 42      | DESK1_S02_고래추적         | 1       | t         | t       | daily_loss -2%, single 35%, concurrent 3 | 2026-02-20 |
| 43      | DESK1_S03_스프레드갭       | 1       | t         | t       | daily_loss -1.5%, single 40%, concurrent 2 | 2026-02-20 |
| 44      | DESK1_S04_플래시크래시     | 1       | t         | t       | daily_loss -2.5%, single 35%, concurrent 2 | 2026-02-20 |
| 45      | DESK1_M03_이격도숏         | 1       | t         | t       | daily_loss -2%, single 40%, concurrent 2 | 2026-02-20 |
| 46      | DESK1_H01_시장센서         | 1       | t         | t       | daily_loss -2%, single 33%, concurrent 3 | 2026-02-20 |

## 인프라 점검
| 항목 | 상태 | 비고 |
|------|------|------|
| 스캘핑 유니버스 | 708종목 | 최종 갱신: 2026-02-21 23:42:08 |
| 분봉 데이터 | 35,029,032행, 547종목 | 최신: 2026-02-19 16:00:00 (금요일 마감) |
| 호가 데이터 | 테이블 미존재 | v4_orderbook_snapshot 없음 |
| 분봉 수집기 | activating (auto-restart), exit-code 실패 | 월요일 장전 CEO 승인 후 start 필요 |
| 호가 수집기 | inactive (dead), disabled | 월요일 활성화 시: `sudo systemctl start kis-v41-orderbook-collector` (CEO 승인 후) |
| 파이프라인 DESK1 지원 | **확인** | v4_pipeline_orchestrator.py 내 run_desk1_cycle, desk_id=1, class B/stop/target/trail 설정 존재 |
| 리스크 매니저 DESK1 설정 | **확인** | risk: max_positions 체크 존재, execution: max_positions 기본 10 |

## 기존 백테스트 결과
- DESK1(desk_id='1') 카드에 대한 **v4_backtest_trades 결과 0건** (아직 DESK1 전용 백테스트 세션 미실행 또는 이관 전 데이터).

## 월요일 활성화 체크리스트
- [ ] 1. 분봉 수집기 시작: `sudo systemctl start kis-v41-minute-collector` (CEO 승인 후)
- [ ] 2. 호가 수집기 시작: `sudo systemctl start kis-v41-orderbook-collector` (CEO 승인 후)
- [ ] 3. 스캘핑 유니버스 갱신 확인 (현재 2026-02-21 갱신, 월요일 장전 재갱신 권장)
- [ ] 4. DESK1 카드 is_live 확인 (현재 10개 전부 is_live=true)
- [ ] 5. 파이프라인 DESK1 사이클 동작 확인 (스케줄러/모니터 로그)
- [ ] 6. 첫 시그널 모니터링 (09:10~09:30)

## CEO 결정 필요 사항
1. 분봉/호가 수집기 월요일 활성화 승인
2. DESK1 카드 10개 전부 라이브 투입 여부 (현재 전부 라이브 설정됨)
3. DESK1 자금 배분 비율 (현재: strategy_cards.allocated_amount는 카드별 상이, 파이프라인 desk_config allocation_pct 100 기준)
4. 스캘핑 최대 손실 한도 설정 확인 (카드별 risk_params daily_loss_limit_pct -1.5%~-2.5% 적용)

## 위험 요소
1. **분봉 수집기 실패** — 현재 exit-code로 재시작 반복 중. 월요일 장전 원인 조치 필요.
2. **호가 테이블 부재** — v4_orderbook_snapshot 미존재 시 호가 기반 전략(S01 등)은 실데이터 없이 동작할 수 있음.
3. **분봉 최신일 2026-02-19** — 주말 미수집으로 월요일 09:00 시점에는 전날 분봉 없음. 월요일 장 시작 후 수집기 정상화 필수.
4. **DESK1 백테스트 이력 없음** — 라이브 전 사전 백테스트 실행 권장.

## 영향
- DB: 없음 (조회만), 코드: 없음, 서비스: 없음

## 컴플라이언스
- [x] .env/.bak 커밋: 없음
- [x] strategy_cards: 62건 유지
- [x] v4_positions OPEN: 5건 유지
- [x] 서비스 재시작: 없음
- [x] 수집기 활성화: 없음 (CEO 승인 대기)
