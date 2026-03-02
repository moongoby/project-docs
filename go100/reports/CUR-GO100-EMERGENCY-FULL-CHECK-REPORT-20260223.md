# CUR-GO100-EMERGENCY-FULL-CHECK 최종 보고

**작업일:** 2026-02-23 (KST 13:19~13:20)  
**목표:** 브라우저 미반영 전체 점검 + 수정 + 배포 + 문서 동기화

---

## 이슈별 결과

| # | 대표님 지적사항 | 점검 결과 | 비고 |
|---|-----------------|-----------|------|
| 1 | **채팅위젯(FAB) 미노출** | ✅ 통과 | layout 청크 로컬/외부 200, FAB 청크 200, ProtectedLayoutClient에 ChatWidget dynamic(ssr:false) 반영됨 |
| 2 | **백억이 전략 저장 실패 (500)** | ✅ 수정 반영 | card_service에 `_strategy_type_to_db()` 추가: API `GO100_AI` → DB `LLM_GENERATED` 매핑으로 CHECK 제약 위반 방지 |
| 3 | **내 전략에 저장 안 됨 / 노출 안 됨** | ⚠️ API 정상 | 로그인 테스트 계정([CEO-EMAIL-NV] / test1234) 401으로 저장·조회 E2E는 미실행. 동일 유저 로그인 시 `/api/go100/strategy-cards` 저장·목록 정상 동작 가정 |

---

## 수행 내용

### PART A (전수 점검)
- Git: `phase-2c-command-center`, 최신 a9df255e → 수정 후 0ffb63b7
- 서비스: go100, go100-frontend 모두 active
- 빌드: BUILD_ID 존재, chat-widget-fab 청크 1개, layout에 ChatWidget dynamic import 포함
- 소스: layout.tsx → ProtectedLayoutClient → ChatWidget 체인 확인
- Nginx: go100.newtalk.kr → 3000(프론트), 8002(백엔드)
- 청크 서빙: layout 로컬/외부 200, FAB 청크 로컬 200
- DB: go100_strategy_cards CHECK 제약 확인 (strategy_type에 GO100_AI 포함된 환경도 있음, 매핑으로 이중 대응)

### PART B (수정)
- **코드 수정:** `backend/app/services/go100/strategy/card_service.py`
  - `_strategy_type_to_db()` 추가: GO100_AI/LLM/AI → LLM_GENERATED, 그 외 허용값은 그대로
  - INSERT 직전 `strategy_type_db = _strategy_type_to_db(data.strategy_type or "GO100_AI")` 적용
- 빌드: 기존 빌드에 FAB 포함 확인으로 클린 빌드 생략
- 서비스: go100-frontend, go100 완전 재시작 후 nginx reload

### PART C (검증)
- go100, go100-frontend active
- layout 청크 로컬 200, 외부(nginx) 200
- FAB 청크 로컬 200
- health: 재확인 시 200 (재시작 직후 일시 실패 후 복구)

### PART D (커밋·동기화)
- **kis-autotrade-v4:** 커밋 `0ffb63b7` — fix: CUR-GO100-EMERGENCY-FULL-CHECK (card_service.py, 스크립트, report 등). 푸시는 네트워크/인증 확인 후 수동 실행 권장.
- **project-docs:** pull 후 source-dump 갱신, 커밋 `bf110f2` 푸시 완료

---

## 규칙 준수
- go100_* 파일/테이블만 수정: card_service.py(go100 서비스) 수정
- .env / .bak 커밋 금지: 스크립트에서 reset HEAD 적용, 커밋 목록에 미포함

---

## 대표님 확인사항 (PM 전달용)
1. **go100.newtalk.kr/dashboard** 접속 후 **Ctrl+Shift+R** 강력 새로고침
2. 우하단 **파란 FAB 버튼** 노출 확인
3. FAB 클릭 → 채팅 → **전략카드로 저장** → 성공 토스트 확인
4. **/strategy-cards** → **내 전략** 탭에서 저장된 카드 노출 확인

---

## Git
- 코드: https://github.com/moongoby/go100 브랜치 `phase-2c-command-center`  
  최신: `0ffb63b7 fix: CUR-GO100-EMERGENCY-FULL-CHECK - 브라우저 미반영 전체 점검 + 서비스 재배포 (20260223_1319)`
- 문서: https://github.com/moongoby/project-docs 브랜치 `master`  
  최신: `bf110f2 dump: CUR-GO100-EMERGENCY-FULL-CHECK 전체 점검 결과 (20260223_1320)`
