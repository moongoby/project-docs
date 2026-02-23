# GO100 전방위 조사 보고서 (CUR-GO100-FULL-AUDIT)

**작성일:** 2026-02-23  
**목표:** GO100 서비스 전체 흐름 조사 — 저장/조회/실행 오류 전방위 파악  
**조사 범위:** 코드·DB·라우팅·인증 (코드/DB 변경 없음, 조사만 수행)

---

## 이슈별 원인 분석

### [이슈1] 전체전략 = 내전략 동일하게 보임

- **Catalog API tab 파라미터가 프론트에서 실제로 전달되는가?**  
  **예.** 프론트 `useStrategyCatalog(activeTab)` → `getCatalog(tab)` → `GET /api/v1/strategy-cards/catalog?tab=${tab}`. `activeTab`은 "all" / "my"이며 탭 전환 시 변경되므로 tab이 쿼리스트링에 포함되어 전달된다.
- **tab=all과 tab=my의 백엔드 쿼리가 실제로 다른가?**  
  **예.** `strategy_card_service.list_cards_with_system(..., tab=tab)`에서:
  - `tab=all`: `WHERE is_featured = true AND is_active = true` (go100_strategy_cards), `ORDER BY featured_order ASC, go100_card_id ASC`
  - `tab=my`: `WHERE user_id = :uid AND is_active = true` (effective_uid 적용), `ORDER BY go100_card_id DESC`
- **원인:**  
  - 코드 상 tab 분기는 정상 동작한다.  
  - **동일하게 보이는 현상**은, 현재 DB에 featured 카드 3건이 모두 **동일 user_id(3) 소유**이기 때문으로 추정된다. 즉, 해당 사용자가 "전체 전략"과 "내 전략" 탭에서 같은 3개 카드를 보게 되는 데이터 구성 이슈다.  
  - 추가로, tab=my 시 `effective_uid`는 레거시 users.id일 경우 v4_users.user_id로 변환하는 로직이 있음(CUR-GO100-MY-STRATEGY-FIX). 변환 실패/불일치 시 "내 전략"이 비어 보일 수 있음.

---

### [이슈2] 백테스트에 V4.1 전략만 표시, GO100 전략은 백테스트에만 나옴

- **백테스트 전략 드롭다운 API:**  
  `GET /api/v1/strategy-cards/for-backtest`
- **해당 API가 조회하는 테이블:**  
  **strategy_cards 만** (V4.1). `list_cards_for_backtest()`는 `strategy_cards`만 SELECT하며, `go100_strategy_cards`는 조회하지 않는다.
- **원인:**  
  - 백테스트 페이지는 `getBacktestCards()` → `/for-backtest`를 호출한다.  
  - 백엔드 `list_cards_for_backtest()`는 `strategy_cards` 테이블만 사용하므로, **GO100 전략 카드(go100_strategy_cards)는 드롭다운에 전혀 노출되지 않는다.**  
  - 반면 전략카드 페이지의 Catalog(tab=all/my)는 **go100_strategy_cards만** 사용하므로, GO100 전략은 "전략카드" 화면에만 보이고 "백테스트" 화면 드롭다운에는 안 나오는 구조적 불일치다.

---

### [이슈3] 백억이 전체화면 링크

- **ChatWidget 전체화면 버튼 href/동작:**  
  `router.push("/go100/chat")` (클릭 시 `/go100/chat`으로 이동)
- **올바른 링크:**  
  사이드바 "백억이" 메뉴와 동일하게 **/llm**이어야 한다는 요구사항 기준으로는 **잘못 연결됨.**
- **/go100/chat 페이지 내용:**  
  GO100 전용 "AI 전략 대화" 페이지. `ChatInterface`(GO100 AI 파이프라인: /api/go100/ai/chat)만 렌더링.
- **/llm 페이지 내용:**  
  "백억이" 라벨의 LLM 채팅 페이지. `sendMessageStream`(일반 LLM API), `ChannelSelector`, `StrategyCardSaveButton` 등 전략설계·저장 플로우 포함.
