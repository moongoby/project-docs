# NewTalk V2 — DB 테이블·API 라우트 갭 분석 보고서

**문서번호**: GAP-ANALYSIS-001
**작성일시**: 2026-03-02 20:45 KST
**목적**: DB 테이블 66개 / API 라우트 66개 갭 원인 파악 및 R5 기획 기초자료 제공

---

## 1. 조사 환경

| 항목 | 값 |
|------|-----|
| 서버 | rfree-0009.cafe24.com (114.207.244.86) |
| V2 DB | MySQL 8.0 (newtalk_v2, :3307) |
| 라우트 파일 | /srv/newtalk-v2/src/routes/api.php |
| 마이그레이션 경로 | /srv/newtalk-v2/src/database/migrations/ (→ /srv/newtalk-v2/database/migrations/ 심볼릭) |
| 분석 기준 | 2026-03-02 |

---

## 2. 핵심 발견: 이중 라우트 파일 구조

> **중요**: 실제 사용 라우트 파일과 R4 확장 라우트 파일이 분리되어 있음

| 파일 | 라인 수 | 용도 | 사용 여부 |
|------|---------|------|-----------|
| `/srv/newtalk-v2/src/routes/api.php` | 158줄 | **실제 사용 중** (bootstrap/app.php 참조) | ✅ 활성 |
| `/srv/newtalk-v2/routes/api.php` | 158줄 | R4 확장 라우트 (미연결) | ❌ 미사용 |

**root-level routes/api.php에는 R4-API-005·007이 등록되어 있지만, 앱이 참조하는 src/routes/api.php에는 없음.**  
→ R4 라우트를 작성했으나 src/routes/api.php에 병합되지 않은 상태.

---

## 3. DB 테이블 현황 (66개)

### 3-1. 실제 존재하는 테이블 (66개)

```
activity_logs, barcodes, brand_pages, cache, cache_locks,
cafe24_connections, cafe24_product_mappings, cafe24_syncs,
cart_items, carts, categories, code_masters,
content_media, content_pipelines, content_product_tags,
contents, contents_media, contents_product_tags,
contract_items, contracts, conversation_participants, conversations,
coordinations, deposits, deposit_transactions, downloads,
failed_jobs, feed_items, feed_likes, follows,
inbound_receipt_items, inbound_receipts,
job_batches, jobs,
message_logs, message_reads, messages, migrations,
model_has_permissions, model_has_roles, order_items, orders,
password_reset_tokens, permissions, personal_access_tokens,
product_categories, product_channels, product_details,
product_images, product_options, products,
purchase_order_items, purchase_orders,
retail_profiles, role_has_permissions, roles,
sabangnet_logs, sabangnet_syncs, sessions, settings,
shipment_items, shipments, shooting_schedules,
users, wholesale_profiles, wishlists
```

### 3-2. 마이그레이션 실행 현황

| 구분 | 수 |
|------|----|
| 마이그레이션 파일 총수 | 78개 |
| 실행 완료 (Ran) | 69개 |
| 미실행 (파일만 존재) | 9개 |

### 3-3. 미실행 마이그레이션 9개 → 해당 테이블 DB에 없음

| 파일명 | 관련 기능 | 라운드 | 판정 |
|--------|-----------|--------|------|
| `2026_02_26_340001_create_sns_connections_table` | SNS 자동게시 연결 | R4-API-006 | **미구현** |
| `2026_02_26_340002_create_sns_posts_table` | SNS 게시물 | R4-API-006 | **미구현** |
| `2026_02_26_340003_create_sns_post_analytics_table` | SNS 분석 | R4-API-006 | **미구현** |
| `2026_02_26_340004_create_content_pipeline_jobs_table` | 콘텐츠 파이프라인 잡 | R4-API-005 | **미구현** |
| `2026_02_26_340005_create_pipeline_logs_table` | 파이프라인 로그 | R4-API-005 | **미구현** |
| `2026_02_26_340006_create_pipeline_media_table` | 파이프라인 미디어 | R4-API-005 | **미구현** |
| `2026_02_26_400001_create_dropship_orders_table` | 드롭십 주문 | R4-API-007 | **미구현** |
| `2026_02_26_400002_create_return_requests_table` | 반품·교환 요청 | R4-API-007 | **미구현** |
| `2026_02_26_400003_create_fulfillment_tasks_table` | 풀필먼트 작업 | R4-API-007 | **미구현** |

### 3-4. 마이그레이션 없이 누락된 테이블 (설계 미완료)

아래 기능들은 마이그레이션 파일 자체가 없음:

| 누락 테이블 | 관련 기능 | 라운드 |
|-------------|-----------|--------|
| payments, payment_logs | 결제 (토스페이먼츠) | R3-API-002 |
| shipping_addresses, shipment_logs | 배송지·배송 이벤트 로그 | R3-API-003 |
| shorts, short_product_tags, short_likes, short_comments, short_views | 쇼츠 | R3-API-005 |
| settlements, settlement_items, settlement_logs | 정산 | R3-API-006 |
| stories, story_views | 스토리 | R4-API-002 |
| user_interests, product_scores, trend_snapshots | AI 추천 엔진 | R4-API-003 |
| channel_connections, channel_product_mappings | 셀러 채널 (product_channels 기존 존재) | R4-API-004 |
| trade_applications, trade_partnerships, trade_prices | 거래처 제도 | R4-API-001 |

**총 누락 테이블 수**: 9개(미실행) + 약 22개(마이그레이션 없음) = **약 31개**

