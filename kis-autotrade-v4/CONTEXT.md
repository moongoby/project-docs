# KIS AutoTrade V4.1 프로젝트 컨텍스트 (Claude PM용)
> Public URL: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CONTEXT.md
> 최종 갱신: 2026-03-06 (T-136, HANDOVER.md v10.8 기준 전면 동기화 — 불일치 0건)

## 1. 프로젝트 개요
- KIS AutoTrade V4.1: 한국투자증권 API 기반 AI 자동매매 시스템
- DESK 1~5 멀티 전략 운영 (60개 전략카드, D1/D3/S2 폐기 예정 D-011)
- V4.1 코드베이스, 동일 서버/DB에서 타 서비스와 공유
- 도메인: trading41.newtalk.kr
- GitHub: moongoby/kis-autotrade-v4 (private), 문서: moongoby/project-docs (public)
- DB 현황: 288 테이블, 37.82 GB (2026-03-05 기준)
- v4_ohlcv_minute: 108,451,723 rows
- v4_fundamental_quarterly: 787행 + 200행(fallback) = 987행 (20종목 DESK5)
- v4_macro_daily: 730행
- v4_positions OPEN: ~14건

## 2. 서버 환경
- 서버: root@211.188.51.113 (kis-autotrade-v4)
- 프로젝트: /root/kis-autotrade-v4
- 브랜치: phase-2c-command-center
- DB: PostgreSQL 16, kisautotrade / kis_admin / localhost:5432
- Python 3.12, FastAPI, SQLAlchemy (asyncpg), Redis 7.x
- 가상환경: source /root/kis-autotrade-v4/venv/bin/activate
- PYTHONPATH: /root/kis-autotrade-v4/backend

## 3. CEO 절대 규칙
1. kis-v41-* 서비스 재시작 금지 (CEO 승인 시에만)
2. strategy_cards ALTER/DROP/DELETE 금지 (UPDATE는 CEO 승인)
3. v4_positions 직접 수정 금지
4. 핵심 파일 수정 → review/ 업로드 → CEO+Claude 승인 후 적용
5. .env/.bak 커밋 절대 금지
6. 사전확인: strategy_cards=60, v4_positions OPEN=14

## 4. DESK 구성
| DESK | 역할 | max_hold | 라이브/전체 | 풀 현황 | 수익률 | 상태 |
|------|------|----------|------------|--------|--------|------|
| DESK1 | 초단타/스캘핑 | 0-1일 | 10/10 | — | 미검증 | 인프라 구축 완료 |
| DESK2 | 단타 분봉 | 1-3일 | 10/16 | 후보~10종목 | -23.25% | 멀티컨디션 Phase A 완료 (T-125), Phase B 진행 예정 (T-128) |
| DESK3 | 단기스윙 | 3-10일 | 9/11 | ACTIVE 106종목 | +32.23% | 주 수익원 |
| DESK4 | 중기스윙 | 20-40일 | 6/9 | WATCHING 18종목 | 운영중 | 안정 |
| DESK5 | 장기 | 90-120일 | 1/10 | WATCHING 20종목 | — | 프랙탈 트리거 설계 완료 (T-127/T-130), 코어보유 D-014 반영, 펀더멘탈 수집 완료 |

## 5. 서비스 현황
| 서비스 | 포트 | 상태 |
|--------|------|------|
| kis-v41-api | 8003 | active (nginx) |
| kis-v41-monitor | — | active |
| kis-v41-scheduler | — | active |
| kis-v41-minute-collector | — | active (분봉 108.4M rows 수집 완료, 크론 30+ OK) |

## 6. DB 무결성 기준
- strategy_cards: 60건 (D1/D3/S2 폐기 예정 — D-011)
- v4_positions OPEN: 14건
- DB 크기: 37,820 MB (37.82 GB)
- 테이블 수: 288개 (T-106 기준, 2026-03-05)
- v4_ohlcv_minute: 108,451,723행
- v4_ohlcv_daily: 2,615,744행 (3년치)
- v4_scalping_universe: 1,354종목 (T-102에서 646→1,354 갱신)
- v4_fundamental_quarterly: 787행 (149종목 수집) + DESK5 fallback 200건
- v4_macro_daily: 730행
- v4_sector_mapping: 3,844종목 (062 마이그레이션)
- v4_desk5_watchlist: 20종목 / WATCHING
- v4_desk4_watchlist: 18종목 / WATCHING
- v4_desk3_pool: 106종목 / ACTIVE

## 7. 작업 큐 (CEO 지시 로드맵 Phase 2c 기준, 2026-03-06 T-136 현행화)
| 순위 | 작업 | Task | 상태 |
|------|------|------|------|
| ✅완료 | DESK2 멀티컨디션 Phase A | T-125 | 완료 (2026-03-05) |
| ✅완료 | DESK5 프랙탈 트리거 설계 | T-127 | 완료 — fractal_triggers.py 구현 |
| P0 | DESK2 멀티컨디션 Phase B | T-126/T-128 | Phase A 완료 후 진행 예정 |
| P0 | DESK5 프랙탈 BT/배포 | T-130 | T-127 설계 기반 BT Phase 1-2 완료, 배포 대기 |
| ✅완료 | D-009 P0 장중 변수 4건 | T-131 | 완료 — VP_RT/MA_REGIME/PB_3M/UL_EXT |
| P0 | D-009 P1 변수 구현 | T-132 | LEADER_FOLLOWER/CLOSE_BET/RSI_MACD/NEWS_CATALYST |
| P1 | CS×EQS 이중필터 배포 | T-133 | Layer 3.5/4.5 삽입 (OOS WF PASS 기완성) |
| ✅완료 | CONTEXT.md 전면 갱신 | T-134 | 완료 (2026-03-06, 14개 항목 정정) |
| P1 | 반등확인 게이트 5전략 배포 | — | OOS Walk-Forward PASS, 2/3 충족 기본버전 |
| P2 | CONTEXT.md 동기화 | T-136 | **현재 작업** (2026-03-06, 불일치 0건 목표) |
| P3 | D-009 P2 변수 구현 | — | NEW_STOCK_REALTIME_DETECTOR/ORDERBOOK_IMBALANCE/CK480 |
| 보류 | DESK5/4/3 일봉 추세추종 | — | 60일 페이퍼 데이터 축적 후 재개 |
| 보류 | Phase 3 청산최적화 | — | Phase 2 완료 후 |

