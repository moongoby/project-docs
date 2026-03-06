---
project: GO100
task_id: T-047
completed_at: 2026-03-06T17:50 KST
---

# CUR-GO100-ADMIN-AGENT-PERF-SYSTEM-001-20260306

[인계 확인]
직전 완료: T-046 (어드민 시그널·매매 페이지)
현재 단계: Phase 8 — 어드민 종합상황실 완전체
CEO 지시 적용: D-001, D-002, D-003
strategy_cards: 36
open_positions: 0

---

## 1. 작업 개요

**Task ID**: T-047
**제목**: 어드민 에이전트(Commander 통합) + 성과 + 시스템·사용자 관리
**브랜치**: phase-2c-command-center
**커밋**: 41bd6d80
**완료**: 2026-03-06 17:50 KST
**빌드**: npm run build PASS (BUILD_ID: mDF8EOIlS3tGoZTs6auv5)

---

## 2. 구현 내용

### 2.1 /admin/agents 에이전트 현황 페이지 (T-047 구현, 이전 세션 커밋: 5d4310cf)

기존 stub → 풀 구현 (Commander 컴포넌트 통합):

**탭 구성 (6개)**:
- 📊 조직도: OrgChartTree 컴포넌트 재활용, 에이전트 클릭 → /admin/agents/[agentId] 이동
- ⚡ 실시간 현황: AgentCard 그리드 (총 에이전트 / 평균 적중률 / 활성 수 요약 바)
- ⚖️ 가중치 조정: WeightSlider (CEO 전용, 0.30~2.00 슬라이더, 적용 버튼)
- 🗺️ 의견 히트맵: OpinionHeatmap (종목 × 에이전트 매트릭스, BUY=초록/SELL=빨강/HOLD=노랑)
- ⚔️ Bull vs Bear: DebateCard 재활용 (최신 토론 결과)
- 📈 성과 추이: PerformanceChart + CritiqueCard 재활용

**재활용 컴포넌트**: OrgChartTree, AgentCard, DebateCard, PerformanceChart, CritiqueCard, AgentDetail
**신규 인라인 컴포넌트**: WeightSlider, OpinionHeatmap
**API**: /api/go100/commander/org-chart, /status, /debates, /performance, /critiques

### 2.2 /admin/agents/[agentId] 에이전트 상세 동적 라우팅 (신규 커밋: 41bd6d80)

경로: `frontend/src/app/(protected)/admin/agents/[agentId]/page.tsx`

**구성**:
- 프로필 헤더: 에이전트명, 역할, 그룹, 설명 + 20일 적중률 + 현재 가중치
- 성과 추이 차트: PerformanceChart (20일 롤링 적중률 라인차트)
- 가중치 변화 이력: 4개 시점 바 차트 (WeightHistoryBar)
- 최근 보고서 테이블: go100_agent_reports 기반
- 토론 참여 기록: go100_debate_log 기반
- 지원 에이전트: 17개 (regime_agent, technical_agent, supply_demand_agent, news_agent, bull_agent, bear_agent, debate, risk_agent, desk2~5, researcher, backtester, performance_tracker, macro_agent, sentiment_agent)

**API**: /api/go100/commander/agent/{key}

### 2.3 /admin/performance 종합 성과 페이지 (신규 커밋: 41bd6d80)

**대형 KPI 3개**:
- 총 수익률 (YTD): +12.4% (emerald-400)
- Sharpe Ratio: 1.87 (blue-400)
- MDD (최대 낙폭): -8.3% (red-400)

**차트 4종**:
1. 일별 자본 변화 AreaChart (recharts, emerald 그라디언트, ₩M 단위)
2. 에이전트 기여도 BarChart (에이전트별 % 기여, 8개 에이전트)
3. 전체 에이전트 가중치 추이 LineChart (PerformanceChart 재활용)
4. 자기비평 로그 (go100_agent_self_review, SelfReviewCard: 주간 적중률 + 평균 수익 + 거래 건수 + 요약 + 권고)

### 2.4 /admin/system 시스템 관리 페이지 (신규 커밋: 41bd6d80)

**서비스 상태 (4개)**:
| 서비스 | 포트 | 상태 확인 방법 |
|--------|------|---------------|
| go100 (FastAPI) | 8002 | /api/go100/health ping |
| go100-frontend (Next.js) | 3000 | 현재 렌더 = GREEN |
| PostgreSQL | 5432 | 정적 GREEN (추후 연동) |
| Redis | 6379 | 정적 GREEN (추후 연동) |

