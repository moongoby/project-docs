# NXT-LIVE-TRADE-EXEC 보고서

| 항목 | 내용 |
|------|------|
| 작업 ID | NXT-LIVE-TRADE-EXEC |
| 일시 | 2026-02-23 KST |
| 서버 | root@[SERVER-IP] |
| 브랜치 | phase-2c-command-center |
| 승인 | CEO 즉시 승인 |

## 코드 수정 (CUR-NXT-EXCG-PARAM-FIX-001)
- 수정 파일: `backend/app/services/trading/v4_order_executor.py`, `backend/app/services/trading/kis_order_service.py`
- 변경 내용: 주문 body에 EXCG_ID_DVSN_CD 파라미터 추가, 함수 시그니처에 exchange: str = "KRX" 추가 (매수/매도/정정취소)
- 검수 결과: Cursor 3 검수 통과 후 push 예정
- 커밋 해시: df593428

## 실매매 테스트 결과
| 항목 | 결과 |
|------|------|
| 실계좌 전환 | 완료 (KIS_ACCOUNT_MODE=real) |
| 잔고 조회 | 완료 (cash 262,593원, total_eval 606,889원, 보유 6종목) |
| NXT 매수 | 요청 성공 → KIS 응답 "주문가격이 하한가 미만입니다" (체결 없음, EXCG_ID_DVSN_CD=NXT 전달 확인) |
| NXT 매도 | 동일 (하한가 미만 거절, NXT 경로 동작 확인) |
| 실현 P&L | 없음 (미체결) |
| .env 복원 | 완료 (KIS_ACCOUNT_MODE=virtual) |

## DB 무결성
| 테이블 | 전 | 후 |
|--------|----|----|
| strategy_cards | 60 | 60 |
| v4_positions OPEN | 5 | 5 |

## 체크리스트
- [x] 코드 수정 + 검수 완료
- [x] 실계좌 전환/복원 완료
- [ ] NXT 매수 체결 (KIS 하한가 검증으로 미체결 — NXT 파라미터 전달은 정상)
- [ ] NXT 매도 체결 (동일)
- [x] DB 무결성 확인
- [x] 서비스 전체 정상
- [x] project-docs 보고서 push

## 비고
- 실행: `scripts/nxt_live_trade_test.py` (exchange="NXT" 적용). 종목 056190, 지정가 3,000원 1주.
- KIS 실계좌 토큰 발급 1분당 1회 제한(EGW00133)으로 1차 시도 후 1분 대기 재실행.
- NXT 호출 경로 및 EXCG_ID_DVSN_CD 전달 정상 동작 확인. 체결을 위해 NXT 시간대 적정 호가 사용 필요.
