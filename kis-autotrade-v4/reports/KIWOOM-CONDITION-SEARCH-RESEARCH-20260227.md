# 키움증권 조건검색(Condition Search) REST API 리서치 보고서

- 작성일: 2026-02-27
- 작성자: Claude Opus 4.6
- 목적: 키움 REST API 조건검색 기능 조사, 기본 제공 조건식 여부, API 사용법 정리

---

## 1. 핵심 요약

| 항목 | 결론 |
|------|------|
| 기본/시스템 조건식 제공 여부 | **HTS 영웅문4에서만 82개 기본 조건식 제공 (캐치 KATCH 서비스)** — API에서 직접 사용 불가 |
| REST API 조건식 목록 조회 | **ka10171** (WebSocket 기반) — 사용자가 영웅문4에서 저장한 조건식만 조회 가능 |
| API에서 조건식 생성/편집 | **불가** — 반드시 영웅문4 HTS에서 작성 후 서버 저장 필요 |
| API 종류 | **키움 REST API**: ka10171~ka10174 (WebSocket), **KIS API**: psearch-title/psearch-result (HTTP REST) |

---

## 2. 키움증권 조건검색 시스템 개요

### 2.1 조건검색이란?
지정된 각종 조건(기술적분석, 패턴분석, 재무분석, 순위분석, 시세분석 등)에 일치하는 종목을 실시간으로 검색하는 기능. 하나의 조건식에 최대 20개의 조건을 조합 가능. AND, OR, NOT 논리 연산자와 괄호를 사용하여 복잡한 조건 구성 가능.

### 2.2 조건식 저장 위치
- 조건검색식은 **개인 PC에 저장되지 않고 키움증권 서버에만 저장**됨
- API에서 조건검색을 사용하려면 반드시 HTS에서 조건식을 먼저 작성하고 서버에 저장해야 함

---

## 3. 기본 제공 조건식 vs 사용자 조건식

### 3.1 기본 제공 조건식 (HTS에서만)

키움증권은 영웅문4 HTS 내에서 기본 제공 조건식을 제공한다:

#### (A) 조건검색 화면 [0150]
- HTS 조건검색 화면을 열면 **기본 제공되는 검색조건**들이 표시됨
- 예시: '저평가된 성장주', '꾸준히 배당을 주는 종목', '돈 잘 버는 회사' 등
- 사용자가 이를 수정/조합하여 맞춤형 검색식 생성 가능

#### (B) 캐치(KATCH) 서비스 [4000]
- **당사(키움증권)가 선정한 82개의 초단위 조건검색식** 제공
- 3개 탭 구성:
  - **간편작성**: 82개 사전 설정 초단위 조건검색식
  - **일반작성**: [0150] 조건검색 화면의 모든 조건검색식
  - **내조건식**: 사용자가 저장한 개인 조건검색식 목록

### 3.2 사용자 조건식 (API에서 사용 가능)
- **OpenAPI에서 사용할 수 있는 조건식은 오직 사용자가 영웅문 HTS에서 직접 만들고 서버에 저장한 조건식뿐**
- 기본 제공 조건식(82개 등)은 API 목록 조회(ka10171)에서 나타나지 않음
- API에서는 조건검색 수식작성이나 수식편집을 **지원하지 않음**

### 3.3 결론
```
기본 조건식 (82개 등) → HTS/캐치 서비스 전용, API 사용 불가
사용자 조건식          → HTS에서 생성 → 서버 저장 → API로 목록 조회 및 실행 가능
```

> **중요**: API로 조건검색을 사용하려면 반드시 영웅문4 HTS를 설치한 PC에서 조건식을 생성하고 저장해야 한다. 원격 서버(Linux)에서는 HTS 실행이 불가하므로, Windows PC에서 HTS를 실행하여 조건식을 만들어야 한다.

---

## 4. 키움 REST API — 조건검색 관련 API (WebSocket 기반)

키움 REST API의 조건검색은 **WebSocket 프로토콜**을 사용한다 (일반 HTTP REST가 아님).

### 4.1 API 목록

| API ID | 이름 | trnm 코드 | 용도 |
|--------|------|-----------|------|
| **ka10171** | 조건검색 목록조회 | CNSRLST | 서버 저장된 조건식 목록 조회 |
| **ka10172** | 조건검색 요청 일반 | CNSRREQ | 일반 조건검색 실행 (1회성) |
| **ka10173** | 조건검색 요청 실시간 | CNSRREQ (search_type=1) | 실시간 조건검색 등록 |
| **ka10174** | 조건검색 실시간 해제 | CNSRCLR | 실시간 조건검색 해제 |

### 4.2 WebSocket 접속 정보

