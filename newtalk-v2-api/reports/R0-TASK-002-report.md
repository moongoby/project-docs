# R0-TASK-002 작업 완료 보고서

**문서번호**: NT-V2-R0-TASK-002  
**작성일**: 2026-02-21  
**대상**: Cursor AI (대표님 지시)

---

## 1. 작업 요약

| 항목 | 결과 |
|------|------|
| V1 DB(autoda) 전체 스키마 추출 | 스크립트 제공 완료 (서버에서 실행 시 TSV/SQL 생성) |
| 테이블 분류 | 약 140개 테이블 → 11개 카테고리(A~K) 분류 완료 |
| V2 마이그레이션 대상 핵심 테이블 | 40~50개 식별, v1-table-classification.md 반영 |
| V2 신규 스키마 설계 | v2-schema-design.md 작성 완료 |
| V1→V2 컬럼 매핑 | v1-v2-column-mapping.md 작성 완료 |
| Laravel 마이그레이션 파일 | 34개 생성 (users 컬럼 추가 1 + 테이블 33) |
| RBAC 시더 | RolesAndPermissionsSeeder (6역할, 28권한) 작성 완료 |

**참고**: 본 작업은 **워크스페이스(/root/newtalk-v2)** 에서 산출물을 생성하였습니다.  
실제 **마이그레이션 실행(migrate)** 및 **시더 실행**은 서버 `/srv/newtalk-v2`에서 Docker·Laravel 환경 구축 후 수행해야 합니다.

---

## 2. 생성 문서 목록

| 경로 | 설명 |
|------|------|
| docs/scripts/extract-v1-schema.sh | V1 스키마 추출 셸 스크립트 (서버 실행용) |
| docs/README-R0-TASK-002.md | STEP 1 실행 안내 |
| docs/v1-table-classification.md | V1 테이블 A~K 분류, V2 마이그레이션 Y/N |
| docs/v2-schema-design.md | V2 신규 DB 스키마 설계서 |
| docs/v1-v2-column-mapping.md | V1↔V2 컬럼 매핑 (핵심 테이블) |
| docs/reports/R0-TASK-002-report.md | 본 보고서 |

**서버에서 STEP 1 실행 시 추가 생성되는 파일**  
- docs/v1-tables-overview.tsv  
- docs/v1-schema-full.sql  
- docs/v1-columns-detail.tsv  
- docs/v1-indexes.tsv  
- docs/v1-foreign-keys.tsv  

---

## 3. 마이그레이션·시더 목록

### 3.1 마이그레이션 (database/migrations/)

| 순서 | 파일명 |
|------|--------|
| 1 | 2026_02_21_100001_add_v1_and_business_columns_to_users_table.php |
| 2 | 2026_02_21_100002_create_wholesale_profiles_table.php |
| 3 | 2026_02_21_100003_create_retail_profiles_table.php |
| 4 | 2026_02_21_100004_create_categories_table.php |
| 5 | 2026_02_21_100005_create_products_table.php |
| 6 | 2026_02_21_100006_create_product_channels_table.php |
| 7 | 2026_02_21_100007_create_product_images_table.php |
| 8 | 2026_02_21_100008_create_product_options_table.php |
| 9 | 2026_02_21_100009_create_product_details_table.php |
| 10 | 2026_02_21_100010_create_product_categories_table.php |
| 11 | 2026_02_21_100011_create_contracts_table.php |
| 12 | 2026_02_21_100012_create_contract_items_table.php |
| 13 | 2026_02_21_100013_create_orders_table.php |
| 14 | 2026_02_21_100014_create_order_items_table.php |
| 15 | 2026_02_21_100015_create_purchase_orders_table.php |
| 16 | 2026_02_21_100016_create_purchase_order_items_table.php |
| 17 | 2026_02_21_100017_create_inbound_receipts_table.php |
| 18 | 2026_02_21_100018_create_inbound_receipt_items_table.php |
| 19 | 2026_02_21_100019_create_barcodes_table.php |
| 20 | 2026_02_21_100020_create_shipments_table.php |
| 21 | 2026_02_21_100021_create_shipment_items_table.php |
| 22 | 2026_02_21_100022_create_deposits_table.php |
| 23 | 2026_02_21_100023_create_deposit_transactions_table.php |
| 24 | 2026_02_21_100024_create_downloads_table.php |
| 25 | 2026_02_21_100025_create_cafe24_syncs_table.php |
| 26 | 2026_02_21_100026_create_content_pipelines_table.php |
| 27 | 2026_02_21_100027_create_shooting_schedules_table.php |
| 28 | 2026_02_21_100028_create_coordinations_table.php |
| 29 | 2026_02_21_100029_create_message_logs_table.php |
| 30 | 2026_02_21_100030_create_sabangnet_syncs_table.php |
| 31 | 2026_02_21_100031_create_sabangnet_logs_table.php |
| 32 | 2026_02_21_100032_create_activity_logs_table.php |
| 33 | 2026_02_21_100033_create_settings_table.php |
| 34 | 2026_02_21_100034_create_code_masters_table.php |

