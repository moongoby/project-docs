# GO100 URL 정리 보고서 (go100.newtalk.kr)

> 작성일: 2026-03-04
> 태스크: CUR-GO100-URL-CATALOG-001
> 도메인: https://go100.newtalk.kr

---

## 1. 프론트엔드 페이지 URL (총 52개)

### 1.1 Public 페이지 (인증 불필요) — 8개

| # | URL | 설명 |
|---|-----|------|
| 1 | `/` | 홈 → 로그인/대시보드 리다이렉트 |
| 2 | `/auth/login` | 로그인 (이메일, 카카오, 네이버, 구글) |
| 3 | `/auth/signup` | 회원가입 |
| 4 | `/auth/forgot-password` | 비밀번호 찾기 |
| 5 | `/auth/callback` | OAuth 콜백 핸들러 |
| 6 | `/terms` | 이용약관 |
| 7 | `/privacy` | 개인정보처리방침 |
| 8 | `/offline` | 오프라인 폴백 |

### 1.2 GO100 코어 페이지 (인증 필요) — 14개

| # | URL | 설명 |
|---|-----|------|
| 1 | `/go100` | → `/dashboard` 리다이렉트 |
| 2 | `/go100/dashboard` | GO100 트레이딩 실시간 대시보드 |
| 3 | `/go100/strategies` | 내 전략 목록 |
| 4 | `/go100/strategies/[id]` | 전략 상세 (초보자 친화 UI) |
| 5 | `/go100/store` | 전략 마켓플레이스 |
| 6 | `/go100/paper-trading` | 모의투자 목록 |
| 7 | `/go100/paper-trading/[id]` | 모의투자 상세 |
| 8 | `/go100/live-trading` | 실거래 목록 |
| 9 | `/go100/live-trading/[id]` | 실거래 상세 |
| 10 | `/go100/chat` | AI 채팅 → `/llm` 리다이렉트 |
| 11 | `/go100/portfolio` | GO100 포트폴리오 |
| 12 | `/go100/notifications` | GO100 알림 |
| 13 | `/go100/settings` | GO100 설정 (리스크 프로필) |

### 1.3 공통 페이지 (인증 필요) — 7개

| # | URL | 설명 |
|---|-----|------|
| 1 | `/dashboard` | 메인 대시보드 |
| 2 | `/portfolio` | 포트폴리오 요약 |
| 3 | `/trade` | 자동매매 (V4) |
| 4 | `/stock/[code]` | 종목 상세 |
| 5 | `/llm` | AI 챗 (백억이) |
| 6 | `/notifications` | 알림센터 |
| 7 | `/settings` | 사용자 설정 |

### 1.4 프리미엄/관리자 전용 — 11개

| # | URL | 권한 | 설명 |
|---|-----|------|------|
| 1 | `/accounts` | PREMIUM+ | 계좌 관리 |
| 2 | `/strategy-cards` | PREMIUM+ | 전략카드 (V4) |
| 3 | `/backtest` | PREMIUM+ | 백테스트 실행 |
| 4 | `/backtest/analysis` | PREMIUM+ | 백테스트 분석 |
| 5 | `/monitoring` | PREMIUM+ | 시스템 모니터링 |
| 6 | `/monitoring/data-collection` | PREMIUM+ | 데이터수집 모니터 |
| 7 | `/reports` | PREMIUM+ | 트레이딩 리포트 |
| 8 | `/admin` | ADMIN | 관리자 대시보드 |
| 9 | `/admin/backtest` | ADMIN | 관리자 백테스트 |
| 10 | `/admin/backtest/[sessionId]` | ADMIN | 백테스트 세션 상세 |
| 11 | `/admin/backtest/charts` | ADMIN | 백테스트 차트 |

### 1.5 관리자 상세 페이지 — 3개

| # | URL | 설명 |
|---|-----|------|
| 1 | `/admin/backtest/daily/[sessionId]/[date]` | 일별 백테스트 결과 |
| 2 | `/admin/backtest/trades/[tradeId]` | 거래 상세 |
| 3 | `/admin/backtest/discovery/[discoveryId]` | 발견 결과 상세 |

---

## 2. 백엔드 API 엔드포인트 (21개 라우터, 150+ 엔드포인트)

