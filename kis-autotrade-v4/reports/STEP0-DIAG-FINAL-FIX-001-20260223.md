# STEP 0 진단 결과 — CUR-GO100-FINAL-FIX-001 (2026-02-23)

## 0-1. DB 백업
- 파일: `/tmp/backup_FINAL_FIX_001_20260223_104313.dump`
- 상태: 완료

## 0-2. 서비스 상태
- go100: active
- go100-frontend: active
- nginx: active

## 0-3. 포트
- 8002 (go100 백엔드), 3000 (Next.js), 80/443 (nginx) 리스닝 확인

## 0-4. 최근 커밋
- 3c9ba083 config: CUR-GO100-CURSOR-RULES-SPLIT
- 1366d77c rules: 코드 검수 프로세스 반영
- 8529b500 fix: CUR-GO100-HOTFIX-SAVE-500 - strategy_type CHECK에 GO100_AI 추가 + /llm ChatWidget 중복 제거

## 0-5. DB strategy_type CHECK
- `go100_strategy_cards_strategy_type_check`: **이미 'GO100_AI' 포함**
- CHECK ((strategy_type)::text = ANY (ARRAY['CUSTOM','BUILTIN','LLM_GENERATED','SUBSCRIBED','GO100_AI']))
- **STEP 1 ALTER 불필요 (스킵)**

## 0-6. layout.tsx ChatWidget
- usePathname, isLlmPage 사용 중
- `{!isLlmPage && <ChatWidget />}` 조건부 렌더링 적용됨 (로딩/미인증/메인 모두)
- **STEP 2 패치 이미 반영됨 (주석만 FINAL-FIX-001으로 추가)**

## 0-7. ChatWidget.tsx
- 파일 존재: frontend/src/go100/components/ChatWidget.tsx
- chatWithAI: `from "../api"` (go100Api re-export)

## 0-8. go100Api / index
- go100Api.ts: chatWithAI export 있음
- index.ts: export * from './go100Api' → chatWithAI 노출됨

## 0-9. 인증 후 전략 저장 테스트
- 로그인 API 응답: status/detail만 반환 (access_token 없음) → 테스트 계정/엔드포인트 이슈 가능
- 전략 저장 호출 시 401 (유효하지 않은 액세스 토큰)
- **실제 인증 성공 시 201/200 되는지는 브라우저/유효 토큰으로 재검증 필요**

## 0-10. 최근 에러 로그
- KIS Balance API 500 / account_sync WARNING (외부 API 이슈, GO100 전략 저장과 무관)

## 0-11. 프론트엔드 빌드
- BUILD_ID: hBDpgwloT8AeCEqB28dyu
- npm run build: **성공** (ChatWidget 관련 에러 없음)

## 0-12. npm build 로그
- error/failed 없음, 빌드 정상 완료

---
STEP 0 완료. STEP 1은 DB에 GO100_AI 이미 있으므로 스킵. STEP 2는 layout 주석 추가만 수행.
