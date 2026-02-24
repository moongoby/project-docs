# CUR-STRATEGY-SAVE-BACKTEST-PIPELINE 완료 보고서

**작업일**: 2026-02-24
**커밋**: `f7043ab6` (phase-2c-command-center)
**백업 태그**: `backup-before-preview-modal-20260224`

---

## 1. 작업 개요

백억이(LLM 채팅)에서 AI가 설계한 전략을 **미리보기 → 저장 → 백테스트 실행**까지 원스톱으로 연결하는 파이프라인 구축.

### 핵심 요구사항
1. 전략 저장 전 **미리보기 모달** — 규칙을 자연어로 확인 후 저장
2. **universe_filter 또는 종목 미지정 시 저장 차단** — 백억이에서 반드시 설정
3. 백테스트 **기본값 자동세팅** (최근 3개월, 자본금 1천만원) + 사용자 수정 가능
4. GO100 백테스트 **결과 대폭 확장** (등급, 에퀴티 커브, 매매 이력, 종목별 성과)

---

## 2. 변경 파일 (9개)

| 파일 | 변경 유형 | 설명 |
|------|-----------|------|
| `go100/utils/ruleDescriber.ts` | **NEW** | 전략 규칙 JSON→자연어 변환 공용 유틸 (9개 함수) |
| `components/chat/StrategyPreviewModal.tsx` | **NEW** | 2단계 미리보기 모달 (preview → success + 백테스트 링크) |
| `components/chat/StrategyCardSaveButton.tsx` | REWRITE | 기존 인라인 저장 제거, PreviewModal 연동 |
| `app/(protected)/backtest/page.tsx` | MAJOR | 동적 기본값, 쿼리 파라미터, 빠른선택, GO100 결과 확장 |
| `go100/components/StrategyDetailModal.tsx` | REFACTOR | ruleDescriber 공용 유틸 import로 ~100줄 중복 제거 |
| `app/(protected)/go100/strategies/[id]/page.tsx` | REFACTOR | ruleDescriber import 추가 |
| `app/(protected)/portfolio/page.tsx` | BUGFIX | 미사용 onStockClick prop 제거 (기존 빌드 오류) |
| `lib/api/admin.ts` | BUGFIX | DataCollectionTab용 타입·함수 export 추가 (기존 빌드 오류) |
| `report/STRATEGY-SAVE-BACKTEST-PIPELINE-PLAN-20260224.md` | **NEW** | 기획서 |

---

## 3. 기능 상세

### 3-1. 전략 미리보기 모달 (StrategyPreviewModal)

**위치**: 백억이(`/llm`) 채팅에서 "전략카드로 저장" 버튼 클릭 시

| 항목 | 내용 |
|------|------|
| 전략명 | 입력 필드 (수정 가능, 기본값: AI가 제안한 이름) |
| 투자 금액 | 입력 필드 (수정 가능, 기본값: 채팅에서 설정한 금액) |
| 종목발굴 조건 | universe_filter JSON → 자연어 (예: "시가총액 5000억 이상, RSI 30 이하") |
| 매수 규칙 | entry_rules JSON → 자연어 |
| 매도 규칙 | exit_rules JSON → 자연어 |
| 리스크 관리 | risk_params JSON → 자연어 (손절/익절/최대보유일) |
| 저장 차단 | universe_filter AND ticker 둘 다 없으면 "백억이에게 조건 요청 →" 링크 표시, 저장 불가 |
| 저장 완료 | "바로 백테스트 실행 →" 링크 (go100_card_id + 3개월 + 1천만원 자동세팅) |

### 3-2. 백테스트 페이지 개선

**기본값 & 빠른선택**:
- 시작일: 오늘 - 3개월 (동적 계산)
- 종료일: 오늘
- 자본금: 1,000만원
- 기간 빠른선택: 1개월 / 3개월 / 6개월 / 1년
- 자본금 빠른선택: 500만 / 1,000만 / 3,000만 / 5,000만

**URL 쿼리 파라미터 자동세팅**:
```
/backtest?go100_card_id=42&start_date=2025-11-24&end_date=2026-02-24&capital=10000000
```
→ GO100 카드 자동 선택, 날짜·자본금 자동 입력

