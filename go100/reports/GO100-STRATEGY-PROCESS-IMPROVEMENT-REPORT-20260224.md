# GO100 전략 생성 후 프로세스 점검 및 개선안 보고서

**작성일:** 2026-02-24
**대상:** GO100 AI 자동매매 시스템 (kis-autotrade-v4)
**범위:** 전략 생성 → 백테스트 → 모의거래 → 실거래 전체 E2E 프로세스

---

## 1. 현재 프로세스 흐름도

```
[사용자 채팅 입력]
    ↓
[ChatWidget / /llm 페이지]
    ↓ POST /api/go100/ai/chat
[BaseOrchestrator]
    ├─ UNDERSTAND: UserIntent 추출 (투자성향, 리스크, 섹터 등 12개 필드)
    ├─ DESIGN: StrategyDesign 생성 (진입/청산/리스크 규칙)
    ├─ DRAFT Card INSERT → go100_strategy_cards (status=DRAFT)
    ├─ BACKTEST Loop (최대 5+1회)
    │   ├─ 분봉 시뮬레이터 → 실패 시 일봉 시뮬레이터 fallback
    │   ├─ EVALUATE: 리스크 기준 통과 여부 판단
    │   └─ OPTIMIZE: 미통과 시 파라미터 조정 후 재백테스트
    └─ Card UPDATE → status=BACKTESTED + 수익률/MDD/샤프비율 저장
    ↓
[사용자 응답] "전략카드 'xxx'이(가) 저장되었습니다. 내 전략 탭에서 확인하세요."
    ↓ [수동]
[모의거래 생성] POST /api/go100/paper-trading/start
    ↓ [자동 - 스케줄러]
[일일 자동 매매 실행] Go100DailyScheduler.run_all_paper()
    ↓ [수동]
[실거래 전환] status → LIVE + 증권계좌 연결
    ↓ [자동 - 스케줄러]
[실거래 자동 매매] Go100DailyScheduler.run_all_live()
```

### 카드 상태 라이프사이클

```
IDEA → DRAFT → BACKTESTED → PAPER_LIVE → LIVE
       ↑                          ↓    ↓
       └────────────── PAUSED → RETIRED
```

### LLM 모델 배분

| 역할 | 모델 | 용도 |
|------|------|------|
| FREE_CHAT | Google Gemini-2.5-flash | UNDERSTAND, REPLY, EVALUATE |
| DESIGN_CHAT | Anthropic Claude-sonnet-4-6 | DESIGN, OPTIMIZE |

---

## 2. 발견된 문제점 (총 14건)

### 2-1. CRITICAL (즉시 수정 필요) - 4건

#### [C-1] /go100/chat 리다이렉트로 인한 컨텍스트 손실
- **현상:** 사이드바 "AI 대화" 클릭 → `/go100/chat` → `/llm`으로 리다이렉트
- **영향:** GO100 레이아웃(사이드바) 사라짐, 사용자 혼란
- **파일:** `frontend/src/app/(protected)/go100/chat/page.tsx`
- **원인:** 페이지 전체가 `router.replace("/llm")`으로 대체됨

#### [C-2] 전략 상세보기 라우트 미구현
- **현상:** "상세보기" 클릭 → `/go100/strategies/{id}` → `/strategy-cards`로 리다이렉트
- **영향:** GO100 전용 상세 페이지 없음, 전략 파라미터 수정 불가
- **파일:** `frontend/src/app/(protected)/go100/strategies/[id]/page.tsx`
- **원인:** 상세 페이지가 리다이렉트로만 구현, `StrategyCardDetail` 컴포넌트는 존재하나 미연결

#### [C-3] 하드코딩된 DEFAULT_USER_ID = 1
- **현상:** ChatWidget/ChatInterface에서 user_id가 1로 고정
- **영향:** 멀티유저 환경에서 모든 전략이 user_id=1로 생성됨
- **파일:** `ChatWidget.tsx:27`, `ChatInterface.tsx:32`
- **원인:** 인증 컨텍스트 연동 누락

#### [C-4] /llm 페이지의 "전략카드로 저장" 이중 저장 경로
- **현상:** `/llm`의 StrategyCardSaveButton이 `POST /api/go100/strategy-cards` 호출 (수정됨)
- **잔여 리스크:** AI 대화 자체에서도 자동 저장하므로, 사용자가 수동 저장 버튼까지 누르면 중복 카드 생성 가능
- **영향:** "내 전략"에 동일 전략 중복 표시

---

### 2-2. HIGH (조기 수정 권장) - 5건

#### [H-1] 백테스트 드롭다운에서 GO100 카드 누락 가능성
- **현상:** `GET /api/v1/strategy-cards/for-backtest`는 V4.1 + GO100 병합 구현 완료
- **잔여 이슈:** GO100 카드 선택 시 `stock_codes` 수동 입력 요구 (universe_filter 자동 적용 미완)
- **파일:** `backend/app/services/strategy_card_service.py`

