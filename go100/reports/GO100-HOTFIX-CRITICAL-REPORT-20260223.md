# CUR-GO100-HOTFIX-CRITICAL 보고서

**작성일:** 2026-02-23  
**목적:** 5개 크리티컬 이슈 일괄 수정

---

## 1. 백업

- **파일 경로:** `/tmp/backup_HOTFIX_CRITICAL_20260223_043545.dump`
- **명령:** `PGPASSWORD='...' pg_dump -h localhost -U kis_admin -d kisautotrade -F c -f /tmp/backup_HOTFIX_CRITICAL_$(date +%Y%m%d_%H%M%S).dump`

---

## 2. 이슈별 진단·수정·검증

### 이슈1: 백억이 전략저장 500 에러

- **진단:** `go100_strategy_cards` NOT NULL 컬럼은 `user_id`, `strategy_name`만 기본값 없음. INSERT 시 `strategy_name` 빈 값 가능성, `get_effective_uid` 예외 미처리.
- **근본 원인:** (A) 전략명 fallback 미보장 (B) 예외 시 상세 로깅 부재.
- **수정 내용:**
  - `backend/app/services/go100/strategy/card_service.py`: `strategy_name` fallback `"AI 설계 전략"`, `get_effective_uid` 및 INSERT try/except + 로깅, 실패 시 rollback.
  - `backend/app/services/go100/ai/base_orchestrator.py`: `_insert_draft_card`에서 전략명 fallback `"GO100 AI - LLM 전략"`, 이름 길이 200 자 제한, `exc_info=True` 로깅.
- **검증:** 백엔드 헬스 정상, 빌드 성공. 수동 POST 저장은 토큰 필요.

### 이슈2: 전략카드 상세보기 "페이지를 찾을 수 없습니다"

- **진단:** `/go100/strategies/[id]`가 SSR에서 `getStrategyCard` 호출 시 실패 시 `notFound()` 호출로 "페이지를 찾을 수 없습니다" 표시.
- **근본 원인:** 상세 전용 페이지 의존 대신 목록 내 모달로 처리 필요.
- **수정 내용:**
  - **방안 A+C:** 전략카드 목록 페이지에 상세 모달 추가. `selectedCard` 상태, GO100 카드 클릭/상세보기 시 모달 오픈.
  - `frontend/src/components/strategy/StrategyCard.tsx`: `onDetail` prop 추가. GO100 카드에서 `onDetail` 있으면 클릭 시 모달, 없으면 `/strategy-cards?id=...` 링크.
  - `frontend/src/app/(protected)/go100/strategies/[id]/page.tsx`: 기존 상세 페이지를 **리다이렉트 페이지**로 교체. `router.replace("/strategy-cards")` 로 이동.
- **검증:** `/go100/strategies/15` 접속 시 전략카드 페이지로 리다이렉트. 목록에서 상세보기 클릭 시 모달 표시.

### 이슈3: 활성화 토글 오류

- **진단:** 프론트는 `updateStrategyCard(cardId, { is_active })` (PUT) 사용. 전용 PATCH 토글 엔드포인트 없음.
- **근본 원인:** PUT으로도 동작 가능하나, 전용 토글 API 추가로 안정성 확보.
- **수정 내용:**
  - **백엔드:** `backend/app/routers/go100/strategy_router.py`에 `PATCH /api/go100/strategy-cards/{card_id}/toggle` 추가. `is_active = NOT is_active`, 소유권 검사 후 반환.
  - **프론트:** `frontend/src/go100/api/go100Api.ts`에 `toggleStrategyCardActive(cardId)` 추가 (PATCH 호출). `strategy-cards/page.tsx`에서 토글 시 `toggleStrategyCardActive(cardId)` 사용.
- **검증:** 빌드 성공. 실제 토글 동작은 로그인 후 카드 목록에서 확인.

### 이슈4: 채팅 위젯 좌상단 → 우하단

- **진단:** ChatWidget이 이미 `bottom-6 right-6` 사용 중. z-index가 `z-50`이라 다른 요소에 가려질 수 있고, 레이아웃 내부에 있어 fixed 동작 제한 가능성.
- **근본 원인:** z-index 부족, ChatWidget이 flex 컨테이너 내부에 있음.
- **수정 내용:**
  - `frontend/src/go100/components/ChatWidget.tsx`: FAB `z-50` → `z-[9999]`, 패널 `z-50` → `z-[9998]`. 패널 클래스 정리 (모바일 inset-0, 데스크톱 우하단).
  - `frontend/src/app/(protected)/layout.tsx`: ChatWidget을 flex 컨테이너 **밖**으로 이동. `<>` Fragment로 감싸고, `<div className="h-dvh flex ...">` 닫은 뒤 `<ChatWidget />` 배치.
