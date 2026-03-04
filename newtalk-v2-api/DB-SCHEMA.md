# 뉴톡 V2 — DB 스키마 (newtalk_v2)

> 자동 생성 문서. 수동 편집 금지.
> 최초생성: 2026-02-23 / 최종갱신: 2026-03-04 (DOCS-SYNC-002 — 97테이블 반영)
> DB: newtalk_v2 (MySQL 8.0, Port 3307)
> 민감정보 없음 확인 완료.

---

## 테이블 목록

| # | 테이블명 | 설명 |
|---|---------|------|
| 1 | activity_logs | 활동 로그 |
| 2 | barcodes | 바코드 |
| 3 | brand_pages | 브랜드 페이지 |
| 4 | cache | Laravel 캐시 |
| 5 | cache_locks | 캐시 락 |
| 6 | cafe24_connections | Cafe24 연결 |
| 7 | cafe24_product_mappings | Cafe24 상품 매핑 |
| 8 | cafe24_syncs | Cafe24 동기화 |
| 9 | cart_items | 장바구니 아이템 |
| 10 | carts | 장바구니 |
| 11 | categories | 카테고리 |
| 12 | channel_connections | 채널 연결 |
| 13 | channel_product_mappings | 채널-상품 매핑 |
| 14 | code_masters | 코드 마스터 |
| 15 | content_media | 콘텐츠 미디어 |
| 16 | content_pipeline_jobs | 콘텐츠 파이프라인 작업 |
| 17 | content_pipelines | 콘텐츠 파이프라인 |
| 18 | content_product_tags | 콘텐츠-상품 태그 |
| 19 | contents | 콘텐츠 |
| 20 | contents_media | 콘텐츠 미디어(레거시) |
| 21 | contents_product_tags | 콘텐츠-상품 태그(레거시) |
| 22 | contract_items | 계약 아이템 |
| 23 | contracts | 계약 |
| 24 | conversation_participants | 대화 참여자 |
| 25 | conversations | 대화(DM) |
| 26 | coordinations | 코디네이션 |
| 27 | deposit_transactions | 예치금 거래 |
| 28 | deposits | 예치금 |
| 29 | downloads | 다운로드 |
| 30 | dropship_orders | 드롭십 주문 |
| 31 | failed_jobs | 실패 잡 |
| 32 | feed_items | 피드 아이템 |
| 33 | feed_likes | 피드 좋아요 |
| 34 | follows | 팔로우 |
| 35 | fulfillment_tasks | 풀필먼트 작업 |
| 36 | inbound_receipt_items | 입고 아이템 |
| 37 | inbound_receipts | 입고 영수증 |
| 38 | job_batches | 잡 배치 |
| 39 | jobs | 큐 잡 |
| 40 | message_logs | 메시지 로그 |
| 41 | message_reads | 메시지 읽음 |
| 42 | messages | 메시지 |
| 43 | migrations | 마이그레이션 |
| 44 | model_has_permissions | 모델-권한 |
| 45 | model_has_roles | 모델-역할 |
| 46 | order_items | 주문 아이템 |
| 47 | orders | 주문 |
| 48 | partner_prices | 거래처 가격 |
| 49 | partnerships | 거래처 제도 |
| 50 | password_reset_tokens | 비밀번호 재설정 토큰 |
| 51 | payment_logs | 결제 로그 |
| 52 | payments | 결제 |
| 53 | permissions | 권한 |
| 54 | personal_access_tokens | 개인 액세스 토큰 |
| 55 | pipeline_logs | 파이프라인 로그 |
| 56 | pipeline_media | 파이프라인 미디어 |
| 57 | product_categories | 상품-카테고리 |
| 58 | product_channels | 상품-채널 |
| 59 | product_details | 상품 상세 |
| 60 | product_images | 상품 이미지 |
| 61 | product_options | 상품 옵션 |
| 62 | product_scores | 상품 점수 |
| 63 | products | 상품 |
| 64 | purchase_order_items | 발주 아이템 |
| 65 | purchase_orders | 발주 |
| 66 | retail_profiles | 소매 프로필 |
| 67 | return_requests | 반품 요청 |
| 68 | role_has_permissions | 역할-권한 |
| 69 | roles | 역할 |
| 70 | sabangnet_logs | 사방넷 로그 |
| 71 | sabangnet_syncs | 사방넷 동기화 |
| 72 | sessions | 세션 |
| 73 | settings | 설정 |
| 74 | settlement_items | 정산 아이템 |
| 75 | settlement_logs | 정산 로그 |
| 76 | settlements | 정산 |
| 77 | shipment_items | 배송 아이템 |
| 78 | shipment_logs | 배송 로그 |
| 79 | shipments | 배송 |
| 80 | shipping_addresses | 배송지 |
| 81 | shooting_schedules | 촬영 일정 |
| 82 | short_comments | 쇼츠 댓글 |
| 83 | short_likes | 쇼츠 좋아요 |
| 84 | short_product_tags | 쇼츠-상품 태그 |
| 85 | short_views | 쇼츠 조회 |
| 86 | shorts | 쇼츠 |
| 87 | sns_connections | SNS 연결 |
| 88 | sns_post_analytics | SNS 게시물 분석 |
| 89 | sns_posts | SNS 게시물 |
| 90 | stories | 스토리 |
| 91 | story_views | 스토리 조회 |
| 92 | trade_applications | 거래처 신청 |
| 93 | trend_snapshots | 트렌드 스냅샷 |
| 94 | user_interests | 사용자 관심사 |
| 95 | users | 사용자 |
| 96 | wholesale_profiles | 도매 프로필 |
| 97 | wishlists | 찜 목록 |

**총 97개 테이블** (DOCS-SYNC-002, 2026-03-04 갱신)

---

## 테이블 상세

### activity_logs

