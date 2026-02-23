# 백억이 종목 정보 제공 기능 기획 보고서 (Genspark 스타일)

**작성일**: 2026-02-24  
**요청**: (1) Genspark AI처럼 종목 질의에 대해 구조화된 답변 제공 가능 여부 (2) 시스템 내 종목 클릭 → 1차 우리 사이트 데이터, 없으면 증권사 API 검색 제공 기획

---

## 1. 요약 및 결론

| 항목 | 결론 |
|------|------|
| **Genspark 스타일 답변 가능 여부** | **가능** — 1차 우리 DB 기반 요약, 2차 KIS 증권사 API로 상세 정보 보강 후, 채팅으로 구조화된 문장/블록으로 제공 가능 |
| **종목 클릭 → 정보 제공** | **가능** — 거래내역·포트폴리오 등에서 종목 클릭 시, 해당 종목 컨텍스트를 백억이 채팅으로 전달하고 위와 동일한 1차/2차 정보 흐름으로 응답 가능 |
| **1차 우리 사이트 데이터** | **보유** — `stock_universe`(종목명, 시장, 시총, PER/PBR 등), `ohlcv_daily`, 사용자 `v4_trade_executions`(해당 종목 거래 이력) |
| **2차 증권사 API** | **사용 가능** — KIS 오픈API **주식기본조회(CTPF1002R)** `/uapi/domestic-stock/v1/quotations/search-stock-info` (종목코드 6자리 + 상품유형 300). **모의투자 미지원** → 실전 앱키 필요 |

---

## 2. Genspark AI 스타일과의 대응

- **Genspark**: 종목 질의 시 “검색 쿼리 → 주가 조회 → 웹 Fetch(zum, fnguide 등)”를 **단계별로 노출**하고, 그 결과를 종합해 답변.
- **우리 시스템에서의 대응**:
  - **1차: 우리 사이트 데이터** — DB의 `stock_universe`, 필요 시 `ohlcv_daily` 요약, 사용자 거래 이력(해당 종목)을 조회해 요약 블록 생성.
  - **2차: 증권사 API** — 우리 DB에 없거나 보강이 필요할 때 KIS **종목상세정보(CTPF1002R)** 호출해 당일/전일 종가, 업종, 거래정지/관리종목 여부 등 반영.
  - **표시 방식(선택)**  
    - 간단: 채팅 답변 내에 “(1차 우리 데이터 기준 … / 2차 증권사 API로 확인한 …)” 식으로 문장에 포함.  
    - Genspark에 가깝게: “1차 우리 사이트 데이터”, “2차 증권사 API 검색” 같은 **소제목/블록**으로 구분해 표시.

---

## 3. 현재 시스템 정리

### 3.1 우리 사이트가 가진 “종목 관련” 데이터

| 데이터 | 테이블/소스 | 활용 가능 내용 |
|--------|-------------|----------------|
| 종목 마스터 | `stock_universe` | `stock_code`, `stock_name`, `market`, `market_cap`, `per`, `pbr`, `eps`, `dividend_yield`, `sector` 등 |
| 일봉 | `ohlcv_daily` | 최근 종가, 거래량, 기간 수익률 등 요약 |
| 사용자 거래 | `v4_trade_executions` | 해당 종목 매수/매도 이력, 체결가, 수량 |
| 백테스트 결과 | 전략별 `trade_log` | 전략 관점에서의 해당 종목 매매 이력(선택) |

→ **1차 정보**는 위 데이터만으로도 “종목명, 시장, 시총/PER 등 요약 + (선택) 우리 플랫폼 내 거래 이력”까지 제공 가능.

### 3.2 증권사 API (KIS)

| API | TR_ID | 용도 | 비고 |
|-----|--------|------|------|
| 주식현재가 | FHKST01010100 | 현재가, 전일대비 등 | 이미 `broker_kis_adapter.get_quote()` 등에서 사용 |
| **주식기본조회(종목상세)** | **CTPF1002R** | 종목상세정보(상품명, 당일/전일 종가, 업종, 거래정지/관리종목 등) | **모의투자 미지원**, 실전 앱키 필요 |
| 종목정보조회 | CTPF1604R | 종목 검색 | 필요 시 검색용으로 추가 |