### 2.1 GO100 Dashboard API (`/api/go100/dashboard`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/summary` | 포트폴리오 요약, 전략카드, 최근 시그널 |
| GET | `/signals?days=7-30` | 글로벌 시그널 (USD/KRW, VIX, S&P500 등) |
| GET | `/integrity?hours=24-168` | 데이터 무결성 체크 |
| GET | `/experience?days=7-90` | 사용 통계 및 에러 로그 |
| GET | `/overview` | 총자산, 수익률, MDD, 목표, 레짐 |
| GET | `/performance?period=1m|3m|6m|1y|all` | 일별 수익률 vs KOSPI |
| GET | `/positions` | 현재 보유종목 (모의/실거래) |
| GET | `/strategies` | 전략카드 성과 지표 |
| GET | `/regime-history?days=90` | 레짐 변화 이력 |
| GET | `/goal-progress` | 목표 달성률 |
| GET | `/activity-log?limit=50` | 최근 거래 및 이벤트 |

### 2.2 Strategy Cards API (`/api/go100/strategy-cards`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/` | 전략카드 생성 |
| GET | `/` | 전략카드 목록 (페이지네이션) |
| GET | `/{card_id}` | 전략카드 상세 |
| PUT | `/{card_id}` | 전략카드 수정 |
| POST | `/{card_id}/transition` | 상태 전이 (DRAFT→BACKTESTED→PAPER_LIVE→LIVE) |
| PATCH | `/{card_id}/toggle` | 활성/비활성 토글 |
| DELETE | `/{card_id}` | 소프트 삭제 |

### 2.3 Store API (`/api/go100/store`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/store` | 시스템 전략 마켓플레이스 |
| POST | `/store/subscribe` | 시스템 전략 구독/복제 |

### 2.4 Paper Trading API (`/api/go100/paper-trading`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/start` | 모의투자 시작 |
| GET | `/` | 모의 포트폴리오 목록 |
| GET | `/{portfolio_id}` | 모의 포트폴리오 상태 |
| POST | `/{portfolio_id}/pause` | 일시정지 |
| POST | `/{portfolio_id}/resume` | 재개 |
| POST | `/{portfolio_id}/stop` | 중지 |
| GET | `/{portfolio_id}/positions` | 오픈 포지션 |
| GET | `/{portfolio_id}/trades` | 체결 이력 |
| POST | `/{portfolio_id}/run-now` | 수동 실행 |
| GET | `/{portfolio_id}/snapshots?days=30` | 일별 스냅샷 |

### 2.5 Live Trading API (`/api/go100/live-trading`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/start` | 실거래 시작 |
| GET | `/` | 실거래 포트폴리오 목록 |
| GET | `/{portfolio_id}` | 실거래 상태 |
| POST | `/{portfolio_id}/pause` | 일시정지 |
| POST | `/{portfolio_id}/resume` | 재개 |
| POST | `/{portfolio_id}/stop` | 중지 |
| POST | `/{portfolio_id}/run-now?dry_run=true` | 수동 실행 (PREMIUM) |
| POST | `/{portfolio_id}/reconcile?dry_run=true` | 증권사 포지션 조정 |

### 2.6 Trade API (`/api/go100/trade`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/start` | 자동매매 시작 (스케줄 생성) |
| POST | `/stop` | 자동매매 중지 |
| GET | `/status/{card_id}` | 자동매매 상태 |
| GET | `/accounts` | 활성 계좌 목록 |

### 2.7 Backtest API (`/api/go100/backtest`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | 백테스트 실행 목록 |
| POST | `/run` | 백테스트 실행 (비동기) |
| POST | `/{run_id}/retry` | 실패한 백테스트 재시도 |
| POST | `/retry/{run_id}` | 재시도 (대체 경로) |
| GET | `/{run_id}` | 백테스트 결과 상세 |

### 2.8 Risk API (`/api/go100/risk`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/defaults/{risk_tolerance}` | 리스크 프로필 기본값 |
| GET | `/effective?strategy_card_id&risk_tolerance` | 유효 설정 미리보기 |
| POST | `/disclaimer` | 면책동의 기록 |
| GET | `/disclaimers` | 면책동의 이력 |

### 2.9 Live Orders API (`/api/go100/live`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/orders?limit=50&status=FILLED|PENDING|ERROR|REJECTED` | 체결 내역 |

