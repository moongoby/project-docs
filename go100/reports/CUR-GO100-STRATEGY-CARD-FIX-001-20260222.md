# CUR-GO100-STRATEGY-CARD-FIX 작업 보고서

**작업일:** 2026-02-22

---

## 보고 요약 (Executive Summary)

| 항목 | 내용 |
|------|------|
| **지시서** | CUR-GO100-STRATEGY-CARD-FIX |
| **목표** | GO100 전략카드(Cards 13–15)가 사용자 전략카드 화면에 정상 노출 |
| **결과** | Catalog API에 GO100 병합 반영 완료. 전략카드·내 전략 페이지에서 GO100 카드 및 "GO100 AI" 뱃지 표시 |
| **커밋** | `4f8fef24` |
| **보고서** | `report/GO100-STRATEGY-CARD-FIX-REPORT-20260222.md` |

**코드 변경:** 백엔드 2파일, 프론트엔드 3파일, 스크립트 1개 신규. V4.1 핵심 로직 최소 수정, go100_* 전용 추가.

**배포 전 필수:** DB 백업 → STEP A(13,14,15만 유지) → STEP B(user_id 정합성) 수동 실행 후 서비스 재시작.

---

## 1. 백업 경로

DB 백업은 서버에서 수동 실행 필요 (비밀번호 인증):

```bash
pg_dump -h 127.0.0.1 -U go100user -d go100db -F c \
  -f /tmp/backup_STRATEGY_CARD_FIX_$(date +%Y%m%d_%H%M%S).dump
```

또는 스크립트 실행:

```bash
cd /root/kis-autotrade-v4
PGPASSWORD='...' bash scripts/cur_go100_strategy_card_fix_db.sh
```

**백업 경로 (실행 후 기록):** `/tmp/backup_STRATEGY_CARD_FIX_[타임스탬프].dump`

---

## 2. 사전 상태

다음은 **배포 서버에서 psql로 확인 후 기록**할 값입니다.

| 항목 | 명령 | 기록 |
|------|------|------|
| go100_strategy_cards | `SELECT COUNT(*) FROM go100_strategy_cards;` | [변경 전 건수] |
| Cards 13–15 | `SELECT go100_card_id, strategy_name, card_status, user_id FROM go100_strategy_cards ORDER BY go100_card_id;` | (결과 붙여넣기) |
| v4_positions OPEN | `SELECT COUNT(*) FROM v4_positions WHERE status='OPEN';` | [건수] |
| moongoby@naver.com | `SELECT user_id FROM v4_users WHERE email = 'moongoby@naver.com';` | id=[NAVER_USER_ID] |
| strategy_cards (V4.1) | `SELECT COUNT(*) FROM strategy_cards;` | [건수] |

---

## 3. 수행 작업

### [A] DB 정리 (수동 실행)

목적: `go100_strategy_cards`에서 **go100_card_id 13, 14, 15만 유지** (실제 PK 컬럼명: `go100_card_id`).

```sql
DELETE FROM go100_strategy_cards WHERE go100_card_id NOT IN (13, 14, 15);
```

검증: `SELECT go100_card_id, strategy_name, card_status, user_id FROM go100_strategy_cards ORDER BY go100_card_id;` → 3건이어야 함.

### [B] user_id 정합성 (수동 실행)

- `NAVER_USER_ID` = `v4_users`에서 `email = 'moongoby@naver.com'`인 행의 `user_id`.
- Cards 13–15의 `user_id`가 위와 다르면:

```sql
UPDATE go100_strategy_cards SET user_id = [NAVER_USER_ID] WHERE go100_card_id IN (13, 14, 15);
```

### [C] 백엔드 — 전략카드 Catalog API에 GO100 병합

- **파일:** `backend/app/schemas/strategy_card_schemas.py`
  - `StrategyCardDisplay`에 `source: Optional[str]` 추가 (v4 / go100 구분).
- **파일:** `backend/app/services/strategy_card_service.py`
  - `list_cards_with_system()` 내에서 기존 V4 로직 **수정 없이**,  
    `go100_strategy_cards`를 **추가 조회**하여 `user_id = current_user`인 카드만 병합.
  - GO100 카드는 `type="GO100"`, `source="go100"`으로 응답에 포함.
  - 예외 시(테이블 없음/스키마 차이) 로깅 후 무시하여 V4 동작에 영향 없음.

