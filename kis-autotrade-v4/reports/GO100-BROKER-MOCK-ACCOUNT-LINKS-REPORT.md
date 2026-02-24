# 모의계좌 개설 링크 반영 보고서

**작성일**: 2026-02-24  
**대상**: 계좌 추가 모달(`AddAccountModal`) — STEP 1·2·3 바로가기 영역

---

## 1. 반영 주소

| 증권사 | 버튼 문구 | 연결 URL |
|--------|-----------|----------|
| **한투** | 한투 모의계좌 개설 | https://securities.koreainvestment.com/main/research/virtual/_static/TF07da010000.jsp |
| **키움** | 키움 모의계좌 개설 | https://www.kiwoom.com/h/customer/acctopen/VAcctOpenInfoView?dummyVal=0 |

---

## 2. 반영 위치

- **파일**: `frontend/src/components/accounts/AddAccountModal.tsx`
- **상수**: `BROKER_LINKS` — `mockAccountUrl`, `mockAccountLabel` 사용
- **노출**: 새 계좌 등록 모달 STEP 1(브로커 선택), STEP 2(계좌 정보), STEP 3(API 연동) 하단 **바로가기** 블록에서, **모의 계좌** 선택 시 첫 번째 버튼으로 노출

---

## 3. 적용 내용

- 한투: `mockAccountUrl` → 위 한투 URL, `mockAccountLabel` → **한투 모의계좌 개설**
- 키움: `mockAccountUrl` → 위 키움 URL, `mockAccountLabel` → **키움 모의계좌 개설**
- API 발급 링크(KIS 개발자센터 / 키움 Open API)는 기존 유지

반영 후 **프론트엔드 재빌드**가 필요합니다. (`npm run build` 또는 배포 파이프라인 실행)
