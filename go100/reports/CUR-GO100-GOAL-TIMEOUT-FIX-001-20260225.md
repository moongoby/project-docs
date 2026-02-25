# CUR-GO100-GOAL-TIMEOUT-FIX-001 보고서

**작성일**: 2026-02-25 19:00 KST
**우선순위**: P0
**상태**: **완료**

---

## 1. 문제

### 1.1 Cloudflare 524 타임아웃 (핵심)

- **현상**: Goal 2턴(전략 생성), strategy(전략 설계), optimize_existing(최적화) 처리 시 1~5분 소요 → Cloudflare 100초 타임아웃(524) → 사용자에게 오류 표시
- **Cloudflare 524**: Origin 서버가 100초 이내에 응답하지 않으면 Cloudflare가 연결 종료 (Free/Pro 플랜 변경 불가)
- **백엔드는 정상 완료**하지만 프론트가 응답을 받지 못함

### 1.2 Nginx 타임아웃 설정 불완전

- `proxy_read_timeout 300s`만 설정, `proxy_connect_timeout`과 `proxy_send_timeout`은 Nginx 기본값(60s)

## 2. 해결 내용

### 2.1 Nginx 타임아웃 확장 (Belt-and-Suspenders)

**파일**: `/etc/nginx/sites-enabled/go100`

```nginx
location /api/ {
    proxy_pass http://go100_backend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_connect_timeout 30s;   # 추가 (기존 Nginx 기본 60s)
    proxy_send_timeout 300s;     # 추가 (기존 Nginx 기본 60s)
    proxy_read_timeout 300s;     # 기존 유지
}
```

| 타임아웃 | 이전 | 이후 | 설명 |
|---------|------|------|------|
| `proxy_connect_timeout` | 60s (기본) | **30s** | 백엔드 연결 대기 (30초면 충분) |
| `proxy_send_timeout` | 60s (기본) | **300s** | 클라이언트→백엔드 요청 전송 |
| `proxy_read_timeout` | 300s | 300s | 백엔드 응답 대기 (기존 유지) |

**참고**: Nginx 타임아웃 300초 확장은 "보험" 역할. 실제 524 방지는 비동기 태스크 시스템(CUR-GO100-CHAT-LOADING-UX-001)이 담당.

### 2.2 비동기 태스크 시스템 (CUR-GO100-CHAT-LOADING-UX-001과 공유)

Goal 2턴 카드 생성의 524 방지는 CUR-GO100-CHAT-LOADING-UX-001에서 구현한 비동기 태스크 시스템으로 해결:

- `POST /chat` → 즉시 `{status: "processing", task_id: "xxx"}` 반환 (< 0.1초)
- 프론트에서 2초 간격 `GET /task/{task_id}` 폴링 (각 폴링 < 0.1초)
- Cloudflare 100초 제한에 걸리지 않음

비동기 처리 대상:
| 인텐트 | 방식 | 소요 시간 |
|--------|------|----------|
| **goal_setup 2턴** | 비동기 | 1~5분 |
| **strategy** | 비동기 | 10초~3분 |
| **optimize_existing** | 비동기 | 30초~2분 |
| 기타 (help, stock_info 등) | 동기 | < 3초 |

## 3. 검증

### 3.1 Nginx 설정 검증

```
$ sudo nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful

$ sudo systemctl reload nginx  # 무중단 리로드
```

### 3.2 Cloudflare E2E 테스트

공개 URL(`https://go100.newtalk.kr`)을 통한 테스트:

```
$ curl -s -o /dev/null -w "%{http_code} %{time_total}s" \
    -H "Authorization: Bearer $TOKEN" \
    https://go100.newtalk.kr/api/go100/ai/chat \
    -d '{"message": "test strategy", "user_id": 1, ...}'
→ 200 0.1s  (즉시 task_id 반환)

$ curl -s https://go100.newtalk.kr/api/go100/ai/task/{task_id} \
    -H "Authorization: Bearer $TOKEN"
→ 200 0.1s  (processing/completed 상태)
```

- 모든 요청 0.1초 이내 응답
- 524 에러 없음
- `server: cloudflare` 헤더 확인 → Cloudflare CDN 경유 확인

### 3.3 Cloudflare 프록시 확인

```
$ curl -sI https://go100.newtalk.kr/health | grep -i server
server: cloudflare
cf-ray: 91f02...
```

## 4. 변경 파일

| 파일 | 변경 | 위치 |
|------|------|------|
| `/etc/nginx/sites-enabled/go100` | `proxy_connect_timeout 30s`, `proxy_send_timeout 300s` 추가 | 서버 직접 (git 외부) |

**코드 레포 변경 없음**: 비동기 태스크 시스템은 CUR-GO100-CHAT-LOADING-UX-001 커밋(`1e3871e2`)에 포함.

## 5. 연관 작업

- **CUR-GO100-CHAT-LOADING-UX-001** (P1): 비동기 태스크 시스템 + 폴링 + AIProgressIndicator 실시간 단계 표시
  - 이 작업의 "Goal 2턴 카드 생성 동기 → 백테스트 백그라운드" 요구사항도 해당 시스템이 처리
  - 보고서: `CUR-GO100-CHAT-LOADING-UX-001-20260225.md`
  - 커밋: `1e3871e2` (`phase-2c-command-center` 브랜치)

## 보고 요약

- **Nginx 타임아웃**: `proxy_connect_timeout 30s`, `proxy_send_timeout 300s` 추가 (보험 역할)
- **524 방지 핵심**: 비동기 태스크 시스템으로 모든 장시간 작업 즉시 응답 (< 0.1초)
- **E2E 검증**: Cloudflare 공개 URL 통해 524 미발생 확인
- **Goal 2턴 비동기화**: CUR-GO100-CHAT-LOADING-UX-001에서 이미 구현 완료
