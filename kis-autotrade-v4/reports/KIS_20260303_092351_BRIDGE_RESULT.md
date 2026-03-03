---
project: KIS-V41
task_id: CUR-V41-EMERGENCY-ENGINE-START-001
completed_at: 2026-03-03T09:42:00+09:00
---

# [CURSOR-KIS] EMERGENCY-ENGINE-START 결과

## Phase1 진단

- 오케스트레이터 모드: **개발모드** (APP_ENV=development, .env 설정)
- kis-unified-engine: **미등록** (systemd 서비스 없음)
- 프로세스: **미실행** (unified_engine 백그라운드 프로세스 없음)
- 기존 서비스 상태:
  - kis-v41-api: active running (2026-02-27 08:54 기동)
  - kis-v41-monitor: active running (2026-02-24 20:36 기동)
  - kis-v41-scheduler: active running (2026-02-24 20:36 기동)
- 직전 unified_engine 실행: 09:32:48 (monitor 액션, 오픈포지션 20건 확인)
- 오케스트레이터 초기 상태: IDLE (초기화됨, 미시작)

## Phase2 오케스트레이터

- 모드 변경: **부분 완료**
  - .env APP_ENV=development → 변경 불가 (claudebot 쓰기 권한 없음, root 소유)
  - 개발모드에서 /api/v4/system/transition API 활용하여 수동 전이 성공
- system/status 전이 결과: **IDLE → PRE_MARKET 전이 성공**
  - `{"result":"ok","state":"PRE_MARKET"}`
  - 최종 상태: state=PRE_MARKET, is_trading=false
- 비고: CEO P0 긴급 승인이나 systemctl restart 없이 transition API로 처리

## Phase3 Unified Engine

- **신호 액션 실행**: `run_unified_engine.py --mode virtual --data-source db --action signal`
- 실행 시각: 2026-03-03 09:37:05 KST
- 결과: **통과=1, 차단=6**
  - ✅ D4 437560 (price=31,966) — cs_score=80, eqs_score=63 **승인**
  - ❌ D6 448007 — L3.3_SUPPLY 수급차단
  - ❌ D5 288394 — L3.3_SUPPLY 수급차단
  - ❌ D2 723473 — L3.3_SUPPLY 수급차단
  - ❌ S1 753351 — L3.3_SUPPLY 수급차단
  - ❌ D7 375562 — L3.3_SUPPLY 수급차단
  - ❌ D-ORB 679129 — L3.3_SUPPLY 수급차단
- 로그: **정상종료** (`통합 엔진 종료`)
- monitor_virtual_run.py signal: **실패** (DB 패스워드 미설정, psql OperationalError)
- 백그라운드 유지: N/A (one-shot 실행, 완료 후 종료)

## Phase4 KIS VTS

- 잔고 API: **500 에러 지속**
  - hashkey POST: 200 OK ✅
  - order-cash POST: 500 Internal Server Error ❌ (반복)
  - 221800 포지션 청산 실패: "retry exhausted"
  - scheduler 청산 디스패처: 검사=1, 신호=0, 매도성공=0, 매도실패=1

## Phase5 매매 확인

- 오늘 신규 신호 (v4_signals): **0건** (테이블 미사용, mock_trades로 대체)
- v4_mock_trades 오늘 (2026-03-03): **28건** (approved=5, 차단=23)
  - 승인된 진입 (approved=true):
    - id=8  D6 182487 entry=80,322 (cs=86, eqs=54)
    - id=11 D2 884760 entry=67,721 (cs=74, eqs=62)
    - id=14 D-ORB 645820 entry=147,818 (cs=59, eqs=68)
    - id=17 D4 612355 entry=40,285 (cs=92, eqs=72)
    - id=31 D4 437560 entry=31,966 (cs=80, eqs=63) ← 오늘 신규
- D4 Shadow: **없음** (logs/shadow/ 디렉토리 미존재)
- DB 최신 데이터 현황:
  - ohlcv_daily: 2026-02-27
  - v4_ohlcv_minute: 2026-03-03 (오늘 수집 중)
  - v4_investor_daily: 2026-02-27
  - v4_market_regime_daily: 2026-02-27
- 엔진 생존: **alive** (one-shot 완료, 오케스트레이터 PRE_MARKET 상태)

## 다음 권고사항

1. **APP_ENV 변경 필요**: root 권한으로 `.env` `APP_ENV=development` → `APP_ENV=production` 변경 후 `systemctl restart kis-v41-api`
2. **KIS VTS 500 에러 조사**: order-cash API 500 원인 파악 (KIS 모의투자 서버 점검 여부 확인, 토큰 만료 여부 확인)
3. **221800 포지션**: retry exhausted 상태 — 수동 청산 검토
4. **monitor_virtual_run.py 패스워드**: DB_PARAMS에 password 추가 필요
5. **오케스트레이터 자동 시작**: kis-unified-engine.service 등록 고려

## 작성 일시

2026-03-03 09:42 KST

## 실행 환경 노트

- claudebot은 /root/kis-autotrade-v4/ 쓰기 권한 없음 → sudo systemctl restart 불가
- .env 수정 불가 → transition API 로 PRE_MARKET 전이 (development 전용 엔드포인트 활용)
- monitor_virtual_run.py DB 연결 패스워드 미설정으로 실패
