# R2-API-004 작업 보고서

## 기본 정보
| 항목 | 내용 |
|------|------|
| 작업 ID | R2-API-004 |
| 작업명 | 카페24 API 연동 (OAuth, 상품 push/sync) |
| 작업일 | 2026-02-25 KST |
| 버전 | v2.0.0 (예정) |
| 커밋 SHA | 푸시후기록 |
| 상태 | 구현 완료 (실연동은 client_id/secret 설정 후) |

## 구현 기능

### 엔드포인트
| 메서드 | 경로 | 설명 | 권한 |
|--------|------|------|------|
| POST | /api/cafe24/connect | mall_id 입력 → OAuth 인증 URL 반환 | retail, wholesale, admin |
| GET | /api/cafe24/callback | code, mall_id → access_token 교환, DB 저장 | auth |
| GET | /api/cafe24/status | 연동 상태 (토큰 만료 시각 등) | auth |
| POST | /api/cafe24/products/push | V2 상품 → 카페24 등록 (product_ids 배열) | auth |
| PUT | /api/cafe24/products/{id} | 카페24 상품 수정 (id=cafe24_product_no, mall_id 쿼리) | auth |
| DELETE | /api/cafe24/products/{id} | 카페24 상품 삭제 (mall_id 쿼리) | auth |
| GET | /api/cafe24/products | 동기화 매핑 목록 + 카페24 상품 (mall_id 쿼리) | auth |

### DB 테이블
- **cafe24_connections**: id, user_id(FK), mall_id(unique per user), client_id, client_secret, access_token, refresh_token, token_expires_at, scopes, is_active(default true), created_at, updated_at
- **cafe24_product_mappings**: id, user_id(FK), product_id(FK), cafe24_product_no(bigint), cafe24_mall_id, sync_status(enum: pending,synced,failed,deleted), last_synced_at, error_message, created_at, updated_at, unique(user_id, product_id, cafe24_mall_id)

### 모델
- **Cafe24Connection**: user, productMappings (cafe24_mall_id + user_id 기준)
- **Cafe24ProductMapping**: user, product

### 서비스
- **Cafe24ApiService**: getAuthUrl, exchangeToken, refreshToken, pushProduct, updateProduct, deleteProduct, getProducts. Base URL: https://{mall_id}.cafe24api.com/api/v2. client_id/secret 미설정 시 "연동 준비 완료" 메시지 반환.

## 신규/수정 파일
- `config/services.php` (신규 — cafe24 섹션)
- `database/migrations/2026_02_25_120001_create_cafe24_connections_table.php` (신규)
- `database/migrations/2026_02_25_120002_create_cafe24_product_mappings_table.php` (신규)
- `app/Models/Cafe24Connection.php` (신규)
- `app/Models/Cafe24ProductMapping.php` (신규)
- `app/Services/Cafe24ApiService.php` (신규)
- `app/Http/Controllers/Api/Cafe24Controller.php` (신규)
- `app/Models/User.php` (수정 — cafe24Connections, cafe24ProductMappings 관계)
- `routes/api.php` (수정 — /api/cafe24/* 라우트 그룹)

## 설정
- **config/services.php**: cafe24.client_id, client_secret, redirect_uri, scopes (env 기반)
- **.env.docker** (서버만, 커밋 금지): CAFE24_CLIENT_ID=, CAFE24_CLIENT_SECRET=, CAFE24_REDIRECT_URI= (예: https://도메인/api/cafe24/callback)

## 검수 결과 (서버에서 실행)
- **PHP Syntax**: (실행 후 기입) — `php -l` app/Http/Controllers/Api/Cafe24Controller.php, app/Services/Cafe24ApiService.php, app/Models/Cafe24Connection.php, app/Models/Cafe24ProductMapping.php
- **마이그레이션**: (실행 후 기입) — `php artisan migrate:status` cafe24
- **라우트**: (실행 후 기입) — `php artisan route:list --path=cafe24`
- **V1 헬스**: (실행 후 기입) — curl 114.207.244.86 → 200

## 비고
- 실제 카페24 API 호출은 개발자센터에서 앱 발급 후 client_id/secret 설정해야 가능. 구조(마이그레이션·모델·서비스·컨트롤러·라우트)는 완성되어 있으며, 미설정 시 try-catch 및 메시지로 "연동 준비 완료" 상태 반환.
- 기존 cafe24_syncs 테이블(2026_02_21_100025)은 유지. R2-API-004는 cafe24_connections, cafe24_product_mappings 사용.