- **검증:** 빌드 성공. 우하단 고정 및 다른 UI 위 표시 확인 가능.

### 이슈5: 백테스트 드롭다운 GO100 카드 미노출

- **진단:** `list_cards_for_backtest`에서 이미 `go100_strategy_cards` 조회 후 `source="go100"`, `go100_card_id` 로 병합. 프론트는 `[GO100] {전략명}` 표시 로직 존재.
- **근본 원인:** 백엔드 로직은 정상. 헤더 추가 및 표시 일관성 유지.
- **수정 내용:**
  - `backend/app/services/strategy_card_service.py`: 파일 상단에 `# CUR-GO100-HOTFIX-CRITICAL, 2026-02-23` 추가.
  - `frontend/src/app/(protected)/backtest/page.tsx`: HOTFIX 헤더 추가. (드롭다운 표시 로직은 기존 유지.)
- **검증:** for-backtest API가 동일 앱에서 GO100 카드 포함해 반환하면 드롭다운에 "[GO100] 전략명" 노출.

---

## 3. 수정 파일 목록

| 구분 | 파일 |
|------|------|
| BE | `backend/app/routers/go100/strategy_router.py` |
| BE | `backend/app/services/go100/ai/base_orchestrator.py` |
| BE | `backend/app/services/go100/strategy/card_service.py` |
| BE | `backend/app/services/strategy_card_service.py` |
| FE | `frontend/src/app/(protected)/backtest/page.tsx` |
| FE | `frontend/src/app/(protected)/go100/strategies/[id]/page.tsx` |
| FE | `frontend/src/app/(protected)/layout.tsx` |
| FE | `frontend/src/app/(protected)/strategy-cards/page.tsx` |
| FE | `frontend/src/components/strategy/StrategyCard.tsx` |
| FE | `frontend/src/go100/api/go100Api.ts` |
| FE | `frontend/src/go100/components/ChatWidget.tsx` |

---

## 4. DB 스키마 변경

- **없음.** `go100_strategy_cards` 스키마 변경 없음.

---

## 5. 빌드·테스트 결과

- **pytest:** 환경에 pytest 미설치로 스킵. (필요 시 `pip install pytest` 후 실행.)
- **프론트:** `npm run build` 성공.
- **헬스체크:** `curl http://localhost:8002/health` → `{"status":"ok",...}`. 프론트 `strategy-cards` 307(리다이렉트).

---

## 6. API 검증 (토큰 필요 시)

- POST 전략카드 저장: `POST /api/go100/strategy-cards` (Body: strategy_name, strategy_type 등)
- 토글: `PATCH /api/go100/strategy-cards/{card_id}/toggle`
- for-backtest: `GET /api/v1/strategy-cards/for-backtest` (GO100 카드 포함 여부 확인)
- tab=my: `GET /api/v1/strategy-cards/catalog?tab=my`

---

## 7. 컴플라이언스 체크리스트

- [x] go100_* 파일/테이블만 수정 (V4.1 strategy_card_service.py는 헤더만 추가)
- [x] .env / .bak 미커밋
- [x] 헤더 코멘트 추가 (CUR-GO100-HOTFIX-CRITICAL, 2026-02-23)
- [x] V4.1 기능 영향 없음 (기존 catalog, for-backtest, strategy_cards 유지)
- [x] 테스트 데이터 정리 (HOTFIX 전용 테스트 카드 없음)

---

## 8. 커밋 해시

```
8da6191b fix: CUR-GO100-HOTFIX-CRITICAL - 전략저장500 + 상세모달 + 토글 + 채팅위치 + 백테스트드롭다운
```

---

## 9. 롤백 절차

```bash
sudo systemctl stop go100 go100-frontend
cd /root/kis-autotrade-v4
git revert HEAD --no-edit
PGPASSWORD='KisAuto2026!Secure' pg_restore -h localhost -U kis_admin -d kisautotrade \
  --clean --if-exists /tmp/backup_HOTFIX_CRITICAL_20260223_043545.dump
sudo systemctl start go100 go100-frontend
sleep 10
curl -s http://localhost:8002/health
curl -s -o /dev/null -w "frontend: %{http_code}\n" http://localhost:3000/go100
```

---

*CUR-GO100-HOTFIX-CRITICAL, 2026-02-23*
