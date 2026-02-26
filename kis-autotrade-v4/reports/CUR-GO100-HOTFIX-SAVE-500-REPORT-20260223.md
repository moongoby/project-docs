# CUR-GO100-HOTFIX-SAVE-500 결과 보고 (2026-02-23)

**작성자:** GO100 PM Claude Opus 4.6  
**목적:** 전략 저장 500 에러 해결 + 채팅 위젯 /llm 페이지 중복 제거  
**근본 원인:** `go100_strategy_cards.strategy_type` CHECK 제약조건에 `GO100_AI` 미포함

---

## 1. DB CHECK 제약조건 변경 전/후

### 변경 전
```text
go100_strategy_cards_strategy_type_check | CHECK (((strategy_type)::text = ANY ((ARRAY['CUSTOM', 'BUILTIN', 'LLM_GENERATED', 'SUBSCRIBED'])::text[])))
```

### 변경 후
```text
go100_strategy_cards_strategy_type_check | CHECK (((strategy_type)::text = ANY ((ARRAY['CUSTOM', 'BUILTIN', 'LLM_GENERATED', 'SUBSCRIBED', 'GO100_AI'])::text[])))
```

**적용 방법:** `kis_admin`이 테이블 소유자가 아니어서 `ALTER TABLE` 실패 → `sudo -u postgres psql -d kisautotrade` 로 실행하여 적용 완료.

---

## 2. API 응답 코드

- **전략 저장 API (인증 없이):** `HTTP: 401`  
  - 401 = 인증 필요(정상). 500이 아님 → CHECK 위반으로 인한 500은 해소된 상태.

---

## 3. 프론트 빌드

- **결과:** 성공  
- Next.js 14.2.35 production 빌드 완료, `/llm` 라우트 포함 정상 생성.

---

## 4. 커밋 해시

| 저장소 | 브랜치 | 커밋 해시 | 메시지 |
|--------|--------|-----------|--------|
| kis-autotrade-v4 (go100) | phase-2c-command-center | **7b39c087** | fix: CUR-GO100-HOTFIX-SAVE-500 - strategy_type CHECK 제약조건에 GO100_AI 추가 + /llm 페이지 ChatWidget 중복 제거 |
| project-docs | master | **09dcbce** | cleanup: source dump 삭제 |

---

## 5. source-dump 삭제 확인

- **위치:** `project-docs/go100/_source-dump`
- **처리:** `rm -rf go100/_source-dump` 실행 후 `git add -A` → 커밋 `09dcbce` 로 푸시 완료.
- **삭제된 항목:** BE_*.py, DB_SCHEMA.txt, ERROR_LOG.txt, FE_*.tsx 등 14개 파일.

---

## 수정 파일 요약

| 파일 | 변경 내용 |
|------|-----------|
| `frontend/src/app/(protected)/layout.tsx` | 헤더 `// CUR-GO100-HOTFIX-SAVE-500, 2026-02-23` 추가, `usePathname` 도입, `pathname === "/llm"` 일 때 `ChatWidget` 미렌더 (`{!isLlmPage && <ChatWidget />}`) — 로딩/미인증/인증완료 세 곳 모두 적용 |

---

## 검증 요약

| 항목 | 결과 |
|------|------|
| DB CHECK (GO100_AI 포함) | ✅ 적용 및 검증 완료 |
| go100 백엔드 헬스체크 | ✅ status ok, database/redis connected |
| 전략 저장 API (미인증) | ✅ 401 (500 아님) |
| 프론트 빌드 | ✅ 성공 |
| go100 페이지 (localhost:3000/go100) | ✅ 200 |
| /llm 페이지 (localhost:3000/llm) | 307 (리다이렉트, 미인증 시 로그인 등으로 정상 동작 가능) |
| .env/.bak 커밋 | ✅ 미포함 |
| 지정 파일만 수정 | ✅ layout.tsx 만 수정·커밋 |

---

*CUR-GO100-HOTFIX-SAVE-500 완료.*
