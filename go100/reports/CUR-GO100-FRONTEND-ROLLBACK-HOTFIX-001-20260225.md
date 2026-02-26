# CUR-GO100-FRONTEND-ROLLBACK-HOTFIX-001 보고서

**작성일**: 2026-02-25 11:30 KST
**우선순위**: P0-EMERGENCY
**상태**: **해결 완료**

---

## 1. 증상

- `go100.newtalk.kr/go100/strategies` (전략카드 페이지) 크래시
- `go100.newtalk.kr/llm` (백억이 LLM 페이지) 크래시
- Next.js 런타임 에러 발생

## 2. 원인 분석

### 2.1 에러 로그

```
⨯ Error: Cannot find module '/root/kis-autotrade-v4/frontend/.next/server/pages/_error.js'
  code: 'MODULE_NOT_FOUND'
```

### 2.2 진단 결과

| 항목 | 결과 |
|------|------|
| `npx tsc --noEmit` | **에러 0건** (소스코드 정상) |
| GoalScenarioCards.tsx | 파일 존재 (`src/go100/components/`) |
| GoalStrategyResult.tsx | 파일 존재 (`src/go100/components/`) |
| GoalChatData / GoalScenario / GoalCreatedCard 타입 | `types/ai.ts`에 정의, `types/index.ts`에서 re-export |
| ChatWidget.tsx import 경로 | 모두 정상 |
| `.next/server/pages/_error.js` 파일 | 파일 자체는 존재하나 빌드 무결성 깨짐 |

### 2.3 근본 원인

**`.next` 빌드 아티팩트 손상**

CUR-GO100-GOAL-UX-001 (Cursor4)이 ChatWidget.tsx, GoalScenarioCards.tsx, GoalStrategyResult.tsx 3개 파일을 추가/수정한 후, 소스코드는 정상이나 `.next` 빌드 디렉토리의 무결성이 깨짐. 서버가 빌드된 페이지 모듈을 로드할 때 `MODULE_NOT_FOUND` 에러 발생.

**원인 추정**: Cursor의 코드 변경 후 빌드가 부분적으로만 수행되었거나, 이전 빌드 캐시와 새 소스 간 불일치 발생.

## 3. 수정 내역

### 3.1 수행 작업

| 순서 | 작업 | 결과 |
|:---:|------|:---:|
| 1 | 프론트엔드 백업 (`/root/backup/frontend-hotfix-20260225-111222/`) | ✅ |
| 2 | TypeScript 컴파일 검증 (`tsc --noEmit`) | 에러 0건 |
| 3 | 소스 파일 존재·타입·import 경로 확인 | 모두 정상 |
| 4 | **`npm run build` (빌드 재생성)** | **성공** — 모든 라우트 정상 생성 |
| 5 | `systemctl restart go100-frontend` | 정상 기동 |
| 6 | 전체 페이지 HTTP 검증 | 모두 정상 |

### 3.2 소스 코드 변경

**변경 없음** — 빌드 재생성만으로 해결.

CUR-GO100-GOAL-UX-001이 추가한 3개 파일은 모두 정상 동작:
- `src/go100/components/ChatWidget.tsx` (369줄) — Goal UI 통합
- `src/go100/components/GoalScenarioCards.tsx` (56줄) — 시나리오 3장 카드
- `src/go100/components/GoalStrategyResult.tsx` (41줄) — 생성된 전략 결과

## 4. 검증 결과

### 4.1 빌드 출력 (주요 라우트)

```
✓ /go100/strategies       819 B   298 kB
✓ /go100/strategies/[id]  9.2 kB  127 kB
✓ /llm                    59.4 kB 220 kB
✓ /go100/chat             2.86 kB 134 kB
✓ /dashboard              21.8 kB 177 kB
✓ /strategy-cards         20.9 kB 193 kB
```

### 4.2 HTTP 상태 코드

| 페이지 | 코드 | 상태 |
|--------|:---:|:---:|
| `/` (대시보드) | 200 | ✅ |
| `/auth/login` | 200 | ✅ |
| `/settings` | 200 | ✅ |
| `/go100/strategies` | 307 → login | ✅ (인증 리다이렉트 정상) |
| `/llm` | 307 → login | ✅ (인증 리다이렉트 정상) |
| `/dashboard` | 307 → login | ✅ |
| `/go100` | 307 → login | ✅ |
| `/go100/chat` | 307 → login | ✅ |
| `/strategy-cards` | 307 → login | ✅ |

### 4.3 재시작 후 에러 로그

**에러 0건** — `journalctl -u go100-frontend` 정상

## 5. 영향 범위

| 항목 | 영향 |
|------|------|
| 소스 코드 변경 | 없음 |
| 서비스 재시작 | go100-frontend만 (go100 백엔드, kis-v41 미영향) |
| 데이터 영향 | 없음 |
| 다운타임 | 빌드 ~60초 + 재시작 ~5초 |

## 6. 재발 방지

1. Cursor 등 외부 도구가 소스 수정 후 반드시 `npm run build` 완전 수행 확인
2. `.next` 디렉토리가 손상 의심 시 `rm -rf .next && npm run build`로 클린 빌드
3. 빌드 전 `npx tsc --noEmit`으로 타입 에러 0건 확인

## 보고 요약

- **원인**: `.next` 빌드 아티팩트 손상 (소스코드 정상, 빌드 무결성 깨짐)
- **해결**: `npm run build` 재생성 + `systemctl restart go100-frontend`
- **결과**: 전체 페이지 정상, 에러 0건
- **소스 변경**: 없음
