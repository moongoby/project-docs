# GO100 서비스 가동 전수 점검 보고서

| 항목 | 내용 |
|------|------|
| 문서 ID | CUR-GO100-SERVICE-AUDIT-001 |
| 점검 일시 | 2026-04-07 (KST, 서버 로컬 시각 기준) |
| 대상 호스트 | `kis-autotrade-v4` (uptime 약 33일) |
| 점검 범위 | systemd, 프로세스, 로컬/공개 HTTP, DB·Redis, 스케줄러·크론, 이중 venv 이슈 |

---

## 1. 서버·인프라 상태

| # | 점검 항목 | 결과 | 비고 |
|---|-----------|------|------|
| 1.1 | 호스트 가동 | ✅ | 부하 평균 약 6.6 전후 — 상시 워크로드 대비 다소 높음, 지속 모니터 권장 |
| 1.2 | 루트 디스크 | ⚠️ | `/` 사용률 약 **77%** (여유 ~23GB) — 로그·백업 증가 시 정리 계획 권장 |
| 1.3 | 메모리 | ✅ | 가용 메모리 여유 있음(Swap 미사용) |
| 1.4 | `postgresql@16-main` | ✅ | active (running) |
| 1.5 | `postgresql.service` (메타 유닛) | ℹ️ | active (exited) — 클러스터 유닛이 실제 DB |
| 1.6 | `pgbouncer` | ✅ | active, 통계상 고빈도 트래픽 |
| 1.7 | `redis-server` | ✅ | active, `127.0.0.1:6379` LISTEN |
| 1.8 | `nginx` | ✅ | active |
| 1.9 | PostgreSQL 연결 수 | ✅ | 샘플 시점 **13** / `max_connections` **100** — 현재 여유 |
| 1.10 | 과거 연결 포화 이력 | ⚠️ | `go100-scheduler@reconcile` 실패 로그에 `TooManyConnectionsError` (2026-04-06) — **피크 시간대 풀·PgBouncer·앱 워커 수 재검토 필요** |

---

## 2. GO100 코어 서비스 (API·프론트·리버스 프록시)

| # | 점검 항목 | 결과 | 비고 |
|---|-----------|------|------|
| 2.1 | `go100.service` (Gunicorn) | ✅ | active (running), `127.0.0.1:8002` LISTEN |
| 2.2 | API 헬스 | ✅ | `GET http://127.0.0.1:8002/api/v1/go100/monitor/health` → **HTTP 200**, 본문: `status=ok`, `database=connected`, `redis=connected` |
| 2.3 | 공개 도메인 | ✅ | `https://go100.newtalk.kr/health` → **200**, `/` → **200** |
| 2.4 | Nginx 업스트림 | ✅ | `sites-enabled/go100`: backend `8002`, frontend `3000`, `server_name go100.newtalk.kr` |
| 2.5 | `go100-frontend.service` (Next.js 14) | ✅ | active, `0.0.0.0:3000` LISTEN |
| 2.6 | 로컬 프론트 루트 | ✅ | `http://127.0.0.1:3000/` → **200** |
| 2.7 | 프론트 `/api/health` | ℹ️ | **404** — 별도 헬스 라우트 없을 수 있음, 백엔드 `/health`는 Nginx에서 프록시됨 |

---

## 3. 엔진·데이터 파이프라인 (상세)

### 3.1 가설·연구 엔진

| # | 점검 항목 | 결과 | 비고 |
|---|-----------|------|------|
| 3.1.1 | `go100-hypothesis-daemon.service` | ✅ | active (running), `.venv/bin/python3 hypothesis_daemon.py` |
| 3.1.2 | 장시간 백테스트 워커 프로세스 | ✅ | `run_hypothesis_backtest.py` 프로세스 존재 (PID 관찰) |
| 3.1.3 | 크론: 가설 파이프라인·워치독 | ✅ | `hypothesis_watchdog.sh`, `run_hypothesis_pipeline.sh` 등 등록됨 |
| 3.1.4 | **`.venv` NumPy/Pandas** | ❌ | 동일 환경에서 `import numpy` **실패**(순환 import/`linalg` 등). **가설 데몬·백테 데몬이 `.venv` 기반이면 실질 작업 루프 장애 위험** — `venv`와 정합성 조치 필요 (아래 7장) |

### 3.2 백테스트 엔진

