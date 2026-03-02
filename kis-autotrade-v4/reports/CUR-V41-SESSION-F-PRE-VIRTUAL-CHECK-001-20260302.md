# Session F-Pre: 03-03 Virtual Run 사전 점검 보고서

- **보고서 ID**: CUR-V41-SESSION-F-PRE-VIRTUAL-CHECK-001-20260302
- **작성일**: 2026-03-02 (KST)
- **목적**: 03-03(월) 08:40 Unified Engine Virtual Mode 첫 자동 실행 무중단 보장
- **점검자**: Claude Code (claude-sonnet-4-6)
- **최종 판정**: ✅ **ALL PASS — 03-03 Virtual Run GO**

---

## 점검 결과 요약

| # | 점검 항목 | 기대값 | 실측값 | 판정 | 비고 |
|---|----------|--------|--------|------|------|
| 1 | Cron premarket | 07:55 1-5 | `55 7 * * 1-5` | ✅ PASS | 오늘 07:55 이미 실행 확인 |
| 2 | Cron signal | 08:50 1-5 | `50 8 * * 1-5` | ✅ PASS | |
| 3 | Cron monitor | `*/1 9-15 1-5` | `*/1 9-15 * * 1-5` | ✅ PASS | |
| 4 | Cron close | 15:30 1-5 | `30 15 * * 1-5` | ✅ PASS | |
| 5 | 스크립트 경로 존재 | 파일 존재 | 40,300 bytes (03-02 06:34) | ✅ PASS | `scripts/run_unified_engine.py` |
| 6 | 로그 파일 존재 | `/var/log/unified_engine.log` | 799 bytes (03-02 07:55) | ✅ PASS | 오늘 premarket 로그 기록됨 |
| 7 | 로그 리다이렉션 | `>> log 2>&1` | 4건 모두 `>> /var/log/unified_engine.log 2>&1` | ✅ PASS | |
| 8 | ohlcv_daily 02-27 | > 0건 | 3,839건 (='20260227') | ✅ PASS | VARCHAR(8) 포맷 |
| 9 | v4_ohlcv_minute 최신 | 2026-02-27 | 2026-02-27 | ✅ PASS | |
| 10 | regime_daily 02-27 | ≥ 1건 | 1건 | ✅ PASS | |
| 11 | investor_daily 02-27 | > 0건 | 3,839건 | ✅ PASS | trade_date 컬럼 |
| 12 | v4_mock_trades 존재 | 테이블 존재·빈 상태 | 존재, 0건 | ✅ PASS | 첫 거래 03-03 예정 |
| 13 | KIS_VIRTUAL_APP_KEY | 존재 | 존재 | ✅ PASS | 값 미출력 |
| 14 | KIS_VIRTUAL_APP_SECRET | 존재 | 존재 | ✅ PASS | 값 미출력 |
| 15 | KIS_VIRTUAL_ACCOUNT_NUMBER | 존재 | 존재 | ✅ PASS | 값 미출력 |
| 16 | Mock API 토큰 발급 | HTTP 200 + access_token | HTTP 200 ✓ + access_token 존재 | ✅ PASS | openapivts.koreainvestment.com:29443 |
| 17 | kis-v41-api | active (running) | active (running) since 02-27 | ✅ PASS | 재시작 금지 준수 |
| 18 | kis-v41-scheduler | active (running) | active (running) since 02-24 | ✅ PASS | |
| 19 | kis-v41-monitor | active (running) | active (running) since 02-24 | ✅ PASS | |
| 20 | kis-v41-position-monitor | active (running) | active (running) since 02-24 | ✅ PASS | |
| 21 | 포트 8003 (V4.1 API) | LISTEN | LISTEN | ✅ PASS | uvicorn |
| 22 | 포트 8002 (GO100) | LISTEN | LISTEN | ✅ PASS | |
| 23 | 포트 3000 (Next.js) | LISTEN | LISTEN | ✅ PASS | next-server |
| 24 | 포트 80/443 (nginx) | LISTEN | LISTEN | ✅ PASS | |
| 25 | Swap 사용률 | < 80% | **66.6%** (5.3G/8G) | ✅ PASS | |
| 26 | Disk 사용률 | < 85% | **77%** (73G/99G) | ✅ PASS | 여유 22GB |
| 27 | 메모리 available | > 2GB | **7.9GB** available | ✅ PASS | |
| 28 | UnifiedEngine import | import OK | `import OK` | ✅ PASS | |
| 29 | 오늘 premarket 실행 확인 | 로그 존재 | 07:55:01 premarket 완료 | ✅ PASS | DB 연결 PASS, Mock URL 확인 |

---

## 상세 점검 내역

### Task 1 — Cron 4건 동작 확인

```
# UNIFIED ENGINE 4건 모두 등록 확인
55 7 * * 1-5   ... run_unified_engine.py --mode virtual --action premarket >> /var/log/unified_engine.log 2>&1
50 8 * * 1-5   ... run_unified_engine.py --mode virtual --action signal    >> /var/log/unified_engine.log 2>&1
*/1 9-15 * * 1-5 . run_unified_engine.py --mode virtual --action monitor  >> /var/log/unified_engine.log 2>&1
30 15 * * 1-5  ... run_unified_engine.py --mode virtual --action close     >> /var/log/unified_engine.log 2>&1
```

- 스크립트: `/root/kis-autotrade-v4/scripts/run_unified_engine.py` (40,300 bytes, 2026-03-02 06:34)
- 4건 모두 동일 로그 파일로 리다이렉션 ✅

