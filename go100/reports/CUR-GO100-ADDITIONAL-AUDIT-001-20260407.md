# GO100 추가 점검 항목 — 상세 체크리스트 보고서

| 항목 | 내용 |
|------|------|
| 문서 ID | CUR-GO100-ADDITIONAL-AUDIT-001 |
| 상위 보고서 | CUR-GO100-SERVICE-AUDIT-001-20260407.md §7 |
| 점검 일시 | 2026-04-07 (KST) |
| 대상 호스트 | `kis-autotrade-v4` |

본 문서는 전수 점검 보고서 **「추가 점검 항목(§7)」** 각각에 대해 **증거 수집 방법**, **실측 결과**, **권장 후속 조치**를 체크리스트 형태로 상세화한 것입니다.

---

## 7.1 `venv` vs `.venv` 이원화 — 상세 점검

### 점검 방법
- systemd 유닛 `ExecStart` 경로 확인: `/etc/systemd/system/go100*.service`
- root `crontab` 내 `venv/bin`·`.venv/bin`·`source venv`·`source .venv` 문자열 집계
- 두 디렉터리의 `pyvenv.cfg` 동일 여부, `python3` 심볼릭 타깃 확인

### 실측 결과 (체크리스트)

| # | 세부 항목 | 결과 | 증거·비고 |
|---|-----------|------|-----------|
| 7.1.1 | 물리적으로 별도 가상환경인가 | ✅ 확인 | `readlink -f`: `venv` ≠ `.venv` (서로 다른 디렉터리) |
| 7.1.2 | `pyvenv.cfg` 동일 여부 | ❌ 상이 | `diff` 결과 **다름** |
| 7.1.3 | GO100 API(`go100.service`) 인터프리터 | `venv` | `ExecStart=.../venv/bin/gunicorn` |
| 7.1.4 | GO100 스케줄러(`go100-scheduler@.service`) | `venv` | `ExecStart=.../venv/bin/python3 ... go100_scheduler.py` |
| 7.1.5 | GO100 WS(KRX/NXT) 유닛 | `venv` | `go100-ws-*.service` → `venv/bin/python3` |
| 7.1.6 | 가설 연속 데몬(`go100-hypothesis-daemon`) | `.venv` | `ExecStart=.../.venv/bin/python3 ... hypothesis_daemon.py` |
| 7.1.7 | root crontab — `.venv` 직접 호출/activate | 다수 | 샘플링상 GO100·리포트·수집 일부가 `.venv` |
| 7.1.8 | root crontab — `venv` 직접/activate | 다수 | `run_unified_engine`, 수집, 키움 갱신 등 |
| 7.1.9 | 동일 리포 내 이중 기준 운영 | ⚠️ | **한 호스트에서 두 스택 병행** → 배포·트러블슈팅 시 혼선·재현 난이도 증가 |

### 권장 조치
- **단일 소스 오브 트루스**: 운영 표준을 `venv` 또는 `.venv` 하나로 정하고, systemd·cron·문서를 일괄 정렬.
- **검증 커맨드**: 표준 venv로 `python -c "import numpy, pandas; print('ok')"` 를 배포 체크에 포함.

---

## 7.2 `.venv` NumPy / Pandas 스택 — 상세 점검

### 점검 방법
- `pip show numpy pandas` (각 venv)
- `python -c "import numpy"` (각 venv)

### 실측 결과 (체크리스트)

| # | 세부 항목 | 결과 | 증거·비고 |
|---|-----------|------|-----------|
| 7.2.1 | `venv` NumPy 버전 | ✅ | **1.26.4** |
| 7.2.2 | `venv` Pandas 버전 | ✅ | **2.3.3** |
| 7.2.3 | `venv` `import numpy` | ✅ | (이전 점검과 일치, 과학 스택 정상 조합) |
| 7.2.4 | `.venv` NumPy 버전 | ⚠️ | **2.2.6** |
| 7.2.5 | `.venv` Pandas 버전 | ⚠️ | **3.0.1** |
| 7.2.6 | `.venv` `import numpy` | ❌ | `ImportError: cannot import name 'linalg' from partially initialized module 'numpy.linalg'` (순환 초기화) |
| 7.2.7 | 영향 범위 | 🔴 | `.venv`를 쓰는 **크론·`start_bt_daemon.sh`·가설 데몬 자식 프로세스**는 pandas/numpy 의존 코드에서 **즉시 실패** 가능 |
| 7.2.8 | API 프로세스 | ✅ | Gunicorn은 `venv` 기반 → **API 자체는 본 이슈와 분리** |