---

## 4. API 라우트 현황 (66개)

### 4-1. 등록된 라우트 (src/routes/api.php 기준)

| 그룹 | 라운드 | 라우트 수 |
|------|--------|---------|
| 인증 (register, login, logout, me) | R1 | 4 |
| 상품 + 이미지 | R1 | 7 |
| 발주·입고·바코드 | R1 | 19 |
| 대시보드 (기본+사입+역할별) | R1·R4 | 13 |
| SNS (피드·팔로우·찜) | R2-API-001 | 13 |
| DM (대화·메시지) | R3-API-004 | 10 |
| **합계** | | **66** |

### 4-2. 미등록 라우트 (구현됐으나 src/routes/api.php 미병합)

| 기능 | 라운드 | 예상 EP | 상태 |
|------|--------|---------|------|
| 브랜드 페이지 | R2-API-002 | ~6 | 컨트롤러 있음, 라우트 없음 |
| AI 콘텐츠 + 미디어 | R2-API-003 | ~8 | 컨트롤러 있음, 라우트 없음 |
| 카페24 연동 | R2-API-004 | 7 | root routes/api.php에만 있음 |
| 장바구니·주문 | R3-API-001 | ~10 | 컨트롤러 있음, 라우트 없음 |
| 결제 (토스페이먼츠) | R3-API-002 | ~6 | 컨트롤러 없음, 테이블 없음 |
| 배송·배송지 | R3-API-003 | ~11 | 컨트롤러 없음, 일부 테이블 없음 |
| 쇼츠 | R3-API-005 | ~11 | 컨트롤러 없음, 테이블 없음 |
| 정산 | R3-API-006 | ~9 | 컨트롤러 없음, 테이블 없음 |
| 거래처 제도 | R4-API-001 | ~11 | 컨트롤러 없음, 테이블 없음 |
| 스토리 | R4-API-002 | ~10 | 컨트롤러 없음, 테이블 없음 |
| AI 추천 피드 | R4-API-003 | ~8 | 컨트롤러 없음, 테이블 없음 |
| 셀러 채널 | R4-API-004 | ~8 | 컨트롤러 없음, 테이블 없음 |
| 콘텐츠 파이프라인 | R4-API-005 | ~13 | root routes/api.php에만 있음, DB 테이블 없음 |
| SNS 자동 게시 | R4-API-006 | ~10 | SnsController 있음, 라우트/DB 없음 |
| 드롭십·반품·풀필먼트 | R4-API-007 | ~20 | root routes/api.php에만 있음, DB 테이블 없음 |

**총 미등록 예상 라우트**: 약 148개 (실제 구현 비율: 66 / 214 ≈ 31%)

---

## 5. 종합 갭 요약

| 구분 | 현재 | 예상 (설계) | 갭 | 갭 원인 |
|------|------|------------|-----|---------|
| DB 테이블 | 66개 | 97개+ | -31개 | 9개 미실행 마이그레이션 + 22개 미작성 |
| API 라우트 | 66개 | 214개+ | -148개 | src/routes/api.php 병합 누락 + 미구현 컨트롤러 |
| API 컨트롤러 | 26개 | 40개+ | -14개 | R3-API-002·003·005·006, R4-API-001~004 미구현 |

---

## 6. R5 기획 방향 제안

### 즉시 실행 가능 (DB 있음, 컨트롤러 있음, 라우트만 누락)
1. **카페24 연동** (R2-API-004): src/routes/api.php에 병합만 하면 됨
2. **장바구니·주문** (R3-API-001): CartController, OrderController 존재
3. **콘텐츠·미디어** (R2-API-003): ContentController, MediaController 존재

### DB 마이그레이션 실행 후 라우트 병합 필요
4. **드롭십·반품·풀필먼트** (R4-API-007): 마이그레이션 9개 실행 + routes 병합
5. **콘텐츠 파이프라인** (R4-API-005): 마이그레이션 실행 + routes 병합
6. **SNS 자동 게시** (R4-API-006): 마이그레이션 실행 + 라우트 작성

### 설계·구현 모두 필요 (R5 범위)
7. **결제** (R3-API-002): 토스페이먼츠 마이그레이션 + 컨트롤러 + 라우트
8. **배송지·배송 이벤트** (R3-API-003): 마이그레이션 + 컨트롤러 + 라우트
9. **쇼츠** (R3-API-005): 마이그레이션 + 컨트롤러 + 라우트
10. **정산** (R3-API-006): 마이그레이션 + 컨트롤러 + 라우트
11. **거래처 제도** (R4-API-001): 마이그레이션 + 컨트롤러 + 라우트
12. **스토리** (R4-API-002): 마이그레이션 + 컨트롤러 + 라우트
13. **AI 추천 피드** (R4-API-003): 마이그레이션 + 컨트롤러 + 라우트
14. **셀러 채널 관리** (R4-API-004): 마이그레이션 + 컨트롤러 + 라우트

---

## 7. 결론

**R1~R2 기본 기능은 완성 수준(R2-API-001 SNS, R1 발주·상품 100% 동작)**

**R3~R4 API는 코드(컨트롤러·모델)만 작성됐고 DB+라우트 연결이 누락된 상태**

→ R5는 기존 코드를 DB + 라우트와 연결하는 "연결 작업"과 미구현 기능을 새로 만드는 두 갈래로 구성됨

---

**완료일시**: 2026-03-02 20:45 KST
**검수**: Cursor Agent (GAP-ANALYSIS-001)
