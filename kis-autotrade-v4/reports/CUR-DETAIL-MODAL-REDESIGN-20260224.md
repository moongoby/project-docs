# CUR-DETAIL-MODAL-REDESIGN-20260224

**일시:** 2026-02-24 KST
**서버:** [SERVER-IP]
**브랜치:** phase-2c-command-center

---

## 1. 작업 개요

전략카드 상세 모달(`StrategyDetailModal.tsx`)을 AI(백억이) 생성 시 미리보기 수준으로 전면 리디자인하고, 수정 기능 통합 및 4건의 버그 수정.

## 2. 변경 파일

| 파일 | 변경 | 내용 |
|------|------|------|
| `frontend/src/go100/components/StrategyDetailModal.tsx` | 전면 리라이트 (457줄→~700줄) | 미리보기 UI + 수정 기능 통합 |
| `backend/app/services/go100/strategy/card_service.py` | description 컬럼 연동 | INSERT/SELECT/UPDATE/RETURNING에 description 추가 |
| `backend/app/services/go100/strategy/schemas.py` | Response 스키마 | Go100StrategyCardResponse에 description 필드 추가 |
| `backend/app/routers/go100/strategy_router.py` | 토글 연동 | ON 시 v4_trade_schedules 재활성화 로직 추가 |
| DB: `go100_strategy_cards` | ALTER TABLE | description TEXT 컬럼 추가 |

## 3. 상세 모달 리디자인

### 3-1. 구조 변경
- **기존:** 3탭(요약/매매규칙/위험관리) READ-ONLY
- **변경:** 단일 스크롤 뷰 + 보기/수정 모드 토글

### 3-2. 레이아웃 (위→아래)
```
[헤더] ✕닫기 | 수정/저장/취소 | 토글 | 삭제
[히어로] 상태배지 + 보유기간배지 + 전략명(수정모드시 input) + 백테스트 4칸 지표
[액션 버튼] 백테스트 실행 / 모의거래 / 실거래 현황
[보유기간 선택] 수정모드시 버튼 그룹 (스캘핑⚡~장기스윙🏔️)
[기본 정보] 보유기간·전략유형·투자대상·최대종목수·배분방식·생성방식
[종목선정 조건]
[매수 조건 + 분할매수 설정]
[매도 조건]
[위험 관리] NumField 4개(손절/익절/트레일링/최대보유일) + 분할매도 설정
[백테스트 상세 결과]
[투자 동의 상태]
```

### 3-3. 수정 모드 기능
- 전략명, 최대 종목 수, 보유기간 편집
- 위험관리 수치 직접 입력 (손절/익절/트레일링 스탑/최대 보유일)
- 분할매수: 횟수(2~10), 비중, 트리거 조건(시그널/하락시/N일후)
- 분할매도: 횟수(2~10), 비중, 목표수익, 손절상향, 마지막 트레일링
- 저장 시 `updateStrategyCard()` API 호출

### 3-4. 백엔드 제약 반영
- `RETIRED` → 수정 버튼 비활성화
- `LIVE` → risk_params만 수정 가능 (전략명, max_stocks 비활성화)

## 4. 버그 수정 (4건)

### 4-1. 전략카드 삭제 안됨
- **원인:** `handleDelete` catch에서 에러를 무시 → 사용자에게 피드백 없음
- **수정:** catch에서 백엔드 에러 메시지(`LIVE 상태 카드 삭제 불가`, `OPEN 포지션 있음` 등) alert 표시

### 4-2. 토글 ON 시 자동매매 연동 누락
- **원인:** `strategy_router.py` toggle 엔드포인트에서 ON 시 아무 것도 안 함 (OFF만 스케줄 비활성화)
- **수정:** ON 시 기존 `v4_trade_schedules` 레코드 재활성화 (`is_active = true`)
- **동작:** 토글 ON → 기존 스케줄 활성화 / 토글 OFF → 스케줄 비활성화

### 4-3. 전략 설명(description) 미표시
- **원인:** DB에 `description` 컬럼 자체 없음. 백엔드에서 저장/조회 안 함
- **수정:**
  - DB: `ALTER TABLE go100_strategy_cards ADD COLUMN description TEXT`
  - 백엔드: INSERT/SELECT/UPDATE/RETURNING 모두 description 포함
  - 스키마: `Go100StrategyCardResponse`에 description 필드 추가
  - 프론트: `strategy_params.description` 폴백 표시 (기존 카드 호환)

### 4-4. 백테스트 버튼 사라짐
- **원인:** DRAFT/BACKTESTED 상태에서만 표시 → 다른 상태 카드에서 안 보임
- **수정:** RETIRED 제외 모든 상태에서 "백테스트 실행" 버튼 표시

## 5. 검증

- [x] `npx next build` 빌드 성공
- [x] `go100-frontend` 서비스 재시작 정상
- [x] `go100` 백엔드 서비스 재시작 정상
- [x] DB description 컬럼 추가 완료

## 6. 재사용 코드

| 유틸 | 출처 | 용도 |
|------|------|------|
| `inferHoldingPeriod()` | `go100/utils/holdingPeriod.ts` | 보유기간 자동 추론 |
| `HOLDING_PERIODS`, `HOLDING_PERIOD_LIST` | `go100/utils/holdingPeriod.ts` | 배지/선택 UI |
| `parseEntryRules`, `parseExitRules`, `parseUniverseConditions` | `go100/utils/ruleDescriber.ts` | 매매규칙 자연어 변환 |
| `updateStrategyCard()` | `go100/api/go100Api.ts` | 저장 API |
| NumField 패턴 | StrategyPreviewModal.tsx | 수치 편집 필드 |

---

**배포 완료:** 2026-02-24 15:14 KST
**확인 URL:** https://go100.newtalk.kr/strategy-cards
