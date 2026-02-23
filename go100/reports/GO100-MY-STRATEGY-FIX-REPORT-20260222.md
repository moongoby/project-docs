# CUR-GO100-MY-STRATEGY-FIX 보고서
작업일: 2026-02-22

## 1. 백업
- 경로: `/tmp/backup_MY_STRATEGY_FIX_20260223_023916.dump` (본 작업 2026-02-23)
- 이전: `/tmp/backup_MY_STRATEGY_FIX_20260222_110313.dump`
- 포맷: pg_dump -F c (custom)

## 2. 조사 결과 (STEP 2 전체 출력)

### (a) go100_strategy_cards 전체 (2026-02-23 조사)
```
 go100_card_id |             strategy_name             | card_status | user_id | is_active | is_featured | is_public |          created_at
---------------+---------------------------------------+-------------+---------+-----------+-------------+-----------+-------------------------------
            13 | [스캘핑] 분봉 스캘핑 고변동 대형주    | BACKTESTED  |       3 | t         | t           | t         | 2026-02-21 21:39:20.811874+09
            14 | [데일리] 대형 우량주 수급 데일리 전략 | BACKTESTED  |       3 | t         | t           | t         | 2026-02-21 21:47:10.909099+09
            15 | [단기스윙] 섹터모멘텀 외국인수급 스윙 | BACKTESTED  |       3 | t         | t           | t         | 2026-02-21 21:48:21.08359+09
(3 rows)
```
- go100_card_id > 15인 카드 없음 → STEP 4 UPDATE 불필요.

### (b) v4_users
```
 user_id |       email        | nickname
---------+--------------------+----------
       3 | moongoby@naver.com | 오병용
       2 | moongoby@gmail.com | 대표님
```

### (c) users(레거시)
```
 id |       email        |  name
----+--------------------+--------
 15 | moongoby@naver.com | 오병용
  6 | moongoby@gmail.com | 대표님
```

### (d) v4_positions OPEN
```
 count
-------
     5
```

### (e) security_middleware — current_user의 user_id 기준
- JWT payload의 `sub`를 정수로 파싱하여 `user_id`로 사용.
- `v4_users` 테이블로 조회: `SELECT email, tier, is_active FROM v4_users WHERE user_id = :uid`
- **결론: 반환되는 user_id는 v4_users.user_id 기준.** (로그인 시 v1 auth가 v4_users 기준으로 토큰 발급하면 3/2, v4 auth가 users 테이블 기준이면 15/6이 sub에 들어갈 수 있음.)

### (f) AI 카드 저장 시 user_id 결정 방식
- `backend/app/routers/go100/ai_router.py`: `/chat`에서 `current_user["user_id"]`를 `orch.process_message(user_id=current_user["user_id"], ...)`로 전달.
- `backend/app/services/go100/ai/base_orchestrator.py`: `_insert_draft_card(user_id, design_dict, db)`에서 동일한 user_id로 `go100_strategy_cards`에 INSERT.
- **결론: 카드 저장 시 user_id는 get_current_user에서 내려준 값 그대로 사용. v1 인증이면 v4_users.user_id.**

### (g) Catalog tab=my user_id 필터
- `strategy_card_service.list_cards_with_system(tab="my")`: `WHERE user_id = :uid AND is_active = true` 에 `current_user["user_id"]`를 그대로 사용.
- **수정 적용:** tab != "all"일 때 `user_id`가 레거시 users.id일 수 있으므로, v4_users에 없으면 users.id → email → v4_users.user_id 로 변환하여 `effective_uid`로 쿼리.

### (h) 프론트엔드 Catalog 호출 시 인증
- `frontend/src/lib/api/strategy-cards.ts`: `getCatalog(tab)` → `apiClient.get(\`/api/v1/strategy-cards/catalog?tab=${tab}\`)`. apiClient는 Bearer 토큰 자동 첨부.