- **원인:**  
  - 위젯 "전체 화면"은 **/go100/chat**으로 연결되어 있고, 사이드바 "백억이"는 **/llm**으로 연결되어 있어 **동일한 "백억이" 진입점이 두 개의 서로 다른 페이지**로 나뉜다.  
  - 기대 동작(백억이 전체화면 = /llm)과 불일치하므로, **ChatWidget의 전체화면 이동을 /llm으로 변경하는 것이 맞다.**

---

### [이슈4] 백억이 전략 저장 미작동 (내 전략 미저장 + 백테스트 미진행)

- **저장 버튼 클릭 시 호출 API:**  
  - **/llm** 페이지의 "전략카드로 저장" 버튼: `StrategyCardSaveButton` → `createCard(body)` → **POST /api/v1/strategy-cards** (V4.1 카드 생성).
- **해당 API가 INSERT하는 테이블:**  
  **strategy_cards** (V4.1). `strategy_card_service.create_card()` → `INSERT INTO strategy_cards ...`.
- **INSERT 시 user_id 값:**  
  `current_user["user_id"]` (JWT sub → get_current_user에서 v4_users.user_id 기준 조회 후 반환).
- **내 전략 탭 조회 시 호출 API:**  
  `GET /api/v1/strategy-cards/catalog?tab=my`
- **SELECT 시 사용 테이블·조건:**  
  **go100_strategy_cards**만 조회, `WHERE user_id = :uid AND is_active = true`.
- **테이블/user_id 불일치 여부:**  
  **불일치.**  
  - "전략카드로 저장"은 **strategy_cards**에만 INSERT.  
  - "내 전략" 탭은 **go100_strategy_cards**만 SELECT.  
  - 따라서 **/llm에서 저장한 카드는 "내 전략"에 절대 나타나지 않는다.**
- **원인:**  
  - **저장 대상 테이블과 조회 대상 테이블이 다르다.**  
  - LLM(백억이) 페이지의 저장은 V4.1용 strategy_cards로만 가고, 전략카드 Catalog "내 전략"은 GO100용 go100_strategy_cards만 보여준다.  
  - 한편 **GO100 채팅(/api/go100/ai/chat)** 파이프라인에서는 오케스트레이터가 `_insert_draft_card()`로 **go100_strategy_cards**에 직접 INSERT하므로, /go100/chat에서 생성된 전략은 "내 전략"에 나타날 수 있다. 즉, "백억이"라고 불리는 두 진입점(/llm vs /go100/chat)의 저장·노출 경로가 서로 다름.

---

### [이슈5] 백테스트 종목선정 오류 (전략에 이미 종목 포함인데 종목 선택 요구)

- **백테스트 실행 시 종목 파라미터:**  
  **필수.** `BacktestRunRequest.stock_codes: List[str]`, min_length=1. API에서 `if not stock_codes: raise HTTPException(400, "stock_codes 필수 1개 이상")`.
- **GO100 카드의 universe_filter:**  
  - GO100 백테스트 서비스(`go100/backtest/backtest_service.py`)는 **go100_strategy_cards**의 `universe_filter`를 읽어 `UniverseEngine`/`advanced_filters`로 종목 집합을 만든다.  
  - 즉 **GO100 전용 백테스트 API**는 카드에 포함된 universe로 자동 종목선정이 가능하다.
- **현재 백테스트 페이지가 사용하는 API:**  
  - **POST /api/v1/backtest/run** (backtest_router).  
  - 이 API는 **strategy_cards**의 `card_id`만 사용하며, `stock_codes`를 **요청 body에서 필수**로 받는다.  
  - **go100_strategy_cards**나 `universe_filter`를 전혀 사용하지 않는다.
