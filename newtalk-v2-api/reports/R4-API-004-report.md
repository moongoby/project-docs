# R4-API-004 셀러 채널 관리 API — 완료 보고서

**작성일시**: 2026-02-26 KST  
**버전**: v3.4.0  
**커밋 접두사**: `[R4-API-004]`

---

## 요약

| 항목 | 내용 |
|------|------|
| 테이블 | 2개 (`channel_connections`, `channel_product_mappings`) |
| 모델 | 2개 (`ChannelConnection`, `ChannelProductMapping`) |
| 서비스 | `ChannelService` (12 메서드) + `ChannelDriverInterface` |
| 드라이버 | Cafe24(실구현), Naver/Coupang/11st(스텁) |
| 엔드포인트 | 12개 (+ OAuth URL 1개) |

---

## STEP 1: 마이그레이션

- `database/migrations/2026_02_26_330001_create_channel_connections_table.php`
  - `channel_connections`: user_id, platform(enum), platform_store_id, platform_store_name, access_token, refresh_token, token_expires_at, scopes, settings, is_active, status, last_error, last_synced_at, softDeletes, unique(user_id, platform, platform_store_id)
- `database/migrations/2026_02_26_330002_create_channel_product_mappings_table.php`
  - `channel_product_mappings`: channel_connection_id, product_id, platform_product_id, sync_status(enum), last_synced_at, error_message, platform_data, unique(channel_connection_id, product_id)

---

## STEP 2: 모델

- **ChannelConnection**  
  관계: `user`, `mappings`  
  fillable, casts, hidden(access_token, refresh_token)  
  scopes: `byPlatform`, `active`, `byUser`  
  헬퍼: `isTokenExpiredOrExpiringSoon()`

- **ChannelProductMapping**  
  관계: `channelConnection`, `product`  
  fillable, casts  
  scopes: `byPlatform`, `active`, `bySyncStatus`  
  상수: SYNC_STATUS_PENDING, SYNCED, FAILED, DELETED, UPDATED

---

## STEP 3: 서비스 레이어

### ChannelDriverInterface

- `getAuthUrl(connection, redirectUri, state): string`
- `exchangeToken(connection, code): ChannelConnection`
- `refreshToken(connection): ChannelConnection`
- `pushProduct(connection, product): array`
- `updateProduct(connection, product, platformProductId): array`
- `deleteProduct(connection, platformProductId): bool`
- `getProducts(connection, params): array`

### 드라이버

| 드라이버 | 파일 | 비고 |
|---------|------|------|
| Cafe24 | `App\Services\Channels\Cafe24Driver` | 기존 `Cafe24ApiService` 래핑, 실구현 |
| Naver | `App\Services\Channels\NaverDriver` | 스텁, `NotImplementedException` |
| Coupang | `App\Services\Channels\CoupangDriver` | 스텁 |
| Elevenst | `App\Services\Channels\ElevenstDriver` | 스텁 |

### ChannelService (12 메서드)

1. `connect(userId, platform, authData)` — 채널 연결
2. `disconnect(connectionId)` — 채널 해제
3. `getConnections(userId)` — 내 채널 목록
4. `getConnectionDetail(connectionId)` — 채널 상세 + 매핑 통계
5. `refreshToken(connection)` — 토큰 갱신
6. `pushProduct(connectionId, productId)` — 단일 상품 푸시
7. `pushProducts(connectionId, productIds)` — 일괄 푸시
8. `deleteProduct(connectionId, productId)` — 상품 삭제
9. `syncProducts(connectionId)` — 전체 동기화
10. `getMappings(connectionId, filters)` — 매핑 목록(페이지네이션)
11. `getProductChannels(productId, userId)` — 상품이 등록된 채널 목록
12. `updateSettings(connectionId, settings)` — 채널 설정 변경

---

## STEP 4: 컨트롤러·라우트

**파일**: `app/Http/Controllers/Api/ChannelController.php`

| Method | URI | 메서드 | 비고 |
|--------|-----|--------|------|
| GET | /api/channels | index | 내 채널 목록 |
| POST | /api/channels/connect | connect | 채널 연결 |
| GET | /api/channels/connect/auth-url | authUrl | OAuth URL (쿼리: platform, platform_store_id) |
| GET | /api/channels/{id} | show | 채널 상세 |
| DELETE | /api/channels/{id} | destroy | 채널 해제 |
| PUT | /api/channels/{id}/settings | updateSettings | 설정 변경 |
| POST | /api/channels/{id}/push/{productId} | pushProduct | 단일 상품 푸시 |
| POST | /api/channels/{id}/push-bulk | pushBulk | 일괄 푸시 |
| DELETE | /api/channels/{id}/products/{productId} | deleteProduct | 상품 삭제 |
| POST | /api/channels/{id}/sync | sync | 전체 동기화 |
| GET | /api/channels/{id}/mappings | mappings | 매핑 목록 |
| POST | /api/channels/{id}/refresh-token | refreshToken | 토큰 갱신 |
| GET | /api/products/{productId}/channels | productChannels | 상품 채널 목록 |

미들웨어: `auth:sanctum`, `role:retail|wholesale|admin`.

---

## 검증

- 채널 목록/상세/해제/설정: 본인 `user_id` 기준 조회·수정.
- 상품 푸시/삭제/동기화: 해당 채널 소유자만 가능.
- 상품 채널 목록: 해당 상품에 매핑된 채널 중 요청 사용자 소유 채널만 반환.

**마이그레이션**: 배포 환경(artisan 존재 경로)에서 `php artisan migrate` 실행.

---

## 신규·변경 파일 목록

- `database/migrations/2026_02_26_330001_create_channel_connections_table.php`
- `database/migrations/2026_02_26_330002_create_channel_product_mappings_table.php`
- `app/Models/ChannelConnection.php`
- `app/Models/ChannelProductMapping.php`
- `app/Exceptions/NotImplementedException.php`
- `app/Services/Channels/ChannelDriverInterface.php`
- `app/Services/Channels/Cafe24Driver.php`
- `app/Services/Channels/NaverDriver.php`
- `app/Services/Channels/CoupangDriver.php`
- `app/Services/Channels/ElevenstDriver.php`
- `app/Services/ChannelService.php`
- `app/Http/Controllers/Api/ChannelController.php`
- `app/Models/User.php` (channelConnections 관계 추가)
- `routes/api.php` (채널 라우트 그룹 및 products/{productId}/channels 추가)

---

## R4-API-004 완료

- 테이블 2개, 모델 2개  
- 서비스: ChannelService (12 메서드) + ChannelDriverInterface  
- 드라이버: Cafe24(실구현), Naver/Coupang/11st(스텁)  
- 엔드포인트 12개 (+ auth-url 1개)
