# DESK-RECOMMEND-PAGE 결과 보고

**작업일**: 2026-02-22  
**작업명**: DESK 종목추천 흐름 페이지 개발

---

## 완료 요약

| 항목 | 결과 |
|------|------|
| desk-recommend.html 생성 | **Y** (경로: `/var/www/trading.newtalk.kr/desk-recommend.html`, 프로젝트 복사본: `frontend/desk-recommend.html`) |
| 레거시 메뉴 링크 추가 | **Y** (데스크탑 nav, 모바일 메뉴, 모바일 하단 nav) |
| API 엔드포인트 추가 | **Y** (아래 목록) |
| 파이프라인 흐름도 | **Y** |
| DESK 탭 | **Y** |
| 추천 종목 카드 | **Y** |
| 매매 타임라인 | **Y** |
| DESK 요약 사이드바 | **Y** |
| 디자인 레거시 통일 | **Y** (design-system.css, navigation.css, 그라데이션 배경, 카드 스타일) |
| DESK 색상 구분 | **Y** (DESK1 빨강/주황, DESK2 파랑, DESK3 초록, DESK4 보라, DESK5 금색) |
| Promotion 표시 | **Y** (타임라인에서 DESK 승격 이벤트, from_desk→to_desk) |
| 브라우저 접속 확인 | **Y** (URL: https://trading41.newtalk.kr/desk-recommend.html, curl 200) |
| kis-v41-api 재시작 | **Y** (API 라우터·미들웨어 반영) |
| strategy_cards COUNT | **59** |
| v4_positions OPEN | **5** |
| 커밋 해시 | **d0a09050** |
| 이슈 사항 | 없음 |

---

## API 엔드포인트 목록

- `GET /api/v4/desk-recommend/pipeline-summary` — 파이프라인 스텝별 건수 (유니버스, 스캘핑풀, 필터, 시그널, 리스크, 주문, 체결)
- `GET /api/v4/desk-recommend/signals?desk_id=N` — DESK별 오늘 시그널 목록 (v4_signals + v4_pick_reasons, SELECT만)
- `GET /api/v4/desk-recommend/timeline?limit=50` — 오늘 매매 타임라인 (시그널/주문/체결/승격)
- `GET /api/v4/desk-recommend/desk-summary` — DESK별 요약 (활성 전략, 시그널/체결, FundPool, 포지션)

인증: Bearer 토큰 (레거시 로그인 토큰). `/api/v4/desk-recommend/*` 는 브라우저 Bearer 호출 허용을 위해 `security_middleware` 에 예외 추가됨.

---

## 파일 변경

- **신규**: `backend/app/api/v4_desk_recommend.py`
- **수정**: `backend/app/main.py` (라우터 등록)
- **수정**: `backend/app/core/security_middleware.py` (desk-recommend Bearer 예외)
- **신규**: `frontend/desk-recommend.html` (프로젝트 내 복사본)
- **서버**: `/var/www/trading.newtalk.kr/desk-recommend.html` (배포본)
- **서버**: `/var/www/trading.newtalk.kr/dashboard.html` (메뉴 링크 추가)
- **백업**: `/root/backups/dashboard_restore_20260222/dashboard.html.before_menu_add`

---

## 비고

- 레거시 dashboard.html 수정은 메뉴 링크 추가만 수행. 기존 기능 변경 없음.
- 새 API는 SELECT만 수행. INSERT/UPDATE/DELETE 없음.
- strategy_cards, v4_positions 데이터 임의 수정 없음.

--- 보고 끝 ---
