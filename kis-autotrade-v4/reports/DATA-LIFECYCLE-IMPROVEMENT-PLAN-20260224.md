# 데이터 생명 주기 개선안 — 확인·수집·관리

**작성일**: 2026-02-24  
**관련 문서**: [ADMIN-DATA-COLLECTION-PLAN-20260224.md](./ADMIN-DATA-COLLECTION-PLAN-20260224.md), [ADMIN-DATA-COLLECTION-PLAN-ADDENDUM-20260224.md](./ADMIN-DATA-COLLECTION-PLAN-ADDENDUM-20260224.md)  
**원칙**: 데이터가 생명이다. 데이터를 **확인**하고 **수집**하며 **관리**할 수 있는 체계를 갖춘다.

---

## 1. 개요

본 문서는 다음 세 가지를 반영한 **추가·확장 기획**이다.

| 번호 | 요구 | 요약 |
|------|------|------|
| 1 | **실시간 데이터 수집 현황** | 모든 수집 항목 표시, 실시간 갱신, 당일 일자·숫자 변동으로 “지금 수집 중” 가시화 |
| 2 | **분봉·섹터·순위 트리거 및 표 컬럼 확장** | 일자별 표·수집 트리거에 분봉·섹터·순위 포함 |
| 3 | **데이터 확인·수집·관리 종합 개선** | “데이터가 생명” 관점의 확인·수집·관리 추가 개선안 |

---

## 2. 실시간 데이터 수집 현황

### 2.1 목표

- **모든** 데이터 수집 항목을 한 화면에 나열.
- **실시간**으로 “지금 수집이 되고 있는지”를 알 수 있도록, **당일 일자·숫자 변동**을 보여 준다.

### 2.2 수집 항목 전체 목록 (표시 대상)

리포트 [DATA-COLLECTION-STATUS-REPORT-20260224.md](./DATA-COLLECTION-STATUS-REPORT-20260224.md) 기준, 관리자 화면에 노출할 **전체 항목**:

| 순번 | 데이터 종류 | 테이블/대상 | 당일/최신 표시 항목 | 실시간 변동 포인트 |
|------|-------------|-------------|---------------------|---------------------|
| 1 | 일봉 | ohlcv_daily | 당일 종목 수, 최신 일자 | 당일 장 마감 후 건수 증가 |
| 2 | 분봉 | v4_ohlcv_minute | 당일 건수, 최신 ts | 장중·배치 수집 시 건수·최신 ts 갱신 |
| 3 | 종목별 수급 | v4_investor_daily | 당일/최신 일자, 건수 | 장전 수집 후 건수·일자 갱신 |
| 4 | 시장 수급 | v4_market_investor_daily | 최신 일자, 건수 | 장후 수집 후 갱신 |
| 5 | 지수 일봉 | index_daily | 최신 일자 | 수집 후 갱신 |
| 6 | 시장 레짐 | v4_market_regime_daily | 최신 일자 | PRE_MARKET 후 갱신 |
| 7 | 섹터 일봉 | v4_sector_daily | 최신 일자, 건수 | 장전 수집 후 갱신 |
| 8 | 순위 | v4_market_ranking | 최신 일자, 건수 | 장전 수집 후 갱신 |
| 9 | 호가 실시간 | v4_orderbook_realtime | 당일/최신 행 수 | 장중 수집 시 실시간 증가 |
| 10 | 유니버스 | stock_universe | 활성 종목 수 | cron 후 갱신 |

- **실시간 변동**: 주기적 API 재조회 시 “이전 값 → 현재 값”이 바뀌면 **강조(색·아이콘)** 로 “방금 갱신됨”을 보여 주면 좋다.

### 2.3 API

- **기존 확장 또는 신규**:  
  - `GET /api/v1/monitoring/data-collection` 을 **전체 항목**으로 확장하거나,  
  - 관리자 전용 `GET /api/v4/admin/data-collection/realtime` (또는 `.../summary`) 를 두어,  
  - **모든** 위 테이블에 대해 **당일 건수/최신 일자/최신 ts** 를 한 번에 반환.

- **응답 필드 예 (전체 항목)**  
  - `ohlcv_daily_today`, `ohlcv_daily_latest_date`  
  - `v4_ohlcv_minute_today`, `v4_ohlcv_minute_latest_ts`  
  - `v4_investor_daily_today_count`, `v4_investor_daily_latest_date`  
  - `v4_market_investor_daily_latest_date`, `v4_market_investor_daily_count`  
  - `index_daily_latest_date`  
  - `v4_market_regime_daily_latest_date`  
  - `v4_sector_daily_latest_date`, `v4_sector_daily_count`  
  - `v4_market_ranking_latest_date`, `v4_market_ranking_count`  
  - `v4_orderbook_realtime_today_count`, `v4_orderbook_realtime_latest_ts`  
  - `stock_universe_active`  
  - `server_time` 또는 `queried_at` (클라이언트에서 “마지막 조회 시각” 표시용)