- **원인:**  
  - 프론트 백테스트 페이지는 **V4.1 백테스트 API**만 사용하고, 전략도 **for-backtest = strategy_cards**만 쓰므로, **GO100 카드(universe_filter 포함)를 선택해도** 그 API는 GO100 카드를 지원하지 않는다.  
  - 따라서 "종목이 이미 포함된 전략"은 GO100 쪽 설계인데, 현재 백테스트 UI/API는 V4.1 전용이라 **항상 사용자가 종목을 직접 넣어야 하는 구조**다.  
  - GO100 카드를 백테스트하려면 **GO100 백테스트 API**(universe 기반)를 쓰거나, V4.1 API를 확장해 go100_card_id + universe_filter 경로를 지원해야 한다.

---

### [이슈6] 전방위 추가 이슈

- **진입점 이원화:** "백억이"가 /llm(전략설계·저장 버튼)과 /go100/chat(GO100 AI 파이프라인) 두 경로로 나뉘어 있어, 사용자 기대와 혼동 가능.
- **백테스트 API 이원화:**  
  - V4.1: `/api/v1/backtest/run` → strategy_cards + stock_codes 필수.  
  - GO100: go100 백테스트 서비스 → go100_strategy_cards + universe_filter.  
  - 프론트 백테스트 페이지는 V4.1만 사용하므로 GO100 전략은 선택·실행 불가.
- **삭제/비활성화 API:**  
  전략카드 페이지에서 GO100 카드 삭제 시 `deleteCard(card_id)` 등 V4.1 엔드포인트를 호출할 수 있음. GO100 카드는 **go100_strategy_cards**이므로 별도 GO100 삭제 API 또는 통합 처리 필요(현재 전략카드 쪽에서 GO100용 updateStrategyCard 등으로 is_active 처리하는 부분은 확인됨).
- **Catalog tab=my의 user_id:**  
  JWT sub = v4_users.user_id. 레거시 users.id로 로그인한 경우 effective_uid 변환 로직에 의존. 변환 실패 시 "내 전략"이 비어 보일 수 있음.

---

## 라우팅 매핑표

| 사이드바 메뉴 | 링크 경로 | 실제 페이지 파일 | 정상 여부 |
|--|--|--|--|
| 대시보드 | /dashboard | (protected)/dashboard/page.tsx | 정상 |
| 포트폴리오 | /portfolio | (protected)/portfolio/page.tsx | 정상 |
| 계좌관리 | /accounts | (protected)/accounts/page.tsx | 정상 |
| 자동매매 | /trade | (protected)/trade/page.tsx | 정상 |
| 백테스트 | /backtest | (protected)/backtest/page.tsx | 정상(기능은 V4.1만) |
| 리포트 | /reports | (protected)/reports/page.tsx | 정상 |
| 전략카드 | /strategy-cards | (protected)/strategy-cards/page.tsx | 정상 |
| 백억이 | /llm | (protected)/llm/page.tsx | 정상 |
| 알림 | /notifications | (protected)/notifications/page.tsx | 정상 |
| 모니터링 | /monitoring | (protected)/monitoring/page.tsx | 정상 |
| 설정 | /settings | (protected)/settings/page.tsx | 정상 |
| 관리자 | /admin | (protected)/admin/page.tsx | 정상 |

- ChatWidget "전체 화면"만 **/go100/chat**으로 이동하며, 기대값(/llm)과 불일치.

---

## 인증 흐름

| 항목 | 값 |
|--|--|
| 로그인 API | POST /api/v1/auth/login (auth_router), auth_v1.login() |
| JWT sub 기준 테이블 | v4_users (로그인 시 v4_users 조회 또는 레거시 users 조회 후 v4_users INSERT) |
| JWT sub 값 (일반 로그인) | v4_users.user_id (int) |
| get_current_user 반환 user_id | payload["sub"]로 추출한 정수, v4_users에서 email/tier/is_active 조회 후 반환 |
| GO100 AI 저장 시 user_id | current_user["user_id"] (오케스트레이터 process_message 인자) → _insert_draft_card(user_id) → go100_strategy_cards.user_id |
| Catalog tab=my user_id | list_cards_with_system(user_id, ...)의 effective_uid (v4_users.user_id 또는 레거시 users.id→v4_users.user_id 변환) |
| 일관성 | 동일 로그인 사용자에 대해 JWT sub = v4_users.user_id로 통일되어 있으면 일치. 레거시 users.id만 있는 경우 마이그레이션 후 v4_users.user_id 사용. |

