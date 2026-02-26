# 배포 및 X-Internal-API-Key 반영 결과 보고

- **작성일**: 2026-02-24
- **관련**: X-INTERNAL-API-KEY-VERIFY-AND-FIX-REPORT.md

---

## 1. 수행 내용

| 단계 | 작업 | 결과 |
|------|------|------|
| 1 | 프론트엔드 클린 빌드 (`rm -rf .next && pnpm run build`) | ✅ 성공 (Next.js 14.2.35, 29페이지 생성) |
| 2 | go100-frontend 서비스 재시작 | ✅ active (running) |
| 3 | systemd에 `EnvironmentFile=/root/kis-autotrade-v4/.env` 추가 | ✅ 적용 (INTERNAL_API_KEY 로드) |
| 4 | daemon-reload 후 go100-frontend 재시작 | ✅ 적용 |
| 5 | 헬스체크 및 /api/v4 경유 호출 검증 | ✅ 아래 참조 |

---

## 2. 검증 결과

| 항목 | 결과 |
|------|------|
| 백엔드(8002) /health | ✅ 200, status ok, database/redis connected |
| 프론트(3000) | ✅ 200, HTML 응답 |
| **프론트 경유 /api/v4/chart/stocks** | **✅ HTTP 200**, JSON 정상 (종목 목록 반환) |
| 공개 URL (go100.newtalk.kr) | ✅ 접근 가능 |

- **의미**: 이전에 403 "Invalid or missing X-Internal-API-Key" 로 실패하던 `/api/v4/*` 호출이, Next.js 미들웨어에서 `INTERNAL_API_KEY`를 주입하고, 서비스가 `.env`를 로드하도록 한 뒤 **200으로 정상 응답**함.

---

## 3. 변경된 설정 (서버)

- **파일**: `/etc/systemd/system/go100-frontend.service`
- **추가된 줄**: `EnvironmentFile=/root/kis-autotrade-v4/.env`
- **위치**: `[Service]` 블록 상단 (기존 Environment 줄과 함께 유지)

이에 따라 Next.js 프로세스에 `INTERNAL_API_KEY`가 전달되고, 미들웨어가 `/api/v4/*` 요청에 `X-Internal-API-Key` 헤더를 붙여 백엔드 검증을 통과함.

---

## 4. 요약

- 배포(빌드 + 재시작) 완료.
- X-Internal-API-Key 미전달로 인한 403 제거를 위해 **미들웨어 주입 + systemd EnvironmentFile** 적용 완료.
- **/api/v4/chart/stocks** 프론트(3000) 경유 호출 **200 확인**으로, 종목 상세 모달의 차트·재무·수급 등 V4 API 연동이 동작할 환경이 갖춰진 상태임.

---

## 5. 사용자 확인 권장

- 브라우저에서 **https://go100.newtalk.kr/dashboard** 접속 후, 시장 순위 등에서 **종목 클릭 → 종목 상세 모달**에서 일봉/분봉 차트·재무·수급이 로드되는지 확인.
- "Invalid or missing X-Internal-API-Key" 배너가 더 이상 나오지 않아야 함.