## 8. CEO 결정 대기
1. v4_news_feed 테이블 수집 방법 및 일정 결정
2. DESK3 AXIS2 분류 97.6% NONE → 근본 해결 방향 (데이터 부족)
3. CS×EQS 이중필터 배포 최종 승인
4. 반등확인 게이트 5전략 배포 승인 (OOS Walk-Forward PASS)
5. DESK5/4/3 보류 해제 조건 판단 (60일 페이퍼 데이터 축적 후)
6. D-009 P2 변수 구현 우선순위 확정

## 9. 핵심 파일 (수정 시 검수 필수)
- v4_pipeline_orchestrator.py, strategy_engine.py, risk_manager.py
- order_executor.py, position_manager.py, split_transfer_engine.py
- lifecycle.py, fund/*, adaptive/*, regime_detector.py
- backtest_engine_v2.py, collector_minute.py, main.py
- cte_pipeline.py, supply_demand_gate.py, funnel_score_engine.py
- feature_engine.py, confirmation_entry_engine.py, hypothesis_tester.py

## 10. 문서 체계
- Cursor Rules: .cursor/rules/kis-v41-rules.md (서버)
- Public Rules: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/kis-v41-rules.md
- 보고서: report/v41/{작업ID}-{YYYYMMDD}.md → sync_reports.sh
- 검수: review/ → push_review.sh → CEO+Claude 승인 → clean_review.sh

## 11. AI 세션 시작 시 필수 읽기
1. https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CONTEXT.md (이 파일)
2. https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/kis-v41-rules.md
3. https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/CLAUDE.md
4. https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md (v10.8 이상)

## 12. 지시서 작성규칙

```
<!-- DIRECTIVE_START -->
Task ID: T-NNN
제목: (한글 제목)
서버: 211 (kis-autotrade-v4)
우선순위: P0-CRITICAL / P1-HIGH / P2-NORMAL
예상 시간: N분
예상 비용: $0
의존성: (없음 또는 선행 Task ID)

(작업 내용 상세 기술)
<!-- DIRECTIVE_END -->
```

- 타임스탬프: KST 기준 (UTC 금지)
- 작업 완료 후 HANDOVER.md 반드시 갱신
- git commit + push 필수
- RESULT.md는 /root/.genspark/directives/done/ 에 저장 (YAML 프런트매터 포함)
- 보고서는 /root/kis-autotrade-v4/report/v41/{ID}-{DATE}.md 작성 후 project-docs sync 필수

## 13. 문서 간 정합성 점검 (T-136, 2026-03-06)

### CONTEXT.md vs HANDOVER.md 불일치 (T-134 갱신 후 → T-136 갱신 후)
| 항목 | T-134 후 CONTEXT.md | HANDOVER.md v10.8 (기준) | 갱신 여부 |
|------|---------------------|--------------------------|-----------|
| strategy_cards | 60건 ✅ | 60건 (D1/D3/S2 폐기) | ✅ 일치 |
| v4_positions OPEN | ~14건 ✅ | 14건 | ✅ 일치 |
| DB 크기 | 37.82 GB ✅ | 37.82 GB | ✅ 일치 |
| 테이블 수 | 288개 ✅ | 288개 | ✅ 일치 |
| v4_ohlcv_minute | 108,451,723행 ✅ | 108,451,723행 | ✅ 일치 |
| v4_fundamental_quarterly | 787+200행 ✅ | 787+200행 | ✅ 일치 |
| v4_macro_daily | 730행 ✅ | 730행 | ✅ 일치 |
| v4_sector_mapping | 3,844종목 ✅ | 3,844종목 | ✅ 일치 |
| DESK2 상태 | Phase A 완료만 기재 | Phase B (T-128) 진행 예정 | ✅ 갱신 (T-136) |
| DESK5 상태 | 펀더멘탈만 기재 | 프랙탈(T-127/T-130)+D-014 | ✅ 갱신 (T-136) |
| 작업 큐 | T-126/T-132/T-133/T-134 | T-125~T-136 현행 | ✅ 갱신 (T-136) |
| T-131 D-009 P0 완료 | 미기재 | VP_RT/MA_REGIME/PB_3M/UL_EXT 완료 | ✅ 갱신 (T-136) |

### 잔존 불일치 사항 (T-136 기준 = 0건)
| 항목 | 비고 |
|------|------|
| DESK2 수익률 -23.25% | 페이퍼 트레이딩 진행 중 — 확정치 아님, 모니터링 대기 |
| DESK3 수익률 +32.23% | 실 거래 기준 미검증 — 정기 점검 시 갱신 예정 |
| CEO-DIRECTIVES.md | D-012/D-013/D-014 반영 완료 (프랙탈 구현 D-013/D-014, HANDOVER v10.8 반영) |