**GO100 결과 확장**:

| 항목 | 설명 |
|------|------|
| 성과 등급 | ★1~5 (수익률/MDD/승률 기반 복합 평가) |
| 에퀴티 커브 | equity_curve 데이터로 막대 차트 렌더링 |
| 매매 이력 | 필터(전체/수익/손실) + 정렬(날짜/손익) 지원 테이블 |
| 종목별 성과 | 종목코드별 매매 횟수, 승률, 합산 수익률 |
| 청산 사유 분석 | 손절/익절/시간 종료 등 비율 차트 |
| 전략 규칙 요약 | 카드에 설정된 매매규칙 자연어 표시 |
| 다음 액션 | "백억이에게 개선 요청" / "모의거래 시작" / "내 전략 카드" 링크 |

### 3-3. ruleDescriber 공용 유틸

| 함수 | 용도 |
|------|------|
| `fmtNum()` | 숫자 콤마 포맷 |
| `describeCondition()` | 단일 조건 → 한국어 (예: "RSI ≤ 30") |
| `describeEntry()` | 매수 규칙 → 한국어 |
| `describeExit()` | 매도 규칙 → 한국어 |
| `parseUniverseConditions()` | universe_filter → `{label, value}[]` |
| `parseEntryRules()` | entry_rules → `{label, value}[]` |
| `parseExitRules()` | exit_rules → `{label, value}[]` |
| `describeUniverse()` | universe_filter → 한 줄 요약 |
| `hasValidUniverseOrTicker()` | 저장 가능 여부 판별 |

**사용처**: StrategyPreviewModal, StrategyDetailModal, [id]/page, backtest/page

---

## 4. 기존 빌드 오류 수정 (부수 작업)

| 파일 | 오류 | 원인 | 조치 |
|------|------|------|------|
| portfolio/page.tsx | `onStockClick` prop 없음 | HoldingsTable에 해당 prop 미정의 | prop 제거 |
| admin.ts | DataCollectionMissingItem 미export | DataCollectionTab이 참조하는 타입/함수 미구현 | 타입·함수 추가 |

---

## 5. 사용자 흐름 (End-to-End)

```
[백억이 /llm] AI와 전략 대화
    ↓
"전략카드로 저장" 버튼 클릭
    ↓
[StrategyPreviewModal] 미리보기
  - 전략명 수정 가능
  - 투자금액 수정 가능
  - 규칙을 자연어로 확인
  - universe_filter 없으면 → 저장 차단, "백억이에게 조건 요청 →"
    ↓
"저장" 클릭 → API 호출 → 저장 완료
    ↓
"바로 백테스트 실행 →" 클릭
    ↓
[/backtest] 자동세팅 상태로 이동
  - GO100 카드 자동 선택
  - 기간: 최근 3개월
  - 자본금: 1,000만원
  - 사용자 자유 수정 가능
    ↓
"백테스트 실행" → 결과 표시
  - 등급 ★★★ / 수익 요약
  - 에퀴티 커브 차트
  - 매매 이력 (필터/정렬)
  - 종목별 성과
  - 청산 사유 분석
    ↓
다음 액션 선택:
  ├ "백억이에게 개선 요청" → /llm
  ├ "모의거래 시작" → /go100/paper-trading
  └ "내 전략 카드" → /strategy-cards
```

---

## 6. 미구현 항목 (향후)

| 항목 | 설명 | 우선순위 |
|------|------|----------|
| 종목별 시그널 타이밍 차트 | 캔들스틱 + 매수/매도 마커 오버레이 | 높음 |
| 백테스트 결과 저장 + 비교 | 여러 백테스트 결과를 비교하는 UI | 중간 |
| 전략 최적화 제안 | 백테스트 결과 기반 AI 개선 제안 | 중간 |

---

## 7. 배포 정보

- **프론트엔드**: go100-frontend (systemctl) — 정상 운영 확인
- **백엔드**: go100 — 변경 없음 (health OK)
- **빌드**: Next.js 14.2.35 — 경고/오류 0건
- **Git**: `f7043ab6` → origin/phase-2c-command-center push 완료
- **문서**: project-docs sync 완료
