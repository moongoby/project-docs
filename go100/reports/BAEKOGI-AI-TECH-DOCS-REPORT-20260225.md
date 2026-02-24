# 백억이 AI 관련 기술문서 검색·보고

**작성일**: 2026-02-25  
**목적**: kis-autotrade-v4 프로젝트 내 "백억이(Baekogi)" AI 관련 기술문서를 검색·정리한 보고서

**작업·반영 이력**

| 일자 | 내용 |
|------|------|
| 2026-02-25 | 최초 작성: 백억이 AI 관련 기술문서 검색·목록 정리 |
| 2026-02-25 | 문서 레포 URL 섹션 추가: 저장소(go100), 브랜치(phase-2c-command-center), 문서별 blob URL 테이블 반영 |
| 2026-02-25 | 미푸시 report 8건 add/commit/push (본 보고서 포함), 추가 참고 문서 레포 URL 표 추가 |
| 2026-02-25 | 본 「작업·반영 이력」 섹션 추가 및 보고서 최종 반영 보고 |

---

## 문서 레포 (Repository URL)

| 항목 | 값 |
|------|-----|
| **저장소** | [go100](https://github.com/moongoby/go100) |
| **기본 브랜치** | `phase-2c-command-center` |
| **트리 (파일 목록)** | https://github.com/moongoby/go100/tree/phase-2c-command-center |

---

## 1. 문서 목록 (요약) · 레포 URL

| 구분 | 문서 경로 | 레포 URL | 요약 |
|------|-----------|----------|------|
| **핵심 스펙** | `docs/go100/기획문서/OPUS-LLM-AI-v1-FULL-SPEC.md` | [보기](https://github.com/moongoby/go100/blob/phase-2c-command-center/docs/go100/기획문서/OPUS-LLM-AI-v1-FULL-SPEC.md) | LLM/AI 레이어 통합 기획 (멀티벤더, Gateway, 비용, 프롬프트) |
| **아키텍처** | `docs/go100-architecture-v1.1.md` | [보기](https://github.com/moongoby/go100/blob/phase-2c-command-center/docs/go100-architecture-v1.1.md) | GO100(백억이) 시스템 아키텍처, 사용자 여정, LLM 연동 |
| **대시보드·채팅** | `report/DASHBOARD-BAEKOGI-BANNER-NAMING-AND-CHAT-INPUT-PLAN-20260224.md` | [보기](https://github.com/moongoby/go100/blob/phase-2c-command-center/report/DASHBOARD-BAEKOGI-BANNER-NAMING-AND-CHAT-INPUT-PLAN-20260224.md) | 배너 이름 표기·채팅 입력창 기획 |
| **브리핑** | `report/DAILY-MARKET-BRIEFING-PLAN-20260224.md` | [보기](https://github.com/moongoby/go100/blob/phase-2c-command-center/report/DAILY-MARKET-BRIEFING-PLAN-20260224.md) | 당일 투자 환경 브리핑 (레짐, 지수, 백억이 채팅 연동) |
| **로그인 인사** | `report/LOGIN-GREETING-AND-BRIEFING-PLAN-20260224.md` | [보기](https://github.com/moongoby/go100/blob/phase-2c-command-center/report/LOGIN-GREETING-AND-BRIEFING-PLAN-20260224.md) | 로그인 시 인사·브리핑, 백억이 위젯 연동 |
| **종목 정보** | `report/GO100-STOCK-INFO-GENSPARK-STYLE-REPORT.md` | [보기](https://github.com/moongoby/go100/blob/phase-2c-command-center/report/GO100-STOCK-INFO-GENSPARK-STYLE-REPORT.md) | Genspark 스타일 종목 정보·1차 DB/2차 KIS API 기획 |
| **채팅 위젯** | `report/GO100-CHAT-WIDGET-REPORT-20260222.md` | [보기](https://github.com/moongoby/go100/blob/phase-2c-command-center/report/GO100-CHAT-WIDGET-REPORT-20260222.md) | AI 대화 API, ChatWidget, `/go100/chat` 연동 |
| **본 보고서** | `report/BAEKOGI-AI-TECH-DOCS-REPORT-20260225.md` | [보기](https://github.com/moongoby/go100/blob/phase-2c-command-center/report/BAEKOGI-AI-TECH-DOCS-REPORT-20260225.md) | 백억이 AI 기술문서 검색·정리 보고서 |

---

## 2. 핵심 문서 상세

### 2.1 OPUS-LLM-AI-v1-FULL-SPEC (LLM/AI 레이어)

- **경로**: `docs/go100/기획문서/OPUS-LLM-AI-v1-FULL-SPEC.md`
- **버전**: v2.1.1 (2026-02-23)
- **내용 요약**:
  - **MyTrader AI**: AI 교육형 자동매매 플랫폼, 자연어 대화로 투자 교육·전략 설계·백테스트·실매매 제공.
  - **도메인 분리**: 자유대화(free_chat), 설계대화(design_chat), C2SC 파싱(c2sc), 전략 검증(strategy_review), CS(Phase 2) — 각각 별도 시스템 프롬프트·모델·엔드포인트.
  - **멀티벤더**:
    - 자유대화: Gemini 2.0 Flash (Google)
    - 설계대화: Claude Sonnet 4.6 (Anthropic, 프롬프트 캐싱)
    - C2SC: GPT-4.1 mini (OpenAI, temp=0)
    - 전략 검증: Claude Opus 4.6 (Anthropic, 배치 API 50% 할인)
  - **LLM Gateway**: 독립 서비스 모듈, Chat Router → LLMGateway → 벤더 클라이언트(Gemini/Anthropic/OpenAI), 페일오버·서킷 브레이커·Rate Limiter·비용 추적(LLMCostTracker).
  - **규제**: AI 생성 답변 고지, 종목 추천/매매 시점/가격 예측 금지.
  - **비용**: 100명 기준 월 약 $14.93(₩21,649), 사용자당 약 ₩216.

### 2.2 GO100 아키텍처 (백억이 플랫폼)

- **경로**: `docs/go100-architecture-v1.1.md`
- **내용 요약**:
  - GO100 = 백억이 AI 기반 전략 설계 → 백테스트 → 실매매 플랫폼.
  - 백엔드: FastAPI, V4.1 인프라(DB, KIS, LLMGateway) 읽기 전용 참조 + go100_* 전용 테이블.
  - 사용자 여정: AI 채팅(자유 대화 → UNDERSTAND → DESIGN → EVALUATE/OPTIMIZE), UniverseEngine, BacktestService, StrategyCardService.
  - LLM: Gemini, Anthropic, OpenAI 연동 명시.

### 2.3 대시보드 백억이 배너·채팅 입력 (기획)

- **경로**: `report/DASHBOARD-BAEKOGI-BANNER-NAMING-AND-CHAT-INPUT-PLAN-20260224.md`
- **내용 요약**:
  - 배너 인사 문구에 "백억이" 명시 (예: `백억이 · 좋은 아침이에요! ☀️ 투자자님`).
  - 배너 내 채팅 입력창 추가: 전송 시 채팅 위젯 열고 메시지 전달(옵션 A/C) 또는 `/llm` 이동+쿼리(옵션 B).
  - 컴포넌트: `BaekogiWelcomeBanner.tsx`.

### 2.4 당일 투자 환경 브리핑

- **경로**: `report/DAILY-MARKET-BRIEFING-PLAN-20260224.md`
- **내용 요약**:
  - 브리핑 항목: 시장 레짐, 국내 지수(KOSPI/KOSDAQ), 환율, 코인, 해외 지수.
  - 노출: 로그인 브리핑 카드, 대시보드 "오늘의 시장" 위젯, **백억이 채팅**("오늘 시장 어때?" 등).
  - API 제안: `GET /api/v1/dashboard/market-briefing` (또는 briefing 통합).

### 2.5 로그인 인사·브리핑

- **경로**: `report/LOGIN-GREETING-AND-BRIEFING-PLAN-20260224.md`
- **내용 요약**:
  - 로그인 직후 1회 인사(토스트) + "오늘의 브리핑" 카드(1~3줄).
  - 2단계에서 백억이 위젯 자동 첫 메시지 검토.

### 2.6 종목 정보 (Genspark 스타일)

- **경로**: `report/GO100-STOCK-INFO-GENSPARK-STYLE-REPORT.md`
- **내용 요약**:
  - "종목 OOO 알려줘" / 종목 클릭 → 1차 우리 DB(stock_universe, ohlcv_daily, v4_trade_executions) → 2차 KIS API(CTPF1002R 등) → 구조화 답변.
  - 의도 분기: `stock_info` 추가, `POST /api/go100/ai/chat` 연동.

### 2.7 채팅 위젯·AI 대화 API

- **경로**: `report/GO100-CHAT-WIDGET-REPORT-20260222.md`
- **내용 요약**:
  - API: `POST /api/go100/ai/chat` (message, user_id, session_id 등).
  - 백엔드: `backend/app/routers/go100/ai_router.py`.
  - ChatWidget.tsx: FAB, 대화 패널, `chatWithAI`, 전체화면 `/go100/chat` 연결.

---

## 3. 추가 참고 문서 (레포 URL)

| 문서 | 레포 URL |
|------|----------|
| 로그인 인사·브리핑 구현 보고 | [report/LOGIN-GREETING-AND-BRIEFING-IMPLEMENTATION-REPORT-20260224.md](https://github.com/moongoby/go100/blob/phase-2c-command-center/report/LOGIN-GREETING-AND-BRIEFING-IMPLEMENTATION-REPORT-20260224.md) |
| 로드맵 | [docs/ROADMAP.md](https://github.com/moongoby/go100/blob/phase-2c-command-center/docs/ROADMAP.md) |
| 이슈 | [docs/ISSUES.md](https://github.com/moongoby/go100/blob/phase-2c-command-center/docs/ISSUES.md) |
| 변경 이력 | [docs/CHANGELOG.md](https://github.com/moongoby/go100/blob/phase-2c-command-center/docs/CHANGELOG.md) |
| 사용자 가이드 (go100) | [docs/go100/user-guide/](https://github.com/moongoby/go100/tree/phase-2c-command-center/docs/go100/user-guide) — 백억이 화면·온보딩 등 |

---

## 4. 정리

| 분류 | 문서 수 | 비고 |
|------|---------|------|
| **LLM/아키텍처 스펙** | 2 | OPUS-LLM-AI-v1, go100-architecture-v1.1 |
| **UI/UX·배너·채팅** | 2 | 배너 이름·채팅 입력, 채팅 위젯 |
| **브리핑·인사** | 3 | 당일 브리핑, 로그인 인사·브리핑 (및 구현 보고) |
| **기능 기획** | 1 | 종목 정보 Genspark 스타일 |

백억이 AI 관련 **핵심 기술문서**는 위 목록으로 정리되며, **가장 중심이 되는 문서**는 `docs/go100/기획문서/OPUS-LLM-AI-v1-FULL-SPEC.md`(LLM 레이어 통합 스펙)과 `docs/go100-architecture-v1.1.md`(시스템 아키텍처)이다.

---

## 보고 요약

- **대상**: 백억이(Baekogi) AI 관련 기술문서.
- **저장소**: https://github.com/moongoby/go100 (브랜치 `phase-2c-command-center`).
- **문서 수**: 핵심 8건(스펙·아키텍처·배너·브리핑·로그인 인사·종목 정보·채팅 위젯·본 보고서) + 참고 5건.
- **반영 사항**: 문서 레포 URL을 1·3절 테이블에 반영함. 미푸시 report 8건 푸시 완료. 본 보고서에 작업·반영 이력 및 보고 요약 추가.