| # | 점검 항목 | 결과 | 비고 |
|---|-----------|------|------|
| 3.2.1 | `bt_daemon_watchdog.sh` (5분) | ✅ | crontab 등록됨 |
| 3.2.2 | `start_bt_daemon.sh` | ⚠️ | `.venv` 활성화 후 `run_hypothesis_backtest.py` 기동 — **3.1.4와 동일 리스크** |
| 3.2.3 | API 백테스트 라우터 | ✅ | 앱 기동 중(`main.py`에 `go100_backtest_router` 등록) |

### 3.3 페이퍼(실데이터 가상매매) 엔진

| # | 점검 항목 | 결과 | 비고 |
|---|-----------|------|------|
| 3.3.1 | `go100-scheduler@paper.service` | ❌ | **failed** (2026-04-06 18:02) — 로그: DB 연결 중단 `ConnectionDoesNotExistError` |
| 3.3.2 | 크론 `run_paper_trading.sh` 등 | ⚠️ | 등록됨. `/var/log/go100/paper.log` 등에 **pandas/numpy ImportError(.venv)** 흔적 — **크론 경로와 가상환경 불일치 의심** |
| 3.3.3 | systemd timer | ℹ️ | `go100-scheduler@paper.timer` 다음 실행 스케줄 존재 — **직전 실행 실패 상태 유지** |

### 3.4 실매매(Live) 엔진

| # | 점검 항목 | 결과 | 비고 |
|---|-----------|------|------|
| 3.4.1 | `go100-scheduler@live.service` | ✅ (마지막 런) | 2026-04-06 09:10경 **성공 종료**(journal). Kiwoom API 200 응답·체결 확인 로그 존재 |
| 3.4.2 | 실매매 로직 경고 | ⚠️ | 동일 로그에 `go100_live_daily_summary`에 **`portfolio_id` 컬럼 없음** → Arbiter 쿼리 `ProgrammingError` 다건 — **스키마·마이그레이션 미적용 또는 코드·DB 불일치** |
| 3.4.3 | 증거금 오류 | ℹ️ | 일부 포트폴리오에서 매수 실패(증거금 부족 코드) — 비즈니스/설정 이슈로 구분 |
| 3.4.4 | 크론 `run_live_trading.sh` | ⚠️ | **`.venv`** 사용. `/var/log/go100/live_trading.log` 최종 갱신 2026-04-06, 내용 **numpy ImportError** — **systemd 타이머( `venv` )는 동작했으나 크론 기반 실매매는 실패 가능성 큼** |

### 3.5 리콘실(Reconcile)·리포트 스케줄러

| # | 점검 항목 | 결과 | 비고 |
|---|-----------|------|------|
| 3.5.1 | `go100-scheduler@reconcile.service` | ❌ | **failed** (2026-04-06 15:40) — `TooManyConnectionsError` |
| 3.5.2 | `go100-scheduler@report.service` | ℹ️ | oneshot, 마지막 관찰 시점 inactive(dead) — 타이머는 등록됨 |

### 3.6 시세·WebSocket 수집 (KRX / NXT)

| # | 점검 항목 | 결과 | 비고 |
|---|-----------|------|------|
| 3.6.1 | `go100-ws-nxt-am.service` | ✅ | 점검 시각 기준 **active** — NXT 오전 윈도우 정책과 부합 가능 |
| 3.6.2 | `go100-ws-nxt.service` | ℹ️ | inactive — crontab상 오후 15:40~20:00 운용, 20:00 stop |
| 3.6.3 | `go100-ws-krx.service` | ℹ️ | inactive — 평일 07:50 start 등 크론 기반 |

### 3.7 부가 배치·운영 스크립트 (크론 샘플)

| # | 점검 항목 | 결과 | 비고 |
|---|-----------|------|------|
| 3.7.1 | `run_health_monitor.sh` / `health_monitor.py` | ✅ | 5분 주기 crontab |
| 3.7.2 | `run_alert_sender.sh` | ✅ | 1분 주기 |
| 3.7.3 | `run_data_integrity_check.sh` | ✅ | 장중/장외 주기 상이 |
| 3.7.4 | 조건검색 수집 | ✅ | 5분마다 `localhost:8002/api/go100/conditions/collect` POST (로그 대상) |
| 3.7.5 | `aads-pipeline-runner.service` | ✅ | active |
| 3.7.6 | `genspark-bridge.service` | ℹ️ | **inactive (dead)** — CEO 브리지 자동화가 이 인스턴스에 필요하면 별도 기동 정책 확인 |

---

## 4. 회원·인증 관련

