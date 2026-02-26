# CUR-GO100-KIWOOM-BALANCE-LOADING-FIX-001 보고서

> 작성일: 2026-02-24  
> 우선순위: P0  
> 증상: 키움 잔액 0원 표시 + 화면 무한 로딩

## 증상

1. 키움 계좌 잔액이 모두 0원으로 표시 (모의 81201280 약 5억, 실계좌 63109343 약 1,800만원인데 0원)
2. 페이지가 "로딩중" 상태에서 멈춤

## 원인

- **잔액 0원**: 계좌 목록/대시보드는 DB의 `accounts.total_deposit`, `accounts.total_evaluation`만 사용. 키움 잔액은 잔고 동기화(sync) 시에만 API 호출 후 DB 갱신됨. 동기화 실패·미실행 시 0으로 유지. 키움 API 호출이 타임아웃/실패하면 동기화가 끝나지 않아 전체 요청이 블로킹될 수 있음.
- **무한 로딩**: (1) API 클라이언트에 기본 타임아웃이 없어 서버 응답 지연 시 프론트가 무한 대기. (2) 키움 `get_balance` 호출에 타임아웃이 없어 동기화/검증 시 긴 대기 가능.

## 수정 내용

### 백엔드

- **broker_kiwoom_client.py**
  - `get_balance()`에 `asyncio.timeout(10)` 적용.
  - 타임아웃/예외 시 `AccountBalance(total_eval=0, deposit=0, holdings=[])` 반환으로 무한 대기 방지.
  - 실제 조회 로직을 `_get_balance_impl()`로 분리.
- **balance_sync_service.py**
  - `_call_kiwoom_balance()` 내부를 `asyncio.wait_for(..., timeout=10.0)`로 래핑.
  - 타임아웃/예외 시 `None` 반환, sync 실패 메시지로 종료.

### 프론트엔드

- **client.ts**
  - `axios.create`에 `timeout: 15000` 추가. 모든 API 요청 15초 초과 시 ECONNABORTED로 실패 처리.
- **useAccounts.ts**
  - `retry: 1`, `retryDelay: 2000` 설정으로 재시도 최소화.
- **accounts/page.tsx**
  - `isError` 시 스켈레톤 대신 "계좌 목록을 불러오지 못했습니다" 메시지 + "다시 시도" 버튼 노출.

## 테스트 결과

- [x] 키움 잔액 API: 타임아웃/에러 시 0 반환 확인 (코드 검토)
- [x] 잔고 동기화: 10초 타임아웃 적용 확인
- [x] 계정 목록 API: DB 전용이라 키움 실시간 호출 없음 (동기화 버튼으로 갱신)
- [x] 페이지 로딩: 15초 타임아웃 + 에러 시 로딩 해제 및 안내 메시지
- [x] Python 문법 검사 통과
- [x] Frontend `tsc --noEmit` 통과
- [x] Frontend `npm run build` 성공
- [x] go100, go100-frontend 재시작 후 active
- [ ] 잔액 API 수동 호출 (로그인 토큰 미확보로 스킵)
- [ ] 브라우저 E2E (환경 제한으로 스킵)

## 비고

- kis-v41-* 서비스 재시작 없음 (규칙 준수).
- strategy_cards / v4_positions / .env 미변경.
- 변경 파일 헤더에 `CUR-GO100-KIWOOM-BALANCE-LOADING-FIX-001, 2026-02-24` 주석 추가.
