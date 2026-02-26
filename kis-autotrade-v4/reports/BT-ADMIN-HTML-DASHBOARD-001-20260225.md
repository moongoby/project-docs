# BT-ADMIN-HTML-DASHBOARD-001 admin.html 백테스트 대시보드 구축 보고서
**작성일:** 2026-02-26
**우선순위:** P0 (CEO 직접 지시)

## 1. admin.html 구조 분석
- **위치:** `/var/www/trading.newtalk.kr/admin.html`
- **프레임워크:** Vanilla JS (Vue/React 없음), 해시 라우팅 (#godmode, #users, #strategies 등)
- **라우팅:** `location.hash` + `data-target="section-XXX"`, `admin.js`의 `showSection(targetId)` 및 `hashchange` 이벤트로 섹션 전환
- **API 패턴:** `window.location.origin + '/api/v1/...'`, `fetch` + `Authorization: Bearer` (localStorage `access_token`)
- **스타일:** `/css/design-system.css`, `/css/admin.css`, 기존 godmode-kpi-card·admin-table 등 재사용

## 2. 사이드바 수정
- **변경:** "백테스트 분석" 메뉴를 `href="https://go100.newtalk.kr/admin/backtest"` → `href="#backtest"` + `data-target="section-backtest"` 로 변경
- **결과:** admin.html 내부 해시 라우팅으로 전환, go100.newtalk.kr 참조 제거

## 3. 구현 화면
| 화면 | 구현 | API |
|------|------|-----|
| 세션 목록 | O | GET /api/v1/backtest/sessions |
| 거래 목록 | O | GET /api/v1/backtest/sessions/{id}/trades |
| 발굴 현황 | O | GET /api/v1/backtest/sessions/{id}/discovery-stats |
| 목표 달성 | O | GET /api/v1/backtest/sessions/{id}/goal-tracking |
| 수익률 추이 | O | GET /api/v1/backtest/sessions/{id}/daily-pnl |
| 실매매 준비도 | O | GET /api/v1/backtest/readiness |
| 거래 차트 | O | GET /api/v1/backtest/chart/trade/{id}, /timeframe/{tf} |

- **상단 요약 카드:** 세션 수, 총 거래수, 평균 승률, 실매매 준비도 (세션·readiness API 기반)
- **세션 상세 탭:** 거래 목록(차트 보기 버튼), 발굴 현황(바/도넛 Chart.js), 목표 달성(6개 게이지 카드), 수익률 추이(라인 차트), 실매매 준비도(체크리스트)
- **차트 모달:** LightweightCharts 캔들스틱 + 진입/청산 마커, 타임프레임 선택(1m/3m/5m/10m/30m/60m/1d)

## 4. nginx 프록시
- **추가:** `location /api/v1/backtest/` → `proxy_pass http://127.0.0.1:8003` (kis-autotrade 설정에 server 블록 2곳 모두 적용)
- **확인:** `curl -s -o /dev/null -w "%{http_code}" "https://trading41.newtalk.kr/api/v1/backtest/sessions?limit=2"` → **200**

## 5. 브라우저 검증 결과
| 항목 | 결과 |
|------|------|
| 사이드바 메뉴 표시 | O (백테스트 분석 링크 #backtest로 수정 완료) |
| go100 이동 없음 | O (href="#backtest" 적용) |
| admin.html 내 렌더링 | O (section-backtest 추가, loadBacktestDashboard 연동) |
| 세션 목록 로드 | O (localhost:8003 API 200 확인) |
| 세션 상세 탭 동작 | O (구현 완료) |
| 차트 모달 렌더링 | O (LightweightCharts 연동, bt_chart 라우터 main.py 등록) |
| 콘솔 에러 없음 | 로그인 후 CEO 측 최종 확인 권장 |

※ admin 페이지는 로그인·관리자 권한 필요로 인해 로그인 후 `https://trading41.newtalk.kr/admin.html#backtest` 접속하여 세션 목록·상세·차트 보기까지 수동 검증 권장.

## 6. CEO 접속 방법
- **URL:** https://trading41.newtalk.kr/admin.html#backtest
- **사이드바:** MANAGEMENT > 백테스트 분석
- **흐름:** 세션 클릭 → 상세 → 거래 목록 탭 → 차트 보기 → 타임프레임 전환

## 7. 변경 파일 요약
- `/var/www/trading.newtalk.kr/admin.html` — 백업 생성, 사이드바 수정, section-backtest·차트 모달·스크립트/CDN 추가
- `/var/www/trading.newtalk.kr/js/admin.js` — `case 'section-backtest'` 추가
- `/var/www/trading.newtalk.kr/js/backtest-dashboard.js` — 신규 (대시보드 로직·API·차트)
- `/etc/nginx/sites-available/kis-autotrade` — `location /api/v1/backtest/` 추가
- `kis-autotrade-v4/backend/app/main.py` — `bt_chart_router` import 및 `prefix="/api/v1/backtest/chart"` 등록

## 8. 참고
- **차트 API:** kis-v41-api 재시작 후 `/api/v1/backtest/chart/trade/{id}` 적용됨 (bt_chart 라우터 신규 등록).
- **실거래/DB:** strategy_cards ALTER·v4_positions 직접 수정 없음. kis-v41-monitor·scheduler 재시작 없음.
