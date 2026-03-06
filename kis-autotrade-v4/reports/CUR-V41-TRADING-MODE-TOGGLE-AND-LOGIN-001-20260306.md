---
project: kis-autotrade-v4
task_id: T-157
completed_at: 2026-03-06 11:00 KST
status: completed
author: Claude Code (Sonnet 4.6) / root
---

# T-157: 실매매/모의 토글 UI 연동 + 로그인 비밀번호 변경 (2026-03-06)

> 실행일시: 2026-03-06 10:30~11:00 KST
> 대상 서비스: go100.newtalk.kr (Next.js 프론트엔드)
> 커밋: fc398d2d (phase-2c-command-center)

---

## 1. 작업 배경

- CEO 요청: go100.newtalk.kr/accounts, /settings 페이지에 실매매/모의투자 온오프 기능 추가 및 실제 API 연동
- 기존 상태: 설정 페이지에 계좌 모드 조회만 가능 (전환 UI 없음), accounts 페이지에 모드 표시 없음
- 실계좌는 OFF 상태로 유지 요청

---

## 2. 구현 내용

### 2-1. `frontend/src/lib/api/trade.ts`
`switchAccountMode()` 함수 추가:
- 엔드포인트: `POST /api/v4/admin/switch-account-mode`
- 파라미터: `{ account_type: "virtual" | "real" }`
- 반환: `{ active_account_type, daily_order_limit, single_stock_max_pct, ... }`

### 2-2. `AccountModeSafetySection.tsx` (settings 페이지)
기존: 계좌 모드 텍스트 조회만 표시
변경: 실매매/모의 **토글 스위치** 실제 연동
- OFF(회색): 모의투자 모드
- ON(빨간색): 실계좌 매매 활성
- 실계좌 → ON 시: 확인 다이얼로그 노출 후 승인 필요
- 실계좌 → OFF 시: 즉시 모의투자로 전환
- 실계좌 ON 상태에서: 일일 한도/단일 주문 상한 설정 폼 노출

### 2-3. `accounts/page.tsx` (accounts 페이지)
`TradingModeBanner` 컴포넌트 추가 (계좌 목록 상단):
- 모의투자: 초록 점 + "모의투자 (OFF)" + 회색 토글
- 실계좌: 빨간 점(pulse) + "실계좌 매매 활성 (ON)" + 빨간 토글
- 토글 직접 조작 가능 (확인 다이얼로그 포함)

---

## 3. DB 처리

```sql
-- 실계좌 OFF
UPDATE v4_account_config SET is_active = false WHERE account_type = 'real';
-- 모의계좌 ON
UPDATE v4_account_config SET is_active = true  WHERE account_type = 'virtual';
```

결과: virtual is_active=true, real 행 없음 (v4_account_config에 virtual 1건만 존재)

---

## 4. 로그인 비밀번호 변경

CEO 요청으로 아래 계정 비밀번호 변경:
- `moongoby@naver.com` (ADMIN)
- `moongoby@gmail.com` (ADMIN)
- 변경 후 로그인 테스트: **OK**

---

## 5. 빌드/배포 결과

| 항목 | 결과 |
|------|------|
| Next.js 빌드 | 성공 (에러 0) |
| go100-frontend 재시작 | active |
| /accounts 응답 | 307 (로그인 리다이렉트 — 정상) |
| /settings 응답 | 200 OK |
| 커밋 | `fc398d2d` → go100.git / phase-2c-command-center |

---

## 6. 완료 체크리스트

- [x] `switchAccountMode()` API 함수 추가 (`trade.ts`)
- [x] `AccountModeSafetySection.tsx` 토글 스위치 실제 연동
- [x] `accounts/page.tsx` 모드 배너 추가
- [x] DB 실계좌 OFF 처리
- [x] 비밀번호 변경 (naver/gmail 2계정)
- [x] 빌드 성공, 서비스 재시작
- [x] git push 완료
