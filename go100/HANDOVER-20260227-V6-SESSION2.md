# GO100 인수인계서 v6.0 — Session 2 Complete Handover
> 작성: Claude Opus 4.6 | 날짜: 2026-02-27 | 대상: 다음 세션 AI

---

## ⚠️ 필수 규칙 — 반드시 먼저 읽고 준수

### 작업 규칙
1. 작업 시작 전 반드시 서비스 경계 확인: V4.1인지 GO100인지
2. 커밋 메시지 prefix 필수: [V4.1], [GO100], [SHARED]
3. GO100 작업 시 V4.1 파일 절대 수정 금지, 역도 동일
4. 공유 인프라(.env, main.py, nginx 등) 수정 시 양쪽 영향 명시
5. 대표님(user_id=2, [CEO-EMAIL-GM])이 CEO — 보고체 사용
6. 백억이 = GO100 AI 에이전트의 이름
7. 문서 레포(project-docs)와 코드 레포(kis-autotrade-v4)는 별도 관리

### Cursor 필수 규칙
1. 반드시 /root/kis-autotrade-v4/.cursorrules 파일을 읽고 시작
2. 반드시 /root/kis-autotrade-v4/CLAUDE.md 파일을 읽고 시작
3. 각 디렉토리의 SERVICE_BOUNDARY.md 확인
4. 파일 수정 전 백업: cp file.py file.py.bak.{작업명}
5. DB 스키마 변경 시 IF NOT EXISTS 필수
6. .env 수정 시 기존 값 주석 보존
7. 크론 등록 시 기존 crontab 백업 먼저
8. 작업 완료 후 반드시 보고서를 /root/project-docs/go100/reports/에 저장하고 git push

---

## 1. 프로젝트 개요

### GO100 (백억이)
- 목표: 증권사급 AI 투자 에이전트 (조건검색 + 자동매매 + 자율 전략 진화)
- 서버: Ubuntu 24.04, Xeon Gold 5220, 15GB RAM, 99GB SSD
- 스택: FastAPI(8002) + Next.js(3000) + PostgreSQL(16) + Redis + Nginx
- 도메인: go100.newtalk.kr
- 코드: /root/kis-autotrade-v4 (로컬 git, GitHub private 미등록)
- 문서: /root/project-docs → github.com/moongoby/project-docs (public)

