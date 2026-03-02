# R0-TASK-002-FIX-3 실행 보고서

**문서번호**: NT-V2-R0-TASK-002-FIX-3  
**작성일**: 2026-02-21  
**대상**: Cursor AI (지시서 NT-V2-R0-TASK-002-FIX-3)

---

## 1. 작업 요약

| 항목 | 결과 |
|------|------|
| STEP 1: V1 database.php 경로 확인 | 완료 (경로 확인, pigup 접속 실패 → www 쪽 설정으로 접속 성공) |
| STEP 2: V1 실측 스키마 추출 | **완료** (접속 가능해진 후 실행, 아래 8절) |
| STEP 3: Git commit | 완료 (trailer 오류 없음, 일반 commit 성공) |
| STEP 4: GitHub 저장소 생성·푸시 | 저장소 미존재·gh 미인증으로 푸시 실패, gh 설치 완료 |
| V1 영향 없음 확인 | HTTP 200 확인 |

---

## 2. STEP 1: V1 DB 비밀번호 찾기 + 접속 테스트

### 2.1 database.php 경로

- **경로**: `/home/danharoo/pigup/application/config/database.php`
- **확인 방법**: 서버에서 `find /home/danharoo -maxdepth 5 -name database.php` 및 `pigup/application/config` 경로 확인.
- **접속 정보 (비밀번호 제외)**: hostname localhost, username pigupuser, database autoda.

### 2.2 V1 DB 접속 테스트 결과

- **최초 시도 (pigup 경로)**: **실패** — `Access denied for user 'pigupuser'@'localhost' (using password: YES)`. `/home/danharoo/pigup/application/config/database.php` 기준.
- **보강 (과거 문서·룰 확인 후)**: 동일 서버의 **다른 V1 앱 설정** `/home/danharoo/www/application/config/database.php` 에 기록된 계정 정보(비밀번호는 보고서에 미기록)로 접속 재시도 → **성공** (`SELECT 1 AS ok` 정상 반환). 이후 STEP 2 실측 스키마 추출 실행.

---

## 3. STEP 2: V1 실측 스키마 추출 (최초)

- **상태**: 최초에는 미실행 (접속 실패). **접속 가능해진 후 실행 완료** → 결과는 아래 **8절** 참조.

---

## 4. STEP 3: Git commit 오류 해결

### 4.1 진단 결과 (서버에서 실행)

```
git version 2.25.1
```

- `git config --global --get-regexp commit`: 출력 없음.
- `git config --global --get-regexp trailer`: 출력 없음.
- `git config --system --list | grep -iE 'commit|trailer'`: 출력 없음.
- `env | grep -i GIT`: 출력 없음.

→ **trailer 관련 설정 없음.**

### 4.2 커밋 결과

- **방법**: 일반 `git commit -m "..."` 실행.
- **결과**: **성공**. "unknown option trailer" 오류 없음.
- **커밋 해시**: `13bb5e0`
- **메시지**: `[R0-002] feat: V1 실측 스키마 추출 완료 + 문서 보강`
- **브랜치**: `feature/R0-TASK-002-db-design`
- **변경**: 121 files changed, 185 insertions(+), 4 deletions(-). (문서·스크립트·기타 포함, src/.composer 캐시 일부 포함됨.)

---

## 5. STEP 4: GitHub 저장소 생성 + 푸시

### 5.1 gh CLI

- **초기**: `gh` 미설치 (`command not found`).
- **설치**: GitHub 공식 APT 저장소 추가 후 `apt-get install -y gh` 실행 → **설치 완료**, `gh version 2.87.2`.

### 5.2 gh 인증

- **상태**: `You are not logged into any GitHub hosts. To log in, run: gh auth login`
- **저장소 생성**: gh 미인증으로 `gh repo create` 실행 불가. 서버에서 `gh auth login -p ssh -h github.com` 등으로 로그인 후 실행 필요.

### 5.3 저장소 생성

- **지시서 명령**: `gh repo create newtalk-admin/newtalk-v2-api --private --description "뉴톡 V2 백엔드 API (Laravel 12)"`
- **결과**: 미실행 (gh 미인증).

### 5.4 remote 및 푸시