### Task 2 — 로그 파일 준비

```
-rw-r--r-- 1 root root 799 Mar  2 07:55 /var/log/unified_engine.log
```

- 파일 존재, 오늘 07:55 premarket 실행 결과 기록됨 ✅
- 권한: 644 (root 소유, cron 실행 시 root → 문제없음)

### Task 3 — DB 연결 & 핵심 테이블

```
ohlcv_daily 2026-02-27 (='20260227'): 3,839건  ← VARCHAR(8) 날짜 포맷
v4_ohlcv_minute max trade_date: 2026-02-27
v4_market_regime_daily 2026-02-27: 1건
v4_investor_daily 2026-02-27: 3,839건
v4_mock_trades: 테이블 존재, 0건 (03-03 첫 거래 후 자동 적재)
```

> ⚠️ **참고**: `ohlcv_daily.date`는 `VARCHAR(8)` 포맷 (`'20260227'`). WHERE 절에서 ISO 날짜 형식(`'2026-02-27'`) 사용 시 0건 반환 주의.

### Task 4 — KIS Mock API 토큰 갱신 테스트

```
환경변수 체크:
  KIS_VIRTUAL_APP_KEY        = <존재함>
  KIS_VIRTUAL_APP_SECRET     = <존재함>
  KIS_VIRTUAL_ACCOUNT_NUMBER = <존재함>
  KIS_VIRTUAL_ACCOUNT_PRODUCT_CODE = <존재함>
  KIS_MOCK_RATE_LIMIT        = <존재함>

토큰 발급 결과:
  POST https://openapivts.koreainvestment.com:29443/oauth2/tokenP
  HTTP: 200
  access_token 존재: True ✅
```

### Task 5 — 서비스 & 포트 상태

| 서비스 | 상태 | 가동 시작 |
|--------|------|----------|
| kis-v41-api | active (running) | 2026-02-27 08:54:25 |
| kis-v41-scheduler | active (running) | 2026-02-24 20:36:12 |
| kis-v41-monitor | active (running) | 2026-02-24 20:36:13 |
| kis-v41-position-monitor | active (running) | 2026-02-24 20:36:12 |

포트: 8003 ✅ | 8002 ✅ | 3000 ✅ | 80 ✅ | 443 ✅

### Task 6 — 메모리 & 디스크

```
Memory: 15GB 중 7.8GB used, 7.9GB available
Swap:   8.0GB 중 5.4GB used (66.6%)  ← < 80% PASS
Disk:   99GB 중 73GB used (77%)      ← < 85% PASS, 여유 22GB
```

### Task 7 — UnifiedEngine dry-run

```python
from backend.app.services.unified_engine.engine import UnifiedEngine
# → import OK ✅
```

**오늘 07:55 premarket 실제 실행 로그 (발췌)**:
```
2026-03-02 07:55:01,145 [INFO] CTE 모듈 로드 성공
2026-03-02 07:55:01,181 [INFO] 통합 엔진 시작: mode=virtual action=premarket data-source=db
2026-03-02 07:55:01,181 [INFO] [PREMARKET] 07:55:01 — 장 전 준비 시작
2026-03-02 07:55:01,181 [INFO]   KIS Mock URL: https://openapivts.koreainvestment.com:29443
2026-03-02 07:55:01,181 [INFO]   VIRTUAL_ACCOUNT: 50160697
2026-03-02 07:55:01,206 [INFO] v4_mock_trades 테이블 확인/생성 완료
2026-03-02 07:55:01,206 [INFO]   DB 연결 PASS
2026-03-02 07:55:01,230 [INFO]   Mock API 엔드포인트: https://openapivts.koreainvestment.com:29443 (signal 액션에서 토큰 발급)
2026-03-02 07:55:01,230 [INFO] [PREMARKET] 완료
```

엔진이 이미 오늘 정상 기동했음을 실측 확인.

### Task 8 — 금일 수집 데이터 완결성 (02-27 금요일)

```
ohlcv_daily     2026-02-27 : 3,839건  ✅
investor_daily  2026-02-27 : 3,839건  ✅
regime_daily    2026-02-27 : 1건      ✅
ohlcv_minute    max        : 2026-02-27 ✅
```

모든 핵심 피처 테이블이 직전 거래일 데이터 완비.

---

## 최종 판정

```
✅ ALL PASS (29/29)
→ 03-03(월) Virtual Run GO
```

03-03 08:40 (cron 08:50 signal) Unified Engine 자동 가동 준비 완료.
`v4_mock_trades` 첫 거래 기록은 signal 실행 후 생성 예정.

---

## 특이 사항 / 주의

1. **오늘 07:55 premarket 이미 실행됨** — 로그 확인으로 cron 정상 동작 실증
2. **ohlcv_daily 날짜 포맷 주의** — `VARCHAR(8)` → `'20260227'` 형식 사용 필요
3. **Swap 66.6%** — 임계치(80%) 내이나 상승 추이 모니터링 권장
4. **Disk 77%** — 여유 22GB. 분봉 배치(16:00) 이후 주기적 정리 권장
5. **VKOSPI 임시 cron** (`0 9,12,15 2 3 *`) — 오늘(03-02) 한정, 내일(03-03) 자동 소멸

---

*보고서: CUR-V41-SESSION-F-PRE-VIRTUAL-CHECK-001-20260302.md*
*경로: kis-autotrade-v4/reports/*