### KIS AutoTrade V4.1
- 기존 자동매매 시스템, GO100과 같은 모노리포에 공존
- V4.1 라우터: /api/v4/*, GO100 라우터: /api/go100/*
- 서비스 경계: .cursorrules에 명시

---

## 2. 현재 상태 (2026-02-27 기준)

### 완료된 작업 (Session 1 + Session 2)

#### Day 1-3 (02-22 ~ 02-25): 기초 인프라
- Phase 1-10 완료: LLM 라우팅, 17 인텐트, Goal Engine, Adaptive Regime, Reporter, Paper-trading, E2E 검증, 라이브 트레이드 통합, 대시보드, 베타 모니터링
- 전략 카드 3개 생성 (스캘핑, 데일리, 단기스윙)
- HANDOVER v1~v5 문서화

#### Day 4 (02-26): 데이터 파이프라인 최적화
- V4.1 데이터 수집 지연 해소: 19:30 → 17:30 (2시간 단축)
- pykrx 데이터 확정 시점(15:35) 직후 수집 개시
- lib_collect.sh 공통 라이브러리 생성 (wait, retry, timing 유틸)
- 크론 45개 재설계, 36개 스크립트 교차검증

#### Day 4 (02-26~27): Agentic Architecture (v2.0 핵심)
- **Phase 2 Agent Core**: 21개 도구 (market 3, stock 4, sector 3, portfolio 3, strategy 3, regime 2, trade 2, report 1)
- **3-Layer Dispatcher**: Layer 0 Gemini 분류, Layer 1 단순/데이터, Layer 2 Claude 분석
- **데이터 무결성 모니터**: data_integrity_checker.py, 장중 2분/장외 15분 주기
- **자율 복구 엔진**: data_auto_healer.py, 감지→진단→내부복구→외부API→검증→보고
  - 복구 우선순위: DB내부 → pykrx → FinanceDataReader → KIS API → 수동
  - 테이블별: ohlcv_daily, index_daily, v4_vkospi_daily, v4_investor_daily, v4_market_regime_daily, go100_global_market, WS 재시작
- **텔레그램 알림**: @go100_auto_trading_bot, 1분 주기 발송, 08:30/17:30 일일 요약
  - BOT_TOKEN: 8327167593:AAGln8wlk4XQDLeeqVCo_DESVPcGmbNYXPk
  - .env에 GO100_TELEGRAM_BOT_TOKEN, GO100_TELEGRAM_CHAT_ID 설정 완료
- **레짐 갭 수정**: 02-24~26 누락분 자동 생성 (MA20+VKOSPI 기반)
- **서비스 경계**: .cursorrules, CLAUDE.md, SERVICE_BOUNDARY.md 3곳 배치

#### Day 4 (02-27): 진행 중 — 병렬 5작업 투입

##### Cursor 1: Redis 세션 메모리 (계층 1)
- 파일: backend/app/services/go100/memory/session_memory.py
- 기능: 대화 이력(20턴), 종목 스택(10개), 데이터 캐시, 의도 트래킹, 미완료 작업
- Redis key: go100:session:{session_id}:{field}
- TTL: 장중 2시간, 장외 30분
- build_context_prompt()로 LLM 프롬프트 주입용 컨텍스트 합성
- 상태: 지시서 전달 완료, 구현 대기/진행 중

##### Cursor 2: 에피소드 기억 DB (계층 2)
- 테이블: go100_episodic_memory (세션 종료 시 LLM 요약 저장)
- 테이블: go100_user_profile (장기 기억, 스키마만 선 생성)
- 파일: backend/app/services/go100/memory/episodic_memory.py
- 기능: 세션 요약 저장, 종목별 에피소드 조회, 에피소드 컨텍스트 프롬프트 생성
- 상태: 지시서 전달 완료, 구현 대기/진행 중

##### Cursor 3: Agent Core 메모리 통합
- 파일: backend/app/services/go100/memory/coreference_resolver.py (대명사 해석)
- 파일: backend/app/services/go100/ai/agent_memory_wrapper.py (메모리 래퍼)
- 기능: 대명사→종목 해석, 메모리 컨텍스트 주입, 세션 종료 시 에피소드 자동 저장
- ai_router.py 패치: run_agent → run_agent_with_memory 교체
- 의존성: Cursor 1, 2 완료 후 통합 (coreference_resolver.py는 독립 착수 가능)
- 상태: 지시서 전달 완료, 구현 대기/진행 중

##### Cursor 4: 조건검색 엔진 검토·최적화
- 클로드(별도 세션)가 1차 구축 중인 조건검색 엔진 완료 후 검토
- 체크리스트: 스키마, 지표 정합성, 성능(전종목 5분/쿼리 2초), Agent 연동, 캔들패턴, 순위필터
- 상태: 클로드 1차 완료 대기 중

##### Cursor 5: 재무 데이터 수집 복구
- 테이블: go100_fundamentals (PER/PBR/EPS/BPS/배당/ROE/ROA/부채비율/시총)
- 소스: pykrx get_market_fundamental (일별) + OpenDartReader (분기 재무비율)
- 파일: backend/app/services/go100/collectors/collect_fundamentals.py
- 크론: 16:05 Mon-Fri
- 백필: 최근 7일분 초기 실행
- 상태: 지시서 전달 완료, 구현 대기/진행 중

---

## 3. 알려진 이슈 (3건)

| # | 이슈 | 심각도 | 상태 |
|---|------|--------|------|
| 1 | collect_financials.py KIS API 403 (AppKey 무효) | HIGH | Cursor 5에서 대체 소스로 우회 중 |
| 2 | v4_market_regime_daily 02-23 이후 정체 | MED | 레짐 갭 수동 복구 완료, regime_detector 점검 필요 |
| 3 | ohlcv_daily 크론 로그 비어있음 (16:00 이동 후) | LOW | 다음 장일 16:00 실행 후 확인 |

---

## 4. DB 핵심 테이블 현황

### GO100 전용 테이블
| 테이블 | rows | 용도 |
|--------|------|------|
| go100_strategy_cards | 3 | 전략 카드 (스캘핑/데일리/스윙) |
| go100_backtest_runs | 0 | 백테스트 이력 |
| go100_data_integrity_log | ~수백 | 무결성 체크 로그 |
| go100_alerts | ~수십 | 텔레그램 알림 큐 |
| go100_episodic_memory | 신규 | 세션 에피소드 기억 (Cursor 2) |
| go100_user_profile | 신규 | 사용자 장기 프로필 (Cursor 2) |
| go100_fundamentals | 신규 | 재무 데이터 (Cursor 5) |
| go100_technical_indicators | 신규 | 기술적 지표 (클로드 조건검색) |

### V4.1 공유 테이블 (읽기만, 수정 금지)
| 테이블 | 용도 |
|--------|------|
| ohlcv_daily | 전종목 일봉 OHLCV |
| v4_ohlcv_minute | 분봉 데이터 |
| v4_tick_data | 틱 데이터 (40종목) |
| v4_orderbook_realtime | 10호가 호가창 |
| v4_investor_daily | 투자자별 매매동향 |
| v4_vkospi_daily | VKOSPI |
| v4_market_regime_daily | 시장 레짐 |
| index_daily | KOSPI/KOSDAQ/KOSPI200 지수 |
| stock_universe | 종목 기본정보 |

### 사용자 매핑
| legacy users.id | v4_users.user_id | email | 비고 |
|-----------------|-------------------|-------|------|
| 6 | 2 | [CEO-EMAIL-GM] | 대표님 (CEO) |
| 15 | 3 | [CEO-EMAIL-NV] | 오병용 |

---

## 5. 파일 구조 (GO100 핵심)

```
/root/kis-autotrade-v4/
├── .cursorrules          ← 서비스 경계 규칙 (필독!)
├── CLAUDE.md             ← Claude Code용 동일 규칙
├── .env                  ← 환경변수 (GO100_AGENT_MODE, TELEGRAM 등)
├── backend/app/
│   ├── routers/go100/
│   │   ├── ai_router.py   ← GO100 채팅 엔드포인트 (AGENT_MODE 분기)
│   │   └── SERVICE_BOUNDARY.md
│   └── services/go100/
│       ├── ai/
│       │   ├── agent_core.py           ← Agent Core (21도구, run_agent)
│       │   ├── agent_memory_wrapper.py ← 메모리 래퍼 (Cursor 3, 신규)
│       │   ├── llm_router.py           ← LLM 라우팅 (Gemini/Claude)
│       │   └── tool_executors.py       ← 도구 실행기
│       ├── memory/                     ← 세션 메모리 (Cursor 1,2,3, 신규)
│       │   ├── __init__.py
│       │   ├── session_memory.py       ← Redis 단기 기억
│       │   ├── episodic_memory.py      ← PostgreSQL 에피소드 기억
│       │   └── coreference_resolver.py  ← 대명사 해석
│       ├── monitoring/
│       │   ├── data_integrity_checker.py ← 무결성 체커
│       │   ├── data_auto_healer.py       ← 자율 복구
│       │   └── alert_sender.py           ← 텔레그램 발송
│       ├── collectors/
│       │   └── collect_fundamentals.py  ← 재무 수집 (Cursor 5, 신규)
│       └── SERVICE_BOUNDARY.md
├── scripts/go100/
│   ├── lib_collect.sh           ← 공통 유틸 (wait, retry, timing)
│   ├── run_data_integrity_check.sh
│   ├── run_auto_heal.sh
│   ├── run_alert_sender.sh
│   ├── run_daily_summary.sh
│   ├── run_collect_fundamentals.sh ← 재무 수집 크론 (Cursor 5, 신규)
│   └── SERVICE_BOUNDARY.md
└── venv/                    ← Python 3.12 가상환경
```

```
/root/project-docs/           ← 문서 레포 (GitHub public)
├── go100/
│   ├── ARCHITECTURE.md
│   ├── DB_SCHEMA.md
│   ├── GO100-HANDOVER-V3-PLANNING-20260226.md
│   ├── HANDOVER-20260227-V6-SESSION2.md  ← 이 문서
│   └── reports/
│       ├── CUR-GO100-PARALLEL-4-TASKS-20260227.md
│       ├── CUR-GO100-AUTO-HEALER-20260227.md
│       ├── CUR-CRON-REALTIME-OPTIMIZATION-20260227.md
│       └── (기타 보고서들)
└── common/
    ├── CONTEXT_TEMPLATE.md
    └── GIT_CONVENTION.md
```

---

## 6. 크론 현황 (45개)

주요 GO100 크론:
| 시간 | 스크립트 | 용도 |
|------|---------|------|
| */2 9-15 * * 1-5 | run_data_integrity_check.sh | 장중 무결성 체크 2분 |
| */15 0-8,16-23 * * * | run_data_integrity_check.sh | 장외 무결성 체크 15분 |
| * * * * 1-5 | run_alert_sender.sh | 텔레그램 발송 1분 |
| 30 8,30 17 * * 1-5 | run_daily_summary.sh | 일일 요약 |
| 20 16 * * 1-5 | run_auto_heal.sh | 국내 데이터 복구 |
| 10 7 * * 1-5 | run_auto_heal.sh | 해외 데이터 복구 |
| 5 16 * * 1-5 | run_collect_fundamentals.sh | 재무 수집 (신규) |

