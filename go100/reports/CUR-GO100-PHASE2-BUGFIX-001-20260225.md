# CUR-GO100-PHASE2-BUGFIX-001 보고서
**작성일:** 2026-02-25 (KST)  
**작업 ID:** CUR-GO100-PHASE2-BUGFIX-001  
**브랜치:** fix/CUR-GO100-PHASE2-BUGFIX-001 → phase-2c-command-center  

---

## 0. 사전 확인 결과 (2026-02-25 실행)

| 이슈 | 확인 명령 | 결과 | 조치 |
|------|-----------|------|------|
| **ISS-012** | `grep DEFAULT_USER_ID\|useAuthStore ChatWidget.tsx` | `DEFAULT_USER_ID` 없음, `useAuthStore` 이미 사용 중 (L18, L48), `user?.user_id` 사용 | **기 반영** → SKIP |
| **ISS-011** | `cat go100/chat/page.tsx`, `grep redirect\|router.push.*llm` | 리다이렉트 없음, `ChatWidget mode="fullscreen"` 임베드, 헤더 ISS-011 fix 존재 | **기 반영** → SKIP |
| **ISS-013** | `grep retry backtest_router.py` | `@router.post("/retry/{run_id}")`, `retry_backtest` 존재 (L115~151) | **기 반영** → SKIP |

**결론:** 3건 모두 이미 반영됨. 본 작업에서 **추가 코드 수정 없음**. 검증 grep 재확인 및 보고서·문서레포 push만 수행.

---

## 1. 개요
Phase 2 미해결 이슈 ISS-011, ISS-012, ISS-013 수정.  
보호 파일(auth-store.ts, client.ts) 변경 없음. kis-v41-* 서비스 재시작 금지 준수.

---

## 2. ISS-012 (HIGH) — ChatWidget DEFAULT_USER_ID 하드코딩

### 원인
- `DEFAULT_USER_ID = 1` 상수로 인해 모든 사용자 전략이 user_id=1로 생성됨.

### 수정 내용
- **파일:** `frontend/src/go100/components/ChatWidget.tsx`
- `useAuthStore()`에서 `user` 조회, `user?.user_id`를 API 호출 시 사용.
- `DEFAULT_USER_ID` 상수 제거(이미 제거된 상태 정리 및 헤더 추가).
- 미로그인(`user === null`) 시 위젯(FAB/패널) 미렌더.
- 헤더: `// CUR-GO100-PHASE2-BUGFIX-001, 2026-02-25 — ISS-012 fix`

### 검증
- `grep DEFAULT_USER_ID ChatWidget.tsx` → 없음.
- `grep useAuthStore ChatWidget.tsx` → 있음.

---

## 3. ISS-011 (MEDIUM) — /go100/chat 리다이렉트

### 원인
- /go100/chat 접근 시 /llm으로 리다이렉트되어 GO100 사이드바가 사라짐.

### 수정 내용
- **파일:** `frontend/src/app/(protected)/go100/chat/page.tsx`
- 기존에 이미 전용 페이지로 구현됨(리다이렉트 없음). 헤더만 추가.
- `ChatWidget mode="fullscreen"`으로 GO100 레이아웃 내 채팅만 렌더.
- 헤더: `// CUR-GO100-PHASE2-BUGFIX-001, 2026-02-25 — ISS-011 fix`

### 검증
- `grep -rn "redirect\|router.push.*llm" frontend/src/app/(protected)/go100/chat/` → 없음.

---

## 4. ISS-013 (MEDIUM) — 백테스트 재시도 API

### 원인
- 백테스트 실패 시 재시도 불가, 새 전략/동일 설정으로 다시 실행해야 함.

### 수정 내용

#### 백엔드
- **파일:** `backend/app/routers/go100/backtest_router.py`
  - `data_gate_check_readiness` import 추가: `from backend.app.services.go100.backtest.data_gate import check_readiness as data_gate_check_readiness`
  - `POST /api/go100/backtest/retry/{run_id}` 추가.
  - 처리: run_id 조회, status가 FAILED/ERROR만 허용, 동일 파라미터로 새 run 생성, 기존 run을 RETRIED로 업데이트, 백그라운드 실행.
  - 응답: `{"new_run_id": ..., "original_run_id": run_id, "status": "running"}`

- **파일:** `backend/app/services/go100/backtest/backtest_service.py`
  - `get_run_for_retry(user_id, run_id, db)` → Go100BacktestRequest 반환.
  - `update_run_status(run_id, status, db)` (RETRIED 업데이트용).

#### 프론트엔드
- **파일:** `frontend/src/go100/api/go100Api.ts`
  - `retryBacktest(runId)` 추가. POST `/api/go100/backtest/retry/{runId}` 호출.
- **파일:** `frontend/src/app/(protected)/backtest/page.tsx`
  - GO100 백테스트 결과가 FAILED/ERROR일 때 카드에 에러 메시지 + "재시도" 버튼 표시.
  - 재시도 클릭 시 `retryBacktest(go100Result.run_id)` 호출 후 `go100RunId`를 새 run_id로 설정하여 폴링.
- **파일:** `frontend/src/go100/types/backtest.ts`
  - `BacktestStatus`에 `'ERROR'`, `'RETRIED'` 추가.

### 검증
- `grep -rn "retry" backend/app/routers/go100/backtest_router.py` → retry 엔드포인트 존재.

---

## 5. 검증 요약
| 항목 | 결과 |
|------|------|
| DEFAULT_USER_ID 제거 | OK |
| useAuthStore 사용 | OK |
| /go100/chat 리다이렉트 없음 | OK |
| retry API 존재 | OK |
| npx tsc --noEmit | PASS |
| npm run build | PASS |
| pre-commit-check.sh | PASS |
| 보호 파일 변경 | 없음 |

---

## 6. 수정 파일 요약
| 파일 | 이슈 | 비고 |
|------|------|------|
| frontend/src/go100/components/ChatWidget.tsx | ISS-012 | user_id 동적, 미로그인 미렌더 |
| frontend/src/app/(protected)/go100/chat/page.tsx | ISS-011 | 헤더 추가(전용 페이지 유지) |
| backend/app/routers/go100/backtest_router.py | ISS-013 | retry 엔드포인트, data_gate import |
| backend/app/services/go100/backtest/backtest_service.py | ISS-013 | get_run_for_retry, update_run_status |
| frontend/src/go100/api/go100Api.ts | ISS-013 | retryBacktest, checkBacktestReadiness import(기존 사용처) |
| frontend/src/app/(protected)/backtest/page.tsx | ISS-013 | 재시도 버튼, checkBacktestReadiness import |
| frontend/src/go100/types/backtest.ts | ISS-013 | BacktestStatus에 ERROR, RETRIED |

---

## 7. ISSUES.md 반영
- ISS-011, ISS-012, ISS-013 → "해결됨" 섹션으로 이동, 해결 커밋 해시 기록.

---

**해결 커밋:** phase-2c-command-center 머지 커밋 (fix 브랜치 머지)
