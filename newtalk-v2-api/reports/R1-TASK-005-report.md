# R1-TASK-005 보고서: 기본 대시보드 API + V1 데이터 이관

**문서번호**: R1-TASK-005  
**작성일**: 2026-02-22  
**갱신**: 2026-02-23 (R1-TASK-005-FIX products 이관 커맨드 수정 반영)  
**브랜치**: feature/R1-TASK-005-migration  
**기준 브랜치**: feature/R1-TASK-004-dashboard  

---

## 0. R1-TASK-005-FIX: V1 goods 스키마 (실측)

**실행일시**: 2026-02-23. 서버 `docker compose --env-file .env.docker exec app php artisan tinker --execute="..."` 로 DESCRIBE 실행 후 기록.

**goods 테이블 (실제 컬럼)**  
PK: `id`. 주요: `user_id`, `GdsMstId`, `market`, `Category1`~`Category4`, `GoodsName`, `DanharooGoodsName`, `GoodsCode_1`~`GoodsCode_6`, `GoodsCode`, `CatalogName`, `BrandName`, `MakerName`, `SellingPeriod`*, `GoodsPrice`, `GoodsCount`, 옵션·배송·기타(GoodsEtc4~57 등), `activated`, `activated_day`, `mall_activated`, `re_created`, `created`, `modified`, `wholessalerPrice` 등 120개 이상.

**goods_master 테이블**  
PK: `id`. 주요: `user_id`, `Category1`~`Category4`, `GoodsName`, `GoodsCode`, `CatalogName`, `BrandName`, `MakerName`, `SellingPeriod`*, `GoodsPrice`, `GoodsCount`, `activated`, `created`, `modified` (24개).

**매핑 (실제 반영)**  
goods.`id`→v1_goods_idx, `GoodsName`→name, `GoodsCode`→product_code, `GoodsPrice`→retail_price, 도매가 컬럼 없음→wholesale_price 0, `BrandName`→brand, `created`→created_at, `activated`→status, `GdsMstId`→goods_master.`id`(v1_master_idx). JOIN: `g.GdsMstId = gm.id`.

커맨드는 런타임에 `getColumnListing`(대소문자 무시)으로 컬럼 감지 후 select/join 구성.

---

## 1. 개요

- **PART A**: 역할별 기본 대시보드 API `GET /api/dashboard/overview`, admin 전용 `GET /api/dashboard/stats` 구현.
- **PART B**: V1→V2 이관 Artisan 커맨드 3개 + 총괄 1개, V1 DB 연결 설정 가이드, products 컬럼 보강 마이그레이션.

**서버(/srv/newtalk-v2) 반영 후 §3 route:list, §4 curl, §5 이관 테스트, §6 Git을 실행하여 결과를 기입할 것.**

---

## 2. 생성·수정된 파일 목록

| 구분 | 경로 |
|------|------|
| 신규 | `app/Http/Controllers/Api/DashboardController.php` |
| 신규 | `app/Console/Commands/V1MigrateUsersCommand.php` |
| 신규 | `app/Console/Commands/V1MigrateProductsCommand.php` |
| 신규 | `app/Console/Commands/V1MigrateWholesaleCommand.php` |
| 신규 | `app/Console/Commands/V1MigrateAllCommand.php` |
| 신규 | `app/Models/Product.php` (없던 경우 생성) |
| 신규 | `database/migrations/2026_02_22_100000_add_v1_product_price_columns_to_products_table.php` |
| 신규 | `docs/R1-TASK-005-v1-database-config.md` (V1 DB 설정 가이드) |
| 수정 | `routes/api.php` (dashboard/overview, dashboard/stats 라우트 추가) |

---

## 3. route:list 결과

**실행 위치**: `/srv/newtalk-v2`  
**명령**:  
`docker compose --env-file .env.docker exec app php artisan route:clear && docker compose --env-file .env.docker exec app php artisan route:list --path=api/dashboard`

```
이번 R1-TASK-005-FIX에서는 미실행. 대시보드 라우트 검증은 별도 실행 시 위 명령으로 확인.
```

---

## 4. curl 테스트 결과

**사전**: admin 토큰 획득 (로그인 API 사용)

```bash
TOKEN=$(curl -s -X POST "http://127.0.0.1:8080/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@newtalk.kr","password":"NewTalk2026!@#"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('token') or d.get('data',{}).get('token',''))")
```

| # | 항목 | 명령 | 기대 | 결과 |
|---|------|------|------|------|
| E-1 | admin overview | curl Bearer $TOKEN .../dashboard/overview | 200, role=admin, ... | R1-TASK-005-FIX 범위 외(별도 curl 검증). |
| E-2 | md overview | GET /api/dashboard/overview (md 토큰) | 200, role=md, ... | 동일. |
| E-3 | purchaser overview | (purchaser 토큰) | 200, role=purchaser, ... | 동일. |
| E-4 | wholesale overview | (wholesale 토큰) | 200, role=wholesale, ... | 동일. |
| E-5 | retail overview | (retail 토큰) | 200, role=retail, ... | 동일. |
| E-6 | stats (admin) | curl .../dashboard/stats | 200, system/storage | 동일. |
| E-7 | stats (비admin) | md 토큰 | 403 | 동일. |
| E-8 | 기존 라우트 | purchase-orders 등 | 200 | 동일. |
| E-9 | V1 보호 | curl [SERVER-IP] | 200 | 동일. |

---

## 5. 이관 커맨드 테스트 결과

**실행 위치**: `/srv/newtalk-v2` (Docker 컨테이너 내 또는 `docker compose --env-file .env.docker exec app php artisan ...`)