주요 V4.1 크론:
| 시간 | 용도 |
|------|------|
| 45 15 | index_daily 수집 |
| 50 15 | VKOSPI 수집 |
| 55 15 | VKOSPI regime sync |
| 0 16 | ohlcv_daily 수집 |
| 15 16 | market_investor 수집 |
| 25 16 | stock_universe 수집 |

---

## 7. 로드맵 & 진행률

### 전체 진행률: ~18% (천재 100% 기준)

| 단계 | 기간 | 핵심 작업 | 상태 |
|------|------|----------|------|
| P0 | 02-27 | Agent Mode 활성화, 크론 검증, 무결성 모니터 | ✅ 완료 |
| P1 | 02-28~03-01 | 세션 메모리, freshness 경고, 대시보드 | 🔧 진행중 (Cursor 1,2,3) |
| P2 | 03-02~03-08 | 경험 DB, 시그널 성과 추적, 모닝 브리핑 자동화 | 예정 |
| P3 | 03-09~03-22 | 전략 진화 엔진, 호가창 백테스트, 이벤트 엔진 | 예정 |
| P4 | 03-23~04-19 | 갭 캘리브레이터, 30일 모의투자 | 예정 |
| P5 | 04-20~06-14 | 자기리뷰, 포트폴리오 최적화, 개인화, 실투자 | 예정 |