### 권장 조치
- `.venv`에서 NumPy/Pandas **재설치 또는 `venv`와 동일 메이저/마이너로 고정** (예: numpy 1.26.x + pandas 2.x 검증된 조합).
- 설치 후: `run_live_trading.sh` / `run_paper_trading.sh` / `paper_trading_daily.py` / 백테 데몬 **수동 1회 실행으로 스모크**.

---

## 7.3 `go100_live_daily_summary` / `portfolio_id` — 상세 점검

### 점검 방법
- PostgreSQL: `\d go100_live_daily_summary` (DB `kisautotrade`)
- 코드베이스: `go100_live_daily_summary` 참조 검색

### 실측 결과 (체크리스트)

| # | 세부 항목 | 결과 | 증거·비고 |
|---|-----------|------|-----------|
| 7.3.1 | 테이블 존재 | ✅ | `kisautotrade` 내 조회 성공 |
| 7.3.2 | 컬럼 `portfolio_id` 존재 | ❌ | 실제 컬럼: `summary_id`, `user_id`, `summary_date`, `total_orders`, `total_buy_amount`, `total_sell_amount`, `realized_pnl`, `realized_pnl_pct`, `is_circuit_broken`, `created_at` |
| 7.3.3 | 앱 코드 UPSERT 키 | `user_id` + `summary_date` | `backend/app/services/go100/ai/live_trading.py` 의 `INSERT ... ON CONFLICT (user_id, summary_date)` |
| 7.3.4 | 리스크 에이전트 등 조회 | `user_id` 기준 | `risk_agent.py`, `live_trading.py` 등은 **`user_id`·`summary_date`** 조합 사용 |
| 7.3.5 | 과거 journal의 `WHERE portfolio_id` 오류 | ⚠️ | **현재 워크스페이스 트리에서는 해당 SQL 문자열 미검색** — 배포 리비전 불일치·동적 SQL·미커밋 코드 가능성. DB에 컬럼 없음은 **확정**이므로, 해당 쿼리가 남아 있으면 **런타임 재발** |

### 권장 조치
- 운영 중인 `live_engine`/스케줄러 바이너리(또는 배포 브랜치)에서 `go100_live_daily_summary` + `portfolio_id` 문자열 **재검색**.
- 설계 선택: (A) `portfolio_id` 컬럼 추가 + 마이그레이션, 또는 (B) 쿼리를 `user_id`(+포트폴리오 매핑)로 통일.

---

## 7.4 DB 연결 상한·PgBouncer — 상세 점검

### 점검 방법
- `show max_connections;`, `pg_stat_activity` 카운트
- `/etc/pgbouncer/pgbouncer.ini` 주요 풀 파라미터

### 실측 결과 (체크리스트)

| # | 세부 항목 | 결과 | 증거·비고 |
|---|-----------|------|-----------|
| 7.4.1 | PostgreSQL `max_connections` | 100 | `psql -tAc "show max_connections;"` |
| 7.4.2 | 샘플 시점 `pg_stat_activity` 수 | 9 | 피크 아님 — **저부하 스냅샷** |
| 7.4.3 | PgBouncer `pool_mode` | transaction | 트랜잭션 단위 풀링 |
| 7.4.4 | `max_client_conn` | 200 | 클라이언트 최대 접속 |
| 7.4.5 | `default_pool_size` | 20 | DB 쪽 기본 연결 풀 |
| 7.4.6 | `reserve_pool_size` | 5 | 예비 풀 |
| 7.4.7 | 과거 `TooManyConnectionsError` | ⚠️ | `go100-scheduler@reconcile` (2026-04-06) — **Postgres 슬롯 고갈** 이력 |
| 7.4.8 | 원인 가설 | ℹ️ | Gunicorn 워커·다수 앱·직접 5432 접속·마이그레이션 등이 동시에 붙으면 PgBouncer를 우회한 연결이 `max_connections`를 소모할 수 있음 |

### 권장 조치
- 장중 피크에 `pg_stat_activity`·`pgbouncer` `SHOW POOLS` / `SHOW STATS` 스냅샷 수집.
- 애플리케이션 `DATABASE_URL`이 **6432(PgBouncer)** 인지, 배치만 직접 5432인지 **역할별 표준화**.
- 필요 시 `max_connections`·풀 크기·워커 수 **연동 튜닝 표** 작성.

