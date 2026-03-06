# NTV2-031 Reverb 활성화 보고서
**작성일**: 2026-03-06 KST
**최종 업데이트**: 2026-03-06 22:50 KST

## 결과
| 항목 | 결과 |
|---|---|
| Reverb 컨테이너 | ✅ Running (Up 7분+, port 8081:8080) |
| :8081 응답 | HTTP 404 (GET /) / HTTP 101 WebSocket Upgrade ✅ |
| WebSocket 핸드쉐이크 | ✅ HTTP/1.1 101 Switching Protocols (X-Powered-By: Laravel Reverb) |
| socket_id 발급 | ✅ pusher:connection_established 이벤트 수신 |
| echo.ts ECHO_ENABLED | ✅ true |
| laravel/reverb 설치 | ✅ v1.8.0 (composer require 실행) |
| docker-compose.yml Redis 수정 | ✅ REDIS_HOST=redis, REDIS_PORT=6379 추가 |
| 프론트 재빌드 | ✅ --no-cache 빌드 성공 (에러 0) |
| Frontend :3000 | HTTP 307 ✅ |
| Docker 전체 상태 | 6개 running |

## 실행 과정

### 1단계: 환경 확인
- `.env.docker` → REVERB_APP_ID 이미 존재 → skip
- `docker-compose.yml` → reverb 서비스 이미 존재 → skip 추가
- `echo.ts` → ECHO_ENABLED = true 이미 설정됨

### 2단계: composer require laravel/reverb
이전 세션에서 composer.json에는 `laravel/reverb: ^1.0` 추가되었으나 `composer.lock`에 누락
→ `docker exec -u root newtalk-v2-app composer require laravel/reverb:^1.0` 실행
→ laravel/reverb v1.8.0 설치 완료

### 3단계: docker-compose.yml Redis 수정
`.env.docker`의 `REDIS_PORT=6380` (호스트 포트)이 컨테이너 내부 Redis 포트 6379를 덮어쓰는 문제 발견
→ reverb 서비스에 `environment` 섹션 추가:
```yaml
environment:
  - REDIS_HOST=redis
  - REDIS_PORT=6379
  - REDIS_PASSWORD=null
```

### 4단계: Reverb 기동 확인
```
INFO  Starting server on 0.0.0.0:8080.
```
WebSocket 테스트 결과:
```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: HSmrc0sMlYUkAGmm5OPpG2HaGWk=
X-Powered-By: Laravel Reverb

{"event":"pusher:connection_established","data":"{\"socket_id\":\"363497917.290045803\",\"activity_timeout\":30}"}
```

### 5단계: 프론트엔드 재빌드
```
docker compose --env-file .env.docker build --no-cache frontend
→ [frontend builder 1/1] RUN npm run build — DONE 51.7s (에러 없음)
```

## 포트 불일치 사항 (문서화)
- 지시서: REVERB_PORT=6001, 테스트 대상: http://127.0.0.1:6001
- 기존 docker-compose.yml: --port=8080, 8081:8080 (grep 조건 충족 → SKIP)
- 실제 테스트: :8081 → HTTP 404 (GET /) / HTTP 101 (WebSocket) — 정상
- :6001 응답: HTTP 000 (미사용 포트)

## 최종 컨테이너 상태
```
NAME                  STATUS          PORTS
newtalk-v2-app        Up 11 days      9000/tcp
newtalk-v2-db         Up 12 days      0.0.0.0:3307->3306/tcp (healthy)
newtalk-v2-frontend   Up 40 seconds   0.0.0.0:3000->3000/tcp
newtalk-v2-nginx      Up 12 days      0.0.0.0:8080->80/tcp
newtalk-v2-redis      Up 12 days      0.0.0.0:6380->6379/tcp
newtalk-v2-reverb     Up 7 minutes    0.0.0.0:8081->8080/tcp
```

HANDOVER.md 업데이트 완료: (커밋해시 — git commit 후 확인)
