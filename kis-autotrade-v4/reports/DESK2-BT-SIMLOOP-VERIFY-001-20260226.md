# DESK2-BT-SIMLOOP-VERIFY-001 실거래 발생 검증 보고서

- **일자**: 2026-02-26  
- **우선순위**: P0  
- **선행**: DESK2-BT-SIMLOOP-001  

---

## STEP 1 — 분봉 데이터 존재 확인

### 2026-02-20 분봉 건수

| 쿼리 | 결과 |
|------|------|
| `SELECT COUNT(*) FROM v4_ohlcv_minute WHERE trade_date = '2026-02-20'` | **211,411건** |

(지침의 `date_trunc('day', datetime)` 대신 실제 백테스터가 사용하는 `trade_date` 컬럼 기준으로 확인함.)

### 데이터 있는 최근 거래일 10일

| trade_date | bar_count |
|------------|-----------|
| 2026-02-25 | 186,246 |
| 2026-02-24 | 191,903 |
| 2026-02-23 | 191,904 |
| **2026-02-20** | **211,411** |
| 2026-02-19 | 214,328 |
| 2026-02-13 | 214,242 |
| 2026-02-12 | 213,664 |
| 2026-02-11 | 212,971 |
| 2026-02-10 | 212,678 |
| 2026-02-09 | 212,917 |

### universe 로드 쿼리 (_load_minute_bars)

- **파일**: `backend/app/services/trading/desk2/tests/desk2_backtester.py`
- **WHERE 조건**: `trade_date = %s AND stock_code IN (...)`  
- **결론**: 2026-02-20 데이터 존재하므로 로드 쿼리 버그 없음. 해당일 기준 실행 가능.

---

## STEP 2 — 분기 판단

- **2026-02-20 데이터 있음** → 로드 쿼리 수정 없이 해당일로 실행.

---

## STEP 3 — 실거래 발생 검증

### 실행 명령

```bash
cd /root/kis-autotrade-v4 && source .venv/bin/activate
PYTHONPATH=/root/kis-autotrade-v4:/root/kis-autotrade-v4/backend \
python3 scripts/backtest/desk2_backtester.py \
  --date 2026-02-20 --conditions C1,C2,C3,C4,C5,C6,C7 \
  --strategies ALL --verbose \
  --session-name "DESK2-V2-SIMLOOP-VERIFY" \
  --output-json /tmp/simloop_verify.json
```

### 사용 날짜

- **2026-02-20**

### PASS 기준 검증

| 항목 | 기준 | 결과 |
|------|------|------|
| 발굴 | ≥ 1건 | **3건** (038530 C4 2회, 004060 C4 1회) |
| 거래(진입+청산) | ≥ 1건 | **1건** (004060 BRAVO_ORB, 진입 후 손절 청산) |
| v4_bt_trades INSERT | 확인 | **1건** 기록 |
| v4_bt_discoveries INSERT | 확인 | **3건** 기록 |
| 대시보드 API 해당 세션 trades 조회 | 가능 | **가능** (아래 경로) |

### 실행 요약 (--verbose)

- **universe**: 500종목  
- **bars**: 500종목, 총 188,353건  
- **all_times**: 381개 봉  
- **레짐**: MILD_TREND_DOWN  
- **발굴**: [C4] 038530 (DESK 62), [C4] 004060 (DESK 62), [C4] 038530 (DESK 62)  
- **진입/청산**: 004060 BRAVO_ORB — entry=587, exit=448, pnl_pct=-24.00%, exit_type=STOP_LOSS  
- **BT trade written**: T-BT-DESK2-V2-SIMLOOP-VER-20260226064603-31c2975f  
- **BT session updated**: status=FAIL (손실 1건으로 pass_criteria 미충족)

### stalk() 호출

- 로그에 **총 호출 횟수 집계 미출력**.  
- 구조상 매 봉마다 `orch_l3.process_tick` → watchlist 종목에 대해 전략별 `stalk()` 호출.  
- 381봉 × (해당 봉 시점 watchlist 종목 수) × 전략 수로 추정 가능.

### CS Score

- **진입 건**: BRAVO_ORB 004060 **cs=60**, composite=37.2 (≥50 충족으로 진입)

### DB INSERT 확인

| 테이블 | 세션 (session_id) | 건수 |
|--------|-------------------|------|
| v4_bt_sessions | BT-DESK2-V2-SIMLOOP-VER-20260226064603 (id=9) | 1 |
| v4_bt_discoveries | 동일 | **3** |
| v4_bt_trades | 동일 | **1** |

### 대시보드 확인

- **세션 상세**: `GET /api/v1/backtest/sessions/BT-DESK2-V2-SIMLOOP-VER-20260226064603`  
- **해당 세션 거래 목록**: `GET /api/v1/backtest/sessions/BT-DESK2-V2-SIMLOOP-VER-20260226064603/trades`  
- (실서버 기준: `https://trading41.newtalk.kr/api/v1/backtest/sessions/BT-DESK2-V2-SIMLOOP-VER-20260226064603/trades`)

---

## STEP 4 — 재현성

- 동일 날짜(**2026-02-20**) 2회 실행 후 `--output-json` 재현성 JSON 비교.
- **결과**: `diff /tmp/simloop_verify_run1.json /tmp/simloop_verify_run2.json` → **0건 (동일)**.

---

## STEP 5 — 결론

- **분봉 데이터**: 2026-02-20 **211,411건** 존재.  
- **사용 날짜**: 2026-02-20.  
- **발굴**: 3건, **거래**: 1건(진입+청산), **v4_bt_discoveries/v4_bt_trades** INSERT 확인, **대시보드 API** 해당 세션 trades 조회 가능.  
- **재현성**: 동일 일자 2회 실행 시 재현성 JSON **diff 0건**.  

**DESK2-BT-SIMLOOP-VERIFY-001 실거래 발생 검증 기준 충족.**

---

## 문서 레포 푸시 및 경로

- 본 보고서 경로: **`report/v41/DESK2-BT-SIMLOOP-VERIFY-001-20260226.md`** (메인 레포 `kis-autotrade-v4` 내).  
- 별도 문서 레포(예: project-docs)에 푸시가 정책인 경우, 해당 레포로 복사·푸시 후 최종 문서 URL/경로를 운영 측에서 보고할 것.