- CTPF1002R 요청: GET, Query `PRDT_TYPE_CD=300`, `PDNO=종목코드(6자리)`.
- 응답: `prdt_name`, `prdt_abrv_name`, `thdt_clpr`, `bfdy_clpr`, `std_idst_clsf_cd_name`, `tr_stop_yn`, `admn_item_yn` 등 풍부한 메타데이터.

### 3.3 백억이(Go100 AI) 현재 구조

- **의도 분기**: `intent_router` → `help`(사용법/화면) / `strategy`(전략 설계).
- **채팅 진입점**: `POST /api/go100/ai/chat` (body: `message`, `conversation_history`, `source` 등).
- **데이터 연동**: 현재는 전략 설계 시 백테스트 요약 등 **구조화된 결과만** LLM에 전달하며, 실시간 시세/DB 원본은 직접 넣지 않음.

→ 종목 정보 답변을 위해 **새 의도(stock_info)** 와 **전용 플로우(1차 DB → 2차 KIS)** 를 추가하는 방식이 자연스럽다.

---

## 4. 제안 기능 요구사항

### 4.1 기능 1: “종목 OOO 알려줘” / “OOO(001510) 정보”

- **트리거**:  
  - 사용자가 채팅에 종목명/종목코드(예: “SK증권 001510”, “001510 알려줘”)를 포함하거나,  
  - **종목 클릭**으로 넘어온 컨텍스트(`stock_code`, `stock_name`)가 있을 때.
- **동작**:  
  1. **1차**: 우리 DB 조회  
     - `stock_universe`에서 해당 종목 기본 정보(이름, 시장, 시총, PER/PBR 등).  
     - 필요 시 `ohlcv_daily`로 최근 종가/수익률 요약.  
     - (선택) 해당 사용자 `v4_trade_executions`에서 해당 종목 거래 요약.  
  2. **2차**: 1차에서 부족하거나 최신 시세/상세가 필요할 때 KIS **CTPF1002R** 호출.  
  3. 1차+2차 결과를 조합해 **일관된 문장/블록**으로 답변 생성(Genspark 스타일 선택 시 “1차 우리 데이터”, “2차 증권사 API” 구역 표시).

### 4.2 기능 2: 시스템 내 “종목 클릭” → 백억이로 컨텍스트 전달

- **대상 화면**:  
  - 자동매매 **거래내역** (`TradeHistoryPanel` — “종목” 컬럼에 `stock_name`, `stock_code` 노출).  
  - (추가 시) 포트폴리오, 백테스트 결과 테이블 등 종목이 나오는 목록.
- **동작**:  
  - 종목명/코드 셀을 **클릭 가능**하게 변경.  
  - 클릭 시:  
    - **옵션 A**: 백억이 전체화면(`/llm`)으로 이동 + **쿼리 파라미터**로 `stock_code`, `stock_name` 전달 → 채팅 입력창에 “{종목명}({코드})에 대해 알려줘” 자동 입력 또는 전송.  
    - **옵션 B**: 위젯이 있으면 위젯 열고 동일한 컨텍스트로 메시지 전송.  
  - 백엔드 `POST /api/go100/ai/chat`에 **context** 필드 추가 예:  
    `context: { "type": "stock_info", "stock_code": "001510", "stock_name": "SK증권" }`  
  - 이 경우 의도 라우팅에서 `context.type === "stock_info"` 또는 메시지에 종목 코드/이름이 있으면 **stock_info** 플로우로 분기.

### 4.3 Genspark 스타일 “단계 노출” (선택)

- 답변 구조 예:  
  - **1차 — 우리 사이트 데이터**  
    - “종목명(001510), 시장, 시총, PER 등 (우리 DB 기준)”  
    - “우리 플랫폼에서의 최근 거래: N건” (있을 경우)  
  - **2차 — 증권사 API 검색**  
    - “한국투자증권 API로 확인한 당일/전일 종가, 업종, 거래정지/관리종목 여부”  
  - **요약**  
    - 위를 바탕으로 한 1~2문장 요약.

---

## 5. 구현 시 확인·설계 포인트

### 5.1 백엔드

