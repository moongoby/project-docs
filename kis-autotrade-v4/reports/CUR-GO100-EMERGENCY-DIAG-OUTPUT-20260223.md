# GO100 긴급 진단 결과 (2026-02-23)

## 요약

- **현재 상태**: 서비스·프록시·로컬/외부 HTTP 모두 **정상** (frontend 200, backend 200, https://go100.newtalk.kr 200).
- **"서버에 일시적으로 연결할 수 없습니다"** 는 **Next.js 에러 페이지** (`frontend/src/app/error.tsx`) 문구로, 과거에 프론트엔드가 **MODULE_NOT_FOUND** 로 크래시했을 때 노출된 것으로 보입니다.
- **권장**: 브라우저 강력 새로고침 후 재접속. 재발 방지를 위해 프론트엔드 **클린 빌드** 권장.

---

## 1. 서비스 상태

| 서비스 | 상태 | 비고 |
|--------|------|------|
| go100-frontend | ● active (running) | 08:40:37 시작, "Ready in 781ms" |
| go100 (백엔드) | ● active (running) | 08:38:38 시작 |
| nginx | ● active (running) | 80/443 리스닝 |

---

## 2. 포트 확인

- **3000**: next-server (go100-frontend) — LISTEN
- **8002**: go100 백엔드 (uvicorn) — LISTEN
- **80 / 443**: nginx — LISTEN

---

## 3. 프론트엔드 로그 (원인)

**08:39:52 경** 다음 오류로 크래시:

```
Error: Cannot find module '/root/kis-autotrade-v4/frontend/.next/server/pages/_error.js'
code: 'MODULE_NOT_FOUND'
```

→ 빌드 산출물 불일치 또는 불완전 빌드로 인한 **MODULE_NOT_FOUND**.  
→ 이 시점에 사용자에게 **error.tsx** 가 노출되어 "서버에 일시적으로 연결할 수 없습니다" 가 보였을 가능성이 큼.

**08:40:37** 서비스 재시작 후:

```
✓ Ready in 781ms
```

이후 로그에는 추가 오류 없음.

---

## 4. 백엔드 로그

- 정상 요청 처리 (200).  
- 시세 관련: `Broker quote failed for 005930: invalid literal for int() with base 10: '0.00'` (별도 이슈, 연결 오류와 무관).

---

## 5. Nginx 에러 로그

- 최근 30줄: `/api/v1/notifications/stream` 에 대한 **upstream prematurely closed** 만 기록 (SSE 스트림 정상 종료에 가까운 동작).
- **프론트/API 프록시 관련 연결 실패 로그 없음.**

---

## 6. 로컬 접속 테스트

```
frontend: 200   (http://localhost:3000/go100)
backend:  200   (http://localhost:8002/health)
```

---

## 7. 외부 접속 테스트

```
https://go100.newtalk.kr/     → 200
https://go100.newtalk.kr/go100 → 200
```

---

## 8. 디스크 / 메모리

- 디스크: `/` 54% 사용 (45G 여유)
- 메모리: 15Gi 중 약 11Gi available

---

## 9. BUILD_ID

- 경로: `/root/kis-autotrade-v4/frontend/.next/BUILD_ID`
- 수정 시각: Feb 23 08:40 (프론트 재시작 시점과 일치)

---

## 10. Nginx 설정 (go100-domain)

- `/api/` → 127.0.0.1:8002 (go100_backend)
- `/` → 127.0.0.1:3000 (go100_frontend)
- SSL: Certbot(letsencrypt) 적용

설정 이상 없음.

---

## 조치 권장 사항

1. **즉시**: 브라우저에서 **강력 새로고침**(Ctrl+Shift+R 또는 캐시 비우기 후 재접속).  
   - 현재 서버/프록시는 정상이므로, 캐시된 에러 페이지가 남아 있을 수 있음.

2. **재발 방지**: 프론트엔드 **클린 빌드** 후 서비스 재시작 권장.
   ```bash
   cd /root/kis-autotrade-v4/frontend
   rm -rf .next
   npm run build
   sudo systemctl restart go100-frontend
   ```

3. (선택) 백엔드 시세 파싱 경고 `invalid literal for int() with base 10: '0.00'` 는 별도 이슈로, 시세 필드 파싱 로직 점검 시 float/문자열 처리 보완 권장.

---

*진단 실행: 2026-02-23 (Cursor 긴급 진단 명령)*