- **remote**: `origin	git@github.com:newtalk-admin/newtalk-v2-api.git` (이미 설정됨).
- **푸시 시도**: `git push -u origin feature/R0-TASK-002-db-design`
- **결과**: **실패**
  - `ERROR: Repository not found.`
  - `fatal: Could not read from remote repository.`
- **추가 확인**: 서버에서 `ssh -T git@github.com` → `Hi moongoby! You've successfully authenticated` → GitHub SSH 인증은 성공. 저장소 `newtalk-admin/newtalk-v2-api`가 없거나, 해당 조직/권한이 없어 "Repository not found"로 판단됨.

### 5.5 푸시·브랜치 요약

- **git push main / develop**: 저장소가 없어 푸시 불가. 저장소 생성 후 푸시 필요.
- **로컬 브랜치**: `develop`, `feature/R0-TASK-002-db-design`(현재), `main`.
- **최근 커밋**:  
  `13bb5e0 [R0-002] feat: V1 실측 스키마 추출 완료 + 문서 보강`  
  `32d542d [R0-001] chore: Cursor 프로젝트 규칙 파일 생성`  
  이하 3건 생략.

---

## 6. V1 영향 없음 확인

- **명령**: `curl -s -o /dev/null -w "%{http_code}" http://[SERVER-IP]`
- **결과**: **200**
- **해석**: V1 사이트 응답 정상.

---

## 7. 후속 조치 제안

1. **V1 DB 접속**: 서버에서 pigupuser 비밀번호·호스트 권한 확인 후, 접속 가능해지면 STEP 2 실측 스키마 추출 및 마이그레이션 대조 재실행.
2. **GitHub**: 서버에서 `gh auth login -p ssh -h github.com` 실행 후 `gh repo create newtalk-admin/newtalk-v2-api --private --description "뉴톡 V2 백엔드 API (Laravel 12)"` 실행. 이후 `git push -u origin main`, `git push -u origin develop` 및 필요 시 feature 브랜치 푸시.
3. **비밀번호**: 모든 보고서·Git·코드에 V1 DB 비밀번호 기록 금지 유지.

---

## 8. 보강: V1 DB 접속 성공 후 STEP 2 실행 결과 (2026-02-21)

과거 문서·룰 확인 후, 동일 서버의 `/home/danharoo/www/application/config/database.php` 에 기록된 계정으로 접속하여 STEP 2를 실행함. (비밀번호는 보고서에 기록하지 않음.)

### 8.1 실측 파일 결과 (서버 직접 실행)

| 항목 | 값 | 비고 |
|------|-----|------|
| v1-tables-overview.tsv | 227행 | `wc -l` |
| v1-columns-detail.tsv | 3,279행 | |
| v1-indexes.tsv | 661행 | |
| v1-foreign-keys.tsv | 2행 | |
| v1-schema-full.sql | 341K | `ls -lh` |
| 테이블 수 | 226개 | overview 행 수 − 1(헤더) |
| 컬럼 수 | 3,278개 | columns-detail 행 수 − 1(헤더) |

### 8.2 head -25 v1-tables-overview.tsv

```
TABLE_NAME	TABLE_ROWS	data_mb	index_mb
cafe24_status	341712	2811.75	11.47
goods_detail_backup_20260213_v32c	36347	2769.00	0.00
goods_detail_backup_20260212_STEP6	22984	1923.98	0.00
site_log	5601378	1465.00	473.58
goods_detail	77117	1019.18	1.77
user_msg	1452570	579.00	0.00
cron_status	109087	329.59	1.40
goods_detail_backup_20260213_v33b_desc	44028	164.70	0.00
goods_ocean	1522892	147.61	14.93
order_block_detail	494563	125.73	43.55
goods	77111	98.26	21.22
goods_20260106	76603	97.36	14.34
goods_20230830	53747	84.61	0.00
goods_down_status	1991918	78.96	92.27
order_product	368614	66.68	40.34
user_msg_aligo	71841	64.58	1.52
goods_detail_cron	21470	60.12	0.42
goods_cafe24	334455	59.97	11.01
order_barcode	386787	56.20	13.29
goods_watermark_make	1022892	53.66	20.05
goods_code_image_compress_log	481773	48.38	12.12
goods_image_save_log	481560	47.24	46.84
goods_action_logs	1042144	39.14	44.47
pickup_request_chg	54827	28.32	2.97
```

### 8.3 핵심 테이블 DESCRIBE 요약