### 천재까지 거리
- 0~18%: ✅ 인프라 (데이터, 도구, 알림, 복구)
- 18~20%: 🔧 조건검색 엔진 (클로드 1차 구축 중)
- 20~40%: 세션 메모리 + 경험 DB (Cursor 1,2,3 진행 중)
- 40~60%: 전략 진화 + 가설 기반 스크리닝
- 60~80%: 갭 캘리브레이터 + 30일 모의투자
- 80~95%: 자기리뷰 + 포트폴리오 최적화
- 95~100%: 실전 경험 축적 (수개월)

---

## 8. 조건검색 엔진 설계 (핵심 신규 기능)

### 아키텍처
Layer 0 데이터(PostgreSQL) → Layer 1 지표계산(pandas-ta/TA-Lib) → Layer 2 조건엔진(JSON→SQL) → Layer 3 LLM 에이전트

### 증권사 대비 GO100 차별화 6가지
1. 자연어 조건검색 ("외국인 3일 연속 순매수 + RSI 30 이하 대형주")
2. 크로스마켓 + 레짐 필터 (해외시장, VKOSPI, 시장 레짐)
3. 호가창(오더북) 기반 필터 (매수벽/매도벽, 스프레드)
4. 가설 기반 동적 스크리닝 (LLM이 시장 분석 → 조건 자동 생성)
5. 시간축 순차 패턴 매칭 (3일 전 골든크로스 → 2일 전 거래량 폭증 → ...)
6. 전략 카드 자동 연결 (검색 → 전략 → 백테스트 → 모의투자)

