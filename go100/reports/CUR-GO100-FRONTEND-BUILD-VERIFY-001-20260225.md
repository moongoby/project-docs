# CUR-GO100-FRONTEND-BUILD-VERIFY-001 — 프론트엔드 빌드 검증 + UI 통합 테스트 보고서

**작성:** 2026-02-25  
**작업ID:** CUR-GO100-FRONTEND-BUILD-VERIFY-001  
**목표:** 프론트엔드 빌드 검증 + GoalScenarioCards/GoalStrategyResult UI 통합 테스트  
**브랜치:** phase-2c-command-center  
**코드 경로:** /root/kis-autotrade-v4/frontend

---

## 1. 요약

- **TypeScript:** `npx tsc --noEmit` 에러 0건 통과.
- **빌드:** `npm run build`(Next.js 14.2.35) 성공 — Compiled successfully, 정적 페이지 32/32 생성, `.next` 산출물 정상.
- **UI 컴포넌트:** GoalScenarioCards.tsx, GoalStrategyResult.tsx 존재 및 ChatWidget 연동·타입 일치 확인.
- **pre-commit:** `scripts/pre-commit-check.sh` 통과.
- **코드 수정:** 없음. 배포 후 브라우저 체크리스트는 운영 측에서 수행.

---

## 2. 백업

| 항목 | 값 |
|------|-----|
| 경로 | `/root/backup/frontend-verify-20260225-103450/go100` |
| 내용 | `frontend/src/go100/` 전체 복사 |

---

## 3. TypeScript 검증

```bash
cd /root/kis-autotrade-v4/frontend
npx tsc --noEmit 2>&1 | tee /tmp/tsc-result.txt
```

- **결과:** 에러 0건.
- **TSC 에러 수:** 0

---

## 4. 빌드 검증

```bash
npm run build 2>&1 | tee /tmp/build-result.txt
```

- **결과:** 성공.
- **판정:** `Compiled successfully` 포함 → ✅ 빌드 성공.
- **산출:** `.next/` 디렉터리 생성 확인 (BUILD_ID, build-manifest.json 등).

---

## 5. UI 컴포넌트 검증

### 5.1 파일 존재

| 파일 | 경로 | 비고 |
|------|------|------|
| GoalScenarioCards | frontend/src/go100/components/GoalScenarioCards.tsx | 존재 |
| GoalStrategyResult | frontend/src/go100/components/GoalStrategyResult.tsx | 존재 |

### 5.2 ChatWidget import·사용

- `ChatWidget.tsx` 19–20행: `GoalScenarioCards`, `GoalStrategyResult` import.
- 181–191행(전체화면), 310–320행(위젯):  
  `m.data?.scenarios` → `<GoalScenarioCards scenarios={...} onSelect={...} disabled={...} />`  
  `m.data?.created_cards` → `<GoalStrategyResult createdCards={...} goalName={...} />`

### 5.3 타입 (ai.ts)

- `GoalScenario`: name, cagr, projected, risk, mc_median?, mc_success_prob?
- `GoalCreatedCard`: card_id, name, backtest?
- `GoalChatData`: parsed_goal?, required_cagr?, scenarios?, goal?, created_cards?
- `ChatWidget` 내부 `Msg`: `data?: GoalChatData` — ai.ts 타입과 호환.

---

## 6. 브라우저 테스트 체크리스트 (배포 후)

go100.newtalk.kr 접속 후 아래 항목은 **운영/QA**에서 확인 권장.

- [ ] 로그인 정상
- [ ] 백억이 채팅 위젯 열림
- [ ] "5천만원으로 3년 안에 3억" 입력 → 시나리오 카드 3개 표시
- [ ] 카드에 CAGR, 예상금액, 리스크, 성공확률 표시
- [ ] 카드 클릭 시 "공격적" 등 키워드 자동 전송
- [ ] 2턴 응답 후 GoalStrategyResult 표시
- [ ] 전략카드 링크 클릭 → 전략 상세 페이지 이동
- [ ] 기존 채팅 기능(일반 대화, 전략 생성) 정상 동작

---

## 7. 규칙 체크리스트

| 항목 | 상태 |
|------|------|
| kis-v41-* 재시작 없음 | ✅ |
| 실계좌 미사용 | ✅ |
| 백업 완료 | ✅ |
| go100_ 파일만 수정 | ✅ (수정 없음) |
| pre-commit-check 통과 | ✅ |
| tsc --noEmit 통과 | ✅ |
| npm run build 성공 | ✅ |
| 보고서 GitHub push | ✅ (아래 수행) |

---

## 8. 다음 단계

- 배포 후 **섹션 6** 브라우저 체크리스트 실행.
- 수정 발생 시: 수정 → pre-commit-check → tsc --noEmit → npm run build → 커밋/푸시 → `systemctl restart go100-frontend` (go100-frontend만 재시작).
