# CUR-GO100-CARD-REDESIGN-FE 보고서
작업일: 2026-02-22

## GO100 메뉴 삭제
- **삭제한 메뉴 항목**: 사이드바 `navMain` 배열에서 `{ href: "/go100", label: "GO100", icon: Sparkles }` 항목 주석 처리
- **수정 파일**: `frontend/src/components/layout/Sidebar.tsx`
- **유지**: `/go100/*` 라우트, `Go100Sidebar.tsx` 파일은 삭제하지 않음. 상단 로고 텍스트 "GO100" 유지.
- 사이드바에서 GO100 메뉴 링크 미표시 확인됨.

## 전략카드 탭 수정
- **"전체 전략"**: `tab=all` → `GET /api/v1/strategy-cards/catalog?tab=all` → featured GO100 카드만 표시
- **"내 전략"**: `tab=my` → `GET /api/v1/strategy-cards/catalog?tab=my` → 로그인 사용자 GO100 카드만 표시
- 탭 전환 시 `useStrategyCatalog(activeTab)`로 API 재호출
- 카드 개수: 전체 전략 → "전략카드 N개", 내 전략 → "내 전략 N개" (실제 반환 건수 기준)
- V4.1 전략은 백엔드에서 제외됨 (catalog API가 GO100 전용 응답)

## 수정 파일 목록
| 파일 | 변경 요약 |
|------|-----------|
| `frontend/src/components/layout/Sidebar.tsx` | GO100 nav 항목 주석, Sparkles import 제거, 헤더 주석 |
| `frontend/src/lib/api/strategy-cards.ts` | `getCatalog(tab: "all" \| "my")`, URL에 `?tab=${tab}` 추가 |
| `frontend/src/lib/hooks/useStrategyCards.ts` | `useStrategyCatalog(tab)` 추가, queryKey에 tab 포함, queryFn에서 getCatalog(tab) 호출 |
| `frontend/src/app/(protected)/strategy-cards/page.tsx` | activeTab state "all"\|"my", useStrategyCatalog(activeTab), 카드 소스 API 전용, 개수 문구 분기 |
| `frontend/src/app/(protected)/trade/page.tsx` | catalog useQuery에 `queryFn: () => getCatalog("all")` 적용 (getCatalog(tab) 시그니처 호환) |

## 빌드 결과
- `npx tsc --noEmit`: 성공 (0 errors)
- `npm run build`: 성공 (Next.js 14.2.35)

## 컴플라이언스
- [x] V4.1 핵심 파일 수정 최소화 (사이드바·전략카드·훅·API·trade 페이지만)
- [x] .env / .bak 커밋 없음
- [x] 수정 파일 헤더에 `// CUR-GO100-CARD-REDESIGN-FE, 2026-02-22` 포함

## 서비스 확인
- `sudo systemctl restart go100-frontend` 후
- `curl strategy-cards`: 307 (인증 리다이렉트 정상)
- `curl dashboard`: 307 (인증 리다이렉트 정상)

## 커밋
- 메시지: `feat: CUR-GO100-CARD-REDESIGN-FE - GO100 메뉴 삭제 + 전략카드 탭 GO100 전용`
- 커밋 해시: `af0dbf5f`