---

## 백억이 전략 저장 E2E 흐름

| 단계 | 경로/API | 테이블 | user_id |
|--|--|--|--|
| 1. 대화 메시지 전송 (GO100) | POST /api/go100/ai/chat | - | current_user["user_id"] |
| 2. AI 응답 + 전략 생성 (GO100) | 오케스트레이터 process_message → _insert_draft_card | go100_strategy_cards INSERT | user_id (JWT sub) |
| 3. "전략카드로 저장" 클릭 (LLM 페이지) | StrategyCardSaveButton → createCard() → POST /api/v1/strategy-cards | strategy_cards INSERT | current_user["user_id"] |
| 4. DB INSERT (GO100 파이프라인) | _insert_draft_card | go100_strategy_cards | user_id |
| 4'. DB INSERT (LLM 저장 버튼) | create_card | strategy_cards | current_user["user_id"] |
| 5. "내 전략" 탭 조회 | GET /api/v1/strategy-cards/catalog?tab=my | - | - |
| 6. DB SELECT | list_cards_with_system(tab=my) | go100_strategy_cards | WHERE user_id = effective_uid |

- **결론:** LLM 페이지에서 "전략카드로 저장"한 데이터는 strategy_cards에만 들어가므로 6번 SELECT(go100_strategy_cards) 결과에 포함되지 않아 "내 전략"에 안 보인다.

---

## 백엔드 에러 로그 (최근)

- `journalctl -u go100 --since "2026-02-22"` 기준으로 **card/insert/save 관련 명시적 에러 로그는 없음.**  
- Catalog 요청은 `GET /api/v1/strategy-cards/catalog?tab=all` 및 `?tab=my` 정상 200 처리.  
- for-backtest 요청은 `GET /api/v1/strategy-cards/for-backtest` 200 처리.  
- 로그 상 카드 저장 실패(exception/fail) 메시지는 보이지 않음.

---

## DB 조회 결과 (go100_strategy_cards)

```text
 go100_card_id |             strategy_name             | card_status | user_id | is_active | is_featured
---------------+---------------------------------------+-------------+---------+-----------+-------------
            13 | [스캘핑] 분봉 스캘핑 고변동 대형주    | BACKTESTED  |       3 | t         | t
            14 | [데일리] 대형 우량주 수급 데일리 전략 | BACKTESTED  |       3 | t         | t
            15 | [단기스윙] 섹터모멘텀 외국인수급 스윙 | BACKTESTED  |       3 | t         | t
```

- 세 카드 모두 user_id=3, is_featured=t. 따라서 user_id=3 사용자는 "전체 전략"(featured)과 "내 전략"(my)에서 동일 3개가 보일 수 있음.

---

## 요약 및 수정 제안 방향 (참고)

1. **이슈1:** tab 분기 자체는 정상. 데이터(전체=featured vs 내=user) 구분이 겹치지 않도록 정책/데이터 정리 또는 UI 문구 정리.
2. **이슈2:** for-backtest API 및 백테스트 실행 API에 go100_strategy_cards 병합 또는 별도 GO100 백테스트 진입점 제공.
3. **이슈3:** ChatWidget 전체화면 버튼을 `router.push("/llm")`으로 변경.
4. **이슈4:** (a) LLM "전략카드로 저장"을 go100_strategy_cards에 저장하도록 API/서비스 추가 또는 (b) Catalog tab=my에서 strategy_cards도 함께 조회해 표시. 또는 두 저장 경로를 하나로 통합.
5. **이슈5:** 백테스트 페이지에서 GO100 카드 선택 시 go100_card_id + universe_filter 기반 API 호출 경로 추가하거나, V4.1 run API에 go100_card_id 옵션 및 universe 자동 반영 로직 추가.

이 문서는 **조사만 수행한 결과**이며, 코드/DB 변경은 하지 않았습니다. 위 수정 방향은 통합 수정 지시서 작성 시 참고용입니다.
