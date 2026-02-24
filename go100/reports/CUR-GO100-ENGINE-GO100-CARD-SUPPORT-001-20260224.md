# CUR-GO100-ENGINE-GO100-CARD-SUPPORT-001
# auto_trade_engine GO100 전략카드 지원 + 스케줄 등록 연동

**발행일시:** 2026-02-24 12:00 KST  
**프로젝트:** kis-autotrade-v4  
**브랜치:** phase-2c-command-center

---

## 1. 개요

E2E-AUDIT-001에서 발견된 P0/P1 이슈 대응:

- go100_card_id와 card_id가 13~20 구간에서 ID 충돌
- auto_trade_engine._get_strategy_card()가 strategy_cards만 조회
- 스케줄 등록 드롭다운에서 GO100 카드 제외(임시 조치) 상태

**목표:** GO100 전략카드로 스케줄 등록 → 매매 엔진 실행 → 주문 체결까지 안전하게 연결. ID 충돌은 `card_source` 컬럼으로 해결.

---

## 2. 수정 내용

### 2.1 DB

- **v4_trade_schedules**에 `card_source VARCHAR(10) DEFAULT 'v41' NOT NULL` 추가
- 주석: `v41=strategy_cards`, `go100=go100_strategy_cards`
- 기존 스케줄은 기본값 `v41` 적용

### 2.2 백엔드 — auto_trade_engine.py

- **TradeSchedule** dataclass에 `card_source: str = "v41"` 추가
- **_get_strategy_card(schedule)**  
  - 인자: `card_id: int` → `schedule: TradeSchedule`  
  - `schedule.card_source == "go100"` → `go100_strategy_cards`에서 `go100_card_id`로 조회  
  - 그 외 → 기존대로 `strategy_cards`에서 `card_id`로 조회  
  - 반환 형태 동일: `strategy_type`, `strategy_params`, `strategy_name`
- **run_strategy**에서 `_get_strategy_card(schedule.strategy_id)` → `_get_strategy_card(schedule)` 호출로 변경

### 2.3 백엔드 — schedule_runner.py

- 스케줄 SELECT에 `COALESCE(card_source, 'v41') AS card_source` 추가
- **TradeSchedule** 생성 시 `card_source=(row.get("card_source") or "v41").strip()[:10] or "v41"` 전달

### 2.4 백엔드 — trade_router.py

- **ScheduleCreateRequest**에 `card_source: Optional[str] = Field("v41", ...)` 추가
- **POST /schedules** INSERT 시 `card_source` 컬럼·값 포함
- **GET /schedules** SELECT·응답에 `card_source` 포함

### 2.5 프론트엔드

- **types**: `TradeSchedule`에 `card_source?`, `ScheduleCreateRequest`에 `card_source?` 추가
- **ScheduleForm.tsx**
  - 선택 카드의 `source === "go100"`이면 `card_source: "go100"`으로 전달
  - 전략 선택 SelectItem에서 GO100 카드에 `[GO100]` 접두어 표시
- **trade/page.tsx**: 이미 `catalogCards` 전체를 ScheduleForm에 전달 중(GO100 필터 없음). `createSchedule` 호출 시 전달되는 payload에 `card_source` 포함됨(폼에서 설정)
- **lib/api/trade.ts**: `ScheduleCreateRequest` 타입에 `card_source` 포함되어 있어 별도 수정 없음

---

## 3. 변경 파일 목록

| 구분 | 경로 |
|------|------|
| BE | backend/app/services/auto_trade_engine.py |
| BE | backend/app/services/schedule_runner.py |
| BE | backend/app/api/v1/trade_router.py |
| BE | backend/tests/test_engine_integration.py |
| FE | frontend/src/types/index.ts |
| FE | frontend/src/components/trade/ScheduleForm.tsx |

---

## 4. 테스트 결과

- **DB:** `v4_trade_schedules.card_source` 컬럼 존재 및 기본값 확인
- **GO100 스케줄 연동:**  
  - GO100 카드로 스케줄 INSERT (card_source='go100') → 엔진 `_get_strategy_card(schedule)`로 go100_strategy_cards 조회 성공
- **pytest:** backend/tests/test_engine_integration.py 8 passed (test_schedule_runner_dry_run_execution 등)
- **tsc:** frontend `npx tsc --noEmit` 통과
- **npm run build:** frontend 빌드 성공
- 테스트 스케줄은 검증 후 `is_active = false`로 비활성화하여 장중 실행 방지

---

## 5. ID 충돌 해결 방식

- `card_source='v41'` → `strategy_cards`에서 `card_id`로 조회
- `card_source='go100'` → `go100_strategy_cards`에서 `go100_card_id`로 조회  
→ 동일한 숫자 ID라도 테이블이 분리되어 충돌 없음.

---

## 6. 완료 기준 체크

| 항목 | 결과 |
|------|------|
| v4_trade_schedules에 card_source 컬럼 존재 | ✅ |
| 기존 V4.1 스케줄 card_source='v41' 정상 동작 (회귀 없음) | ✅ |
| GO100 카드로 스케줄 등록 가능 | ✅ |
| auto_trade_engine이 card_source='go100' 시 go100_strategy_cards 조회 | ✅ |
| /trade 드롭다운에 GO100 카드 [GO100] 접두어 표시 | ✅ |
| npm build / pytest 통과 | ✅ |

---

*문서 repo: project-docs, branch: master*
