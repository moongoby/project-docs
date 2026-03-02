# CUR-GO100-BACKTEST-OPT-PHASE1-001 보고서
**작업 ID:** CUR-GO100-BACKTEST-OPT-PHASE1-001  
**날짜:** 2026-02-25  
**우선순위:** P0 (CEO 직접 지시)  
**브랜치:** feat/CUR-GO100-BACKTEST-OPT-PHASE1-001 → phase-2c-command-center

---

## 1. 사전확인 결과 (SKIP 판단)

| 항목 | 명령/확인 | 결과 | 판단 |
|------|-----------|------|------|
| DataGate 관련 파일 | `find backend -name "*data_gate*"` | `backend/app/services/go100/backtest/data_gate.py` 존재 | **기반영 확인** – data_gate.py 이미 구현됨 |
| check_readiness 사용 | `grep check.readiness, data_gate` | backtest_router.py에서 run/retry 시 data_gate_check_readiness 호출 | **기반영 확인** – run/retry 게이트 연동됨 |
| POST /check-readiness | 라우터 엔드포인트 목록 | 기존에 **없음** | **신규 추가** – POST /check-readiness 엔드포인트 추가 |
| OHLCV 프리로드 | `grep preload, pre_load` in backtest/ | 없음 | **신규 구현** – preload_ohlcv, get_stock_data, get_ohlcv_slice 추가 |
| 백테스트 실행 기록 | `SELECT COUNT(*) FROM go100_backtest_runs` | (본 환경에서 DB 미연결로 미실행) | 서버([SERVER-IP])에서 확인 필요 |
| backtest 서비스 파일 | `ls backend/app/services/go100/backtest/` | backtest_service, data_gate, data_loader, minute_data_loader, simulator, minute_simulator 등 | 구조 확인 |
| backtest_router 엔드포인트 | `grep def / @router` | GET "", POST /run, POST /retry/{id}, GET /{run_id} | POST /check-readiness **추가** |
| data_loader 구조 | `grep -n "def " data_loader.py` | load_ohlcv, load_stock_info | preload_ohlcv, get_stock_data, get_ohlcv_slice **추가** |
| simulator 구조 | simulator.py | BacktestSimulator.run() 매일 load_ohlcv 호출 | **수정** – 1회 프리로드 + get_ohlcv_slice 사용 |
| 프론트 checkBacktestReadiness | go100Api.ts, backtest/page.tsx | 이미 구현·연동됨 | **기반영 확인** – 수정 없음 |

---

## 2. DataGate 구현 내역 (보완)

- **기반영:** `data_gate.py`의 `check_readiness()`, 전략 타입별 REQUIREMENTS, gate_level(GREEN/YELLOW/RED), run/retry 시 RED 차단은 이미 반영됨.
- **본 작업에서 한 일:**
  - **POST /api/go100/backtest/check-readiness** 엔드포인트 추가 (body: `go100_card_id`, `period_months`).
  - run/retry 호출 시 **period_months**를 요청 기간(start_date~end_date)으로 계산해 `check_readiness`에 전달.
  - **adjusted_period**에 `requested_months`, `executable_months` 필드 추가.
  - ohlcv_daily 컬럼명 정정: `trade_date` → `date` (실제 스키마에 맞춤).

### 5개 시간축 요건표 (data_gate.REQUIREMENTS)

| strategy_type | 일봉(일) | 분봉(일) | 수급(일) | 섹터 | 재무 | 배당 | gate_if_missing |
|---------------|----------|----------|----------|------|------|------|-----------------|
| scalping | 0 | 20 | 0 | - | - | - | GREEN |
| daily | 120 | 0 | 60 | - | - | - | GREEN |
| swing | 250 | 0 | 0 | O | O | - | GREEN |
| mid_swing | 500 | 0 | 0 | - | O | - | GREEN |
| long_position | 750 | 0 | 0 | - | O | O | YELLOW (배당 미구축) |

---

## 3. OHLCV 1회 프리로드 구현 내역

### 3.1 일봉 (data_loader.py)

- **preload_ohlcv(stock_codes, start_date, end_date, db)**  
  - 해당 종목·기간 일봉을 1회 로드, MultiIndex(stock_code, date) DataFrame 반환.
- **get_stock_data(preloaded_df, stock_code, target_date, lookback_days)**  
  - 프리로드된 DataFrame에서 종목·날짜 기준 lookback_days만큼 슬라이싱.
- **get_ohlcv_slice(preloaded_df, stock_codes, target_date, lookback_days)**  
  - 여러 종목에 대해 target_date 기준 lookback_days 슬라이스 반환 (load_ohlcv와 동일 형식).

### 3.2 simulator.py (일봉 시뮬레이터)

- run() 시작 시:
  - 거래일 목록 수집 후, 유니버스 갱신일마다 `universe_engine.select_stocks` 호출해 **전체 등장 종목 합집합(all_codes)** 수집.
  - **preload_ohlcv(all_codes, load_start_str, end_date, db)** 1회 호출.
