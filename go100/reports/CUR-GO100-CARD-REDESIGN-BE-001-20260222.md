# CUR-GO100-CARD-REDESIGN-BE 보고서
작업일: 2026-02-22

## 백업
- 경로: `/tmp/backup_CARD_REDESIGN_BE_20260222_102735.dump`

## DB 스키마 변경
- **go100_strategy_cards** 컬럼 추가:
  - `is_featured` boolean NOT NULL DEFAULT false
  - `is_public` boolean NOT NULL DEFAULT false
  - `featured_order` integer NOT NULL DEFAULT 0
- 인덱스: `idx_go100_cards_featured`, `idx_go100_cards_public`
- Cards 13, 14, 15: `is_featured=true`, `is_public=true`, `featured_order=1,2,3` 설정
- 테이블 소유자: postgres — 마이그레이션은 `sudo -u postgres psql -d kisautotrade` 로 실행

## 코드 수정
| 파일 | 내용 |
|------|------|
| `backend/app/services/strategy_card_service.py` | `list_cards_with_system(user_id, account_id, db, tab="all")` → tab=all: is_featured GO100만, tab=my: user_id GO100만 반환. V4.1 strategy_cards 제외. `list_v4_cards_with_system()` 추가 (V4.1 병합 로직 보존) |
| `backend/app/api/v1/strategy_cards_router.py` | GET `/catalog` 에 `tab` Query 추가 (all / my / v4). tab=v4 시 `list_v4_cards_with_system` 호출 |
| `backend/app/migrations/025_go100_featured_columns.sql` | 신규 — is_featured, is_public, featured_order DDL |

## V4.1 호환성
- **호출처**: `list_cards_with_system` / `list_v4_cards_with_system` 호출은 `backend/app/api/v1/strategy_cards_router.py` 의 GET `/catalog` 뿐.
- **분리 방법**: Catalog 기본 동작은 GO100 전용 (tab=all → featured, tab=my → 내 전략). V4.1 대시보드에서 기존처럼 strategy_cards+go100 병합이 필요하면 **tab=v4** 로 호출 시 `list_v4_cards_with_system()` 사용.

## 테스트
- **pytest**: 154 passed, 1 failed (test_llm_gateway_e2e::test_c2sc_openai — 외부 API 429 할당량, 본 작업과 무관)
- **health**: `curl http://localhost:8002/health` → `{"status":"ok", ...}`
- **API tab=all**: 인증 토큰 필요. `GET /api/v1/strategy-cards/catalog?tab=all` → is_featured=true GO100 카드만 반환 예상 (3건).
- **API tab=my**: `GET /api/v1/strategy-cards/catalog?tab=my` → 해당 user_id의 GO100 카드만 반환 예상.

## 컴플라이언스
- [x] go100_strategy_cards 3건 유지
- [x] v4_positions OPEN 5건 유지
- [x] V4.1 핵심 파일 수정 최소화 (strategy_card_service에 메서드 추가, 라우터에 tab 분기만 추가)
- [x] .env / .bak 커밋 없음
- [x] 수정 파일 헤더 주석 포함 (CUR-GO100-CARD-REDESIGN-BE, 2026-02-22)
- [x] DB 스키마 변경 go100_* 만

## 커밋
- 메시지: `feat: CUR-GO100-CARD-REDESIGN-BE - featured 플래그 + Catalog GO100 전용`
- 해시: `09f94b56`
