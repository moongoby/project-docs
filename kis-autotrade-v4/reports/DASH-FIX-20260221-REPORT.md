# DASH-FIX 완료 보고서 — 2026-02-21

## 1. 원인 분석
- **nginx 프록시 대상**: `/api/v4/` → 8003 (kis-v41-api), `/api/` → 8001 (webapp), 대시보드 `/dashboard.html` → 8003/dashboard/
- **프론트엔드 API URL**: `window.location.origin + '/api/v4'` (상대 경로, 정상)
- **API 키 위치**: `.env`의 `INTERNAL_API_KEY` 존재(2건). 프론트엔드(`frontend/dashboard/app.js`)는 `localStorage.getItem('api_key')` 또는 `prompt()`로만 키를 획득하여, 미입력 시 `X-Internal-API-Key` 헤더가 비어 있음.
- **근본 원인**: 브라우저에서 `/api/v4/*` 호출 시 API 키를 보내지 않아 백엔드 `InternalAPIKeyMiddleware`가 403 "Invalid or missing X-Internal-API-Key" 반환.

## 2. 수정 내용
- **수정 파일**
  - `/etc/nginx/sites-available/kis-autotrade` (서버 로컬, git 미포함)
    - 80/443 두 server 블록에 `include /etc/nginx/internal-api-key.conf;` 추가
    - `location /api/v4/` 내부에 `proxy_set_header X-Internal-API-Key $internal_api_key;` 추가
  - `scripts/write_nginx_api_key.py` (프로젝트)
    - dotenv 우선으로 `.env`의 `INTERNAL_API_KEY` 읽어 nginx용 `set $internal_api_key "…";` 파일 생성
    - 기본 출력 경로: `/tmp/internal-api-key.conf` (root 없이 실행 가능)
- **키 파일**: `/etc/nginx/internal-api-key.conf` — 프로젝트 루트 `.env`와 동일한 값(venv+dotenv로 생성 후 `sudo cp /tmp/internal-api-key.conf /etc/nginx/`)으로 서버에서 1회 생성·적용함.
- **webapp 상태**: 불필요(대시보드는 8003에서 서빙, nginx가 8003으로 프록시).

## 3. 검증
- **API 호출**: `curl http://127.0.0.1/api/v4/dashboard/overview -H "Host: trading41.newtalk.kr"` → 401 (내부 키 통과 후 해당 라우트의 JWT 등 추가 인증에서 401). 이전 403 "Invalid or missing X-Internal-API-Key" 해소됨.
- **대시보드 로드**: 브라우저에서 `https://trading41.newtalk.kr` 접속 후 새로고침(Ctrl+Shift+R) 시, nginx가 `/api/v4/*` 요청에 `X-Internal-API-Key`를 주입하므로 포트폴리오/시그널/시스템/성과 추천 등 데이터 로드 가능해짐.

## 4. 사전/사후 확인
- strategy_cards: 59 / 59
- v4_positions OPEN: 5 / 5
- 서비스 상태: kis-v41-api, kis-v41-monitor, kis-v41-scheduler 모두 active
- 커밋: 프로젝트 내 수정분만 커밋 (nginx 설정·키 파일은 서버 로컬만 적용, 미커밋)

## 5. 이후 INTERNAL_API_KEY 변경 시
- 프로젝트에서: `source venv/bin/activate && python3 scripts/write_nginx_api_key.py`
- 서버에서: `sudo cp /tmp/internal-api-key.conf /etc/nginx/ && sudo systemctl reload nginx`

## 컴플라이언스 체크리스트
- [x] .env 커밋 여부 → 없음
- [x] 기존 DB 테이블 변경 여부 → 없음
- [x] kis-v41-api/monitor/scheduler 재시작 여부 → 없음
- [x] strategy_cards 59건 확인
- [x] v4_positions OPEN 5건 확인
- [x] 수정 파일 백업: `/root/backups/nginx_trading41.bak.20260221`
- [x] backtest 파일 수정 여부 → 없음
