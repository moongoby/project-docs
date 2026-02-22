# MONDAY-PRECHECK 결과 (월요일 장 전 활성화 사전 점검)

**서버:** 211.188.51.113  
**경로:** /root/kis-autotrade-v4  
**점검일시:** 2026-02-22 (일)

---

## 사전 확인 (필수) 결과

| 항목 | 기준값 | 실제 | 결과 |
|------|--------|------|------|
| strategy_cards COUNT | 59 | 59 | ✓ |
| v4_positions OPEN | 5 | 5 | ✓ |
| kis-v41-api | active | active (running) | ✓ |
| kis-v41-monitor | active | active (running) | ✓ |
| kis-v41-scheduler | active | active (running) | ✓ |
| df -h / | - | 56G Avail, 42% 사용 | ✓ |

→ 기준과 일치하여 점검 계속 진행함.

---

## [분봉 수집기] kis-v41-minute-collector

| 항목 | 결과 |
|------|------|
| **서비스 파일** | 존재 **Y** (`/etc/systemd/system/kis-v41-minute-collector.service`) |
| **ExecStart** | `/root/kis-autotrade-v4/venv/bin/python -m backend.app.services.data_pipeline.collector_minute` |
| **WorkingDirectory** | `/root/kis-autotrade-v4` |
| **User** | root |
| **환경변수** | `EnvironmentFile=/root/kis-autotrade-v4/.env`, PYTHONPATH 설정됨 |
| **ExecStart 스크립트** | 존재 **Y** (`backend/app/services/data_pipeline/collector_minute.py`), 문법검증 **PASS** |
| **KIS API 토큰 키** | 존재 **Y** (.env에 KIS_APP_KEY, KIS_APP_SECRET 등 키 존재 확인, 값 미출력) |
| **v4_ohlcv_minute 최신 데이터** | `trade_date=2026-02-19`, `trade_time=16:00:00` (건수 19,468,781) |
| **이전 실행 에러** | **있음.** 2026-02-21 15:34 경 로그: "초당 거래건수를 초과하였습니다.", "토큰 재발급 쿨다운 중" 등 WARNING 다수. 동일일 15:34:11 서비스 Stopped(Deactivated). 치명적 크래시는 없고, API rate limit 및 쿨다운 동작으로 보임. |
| **월요일 활성화 준비** | **가능.** (서비스/스크립트/테이블/토큰 준비 완료. 활성화 시 API 초당 제한 고려 필요) |

---

## [호가 수집기] kis-v41-orderbook-collector

| 항목 | 결과 |
|------|------|
| **서비스 파일** | 존재 **Y** (`/etc/systemd/system/kis-v41-orderbook-collector.service`, DESK1-DATA에서 생성) |
| **ExecStart** | `/root/kis-autotrade-v4/venv/bin/python scripts/collection/orderbook_collector.py` |
| **WorkingDirectory** | `/root/kis-autotrade-v4` |
| **User** | root |
| **환경변수** | PYTHONPATH만 설정. EnvironmentFile 없음. (스크립트 내부에서 `load_dotenv(.env)` 로드함) |
| **ExecStart 스크립트** | 존재 **Y** (`scripts/collection/orderbook_collector.py`), 문법검증 **PASS** |
| **v4_orderbook_realtime 테이블** | 존재 **Y** (구조 확인됨) |
| **v4_scalping_universe 테이블** | 존재 **Y** (구조 확인됨) |
| **월요일 활성화 준비** | **가능.** (서비스/스크립트/테이블 모두 준비 완료) |

---

## [환경]

| 항목 | 결과 |
|------|------|
| **2026-02-23 거래일 여부** | **Y** (월요일. v4_market_calendar에 2026-02-23 당일 이벤트 없음 → 정상 거래일로 판단) |
| **시스템 시간** | Sun 2026-02-22 01:20:02 KST (Asia/Seoul), NTP 동기화됨 |
| **디스크 여유** | 56G Avail (/) |
| **메모리 여유** | Mem: 15Gi total, 4.5Gi available; Swap: 8Gi total, 3.1Gi free |

---

## 최종 확인값

- **strategy_cards COUNT:** 59 ✓  
- **v4_positions OPEN:** 5 ✓  
- **이슈 사항:** 분봉 수집기 과거 로그에 API "초당 거래건수 초과" 및 토큰 쿨다운 WARNING 있음. 월요일 활성화 시 rate limit 설정/모니터링 권장. 그 외 **없음.**

---

**※ 이 작업은 읽기 전용 점검이다. 서비스 활성화(start/enable) 및 DB/파일 수정은 수행하지 않음.**
