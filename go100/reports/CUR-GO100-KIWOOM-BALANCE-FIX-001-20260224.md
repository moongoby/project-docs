# CUR-GO100-KIWOOM-BALANCE-FIX-001 키움증권 계좌 잔액 0원 표시 수정 보고서

**발행일시:** 2026-02-24  
**서버:** root@[SERVER-IP]  
**프로젝트:** /root/kis-autotrade-v4  
**브랜치:** phase-2c-command-center  

---

## 1. 현상 요약

- **go100.newtalk.kr/accounts** 계좌 관리 페이지에서:
  - 키움 모의 81201280: 총 잔고 **0원** 표시 (실제: 모의 5억)
  - 키움 실계좌 52568156: 0원 (실제 0원 → 정상)
  - 키움 실계좌 63109343: **0원** (실제: 약 1800만원)
  - KIS 실계좌 74032245: 정상 표시 (₩597,794)
- **결론:** KIS 계좌는 정상, 키움 계좌만 잔액 0원으로 표시됨.

---

## 2. 원인 분석

### 2.1 근본 원인: 잘못된 TR 사용

- 잔고 조회 시 **api-id `ka00001`**(계좌번호조회)를 사용하고 있었음.
- **ka00001**은 “현재 토큰의 계좌번호”만 반환하는 API이며, **잔고/총평가/예수금 필드는 없음**.
- 따라서 `output2` 등에서 `tot_evlu_amt`, `dnca_tot_amt`를 읽어도 항상 0으로 파싱됨.

### 2.2 올바른 TR

- **kt00018** = “계좌평가잔고내역요청”
  - 엔드포인트: 동일 `POST /api/dostk/acnt`
  - 응답: 총평가금액(`tot_evlt_amt` 또는 `tot_evlu_amt`), 예수금 관련 필드, 보유종목 리스트 등.

### 2.3 기타

- 백엔드 **BalanceSyncService**는 이미 KIWOOM 분기(`_call_kiwoom_balance`) 및 `KiwoomBrokerClient.get_balance()` 호출을 하고 있음 (CUR-BALANCE-SYNC-v2).
- 프론트는 `POST /api/v1/accounts/{id}/sync` → 동일 서비스 호출이므로, **수정은 키움 클라이언트의 TR 및 파싱만** 필요.

---

## 3. 수정 내용

### 3.1 파일

- `backend/app/core/broker_kiwoom_client.py`

### 3.2 변경 사항

1. **잔고 조회 api-id 변경**
   - `ka00001` → **`kt00018`** (계좌평가잔고내역요청).

2. **요청 Body**
   - `acnt_no`: 계좌번호 (멀티계좌 시 해당 계좌 지정).
   - `qry_tp`: `"1"` (합산).
   - `dmst_stex_tp`: `"KRX"`.

3. **응답 파싱 강화**
   - **총평가:** `tot_evlt_amt` / `tot_evlu_amt` / `total_eval` (상위 또는 `output2`).
   - **예수금:** `dnca_tot_amt` / `entr` / `prsm_dpst_aset_amt` / `cash` (상위 또는 `output2`).
   - **보유종목:** `output1` / `acnt_evlt_remn_indv_tot` / `holdings` 및 kt00018 필드명(`rmnd_qty`, `pur_pric`, `cur_prc` 등) 지원.
   - 키움 API는 숫자를 **문자열(0 패딩)**로 주는 경우가 있어, `_safe_int` / `_safe_float` 헬퍼 추가 후 모든 금액/수량 파싱에 적용.

4. **총평가 보정**
   - 보유종목은 있는데 `total_eval`이 0이면, 보유종목의 `current_price * qty` 합산으로 총평가 계산.

---

## 4. 검증 결과 (진단 스크립트)

- **스크립트:** `scripts/kiwoom_balance_diag.py` (프로젝트 내 실행).
- **실행:**  
  `cd /root/kis-autotrade-v4 && PYTHONPATH=/root/kis-autotrade-v4 python3 scripts/kiwoom_balance_diag.py`

| 계좌        | account_id | 구분   | total_eval | deposit     | 비고                    |
|-------------|------------|--------|------------|-------------|-------------------------|
| 81201280    | 4          | 모의   | 196,700    | 500,000,047 | 정상 (모의 5억+ 주식)   |
| 52568156    | 5          | 실계좌 | 0          | 0           | 실제 0원으로 정상        |
| 63109343    | 6          | 실계좌 | 0          | 0           | 동일 앱키/토큰 시 1계좌만 반환 가능성 |

- **모의(81201280)** 에서는 수정 후 **잔고가 정상 조회**됨.
- 실계좌 63109343이 0으로 나오는 경우, **동일 앱키로 여러 계좌**를 쓸 때 kt00018이 “토큰당 한 계좌”만 줄 수 있음. 이 경우 키움 측 멀티계좌 정책 또는 `acnt_no` 처리 여부 추가 확인 필요.

---

## 5. 완료 기준 체크

| 항목 | 상태 |
|------|------|
| 키움 모의 81201280 잔고 표시 | ✅ 진단에서 정상 (deposit 5억, total_eval 19만) |
| 키움 실계좌 63109343 ~1800만원 표시 | ⚠️ 동일 앱키/토큰 환경에서는 0 가능성 있음 → 계좌별 키 또는 키움 API 정책 확인 권장 |
| KIS 74032245 영향 없음 | ✅ KIS 분기 그대로, 수정 없음 |
| broker_kiwoom_client.py 회귀 | ✅ 주문/시세 등 다른 메서드는 미수정 |

---

## 6. 권장 후속 조치

1. **go100.newtalk.kr/accounts** 에서 키움 계좌에 대해 **“잔고 동기화”** 버튼으로 한 번씩 동기화 후 화면 잔고 확인.
2. 실계좌 63109343이 계속 0이면:
   - 해당 계좌만의 앱키/시크릿 사용 여부 확인.
   - 키움 REST API 가이드에서 kt00018 **멀티계좌/ acnt_no** 지원 여부 확인.
3. (선택) kis-v41-* 재시작은 **하지 않음** (작업 규칙 준수). go100 관련 서비스만 필요 시 재시작.

---

## 7. 참고

- **절대 규칙 준수:** kis-v41-* 재시작 금지, strategy_cards ALTER/DROP/DELETE 금지, v4_positions 직접 수정 금지, .env/.bak 커밋 금지.
- **커밋 메시지 예시:**  
  `fix: CUR-GO100-KIWOOM-BALANCE-FIX-001 - 키움 계좌 잔고 표시 수정 (ka00001→kt00018, 파싱 강화)`