### 2.4 UI (실시간 블록)

- **위치**: 관리자 **데이터 수집** 탭 상단 고정 블록 “실시간 데이터 수집 현황”.
- **표시**:
  - **마지막 조회 시각**: `queried_at` 표시, 자동 갱신 주기 안내 (예: 15초마다 갱신).
  - **테이블**: 행 = 수집 항목(이름, 테이블), 열 = 당일 건수/종목 수, 최신 일자/시각, 상태(정상/지연/미수집).
  - **변동 강조**: 이전 조회 대비 값이 바뀐 셀은 짧은 시간(예: 3초) 동안 하이라이트(예: 배경색·펄스)로 “방금 갱신됨” 표현.
- **자동 갱신**: `refetchInterval` 15~30초 권장. “일시정지” 버튼으로 자동 갱신 중단 가능.

### 2.5 구현 포인트

- 백엔드: `get_data_collection_status()` 를 **전체 항목**으로 확장하거나, `get_data_collection_realtime_summary()` 신규 함수에서 위 테이블들을 읽기 전용으로 집계.
- 프론트: 이전 응답과 비교해 변경된 필드만 하이라이트. 관리자 데이터 수집 탭에 “실시간 수집 현황” 컴포넌트 배치.

---

## 3. 분봉·섹터·순위 트리거 및 표 컬럼 확장

### 3.1 일자별 표 컬럼 확장

**기존 (1차)**  
- 일봉, 분봉, 수급(종목별).

**확장 (필수)**  
- **분봉** — 이미 포함 시 유지.  
- **섹터 일봉** — `v4_sector_daily` 기준 일자별 건수/상태.  
- **순위** — `v4_market_ranking` 기준 (일자 컬럼 있으면 일자별, 없으면 “최신 1건” 표시).

**추가 권장 (전체 현황과 일치)**  
- 시장 수급 `v4_market_investor_daily`  
- 지수 일봉 `index_daily`  
- 시장 레짐 `v4_market_regime_daily`  
- (호가·유니버스는 일자별 개념이 다르면 별도 행/블록으로 처리)

**일자별 by-date API 응답 예 (확장)**  
- `rows[].v4_sector_daily`: `{ count, status }`  
- `rows[].v4_market_ranking`: `{ count, status }` (또는 latest_date 1건)  
- `rows[].v4_market_investor_daily`, `rows[].index_daily`, `rows[].v4_market_regime_daily` 동일 패턴.

### 3.2 수집 트리거 확장

**type 화이트리스트에 반드시 포함**  
- `minute` — 분봉: `collector_minute --days N` (백그라운드).  
- `sector` — 섹터: `run_daily_collection --sector --days N`.  
- `ranking` — 순위: `run_daily_collection --ranking` (일자 파라미터 유무 확인).

**추가 권장**  
- `market_investor` — 시장 수급 (스크립트 경로: `scripts/collect_market_investor.py` 등).  
- `index_daily` — 지수 일봉 (스크립트 경로: `scripts/collect_index_daily.sh` 등).  
- `regime` — 레짐 백필 스크립트 있으면 `backfill_regime_history.py` 등 연동.

**트리거 파라미터 정리**

| type | Body 예시 | 실행 명령/모듈 |
|------|-----------|----------------|
| ohlcv_daily | `dates`: ["20260223"] | collect_ohlcv_daily.py --dates 20260223,... |
| minute | `days`: 5 | collector_minute --days 5 |
| investor | `days`: 3 | run_daily_collection --investor --days 3 |
| sector | `days`: 5 | run_daily_collection --sector --days 5 |
| ranking | (선택 days) | run_daily_collection --ranking |
| market_investor | `days` 또는 `dates` | collect_market_investor.py (인자 확인) |
| index_daily | `days` 또는 `dates` | collect_index_daily.sh (인자 확인) |
| regime | (선택) | backfill_regime_history.py 등 |

- 분봉·섹터·순위는 **일자별 표**와 **수집 버튼** 모두에서 1차 스코프에 포함하는 것을 권장.

---

## 4. 데이터 확인·수집·관리 — 종합 개선안

“데이터가 생명”이라는 전제 아래, **확인(검증)·수집·관리**를 체계화하는 추가 개선안이다.

### 4.1 데이터 확인(검증)

