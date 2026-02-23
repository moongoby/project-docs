# CUR-GO100-CARD-TOGGLE-FIX-001 결과 보고서

- **일시**: 2026-02-23 16:00 KST
- **서버**: root@211.188.51.113
- **DB**: PGPASSWORD='KisAuto2026!Secure' psql -h localhost -U kis_admin -d kisautotrade
- **코드 repo**: /root/kis-autotrade-v4 (branch: phase-2c-command-center)
- **문서 repo**: /root/project-docs (master)
- **절대규칙 준수**: kis-v41-* 재시작 금지, strategy_cards ALTER/DROP/DELETE 금지

---

## 1. 요약

| 항목 | 결과 |
|------|------|
| **목적** | 전략카드 토글 OFF 시 카드가 목록에서 사라지는 문제 수정 |
| **원인** | 카탈로그/목록 API에서 `WHERE is_active = true` 조건으로 비활성 카드 제외 |
| **수정** | 백엔드: tab=my·list_cards에서 is_active 필터 제거 / get_card는 소유주는 비활성 카드 조회 가능 |
| **프론트** | 비활성 GO100 카드에 "비활성" 뱃지 및 opacity 표시 |
| **검증** | catalog?tab=my 호출 시 비활성 카드 2장(id 16, 13) 포함·총 6장 반환 확인 |

---

## 2. 원인 분석

- **카탈로그 API** (`/api/v1/strategy-cards/catalog?tab=my`): `strategy_card_service.list_cards_with_system()`에서 `tab=my` 시 `WHERE user_id = :uid AND is_active = true` 사용 → 토글 OFF 카드 제외.
- **GO100 목록 API** (`/api/go100/strategy-cards`): `card_service.list_cards()`에서 `conditions = ["user_id = :user_id", "is_active = true"]` → 동일 이슈.
- **상세 조회** `get_card`: `AND is_active = true`로 인해 비활성 카드 상세 시 404 발생 가능.

---

## 3. 수정 내용

### 3.1 백엔드

| 파일 | 변경 |
|------|------|
| `backend/app/services/strategy_card_service.py` | `list_cards_with_system`: tab=my 및 fallback에서 `AND is_active = true` 제거. tab=all(전체 전략)은 유지 `is_featured = true AND is_active = true`. |
| `backend/app/services/go100/strategy/card_service.py` | `list_cards`: conditions에서 `is_active = true` 제거. `get_card`: `(user_id = :user_id) OR (is_featured = true AND is_active = true)` 로 변경하여 소유주는 비활성 카드 조회 가능. |

### 3.2 프론트엔드

| 파일 | 변경 |
|------|------|
| `frontend/src/components/strategy/StrategyCard.tsx` | GO100 카드이고 `card.is_active === false`일 때 "비활성" 뱃지(amber) 표시, 카드 컨테이너에 `opacity-80` 적용. |

### 3.3 백업

- `strategy_card_service.py.bak.20260223_1600`
- `card_service.py.bak.20260223_1600`

---

## 4. 검증 결과

### 4.1 카탈로그 API (수정 후)

```
GET /api/v1/strategy-cards/catalog?tab=my
total: 6
  id: 18  name: ---                           is_active: True  source: go100
  id: 17  name: E2E_TEST_FIX002               is_active: True  source: go100
  id: 16  name: E2E-500-DEBUG                 is_active: False source: go100  ← 비활성 유지
  id: 15  name: [단기스윙] 섹터모멘텀...       is_active: True  source: go100
  id: 14  name: [데일리] 대형 우량주...        is_active: True  source: go100
  id: 13  name: [스캘핑] 분봉 스캘핑...        is_active: False source: go100  ← 비활성 유지
```

### 4.2 DB 무결성

| 테이블/조건 | count |
|-------------|-------|
| strategy_cards | 65 |
| go100_cards | 6 |
| go100_active | 4 |
| go100_inactive | 2 |
| v4_positions_OPEN | 5 |

---

## 5. 기대 동작

- 토글 OFF → `is_active = false` → 카드는 **목록에 유지**, "비활성" 뱃지 및 약한 불투명도로 표시.
- 토글 ON → 다시 활성으로 전환 가능.
- tab=all(전체 전략)은 featured + active만 유지.

---

## 6. 배포·참고

- **적용**: go100 서비스 재시작 완료. go100-frontend는 프론트 빌드 후 필요 시 재시작.
- **보고서**: GitHub project-docs master — `go100/reports/CUR-GO100-CARD-TOGGLE-FIX-001-20260223.md`
- **코드**: kis-autotrade-v4 branch `phase-2c-command-center` 커밋 푸시.