| # | 점검 항목 | 결과 | 비고 |
|---|-----------|------|------|
| 4.1 | `GET /api/go100/me` (무인증) | ✅ | **HTTP 401** — 인증 미제공 시 거절(정상 패턴) |
| 4.2 | API 가용성 | ✅ | 동일 프로세스에서 라우팅 응답 확인 |
| 4.3 | DB 연결 | ✅ | 모니터 헬스에서 `database: connected` |

*(실제 가입 수·토큰 발급량은 DB/메트릭 쿼리가 필요하며 본 점검에서는 API 거동만 확인.)*

---

## 5. 백억이(GO100 AI) 상태

| # | 점검 항목 | 결과 | 비고 |
|---|-----------|------|------|
| 5.1 | API 모듈 | ✅ | `ai_router.py` — 태그 `GO100 AI (백억이)`, prefix `/api/go100/ai` |
| 5.2 | 프로세스 | ✅ | 별도 데몬 없이 **go100 Gunicorn 워커**에서 제공 |
| 5.3 | 의존성 | ⚠️ | LLM·외부 연동은 호출 시점에서만 검증 가능 — **엔드포인트별 스모크는 인증·쿼터 필요** |

---

## 6. 프론트엔드 상태 (요약)

| # | 점검 항목 | 결과 | 비고 |
|---|-----------|------|------|
| 6.1 | systemd | ✅ | `go100-frontend` active |
| 6.2 | HTTP | ✅ | 로컬·공개 도메인 200 |
| 6.3 | 런타임 로그 | ⚠️ | journal에 2026-04-06 **Next.js app-page 스택** 흔적 — 특정 경로 SSR/라우팅 이슈 가능, 재현 URL 추적 권장 |

---

## 7. 추가 점검 항목 (권장 체크리스트)

| # | 항목 | 이번 점검 | 권장 조치 |
|---|------|-----------|-----------|
| 7.1 | **`venv` vs `.venv` 이원화** | ⚠️ 확인됨 | Gunicorn·scheduler는 `venv`, 다수 크론·가설 데몬은 `.venv`. **한쪽으로 통일 또는 심볼릭/동기화** |
| 7.2 | **`.venv` NumPy/Pandas 복구** | ❌ 실패 재현 | `pip install`/`numpy` 재설치 또는 venv 클론 후 크론 전수 검증 |
| 7.3 | **`go100_live_daily_summary.portfolio_id`** | ❌ 쿼리 오류 로그 | 마이그레이션 적용 또는 쿼리 수정 |
| 7.4 | **DB 연결 상한** | ⚠️ 이력 | PgBouncer 풀·앱 동시 연결·Postgres `max_connections` 정합성 |
| 7.5 | **스케줄러 실패 알림** | ℹ️ | paper/reconcile 실패 시 텔레그램/온콜 연계 여부 |
| 7.6 | **키움 토큰 크론** | ✅ 등록 | `refresh_kiwoom_tokens.sh` — 로그 정상 여부 주기 확인 |
| 7.7 | **레거시 경로** | ℹ️ | crontab에 `/root/webapp/backend` `paper_trade_analyzer` — 해당 경로 존재 확인됨, **의존 venv 분리 주의** |
| 7.8 | **KIS V4.1 API** (`8003`) | ✅ | 별도 서비스 `kis-v41-api` — GO100과 포트 분리 유지 |
| 7.9 | **보안 스캔·배포 관행** | — | 저장소 푸시 전 `security_scan.sh` / `path_check.sh` (프로젝트 규칙) |

---

## 8. 종합 의견

- **사용자 대면 가용성**: GO100 API·프론트·공개 HTTPS·DB·Redis는 **정상**으로 판단됩니다.
- **자동매매·스케줄 계층**: **paper / reconcile 스케줄러는 최근 실패 상태**이며, **live는 타이머 실행은 성공했으나 DB 스키마 오류와 이중 venv로 인한 크론 실패 위험**이 큽니다.
- **최우선 조치 제안**: (1) `.venv` 과학 스택 복구 및 크론·데몬 실행 인터프리터 통일, (2) `go100_live_daily_summary`와 코드 정합성, (3) 연결 수 피크 대비 PgBouncer/풀 튜닝.

---

*본 보고는 서버 `kis-autotrade-v4`에서 수집한 런타임 스냅샷·로그 기준이며, 장중/장마감 후 재점검 시 일부 서비스 활성 상태가 달라질 수 있습니다.*
