# 전략카드 모달 위치·삭제 수정 보고서 (2026-02-25)

**문서 ID:** CUR-GO100-STRATEGY-CARD-MODAL-DELETE-FIX-20260225  
**작업일:** 2026-02-25

## 1. 개요

- **전략카드 상세 모달 위치**: `/strategy-cards` 페이지에서 카드 클릭 시 모달이 화면 하단에 보여 사용자가 인지하지 못하는 문제 수정.
- **전략카드 삭제 실패**: 빈 카드(수익률/MDD/샤프 없음, 상태: 종료) 삭제 시 "삭제중..." 무한 대기 및 목록에서 사라지지 않는 문제 수정.

## 2. 수정 내용

### 2.1 모달 위치 (StrategyDetailModal)

- **파일:** `frontend/src/go100/components/StrategyDetailModal.tsx`
- **조치:** 모달 래퍼를 단일 컨테이너로 통합하고 뷰포트 기준 고정 배치 적용.
  - `position: fixed`, `inset: 0`, `z-index: 60`
  - `flex items-center justify-center`로 뷰포트 정중앙 배치
  - 오버레이: `absolute inset-0 bg-black/50`
  - 모달 본문: `relative z-10`, `max-h-[90vh] overflow-y-auto`
- **검증:** 상단/하단 카드 클릭 시 모달이 화면 정중앙에 즉시 표시, 배경 클릭 또는 닫기 버튼으로 닫힘, 내용 길 때 모달 내부 스크롤.

### 2.2 삭제 실패 (GO100 RETIRED 카드)

- **원인:**  
  - 카탈로그 API(`list_cards_with_system`, tab=my)에서 `card_status = 'RETIRED'` 카드도 반환하여, 삭제 후에도 목록에 그대로 노출됨.  
  - 이미 RETIRED인 카드 삭제 시 DB 변경 없이 성공만 반환해, 목록 갱신 후에도 카드가 남아 있음.
- **백엔드 수정**
  - **파일:** `backend/app/services/strategy_card_service.py`
    - `list_cards_with_system`에서 tab=my 및 fallback 분기 시 GO100 쿼리에  
      `AND (card_status IS NULL OR card_status != 'RETIRED')` 추가 → 삭제된(RETIRED) 카드는 목록에서 제외.
  - **파일:** `backend/app/services/go100/strategy/card_service.py`
    - `delete_card`에서 이미 `card_status == 'RETIRED'`인 경우에도  
      `is_active = false`로 UPDATE 후 `commit`하고 성공 반환 → 삭제 후 목록에서 제거되도록 일관 처리.
- **프론트엔드:**  
  - `/strategy-cards` 페이지에서 GO100 삭제 시 이미 `try/catch/finally`로 에러 시 `alert`, `setGo100DeletePending(false)` 적용됨.  
  - `deleteStrategyCard` API에 `timeout: 15000` 적용되어 있음.  
  - 별도 코드 변경 없이, 백엔드 수정만으로 삭제 후 목록 새로고침 시 카드 제거됨.
- **검증:** 빈(종료) 카드 삭제 → 즉시 삭제 완료 후 목록에서 제거. 삭제 실패 시 "삭제중..." 무한 대기 없이 에러 안내.

## 3. 백업·배포·푸시

- **백업:** `/root/backup/strategy-card-modal-delete-fix-20260225-224322` (기존 백업 디렉터리 활용)
- **코드 레포:** `kis-autotrade-v4` (go100)  
  - 브랜치: `feat/CUR-GO100-DATA-ENGINE-INTEGRATION`, `phase-2c-command-center`  
  - 커밋: `fix(go100): 전략카드 상세 모달 뷰포트 정중앙 배치 + RETIRED 카드 삭제/목록 제외` (a4afd96c)
- **배포:** `bash /root/kis-autotrade-v4/scripts/deploy.sh` 실행 완료 (백엔드 8002, 프론트 3000 헬스체크 OK)
- **문서 레포:** 본 보고서를 `project-docs`에 push

## 4. 경로 요약

| 구분 | 경로 |
|------|------|
| 백업 | `/root/backup/strategy-card-modal-delete-fix-20260225-224322` |
| 코드 레포 (배포 브랜치) | `github.com:moongoby/go100.git` → `phase-2c-command-center` |
| 문서 레포 | `/root/project-docs` (master) |
| 보고서 | `/root/project-docs/kis-autotrade-v4/reports/CUR-GO100-STRATEGY-CARD-MODAL-DELETE-FIX-20260225.md` |
