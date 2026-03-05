# KIS AutoTrade V4.1 프로젝트 컨텍스트 (Claude PM용)
> Public URL: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CONTEXT.md
> 최종 갱신: 2026-03-05 (T-106 기준값 현행화)

## 1. 프로젝트 개요
- KIS AutoTrade V4.1: 한국투자증권 API 기반 AI 자동매매 시스템
- DESK 1~5 멀티 전략 운영 (60개 전략카드)
- V4.1 코드베이스, 동일 서버/DB에서 타 서비스와 공유
- 도메인: trading41.newtalk.kr
- GitHub: moongoby/kis-autotrade-v4 (private), 문서: moongoby/project-docs (public)

## 2. 서버 환경
- 서버: root@[SERVER-IP] (kis-autotrade-v4)
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
6. 사전확인: strategy_cards=60, v4_positions OPEN=0 (2026-03-05 실측; 이전 14건)

## 4. DESK 구성
| DESK | 역할 | max_hold | 라이브/전체 | 수익률 | 상태 |
|------|------|----------|------------|--------|------|
| DESK1 | 초단타/스캘핑 | 0-1일 | 10/10 | 미검증 | 인프라 구축 완료 |
| DESK2 | 단타 | 1-3일 | 10/16 | -23.25% | 분봉 진입 최적화 필요 |
| DESK3 | 단기스윙 | 3-10일 | 9/11 | +32.23% | 주 수익원 |
| DESK4 | 중기스윙 | 20-40일 | 6/9 | 운영중 | 안정 |
| DESK5 | 장기 | 90-120일 | 1/10 | — | 카드 부족 |

## 5. 서비스 현황
| 서비스 | 포트 | 상태 |
|--------|------|------|
| kis-v41-api | 8003 | active (nginx) |
| kis-v41-monitor | — | active |
| kis-v41-scheduler | — | active |
| kis-v41-minute-collector | — | inactive (월요일 장전) |

## 6. DB 무결성 기준 (2026-03-05 T-106 실측값)
- strategy_cards: 60건
- v4_positions OPEN: 0건 (2026-03-05 실측; T-100 이전 14건)
- DB 크기: 37.82 GB (이전 15.7 GB; T-099/T-105 신규 테이블 추가 후 증가)
- DB 테이블 수(public schema): 288개
- v4_ohlcv_minute: 108,451,723행 (이전 19,468,781행; 분봉 대량 수집 결과)
- v4_fundamental_quarterly: 787행 (신규; T-105 펀더멘털 수집 결과)
- v4_macro_daily: 730행 (신규; T-099 매크로 수집 결과)
- v4_scalping_universe: 708종목
- 일봉 테이블: ohlcv_daily (구칭 v4_ohlcv_daily 사용 금지)
- DESK 풀 테이블: v4_desk5_watchlist / v4_desk4_watchlist / v4_desk3_pool (개별 테이블; 구칭 v4_desk_pool 사용 금지)
- DESK3 풀 현황: 206/ACTIVE (폭락장 풀 팽창; 이전 106/ACTIVE)

## 7. 작업 큐 (2026-03-05 현행화)
| 순위 | 작업 | 상태 |
|------|------|------|
| P0 | T-106 CONTEXT 기준값 현행화 | 완료 (2026-03-05) |
| P1 | DESK2-MINUTE-REBT | 대기 |
| P2 | DESK5-CARD-BT | P1 후 |
| P3 | OVERLAP-GUARD | CEO 정책 대기 |
| P4 | REGIME-FILTER | CEO 승인 대기 |
| P5 | DESK1-LIVE-PREP | 보류 |

## 8. CEO 결정 대기
1. DESK 간 중복 매수 정책
2. 레짐 기반 DESK2 진입 제한
3. 48h 레짐 전환 방어 모드
4. strategy_cards 61, 62 처리
5. index_daily OHLC=0 재수집

## 9. 핵심 파일 (수정 시 검수 필수)
- v4_pipeline_orchestrator.py, strategy_engine.py, risk_manager.py
- order_executor.py, position_manager.py, split_transfer_engine.py
- lifecycle.py, fund/*, adaptive/*, regime_detector.py
- backtest_engine_v2.py, collector_minute.py, main.py

## 10. 문서 체계
- Cursor Rules: .cursor/rules/kis-v41-rules.md (서버)
- Public Rules: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/kis-v41-rules.md
- 보고서: report/v41/{작업ID}-{YYYYMMDD}.md → sync_reports.sh
- 검수: review/ → push_review.sh → CEO+Claude 승인 → clean_review.sh

## 11. AI 세션 시작 시 필수 읽기
1. https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CONTEXT.md (이 파일)
2. https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/kis-v41-rules.md
3. https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/CLAUDE.md