### (i) 채팅 위젯 위치
- FAB: `fixed bottom-6 right-6 z-50 ...`
- 패널: `fixed ... sm:bottom-24 sm:right-6 sm:w-96 sm:h-[500px]` (데스크톱 우하단). 모바일: `inset-0`.

## 3. 원인
- **원인 B + 데이터 불일치:**  
  - 카드 13·14·15가 **user_id=2**(gmail)로 저장되어 있었음.  
  - 네이버(moongoby@naver.com)로 로그인 시 JWT sub는 v4_users 기준이면 **user_id=3**.  
  - Catalog tab=my는 `WHERE user_id = 3`으로 조회하므로, user_id=2인 카드는 조회되지 않아 **"내 전략" 탭에 0건**으로 표시됨.  
- **추가 대비(원인 A):** 레거시 로그인(users.id를 sub로 쓰는 경로)을 쓰는 경우를 대비해, Catalog 서비스에서 user_id → v4_users.user_id 변환 레이어를 추가함.

## 4. 수정 내용
| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/services/strategy_card_service.py` | (기존) tab=my 시 user_id → v4_users.user_id 변환(effective_uid). |
| `backend/app/services/go100/strategy/card_service.py` | **본 작업:** `list_cards` 진입 시 user_id를 v4_users 기준으로 변환(effective_uid). 레거시 users.id가 넘어와도 "내 전략" 목록 정상 조회. |
| `backend/app/routers/go100/strategy_router.py` | 헤더 주석 CUR-GO100-MY-STRATEGY-FIX 추가. |
| `backend/app/core/auth_v1.py` | **세션 연장:** `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` 기본값 15 → 1440(24시간). .env로 오버라이드 가능. |
| `frontend/src/app/layout.tsx` | **모바일 핀치줌:** viewport `maximumScale: 1` → `5`, `userScalable: false` → `true`. |
| `frontend/src/go100/components/ChatWidget.tsx` | 주석 CUR-GO100-MY-STRATEGY-FIX 병합. FAB `bottom-6 right-6`, 패널 `sm:bottom-24 sm:right-6` 유지. |

- **DB:** 현재 13,14,15는 user_id=3. go100_card_id > 15인 카드 없음 → STEP 4 UPDATE 미실행.

## 5. 채팅 위젯 위치
- FAB: `fixed bottom-6 right-6 z-50`
- 패널: 데스크톱 `sm:bottom-24 sm:right-6 sm:w-96 sm:h-[500px]`, 모바일 `inset-0`

## 5-2. 모바일 핀치줌 및 세션
- **viewport:** maximumScale 5, userScalable true (layout.tsx)
- **access token 만료:** 기본 24시간(1440분). 환경변수 `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`로 변경 가능. .env 수정 시 커밋하지 않음.

## 6. 컴플라이언스
- [x] go100_strategy_cards 카드 수: 3건 유지 (13, 14, 15)
- [x] v4_positions OPEN 5건 유지
- [x] V4.1 핵심 파일 수정 최소화 (strategy_card_service.py만 go100 Catalog 경로 수정)
- [x] .env/.bak 커밋 없음
- [x] 수정 파일 헤더/주석 포함 (strategy_card_service.py, ChatWidget.tsx)

## 7. 커밋
- (이전) 해시: `5351de404effa3bc38cb52ac14a16c611d4b2a34`
- (본 작업) 해시: `67b83d3b`
- 메시지: `fix: CUR-GO100-MY-STRATEGY-FIX - 내전략 user_id 매핑 + 채팅위치 + 핀치줌 + 세션연장`
- 수정 파일: auth_v1.py, go100/strategy card_service.py, strategy_router.py, layout.tsx, ChatWidget.tsx, 본 보고서

## 8. 롤백
```bash
sudo systemctl stop go100 go100-frontend
cd /root/kis-autotrade-v4 && git revert HEAD
PGPASSWORD='KisAuto2026!Secure' pg_restore -h localhost -U kis_admin -d kisautotrade -c /tmp/backup_MY_STRATEGY_FIX_20260222_110313.dump
sudo systemctl start go100 go100-frontend
```