**전제**: Laravel 기본 마이그레이션(users, password_resets) 및 **Spatie Permission** 패키지 publish 마이그레이션이 먼저 실행되어 있어야 함.

### 3.2 시더

- database/seeders/RolesAndPermissionsSeeder.php  
  - 역할: admin, md, purchaser, wholesale, retail, outsource (6개)  
  - 권한: 약 28개 (products.*, orders.*, purchase_orders.*, inbound.*, users.*, contracts.*, content.*, downloads.*, deposits.*, dashboard.*, settings.*)

---

## 4. V2 DB 예상 상태 (마이그레이션·시더 실행 후)

| 항목 | 예상 값 |
|------|---------|
| 테이블 수 | Laravel 기본 + Spatie 4 + 본 마이그레이션 34 ≈ 40개 이상 |
| 마이그레이션 | 전체 Ran |
| 역할(roles) | 6개 |
| 권한(permissions) | 28개 |

---

## 5. 핵심 설계 변경 사항

| 구분 | 내용 |
|------|------|
| 상품 이중등록 해소 | goods + goods_master → products + product_channels |
| 회원 역할 분리 | users.auth_code → users + Spatie roles/permissions |
| 주문/물류 정규화 | order_product → orders + order_items, order_block → purchase_orders + purchase_order_items |
| 사입/입고 분리 | inbound_receipts, inbound_receipt_items, barcodes |
| 예치금 | user_deposit → deposits + deposit_transactions |
| V1 원본 ID 보존 | users.v1_idx, v1_auth_code / products.v1_goods_idx, v1_master_idx / contracts.v1_contract_id / orders.v1_order_idx 등 |

---

## 6. 이슈/특이사항

- **실행 환경**: 현재 워크스페이스에 Laravel 프로젝트가 없어, 마이그레이션·시더 **파일만** 생성됨. 서버 `/srv/newtalk-v2`에 Laravel + Docker 구성 후 본 디렉터리를 복사하여 `php artisan migrate`, `php artisan db:seed --class=RolesAndPermissionsSeeder` 실행 필요.
- **users 테이블**: Laravel 기본 migration에 `email` 등이 있음. V1은 `userid`를 로그인 ID로 사용하므로, V2에서는 `email` 컬럼에 userid 값을 저장하거나, 별도 `login_id` 컬럼 추가 검토 가능.
- **Spatie 실행 순서**: `composer require spatie/laravel-permission` 후 `php artisan vendor:publish --provider="Spatie\Permission\PermissionServiceProvider"` 실행하여 생성된 permission 마이그레이션이 **본 마이그레이션보다 먼저** 실행되도록 할 것.

---

## 7. 미해결 사항

- auth_code=90 (65,580명) 정체 → V1 코드/업무 정의 추가 분석 권장.
- V1 데이터 실제 이관(INSERT·매핑)은 **별도 작업(R1)** 에서 진행.
- 서버에서 STEP 1(mysql/mysqldump) 미실행 시 v1-tables-overview.tsv 등 5개 파일은 없음. 필요 시 extract-v1-schema.sh 실행 후 보강.

---

## 8. 다음 작업

- **R0-TASK-003**: 사방넷 API 연동 테스트 + 시스템 C·D 연동 테스트  
- 서버에 `/srv/newtalk-v2` Laravel 프로젝트 구성 후, 본 마이그레이션·시더 반영 및 `migrate`/`db:seed` 실행  
- Git: 브랜치 `feature/R0-TASK-002-db-design`, 커밋 메시지 `[R0-002]` 접두사 사용 (지시서 9번 참고)

---

*본 보고서는 R0-TASK-002 지시서에 따른 분석·설계·마이그레이션 파일 생성 결과를 정리한 문서입니다.*
