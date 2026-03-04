# NewTalk V2 — R1~R4 버그 수정 보고서

**문서번호**: CODE-FIX-001
**수정일**: 2026-02-27 (코드 수정) / 2026-03-02 (Frontend 재빌드 + 최종 검증)
**근거**: CODE-REVIEW-001 검수 보고서
**수정환경**: [SERVER-IP-114] (서버 114)

---

## 1. 수정 요약

| 버그 ID | 심각도 | 수정 전 | 수정 후 | 상태 |
|---|---|---|---|---|
| BUG-001 | CRITICAL | R1 모델 3개 빈 스텁 → 500 에러 | 백업에서 전체 코드 복원 → 200 | ✅ 완료 |
| BUG-002 | CRITICAL | ConversationService 구문 오류 → DM 전면 장애 | 닫는 `});` 추가 + 중복 제거 | ✅ 완료 |
| BUG-003 | HIGH | Frontend Server Action ID 불일치 | Docker 이미지 재빌드 + 컨테이너 교체 | ✅ 완료 |
| WARN-001 | MEDIUM | TypeScript 43개 에러 | 0개로 수정 완료 | ✅ 완료 |

---

## 2. BUG-001: R1 모델 복원

### 원인
`PurchaseOrder.php`, `InboundReceipt.php`, `Barcode.php` 3개 모델이 2026-02-21 작업 중 빈 스텁으로 덮어씌워짐.

### 수정 내용
백업 파일(`.bak.20260221_230235`)에서 전체 코드를 복원.

| 파일 | 수정 전 | 수정 후 |
|---|---|---|
| `app/Models/PurchaseOrder.php` | 10줄 (빈 스텁) | 105줄 (7개 상수, 5개 관계, 3개 스코프) |
| `app/Models/InboundReceipt.php` | 10줄 (빈 스텁) | 77줄 (4개 상수, 3개 관계, 2개 스코프) |
| `app/Models/Barcode.php` | 10줄 (빈 스텁) | 70줄 (5개 상수, 4개 관계, 바코드 생성기) |

### 검증 결과

| 엔드포인트 | 수정 전 | 수정 후 |
|---|---|---|
| GET /api/dashboard/overview | 500 (STATUS_PENDING 미정의) | **200** ✅ |
| GET /api/purchase-orders | 500 (byDateRange 미정의) | **200** ✅ |
| GET /api/dashboard/purchasing/summary | 500 (STATUS_CANCELLED 미정의) | **200** ✅ |

---

## 3. BUG-002: ConversationService 구문 오류 수정

### 원인
`getOrCreateDirect()` 메서드의 `DB::transaction()` 클로저에 닫는 `});` 누락, `leave()` 메서드에 `});` 중복.

### 수정 내용

**수정 1**: Line 57-58 — DB::transaction 클로저 닫기 추가
```php
// 수정 전
        return $conversation->fresh(['participants']);
    }
// 수정 후
            return $conversation->fresh(['participants']);
        });
    }
```

**수정 2**: Line 90-91 — 중복 `});` 제거
```php
// 수정 전
        });
    });
    }
// 수정 후
        });
    }
```

### 검증 결과

| 엔드포인트 | 수정 전 | 수정 후 |
|---|---|---|
| GET /api/conversations | 500 (ParseError) | **200** ✅ |
| POST /api/conversations | 500 (ParseError) | **201** ✅ (대화방 생성 성공) |
| `php -l ConversationService.php` | 구문 에러 | No syntax errors detected ✅ |

---

## 4. BUG-003: Frontend 재빌드

### 원인
이전 빌드의 Server Action ID와 현재 서버의 ID가 불일치. 외부 캐시된 클라이언트/봇이 이전 ID로 요청.

### 수정 내용
```bash
docker compose build frontend    # 새 이미지 빌드
docker compose up -d frontend    # 컨테이너 교체
```

### 검증 결과

| 항목 | 수정 전 | 수정 후 |
|---|---|---|
| 빌드 ID (이전) | KEvC84YuRPSre5wT4H4Py | **6ZRCh-_26d_domABPBPhs** (2026-03-02 재빌드) |
| /login 페이지 | 200 (렌더링 정상) | **200** (렌더링 정상, 새 빌드) ✅ |
| Server Action 에러 | 지속 발생 | **0건** — 컨테이너 로그 에러 없음 ✅ |

---

## 5. WARN-001: TypeScript 43개 에러 → 0개

### 원인
`fetchApi<T>()` 반환 타입 `Promise<ApiResponse<T>>`와 호출측 기대 타입 `T` 불일치.

### 수정 내용

**핵심 수정**: `src/lib/api.ts`
- `fetchApi<T>()` 반환 타입을 `Promise<ApiResponse<T>>` → `Promise<T>`로 변경
- `getMe()` 응답 타입 수정