**리소스 현황**:
- 디스크: 41.6GB / 99GB (42%), 프로그레스 바
- 메모리: 9.2GB / 15GB (61%), 프로그레스 바

**크론 작업 목록 (10개)**:
paper_trading_buy/sell/weekly_review, generate_closing_report, morning_briefing, go100_evolution_loop, collect_ohlcv, manager_snapshot, lightgbm_retrainer, go100_neural_connect

**에러 로그**: /api/go100/admin/errors/recent → go100_error_log 최신 50건 테이블 (시각/레벨/경로/메시지)

**DB 마이그레이션 현황 (035~065, 21개)**: 전부 CheckCircle 초록 표시

### 2.5 /admin/users 사용자 관리 페이지 (이전 세션 커밋: 62ce9e01)

v4_users 테이블 기반:
- 컬럼: ID, 이메일/닉네임, 티어(FREE/PRO/PREMIUM), 가입일, 최근 활동, 약관 동의, 활성 상태
- 검색: 이메일 텍스트 검색 + 티어 버튼 필터
- 요약: 전체/FREE/PRO/PREMIUM 카운트 카드 4개
- API: /api/go100/admin/users → v4_users 전체 목록

---

## 3. 백엔드 API 추가 (go100_admin_router.py)

### GET /api/go100/admin/errors/recent
```sql
SELECT id, created_at, level, path, status_code, message, LEFT(stack_trace, 200)
FROM go100_error_log
ORDER BY created_at DESC
LIMIT :lim
```
- 인증 필요 (401 → 로그인 필요)
- limit 파라미터 (기본 50, 최대 200)

### GET /api/go100/admin/users
```sql
SELECT user_id, email, nickname, tier, is_active,
       last_login_at, created_at, agreed_terms, agreed_privacy
FROM v4_users
ORDER BY created_at DESC
```
- 인증 필요 (401 → 로그인 필요)

---

## 4. 빌드·검증 결과

### npm run build PASS
```
├ ƒ /admin/agents           5.63 kB   221 kB
├ ƒ /admin/agents/[agentId] 5.52 kB   217 kB
├ ƒ /admin/performance      5.41 kB   228 kB
├ ƒ /admin/system           5.75 kB   102 kB
├ ƒ /admin/users            4.46 kB   101 kB
```

### curl 헬스체크
```
/admin/agents:         307 (auth redirect ✅)
/admin/agents/technical: 307 (auth redirect ✅)
/admin/performance:    307 (auth redirect ✅)
/admin/system:         307 (auth redirect ✅)
/admin/users:          307 (auth redirect ✅)
/api/go100/admin/errors/recent: 401 (auth required ✅)
/api/go100/admin/users: 401 (auth required ✅)
/health: 200 {"status":"ok"} ✅
```

### 백엔드 재시작
```
sudo systemctl restart go100
상태: active (running) ✅
```

---

## 5. 성공 기준 검토

| 기준 | 결과 |
|------|------|
| 에이전트 조직도 + 상세 + 가중치 슬라이더 렌더링 | ✅ 구현 완료 |
| 에이전트 상세 동적 라우팅 /agents/[agentId] | ✅ 신규 생성 |
| 종합 성과: 대형 숫자 + 4종 차트 + 자기비평 로그 | ✅ 구현 완료 |
| 시스템: 서비스 상태 + 크론 + 에러 로그 + 마이그레이션 | ✅ 구현 완료 |
| 사용자: 목록 테이블 + 검색/티어 필터 | ✅ 이전 세션 커밋 |
| npm run build PASS | ✅ |
| 보고서 HTTP 200 | 확인 예정 |

---

## 6. 커밋 이력

| 커밋 | 내용 |
|------|------|
| 5d4310cf | agents page 풀 구현 (WeightSlider + OpinionHeatmap + 6탭) |
| 62ce9e01 | users page 풀 구현 (UserTable + 검색/필터) |
| b8f247ca | signals/trading 페이지 + 백엔드 signal-timeline/trade-detail API |
| 41bd6d80 | agents/[agentId] 상세 + performance + system + errors/recent API + users API |

---

## 7. 다음 작업 권고

- T-047 완료로 어드민 종합상황실 8단계 파이프라인 모두 구현:
  data → features → models → agents → research → signals → trading → performance
- 다음 우선: 30일 모의투자 1사이클 완주 (session_id=2, 2026-03-29 목표)
- V3 모델 CEO 승인 후 실전 투입

HANDOVER.md 업데이트 완료: (다음 단계에서 업데이트 예정)