### [D] 프론트엔드 — 단일 API 사용 및 GO100 뱃지

- **파일:** `frontend/src/app/(protected)/strategy-cards/page.tsx`
  - **Catalog 단일 API 사용:** `useStrategyCatalog()`만 사용.  
    별도 `getStrategyCards()` 호출 제거.
  - Catalog 응답 카드에 `source` 정규화 (`source ?? "v4"`).
  - GO100 카드는 기존 `StrategyCard`에서 `source === "go100"`일 때 **"GO100 AI"** 뱃지 표시 유지.
- **파일:** `frontend/src/app/(protected)/go100/strategies/page.tsx`  
  - 헤더 주석 추가 (CUR-GO100-STRATEGY-CARD-FIX).  
  - 동작 변경 없음. GET `/api/go100/strategy-cards` 호출로 Cards 13–15 노출.
- **파일:** `frontend/src/components/strategy/StrategyCard.tsx`  
  - 헤더 주석 추가. `getTypeBadge(..., card.source)`로 GO100 AI 뱃지 유지.

---

## 4. 수정 파일 목록

| 경로 | 변경 내용 |
|------|-----------|
| `backend/app/schemas/strategy_card_schemas.py` | StrategyCardDisplay에 `source` 필드 추가, 헤더 주석 |
| `backend/app/services/strategy_card_service.py` | list_cards_with_system에 go100_strategy_cards 병합, 헤더 주석 |
| `frontend/src/app/(protected)/strategy-cards/page.tsx` | catalog 단일 API, source 정규화, 헤더 주석 |
| `frontend/src/app/(protected)/go100/strategies/page.tsx` | 헤더 주석 |
| `frontend/src/components/strategy/StrategyCard.tsx` | 헤더 주석 |
| `scripts/cur_go100_strategy_card_fix_db.sh` | **신규** — DB 백업/사전 확인/STEP A·B용 스크립트 |

---

## 5. 테스트 결과

| 항목 | 결과 |
|------|------|
| TypeScript (`npx tsc --noEmit`) | 통과 |
| Frontend Build (`npm run build`) | 성공 |
| pytest | (배포 환경/venv에서 실행 후 기록: N/N 통과) |
| Health check | (재시작 후 `curl http://localhost:8002/health`, `curl -o /dev/null -w "%{http_code}" http://localhost:3000/go100` 기록) |
| API 검증 | Catalog: `GET /api/v1/strategy-cards/catalog` → 로그인 사용자 기준 V4 + GO100 카드 병합. GO100 전용: `GET /api/go100/strategy-cards` → Cards 13–15 (user_id 일치 시) |

---

## 6. 컴플라이언스 체크리스트

- [ ] go100_strategy_cards: go100_card_id 13, 14, 15만 보유 (3건) — **DB 수동 실행 후 확인**
- [ ] v4_positions OPEN 5건 유지 — **변경 없음**
- [x] V4.1 핵심 파일 수정 최소화 (strategy_card_schemas, strategy_card_service만 수정, 기존 V4 조회 로직 유지)
- [x] .env / .bak 커밋 없음
- [x] 수정 파일 헤더 주석 포함 (CUR-GO100-STRATEGY-CARD-FIX, 2026-02-22)
- [x] DB 스키마 변경 없음 (go100_* 테이블 구조 변경 없음)

---

## 7. 커밋 해시

```
4f8fef24 feat: CUR-GO100-STRATEGY-CARD-FIX - GO100 전략카드 화면 노출 수정
```

---

## 8. 최종 확인 (배포 후)

1. **go100.newtalk.kr/strategy-cards** — GO100 AI 뱃지가 붙은 카드 3건 표시 여부.
2. **go100.newtalk.kr/go100/strategies** — Cards 13–15 정상 표시 여부.
3. **go100.newtalk.kr 대시보드** — 기존 V4.1 대시보드 정상 동작 여부.
4. **trading41.newtalk.kr** — V4.1 서비스 영향 없음 여부.

---

## 9. 롤백 절차

```bash
sudo systemctl stop go100 go100-frontend
cd /root/kis-autotrade-v4
git revert HEAD
pg_restore -U go100user -d go100db -c /tmp/backup_STRATEGY_CARD_FIX_[타임스탬프].dump
sudo systemctl start go100 go100-frontend
```
