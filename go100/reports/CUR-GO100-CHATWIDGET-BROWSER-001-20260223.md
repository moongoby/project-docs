# CUR-GO100-CHATWIDGET-BROWSER-001 ChatWidget FAB 브라우저 검증

**일시:** 2026-02-23 (월) 15:35 KST  
**서버:** root@211.188.51.113 (SSH)  
**코드 repo:** `/root/kis-autotrade-v4` (branch: phase-2c-command-center)  
**문서 repo:** `/root/project-docs` (branch: master)  
**목적:** useAuth 쿠키 token 패치 후 ChatWidget FAB 브라우저 노출 검증  
**선행:** CHATWIDGET-VERIFY-001 → useAuth.ts 수정, 빌드+재시작 완료  
**절대규칙:** kis-v41-* 서비스 재시작 금지 (준수)

---

## STEP 1. 현재 빌드/서비스 상태 확인

| 항목 | 결과 |
|------|------|
| **BUILD_ID** | `q2KA7Muq-oavchLUr_4jd` |
| **go100-frontend** | ● active (running), 15:27:50 KST 기동 |
| **go100 (API)** | ● active (running), 15:28:06 KST 기동 |
| **useAuth.ts 패치** | `getTokenFromCookie()`, `document.cookie.match(/\btoken=...)`, `getTokenFromCookie()` fallback 적용 확인 |

**useAuth.ts 관련 라인:** 10, 12, 30, 37 (cookie → token 우선 사용)

---

## STEP 2. 토큰 발급 + 인증 후 /dashboard (localhost)

| 항목 | 결과 |
|------|------|
| **로그인** | 성공 (access_token 발급) |
| **쿠키 token으로 /dashboard** | HTML 12,265B 수신 |
| **ChatWidget HTML 언급** | 0회 (SSR 없음, 클라이언트 dynamic import 구조) |
| **layout JS** | `layout-930b4dda40eb2b54.js` |
| **layout 청크 내 ChatWidget/7044** | 1건 (dynamic import 존재) |
| **7044 청크 파일** | `7044-c2f01c78813332b9.js` |
| **localhost:3000 7044 접근** | **HTTP 200** |
| **go100.newtalk.kr 7044 접근** | **HTTP 200** |

---

## STEP 3. 외부 도메인 전체 확인

| 항목 | 결과 |
|------|------|
| **외부 로그인** | 성공 (access_token 발급) |
| **외부 /dashboard HTML** | 12,265B (localhost와 동일) |
| **외부 layout JS** | `layout-930b4dda40eb2b54.js` (동일 → 최신 빌드 반영) |
| **CF Cache** | `cf-cache-status: DYNAMIC` (캐시 미사용, 실시간 서빙) |

---

## STEP 4. 결론

- **판정:** **A) localhost + 외부 모두 layout JS 로딩 + 7044 청크 접근 가능 → FAB 정상 노출 예상**
- layout 청크에 ChatWidget dynamic import 존재, 7044 청크 localhost/외부 모두 HTTP 200.
- 외부 HTML·layout JS 해시가 localhost와 동일하고 CF가 DYNAMIC이므로 구 빌드/캐시 이슈 없음.
- **권장:** 실제 브라우저에서 `https://go100.newtalk.kr/dashboard` 접속 후 로그인(또는 쿠키 `token=...` 설정)하여 FAB 노출 1회 수동 확인.

---

## 동기화 체크

- [x] STEP 1 빌드/서비스 상태 + useAuth 패치 확인
- [x] STEP 2 localhost 인증 + layout/7044 청크 접근
- [x] STEP 3 외부 도메인 + CF 캐시 확인
- [x] STEP 4 결론
- [x] 보고서 작성 → project-docs 커밋 + push (수동 실행 가이드 아래 참조)

---

## 보고서 저장 및 배포

- **서버 경로:** `/root/project-docs/go100/reports/CUR-GO100-CHATWIDGET-BROWSER-001-20260223.md`
- **GitHub URL:** https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-CHATWIDGET-BROWSER-001-20260223.md

**커밋 예시:**

```bash
cd /root/project-docs
git pull --rebase origin master
git add go100/reports/CUR-GO100-CHATWIDGET-BROWSER-001-20260223.md
git commit -m 'docs: CUR-GO100-CHATWIDGET-BROWSER-001 ChatWidget FAB 브라우저 검증 (20260223_1535)'
git push
```

---

*CUR-GO100-CHATWIDGET-BROWSER-001 종료.*