| 구분 | URL |
|------|-----|
| 운영 도메인 | `wss://api.kiwoom.com:10000` |
| 모의투자 도메인 | `wss://mockapi.kiwoom.com:10000` (KRX만 지원) |
| URL Path | `/api/dostk/websocket` |
| Format | JSON |

### 4.3 ka10171 — 조건검색 목록조회

**요청 (Request):**
```json
{
  "trnm": "CNSRLST"
}
```
- `trnm`: 고정값 "CNSRLST" (필수, 문자열, 길이 7)

**응답 (Response):**
```json
{
  "return_code": 0,
  "return_msg": "정상",
  "trnm": "CNSRLST",
  "data": [
    {"seq": "0", "name": "조건식이름1"},
    {"seq": "1", "name": "조건식이름2"},
    {"seq": "4", "name": "급등주 포착"}
  ]
}
```
- `return_code`: 결과코드 (정상: 0)
- `return_msg`: 결과메시지
- `data`: 조건검색식 목록 (리스트)
  - `seq`: 조건검색식 일련번호
  - `name`: 조건검색식 명

> **주의**: ka10171을 먼저 호출한 후에야 ka10172/ka10173 호출이 가능하다.

### 4.4 ka10172 — 조건검색 요청 일반

**요청 (Request):**
```json
{
  "trnm": "CNSRREQ",
  "seq": "4",
  "search_type": "0",
  "stex_tp": "K",
  "cont_yn": "N",
  "next_key": ""
}
```

| 파라미터 | 설명 | 비고 |
|----------|------|------|
| trnm | TR명 | "CNSRREQ" 고정값 |
| seq | 조건검색식 일련번호 | ka10171에서 받은 seq 값 |
| search_type | 검색유형 | "0": 조건검색, "1": 조건검색+실시간 |
| stex_tp | 거래소 | "K": KRX |
| cont_yn | 연속조회 여부 | "N": 단순조회, "Y": 연속조회 |
| next_key | 연속조회 키 | cont_yn이 "Y"인 경우 필수 |

### 4.5 ka10174 — 조건검색 실시간 해제

**요청 (Request):**
```json
{
  "trnm": "CNSRCLR",
  "seq": "4"
}
```

### 4.6 제한사항

| 제한 항목 | 내용 |
|-----------|------|
| 조건검색 조회 빈도 | 시세조회 + 관심종목조회 합산 **1초 5회** |
| 조건별 조회 제한 | **1분 1회** |
| 실시간 조건검색 최대 수 | **10개 조건식** |
| 실시간 결과 종목 수 제한 | 100종목 초과 시 실시간 조건검색 불가 |
| 실시간 포착 속도 | 1초에 1종목 |

---

## 5. 참고: KIS(한국투자증권) API — 조건검색

현재 프로젝트(`kis-autotrade-v4`)에서 사용하는 **한국투자증권(KIS) API**에도 조건검색 관련 API가 존재한다:

### 5.1 KIS API 조건검색 엔드포인트

| API 키 | 이름 | URL | TR ID | Method |
|---------|------|-----|-------|--------|
| condition_search_list | 조건식목록조회 | `/uapi/domestic-stock/v1/quotations/psearch-title` | HHKST03900300 | GET |
| condition_search_result | 조건검색결과조회 | `/uapi/domestic-stock/v1/quotations/psearch-result` | HHKST03900400 | GET |

### 5.2 KIS API 조건검색 특징
- **HTTP REST** 방식 (키움과 달리 WebSocket 불필요)
- psearch-title에서 받은 `seq` 값을 psearch-result의 입력으로 사용
- **HTS(eFriend Plus) [0110] 조건검색 화면**에서 사용자가 조건식을 만들고 "사용자조건 서버저장"을 해야 API에서 사용 가능
- 조건검색 결과는 시스템 안정성을 위해 **조건당 100종목**으로 제한
- "조회가 계속 됩니다" 오류 발생 시: HTS [0110]에서 조건식 등록 후 "사용자조건 서버저장" 클릭 필요
- 이미 `kis_api_registry.py`에 등록되어 있음 (ANALYSIS_APIS 섹션)

### 5.3 KIS vs 키움 조건검색 비교

| 항목 | KIS (한국투자증권) | 키움증권 |
|------|-------------------|---------|
| 프로토콜 | HTTP REST (GET) | WebSocket |
| HTS 필요 | eFriend Plus [0110] | 영웅문4 [0150] |
| API ID | psearch-title / psearch-result | ka10171~ka10174 |
| 결과 제한 | 100종목/조건 | 100종목(실시간) |
| 기본 조건식 API 사용 | 불가 (사용자 조건식만) | 불가 (사용자 조건식만) |
| 실시간 지원 | 미지원 (폴링 필요) | WebSocket 실시간 지원 |

---

