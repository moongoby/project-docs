---
project: KIS-AutoTrade-V4.1
task_id: CUR-V41-EMERGENCY-ENV-FIX-002
completed_at: "2026-03-03 09:58 KST"
executor: Claude Code (claudebot)
---

# CUR-V41-EMERGENCY-ENV-FIX-002 실행 결과 보고서

[인계 확인]
직전 완료: CUR-V41-DIRECTIVE-AUTOMATION-002
현재 단계: Phase 3 (Virtual Run / Live Engine 가동)
CEO 지시 적용: D-001, D-002, D-003
strategy_cards: 60
open_positions: 14

---

## 작업1: APP_ENV production 전환

**결과: 이미 production 완료 (변경 불필요)**

- `.env` 확인: `APP_ENV=production` 이미 설정됨 (변경 불필요)
- `kis-v41-api.service` 상태: `active (running)` since 2026-03-03 09:48:05 KST
  - PID 2219706, workers=2, memory=364.9M
- 오케스트레이터 상태: `IDLE` (모든 모듈 UNKNOWN)
  - PRE_MARKET 전이 시도 → **403 "development 전용"** (정상: production 모드에서는 자동 전이)
  - is_trading=false, is_buy_allowed=false
- 오케스트레이터 수동 전이 불가 (production mode에서 자동 스케줄 기반 전이 설계)
- "개발 모드" 문구 없음 ✓

**조치**: production 이미 설정됨. 오케스트레이터 IDLE 상태는 auto-transition 미동작으로 보임 — CEO 확인 필요.

---

## 작업2: KIS VTS 500 에러 조사

**결과: KIS VTS 서버 측 500 에러 확인 — 클라이언트 정상**

### 근본 원인 분석
- **토큰 상태**: 정상 (kis_configs.id=3, expires=2026-03-04 08:01, acct=50160711)
- **에러 패턴**:
  - hashkey 요청: `200 OK` ✓
  - order-cash 요청: `500 Internal Server Error` ✗
  - inquire-balance 요청: `500 Internal Server Error` ✗
- **에러 시작**: 2026-03-03 07:54부터 지속 (전일부터 이어진 것으로 보임)
- **영향 계좌**: config_id=3 (acct=50160711, 모의투자), last_err 기록됨
- **config_id=4**: acct=81201280 (is_mock=True, kis_cfg=None) — 잔고 200 OK

### 계좌 구조
- `accounts.id=1`: acct=50160711, is_mock=True, kis_cfg=3 → **VTS 500 발생**
- `accounts.id=2`: acct=50160697, is_mock=True, kis_cfg=1 → token 정상
- kis_configs.id=3: is_prod=False (VTS), last_err="500 Server Error"

### 추가 발견: json NameError
- positions 65 (419430), 66 (452260): `reason="name 'json' is not defined"`
- EXIT-DISPATCHER 내 예외 처리 → `str(e)` 기록
- 코드 상 v4_pipeline_orchestrator.py:18에 `import json` 존재 — 별도 코드 경로에서 발생 가능
- 영향: 2건 추가 실패 (전체 10건 실패 중)

### 결론
- KIS VTS API 서버 자체 500 응답 → 클라이언트 코드 이상 없음
- **CEO 조치 필요**: KIS 개발자 포털에서 acct=50160711 VTS 계좌 상태 확인 필요
- 해시키 성공 = 앱키/앱시크릿 정상 → 계좌 설정 또는 VTS 서버 점검 중 가능성

---

## 작업3: monitor_virtual_run.py DB 패스워드 수정

**결과: 부분 진단 완료 — 파일 수정 권한 부재로 코드 변경 불가**

### 진단
- `DB_PARAMS.password`: `os.getenv("DB_PASSWORD", "")` — 기본값 빈 문자열
- `.env`에 `DB_PASSWORD=KisAuto2026!Secure` 존재 → cron 실행 시 env 미로드
- 실제 테스트 시 추가 오류 발견:
  ```
  PermissionError: [Errno 13] Permission denied:
  '/root/kis-autotrade-v4/reports/daily/2026-03-03/snapshots.jsonl'
  ```
- claudebot은 `/root/kis-autotrade-v4/` 쓰기 권한 없음

