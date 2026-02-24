# CUR-GO100-TRADE-MODAL-IMPL-001 — 자동매매 시작 모달 구현 (설정값 중복 제거) 보고서

**발행:** 2026-02-24 13:00 KST  
**우선순위:** P0  
**프로젝트:** /root/kis-autotrade-v4  
**브랜치:** phase-2c-command-center → feat/CUR-GO100-TRADE-MODAL-IMPL-001  

---

## 1. 작업 요약 (AS-IS → TO-BE)

### AS-IS
- 전략카드에 저장된 설정값(allocated_amount, max_stocks, risk_params)을 /trade 스케줄 등록 시 사용자가 다시 수동 입력해야 함 (설정값 중복).
- 카드 토글(is_active)이 v4_trade_schedules와 연동되지 않아, 토글 ON 해도 스케줄이 없으면 자동매매 미실행.
- auto_trade_engine은 스케줄 값만 읽고 카드의 allocated_amount/max_stocks/risk_params는 사용하지 않음.

### TO-BE
- 전략카드 상세에서 **"자동매매 시작"** 모달로 계좌 선택 후 스케줄 자동 생성.
- 카드 설정값을 모달에 자동 로드, 필요 시만 수정 가능.
- 카드 비활성화(토글 OFF) 시 해당 카드의 go100 스케줄도 자동 비활성화.

---

## 2. 변경 파일 목록

| 구분 | 파일 경로 |
|------|-----------|
| **신규** | backend/app/routers/go100/trade_modal_router.py |
| **신규** | frontend/src/go100/components/AutoTradeModal.tsx |
| **수정** | backend/app/routers/go100/strategy_router.py |
| **수정** | backend/app/main.py |
| **수정** | frontend/src/go100/api/go100Api.ts |
| **수정** | frontend/src/app/(protected)/go100/strategies/[id]/page.tsx |

---

## 3. 신규 API 4개 스펙

| 메서드 | 경로 | 설명 | 입력 | 출력 |
|--------|------|------|------|------|
| POST | /api/go100/trade/start | 자동매매 시작 | go100_card_id, account_id, (선택) invest_amount, max_stocks, stop_loss_pct, take_profit_pct | success, schedule_id, card_id, account_id, settings |
| POST | /api/go100/trade/stop | 자동매매 중지 | go100_card_id | success, card_id, stopped_schedules |
| GET | /api/go100/trade/status/{card_id} | 카드별 자동매매 상태 | path: card_id | is_trading, schedule, account |
| GET | /api/go100/trade/accounts | 활성 계좌 목록 | 없음 | [{ account_id, broker_type, account_number, alias, is_mock }] |

---

## 4. DB 변경사항

- **v4_trade_schedules**
  - **INSERT:** 자동매매 시작 시 card_source='go100', strategy_id=go100_card_id, user_id, account_id, invest_amount, max_stocks, stop_loss_pct, take_profit_pct, is_active=true, run_interval='daily', market_open_only=true 로 행 생성.
  - **UPDATE:** 동일 카드에 활성 스케줄이 이미 있으면 해당 행을 갱신(계좌/금액/종목수/손절/익절).
- **go100_strategy_cards**
  - **UPDATE:** start 시 is_active=true, is_live=true; stop 시 is_active=false, is_live=false.
  - **PATCH toggle:** is_active를 false로 바꿀 때 v4_trade_schedules에서 card_source='go100' AND strategy_id=card_id 인 행을 is_active=false 로 UPDATE.

---

## 5. 테스트 결과

- **Python 문법:** `find backend/app/routers/go100 ... -exec python3 -m py_compile {} \;` 통과.
- **TypeScript:** `npx tsc --noEmit` 통과 (exit 0).
- **프론트 빌드:** `npm run build` 실행 (Compiled successfully).
- **API 존재 확인:** 라우터 prefix `/api/go100/trade` 로 등록됨. (실서버에서 401/200 확인 권장.)
- **통합 테스트:** 제공된 `/tmp/test_trade_modal.py` 스크립트로 로그인 → accounts → status → start → status → stop 순서 검증 권장.

---

## 6. 검수 결과

- **기존 토글:** PATCH /api/go100/strategy-cards/{card_id}/toggle 유지. OFF 시에만 v4_trade_schedules 비활성화 추가. 기존 동작 유지.
- **기존 삭제/백테스트/모의거래:** strategies/[id]/page.tsx 에서 기존 링크 및 버튼 유지. 자동매매 섹션만 상단에 추가.

---

## 7. 체크리스트

- [x] STEP 0: 백업 생성 완료
- [x] STEP 1: trade_modal_router.py 4개 API 구현
- [x] STEP 2: strategy_router.py 토글 → 스케줄 연동
- [x] STEP 3: main.py 라우터 등록
- [x] STEP 4: go100Api.ts API 함수 4개 추가
- [x] STEP 5: AutoTradeModal.tsx 모달 구현
- [x] STEP 6: strategies/[id]/page.tsx 시작/중지 버튼
- [x] STEP 7: python compile ✓, tsc ✓, npm build ✓
- [ ] STEP 8: 통합 테스트 (서버에서 스크립트 실행 권장)
- [ ] STEP 9: pre-commit-check.sh 통과, 커밋, 병합, push
- [ ] STEP 10: 보고서 GitHub push, HTTP 200 확인

---

**보고서 저장 위치:** /root/project-docs/go100/reports/CUR-GO100-TRADE-MODAL-IMPL-001-20260224.md  
**GitHub:** https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-TRADE-MODAL-IMPL-001-20260224.md