### 2.10 Notifications API (`/api/go100/notifications`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | 알림 목록 (페이지네이션) |
| GET | `/unread-count` | 읽지 않은 알림 수 |
| PATCH | `/{notification_id}/read` | 단일 읽음 처리 |
| POST | `/read-all` | 전체 읽음 처리 |
| GET | `/stream` | **SSE** 실시간 알림 스트림 |
| GET | `/settings` | 알림 설정 조회 |
| PUT | `/settings` | 알림 설정 변경 |
| POST | `/push-subscribe` | 브라우저 푸시 구독 |
| DELETE | `/push-subscribe?endpoint=...` | 푸시 구독 해제 |
| POST | `/test` | 테스트 알림 발송 |

### 2.11 Reports API (`/api/go100/reports`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/unread-count` | 읽지 않은 리포트 수 |
| GET | `/` | 리포트 목록 |
| PATCH | `/{report_id}/read` | 읽음 처리 |

### 2.12 Portfolio API (`/api/go100/portfolios`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/` | 포트폴리오 생성 |
| GET | `/` | 포트폴리오 목록 |
| GET | `/{portfolio_id}` | 포트폴리오 상세 + 포지션 |
| PUT | `/{portfolio_id}` | 포트폴리오 수정 |
| DELETE | `/{portfolio_id}` | 포트폴리오 비활성화 |
| GET | `/{portfolio_id}/positions` | 포지션 목록 |
| GET | `/{portfolio_id}/summary` | 포트폴리오 요약 |

### 2.13 Scheduler API (`/api/go100/scheduler`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/run-live?dry_run=true` | 수동 실거래 실행 (PREMIUM) |
| POST | `/run-paper` | 수동 모의투자 실행 |
| POST | `/reconcile?dry_run=true` | 증권사 조정 (PREMIUM) |
| GET | `/status` | 스케줄러 상태 |

### 2.14 Optimizer API (`/api/go100/optimizer`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/fit-analysis` | 종목×전략 Fit 분석 |
| GET | `/fit-analysis/{card_id}` | Fit 분석 결과 |
| POST | `/exit-optimize` | Exit 파라미터 최적화 (그리드 탐색) |
| POST | `/desk-allocation` | 멀티 DESK 자금 배분 |
| GET | `/desk-allocation/{alloc_id}` | 배분 결과 |

### 2.15 Goals API (`/api/go100/goals`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/` | 투자 목표 생성 |
| GET | `/` | 목표 목록 |
| GET | `/{goal_id}` | 목표 상세 |
| PUT | `/{goal_id}` | 목표 수정 |

### 2.16 AI Chat API (`/api/go100/ai`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/chat` | 멀티턴 AI 대화 |
| POST | `/understand` | 이해 에이전트 |
| POST | `/design` | 설계 에이전트 |
| POST | `/evaluate` | 평가 에이전트 |
| POST | `/optimize` | 최적화 에이전트 |
| GET | `/task/{task_id}` | 장기 실행 작업 상태 |

### 2.17 Commander API (`/api/go100/commander`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/status` | Commander 상태 + 에이전트 가중치 |
| POST | `/morning-analysis` | 모닝 분석 (레짐/수급/기술/뉴스) |
| POST | `/post-market` | 장 마감 리뷰 |
| POST | `/desk5-scan` | 주간 시드 발굴 (DESK5) |
| POST | `/desk4-review` | 일간 캔들 트래킹 (DESK4) |
| POST | `/desk-chain` | DESK 체인 실행 (5→4→3→2) |
| POST | `/research` | 리서치 파이프라인 |
| POST | `/research-lab` | 연구실 파이프라인 |
| GET | `/knowledge-base?status=hypothesis&source_type=...` | 전략 지식베이스 |

### 2.18 Me API (`/api/go100`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/me` | 유저 매핑 (v4_users) |

### 2.19 Briefing API (`/api/go100/briefing`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/latest` | 최신 일일 브리핑 |
| POST | `/generate` | 브리핑 수동 생성 |

### 2.20 Trading Dashboard API (`/api/v1/trading/dashboard`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/summary?account_type=paper|live|all` | 오늘 요약 (채널별) |
| GET | `/positions?account_type=...` | 현재 보유종목 (1초 캐시) |
| GET | `/orders` | 일간 주문/체결 내역 |
| GET | `/performance` | 기간별 수익률 차트 데이터 |
| GET | `/signals` | 오늘 시그널 상태 |
| GET | `/stream` | **SSE** 실시간 트레이딩 이벤트 |