### 활용 데이터 조합 패턴 12가지
1. 수급 반전 포착 (외국인 10일 매도 후 순매수 전환 + RSI<35)
2. 변동성 압축 후 폭발 (BB 폭 60일 최저 + 거래량 200%)
3. 섹터 로테이션 선행 (해외 ETF 급등 + 국내 미반응 종목)
4. 레짐 전환 수혜 (BEAR→SIDEWAYS + VKOSPI 하락 + 외국인 전환)
5. 골든크로스 + 수급 확인 (5/20일선 돌파 + 기관 3일 순매수)
6. 낙폭과대 반등 (20일 -15% + RSI<25 + 양봉 + 거래량 200%)
7. 신고가 돌파 모멘텀 (52주 신고가 + 거래량 300% + 외국인)
8. 호가창 매수벽 (매수벽 5배 + 현재가 -3%)
9. 글로벌 이벤트 연동 (환율 급등 + 수출주 + PER<10)
10. VKOSPI 극단값 역발상 (VKOSPI>35 + KOSPI -2% + 낙폭과대)
11. 분봉 급등 초기 (3분봉 거래량 500% + 등락률 +1%)
12. 어닝 서프라이즈 후 지속 (EPS 서프라이즈 + 외국인 3일 순매수)

---

## 9. 세션 메모리 설계 (상세)

### 3계층 구조
| 계층 | 저장소 | TTL | 용도 |
|------|--------|-----|------|
| 1. Working Memory | Redis | 2h/30min | 세션 내 맥락 (종목 스택, 의도, 캐시) |
| 2. Episodic Memory | PostgreSQL | 영구 | 세션 요약 (LLM 자동 생성) |
| 3. User Profile | PostgreSQL | 영구 | 투자 성향, 선호 (주간 분석) |

### 대명사 해석
"그 종목", "아까 그거", "RSI는?" → 종목 스택 top에서 자동 해석

### 컨텍스트 합성 (LLM 프롬프트 주입)
최근 5턴 전문 + 이전 15턴 요약 + 에피소드 요약 1~2건 + 유저 프로필

---

## 10. 필수 참고 문서 전체 목록

### 10.1 서버 내 규칙 파일 (작업 전 반드시 읽기)
| 파일 | 경로 | 용도 |
|------|------|------|
| .cursorrules | /root/kis-autotrade-v4/.cursorrules | Cursor AI 서비스 경계 규칙 (V4.1/GO100 구분) |
| CLAUDE.md | /root/kis-autotrade-v4/CLAUDE.md | Claude Code용 동일 규칙 |
| SERVICE_BOUNDARY.md (3곳) | backend/app/routers/go100/, backend/app/services/go100/, scripts/go100/ | 디렉토리 소속 명시 |
| .env | /root/kis-autotrade-v4/.env | 환경변수 (GO100_AGENT_MODE, TELEGRAM, DB 등) |

### 10.2 프로젝트 공통 문서 (project-docs 루트)
| 파일 | 용도 | 우선순위 |
|------|------|---------|
| README.md | 레포 소개, 구조 설명 | ★★ |
| ONBOARDING.md | 새 작업자 온보딩 가이드 | ★★★ |
| DOCUMENT-NAMING-CONVENTION.md | 문서 명명 규칙 (CUR-, RPT- 등) | ★★ |

### 10.3 공통 템플릿/규칙 (common/)
| 파일 | 용도 | 우선순위 |
|------|------|---------|
| common/CONTEXT_TEMPLATE.md | AI 컨텍스트 전달 템플릿 | ★★ |
| common/CURSORRULES_TEMPLATE.md | .cursorrules 작성 템플릿 | ★★ |
| common/GIT_CONVENTION.md | Git 커밋 규칙 ([V4.1]/[GO100]/[SHARED]) | ★★★ |
| common/HANDOVER_TEMPLATE.md | 인계서 작성 템플릿 | ★★ |
| common/REPORT_TEMPLATE.md | 보고서 작성 템플릿 | ★★ |
| common/SECURITY_RULES.md | 보안 규칙 (API키, 토큰 등) | ★★★ |
| common/SYNC_GUIDE.md | 문서-코드 동기화 가이드 | ★★ |