```sql
       Table: activity_logs
CREATE TABLE `activity_logs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned DEFAULT NULL,
  `action` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `target_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `target_id` bigint unsigned DEFAULT NULL,
  `metadata` json DEFAULT NULL,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `activity_logs_user_id_foreign` (`user_id`),
  CONSTRAINT `activity_logs_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### barcodes

```sql
       Table: barcodes
CREATE TABLE `barcodes` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `product_id` bigint unsigned NOT NULL,
  `product_option_id` bigint unsigned DEFAULT NULL,
  `inbound_receipt_item_id` bigint unsigned DEFAULT NULL,
  `barcode` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'generated',
  `generated_by` bigint unsigned DEFAULT NULL,
  `generated_at` timestamp NULL DEFAULT NULL,
  `v1_barcode_idx` bigint unsigned DEFAULT NULL,
  `is_printed` tinyint(1) NOT NULL DEFAULT '0',
  `printed_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `barcodes_barcode_unique` (`barcode`),
  KEY `barcodes_product_id_foreign` (`product_id`),
  KEY `barcodes_product_option_id_foreign` (`product_option_id`),
  KEY `barcodes_inbound_receipt_item_id_foreign` (`inbound_receipt_item_id`),
  KEY `barcodes_v1_barcode_idx_index` (`v1_barcode_idx`),
  KEY `barcodes_generated_by_foreign` (`generated_by`),
  CONSTRAINT `barcodes_generated_by_foreign` FOREIGN KEY (`generated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `barcodes_inbound_receipt_item_id_foreign` FOREIGN KEY (`inbound_receipt_item_id`) REFERENCES `inbound_receipt_items` (`id`) ON DELETE SET NULL,
  CONSTRAINT `barcodes_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `barcodes_product_option_id_foreign` FOREIGN KEY (`product_option_id`) REFERENCES `product_options` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **10**건

### cache

```sql
       Table: cache
CREATE TABLE `cache` (
  `key` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expiration` int NOT NULL,
  PRIMARY KEY (`key`),
  KEY `cache_expiration_index` (`expiration`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### cache_locks

```sql
       Table: cache_locks
CREATE TABLE `cache_locks` (
  `key` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `owner` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `expiration` int NOT NULL,
  PRIMARY KEY (`key`),
  KEY `cache_locks_expiration_index` (`expiration`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### cafe24_syncs

```sql
       Table: cafe24_syncs
CREATE TABLE `cafe24_syncs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned DEFAULT NULL,
  `product_id` bigint unsigned DEFAULT NULL,
  `external_product_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `payload` json DEFAULT NULL,
  `synced_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cafe24_syncs_user_id_foreign` (`user_id`),
  KEY `cafe24_syncs_product_id_foreign` (`product_id`),
  CONSTRAINT `cafe24_syncs_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL,
  CONSTRAINT `cafe24_syncs_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### categories

```sql
       Table: categories
CREATE TABLE `categories` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `parent_id` bigint unsigned DEFAULT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sort_order` smallint unsigned NOT NULL DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `categories_parent_id_index` (`parent_id`),
  KEY `categories_code_index` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **1**건

### code_masters

```sql
       Table: code_masters
CREATE TABLE `code_masters` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `group` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sort_order` smallint unsigned NOT NULL DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `meta` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_masters_group_code_unique` (`group`,`code`),
  KEY `code_masters_group_index` (`group`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### content_pipelines

```sql
       Table: content_pipelines
CREATE TABLE `content_pipelines` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `product_id` bigint unsigned NOT NULL,
  `current_step` tinyint unsigned NOT NULL DEFAULT '1',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `step_data` json DEFAULT NULL,
  `assigned_md_id` bigint unsigned DEFAULT NULL,
  `assigned_outsource_id` bigint unsigned DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `content_pipelines_product_id_foreign` (`product_id`),
  KEY `content_pipelines_assigned_md_id_foreign` (`assigned_md_id`),
  KEY `content_pipelines_assigned_outsource_id_foreign` (`assigned_outsource_id`),
  CONSTRAINT `content_pipelines_assigned_md_id_foreign` FOREIGN KEY (`assigned_md_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `content_pipelines_assigned_outsource_id_foreign` FOREIGN KEY (`assigned_outsource_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `content_pipelines_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### contract_items

```sql
       Table: contract_items
CREATE TABLE `contract_items` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `contract_id` bigint unsigned NOT NULL,
  `product_id` bigint unsigned DEFAULT NULL,
  `quantity` smallint unsigned NOT NULL DEFAULT '0',
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `contract_items_contract_id_foreign` (`contract_id`),
  KEY `contract_items_product_id_foreign` (`product_id`),
  CONSTRAINT `contract_items_contract_id_foreign` FOREIGN KEY (`contract_id`) REFERENCES `contracts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `contract_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### contracts

```sql
       Table: contracts
CREATE TABLE `contracts` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `wholesale_profile_id` bigint unsigned NOT NULL,
  `monthly_fee` int unsigned NOT NULL,
  `min_products` smallint unsigned NOT NULL DEFAULT '0',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `memo` text COLLATE utf8mb4_unicode_ci,
  `v1_contract_id` bigint unsigned DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `contracts_wholesale_profile_id_foreign` (`wholesale_profile_id`),
  KEY `contracts_v1_contract_id_index` (`v1_contract_id`),
  CONSTRAINT `contracts_wholesale_profile_id_foreign` FOREIGN KEY (`wholesale_profile_id`) REFERENCES `wholesale_profiles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### coordinations

```sql
       Table: coordinations
CREATE TABLE `coordinations` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `content_pipeline_id` bigint unsigned DEFAULT NULL,
  `product_id` bigint unsigned DEFAULT NULL,
  `coordinator_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `items` text COLLATE utf8mb4_unicode_ci,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `coordinations_content_pipeline_id_foreign` (`content_pipeline_id`),
  KEY `coordinations_product_id_foreign` (`product_id`),
  CONSTRAINT `coordinations_content_pipeline_id_foreign` FOREIGN KEY (`content_pipeline_id`) REFERENCES `content_pipelines` (`id`) ON DELETE SET NULL,
  CONSTRAINT `coordinations_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### deposit_transactions

```sql
       Table: deposit_transactions
CREATE TABLE `deposit_transactions` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `deposit_id` bigint unsigned NOT NULL,
  `type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` bigint NOT NULL,
  `balance_after` bigint NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reference_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reference_id` bigint unsigned DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `deposit_transactions_deposit_id_foreign` (`deposit_id`),
  CONSTRAINT `deposit_transactions_deposit_id_foreign` FOREIGN KEY (`deposit_id`) REFERENCES `deposits` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### deposits

```sql
       Table: deposits
CREATE TABLE `deposits` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `balance` bigint NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `deposits_user_id_foreign` (`user_id`),
  CONSTRAINT `deposits_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### downloads

```sql
       Table: downloads
CREATE TABLE `downloads` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `product_id` bigint unsigned NOT NULL,
  `download_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'image',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `downloads_user_id_foreign` (`user_id`),
  KEY `downloads_product_id_foreign` (`product_id`),
  CONSTRAINT `downloads_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `downloads_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### failed_jobs

```sql
       Table: failed_jobs
CREATE TABLE `failed_jobs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `uuid` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `connection` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `queue` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `payload` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `exception` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `failed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `failed_jobs_uuid_unique` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### feed_items

```sql
       Table: feed_items
CREATE TABLE `feed_items` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `type` enum('product','content','story','shorts') COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `media_url` varchar(2048) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `media_type` enum('image','video') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_id` bigint unsigned DEFAULT NULL,
  `like_count` int unsigned NOT NULL DEFAULT '0',
  `comment_count` int unsigned NOT NULL DEFAULT '0',
  `view_count` int unsigned NOT NULL DEFAULT '0',
  `is_pinned` tinyint(1) NOT NULL DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `published_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `feed_items_product_id_foreign` (`product_id`),
  KEY `feed_items_user_id_is_active_published_at_index` (`user_id`,`is_active`,`published_at`),
  KEY `feed_items_type_is_active_published_at_index` (`type`,`is_active`,`published_at`),
  CONSTRAINT `feed_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL,
  CONSTRAINT `feed_items_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **3**건

### feed_likes

```sql
       Table: feed_likes
CREATE TABLE `feed_likes` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `feed_item_id` bigint unsigned NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `feed_likes_user_id_feed_item_id_unique` (`user_id`,`feed_item_id`),
  KEY `feed_likes_feed_item_id_foreign` (`feed_item_id`),
  CONSTRAINT `feed_likes_feed_item_id_foreign` FOREIGN KEY (`feed_item_id`) REFERENCES `feed_items` (`id`) ON DELETE CASCADE,
  CONSTRAINT `feed_likes_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **1**건

### follows

```sql
       Table: follows
CREATE TABLE `follows` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `follower_id` bigint unsigned NOT NULL,
  `following_id` bigint unsigned NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `follows_follower_id_following_id_unique` (`follower_id`,`following_id`),
  KEY `follows_following_id_index` (`following_id`),
  CONSTRAINT `follows_follower_id_foreign` FOREIGN KEY (`follower_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `follows_following_id_foreign` FOREIGN KEY (`following_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **1**건

### inbound_receipt_items

```sql
       Table: inbound_receipt_items
CREATE TABLE `inbound_receipt_items` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `inbound_receipt_id` bigint unsigned NOT NULL,
  `purchase_order_item_id` bigint unsigned DEFAULT NULL,
  `product_id` bigint unsigned NOT NULL,
  `product_option_id` bigint unsigned DEFAULT NULL,
  `quantity` smallint unsigned NOT NULL DEFAULT '0',
  `defective_quantity` int unsigned NOT NULL DEFAULT '0',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `condition` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'good',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inbound_receipt_items_inbound_receipt_id_foreign` (`inbound_receipt_id`),
  KEY `inbound_receipt_items_product_id_foreign` (`product_id`),
  KEY `inbound_receipt_items_product_option_id_foreign` (`product_option_id`),
  KEY `inbound_receipt_items_purchase_order_item_id_foreign` (`purchase_order_item_id`),
  CONSTRAINT `inbound_receipt_items_inbound_receipt_id_foreign` FOREIGN KEY (`inbound_receipt_id`) REFERENCES `inbound_receipts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `inbound_receipt_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `inbound_receipt_items_product_option_id_foreign` FOREIGN KEY (`product_option_id`) REFERENCES `product_options` (`id`) ON DELETE SET NULL,
  CONSTRAINT `inbound_receipt_items_purchase_order_item_id_foreign` FOREIGN KEY (`purchase_order_item_id`) REFERENCES `purchase_order_items` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **33**건

### inbound_receipts

```sql
       Table: inbound_receipts
CREATE TABLE `inbound_receipts` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `purchase_order_id` bigint unsigned DEFAULT NULL,
  `user_id` bigint unsigned NOT NULL,
  `receipt_number` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `received_date` date DEFAULT NULL,
  `total_quantity` int unsigned NOT NULL DEFAULT '0',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `v1_block_idx` bigint unsigned DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `received_at` timestamp NULL DEFAULT NULL,
  `memo` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `inbound_receipts_receipt_number_unique` (`receipt_number`),
  KEY `inbound_receipts_purchase_order_id_foreign` (`purchase_order_id`),
  KEY `inbound_receipts_user_id_foreign` (`user_id`),
  KEY `inbound_receipts_v1_block_idx_index` (`v1_block_idx`),
  CONSTRAINT `inbound_receipts_purchase_order_id_foreign` FOREIGN KEY (`purchase_order_id`) REFERENCES `purchase_orders` (`id`) ON DELETE SET NULL,
  CONSTRAINT `inbound_receipts_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **18**건

### job_batches

```sql
       Table: job_batches
CREATE TABLE `job_batches` (
  `id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_jobs` int NOT NULL,
  `pending_jobs` int NOT NULL,
  `failed_jobs` int NOT NULL,
  `failed_job_ids` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `options` mediumtext COLLATE utf8mb4_unicode_ci,
  `cancelled_at` int DEFAULT NULL,
  `created_at` int NOT NULL,
  `finished_at` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### jobs

```sql
       Table: jobs
CREATE TABLE `jobs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `queue` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `payload` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `attempts` tinyint unsigned NOT NULL,
  `reserved_at` int unsigned DEFAULT NULL,
  `available_at` int unsigned NOT NULL,
  `created_at` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `jobs_queue_index` (`queue`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### message_logs

```sql
       Table: message_logs
CREATE TABLE `message_logs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned DEFAULT NULL,
  `channel` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'aligo',
  `type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `recipient` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `content` text COLLATE utf8mb4_unicode_ci,
  `external_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'sent',
  `sent_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `message_logs_user_id_foreign` (`user_id`),
  CONSTRAINT `message_logs_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### migrations

```sql
       Table: migrations
CREATE TABLE `migrations` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `migration` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `batch` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **49**건

### model_has_permissions

```sql
       Table: model_has_permissions
CREATE TABLE `model_has_permissions` (
  `permission_id` bigint unsigned NOT NULL,
  `model_type` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`permission_id`,`model_id`,`model_type`),
  KEY `model_has_permissions_model_id_model_type_index` (`model_id`,`model_type`),
  CONSTRAINT `model_has_permissions_permission_id_foreign` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### model_has_roles

```sql
       Table: model_has_roles
CREATE TABLE `model_has_roles` (
  `role_id` bigint unsigned NOT NULL,
  `model_type` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`role_id`,`model_id`,`model_type`),
  KEY `model_has_roles_model_id_model_type_index` (`model_id`,`model_type`),
  CONSTRAINT `model_has_roles_role_id_foreign` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **17**건

### order_items

```sql
       Table: order_items
CREATE TABLE `order_items` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `order_id` bigint unsigned NOT NULL,
  `product_id` bigint unsigned NOT NULL,
  `product_option_id` bigint unsigned DEFAULT NULL,
  `quantity` smallint unsigned NOT NULL DEFAULT '1',
  `unit_price` int unsigned NOT NULL DEFAULT '0',
  `total_price` int unsigned NOT NULL DEFAULT '0',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `order_items_order_id_foreign` (`order_id`),
  KEY `order_items_product_id_foreign` (`product_id`),
  KEY `order_items_product_option_id_foreign` (`product_option_id`),
  CONSTRAINT `order_items_order_id_foreign` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `order_items_product_option_id_foreign` FOREIGN KEY (`product_option_id`) REFERENCES `product_options` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### orders

```sql
       Table: orders
CREATE TABLE `orders` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `order_number` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `total_amount` int unsigned NOT NULL DEFAULT '0',
  `payment_method` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `shipping_address` text COLLATE utf8mb4_unicode_ci,
  `recipient_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `recipient_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `memo` text COLLATE utf8mb4_unicode_ci,
  `v1_order_idx` bigint unsigned DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `orders_order_number_unique` (`order_number`),
  KEY `orders_user_id_foreign` (`user_id`),
  KEY `orders_v1_order_idx_index` (`v1_order_idx`),
  CONSTRAINT `orders_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### password_reset_tokens

```sql
       Table: password_reset_tokens
CREATE TABLE `password_reset_tokens` (
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `token` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### permissions

```sql
       Table: permissions
CREATE TABLE `permissions` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `guard_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `permissions_name_guard_name_unique` (`name`,`guard_name`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **36**건

### personal_access_tokens

```sql
       Table: personal_access_tokens
CREATE TABLE `personal_access_tokens` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `tokenable_type` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tokenable_id` bigint unsigned NOT NULL,
  `name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `token` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `abilities` text COLLATE utf8mb4_unicode_ci,
  `last_used_at` timestamp NULL DEFAULT NULL,
  `expires_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `personal_access_tokens_token_unique` (`token`),
  KEY `personal_access_tokens_tokenable_type_tokenable_id_index` (`tokenable_type`,`tokenable_id`),
  KEY `personal_access_tokens_expires_at_index` (`expires_at`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **6**건

### product_categories

```sql
       Table: product_categories
CREATE TABLE `product_categories` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `product_id` bigint unsigned NOT NULL,
  `category_id` bigint unsigned NOT NULL,
  `sort_order` smallint unsigned NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_categories_product_id_category_id_unique` (`product_id`,`category_id`),
  KEY `product_categories_category_id_foreign` (`category_id`),
  CONSTRAINT `product_categories_category_id_foreign` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE,
  CONSTRAINT `product_categories_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### product_channels

```sql
       Table: product_channels
CREATE TABLE `product_channels` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `product_id` bigint unsigned NOT NULL,
  `channel` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `external_product_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `channel_data` json DEFAULT NULL,
  `synced_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_channels_product_id_channel_unique` (`product_id`,`channel`),
  CONSTRAINT `product_channels_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **2**건

### product_details

```sql
       Table: product_details
CREATE TABLE `product_details` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `product_id` bigint unsigned NOT NULL,
  `html_content` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `version` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `product_details_product_id_foreign` (`product_id`),
  CONSTRAINT `product_details_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **1**건

### product_images

```sql
       Table: product_images
CREATE TABLE `product_images` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `product_id` bigint unsigned NOT NULL,
  `type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `path` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `filename` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_size` int unsigned NOT NULL DEFAULT '0',
  `sort_order` smallint unsigned NOT NULL DEFAULT '0',
  `is_primary` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `product_images_product_id_foreign` (`product_id`),
  CONSTRAINT `product_images_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **1**건

### product_options

```sql
       Table: product_options
CREATE TABLE `product_options` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `product_id` bigint unsigned NOT NULL,
  `color` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `size` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `option_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `stock` int unsigned NOT NULL DEFAULT '0',
  `additional_price` int unsigned NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `product_options_product_id_foreign` (`product_id`),
  CONSTRAINT `product_options_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **3**건

### products

```sql
       Table: products
CREATE TABLE `products` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `wholesale_profile_id` bigint unsigned DEFAULT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `brand` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `supply_price` int unsigned NOT NULL DEFAULT '0',
  `retail_price` int unsigned NOT NULL DEFAULT '0',
  `wholesale_price` int unsigned NOT NULL DEFAULT '0',
  `purchase_price` int unsigned NOT NULL DEFAULT '0',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `v1_goods_idx` bigint unsigned DEFAULT NULL,
  `v1_master_idx` bigint unsigned DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `products_product_code_unique` (`product_code`),
  KEY `products_user_id_foreign` (`user_id`),
  KEY `products_wholesale_profile_id_foreign` (`wholesale_profile_id`),
  KEY `products_v1_goods_idx_index` (`v1_goods_idx`),
  KEY `products_v1_master_idx_index` (`v1_master_idx`),
  CONSTRAINT `products_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `products_wholesale_profile_id_foreign` FOREIGN KEY (`wholesale_profile_id`) REFERENCES `wholesale_profiles` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **16**건

### purchase_order_items

```sql
       Table: purchase_order_items
CREATE TABLE `purchase_order_items` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `purchase_order_id` bigint unsigned NOT NULL,
  `product_id` bigint unsigned NOT NULL,
  `product_option_id` bigint unsigned DEFAULT NULL,
  `quantity` smallint unsigned NOT NULL DEFAULT '1',
  `unit_price` int unsigned NOT NULL DEFAULT '0',
  `subtotal` decimal(12,0) NOT NULL DEFAULT '0',
  `received_quantity` smallint unsigned NOT NULL DEFAULT '0',
  `status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `purchase_order_items_purchase_order_id_foreign` (`purchase_order_id`),
  KEY `purchase_order_items_product_id_foreign` (`product_id`),
  KEY `purchase_order_items_product_option_id_foreign` (`product_option_id`),
  CONSTRAINT `purchase_order_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `purchase_order_items_product_option_id_foreign` FOREIGN KEY (`product_option_id`) REFERENCES `product_options` (`id`) ON DELETE SET NULL,
  CONSTRAINT `purchase_order_items_purchase_order_id_foreign` FOREIGN KEY (`purchase_order_id`) REFERENCES `purchase_orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=122 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **121**건

### purchase_orders

```sql
       Table: purchase_orders
CREATE TABLE `purchase_orders` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `approved_by` bigint unsigned DEFAULT NULL,
  `wholesale_profile_id` bigint unsigned NOT NULL,
  `po_number` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft',
  `total_amount` int unsigned NOT NULL DEFAULT '0',
  `total_quantity` int unsigned NOT NULL DEFAULT '0',
  `order_date` date DEFAULT NULL,
  `expected_date` date DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `v1_order_idx` bigint unsigned DEFAULT NULL,
  `memo` text COLLATE utf8mb4_unicode_ci,
  `v1_order_block_id` bigint unsigned DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `purchase_orders_po_number_unique` (`po_number`),
  KEY `purchase_orders_user_id_foreign` (`user_id`),
  KEY `purchase_orders_wholesale_profile_id_foreign` (`wholesale_profile_id`),
  KEY `purchase_orders_v1_order_block_id_index` (`v1_order_block_id`),
  KEY `purchase_orders_v1_order_idx_index` (`v1_order_idx`),
  KEY `purchase_orders_status_wholesale_profile_id_order_date_index` (`status`,`wholesale_profile_id`,`order_date`),
  CONSTRAINT `purchase_orders_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `purchase_orders_wholesale_profile_id_foreign` FOREIGN KEY (`wholesale_profile_id`) REFERENCES `wholesale_profiles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **36**건

### retail_profiles

```sql
       Table: retail_profiles
CREATE TABLE `retail_profiles` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `shop_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `memo` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `retail_profiles_user_id_foreign` (`user_id`),
  CONSTRAINT `retail_profiles_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### role_has_permissions

```sql
       Table: role_has_permissions
CREATE TABLE `role_has_permissions` (
  `permission_id` bigint unsigned NOT NULL,
  `role_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`permission_id`,`role_id`),
  KEY `role_has_permissions_role_id_foreign` (`role_id`),
  CONSTRAINT `role_has_permissions_permission_id_foreign` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `role_has_permissions_role_id_foreign` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **65**건

### roles

```sql
       Table: roles
CREATE TABLE `roles` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `guard_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `roles_name_guard_name_unique` (`name`,`guard_name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **6**건

### sabangnet_logs

```sql
       Table: sabangnet_logs
CREATE TABLE `sabangnet_logs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `sabangnet_sync_id` bigint unsigned DEFAULT NULL,
  `action` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `request_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `response_code` smallint unsigned DEFAULT NULL,
  `request_payload` json DEFAULT NULL,
  `response_payload` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sabangnet_logs_sabangnet_sync_id_foreign` (`sabangnet_sync_id`),
  CONSTRAINT `sabangnet_logs_sabangnet_sync_id_foreign` FOREIGN KEY (`sabangnet_sync_id`) REFERENCES `sabangnet_syncs` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### sabangnet_syncs

```sql
       Table: sabangnet_syncs
CREATE TABLE `sabangnet_syncs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned DEFAULT NULL,
  `sabangnet_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `last_synced_at` timestamp NULL DEFAULT NULL,
  `config` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sabangnet_syncs_user_id_foreign` (`user_id`),
  CONSTRAINT `sabangnet_syncs_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### sessions

```sql
       Table: sessions
CREATE TABLE `sessions` (
  `id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` bigint unsigned DEFAULT NULL,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` text COLLATE utf8mb4_unicode_ci,
  `payload` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_activity` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sessions_user_id_index` (`user_id`),
  KEY `sessions_last_activity_index` (`last_activity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### settings

```sql
       Table: settings
CREATE TABLE `settings` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `group` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `key` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` text COLLATE utf8mb4_unicode_ci,
  `type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'string',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `settings_group_key_unique` (`group`,`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### shipment_items

```sql
       Table: shipment_items
CREATE TABLE `shipment_items` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `shipment_id` bigint unsigned NOT NULL,
  `order_item_id` bigint unsigned DEFAULT NULL,
  `product_id` bigint unsigned NOT NULL,
  `product_option_id` bigint unsigned DEFAULT NULL,
  `quantity` smallint unsigned NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `shipment_items_shipment_id_foreign` (`shipment_id`),
  KEY `shipment_items_order_item_id_foreign` (`order_item_id`),
  KEY `shipment_items_product_id_foreign` (`product_id`),
  KEY `shipment_items_product_option_id_foreign` (`product_option_id`),
  CONSTRAINT `shipment_items_order_item_id_foreign` FOREIGN KEY (`order_item_id`) REFERENCES `order_items` (`id`) ON DELETE SET NULL,
  CONSTRAINT `shipment_items_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `shipment_items_product_option_id_foreign` FOREIGN KEY (`product_option_id`) REFERENCES `product_options` (`id`) ON DELETE SET NULL,
  CONSTRAINT `shipment_items_shipment_id_foreign` FOREIGN KEY (`shipment_id`) REFERENCES `shipments` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### shipments

```sql
       Table: shipments
CREATE TABLE `shipments` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `order_id` bigint unsigned NOT NULL,
  `carrier` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tracking_number` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `shipping_fee` int unsigned NOT NULL DEFAULT '3000',
  `shipped_at` timestamp NULL DEFAULT NULL,
  `delivered_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `shipments_order_id_foreign` (`order_id`),
  CONSTRAINT `shipments_order_id_foreign` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### shooting_schedules

```sql
       Table: shooting_schedules
CREATE TABLE `shooting_schedules` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `content_pipeline_id` bigint unsigned DEFAULT NULL,
  `product_id` bigint unsigned DEFAULT NULL,
  `scheduled_date` date NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `location` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `memo` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `shooting_schedules_content_pipeline_id_foreign` (`content_pipeline_id`),
  KEY `shooting_schedules_product_id_foreign` (`product_id`),
  CONSTRAINT `shooting_schedules_content_pipeline_id_foreign` FOREIGN KEY (`content_pipeline_id`) REFERENCES `content_pipelines` (`id`) ON DELETE SET NULL,
  CONSTRAINT `shooting_schedules_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

### users

```sql
       Table: users
CREATE TABLE `users` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `company_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `business_number` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email_verified_at` timestamp NULL DEFAULT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `remember_token` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `v1_idx` bigint unsigned DEFAULT NULL,
  `v1_auth_code` tinyint unsigned DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_email_unique` (`email`),
  KEY `users_v1_idx_index` (`v1_idx`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **17**건

### wholesale_profiles

```sql
       Table: wholesale_profiles
CREATE TABLE `wholesale_profiles` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `shop_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `shop_location` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `kakao_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `memo` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `wholesale_profiles_user_id_foreign` (`user_id`),
  CONSTRAINT `wholesale_profiles_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **4**건

### wishlists

```sql
       Table: wishlists
CREATE TABLE `wishlists` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `product_id` bigint unsigned NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wishlists_user_id_product_id_unique` (`user_id`,`product_id`),
  KEY `wishlists_product_id_foreign` (`product_id`),
  CONSTRAINT `wishlists_product_id_foreign` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `wishlists_user_id_foreign` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```

레코드 수: **0**건

---

## 외래키(FK) 관계 요약

| 테이블 | FK 컬럼 | 참조 테이블 | 참조 컬럼 |
|--------|---------|------------|----------|
| activity_logs | user_id | users | id |
| barcodes | generated_by | users | id |
| barcodes | inbound_receipt_item_id | inbound_receipt_items | id |
| barcodes | product_id | products | id |
| barcodes | product_option_id | product_options | id |
| cafe24_syncs | product_id | products | id |
| cafe24_syncs | user_id | users | id |
| content_pipelines | assigned_md_id | users | id |
| content_pipelines | assigned_outsource_id | users | id |
| content_pipelines | product_id | products | id |
| contract_items | contract_id | contracts | id |
| contract_items | product_id | products | id |
| contracts | wholesale_profile_id | wholesale_profiles | id |
| coordinations | content_pipeline_id | content_pipelines | id |
| coordinations | product_id | products | id |
| deposit_transactions | deposit_id | deposits | id |
| deposits | user_id | users | id |
| downloads | product_id | products | id |
| downloads | user_id | users | id |
| feed_items | product_id | products | id |
| feed_items | user_id | users | id |
| feed_likes | feed_item_id | feed_items | id |
| feed_likes | user_id | users | id |
| follows | follower_id | users | id |
| follows | following_id | users | id |
| inbound_receipt_items | inbound_receipt_id | inbound_receipts | id |
| inbound_receipt_items | product_id | products | id |
| inbound_receipt_items | product_option_id | product_options | id |
| inbound_receipt_items | purchase_order_item_id | purchase_order_items | id |
| inbound_receipts | purchase_order_id | purchase_orders | id |
| inbound_receipts | user_id | users | id |
| message_logs | user_id | users | id |
| model_has_permissions | permission_id | permissions | id |
| model_has_roles | role_id | roles | id |
| order_items | order_id | orders | id |
| order_items | product_id | products | id |
| order_items | product_option_id | product_options | id |
| orders | user_id | users | id |
| product_categories | category_id | categories | id |
| product_categories | product_id | products | id |
| product_channels | product_id | products | id |
| product_details | product_id | products | id |
| product_images | product_id | products | id |
| product_options | product_id | products | id |
| products | user_id | users | id |
| products | wholesale_profile_id | wholesale_profiles | id |
| purchase_order_items | product_id | products | id |
| purchase_order_items | product_option_id | product_options | id |
| purchase_order_items | purchase_order_id | purchase_orders | id |
| purchase_orders | user_id | users | id |
| purchase_orders | wholesale_profile_id | wholesale_profiles | id |
| retail_profiles | user_id | users | id |
| role_has_permissions | permission_id | permissions | id |
| role_has_permissions | role_id | roles | id |
| sabangnet_logs | sabangnet_sync_id | sabangnet_syncs | id |
| sabangnet_syncs | user_id | users | id |
| shipment_items | order_item_id | order_items | id |
| shipment_items | product_id | products | id |
| shipment_items | product_option_id | product_options | id |
| shipment_items | shipment_id | shipments | id |
| shipments | order_id | orders | id |
| shooting_schedules | content_pipeline_id | content_pipelines | id |
| shooting_schedules | product_id | products | id |
| wholesale_profiles | user_id | users | id |
| wishlists | product_id | products | id |
| wishlists | user_id | users | id |

---

## 인덱스 요약

| 테이블 | 인덱스명 | 유니크 | 컬럼 |
|--------|---------|--------|------|
| activity_logs | activity_logs_user_id_foreign | N | user_id |
| activity_logs | PRIMARY | Y | id |
| barcodes | barcodes_barcode_unique | Y | barcode |
| barcodes | barcodes_generated_by_foreign | N | generated_by |
| barcodes | barcodes_inbound_receipt_item_id_foreign | N | inbound_receipt_item_id |
| barcodes | barcodes_product_id_foreign | N | product_id |
| barcodes | barcodes_product_option_id_foreign | N | product_option_id |
| barcodes | barcodes_v1_barcode_idx_index | N | v1_barcode_idx |
| barcodes | PRIMARY | Y | id |
| cache | cache_expiration_index | N | expiration |
| cache | PRIMARY | Y | key |
| cache_locks | cache_locks_expiration_index | N | expiration |
| cache_locks | PRIMARY | Y | key |
| cafe24_syncs | cafe24_syncs_product_id_foreign | N | product_id |
| cafe24_syncs | cafe24_syncs_user_id_foreign | N | user_id |
| cafe24_syncs | PRIMARY | Y | id |
| categories | categories_code_index | N | code |
| categories | categories_parent_id_index | N | parent_id |
| categories | PRIMARY | Y | id |
| code_masters | code_masters_group_code_unique | Y | group, code |
| code_masters | code_masters_group_index | N | group |
| code_masters | PRIMARY | Y | id |
| content_pipelines | content_pipelines_assigned_md_id_foreign | N | assigned_md_id |
| content_pipelines | content_pipelines_assigned_outsource_id_foreign | N | assigned_outsource_id |
| content_pipelines | content_pipelines_product_id_foreign | N | product_id |
| content_pipelines | PRIMARY | Y | id |
| contract_items | contract_items_contract_id_foreign | N | contract_id |
| contract_items | contract_items_product_id_foreign | N | product_id |
| contract_items | PRIMARY | Y | id |
| contracts | contracts_v1_contract_id_index | N | v1_contract_id |
| contracts | contracts_wholesale_profile_id_foreign | N | wholesale_profile_id |
| contracts | PRIMARY | Y | id |
| coordinations | coordinations_content_pipeline_id_foreign | N | content_pipeline_id |
| coordinations | coordinations_product_id_foreign | N | product_id |
| coordinations | PRIMARY | Y | id |
| deposit_transactions | deposit_transactions_deposit_id_foreign | N | deposit_id |
| deposit_transactions | PRIMARY | Y | id |
| deposits | deposits_user_id_foreign | N | user_id |
| deposits | PRIMARY | Y | id |
| downloads | downloads_product_id_foreign | N | product_id |
| downloads | downloads_user_id_foreign | N | user_id |
| downloads | PRIMARY | Y | id |
| failed_jobs | failed_jobs_uuid_unique | Y | uuid |
| failed_jobs | PRIMARY | Y | id |
| feed_items | feed_items_product_id_foreign | N | product_id |
| feed_items | feed_items_type_is_active_published_at_index | N | type, is_active, published_at |
| feed_items | feed_items_user_id_is_active_published_at_index | N | user_id, is_active, published_at |
| feed_items | PRIMARY | Y | id |
| feed_likes | feed_likes_feed_item_id_foreign | N | feed_item_id |
| feed_likes | feed_likes_user_id_feed_item_id_unique | Y | user_id, feed_item_id |
| feed_likes | PRIMARY | Y | id |
| follows | follows_follower_id_following_id_unique | Y | follower_id, following_id |
| follows | follows_following_id_index | N | following_id |
| follows | PRIMARY | Y | id |
| inbound_receipt_items | inbound_receipt_items_inbound_receipt_id_foreign | N | inbound_receipt_id |
| inbound_receipt_items | inbound_receipt_items_product_id_foreign | N | product_id |
| inbound_receipt_items | inbound_receipt_items_product_option_id_foreign | N | product_option_id |
| inbound_receipt_items | inbound_receipt_items_purchase_order_item_id_foreign | N | purchase_order_item_id |
| inbound_receipt_items | PRIMARY | Y | id |
| inbound_receipts | inbound_receipts_purchase_order_id_foreign | N | purchase_order_id |
| inbound_receipts | inbound_receipts_receipt_number_unique | Y | receipt_number |
| inbound_receipts | inbound_receipts_user_id_foreign | N | user_id |
| inbound_receipts | inbound_receipts_v1_block_idx_index | N | v1_block_idx |
| inbound_receipts | PRIMARY | Y | id |
| job_batches | PRIMARY | Y | id |
| jobs | jobs_queue_index | N | queue |
| jobs | PRIMARY | Y | id |
| message_logs | message_logs_user_id_foreign | N | user_id |
| message_logs | PRIMARY | Y | id |
| migrations | PRIMARY | Y | id |
| model_has_permissions | model_has_permissions_model_id_model_type_index | N | model_id, model_type |
| model_has_permissions | PRIMARY | Y | permission_id, model_id, model_type |
| model_has_roles | model_has_roles_model_id_model_type_index | N | model_id, model_type |
| model_has_roles | PRIMARY | Y | role_id, model_id, model_type |
| order_items | order_items_order_id_foreign | N | order_id |
| order_items | order_items_product_id_foreign | N | product_id |
| order_items | order_items_product_option_id_foreign | N | product_option_id |
| order_items | PRIMARY | Y | id |
| orders | orders_order_number_unique | Y | order_number |
| orders | orders_user_id_foreign | N | user_id |
| orders | orders_v1_order_idx_index | N | v1_order_idx |
| orders | PRIMARY | Y | id |
| password_reset_tokens | PRIMARY | Y | email |
| permissions | permissions_name_guard_name_unique | Y | name, guard_name |
| permissions | PRIMARY | Y | id |
| personal_access_tokens | personal_access_tokens_expires_at_index | N | expires_at |
| personal_access_tokens | personal_access_tokens_token_unique | Y | token |
| personal_access_tokens | personal_access_tokens_tokenable_type_tokenable_id_index | N | tokenable_type, tokenable_id |
| personal_access_tokens | PRIMARY | Y | id |
| product_categories | PRIMARY | Y | id |
| product_categories | product_categories_category_id_foreign | N | category_id |
| product_categories | product_categories_product_id_category_id_unique | Y | product_id, category_id |
| product_channels | PRIMARY | Y | id |
| product_channels | product_channels_product_id_channel_unique | Y | product_id, channel |
| product_details | PRIMARY | Y | id |
| product_details | product_details_product_id_foreign | N | product_id |
| product_images | PRIMARY | Y | id |
| product_images | product_images_product_id_foreign | N | product_id |
| product_options | PRIMARY | Y | id |
| product_options | product_options_product_id_foreign | N | product_id |
| products | PRIMARY | Y | id |
| products | products_product_code_unique | Y | product_code |
| products | products_user_id_foreign | N | user_id |
| products | products_v1_goods_idx_index | N | v1_goods_idx |
| products | products_v1_master_idx_index | N | v1_master_idx |
| products | products_wholesale_profile_id_foreign | N | wholesale_profile_id |
| purchase_order_items | PRIMARY | Y | id |
| purchase_order_items | purchase_order_items_product_id_foreign | N | product_id |
| purchase_order_items | purchase_order_items_product_option_id_foreign | N | product_option_id |
| purchase_order_items | purchase_order_items_purchase_order_id_foreign | N | purchase_order_id |
| purchase_orders | PRIMARY | Y | id |
| purchase_orders | purchase_orders_po_number_unique | Y | po_number |
| purchase_orders | purchase_orders_status_wholesale_profile_id_order_date_index | N | status, wholesale_profile_id, order_date |
| purchase_orders | purchase_orders_user_id_foreign | N | user_id |
| purchase_orders | purchase_orders_v1_order_block_id_index | N | v1_order_block_id |
| purchase_orders | purchase_orders_v1_order_idx_index | N | v1_order_idx |
| purchase_orders | purchase_orders_wholesale_profile_id_foreign | N | wholesale_profile_id |
| retail_profiles | PRIMARY | Y | id |
| retail_profiles | retail_profiles_user_id_foreign | N | user_id |
| role_has_permissions | PRIMARY | Y | permission_id, role_id |
| role_has_permissions | role_has_permissions_role_id_foreign | N | role_id |
| roles | PRIMARY | Y | id |
| roles | roles_name_guard_name_unique | Y | name, guard_name |
| sabangnet_logs | PRIMARY | Y | id |
| sabangnet_logs | sabangnet_logs_sabangnet_sync_id_foreign | N | sabangnet_sync_id |
| sabangnet_syncs | PRIMARY | Y | id |
| sabangnet_syncs | sabangnet_syncs_user_id_foreign | N | user_id |
| sessions | PRIMARY | Y | id |
| sessions | sessions_last_activity_index | N | last_activity |
| sessions | sessions_user_id_index | N | user_id |
| settings | PRIMARY | Y | id |
| settings | settings_group_key_unique | Y | group, key |
| shipment_items | PRIMARY | Y | id |
| shipment_items | shipment_items_order_item_id_foreign | N | order_item_id |
| shipment_items | shipment_items_product_id_foreign | N | product_id |
| shipment_items | shipment_items_product_option_id_foreign | N | product_option_id |
| shipment_items | shipment_items_shipment_id_foreign | N | shipment_id |
| shipments | PRIMARY | Y | id |
| shipments | shipments_order_id_foreign | N | order_id |
| shooting_schedules | PRIMARY | Y | id |
| shooting_schedules | shooting_schedules_content_pipeline_id_foreign | N | content_pipeline_id |
| shooting_schedules | shooting_schedules_product_id_foreign | N | product_id |
| users | PRIMARY | Y | id |
| users | users_email_unique | Y | email |
| users | users_v1_idx_index | N | v1_idx |
| wholesale_profiles | PRIMARY | Y | id |
| wholesale_profiles | wholesale_profiles_user_id_foreign | N | user_id |
| wishlists | PRIMARY | Y | id |
| wishlists | wishlists_product_id_foreign | N | product_id |
| wishlists | wishlists_user_id_product_id_unique | Y | user_id, product_id |