### 2.21 Monitor API (`/monitor`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 서비스 헬스 (DB, Redis, 디스크, 메모리) |
| GET | `/system` | 시스템 상태 |
| GET | `/stats?days=7-90` | 사용 통계 |
| GET | `/errors` | 최근 에러 로그 |
| GET | `/alerts` | 시스템 알림 |
| GET | `/disk` | 디스크 사용량 |

### 2.22 Bridge API (`/api/go100/bridge`) — 내부 전용 (localhost only)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/risk/status?user_id=2` | GO100 리스크 엔진 상태 |
| POST | `/portfolio/optimize` | 포트폴리오 최적화 |
| GET | `/score?...` | AI 스코어링 |
| POST | `/score/batch` | 배치 AI 스코어링 |

---

## 3. 실시간 채널 (SSE)

| 엔드포인트 | 용도 | 하트비트 | 재연결 |
|-----------|------|---------|--------|
| `/api/go100/notifications/stream` | 사용자 알림 실시간 푸시 | 30초 | 자동 |
| `/api/v1/trading/dashboard/stream` | 체결/거래 이벤트 | 30초 | 5초 후 재시도 |

---

## 4. Nginx 라우팅 구조

```
go100.newtalk.kr (HTTPS)
├── /api/*          → localhost:8002 (GO100 FastAPI)
├── /ws/*           → localhost:8003 (V4.1 WebSocket)
├── /_next/hmr      → localhost:3000 (Next.js HMR WebSocket)
└── /*              → localhost:3000 (Next.js Frontend)
```

---

## 5. 인증 & 미들웨어

### 5.1 Public 경로 (인증 우회)
```
/auth/login, /auth/register, /auth/signup, /auth/forgot-password,
/auth/callback, /, /terms, /privacy
```

### 5.2 미들웨어 제외 경로
```
/_next, /health, /api, /favicon
```

### 5.3 인증 필수 경로 (JWT)
```
/dashboard, /accounts, /strategy-cards, /admin, /llm, /go100
```

### 5.4 권한 체계
| 역할 | 접근 범위 |
|------|----------|
| 일반 사용자 | GO100 코어 + 공통 페이지 |
| PREMIUM | + accounts, strategy-cards, backtest, monitoring, reports |
| ADMIN / SUPER_ADMIN | + admin/* 전체 |
| CEO (user_id=2) | 전체 데이터 조회 (target_user_id 파라미터) |

---

## 6. 요약 통계

| 항목 | 수치 |
|------|------|
| 프론트엔드 페이지 | **52개** |
| 백엔드 라우터 | **22개** |
| API 엔드포인트 | **150+개** |
| SSE 스트림 | **2채널** |
| API 연동률 | **97%** |
| 인증 방식 | JWT (자동갱신, 401 리다이렉트) |

---

## 7. 브라우저 접근 경로 (Full URL)

### 일반 사용자 주요 경로
| 경로 | Full URL |
|------|----------|
| 로그인 | `https://go100.newtalk.kr/auth/login` |
| 대시보드 | `https://go100.newtalk.kr/dashboard` |
| GO100 대시보드 | `https://go100.newtalk.kr/go100/dashboard` |
| 내 전략 | `https://go100.newtalk.kr/go100/strategies` |
| 전략 마켓 | `https://go100.newtalk.kr/go100/store` |
| 모의투자 | `https://go100.newtalk.kr/go100/paper-trading` |
| 실거래 | `https://go100.newtalk.kr/go100/live-trading` |
| 포트폴리오 | `https://go100.newtalk.kr/go100/portfolio` |
| AI 챗 | `https://go100.newtalk.kr/llm` |
| 알림 | `https://go100.newtalk.kr/go100/notifications` |
| 설정 | `https://go100.newtalk.kr/go100/settings` |

### 관리자 주요 경로
| 경로 | Full URL |
|------|----------|
| 관리자 홈 | `https://go100.newtalk.kr/admin` |
| 계좌 관리 | `https://go100.newtalk.kr/accounts` |
| 백테스트 | `https://go100.newtalk.kr/admin/backtest` |
| 모니터링 | `https://go100.newtalk.kr/monitoring` |
| 리포트 | `https://go100.newtalk.kr/reports` |

---

*보고서 끝*
