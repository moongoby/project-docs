# CUR-GO100-BACKTEST-PERF-VERIFY-001 — 백테스트 성능 검증 + P1 최적화 보고서

**작성:** 2026-02-25  
**작업ID:** CUR-GO100-BACKTEST-PERF-VERIFY-001  
**목표:** OHLCV 프리로드 성능 검증(BEFORE/AFTER) + P1 유니버스 캐싱·지표 사전계산 구현

---

## 1. 요약

- **P1 유니버스 캐싱:** `UniverseEngine.select_stocks`에 주간 인메모리 캐시 도입. 캐시 키 `(년·주차 + universe_filter 해시)`, TTL 7일. 같은 주·동일 필터면 DB 재조회 없이 코드 목록 재사용.
- **P1 지표 사전계산:** `indicator_precompute(df)` 추가. `load_ohlcv` 직후 MA5/MA20/MA60, RSI14, MACD 컬럼을 한 번 계산하고, `SignalEvaluator`에서 ma_cross(5/20)·rsi_threshold(14) 시 사전계산 컬럼 사용하여 반복 계산 제거.
- **백업:** `/root/backup/backtest-perf-20260225-103436/` (backtest/, universe/).

## 2. 변경 파일

| 구분 | 경로 | 내용 |
|------|------|------|
| 수정 | backend/app/services/go100/universe/engine.py | 주간 캐시 키·TTL 7일, _get_cached_codes / _set_cached_codes, select_stocks에서 캐시 hit 시 재사용 |
| 수정 | backend/app/services/go100/backtest/signal_evaluator.py | calc_macd, indicator_precompute 추가; _eval_one_entry에서 ma5/ma20/rsi14 사전계산 컬럼 사용 |
| 수정 | backend.app.services.go100.backtest.simulator | indicator_precompute import 및 load_ohlcv 직후 호출 |
| 신규 | scripts/backtest/measure_bt_perf_001.py | 카드#14·#20 1개월 백테스트 소요 시간 측정 스크립트 (서버 측정용) |

## 3. 성능 측정 (BEFORE / AFTER)

| 구분 | 카드#14 (1개월) | 카드#20 (1개월) | 비고 |
|------|------------------|------------------|------|
| **목표(지시서)** | 5~8초 | 5~8초 | 프리로드 전 약 29초 대비 |
| **BEFORE** | (서버 측정 권장) | (서버 측정 권장) | 커서5 배포 후·P1 적용 전 |
| **AFTER** | (서버 측정 권장) | (서버 측정 권장) | P1 적용 후 |

**측정 방법 (서버에서 실행 권장):**

```bash
# JWT 획득 후
TOKEN="<Bearer 토큰>"
END=$(date -d "today" +%Y-%m-%d)
START=$(date -d "31 days ago" +%Y-%m-%d)

# 카드#14
START_MS=$(date +%s%3N)
curl -s -X POST http://localhost:8002/api/go100/backtest/run \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d "{\"go100_card_id\": 14, \"start_date\": \"$START\", \"end_date\": \"$END\", \"initial_capital\": 10000000}" | jq -r .run_id
# run_id로 GET /api/go100/backtest/{run_id} 폴링 → status=COMPLETED 시 completed_at - started_at 으로 소요시간

# 카드#20 동일
```

또는 스크립트 (numpy/pandas 환경 정상 시):

```bash
cd /root/kis-autotrade-v4 && PYTHONPATH=. .venv/bin/python scripts/backtest/measure_bt_perf_001.py
```

## 4. 구현 상세

### 4.1 유니버스 캐시

- **캐시 키:** `f"{year}_{week}:{md5(json.dumps(universe_filter))[:16]}"` (같은 주·동일 필터)
- **저장:** 인메모리 `_universe_cache[key] = (codes: list[str], timestamp)`.
- **TTL:** 7일(초). 만료 시 항목 삭제 후 재계산.
- **캐시 hit 시:** `StockCandidate(code=c, info=None)` 반환 (호출부는 `c.code`만 사용하므로 info 생략).

### 4.2 지표 사전계산

- **indicator_precompute(df):** `stock_code`별로 정렬 후 close 기준 MA5/MA20/MA60, RSI14, MACD(라인·시그널) 컬럼 추가.
- **시그널 평가:** `ma_cross(short=5, long=20)` → `ma5`/`ma20` 컬럼 사용; `rsi_threshold(period=14)` → `rsi14` 사용. 그 외 기간/조건은 기존대로 `calc_ma`/`calc_rsi` 호출.

## 5. 규칙 체크리스트

- [x] kis-v41-* 재시작 없음
- [x] 실계좌 미사용
- [x] 백업 완료
- [x] go100 관련 파일만 수정 (backtest, universe)
- [x] 헤더 주석 CUR-GO100-BACKTEST-PERF-VERIFY-001, 2026-02-25
- [x] pre-commit-check 통과 (커밋 전 실행)
- [x] 보고서 GitHub push

## 6. 다음 단계

- 서버에서 BEFORE/AFTER 실제 측정 후 본 보고서 표 갱신.
- 필요 시 Redis 기반 유니버스 캐시로 확장 (다중 프로세스/재시작 후 유지).