---

## 7.5 스케줄러 실패 알림 — 상세 점검

### 점검 방법
- `go100-scheduler@.service` 내 `OnFailure=` / `OnSuccess=` 여부
- `go100_scheduler.py` 내 텔레그램·외부 알림 호출 여부

### 실측 결과 (체크리스트)

| # | 세부 항목 | 결과 | 증거·비고 |
|---|-----------|------|-----------|
| 7.5.1 | systemd `OnFailure` | ❌ | `go100-scheduler@.service`에 **미설정** |
| 7.5.2 | 스케줄러 내 Telegram 연동 | ❌ | `go100_scheduler.py`는 **logger / print 중심**, 실패 시 외부 알림 없음 |
| 7.5.3 | 타 스크립트의 Telegram | ℹ️ | `strategy_promotion_engine.py`, `virtual_hourly_report.py`, `watch_*.sh` 등 **별도 배치**에만 존재 — **스케줄러 실패와 연동되지 않음** |

### 권장 조치
- `OnFailure=go100-alert@.service` 패턴 또는 실패 시 `curl` 텔레그램 래퍼 유닛.
- 또는 `go100_scheduler.py` 최상위 `except`에서 공통 알림 함수 호출(중복 알림 방지 정책 포함).

---

## 7.6 키움 토큰 갱신 크론 — 상세 점검

### 점검 방법
- `scripts/cron/refresh_kiwoom_tokens.sh` 내용
- 실제 로그: `logs/cron/kiwoom_token_YYYYMMDD.log` 및 crontab 리다이렉트 대상

### 실측 결과 (체크리스트)

| # | 세부 항목 | 결과 | 증거·비고 |
|---|-----------|------|-----------|
| 7.6.1 | 스크립트 인터프리터 | `venv` | `.../venv/bin/python scripts/refresh_kiwoom_tokens.py` |
| 7.6.2 | 로그 출력 위치 | `logs/cron/kiwoom_token_$(date +%Y%m%d).log` | 스크립트 내부 `LOG_FILE` |
| 7.6.3 | `/var/log/go100/kiwoom_token_refresh.log` | ⚠️ | **0바이트** — crontab이 여기로 리다이렉트해도 스크립트가 표준출력에 거의 안 씀 → **빈 파일은 정상일 수 있음** |
| 7.6.4 | 당일(2026-04-07) 갱신 로그 | ✅ | `kiwoom_token_20260407.log`에 **3/3 success**, 계정별 만료 시각 기록 |
| 7.6.5 | 기능 판정 | ✅ | 토큰 갱신 파이프라인 **정상 동작** (검증 시점 기준) |

### 권장 조치
- 모니터링은 **`logs/cron/kiwoom_token_*.log`** 기준으로 통일하거나, 스크립트 마지막에 `echo` 한 줄을 stdout에 남겨 통합 로그에도 흔적 남기기.

---

## 7.7 레거시 `/root/webapp/backend` (paper_trade_analyzer 등) — 상세 점검

### 점검 방법
- 경로·모듈 존재
- 해당 venv에서 `numpy`/`pandas` import

### 실측 결과 (체크리스트)

| # | 세부 항목 | 결과 | 증거·비고 |
|---|-----------|------|-----------|
| 7.7.1 | `paper_trade_analyzer.py` 존재 | ✅ | `/root/webapp/backend/app/services/go100/paper_trade_analyzer.py` |
| 7.7.2 | `webapp/backend/venv` 과학 스택 | ✅ | `import numpy, pandas` **성공** (경고: pandas 3.0 에서 pyarrow 권고) |
| 7.7.3 | crontab 의존성 | ℹ️ | 평일 15:30 `python3 -m app.services.go100.paper_trade_analyzer` — **kis-autotrade-v4와 별도 코드베이스** |
| 7.7.4 | 운영 리스크 | ⚠️ | **이중 트랙**: GO100 메인은 `kis-autotrade-v4`, 분석 일부는 `webapp` — 버전·스키마·환경변수 **드리프트** 가능 |

### 권장 조치
- 장기적으로 분석 모듈을 모노리포로 편입하거나, 최소한 **동일 DB 마이그레이션 파이프라인** 문서화.

---

