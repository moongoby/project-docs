# 키움증권 조건식 수집 기능 확인 보고서

- **일자**: 2026-02-27
- **요청**: 키움증권 조건식(조건검색) 수집 기능 현황 확인 및 보고

---

## 1. 기능 개요

키움증권 조건식(조건검색)은 HTS에서 사용자가 설정한 기술적/재무적 필터 조건에 부합하는 종목을 실시간으로 추출하는 기능입니다. V4.1 시스템에는 이 조건식 결과를 REST API(ka10050)로 수집하여 DB에 적재하는 코드가 **Phase3 데이터 수집 단계에서 구현**되어 있습니다.

---

## 2. 구현 현황 (코드 레벨)

### 2-1. 구현 완료된 항목

| 구성요소 | 파일/위치 | 상태 |
|----------|----------|------|
| 수집기 | `backend/app/services/data/condition_search_collector.py` | 구현 완료 |
| DB 테이블 | `v4_condition_search` (11개 컬럼, 인덱스 3개) | 생성 완료 |
| Phase3 스케줄러 | `backend/app/services/phase3_data_scheduler.py` | 등록 완료 (5분 간격) |
| API 엔드포인트 | `GET /api/v1/market/condition-search` | 등록 완료 |

### 2-2. 수집기 데이터 흐름

```
조건식 목록 조회 (DB or config JSON)
    ↓
조건별 키움 REST API 호출 (ka10050, /api/dostk/condition-search)
    ↓
응답 파싱 (종목코드, 종목명, IN/OUT 신호, 현재가, 거래량, 등락률)
    ↓
v4_condition_search 테이블 INSERT
```

### 2-3. DB 테이블 스키마 (`v4_condition_search`)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL PK | 자동 증가 |
| condition_name | VARCHAR(100) NOT NULL | 조건식 이름 |
| condition_id | INTEGER | 조건식 ID (키움 내부) |
| stock_code | VARCHAR(10) NOT NULL | 종목코드 |
| stock_name | VARCHAR(50) | 종목명 |
| signal_type | VARCHAR(10) | IN(진입)/OUT(이탈) |
| signal_time | TIMESTAMPTZ NOT NULL | 시그널 발생 시각 |
| current_price | INTEGER | 현재가 |
| volume | BIGINT | 거래량 |
| change_rate | NUMERIC(8,4) | 등락률 |
| created_at | TIMESTAMPTZ | 수집 시각 |

인덱스: `(condition_name, signal_time)`, `(stock_code)`

### 2-4. Phase3 스케줄러 등록

```
09:00~15:30 매 5분 → run_condition_search_collect() 호출
```

### 2-5. API 엔드포인트

```
GET /api/v1/market/condition-search?condition_name=급등주
→ { "data": [...], "disclaimer": "..." }
```

---

## 3. 현재 운영 상태: 미작동 (no_condition_list)

### 3-1. 증상

Phase3 로그에서 5분마다 아래 메시지가 반복됨:

```
Phase3 condition_search: {'ok': 0, 'inserted': 0, 'conditions': 0, 'skipped': 'no_condition_list'}
```

### 3-2. 원인

**조건식 목록이 등록되어 있지 않음** — 부트스트랩 미완료

수집기는 조건식 목록을 2곳에서 탐색합니다:

1. **DB** (`v4_condition_search` 테이블에서 DISTINCT condition_name 조회) → **0건** (한 번도 수집한 적 없으므로)
2. **설정 파일** (`config/condition_search.json`) → **파일 없음**

두 소스 모두 비어 있어 수집 자체가 시작되지 않는 **순환 의존성(Circular Dependency)** 상태입니다:
- 수집하려면 조건식 목록이 필요
- 목록은 수집 결과에서 가져옴
- 최초 시드(seed)가 없어 영원히 스킵

### 3-3. 현재 데이터

| 항목 | 값 |
|------|-----|
| v4_condition_search 레코드 | **0건** |
| config/condition_search.json | **없음** |
| Phase3 실행 | 정상 (5분마다 호출되지만 즉시 스킵) |

---

## 4. 활성화에 필요한 작업

### 4-1. 조건식 목록 시드 등록

`config/condition_search.json` 파일을 생성하여 수집할 조건식을 등록해야 합니다:

```json
{
  "conditions": [
    {"condition_name": "급등주", "condition_id": 1},
    {"condition_name": "거래량폭증", "condition_id": 2},
    {"condition_name": "골든크로스", "condition_id": 3},
    {"condition_name": "기관순매수", "condition_id": 4}
  ]
}
```

> **주의**: 조건식 이름과 ID는 키움 HTS에서 실제 생성/등록된 조건식과 일치해야 합니다.

### 4-2. 키움 REST API(ka10050) 조건검색 지원 확인

키움 REST API에서 조건검색(ka10050)이 실제로 지원되는지 확인 필요합니다. 코드에는 graceful skip 처리가 있어 미지원 시에도 에러 없이 빈 결과를 반환합니다.

### 4-3. 키움 HTS에서 조건식 사전 등록

키움증권 HTS/MTS에서 조건식을 먼저 생성·저장해야 REST API로 조회 가능합니다. 조건식은 사용자 계정에 종속되므로, V4.1에 등록된 키움 계정(account_id=4)의 HTS에서 만들어야 합니다.

---

## 5. 종합 평가

| 항목 | 평가 |
|------|------|
| 코드 구현 | **완료** — 수집기, DB, 스케줄러, API 모두 구현됨 |
| 운영 상태 | **미작동** — 조건식 목록 미등록 (부트스트랩 미완료) |
| 데이터 | **0건** |
| 활성화 난이도 | 중 — 키움 HTS에서 조건식 생성 + config 파일 등록 필요 |
| 시스템 영향 | 없음 — graceful skip으로 다른 수집에 영향 없음 |

**결론**: 조건식 수집 코드는 완전히 구현되어 있으나, **키움 HTS에서 조건식을 생성하고 config 파일에 등록하는 초기 설정 작업**이 필요합니다. 현재는 조건식 목록이 없어 5분마다 스킵되고 있으며, 다른 데이터 수집에는 영향이 없습니다.

---

*Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>*