- 루프 내:
  - 기존 `await self.data_loader.load_ohlcv(...)` 제거.
  - **get_ohlcv_slice(preloaded_df, codes, day, lookback_days)** 로 대체 (DB 쿼리 0회).

### 3.3 분봉 (minute_data_loader.py, minute_simulator.py)

- **preload_minute(db, stock_codes, start_date, end_date)**  
  - v4_ohlcv_minute에서 전체 기간 분봉 1회 배치 로드.
- **get_minute_for_day(preloaded_df, stock_code, day_date)**  
  - 프리로드된 분봉에서 특정 종목·일자만 슬라이싱.
- minute_simulator.run_backtest():
  - 시작 시 **preload_minute(universe_codes, start_date, end_date)** 1회 호출.
  - 포지션 청산·신규 진입 시 `load_minute_data` 대신 **get_minute_for_day(preloaded_minute_df, stock_code, day_date)** 사용.

---

## 4. E2E 백테스트 결과 (서버에서 실행 권장)

본 환경에서는 DB 접속(Peer authentication) 불가로 아래는 서버([SERVER-IP])에서 실행 후 기록하는 것을 권장합니다.

- **DataGate 확인:**  
  `POST /api/go100/backtest/check-readiness`  
  Body: `{"go100_card_id": 14, "period_months": 1}`  
  → gate_level GREEN 확인.

- **백테스트 실행:**  
  `POST /api/go100/backtest/run`  
  Body: `{"go100_card_id": 14, "period_months": 1, "start_date": "...", "end_date": "..."}`  
  → run_id 반환 확인.

- **결과 확인:**  
  `SELECT run_id, go100_card_id, status, total_return, max_drawdown, sharpe_ratio, trade_count, started_at, completed_at FROM go100_backtest_runs ORDER BY run_id DESC LIMIT 5;`  
  → status=COMPLETED, 메트릭 존재, 1건 이상 확인.

- **실행 시간 목표 (BEFORE/AFTER 비교):**
  - 카드 #14 (일봉) 1개월: 목표 5~8초
  - 카드 #20 (일봉) 1개월: 목표 5~8초
  - 카드 #13 (분봉) 1개월: 목표 20~35초

---

## 5. 변경 파일 목록

| 파일 | 작업 |
|------|------|
| backend/app/services/go100/backtest/data_gate.py | 수정 – ohlcv_daily 컬럼 date, adjusted_period에 requested_months/executable_months |
| backend/app/services/go100/backtest/data_loader.py | 수정 – preload_ohlcv, get_stock_data, get_ohlcv_slice 추가 |
| backend/app/services/go100/backtest/simulator.py | 수정 – 1회 프리로드 + get_ohlcv_slice 연동 |
| backend/app/services/go100/backtest/minute_data_loader.py | 수정 – preload_minute, get_minute_for_day 추가 |
| backend/app/services/go100/backtest/minute_simulator.py | 수정 – preload_minute 및 get_minute_for_day 연동 |
| backend/app/routers/go100/backtest_router.py | 수정 – POST /check-readiness 추가, run/retry에서 period_months 계산 후 check_readiness 전달 |

**미수정 (기반영 확인):**  
frontend go100Api.ts, backtest/page.tsx – checkBacktestReadiness 및 RED/YELLOW/GREEN UI 이미 반영됨.

---

## 6. 검증 결과

- **Python import:**  
  `python3 -c "from backend.app.services.go100.backtest.data_gate import check_readiness; print('data_gate import OK')"`  
  → 정상 (해당 환경에서 실행 시).

- **Pre-commit-check (scripts/pre-commit-check.sh):**  
  Python 문법 체크, TypeScript 체크 통과.

- **헬스체크 / DataGate API / TSC·빌드:**  
  서버([SERVER-IP])에서 `systemctl restart go100`, `curl .../health`, `curl .../check-readiness`, `cd frontend && npx tsc --noEmit && npm run build` 실행 후 결과 기록 권장.

---

## 7. 백업

- **경로:** `/root/backup/backtest-opt-phase1-20260225-095031`
- **내용:** backtest 서비스 디렉터리, backtest_router.py, main.py 복사본 (DB 스키마 덤프는 서버 DB 연결 필요).

---

## 8. 커밋

- **브랜치:** feat/CUR-GO100-BACKTEST-OPT-PHASE1-001
- **커밋 메시지:**  
  `feat: CUR-GO100-BACKTEST-OPT-PHASE1-001 - DataGate API + OHLCV 프리로드 + check-readiness 엔드포인트`
- **머지:** phase-2c-command-center에 머지 및 push는 서버에서 실행 후 `git log --oneline -1`로 확인.

---

**보고서 작성:** 2026-02-25  
**문서 push:** project-docs 저장소 `go100/reports/`에 push 후 `git log --oneline -1` 확인 필수.