### 필요 조치 (root/go100user)
1. `monitor_virtual_run.py:26`: `os.getenv("DB_PASSWORD", "KisAuto2026!Secure")`로 기본값 수정
2. 또는 cron에 `DB_PASSWORD=KisAuto2026!Secure` 추가
3. `/root/kis-autotrade-v4/reports/daily/` 디렉토리 권한 확인 (claudebot 쓰기 필요 시)

---

## 작업4: D4 Shadow 디렉토리 생성

**결과: 생성 불가 — 권한 부재**

- `/root/kis-autotrade-v4/logs/shadow/` 미존재 확인
- `/root/kis-autotrade-v4/logs/` 소유자: go100user (claudebot 쓰기 권한 없음)
- **root 또는 go100user로 실행 필요**: `mkdir -p /root/kis-autotrade-v4/logs/shadow`

---

## 작업5: Unified Engine 재실행 + 매매 확인

**결과: 엔진 정상 실행 — 3개 신호 통과**

### Engine 실행 결과 (2026-03-03 09:55:50 KST)
```
통합 엔진 시작: mode=virtual action=signal data-source=db
[SIGNAL] 신호 평가 시작
[SIGNAL] D6 691336 차단 L3.3_SUPPLY: synthetic_BLOCK
[SIGNAL] D5 341777 차단 L3.3_SUPPLY: synthetic_BLOCK
[SIGNAL] D4 209271 차단 L3.3_SUPPLY: synthetic_BLOCK
[SIGNAL] D2 822112 차단 L3.3_SUPPLY: synthetic_BLOCK
[SIGNAL] S1 356628 통과 price=130,920
[SIGNAL] D7 365103 통과 price=81,560
[SIGNAL] D-ORB 978530 통과 price=10,495
[SIGNAL] 완료: 통과=3, 차단=4
```

### DB 종합 현황 (09:57 KST)
| 항목 | 값 |
|------|-----|
| mock_trades_today | **42건** (+14 from engine run) |
| signals_today (v4_signals) | 0건 |
| positions_open | **14건** |
| positions_closed | 17건 |
| ohlcv_daily_max | 2026-02-27 |
| minute_max | 2026-03-03 |
| investor_max | 2026-02-27 |
| regime_max | 2026-02-27 |

### 엔진 프로세스
- `daily_scheduler` PID 3029739: active (root 실행)
- VTS 500 에러로 실제 주문 집행 실패 지속
- L3.3 SupplyDemandGate 정상 작동 (synthetic_BLOCK 4건)

---

## 종합 결과 (보고 형식)

**[CURSOR-KIS] ENV-FIX-002 완료**
- **작업1 APP_ENV**: production 이미 설정 완료 / 오케스트레이터: IDLE (auto-transition 미동작 — CEO 확인 필요)
- **작업2 KIS VTS**: 토큰갱신 성공 / 잔고API: 500 / 원인: KIS VTS 서버 측 500 (acct=50160711) — CEO KIS 포털 확인 필요
- **작업3 monitor DB**: 패스워드 env 이슈 + 쓰기 권한 부재 진단 / 코드 수정은 root 필요
- **작업4 shadow dir**: 생성 불가 (권한 부재) — root 직접 실행 필요
- **작업5 매매현황**: mock_trades=42건(approved 컬럼 없음), 신호=3건(S1/D7/D-ORB), DB최신=03-03(분봉)/02-27(일봉)
- **다음**: CEO VTS 계좌 점검 / root으로 shadow dir 생성 + monitor 권한 수정

---

## CEO 확인 필요 사항

1. **KIS VTS acct=50160711**: KIS 개발자 포털에서 모의투자 계좌 상태 확인
2. **오케스트레이터 IDLE**: production 모드 auto-transition 미동작 원인 확인
3. **shadow dir + monitor 권한**: root로 `mkdir -p /root/kis-autotrade-v4/logs/shadow` 실행 필요
4. **json NameError**: positions 65/66 (419430, 452260) EXIT 코드 디버깅 필요

---

## 체크포인트
- [x] 코드 레포 작업 완료 (Engine 실행, 조사 완료)
- [ ] project-docs 보고서 push (done_watcher.sh 자동 처리 예정)

HANDOVER.md 업데이트: root 권한 필요로 별도 처리 필요