### 10.4 GO100 핵심 문서 (go100/)
| 파일 | 용도 | 우선순위 |
|------|------|---------|
| go100/ARCHITECTURE.md | 시스템 아키텍처 v1.0 (서버, 스택, 라우터) | ★★★ |
| go100/DB_SCHEMA.md | DB 테이블 상세 스키마 | ★★★ |
| go100/API_SPEC.md | API 엔드포인트 명세 | ★★ |
| go100/CONTEXT.md | GO100 프로젝트 컨텍스트 | ★★ |
| go100/CURSORRULES.md | GO100 전용 Cursor 규칙 | ★★ |
| go100/CHANGELOG.md | 변경 이력 | ★★ |
| go100/ISSUES.md | 알려진 이슈 목록 | ★★ |
| go100/PLANNING.md | 단기 계획 | ★★ |
| go100/ROADMAP.md | 장기 로드맵 | ★★ |

### 10.5 인수인계서 히스토리 (go100/ — 최신순으로 읽기)
| 파일 | 날짜 | 핵심 내용 | 우선순위 |
|------|------|----------|---------|
| HANDOVER-20260227-V6-SESSION2.md | 02-27 | **★ 이 문서. 전체 통합 인계 (세션메모리, 조건검색, 병렬5작업)** | ★★★ |
| HANDOVER-20260225-V6.md | 02-25 | Phase 1-10 완료, Agent Core 설계 착수 | ★★★ |
| HANDOVER-20260225-V5.md | 02-25 | Phase 1-10, Agentic Architecture 상세 설계 | ★★★ |
| HANDOVER-20260225-V4.md | 02-25 | 백테스트 최적화, 리스크 관리 | ★★ |
| HANDOVER-20260225-V3.md | 02-25 | 데이터 수집, 전략 카드 시스템 | ★★ |
| GO100-HANDOVER-V3-PLANNING-20260226.md | 02-26 | **v2→v4 로드맵, 데이터 갭 분석, KPI** | ★★★ |
| HANDOVER-CLAUDE-SESSION-FULL-20260226.md | 02-26 | Claude 세션 전체 인계 | ★★ |
| HANDOVER-V3-UPGRADE-20260226.md | 02-26 | V3 업그레이드 세부 계획 | ★★ |
| HANDOVER-20260226-WAVE3-MAIN.md | 02-26 | Wave 3 메인 작업 내역 | ★★ |
| HANDOVER-20260226-WAVE2.md | 02-26 | Wave 2 작업 내역 | ★ |
| HANDOVER-20260224-V2.md | 02-24 | 초기 인프라 구축 | ★ |
| HANDOVER-20260223.md | 02-23 | 프로젝트 시작 | ★ |
| HANDOVER.md | - | 인계서 기본 프레임 | ★ |
| HANDOVER-INDEX.md | - | 인계서 버전 인덱스 | ★★★ |

### 10.6 기술 설계 문서 (go100/docs/)
| 파일 | 용도 | 우선순위 |
|------|------|---------|
| docs/OPUS-LLM-AI-v1-FULL-SPEC.md | **LLM AI 전체 스펙 (64KB, 가장 상세)** | ★★★ |
| docs/go100-architecture-v1.1.md | 아키텍처 v1.1 상세 (33KB) | ★★★ |
| docs/GO100-LLM-ARCHITECTURE-v2.0.md | LLM 아키텍처 v2.0 (3-Layer Dispatcher) | ★★★ |
| docs/BAEKEOGI-TECH-SPEC.md | 백억이 기술 스펙 상세 | ★★★ |
| docs/SERVER-INFRASTRUCTURE.md | 서버 인프라 상세 | ★★ |
| docs/CURSOR-FULL-DATA-COLLECTION-20260226.md | 데이터 수집 파이프라인 전체 명세 (34KB) | ★★★ |
| docs/DB-SCHEMA-GO100.md | GO100 전용 DB 스키마 상세 | ★★ |

