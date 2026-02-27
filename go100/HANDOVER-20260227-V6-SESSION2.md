# GO100 인수인계서 v6.0 — Session 2 Complete Handover
> 작성: Claude Opus 4.6 | 날짜: 2026-02-27 | 대상: 다음 세션 AI

---

## ⚠️ 필수 규칙 — 반드시 먼저 읽고 준수

### 작업 규칙
1. 작업 시작 전 반드시 서비스 경계 확인: V4.1인지 GO100인지
2. 커밋 메시지 prefix 필수: [V4.1], [GO100], [SHARED]
3. GO100 작업 시 V4.1 파일 절대 수정 금지, 역도 동일
4. 공유 인프라(.env, main.py, nginx 등) 수정 시 양쪽 영향 명시
5. 대표님(user_id=2, moongoby@gmail.com)이 CEO — 보고체 사용
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
| 6 | 2 | moongoby@gmail.com | 대표님 (CEO) |
| 15 | 3 | moongoby@naver.com | 오병용 |

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

## 10. 새 대화창 즉시 투입 체크리스트

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

## 11. 핵심 설계 판단 이력 (Why 기록)

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

## 12. 연락처 및 접근 정보

- **서버**: SSH (IP/포트는 .env 참조)
- **DB**: PostgreSQL kisautotrade / kis_admin / localhost:5432
- **Redis**: localhost:6379/0
- **텔레그램**: @go100_auto_trading_bot
- **GitHub 문서**: github.com/moongoby/project-docs
- **대표님 계정**: moongoby@gmail.com (v4_users.user_id=2)