## 7.8 KIS V4.1 API (포트 8003) — 상세 점검

### 점검 방법
- `systemctl is-active kis-v41-api.service`
- `curl` 로컬 헬스

### 실측 결과 (체크리스트)

| # | 세부 항목 | 결과 | 증거·비고 |
|---|-----------|------|-----------|
| 7.8.1 | `kis-v41-api.service` | ✅ | active |
| 7.8.2 | `GET http://127.0.0.1:8003/health` | ✅ | **HTTP 200** |
| 7.8.3 | `GET .../api/v1/health` | ℹ️ | **404** (엔드포인트 미정의 가능) |
| 7.8.4 | `/docs` | ✅ | **200** |
| 7.8.5 | 레거시 `kis-webapp-api` | ✅ | active (별도 플랫폼) |

### 권장 조치
- 모니터링 URL을 `/health`로 표준화해 알람 설정.

---

## 7.9 `security_scan.sh` / `path_check.sh` — 상세 점검

### 점검 방법
- 스크립트 위치: `/root/project-docs/scripts/`
- 실행: `security_scan.sh`, `path_check.sh` (인자 동작은 스크립트 본문 기준)

### 실측 결과 (체크리스트)

| # | 세부 항목 | 결과 | 증거·비고 |
|---|-----------|------|-----------|
| 7.9.1 | `security_scan.sh` 존재 | ✅ | `/root/project-docs/scripts/security_scan.sh` |
| 7.9.2 | 스캔 대상 ROOT | ⚠️ | 스크립트 기본값은 **스크립트 상위(`project-docs`) 트리** — 인자로 `kis-autotrade-v4`만 좁히는 로직은 **본문 상단에 없음** |
| 7.9.3 | 샘플 실행 결과 | ❌ FAIL | 과거 보고서·타 프로젝트 md에 **DB URL·비밀번호 패턴** 검출 (project-docs 내) |
| 7.9.4 | `path_check.sh` 존재 | ✅ | `/root/project-docs/scripts/path_check.sh` |
| 7.9.5 | `path_check` 대상 `/root/kis-autotrade-v4` | ❌ | **「프로젝트 식별 불가」** — 경로명이 `CUR-*` 접두 규칙과 맞지 않아 스크립트가 거부 |
| 7.9.6 | 해석 | ℹ️ | **현재 스크립트는 이 서버 레이아웃과 완전히 맞지 않음** — kis 저장소 전용 래퍼 또는 스크립트 개정 필요 |

### 권장 조치
- `security_scan.sh`에 `REPO_DIR` 인자 지원 추가 또는 `kis-autotrade-v4` 전용 `security_scan_kis.sh` 분리.
- `path_check.sh`에 `kis-autotrade-v4` 화이트리스트 추가 또는 심볼릭 링크 `CUR-KIS-V41-REPO` 등 규칙 부합 경로 사용.

---

## 부록: 통합 요약 표

| § | 주제 | 심각도 | 한 줄 결론 |
|---|------|--------|------------|
| 7.1 | 이중 venv | 높음 | systemd는 주로 `venv`, 가설 데몬·다수 크론은 `.venv` — 운영 기준 미통일 |
| 7.2 | `.venv` numpy | **치명** | `.venv`에서 numpy import 실패 — pandas 의존 배치 광범위 장애 가능 |
| 7.3 | daily_summary 스키마 | 높음 | DB에 `portfolio_id` 없음; 코드는 user 단위; journal 오류는 리비전 추적 필요 |
| 7.4 | 연결 풀 | 중간 | 평시 여유, 피크 시 슬롯 고갈 이력 — PgBouncer·직접접속 역할 정리 |
| 7.5 | 스케줄 알림 | 중간 | systemd/스케줄러에 실패 알림 없음 |
| 7.6 | 키움 토큰 | 낮음(양호) | 당일 로그 정상; 통합 로그 파일은 오해 소지 |
| 7.7 | webapp 레거시 | 중간 | 모듈·venv 정상, 아키텍처 이원화 리스크 |
| 7.8 | KIS 8003 | 낮음(양호) | `/health` 200 |
| 7.9 | 보안/경로 스크립트 | 정보 | project-docs 기준 설계; kis 경로 단독 검증에는 부적합 |

---

*본 보고서는 2026-04-07 런타임 스냅샷 기준이며, 장중 부하·배포 변경 후에는 수치가 달라질 수 있습니다.*