## 6. 현재 프로젝트 내 조건검색 구현 상태

### 6.1 기존 코드
- 파일: `backend/app/services/data/condition_search_collector.py`
- API ID: `ka10050` (존재하지 않는 API ID — 수정 필요)
- 경로: `/api/dostk/condition-search` (비표준 경로)
- 현재 상태: **graceful skip** (조건검색이 미지원이거나 실패 시 조용히 건너뜀)
- 조건식 목록: DB(v4_condition_search)에서 기존 데이터 조회 또는 config 파일에서 로드
- 문제점: **조건식 목록을 ka10171로 먼저 조회하는 로직이 없음**

### 6.2 KIS API 레지스트리
- 파일: `backend/app/core/kis_api_registry.py` (라인 772~786)
- `condition_search_list` / `condition_search_result` — 이미 등록되어 있으나 실제 호출 코드 없음

---

## 7. 실용적 권고사항

### 7.1 조건검색 사용을 위한 필수 사전 작업
1. **Windows PC**에 영웅문4 HTS 또는 eFriend Plus 설치
2. HTS에서 원하는 조건식 작성 (기술적분석, 재무분석 등 조합)
3. 작성한 조건식을 **서버에 저장** (필수!)
4. 이후 API로 조건식 목록 조회(ka10171) 및 검색 실행(ka10172) 가능

### 7.2 API 없이 기본 조건식을 활용하는 대안
기본 제공 82개 조건식을 API로 직접 사용할 수 없으므로, 대안적 접근:

1. **HTS에서 기본 조건식을 복사하여 사용자 조건식으로 저장**
   - 영웅문4 [0150] 조건검색 → 기본 제공 조건식 선택 → "내조건식"으로 복사/저장
   - 저장된 조건식은 API로 사용 가능

2. **직접 동등한 조건을 코드로 구현**
   - 기본 조건식의 조건(예: PER < 10, ROE > 15% 등)을 파악하여
   - SQL 쿼리 또는 Python 로직으로 구현
   - 이미 보유한 데이터(ohlcv_daily, stock_fundamentals 등) 활용

3. **KIS API psearch 활용 (추천)**
   - 현재 프로젝트에서 이미 KIS 계정을 사용 중이므로
   - eFriend Plus HTS에서 조건식 작성 → 서버 저장
   - psearch-title / psearch-result API로 조건검색 실행
   - HTTP REST 방식이므로 WebSocket 구현 없이 사용 가능

### 7.3 키움 REST API 조건검색 구현 시 주의점
- **WebSocket 연결 필요** — 일반 HTTP REST와 다름
- ka10171을 **반드시 먼저 호출**해야 ka10172/ka10173 사용 가능
- 비동기 처리 필수 (결과 수신 시점 예측 불가)
- 현재 `condition_search_collector.py`의 `ka10050` API ID는 잘못되어 있으며, 올바른 API는 ka10171~ka10174

---

## 8. 참고 소스

- [키움 REST API 공식 포털](https://openapi.kiwoom.com/)
- [키움 REST API 가이드 — 조건검색 API](https://openapi.kiwoom.com/m/guide/apiguide?jobTpCode=15)
- [키움 조건검색 및 실시간 기능개선 안내](https://openapi.kiwoom.com/m/board/Board0101View?seqid=7)
- [키움 영웅문4 조건검색 도움말 [0150]](https://download.kiwoom.com/hero4_help_new/0150.htm)
- [키움 캐치(KATCH) 시작하기 [4000]](https://download.kiwoom.com/hero4_help_new/4000.htm)
- [퀀트투자를 위한 키움증권 API — 조건검색 일반조회](https://wikidocs.net/79241)
- [퀀트투자를 위한 키움증권 API — 실시간 조건식](https://wikidocs.net/158232)
- [조건검색식 만들기 (WikiDocs)](https://wikidocs.net/7649)
- [키움증권 REST API 실시간시세조회 및 조건검색 (PHP 예시)](https://www.pabburi.co.kr/content/php/%ED%82%A4%EC%9B%80%EC%A6%9D%EA%B6%8C-rest-api-%EC%8B%A4%EC%8B%9C%EA%B0%84%EC%8B%9C%EC%84%B8%EC%A1%B0%ED%9A%8C-%EB%B0%8F-%EC%A1%B0%EA%B1%B4%EA%B2%80%EC%83%89/)
- [kiwoomRest PyPI 패키지](https://pypi.org/project/kiwoomRest/)
- [KIS Developers 한국투자증권 오픈API](https://apiportal.koreainvestment.com/apiservice)
- [GitHub: coreanq/kw_condition](https://github.com/coreanq/kw_condition)
- [GitHub: me2nuk/stockOpenAPI](https://github.com/me2nuk/stockOpenAPI)
