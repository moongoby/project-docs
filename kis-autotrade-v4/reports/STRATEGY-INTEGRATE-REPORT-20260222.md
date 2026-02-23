# CUR-GO100-STRATEGY-INTEGRATE 보고서

**Task ID**: CUR-GO100-STRATEGY-INTEGRATE  
**Branch**: phase-2c-command-center  
**Date**: 2026-02-22  
**Rule**: go100_* 파일/테이블만 수정, V4.1 코드 수정 최소화

---

## 1. 백업 파일 경로 및 크기

- **로컬 환경**: DB 접속 계정(go100user/go100db)이 프로젝트 설정에 없어, 본 터미널에서 `pg_dump` 실행 불가(Peer authentication failed).
- **실서버 적용 시** 아래 명령으로 백업 후 진행 권장:
  ```bash
  pg_dump -U go100user -d go100db -F c -f /tmp/backup_STRATEGY_INTEGRATE_$(date +%Y%m%d_%H%M%S).dump
  ls -la /tmp/backup_STRATEGY_INTEGRATE_*.dump
  ```

---

## 2. 수정 전 상태 (코드/API 기준)

| 항목 | 내용 |
|------|------|
| V4.1 전략카드 API | `GET /api/v1/strategy-cards` (list), `GET /api/v1/strategy-cards/catalog` (카탈로그) — `strategy_cards` 테이블 조회 |
| GO100 전략카드 API | `GET /api/go100/strategy-cards` — `go100_strategy_cards` 테이블 조회 |
| 전략카드 페이지 | `/strategy-cards` — `useStrategyCatalog()` 만 사용, V4.1 카드만 표시 |
| strategy_cards / go100_strategy_cards | 별도 테이블 (V4.1 백엔드 수정 없이 방안 B 채택) |

---

## 3. 수정 파일 목록 및 각 변경 내용

| 파일 | 변경 요약 |
|------|------------|
| `frontend/src/types/index.ts` | `StrategyCardDisplay`에 `source?: "v4" \| "go100"` 추가. CUR-GO100-STRATEGY-INTEGRATE 주석 추가. |
| `frontend/src/app/(protected)/strategy-cards/page.tsx` | 첫 줄 주석 `// CUR-GO100-STRATEGY-INTEGRATE, 2026-02-22` 추가. `getStrategyCards`(go100 API) 호출용 `useQuery`, `mapGo100ToDisplay` 도입. V4.1 catalog 카드와 GO100 카드 병합(`cards = [...v41Cards, ...go100Cards]`). "내 전략" 탭에 GO100 카드 포함(`source === "go100" && is_active`). 타입 필터에 "GO100 AI" 옵션 추가. 표시 개수 `displayTotalCount` 사용. 카드 key에 `go100-${id}` 구분. |
| `frontend/src/components/strategy/StrategyCard.tsx` | 첫 줄 주석 `// CUR-GO100-STRATEGY-INTEGRATE, 2026-02-22` 추가. `getTypeBadge(type, source)`에 `source === "go100"` 시 "GO100 AI" 파란 뱃지 반환. GO100 카드 좌측 테두리 파란색. GO100일 때 푸터에 "상세보기 →"만 표시하고 `/go100/strategies/${card.id}` 링크로 이동. GO100 카드 전체를 `Link`로 감싸 클릭 시 상세 페이지 이동. |

---

## 4. user_id 정합성 수정 여부

- **수정 안 함.** 방안 B(프론트에서 두 API 병합)만 적용.
- 실서버에서 CEO(moongoby@gmail.com)의 GO100 카드가 "내 전략"에 안 보이면, 아래로 일괄 정합성 수정 후 재검증:
  ```bash
  psql -U go100user -d go100db -c "
    UPDATE go100_strategy_cards
    SET user_id = (SELECT id FROM users WHERE email='moongoby@gmail.com')
    WHERE user_id != (SELECT id FROM users WHERE email='moongoby@gmail.com')
    AND go100_card_id IN (13, 14, 15);
  "
  ```
- 참고: GO100 API는 이미 현재 로그인 사용자(`get_current_user`) 기준으로 카드만 반환하므로, 동일 사용자면 별도 UPDATE 없이 표시됨.

---

## 5. 빌드 결과 (tsc, npm build)

| 단계 | 결과 |
|------|------|
| `npx tsc --noEmit` | 성공 (exit 0) |
| `npm run build` (Next.js) | 성공 (exit 0), `/strategy-cards` 라우트 포함 |

---

## 6. 검증 결과 (API 응답, 브라우저 확인)

- **API**: 실서버에서 `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/strategy-cards`, `curl -s http://localhost:8002/health` 로 확인 권장.
- **브라우저**: `go100.newtalk.kr/strategy-cards` 접속 후 아래 확인:
  1. V4.1 카드 + GO100 카드(13, 14, 15) 총 개수 표시.
  2. GO100 카드에 "GO100 AI" 파란색 뱃지 표시.
  3. "내 전략" 탭에서 CEO의 GO100 카드 3개 표시.
  4. GO100 카드 클릭 시 `/go100/strategies/[id]` 상세 페이지 정상 로드.

---

## 7. 수정 후 상태 (표시되는 카드 수)

- **전체 전략**: V4.1 catalog 카드 수 + GO100 API 반환 카드 수 (예: 52 + 3 = 55개).
- **내 전략**: V4.1에서 활성화한 카드 + 현재 사용자 소유 GO100 카드.
- **타입 필터 "GO100 AI"**: GO100 카드만 필터링.

---

## 8. 컴플라이언스 체크리스트

- [ ] go100_strategy_cards 기존 59건 유지 (실서버 DB 확인)
- [ ] v4_positions OPEN 5건 유지 (실서버 DB 확인)
- [x] V4.1 백엔드 파일 수정 없음
- [x] .env/.bak 커밋 없음
- [x] 파일 헤더 주석 포함 (strategy-cards/page.tsx, StrategyCard.tsx, types index StrategyCardDisplay)

---

## 9. 커밋 해시

- `07c033161f170fb5c743c4066dd3927e4a6408b3`
- 메시지: `feat: CUR-GO100-STRATEGY-INTEGRATE V4.1 전략카드 페이지에 GO100 카드 통합 표시`

---

## 10. STEP 0/1 요약 (참고)

- **V4.1 전략카드**: `strategy_cards` 테이블, `/api/v1/strategy-cards`, `/api/v1/strategy-cards/catalog`.
- **GO100 전략카드**: `go100_strategy_cards` 테이블, `/api/go100/strategy-cards` (list_cards, 사용자별).
- **통합 방식**: 방안 B — 프론트엔드에서 catalog + go100 목록 각각 호출 후 병합, GO100 카드에 `source: 'go100'` 및 뱃지·상세 링크 적용.
