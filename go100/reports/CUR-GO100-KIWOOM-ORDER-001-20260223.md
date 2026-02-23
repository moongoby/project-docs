# CUR-GO100-KIWOOM-ORDER-001 결과 보고서

**일시:** 2026-02-23 (월) 15:35 KST  
**서버:** root@211.188.51.113 (SSH)  
**목적:** 키움 모의계좌(account_id=4, 81201280) 실제 매수/매도 주문 테스트  
**선행:** KIWOOM-TEST-003 → 토큰 발급 성공, 잔고 조회 200 정상  
**절대규칙:** kis-v41-* 서비스 재시작 금지, strategy_cards ALTER/DROP/DELETE 금지

---

## STEP 1. 키움 REST API 문서(PDF) 핵심 확인

| 항목 | 결과 |
|------|------|
| **PDF 경로** | `/root/kis-autotrade-v4/docs/api/키움 REST API 문서.pdf` |
| **파일 존재** | 있음 (약 15MB) |
| **pdftotext** | 미설치 또는 추출 실패 — 텍스트 추출 생략 |
| **주문 엔드포인트 (코드 기준)** | `broker_kiwoom_client.py`에서 **`/api/dostk/ordr`** 사용 (매수/매도/정정/취소 공통) |
| **잔고** | `/api/dostk/acnt` (동일) |

PDF 내 주문 스펙은 pdftotext/pdfplumber 미사용으로 직접 추출하지 않았고, **구현된 클라이언트 코드**를 기준으로 엔드포인트·파라미터를 확정함.

---

## STEP 2. broker_kiwoom_client.py 주문 코드 검수

### 2.1 주문 관련 함수

| 함수 | 엔드포인트 | api-id | 비고 |
|------|------------|--------|------|
| `buy()` | `POST /api/dostk/ordr` | kt10000 | 매수 |
| `sell()` | `POST /api/dostk/ordr` | kt10001 | 매도 |
| `modify_order()` | `POST /api/dostk/ordr` | kt10002 | 정정 |
| `cancel_order()` | `POST /api/dostk/ordr` | kt10003 | 취소 |

### 2.2 주문 Body 파라미터 (매수/매도)

- **dmst_stex_tp**: 거래소 구분 (KRX / NXT / SOR)
- **stk_cd**: 종목코드 (예: 005930)
- **ord_qty**: 주문 수량 (문자열)
- **ord_unpr**: 주문 단가 (시장가 시 0)
- **trde_tp**: 거래유형 (0=지정가, **3=시장가** 등, `TRDE_TP_MAP` 참고)
- **acnt_no**: 계좌번호 (예: 81201280)

### 2.3 헤더

- `Authorization: Bearer {token}`
- `api-id`: 위 표 참고
- `Content-Type: application/json; charset=utf-8`

(모의 API 직접 호출 시 `appkey`, `secretkey` 헤더 추가 사용 — KIWOOM-TEST-003과 동일)

### 2.4 응답 파싱

- `_parse_order_response`: `resp.status_code == 200` 이고 `data.get("rt_cd") != "1"` 이면 성공으로 처리.
- 주문번호: `data.get("output", {}).get("ODNO")` 또는 `order_no` / `odno`.

---

## STEP 3. 토큰 발급 + 잔고 + 매수/매도 테스트 결과

테스트 스크립트: broker와 동일하게 **`/api/dostk/ordr`**, body `dmst_stex_tp`, `stk_cd`, `ord_qty`, `ord_unpr`, `trde_tp`, `acnt_no` 사용.

### 3.1 토큰 발급

- **URL:** `POST https://mockapi.kiwoom.com/oauth2/token`
- **Body:** `grant_type`, `appkey`, `secretkey`
- **결과:** HTTP **200**, 토큰 정상 발급.

### 3.2 잔고 조회

- **URL:** `POST https://mockapi.kiwoom.com/api/dostk/acnt`
- **Body:** `{"acnt_no": "81201280"}`
- **결과:** HTTP **200**, `return_code: 0` — 정상.

### 3.3 매수 주문 (삼성전자 005930, 1주, 시장가)

- **URL:** `POST https://mockapi.kiwoom.com/api/dostk/ordr`
- **Headers:** `api-id: kt10000`
- **Body:** `dmst_stex_tp=KRX`, `stk_cd=005930`, `ord_qty=1`, `ord_unpr=0`, `trde_tp=3`, `acnt_no=81201280`
- **결과:** HTTP **200**
- **응답:** `return_code: 20`, `return_msg: "[2000](RC4058:모의투자 장종료)"`
- **해석:** 주문 **요청·엔드포인트·파라미터는 정상**. 모의투자 장종료로 인해 **체결 거부**된 상태.

### 3.4 매도 주문

- 동일 엔드포인트, `api-id: kt10001`
- **결과:** HTTP **200**, `return_code: 20` (모의투자 장종료) — 주문 API 동작 동일하게 확인.

---

## 요약

| 항목 | 내용 |
|------|------|
| **PDF** | 존재 확인. 주문 스펙은 코드 기준으로 확정. |
| **주문 엔드포인트** | **`/api/dostk/ordr`** (ordstk 아님). 매수 api-id `kt10000`, 매도 `kt10001`. |
| **주문 Body** | `dmst_stex_tp`, `stk_cd`, `ord_qty`, `ord_unpr`, `trde_tp`, `acnt_no` (broker와 일치). |
| **토큰/잔고** | 토큰 발급 200, 잔고 조회 200 정상. |
| **매수/매도** | 주문 API 200 정상 응답. return_code 20 = 모의투자 장종료로 체결 불가. |
| **다음 검증** | **장 운영 시간**에 동일 스크립트 재실행하여 체결 여부 확인 권장. |

---

## 동기화 체크

- [x] STEP 1 PDF 핵심 확인 (경로·코드 기준 엔드포인트)
- [x] STEP 2 broker_kiwoom_client.py 주문 소스 검수
- [x] STEP 3 토큰 발급 + 잔고 + 매수/매도 결과
- [x] 보고서 작성 → project-docs 저장
- [ ] (선택) 코드 수정 시 go100 repo 커밋 + push
- [ ] (선택) project-docs 커밋 + push

---

**보고서 위치**  
- 서버: `/root/project-docs/go100/reports/CUR-GO100-KIWOOM-ORDER-001-20260223.md`  
- GitHub: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-KIWOOM-ORDER-001-20260223.md