#### [H-2] 백테스트 실패 시 복구 메커니즘 없음
- **현상:** 백테스트 실패 → status='FAILED' 기록 후 종료
- **영향:** 재시도 버튼/API 없음, 사용자가 새 전략 생성해야 함
- **파일:** `backend/app/services/go100/backtest/backtest_service.py`

#### [H-3] 포트폴리오 중복 생성 방지가 애플리케이션 레벨만
- **현상:** 동일 카드로 ACTIVE 포트폴리오 중복 생성 방지 로직 존재
- **리스크:** DB UNIQUE 제약조건 없음 → 동시 요청 시 race condition 가능
- **파일:** `backend/app/services/go100/portfolio/portfolio_service.py`

#### [H-4] 세션 ID 관리 취약
- **현상:** localStorage에 세션 ID 저장, TTL/서버 검증 없음
- **영향:** 만료된 세션으로 대화 시도 시 에러 또는 컨텍스트 손실
- **파일:** `ChatWidget.tsx` (WIDGET_SESSION_KEY)

#### [H-5] StrategyCardDetail TODO 미구현
- **현상:** 파라미터 수정(`handleParamSave`), 재백테스트(`handleRebacktest`) 미구현
- **영향:** 전략 미세조정 불가 → 불만족 시 전략 재생성 필요
- **파일:** `frontend/src/go100/components/StrategyCardDetail.tsx`

---

### 2-3. MEDIUM (계획적 수정) - 3건

#### [M-1] 도움말/사용법 질문 미지원
- **현상:** "대시보드가 뭐야?", "전략 어디서 봐?" 등 UI 질문에 전략 생성 파이프라인 실행
- **영향:** 사용자 질문 의도와 다른 응답
- **대안:** HelpFlow 모듈 + Intent Router 도입 (설계 완료, 미구현)

#### [M-2] 카드 상태 자동 전환 없음
- **현상:** 백테스트 완료 후 DRAFT → BACKTESTED 수동 전환 필요
- **영향:** 사용자가 상태 전환 API 직접 호출해야 함
- **파일:** `backend/app/routers/go100/strategy_router.py`

#### [M-3] 네비게이션 이중 구조 혼란
- **현상:** `/go100/strategies`(내 전략)와 `/strategy-cards`(통합 카탈로그) 역할 중복
- **영향:** 사용자가 어디서 전략을 관리해야 하는지 혼란

---

### 2-4. LOW (개선 사항) - 2건

#### [L-1] 에러 메시지 구체성 부족
- **현상:** ChatWidget 에러 시 "오류가 났어요. 다시 시도해 주세요." 고정 메시지
- **개선:** 에러 유형별 안내 + 재시도 버튼

#### [L-2] LIVE 전환 시 증권계좌 유효성 검증 부재
- **현상:** account_id만 전달하면 LIVE 포트폴리오 생성 가능
- **리스크:** 존재하지 않거나 연결 해제된 계좌로 실거래 시도

---

## 3. 개선안

### 3-1. 즉시 실행 (Phase 1 - 1~2일)

| # | 개선 항목 | 작업 내용 | 영향 파일 |
|---|----------|----------|----------|
| 1 | GO100 전용 채팅 페이지 복원 | `/go100/chat` 리다이렉트 제거, ChatInterface 컴포넌트 직접 렌더링 | `go100/chat/page.tsx` |
| 2 | GO100 전략 상세 페이지 구현 | `/go100/strategies/[id]`에 StrategyCardDetail 연결 | `go100/strategies/[id]/page.tsx` |
| 3 | user_id 동적 처리 | useAuth 훅에서 실제 user_id 가져오기 | `ChatWidget.tsx`, `ChatInterface.tsx` |
| 4 | 중복 저장 방지 | AI 자동 저장 후 수동 저장 버튼 비활성화 또는 중복 체크 | `StrategyCardSaveButton.tsx` |

### 3-2. 단기 개선 (Phase 2 - 3~5일)

| # | 개선 항목 | 작업 내용 | 영향 파일 |
|---|----------|----------|----------|
| 5 | 백테스트 재시도 API | `POST /api/go100/backtest/{id}/retry` 엔드포인트 추가 | `backtest_service.py`, `strategy_router.py` |
| 6 | 카드 상태 자동 전환 | 백테스트 성공 시 DRAFT → BACKTESTED 자동 업데이트 | `backtest_service.py` |
| 7 | 전략 파라미터 수정 연동 | StrategyCardDetail의 handleParamSave/handleRebacktest 구현 | `StrategyCardDetail.tsx`, `go100Api.ts` |
| 8 | 세션 관리 강화 | 세션 TTL(30분), 서버 검증, 만료 시 새 세션 자동 생성 | `ChatWidget.tsx`, AI chat backend |
| 9 | 포트폴리오 DB 제약조건 | go100_portfolios에 UNIQUE(card_id, portfolio_type, status) 추가 | DB migration |

