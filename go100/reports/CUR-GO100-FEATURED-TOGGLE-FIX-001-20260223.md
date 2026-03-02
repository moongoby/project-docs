# CUR-GO100-FEATURED-TOGGLE-FIX-001 결과 보고서

- **일시**: 2026-02-23 16:20 KST
- **서버**: root@[SERVER-IP]
- **DB**: PGPASSWORD='[DB-PASSWORD]' psql -h localhost -U kis_admin -d kisautotrade
- **코드 repo**: /root/kis-autotrade-v4 (branch: phase-2c-command-center)
- **문서 repo**: /root/project-docs (master)
- **절대규칙 준수**: kis-v41-* 재시작 금지, strategy_cards ALTER/DROP/DELETE 금지

---

## 1. 요약

| 항목 | 결과 |
|------|------|
| **목적** | featured 카드(is_featured=true) 사용자 토글 OFF 시 전체 전략 탭에서 사라지는 문제 수정 |
| **원인** | 전체 전략(tab=all) 쿼리가 `WHERE is_featured = true AND is_active = true` → 토글 OFF 시 3건→2건으로 감소 |
| **방안** | A) 전체 전략 쿼리에서 is_active 제거 (채택) / B) featured 카드 토글 숨김 / C) is_active 분리 관리 |
| **수정** | tab=all: `WHERE is_featured = true` 만 사용. get_card: featured면 is_active 무관 조회 허용. |
| **검증** | tab=all 호출 시 featured 3건 항상 노출, tab=my 6건 유지. DB ALTER/DROP/DELETE 없음. |

---

## 2. 원인 분석

- **전체 전략 탭** (`list_cards_with_system(..., tab="all")`): `go100_strategy_cards`에서 `WHERE is_featured = true AND is_active = true` 사용.
- 사용자가 featured 카드를 "토글 OFF"하면 `is_active = false`로 변경됨 → 위 조건에서 제외되어 **전체 전략 탭에서 사라짐**.
- featured는 관리자가 지정한 카드이므로, 사용자 토글과 무관하게 **전체 전략에 항상 노출**하는 것이 기획 의도.

---

## 3. 수정 내용

### 3.1 백엔드

| 파일 | 변경 |
|------|------|
| `backend/app/services/strategy_card_service.py` | `list_cards_with_system` tab=all: `WHERE is_featured = true AND is_active = true` → `WHERE is_featured = true`. 주석: CUR-GO100-FEATURED-TOGGLE-FIX-001. |
| `backend/app/services/go100/strategy/card_service.py` | `get_card`: `(user_id = :user_id OR (is_featured = true AND is_active = true))` → `(user_id = :user_id OR is_featured = true)`. featured 카드 토글 OFF여도 상세 조회 가능. |

### 3.2 백업 (배포 전 권장)

- `strategy_card_service.py.bak.20260223_1620`
- `card_service.py.bak.20260223_1620`

---

## 4. 검증 가이드

### 4.1 재시작 및 헬스

```bash
sudo systemctl restart go100
curl http://localhost:8002/health
```

### 4.2 전체 전략 탭 (tab=all)

- `GET /api/go100/strategy-cards?tab=all` → **featured 3건** 항상 노출 (토글 OFF 카드 포함).
- 응답 카드에 `is_active: false`인 항목이 있어도 건수는 3건 유지.

### 4.3 내 전략 탭 (tab=my)

- `GET /api/go100/strategy-cards?tab=my` → 기존과 동일(예: 6건). is_active 필터 없음 유지.

### 4.4 DB 무결성

- `strategy_cards`, `go100_strategy_cards` 건수 변경 없음.
- `go100_strategy_cards` WHERE is_featured = true 건수 = 3 유지.

---

## 5. 기대 동작

- **전체 전략 탭**: is_featured=true인 카드는 사용자가 토글 OFF해도 **항상 3건 노출**.
- **내 전략 탭**: 기존과 동일. 토글 OFF 카드는 비활성 뱃지로 표시.
- **상세 조회**: featured 카드는 is_active와 무관하게 조회 가능.

---

## 6. 배포·참고

- **적용**: go100 서비스만 재시작. kis-v41-* 재시작 금지.
- **보고서**: GitHub project-docs master — `go100/reports/CUR-GO100-FEATURED-TOGGLE-FIX-001-20260223.md`
- **코드**: kis-autotrade-v4 branch `phase-2c-command-center` 커밋 푸시.