| 항목 | 내용 |
|------|------|
| **의도 분기** | `intent_router`에 `stock_info` 추가: 메시지에 종목코드(6자리) 또는 종목명 패턴 + “알려줘/정보/뭐야” 등, 또는 `body.context.type === "stock_info"` 시 `stock_info` 반환. |
| **1차 데이터 API** | `stock_universe` 조회(종목코드/이름), 필요 시 `ohlcv_daily` 최근 N일, `v4_trade_executions` 해당 종목 집계 — 전용 서비스 함수 또는 내부 API로 구현. |
| **2차 KIS 호출** | `kis_api_registry`에 이미 `search_stock_info`(CTPF1002R) 정의됨. KIS 클라이언트에 `GET .../search-stock-info?PRDT_TYPE_CD=300&PDNO={종목코드}` 호출 래퍼 추가. **모의 미지원**이므로 실전 앱키/토큰 사용. |
| **플로우** | `run_stock_info_flow(stock_code, stock_name, user_id?, db)` 형태로 1차 조회 → 2차 KIS(필요 시) → LLM 또는 템플릿으로 문장/블록 생성 → `OrchestrationResult` 반환. |
| **채팅 body** | `POST /api/go100/ai/chat`에 `context: { type?: "stock_info", stock_code?: string, stock_name?: string }` 수용. |

### 5.2 프론트엔드

| 항목 | 내용 |
|------|------|
| **거래내역 종목 셀** | `TradeHistoryPanel`에서 종목 컬럼을 버튼/링크로 변경, 클릭 시 `/llm?stock_code=001510&stock_name=SK증권` 이동 또는 채팅에 해당 문구 + context 전달. |
| **전체화면 채팅** | `/llm` 페이지 로드 시 `stock_code`, `stock_name` 쿼리 있으면 입력창에 “{종목명}({코드})에 대해 알려줘” 설정 또는 자동 전송, 전송 시 `context`에 종목 정보 포함. |
| **표시** | Genspark 스타일 적용 시, 응답 메시지에 “1차 — 우리 사이트 데이터”, “2차 — 증권사 API” 블록이 들어가도록 백엔드에서 마크다운/블록 형태로 내려주고, 프론트는 그대로 렌더링. |

### 5.3 제약·리스크

- **CTPF1002R**: 모의투자 미지원 → 실전 환경에서만 동작. 모의만 쓰는 환경에서는 “2차 증권사 API” 블록은 생략하거나 “실전 연동 시 제공”으로 문구 처리.
- **종목 코드 추출**: 사용자 문장에서 종목코드(6자리) 또는 종목명만 입력한 경우, `stock_universe` 또는 KIS CTPF1604R(검색)으로 코드 확정 필요.
- **속도/캐시**: CTPF1002R 호출은 필요 시에만 하고, 단기 캐시(1~5분) 고려 시 유리.

---

## 6. 권장 단계별 진행

| 단계 | 내용 |
|------|------|
| **1** | 의도 `stock_info` 추가 + `run_stock_info_flow` 골격(1차 DB만 조회, 고정 문장 답변). |
| **2** | 1차 데이터 풍부화(종목 요약 + 선택적 사용자 거래 요약). |
| **3** | KIS CTPF1002R 래퍼 추가 및 2차 호출 연동(실전 앱키 준비 시). |
| **4** | 거래내역 종목 클릭 → `/llm` + 쿼리/context 연동. |
| **5** | (선택) Genspark 스타일 “1차/2차” 블록 표시 및 마크다운 포맷 정리. |

---

## 7. 참고 경로

- 채팅: `backend/app/routers/go100/ai_router.py` — `POST /api/go100/ai/chat`
- 의도 분기: `backend/app/services/go100/ai/intent_router.py`
- 도움 흐름 참고: `backend/app/services/go100/ai/help_flow.py`, `help_knowledge.py`
- KIS 레지스트리: `backend/app/core/kis_api_registry.py` — `search_stock_info`, `search_info`
- KIS 주식기본조회 스펙: `docs/kis-api-portal/excel-full/converted/국내주식_종목정보/주식기본조회.md`
- 우리 종목/시세 캐시: `backend/app/services/go100/universe/data_cache.py` — `StockInfo`, `get_ohlcv`
- 거래내역 UI: `frontend/src/components/trade/TradeHistoryPanel.tsx` — 종목 컬럼
- 대시보드 거래: `backend/app/api/v1/dashboard_router.py` — `v4_trade_executions` 조회

---

*이 보고서는 “Genspark처럼 답할 수 있는지” 및 “종목 클릭 → 1차 사이트 데이터, 2차 증권사 API” 제공 가능 여부를 확인하고, 구현 방향을 정리한 기획 문서입니다. 실제 구현 시 위 단계별 계획과 제약을 반영해 진행하면 됩니다.*
