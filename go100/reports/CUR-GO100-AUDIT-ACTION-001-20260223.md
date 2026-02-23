# CUR-GO100-AUDIT-ACTION-001 감사 6건 구조이슈 액션플랜

**일시:** 2026-02-23 15:40 KST  
**작성:** Claude PM  
**참고:** GO100-FULL-AUDIT-REPORT-20260223.md

## STEP 1 소스 확인 요약 (2026-02-23)

| 항목 | 위치 | 비고 |
|------|------|------|
| 탭 로직 tab=all / tab=my | `strategy_card_service.list_cards_with_system(tab=)` | tab=all → is_featured, tab=my → user_id (go100_strategy_cards) |
| for-backtest API | `strategy_cards_router GET /for-backtest` → `list_cards_for_backtest()` | **이미** strategy_cards + go100_strategy_cards 병합 반환 (CUR-GO100-UNIFIED-SAVE-BE) |
| ChatWidget fullscreen | `ChatWidget.tsx` | `router.push("/llm")` 사용 중 (정상) |
| /go100/chat 페이지 | `go100/chat/page.tsx` | `router.replace("/llm")` 리다이렉트 적용됨 |
| 전략카드 저장 | LLM → POST /api/v1/strategy-cards → strategy_cards INSERT | Catalog "내 전략"은 go100_strategy_cards만 조회 → 불일치 |
| GO100 저장 | go100 AI 파이프라인 → go100_strategy_cards INSERT | "내 전략"에만 노출 |
| stock_codes / universe_filter | backtest run API는 stock_codes 필수; GO100 카드는 universe_filter | V4.1 API는 universe 미지원 |
| 백억이 진입점 | Sidebar/BottomNav: /llm; Go100Sidebar/DashboardContent: /go100/chat | /go100/chat은 리다이렉트로 /llm 이동 |

---

## 이슈별 액션플랜

### Issue 1: 전략카탈로그 탭 중복 카드
- **현상:** tab=all, tab=my 모두 동일 featured 카드 3건 표시
- **원인:** featured 카드 user_id=3이 로그인 사용자와 동일
- **액션:** featured 카드를 admin 계정(user_id=1)으로 이관하거나, tab=my에서 featured 제외
- **우선순위:** P3 (기능에 영향 없음)

### Issue 2: 백테스트 드롭다운 GO100 카드 미노출
- **현상:** for-backtest API가 strategy_cards만 조회 (감사 당시)
- **액션:** for-backtest API에 go100_strategy_cards UNION 추가
- **코드 확인:** `list_cards_for_backtest()`에 이미 go100_strategy_cards 병합 구현됨. 미노출 시 프론트/캐시/권한 추가 검증 권장.
- **우선순위:** P2

### Issue 3: ChatWidget fullscreen 라우트 오류
- **현상:** /go100/chat으로 이동 (정상: /llm)
- **액션:** router.push('/go100/chat') → router.push('/llm') 변경
- **코드 확인:** ChatWidget.tsx는 이미 `router.push("/llm")` 사용. Go100Sidebar/DashboardContent 등 링크는 여전히 `/go100/chat` → 리다이렉트 페이지에서 /llm으로 이동하므로 동작은 통일됨. 일관성을 위해 링크를 /llm으로 통일 권장.
- **우선순위:** P2 (1줄 수정)

### Issue 4: 전략카드 저장 테이블 불일치
- **현상:** LLM에서 저장 → strategy_cards, 내 전략 탭 → go100_strategy_cards 조회
- **액션:** LLM 저장 시 go100_strategy_cards에 INSERT하도록 변경
- **우선순위:** P1 (핵심 기능 불일치)

### Issue 5: GO100 백테스트 stock_codes 필수
- **현상:** GO100 카드는 universe_filter 사용, V4.1 API는 stock_codes 필수
- **액션:** GO100 전용 백테스트 엔드포인트 추가 또는 V4.1 API 확장
- **우선순위:** P3 (설계 필요)

### Issue 6: 백억이 진입점 중복 등 기타
- **현상:** /llm과 /go100/chat 이중 진입
- **액션:** /go100/chat을 /llm으로 리다이렉트, 사이드바 메뉴 통합
- **코드 확인:** /go100/chat 페이지에서 이미 router.replace("/llm") 적용. Go100 영역 링크를 /llm으로 통일하면 UX 일관성 확보.
- **우선순위:** P3

---

## 키움 장중 테스트 준비
- 스크립트: `/tmp/kiwoom_market_order_test.sh`
- 실행 시점: 2026-02-24 09:00~15:30 KST
- 대상: account_id=4 (81201280, 모의)
- 종목: 삼성전자 005930, 1주, 시장가
- 스크립트 내용: DB accounts에서 계좌 정보 조회 → KiwoomBrokerClient 인증 → 잔고 조회 → 시장가 매수 1주

---

## Git
- 코드: https://github.com/moongoby/go100 (phase-2c-command-center)
- 문서: https://github.com/moongoby/project-docs (master)