| # | 항목 | 명령 | 기대 | 결과 |
|---|------|------|------|------|
| 5-1 | V1 접속 테스트 | tinker DB::connection('v1')->table('users')->count() | V1 users 건수 | R1-TASK-005-FIX에서 미실행(products 이관만 검증). |
| 5-2 | users dry-run | `v1:migrate-users --dry-run` | 이관 대상 건수 | 동일. |
| 5-3 | users limit=10 | `v1:migrate-users --limit=10` | 10건 이관 | 동일. |
| 5-4 | users 멱등성 | 동일 재실행 | 0 created, 10 updated | 동일. |
| 5-5 | products dry-run | `php artisan v1:migrate-products --dry-run` | 이관 대상 건수 출력 | **V1 goods 대상: 77111건** / [dry-run] 쓰기 없이 종료. |
| 5-6 | products limit=10 | `php artisan v1:migrate-products --limit=10 --active-only` | 10건 이관, created: 10 | **결과: created=10, updated=0, failed=0** (대상 12585건 중 limit=10) |
| 5-6b | products 멱등성 | 동일 `v1:migrate-products --limit=10 --active-only` 재실행 | created: 0, updated: 10 | **결과: created=0, updated=10, failed=0** |
| 5-7 | wholesale dry-run | `php artisan v1:migrate-wholesale --dry-run` | 도매 대상 건수 출력 | 이번 R1-TASK-005-FIX 범위에서 미실행. |

---

## 6. Git 커밋 및 푸시

**실행 위치**: `/srv/newtalk-v2`

```bash
git checkout feature/R1-TASK-004-dashboard
git pull origin feature/R1-TASK-004-dashboard
git checkout -b feature/R1-TASK-005-migration
git add -A
git diff --cached | grep -iE "(password|secret|key)" | grep -v "test\|example\|fake\|env\|config" | head -5
# → 비어 있어야 함 (.env.docker 제외)
env -i HOME="$HOME" PATH="/usr/bin:/bin" git commit -m "[R1-005] 기본 대시보드 + V1 데이터 이관 커맨드"
git push origin feature/R1-TASK-005-migration
git log --oneline -1
```

| 항목 | 결과 |
|------|------|
| 커밋 SHA | be662c7 |
| 푸시 결과 | feature/R1-TASK-005-migration → origin (f46fae0..be662c7) 푸시 완료. |

---

## 7. 이슈·특이사항

- **V1 DB 연결**: `config/database.php`에 `v1` 커넥션 추가 및 `.env.docker`에 `V1_DB_*` 설정은 서버에서 직접 적용. 상세는 `docs/R1-TASK-005-v1-database-config.md` 참조. Docker에서 호스트 DB 접속 시 `extra_hosts: host.docker.internal:host-gateway` 필요.
- **User 모델**: `getRoleNames()`(Spatie), `is_active` 컬럼은 서버 스키마/모델에 맞게 적용. `is_active` 없으면 마이그레이션 추가 또는 커맨드에서 해당 키 제거.
- **V1 users 컬럼명**: 실제 V1 스키마가 `userid`/`username`/`reg_date` 등이면 커맨드 내 fallback으로 처리. PK는 `user_idx` 또는 `id` 모두 처리.
- **V1 goods (R1-TASK-005-FIX 반영)**: products 이관 커맨드를 V1 실제 스키마에 맞게 수정함. 런타임에 `getColumnListing`(대소문자 무시)으로 컬럼 감지. 실제 스키마: id, GoodsName, GoodsCode, GoodsPrice, BrandName, created, activated, GdsMstId. `goods_master`는 id(PRI)만 사용, JOIN `g.GdsMstId = gm.id`. 리터럴 0/NULL은 `DB::raw()`로 전달해 컬럼 오인 방지. **products 이관 미완 → 해결됨.** 서버 실행 결과: dry-run 77111건, limit=10 created=10, 재실행 시 updated=10, V2 products v1_goods_idx 10건·샘플 정상.
- **products 테이블**: `wholesale_price`, `purchase_price`, `brand` 컬럼은 마이그레이션 `2026_02_22_100000_add_v1_product_price_columns_to_products_table.php`로 추가. `php artisan migrate` 실행 필요.

---

## 8. 완료 체크리스트

- [x] DashboardController (overview + stats) 생성
- [x] routes/api.php에 dashboard/overview, dashboard/stats 등록
- [x] V1MigrateUsersCommand, V1MigrateProductsCommand, V1MigrateWholesaleCommand, V1MigrateAllCommand 생성
- [x] V1 DB 설정 가이드 문서 작성
- [x] products용 wholesale_price/purchase_price/brand 마이그레이션 추가
- [x] Product 모델 생성(없던 경우)
- [ ] route:list에서 dashboard/overview, dashboard/stats 확인 (서버 실행 후)
- [ ] curl 테스트 전 항목 통과 (서버 실행 후)
- [x] 이관 products --dry-run / --limit=10 정상 및 멱등성 확인 (서버 실행 완료)
- [x] V1 DB 접속·goods/goods_master DESCRIBE 확인 (서버 실행 완료)
- [ ] 기존 라우트 정상 (§3·§4는 별도 실행 대상)
- [ ] V1 사이트 200 확인
- [x] Git 푸시 완료 (서버에서 커밋 be662c7, push origin feature/R1-TASK-005-migration 완료)
- [x] 보고서 작성
- [x] R1-TASK-005-FIX: V1MigrateProductsCommand V1 실제 스키마 반영 수정