| 개선안 | 설명 | 우선순위 |
|--------|------|----------|
| **전체 수집 항목 대시보드** | 2절 실시간 현황처럼 **모든** 항목을 한 화면에, 상태(정상/지연/미수집)와 함께 표시 | 높음 |
| **당일·숫자 변동 가시화** | 주기적 갱신 + 값 변경 시 하이라이트로 “지금 수집 중” 인지 직관적 인지 | 높음 |
| **일자별 기간 검색 표** | 기간 선택 시 일자×데이터종류별 건수/상태 표 (분봉·섹터·순위 포함 확장) | 높음 |
| **미수집·부분 수집 목록** | 자동 도출된 “미수집/부분” 항목 목록 + [수집] 버튼으로 보강 유도 | 높음 |
| **데이터 신선도(SLA) 정의** | 항목별 “기대 최신 일자” 규칙 (예: 일봉 = 당일 또는 전일, 분봉 = 당일) → 자동 상태 판정 | 중 |
| **품질 지표(선택)** | 구간 내 null 비율, 중복 건수(선택), 이상치 건수(선택) 등 간단 집계 노출 | 낮음 |

### 4.2 데이터 수집

| 개선안 | 설명 | 우선순위 |
|--------|------|----------|
| **통합 수집 트리거 API** | type별 수집 실행 (일봉·분봉·수급·섹터·순위·시장수급·지수·레짐 등), 백그라운드 실행·중복 방지 | 높음 |
| **수집 버튼 UX** | 미수집 목록/일자별 표에서 항목별 [수집] → 202 + “수집 중” 표시 → 완료 후 재조회 유도 | 높음 |
| **수집 이력(로그) 조회** | 최근 수집 실행 type·시작/종료 시각·성공/실패·건수 (DB 또는 로그 기반) 관리자 화면에서 조회 | 중 |
| **스케줄 가시화** | 크론·스케줄러에 등록된 수집 작업 목록과 “다음 예정 시각” 표시 (기존 크론 API 확장) | 중 |
| **실패 시 알림** | 수집 실패 시 기존 알림 채널(이메일 등) 또는 관리자 전용 알림으로 “어떤 항목·언제 실패” 전달 | 중 |

### 4.3 데이터 관리

| 개선안 | 설명 | 우선순위 |
|--------|------|----------|
| **보관 정책 가이드** | 테이블별 권장 보관 기간·용량 추정 문서화, 필요 시 파티션/아카이브 정책 명시 | 중 |
| **용량·행 수 추이** | 주간/월간 테이블별 행 수·용량 추이 (선택: 그래프) — 증설·정리 시점 판단 | 낮음 |
| **수집 설정 일원화** | 수집 주기·대상 종목 수 등 설정을 설정 테이블/환경변수로 두고, 관리자 화면에서 “현재 설정”만 조회 (변경은 선택) | 낮음 |
| **백업·복구 인지** | 중요 테이블(일봉·분봉·수급 등) 백업 주기·복구 절차 문서화, 관리자 화면에 “마지막 백업 일시” 링크/문구 | 낮음 |

### 4.4 로드맵 제안

**Phase 1 (필수)**  
- 실시간 데이터 수집 현황(전체 항목 + 당일·숫자 변동).  
- 일자별 기간 검색 표 (분봉·섹터·순위 컬럼 포함).  
- 미수집 목록 + 수집 버튼 + 트리거 API (일봉·분봉·수급·섹터·순위).

**Phase 2 (강화)**  
- 수집 이력 조회.  
- 데이터 신선도(SLA) 규칙 적용·상태 자동 판정.  
- 수집 실패 알림.

**Phase 3 (운영)**  
- 스케줄 가시화·보관 정책 가이드·용량 추이(선택)·백업 인지.

---

## 5. 정리

- **실시간 수집 현황**: 모든 수집 항목을 보여 주고, 주기적 갱신과 당일 일자·숫자 변동(및 변경 하이라이트)으로 “지금 수집 중”을 가시화한다.  
- **분봉·섹터·순위**: 일자별 표 컬럼과 수집 트리거 API에 반드시 포함하고, 필요 시 시장수급·지수·레짐까지 확장한다.  
- **데이터가 생명**: 확인(대시보드·일자별 표·미수집 목록·SLA)·수집(트리거·버튼·이력·알림)·관리(보관·용량·설정·백업 인지) 관점의 개선안을 단계적으로 도입한다.

이 문서는 [ADMIN-DATA-COLLECTION-PLAN-20260224.md](./ADMIN-DATA-COLLECTION-PLAN-20260224.md) 및 [ADMIN-DATA-COLLECTION-PLAN-ADDENDUM-20260224.md](./ADMIN-DATA-COLLECTION-PLAN-ADDENDUM-20260224.md) 와 함께, 관리자 데이터 수집 탭과 백엔드 API 확장의 단일 기준으로 사용할 수 있다.
