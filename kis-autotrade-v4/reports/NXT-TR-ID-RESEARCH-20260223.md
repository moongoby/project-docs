# NXT-TR-ID-RESEARCH 보고서

| 항목 | 내용 |
|------|------|
| 작업 ID | NXT-TR-ID-RESEARCH |
| 일시 | 2026-02-23 KST |
| 서버 | root@[SERVER-IP] |
| 목적 | KIS API 문서에서 NXT/시간외 주문 TR_ID 및 파라미터 확인 |

## 분석 결과

### 1. 주문_계좌.xlsx NXT/시간외 TR_ID

- **현금/신용/정정취소 주문**: NXT 전용 별도 TR_ID 없음. **동일 TR_ID** 사용 (매수 TTTC0012U/VTTC0012U, 매도 TTTC0011U/VTTC0011U, 정정취소 TTTC0013U/VTTC0013U).
- **거래소 구분 파라미터**: `EXCG_ID_DVSN_CD` (거래소ID구분코드)
  - 한국거래소: **KRX**
  - 대체거래소(넥스트레이드): **NXT**
  - SOR (Smart Order Routing): **SOR**
- **퇴직연금 미체결내역** (v1_국내주식-033):
  - KRX만: **TTTC2201R**
  - KRX + NXT/SOR: **TTTC2210R**
- **일별주문체결조회** (v1_국내주식-005): 요청 파라미터에 `EXCG_ID_DVSN_CD` (KRX/NXT/SOR) 있음.
- **주문구분(ORD_DVSN/ORD_DVSN_CD)**: 장전 시간외, 장후 시간외, 시장가 시 단가 "0" 입력 권고 등 문서화됨.
- **시간외단일가**: `AFHR_FLPR_YN` (시간외단일가여부) N/Y.

### 2. NXT 주문에 필요한 파라미터

| 구분 | 파라미터/헤더 | 값 (NXT) | 비고 |
|------|----------------|----------|------|
| 거래소 | EXCG_ID_DVSN_CD | NXT | 주문(현금/신용/정정취소), 일별체결조회 등 Request Body |
| 시장 분류(시세) | FID_COND_MRKT_DIV_CODE | NX | 기본시세 등 Query (J:KRX, NX:NXT, UN:통합) |
| 응답 거래소코드 | excg_dvsn_cd | 응답 필드 | 2자리 |

TR_ID는 **기존 국내주식 주문과 동일** (TTTC0012U/0011U/0013U 등). NXT 구분은 **EXCG_ID_DVSN_CD** 로만 처리.

### 3. 기본시세.xlsx NXT/시간외

- **FID_COND_MRKT_DIV_CODE**: J=KRX, NX=NXT, UN=통합 (여러 시세 API 공통).
- 시간외 시세 전용 TR_ID 예: FHPST02320000(시간외일자별주가), FHPST02310000(시간외시간별체결), FHPST02300000(시간외현재가), FHPST02300400(시간외호가).

### 4. 현재 코드 현황

- **kis_order_service.py / v4_order_executor.py**: TR_IDS는 KRX 기준 동일 (TTTC0012U, TTTC0011U, TTTC0013U, TTTC8434R, TTTC8908R, TTTC8001R 등). **EXCG_ID_DVSN_CD 또는 exchange 파라미터 미사용** (execution 디렉터리 grep 결과 없음).
- **broker_kiwoom_client.py**: EXCHANGE_MAP에 `"NXT": ("NXT", "_NX")` 정의. trde_tp에 장마감후시간외(81), 장시작전시간외(61), 시간외단일가(62) 등 주석 존재.
- **broker_base.py**: `exchange: str = "KRX"` (KRX | NXT | SOR).
- **kis_api_registry.py**: NXT 실시간(체결가/호가/시간외체결가/시간외호가/VI/체결통보) 6종, 시간외 관련 시세 다수 등록.
- **account_sync_manager.py**: NXT 시장·시간외 동기화 가능 시간(07:55~20:05 KST) 주석.

### 5. 권장 수정 사항

- **v4_order_executor / kis_order_service**: TR_ID 추가 불필요. 주문 API 호출 시 **Request Body에 `EXCG_ID_DVSN_CD`(또는 문서상 파라미터명)를 NXT/SOR일 때만 "NXT"/"SOR"로 설정**하도록 분기 추가 검토.
- **kis_api_registry**: NXT 주문용 별도 TR_ID 없음 — 기존 주문 TR_ID + EXCG_ID_DVSN_CD 조합으로 충분. 실시간/시세는 이미 NXT 항목 등록됨.
- **exchange_cd 파라미터 추가 위치**: 주문(현금) POST body (`order-cash`), 정정취소 body, 일별체결조회 요청 파라미터. 문서 기준 필드명은 `EXCG_ID_DVSN_CD`.

## 체크리스트
- [ ] 코드 레포 커밋 완료 (본 작업은 읽기+보고서만 수행)
- [x] project-docs 보고서 push 완료