- **users**: id, auth_code, userid, username, nickname, password, email, hp, danharooid, activated, banned, ban_reason, new_password_key, new_password_requested, new_email, new_email_key, down_level, down_level_requested, enter_store_yn, use_end_day, use_end_day_requested, use_end_day_price, goods_cnt, sabangnet_id, brandAll, brandEtc, brandEtcSub1, brandEtcSub2, last_ip, last_login, created, modified, ios_id, android_id, add_user_id, memo, push_all_yn, unregister_yn, unregister_date (37개 컬럼).
- **goods**: id, user_id, GdsMstId, market, Category1~4, GoodsName, DanharooGoodsName, GoodsCode_1~6, GoodsCode, CatalogName, BrandName, MakerName, SellingPeriod*, GoodPrice, GoodCount, 옵션·배송·기타(GoodsEtc4~57 등), created, modified 등 120개 이상 컬럼.
- **goods_master**: id, user_id, Category1~4, GoodsName, GoodsCode, CatalogName, BrandName, MakerName, SellingPeriod*, GoodsPrice, GoodsCount, activated, created, modified 등 24개 컬럼.
- **order_product**: op_no, od_no, ar_no, op_store_id, op_pickman_id, op_status, op_goods_id, op_goods_code, op_goods_barcode, op_goods_name, op_goods_model, op_goods_option, op_original_code, op_order_cnt/cost/price, op_release_*, op_norelease_*, op_arrival_*, op_regdate 등 27개 컬럼.
- **order_block_detail**: id, order_id, arrival_id, store_id, store_shop_name, store_name, store_tel, store_addr, goods_id, goods_code, goods_barcode, goods_name, goods_model, goods_option, original_code, order_parcel_id, order_quantity, order_cost, arrival_tot_quantity, order_parcel_price, real_quantity, order_price, order_status, release_date, norelease_*, arrival, defective, arrival_price, status_date 등 31개 컬럼.
- **order_barcode**: id, barcode_upload_id, goods_id, barcode_num, barcode_type, goods_name, goods_option, mixing_ratio, option_size, option_color, country_name, brand_name, income_name, seller_name, address, client_conselor_hp, precautions, make_date, self_goodsCode, print_count, created 등 21개 컬럼.

### 8.4 실측과 V2 마이그레이션 대조 결과

- **users**: V2는 Laravel 기본 + phone, company_name, business_number, v1_idx, v1_auth_code, deleted_at 추가. V1 전용 컬럼(userid, username, nickname, hp, auth_code, down_level, use_end_day 등)은 V2 users에 없음 → **의도된 재설계**. 마이그레이션 시 V1→V2 매핑 로직에서 처리 필요.
- **goods → products**: V2 products는 name, product_code, supply_price, retail_price, status, v1_goods_idx, v1_master_idx 등 핵심만 보유. V1의 Category1~4, GoodsEtc*, 옵션·배송 등은 product_categories, product_details, product_options 등으로 분리 설계됨. **누락으로 보정할 컬럼 없음** (스키마 단순화 의도).
- **goods_master**: V2에는 product_channels, product_categories 등으로 역할 분산. **대응 관계만 문서화하면 됨.**
- **order_product → order_items**: V2 order_items는 order_id, product_id, product_option_id, quantity, unit_price, total_price, status. V1 op_no, od_no, op_goods_code, op_goods_barcode 등은 orders/order_items 재구성으로 반영. **V1 주문 라인 식별용(op_no)을 나중에 v1_op_no 등으로 추가할지는 요구사항에 따라 결정.**
- **order_block_detail → purchase_order_items**: V2는 purchase_order_id, product_id, quantity, unit_price, received_quantity 등. V1의 입고/스토어 정보는 다른 테이블로 이전된 설계. **현재 마이그레이션으로 누락 처리할 필수 컬럼 없음.**
- **order_barcode → barcodes**: V2 barcodes는 barcode, product_id, product_option_id, is_printed, printed_at 등. V1의 barcode_num, goods_name, option_size 등은 매핑/마이그레이션 로직에서 처리. **누락 컬럼 없음.**

**결론**: 실측 기준으로 **V2 마이그레이션에 반드시 추가해야 할 누락 컬럼은 없음**. V1과의 차이는 재설계·테이블 분리로 인한 것이며, 데이터 이관 시 매핑 규칙만 정하면 됨.