**API 클라이언트 파일 수정** (11개 파일):
| 파일 | 에러 수 | 수정 내용 |
|---|---|---|
| `lib/shorts-api.ts` | 18 → 0 | 불필요한 타입 캐스트 제거 |
| `lib/shipping-api.ts` | 10 → 0 | 중복 `as` 캐스트 제거 |
| `lib/dm-api.ts` | 6 → 0 | `as unknown as` 캐스트 제거 |
| `lib/trade-api.ts` | 13 → 0 | `.data` 접근 제거, 페이지네이션 타입 수정 |
| `lib/recommendation-api.ts` | 13 → 0 | `.data` 접근 제거 |
| `lib/purchase-api.ts` | 9 → 0 | `.data` 접근 제거, 페이지네이션 타입 수정 |
| `lib/purchase-order-api.ts` | 4 → 0 | `.data` 접근 제거 |
| `lib/product-api.ts` | 4 → 0 | `.data` 접근 제거 |
| `lib/feed-api.ts` | 4 → 0 | `.data` 접근 제거 |
| `lib/fulfillment-api.ts` | 3 → 0 | 불필요한 캐스트 제거 |
| `lib/brand-api.ts` | 2 → 0 | `.data` 접근 제거 |

**컴포넌트 파일 수정** (5개 파일):
| 파일 | 수정 내용 |
|---|---|
| `components/ui/button.tsx` | `asChild` prop + `destructive` variant 추가 |
| `components/fulfillment/DropshipOrderCard.tsx` | 누락 컴포넌트 신규 생성 |
| `components/story/StoryReactionBar.tsx` | `Clap` → `HandMetal` 아이콘 교체 |
| `components/channel/ChannelPushDialog.tsx` | `.data` 접근 제거 |
| `app/(admin)/*/page.tsx` | `.data` 접근 제거 |

### 검증 결과
```
$ npx tsc --noEmit
→ 에러 0개 ✅
```

---

## 6. 수정된 파일 전체 목록

### Backend (Laravel, /srv/newtalk-v2/src/)
| 파일 | 변경 유형 |
|---|---|
| `app/Models/PurchaseOrder.php` | 백업에서 복원 |
| `app/Models/InboundReceipt.php` | 백업에서 복원 |
| `app/Models/Barcode.php` | 백업에서 복원 |
| `app/Services/ConversationService.php` | 구문 오류 수정 |

### Frontend (Next.js, /srv/newtalk-v2/frontend/src/)
| 파일 | 변경 유형 |
|---|---|
| `lib/api.ts` | fetchApi 반환 타입 변경 |
| `lib/dm-api.ts` | 타입 캐스트 정리 |
| `lib/shipping-api.ts` | 타입 캐스트 정리 |
| `lib/shorts-api.ts` | 타입 캐스트 정리 |
| `lib/trade-api.ts` | `.data` 접근 제거 |
| `lib/recommendation-api.ts` | `.data` 접근 제거 |
| `lib/purchase-api.ts` | `.data` 접근 제거 |
| `lib/purchase-order-api.ts` | `.data` 접근 제거 |
| `lib/product-api.ts` | `.data` 접근 제거 |
| `lib/feed-api.ts` | `.data` 접근 제거 |
| `lib/fulfillment-api.ts` | 타입 캐스트 정리 |
| `lib/brand-api.ts` | `.data` 접근 제거 |
| `lib/channel-api.ts` | `.data` 접근 패턴 수정 |
| `lib/story-api.ts` | `.data` 접근 패턴 수정 |
| `components/ui/button.tsx` | asChild + destructive variant |
| `components/fulfillment/DropshipOrderCard.tsx` | 신규 생성 |
| `components/story/StoryReactionBar.tsx` | 아이콘 교체 |
| `components/channel/ChannelPushDialog.tsx` | `.data` 접근 제거 |
| `app/(admin)/admin/dashboard/page.tsx` | `.data` 접근 제거 |
| `app/(admin)/purchasing/page.tsx` | `.data` 접근 제거 |

---

## 7. 수정 후 전체 API 상태

| 엔드포인트 | 수정 전 | 수정 후 |
|---|---|---|
| GET /api/auth/me | 200 | 200 ✅ |
| GET /api/products | 200 | 200 ✅ |
| GET /api/dashboard/overview | **500** | **200** ✅ |
| GET /api/purchase-orders | **500** | **200** ✅ |
| GET /api/inbound-receipts | 200 | 200 ✅ |
| GET /api/barcodes | 200 | 200 ✅ |
| GET /api/dashboard/stats | 200 | 200 ✅ |
| GET /api/dashboard/purchasing/summary | **500** | **200** ✅ |
| GET /api/feed/explore | 200 | 200 ✅ |
| GET /api/feed | 200 | 200 ✅ |
| GET /api/conversations | **500** | **200** ✅ |
| POST /api/conversations | **500** | **201** ✅ |
| GET /api/admin/dashboard | 200 | 200 ✅ |
| GET /api/md/dashboard | 200 | 200 ✅ |
| GET /api/purchaser/dashboard | 200 | 200 ✅ |
| GET /api/wholesale/dashboard | 200 | 200 ✅ |
| GET /api/retail/dashboard | 200 | 200 ✅ |
| Frontend /login | 200 | 200 ✅ (새 빌드) |
| TypeScript 빌드 | 43 에러 | **0 에러** ✅ |

**500 에러 5건 → 0건, TypeScript 에러 43건 → 0건**

---

**수정자**: Claude Code
**최종 검증일**: 2026-03-02
**검증 방법**: Docker 내부 curl + node:20-alpine `tsc --noEmit` + frontend 컨테이너 로그 확인