### 10.7 기획/전략 보고서 (go100/)
| 파일 | 용도 | 우선순위 |
|------|------|---------|
| RPT-GO100-BAEKOGI-V3-GENIUS-TRADER-PLAN-20260226.md | **천재 트레이더 마스터플랜 (24KB)** | ★★★ |
| RPT-GO100-BAEKOGI-V3-MASTER-PLAN-20260226.md | V3 마스터플랜 (13KB) | ★★★ |
| GO100-BETA-TEST-CHECKLIST.md | 베타 테스트 체크리스트 | ★★ |

### 10.8 작업 보고서 (go100/reports/ — 최신순 핵심만)
| 파일 | 용도 | 우선순위 |
|------|------|---------|
| CUR-GO100-PARALLEL-4-TASKS-20260227.md | 병렬 4작업 완료 (무결성/레짐/Agent/텔레그램) | ★★★ |
| CUR-GO100-AUTO-HEALER-20260227.md | 자율 복구 엔진 | ★★★ |
| CUR-GO100-AGENT-CORE-V2-20260227.md | Agent Core v2 (21도구) | ★★★ |
| CUR-CRON-REALTIME-OPTIMIZATION-20260227.md | 크론 최적화 (19:30→17:30) | ★★★ |
| CUR-GO100-ADMIN-DATA-DASHBOARD-20260227.md | 관리자 데이터 대시보드 | ★★ |
| CUR-GO100-ADMIN-LOGIN-NGINX-FIX-20260226.md | Nginx 인증 수정 | ★ |
| BAEKOGI-AI-TECH-DOCS-REPORT-20260225.md | AI 기술 문서 정리 보고 | ★★ |
| BAEKOGI-V2-PLANNING-20260224.md | V2 기획 보고서 (36KB) | ★★★ |
| CUR-GO100-BACKTEST-OPT-PHASE1-001-20260225.md | 백테스트 최적화 Phase 1 | ★★ |
| CUR-GO100-BACKTEST-REALISTIC-001-REPORT-20260225.md | 현실적 백테스트 보고 | ★★ |
| CUR-GO100-BACKTEST-DB-AUDIT-001-20260224.md | 백테스트 DB 감사 | ★★ |
| CUR-GO100-ALARM-SYSTEM-CHECK-20260224.md | 알림 시스템 점검 | ★ |
| CUR-GO100-AUTH-REFRESH-v1-20260224.md | 인증 토큰 리프레시 | ★ |
| CUR-GO100-BACKFILL-DASHBOARD-001-20260220.md | 대시보드 백필 | ★ |
| CUR-GO100-AUDIT-ACTION-001-20260223.md | 감사 액션 | ★ |
| CUR-GO100-AI-BACKTEST-OPT-001-20260224.md | AI 백테스트 최적화 | ★ |
| CUR-GO100-BACKTEST-CARD-LIST-FIX-001-20260224.md | 카드 리스트 수정 | ★ |
| CUR-GO100-BACKTEST-SAVE-FIX-001-20260224.md | 백테스트 저장 수정 | ★ |
| CUR-GO100-BACKTEST-PERF-VERIFY-001-20260225.md | 성능 검증 | ★ |
| 20260223-HOTFIX-SAVE-500.md | 핫픽스 저장 500에러 | ★ |
| 20260223-PHASE2-STABILIZE.md | Phase 2 안정화 | ★ |

### 10.9 소스 덤프 (go100/_source-dump/) — 디버깅 참고용
| 파일 | 용도 |
|------|------|
| DOC-RECOVERY-LOG.txt | 문서 복구 로그 (80KB) |
| HANDOVER-001-LOG.txt | 최초 인계 로그 |
| BE_ERROR_LOG.txt | 백엔드 에러 로그 |
| FE_ChatWidget.tsx | 프론트엔드 채팅 위젯 소스 |
| FE_ProtectedLayoutClient.tsx | 프론트 레이아웃 소스 |
| NGINX_CONFIG.txt | Nginx 설정 덤프 |
| DB_CONSTRAINTS.txt | DB 제약조건 덤프 |
| E2E-VERIFY.txt | E2E 검증 로그 |
| DIAG-013.txt | 진단 로그 |

