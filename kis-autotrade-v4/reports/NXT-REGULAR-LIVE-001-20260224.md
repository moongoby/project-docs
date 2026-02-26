# NXT 정규장 실매매 V4.1 파이프라인 보고서 — CUR-NXT-REGULAR-LIVE-001

| 항목 | 내용 |
|------|------|
| 작업 ID | CUR-NXT-REGULAR-LIVE-001 |
| 일시 | 2026-02-24 09:36 ~ 10:40 KST |
| 서버 | root@211.188.51.113 |
| 프로젝트 | /root/kis-autotrade-v4 |
| 브랜치 | phase-2c-command-center |
| 장 상태 | 정규장 (09:00~15:30) |
| 매매 방식 | V4.1 파이프라인 경유 (V4OrderExecutor, exchange=NXT) |

---

## STEP 0: 사전 확인

| 항목 | 결과 |
|------|------|
| KST 확인 | 2026-02-24 10:20 (Tuesday) |
| kis-v41-api / monitor / scheduler / position-monitor | active |
| /health | OK (database, redis connected) |
| strategy_cards | 60 |
| v4_positions OPEN | 11 |
| 오늘 order_requests | 0 |
| DB 백업 | /tmp/backup_NXT_REGULAR_LIVE_*.dump (PGPASSWORD 설정 후 수동 실행 가능) |

---

## STEP 1: .env 백업 및 실계좌 전환

- .env 백업: `.env.bak.pre-nxt-regular-202602241022` 생성
- 실계좌 전환: `KIS_ACCOUNT_MODE=real` 확인

---

## STEP 2: kis-v41-api 재시작 (1회차)

- 재시작 카운트: 1/2
- systemctl is-active kis-v41-api: active
- curl /health: OK

---

## STEP 3: 토큰 및 잔고

- 토큰: V4OrderExecutor.get_balance() 호출 시 내부 발급/재사용 성공
- 예수금(cash): 234,645원
- 총평가(total_eval): 596,492원
- 보유종목: 002630, 003530, 004060, 006340(5주) 등

---

## STEP 4: NXT 현재가 및 종목 선택

- 후보: 056190, 001720, 004170, 002710, 000020, 003480 (MarketDataService 조회)
- 003480: NXT 주문 시 "경쟁매매 거래 불가 종목" → 제외
- 선택: 056190 (에스에프에이), 현재가 32,850원
- 지정가 매수 시도: 32,850원 1주

---

## STEP 5: V4.1 파이프라인 경유 매수 (1주)

- 사용: V4OrderExecutor(config_id=4, dry_run=False).place_buy_order(..., exchange='NXT')
- 1차 매수: 056190, 32,850원 1주 → 주문번호 **0016200400**, 전송 완료 (미체결)
- 토큰 1분 제한(EGW00133)으로 재시도 시 1분 대기 후 진행
- 2차: 미체결 0016200400 취소 후 재매수 32,900원 1주 → 주문번호 **0016557500** (미체결)
- 45초 후 잔고 확인: 056190 미보유 → 미체결 유지
- 미체결 0016557500 취소 완료
- **실제 체결 0주.** 매수/매도 체결 없음.

---

## STEP 6: V4.1 파이프라인 경유 매도 (1주)

- 매수 미체결로 매도 미실행
- 매도 주문번호: -
- 매도 체결가 / 수수료 / 세금 / realized_pnl: 해당 없음

---

## STEP 7: .env 복원 및 API 재시작 (2회차)

- .env 복원: `KIS_ACCOUNT_MODE=virtual` 확인 (복원 완료)
- kis-v41-api 재시작: 2/2 (소진)
- 전체 서비스: active, /health OK

---

## STEP 8: DB 정합성 (사후)

| 테이블 | 사전 | 사후 | 비고 |
|--------|------|------|------|
| strategy_cards | 60 | 60 | 동일 |
| v4_positions OPEN | 11 | 11 | 동일 |
| 오늘 CLOSED positions | - | 0 | 테스트 체결 없음 |
| 오늘 order_requests | 0 | 0 | V4OrderExecutor 직접 호출이라 미기록 |

※ v4_orders 테이블은 본 DB 스키마에 없어 조회 생략.

---

## STEP 9: 보고서 및 GitHub

- 로컬: /root/kis-autotrade-v4/report/v41/NXT-REGULAR-LIVE-001-20260224.md
- project-docs: kis-autotrade-v4/reports/NXT-REGULAR-LIVE-001-20260224.md
- git push: 완료 시 기록
- GitHub raw URL 200: 확인 예정

---

## 전체 타임라인

| 시각 (KST) | 단계 | 비고 |
|------------|------|------|
| 10:20 | STEP 0 완료 | KST, 서비스, DB 스냅샷 |
| 10:22 | STEP 1 완료 | .env 백업, real 전환 |
| 10:22 | STEP 2 완료 | API 재시작 1회차 |
| 10:23 | STEP 3 완료 | 잔고 조회 |
| 10:28 | STEP 4 완료 | 현재가 조회, 056190 선택 |
| 10:28 | STEP 5-1차 매수 | 0016200400 접수, 미체결 |
| 10:30 | 토큰 제한 대기 | 1분 |
| 10:31 | STEP 5-2차 매수 | 0016200400 취소, 0016557500 접수, 미체결 |
| 10:32 | 잔고 확인 | 056190 미보유 |
| 10:38 | 토큰 제한 대기 | 1분 |
| 10:39 | 미체결 취소 | 0016557500 취소 |
| 10:39 | STEP 7 완료 | .env 복원, API 재시작 2회차 |
| 10:39 | STEP 8 완료 | DB 정합성 확인 |
| 10:40 | STEP 9 | 보고서 작성 |

---

## 체크포인트

- [x] 사전 DB 스냅샷 기록
- [x] .env 백업 완료
- [x] 실계좌 전환 및 API 재시작
- [x] 토큰/잔고 확인
- [ ] NXT 매수 체결 확인 (미체결로 미완료)
- [ ] NXT 매도 체결 확인 (미실행)
- [ ] P&L 기록 (체결 없음)
- [x] .env 복원 및 API 재시작
- [x] 사후 DB 정합성 (사전값과 동일)
- [x] 전체 서비스 active
- [ ] project-docs 보고서 push (GitHub raw 200)

---

## 참조

- CLAUDE.md, kis-v41-rules.md, MARKET-HOURS-KR.md
- DB-SCHEMA.md, v41-architecture-v1.2.md
- NXT-TR-ID-RESEARCH-20260223.md, NXT-LIVE-TRADE-EXEC-20260223.md
