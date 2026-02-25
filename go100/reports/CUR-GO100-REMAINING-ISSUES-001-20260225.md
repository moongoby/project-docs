# CUR-GO100-REMAINING-ISSUES-001 보고서

**작성일**: 2026-02-25 14:35 KST
**우선순위**: P1
**상태**: **완료**
**BATCH-002 WAVE 1-C 검수**: 2026-02-25 15:45 KST — 코드베이스 확인: ISS-011/012/013 반영 완료, ISSUES.md v1.5, retry API 존재.

---

## 1. 목표

ISS-011, ISS-012, ISS-013 3건의 잔여 이슈 해결 및 ISSUES.md v1.5 갱신.

## 2. 이슈별 상태

### ISS-011: /go100/chat GO100 레이아웃

- **상태**: ✅ 이전 커밋에서 수정 완료 (73384772, 2026-02-25)
- **수정 내용**: /go100/chat → GO100 Layout 내 ChatWidget fullscreen 모드
- **이번 작업**: 확인만 (추가 수정 없음)

### ISS-012: ChatWidget DEFAULT_USER_ID 하드코딩 제거

- **상태**: ✅ 완전 수정
- **이전 수정**: `ChatWidget.tsx` — useAuthStore() 동적 user_id (73384772)
- **이번 수정**: 잔존 하드코딩 2곳 추가 수정

| 파일 | 변경 |
|------|------|
| `ChatInterface.tsx` | `DEFAULT_USER_ID = 1` 제거 → `useAuthStore().user?.user_id` 사용 |
| `SettingsRiskSection.tsx` | `DEFAULT_USER_ID = 1` 제거 → `useAuthStore().user?.user_id` 사용 |

#### ChatInterface.tsx 변경사항
```typescript
// Before
const DEFAULT_USER_ID = 1;
// ...
user_id: DEFAULT_USER_ID,

// After
const { user } = useAuthStore();
const userId = user?.user_id;
// 미로그인 체크
if (!userId) {
  setMessages([...prev, { role: "assistant", content: "로그인 후 이용해 주세요." }]);
  return;
}
user_id: userId,
```

#### SettingsRiskSection.tsx 변경사항
```typescript
// Before
const DEFAULT_USER_ID = 1;
user_id: DEFAULT_USER_ID,

// After
const { user } = useAuthStore();
const userId = user?.user_id;
user_id: userId ?? 0,
```

### ISS-013: 백테스트 재시도 구현

- **상태**: ✅ 이전 커밋에서 구현 완료 (73384772, 2026-02-25)
- **구현 내용**:
  - Backend: `POST /backtest/retry/{run_id}` 엔드포인트
  - Frontend: `retryBacktest()` API 함수
  - 검증: FAILED/ERROR만 재시도, DataGate 체크, 소유자 검증
- **이번 작업**: 확인만 (추가 수정 없음)

## 3. ISSUES.md 갱신

- 버전: v1.3 → **v1.5**
- 미해결: 3건 → **0건**
- ISS-011, 012, 013 모두 "해결됨" 섹션으로 이동

## 4. 변경 파일 목록

| 파일 | 작업 |
|------|------|
| `frontend/src/go100/components/ChatInterface.tsx` | DEFAULT_USER_ID 제거, useAuthStore 적용 |
| `frontend/src/go100/components/SettingsRiskSection.tsx` | DEFAULT_USER_ID 제거, useAuthStore 적용 |
| `docs/ISSUES.md` | v1.5 갱신, ISS-011/012/013 해결 처리 |

## 보고 요약

- **ISS-011**: ✅ 기수정 (GO100 Layout 내 채팅 페이지)
- **ISS-012**: ✅ 완전 수정 (ChatWidget + ChatInterface + SettingsRiskSection 3곳 모두 동적 user_id)
- **ISS-013**: ✅ 기구현 (백테스트 재시도 API + 프론트)
- **ISSUES.md**: v1.5 갱신, 미해결 0건
