# NewTalk V2 — 라우트 파일 통합 사전 조사 보고서

**문서번호**: ROUTE-MERGE-PREP-001
**작성일시**: 2026-03-02 21:00 KST
**목적**: routes/api.php(미사용) → src/routes/api.php(실사용) 안전 병합 계획 수립

---

## 1. 두 파일 현황

| 항목 | src/routes/api.php (실사용) | routes/api.php (미사용) |
|------|---------------------------|------------------------|
| 경로 | /srv/newtalk-v2/src/routes/api.php | /srv/newtalk-v2/routes/api.php |
| 참조 | bootstrap/app.php 직접 참조 | ❌ 미참조 (사각지대) |
| 라인 수 | 158줄 | 158줄 |
| 등록 라우트 | 66개 (artisan route:list 확인) | 0개 (앱이 로드 안 함) |
| 범위 | R1·R2-API-001·R3-API-004 | R1(중복)+R2-API-004+R4-API-005·007 |

---

## 2. 중복 라우트 분석

routes/api.php에는 src/routes/api.php와 **동일한 라우트가 중복**으로 포함됨:

| 중복 그룹 | 라우트 수 | 판정 |
|-----------|---------|------|
| Auth (login, logout, me) | 3 | 중복 → 병합 시 제외 |
| purchase-orders | 8 | 중복 → 병합 시 제외 |
| inbound-receipts | 6 | 중복 → 병합 시 제외 |
| barcodes | 5 | 중복 → 병합 시 제외 |
| dashboard (overview, stats, purchasing×6) | 8 | 중복 → 병합 시 제외 |
| conversations + messages (R3-API-004) | 10 | 중복 → 병합 시 제외 |
| **중복 합계** | **40개** | 모두 제외 |

---

## 3. 신규 라우트 (routes/api.php에만 존재)

| 그룹 | prefix | EP 수 | 컨트롤러 | DB 테이블 | 병합 가능 여부 |
|------|--------|-------|---------|-----------|--------------|
| 카페24 연동 | /cafe24 | 7 | Cafe24Controller ✅ | cafe24_connections ✅ | ✅ 즉시 가능 |
| 드롭십 주문 | /dropship | 7 | DropshipController ✅ | dropship_orders ❌ (마이그 미실행) | ⚠️ 마이그레이션 후 |
| 반품·교환 | /returns | 7 | ReturnController ✅ | return_requests ❌ (마이그 미실행) | ⚠️ 마이그레이션 후 |
| 풀필먼트 | /fulfillment | 6 | FulfillmentController ✅ | fulfillment_tasks ❌ (마이그 미실행) | ⚠️ 마이그레이션 후 |
| 콘텐츠 파이프라인 | /pipeline | 13 | ContentPipelineController ✅ | content_pipeline_jobs ❌ (마이그 미실행) | ⚠️ 마이그레이션 후 |
| **신규 합계** | | **40개** | | | |

---

## 4. 컨트롤러 파일 존재 확인

routes/api.php에서 참조하는 컨트롤러 모두 실제 파일 확인:

| 컨트롤러 | 파일 경로 | 존재 여부 |
|---------|---------|---------|
| Cafe24Controller | app/Http/Controllers/Api/Cafe24Controller.php | ✅ |
| DropshipController | app/Http/Controllers/Api/DropshipController.php | ✅ |
| ReturnController | app/Http/Controllers/Api/ReturnController.php | ✅ |
| FulfillmentController | app/Http/Controllers/Api/FulfillmentController.php | ✅ |
| ContentPipelineController | app/Http/Controllers/Api/ContentPipelineController.php | ✅ |

---

## 5. 병합 시 충돌 위험 없음 확인

신규 라우트(40개)는 src/routes/api.php의 기존 URI와 충돌하지 않음:

- `/cafe24/*` — 기존 없음 ✅
- `/dropship/*` — 기존 없음 ✅
- `/returns/*` — 기존 없음 ✅
- `/fulfillment/*` — 기존 없음 ✅
- `/pipeline/*` — 기존 없음 ✅

**R1~R2 기존 동작 기능(66라우트)에 전혀 영향 없음.**

---

## 6. 안전 병합 계획 (2단계)

### Phase 1: 즉시 실행 가능 — Cafe24 (DB 있음)

`src/routes/api.php` 끝에 추가:

```php
// === R2-API-004: 카페24 API 연동 ===
Route::middleware(['auth:sanctum', 'role:retail|wholesale|admin'])->prefix('cafe24')->group(function () {
    Route::post('/connect', [Cafe24Controller::class, 'connect']);
    Route::get('/callback', [Cafe24Controller::class, 'callback']);
    Route::get('/status', [Cafe24Controller::class, 'status']);
    Route::post('/products/push', [Cafe24Controller::class, 'pushProducts']);
    Route::put('/products/{id}', [Cafe24Controller::class, 'updateProduct']);
    Route::delete('/products/{id}', [Cafe24Controller::class, 'deleteProduct']);
    Route::get('/products', [Cafe24Controller::class, 'listProducts']);
});
```

### Phase 2: 마이그레이션 실행 후 — R4-API-007·005 (DB 없음)

**선행 작업**: 9개 마이그레이션 실행
```bash
cd /srv/newtalk-v2
docker compose --env-file .env.docker exec app php artisan migrate
```

**실행될 마이그레이션**:
- 2026_02_26_340001~340006: sns_connections, sns_posts, sns_post_analytics, content_pipeline_jobs, pipeline_logs, pipeline_media
- 2026_02_26_400001~400003: dropship_orders, return_requests, fulfillment_tasks

**마이그레이션 후 추가할 라우트** (src/routes/api.php):
- R4-API-007: /dropship (7 EP), /returns (7 EP), /fulfillment (6 EP)
- R4-API-005: /pipeline (13 EP)

---

## 7. 예상 효과

| 구분 | 현재 | Phase 1 후 | Phase 2 후 |
|------|------|-----------|-----------|
| 등록 API 라우트 | 66개 | 73개 (+7) | 106개 (+40) |
| 동작 가능 기능 | R1·R2-API-001·R3-API-004 | +Cafe24 | +Dropship·Returns·Fulfillment·Pipeline |
| SNS 자동게시(R4-006) | 미동작 | 미동작 | 미동작 (컨트롤러 있으나 라우트 추가 필요) |
| DB 테이블 증가 | 66개 | 66개 | 75개 (+9) |

---

## 8. 권고사항

1. **Phase 1 즉시 실행**: Cafe24 라우트 추가 (리스크 없음, DB 이미 존재)
2. **Phase 2 마이그레이션**: `php artisan migrate` 실행 (66→75 테이블, DB에 영향)
3. **Phase 2 라우트 추가**: 마이그레이션 성공 확인 후 R4 라우트 병합
4. **routes/api.php 처리**: 병합 완료 후 `.gitignore` 처리 또는 archive로 이동 권고

---

**완료일시**: 2026-03-02 21:00 KST
**검수**: Cursor Agent (ROUTE-MERGE-PREP-001)
