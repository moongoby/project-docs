# 로그인 인사·브리핑 반영 완료 보고

**작성일**: 2026-02-24  
**참조 기획**: `report/LOGIN-GREETING-AND-BRIEFING-PLAN-20260224.md`

---

## 1. 반영 요약

| 항목 | 내용 |
|------|------|
| **인사** | 로그인 성공 후 대시보드 진입 직후 1회 **토스트**로 시간대별 인사 + 사용자명 + "오늘의 브리핑을 확인해 보세요." |
| **브리핑** | 대시보드 상단 **"오늘의 브리핑"** 카드 1블록(2~3줄): 포트폴리오 한 줄, 자동매매/전략 상태, 계좌 미연결 시 추천 액션 |
| **노출 조건** | `sessionStorage.loginJustNow` 플래그로 로그인 직후 1회만 토스트 + 브리핑 카드 노출, 이후 제거 |

---

## 2. 변경 파일

### 2.1 Auth 콜백 — 로그인 직후 플래그 설정

**파일**: `frontend/src/app/auth/callback/page.tsx`

- `getMe()` 및 `login()` 성공 후, `router.replace("/dashboard")` **직전**에  
  `sessionStorage.setItem("loginJustNow", "1")` 호출 추가.
- 로그인 실패 시에는 플래그를 설정하지 않음.

### 2.2 오늘의 브리핑 카드 컴포넌트 (신규)

**파일**: `frontend/src/components/dashboard/TodayBriefingCard.tsx`

- **역할**: 로그인 직후에만 보이는 "오늘의 브리핑" 섹션.
- **입력**: `portfolio`(total_value, total_profit_rate 등), `system`(orchestrator_state, active_strategies), `accountsTotal`.
- **표시 내용** (2~3줄, summary 기반):
  1. 포트폴리오: `총 자산 ₩xxx, 오늘 +x.x%예요.` (자산 0이면 "아직 보유 자산이 없어요.")
  2. 자동매매/전략: `자동매매가 켜져 있어요.` / `자동매매는 꺼져 있어요.` / `활성 전략 N개가 돌아가고 있어요.`
  3. 계좌 0개일 때: `계좌 연결하면 실거래를 시작할 수 있어요.` + "계좌 연결하기 →" 링크(`/accounts`).
- **접근성**: `<section aria-label="오늘의 브리핑">`, `<h2>오늘의 브리핑</h2>` 사용.

### 2.3 대시보드 페이지 — 토스트 인사 + 브리핑 노출

**파일**: `frontend/src/app/(protected)/dashboard/page.tsx`

- **상수/헬퍼**: `LOGIN_JUST_NOW_KEY = "loginJustNow"`, `getTimeGreetingForToast()` (시간대별 인사 문구 4종).
- **상태**: `showBriefing`(boolean), `loginGreetingDone`(useRef로 중복 실행 방지).
- **useEffect** (마운트 1회):
  - `sessionStorage.getItem(LOGIN_JUST_NOW_KEY) === "1"`일 때만 동작.
  - `sessionStorage.removeItem(LOGIN_JUST_NOW_KEY)` 후 `setShowBriefing(true)`.
  - `useAuthStore.getState().user`에서 이름 조회, `toast({ title: "${이름}님, ${인사}", description: "오늘의 브리핑을 확인해 보세요." })` 호출.
- **렌더**: `showBriefing === true`일 때만 `<TodayBriefingCard />`를 **BaekogiWelcomeBanner 위**에 렌더.  
  (제목·새로고침 영역 바로 아래, 웰컴 배너 바로 위.)

---

## 3. 동작 흐름

1. 사용자가 소셜 로그인 완료 → `/auth/callback`에서 token 수신, getMe, login, **sessionStorage "loginJustNow" = "1"** 설정 후 `/dashboard`로 replace.
2. 대시보드 마운트 → summary 로드와 무관하게 useEffect에서 "loginJustNow" 확인.
3. "1"이면: 플래그 삭제, `showBriefing = true`, 토스트 노출(이름 + 시간대별 인사 + "오늘의 브리핑을 확인해 보세요.").
4. 대시보드 본문에서 `showBriefing`이 true이므로 "오늘의 브리핑" 카드가 웰컴 배너 위에 한 번 표시.
5. 이후 새로고침 시에는 "loginJustNow"가 없으므로 토스트·브리핑 카드 모두 미노출, 기존 웰컴 배너만 유지.

---

## 4. 검증 포인트

- 로그인 직후 대시보드 진입 시 토스트 1회 + "오늘의 브리핑" 카드 노출.
- 같은 세션에서 대시보드 새로고침 시 토스트·브리핑 카드 미노출.
- 브리핑 문장: 자산 유무, 자동매매 상태(AI_ENABLED 등), 계좌 0개일 때 문구 및 계좌 연결 링크 확인.

---

## 5. 추후 확장 (기획 2·3단계)

- **당일 첫 진입**만 브리핑 표시: `localStorage.lastDashboardDate`로 당일 첫 방문 여부 판별 후 `showBriefing` 제어.
- **백엔드 브리핑 API**: `GET /api/v1/dashboard/briefing`에서 시장 한줄·알림 건수 등 반환 후 카드에 연동.

이상으로 1단계 반영을 완료했다.