### 3-3. 중기 개선 (Phase 3 - 1~2주)

| # | 개선 항목 | 작업 내용 | 영향 파일 |
|---|----------|----------|----------|
| 10 | HelpFlow 모듈 구현 | Intent Router + 도움말 KB + HelpFlow 서비스 | 신규 모듈 |
| 11 | 네비게이션 통합 | `/go100/strategies`를 GO100 전용 허브로, `/strategy-cards`는 V4.1 전용으로 분리 | 라우터, 사이드바 |
| 12 | GO100 백테스트 universe_filter 자동 적용 | 카드 선택 시 universe_filter에서 종목 자동 추출 | `backtest/page.tsx`, backtest API |
| 13 | 에러 핸들링 강화 | 에러 유형별 메시지, 재시도 버튼, 에러 로깅 | ChatWidget, API 전반 |
| 14 | 증권계좌 유효성 검증 | LIVE 전환 시 KIS API로 계좌 상태 확인 | `portfolio_service.py` |

---

## 4. 프로세스 개선 후 목표 흐름

```
[사용자 채팅 입력]
    ↓
[Intent Router] ─── 도움말 질문 ──→ [HelpFlow] → 사용법 안내
    ↓ 전략 요청
[GO100 전용 채팅 페이지] (/go100/chat - GO100 레이아웃 유지)
    ↓ POST /api/go100/ai/chat
[BaseOrchestrator]
    ├─ UNDERSTAND → DESIGN → DRAFT INSERT
    ├─ AUTO BACKTEST (최대 5+1회)
    └─ AUTO STATUS TRANSITION → BACKTESTED  ← [개선: 자동 전환]
    ↓
[전략 생성 완료 알림]
    ↓ 자동 이동
[GO100 전략 상세 페이지] (/go100/strategies/{id})  ← [개선: 전용 페이지]
    ├─ 백테스트 결과 확인
    ├─ 파라미터 미세조정 + 재백테스트  ← [개선: TODO 구현]
    └─ "모의거래 시작" 버튼
    ↓
[모의거래] → [스케줄러 자동 매매] → [결과 확인]
    ↓
[실거래 전환] (계좌 유효성 검증 포함)  ← [개선: 검증 추가]
    ↓
[실거래 자동 매매]
```

---

## 5. 우선순위 요약

```
긴급도   ████████████████████████████████
CRITICAL  [C-1] 채팅 리다이렉트    → Phase 1
          [C-2] 상세 페이지 미구현  → Phase 1
          [C-3] 하드코딩 user_id   → Phase 1
          [C-4] 중복 저장 위험     → Phase 1

HIGH      [H-1] 백테스트 연동      → Phase 2
          [H-2] 백테스트 재시도     → Phase 2
          [H-3] DB 제약조건        → Phase 2
          [H-4] 세션 관리          → Phase 2
          [H-5] 상세 TODO 구현     → Phase 2

MEDIUM    [M-1] 도움말 기능        → Phase 3
          [M-2] 상태 자동 전환      → Phase 2
          [M-3] 네비게이션 정리     → Phase 3

LOW       [L-1] 에러 메시지         → Phase 3
          [L-2] 계좌 검증           → Phase 3
```

---

## 6. 참고 파일 목록

### Backend 핵심 파일
| 파일 | 역할 |
|------|------|
| `backend/app/routers/go100/strategy_router.py` | 전략 API 라우터 |
| `backend/app/services/go100/strategy/card_service.py` | 카드 CRUD 서비스 |
| `backend/app/services/go100/backtest/backtest_service.py` | 백테스트 실행 |
| `backend/app/services/go100/portfolio/portfolio_service.py` | 포트폴리오 관리 |
| `backend/app/services/go100/risk/position_sizing.py` | 포지션 사이징 |
| `backend/app/services/go100/scheduler/go100_scheduler.py` | 일일 스케줄러 |
| `backend/app/services/go100/ai/base_orchestrator.py` | AI 오케스트레이터 |

### Frontend 핵심 파일
| 파일 | 역할 |
|------|------|
| `frontend/src/app/(protected)/go100/chat/page.tsx` | AI 대화 페이지 (현재 리다이렉트) |
| `frontend/src/app/(protected)/go100/strategies/page.tsx` | 내 전략 목록 |
| `frontend/src/app/(protected)/go100/strategies/[id]/page.tsx` | 전략 상세 (현재 리다이렉트) |
| `frontend/src/go100/components/ChatWidget.tsx` | 채팅 위젯 |
| `frontend/src/go100/components/StrategyCardDetail.tsx` | 전략 상세 컴포넌트 |
| `frontend/src/go100/components/StrategyResultCard.tsx` | 결과 카드 |
| `frontend/src/go100/api/go100Api.ts` | GO100 API 클라이언트 |

---

**보고 완료.**
