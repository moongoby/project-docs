# CUR-V41-TRADING-PAGE-FIX-001 보고서

[인계 확인]
직전 완료: CUR-V41-DESK2-ACTIVATE-003
현재 단계: 매매현황 페이지 조치 완료
CEO 지시 적용: D-001, D-007
strategy_cards: 60
open_positions: 14

---

## 태스크 정보
- **Task ID**: CUR-V41-TRADING-PAGE-FIX-001
- **날짜**: 2026-03-03
- **완료 시각**: 14:30 KST
- **분류**: 프론트엔드 연결 버그 수정 (Nginx 라우팅)

---

## 문제 요약

**증상**: `https://trading41.newtalk.kr/trading.html` — 매매현황(주문 내역) 패널이 완전히 비어 있음  
**보고 계정**: moongoby@gmail.com

---

## 원인 분석

### 근본 원인: Nginx 라우팅 불일치

| 구분 | 포트 | 경로 |
|------|------|------|
| 실제 V4.1 API (데이터 있음) | 8003 | `/root/kis-autotrade-v4/backend/` |
| 레거시 webapp (데이터 없음) | 8001 | `/root/webapp/backend/` |

```nginx
# 기존 (잘못된 상태):
location /api/v4/ { proxy_pass 8003; }  ← V4 전용만
location /api/    { proxy_pass 8001; }  ← /api/v1/ 전체 포함
```

`trading.html`이 호출하는 `/api/v1/live-trading/...`이 **8001(레거시)**로 라우팅되어,  
v4_mock_trades 데이터가 있는 8003에 도달하지 못함.

### 추가 확인 사항
- `v4_mock_trades`: 18행 존재 (오늘 Desk2 모의 거래)
- 8001 서비스: `/api/v1/live-trading/` 엔드포인트 있으나 v4_mock_trades 미연결
- 8003 v4_compat.py: `recent-trades`, `trades`, `verification` 등 이미 구현됨
- **JWT 인증**: 양쪽 서비스 동일 `users` 테이블 + 동일 `SECRET_KEY` 사용 → 토큰 호환

---

## 조치 내용

### 1. Nginx 라우팅 수정 (`/etc/nginx/sites-enabled/kis-autotrade`)

HTTP(80) + HTTPS(443) 양쪽에 위치 블록 추가:
```nginx
# V4.1 live-trading — /api/v1/live-trading/* → 8003
location /api/v1/live-trading/ {
    proxy_pass http://127.0.0.1:8003;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Internal-API-Key $internal_api_key;
    proxy_connect_timeout 10s;
    proxy_read_timeout 60s;
}
```
Nginx prefix 매칭: `/api/v1/live-trading/` (긴 경로) > `/api/` (짧은 경로) 우선 적용

### 2. Nginx reload
```bash
nginx -t && systemctl reload nginx
```

---

## 검증 결과

### API 엔드포인트 (HTTPS 통해)
| 엔드포인트 | 상태 | 결과 |
|-----------|------|------|
| `/api/v1/live-trading/trades?limit=3` | 200 | ✅ 데이터 반환 |
| `/api/v1/live-trading/recent-trades?limit=10` | 200 | ✅ 10건 반환 |
| `/api/v1/live-trading/detected-signals?limit=20` | 200 | ✅ 6건 반환 |
| `/api/v1/live-trading/pending-buy-integrated` | 200 | ✅ 10건 반환 |
| `/api/v1/live-trading/stats` | 200 | ✅ |
| `/api/v1/live-trading/positions` | 200 | ✅ |

### Playwright 브라우저 검증 (moongoby@gmail.com)
- `#orderList`: ✅ 데이터 표시됨 (HTML 13,350 chars)
- 주문 아이템: **10개** (S1, D-ORB, D7 전략 포함)
- 감지된 매매 신호: **6개**
- 매수 대기 종목: **10개**
- Console 에러: `pipeline/reconcile` 404 1건 (minor, 기능 무관)

### 표시된 주문 예시
```
199231 | S1 | 진입가 ₩44,401 | 3/3 10:28 | OPEN
343669 | D-ORB | 진입가 ₩21,897 | 3/3 10:21 | OPEN
221455 | D7 | 진입가 ₩112,901 | 3/3 10:21 | OPEN
```

---

## 관련 파일
- `/etc/nginx/sites-enabled/kis-autotrade` — Nginx 라우팅 (수정)
- `/root/kis-autotrade-v4/backend/app/routers/v4_compat.py` — 8003 live-trading 라우트 (기 구현)
- `/root/kis-autotrade-v4/backend/app/services/compat/legacy_adapter.py` — v4_mock_trades fallback (기 구현)

---

## 코드 레포 커밋
- Nginx 설정 변경: 코드 레포 외 파일 (`/etc/nginx/...`) — 커밋 불필요
- 기존 8003 코드 활용 (이전 세션 코드 변경 유효)

---

## 체크포인트
- [x] Nginx 라우팅 변경 완료 + reload OK
- [x] HTTPS API 전체 200 확인
- [x] Playwright 브라우저 검증 (moongoby@gmail.com) ✅
- [x] project-docs 보고서 push 완료