### 10.10 읽기 순서 (새 작업자 권장)
1. **이 인계서** (HANDOVER-20260227-V6-SESSION2.md) — 전체 현황 파악
2. **.cursorrules** — 서비스 경계 규칙 숙지
3. **common/GIT_CONVENTION.md** + **common/SECURITY_RULES.md** — 작업 규칙
4. **go100/ARCHITECTURE.md** + **go100/DB_SCHEMA.md** — 시스템 구조
5. **docs/GO100-LLM-ARCHITECTURE-v2.0.md** — LLM 3-Layer Dispatcher
6. **docs/CURSOR-FULL-DATA-COLLECTION-20260226.md** — 데이터 파이프라인
7. **GO100-HANDOVER-V3-PLANNING-20260226.md** — v2→v4 로드맵/KPI
8. **RPT-GO100-BAEKOGI-V3-GENIUS-TRADER-PLAN-20260226.md** — 천재 트레이더 플랜
9. 최신 작업 보고서 3건 (PARALLEL-4-TASKS, AUTO-HEALER, AGENT-CORE-V2)
10. **ONBOARDING.md** — 온보딩 가이드

---

## 11. 새 대화창 즉시 투입 체크리스트

1. 이 문서 읽기 완료
2. /root/kis-autotrade-v4/.cursorrules 읽기
3. Cursor 1~5 작업 상태 확인: 각 파일 존재 여부, git log 확인
4. 미완료 작업 이어받기:
   - Cursor 1,2,3 완료 확인 → 통합 테스트 (go100 서비스 재시작 → 채팅 테스트)
   - Cursor 4: 클로드 조건검색 엔진 완료 시 검토 착수
   - Cursor 5 완료 확인 → 백필 데이터 검증
5. 다음 우선순위: P1 잔여 → P2 (경험 DB, 시그널 성과, 모닝 브리핑)

### 상태 확인 명령어
```bash
# 서비스 상태
systemctl status go100
systemctl status redis

# Redis 세션 메모리 확인
redis-cli keys "go100:session:*"

# 새 테이블 존재 확인
psql -d kisautotrade -c "\dt go100_*"

# 새 파일 확인
ls -la /root/kis-autotrade-v4/backend/app/services/go100/memory/
ls -la /root/kis-autotrade-v4/backend/app/services/go100/collectors/

# 최근 커밋 확인
cd /root/kis-autotrade-v4 && git log --oneline -10
cd /root/project-docs && git log --oneline -10

# 크론 확인
crontab -l | grep go100

# 환경변수 확인
grep GO100 /root/kis-autotrade-v4/.env
```

---

## 12. 핵심 설계 판단 이력 (Why 기록)

| 판단 | 이유 |
|------|------|
| 모노리포 유지 | DB/Redis/Nginx 공유, 분리 비용 > 경계 관리 비용 |
| pandas-ta 주력 | TA-Lib은 C 의존 설치 어려움, pandas-ta는 순수 Python 130+ 지표 |
| Redis 세션 메모리 | PostgreSQL 실시간 read/write 부하 회피, TTL 자동 만료 |
| 에피소드 LLM 요약 | 전체 대화 저장은 비용/용량 문제, 요약본이 효율적 |
| pykrx 재무 우선 | KIS API 403 에러 상태, pykrx는 무료·안정, DART는 보조 |
| 복구 우선순위 5단계 | DB→pykrx→FDR→KIS→수동: 비용 최소·속도 최대 순 |
| 메모리 래퍼 방식 | agent_core.py 원본 최소 수정, 래퍼로 기능 추가 |

---

## 13. 연락처 및 접근 정보

- **서버**: SSH (IP/포트는 .env 참조)
- **DB**: PostgreSQL kisautotrade / kis_admin / localhost:5432
- **Redis**: localhost:6379/0
- **텔레그램**: @go100_auto_trading_bot
- **GitHub 문서**: github.com/moongoby/project-docs
- **대표님 계정**: [CEO-EMAIL-GM] (v4_users.user_id=2)
