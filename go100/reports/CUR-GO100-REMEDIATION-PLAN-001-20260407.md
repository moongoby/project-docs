# GO100 수정 조치 계획 및 광범위 영향 분석

| 항목 | 내용 |
|------|------|
| 문서 ID | CUR-GO100-REMEDIATION-PLAN-001 |
| 기준 문서 | CUR-GO100-SERVICE-AUDIT-001-20260407, CUR-GO100-ADDITIONAL-AUDIT-001-20260407 |
| 작성일 | 2026-04-07 (KST) |
| 대상 | 서버 `kis-autotrade-v4`, 리포 `/root/kis-autotrade-v4` |

---

## 1. 요약: 우선순위·의존 관계

| 우선순위 | 조치 묶음 | 선행 조건 | 비고 |
|----------|-----------|-----------|------|
| **P0** | 가상환경 정합성 (`.venv` NumPy 복구 **또는** 전 구간 `venv` 통일) | 없음 | 크론·백테·페이퍼·실매매 크론 직결 |
| **P0** | 스케줄러(paper/reconcile) 재검증 | P0 가상환경 | 실패 원인이 DB 순간 장애만이면 재실행으로 종료 가능 |
| **P1** | DB 연결·풀 정책 정리 | P0 이후 권장 | 연결 폭주 시 재발 방지 |
| **P1** | `go100_live_daily_summary` vs 운영 코드 정합성 | 스키마/배포 리비전 확인 | 제품 설계(유저 단위 vs 포트폴리오 단위) 결정 필요 |
| **P2** | 스케줄 실패 알림(systemd/텔레그램) | 없음 | 운영 가시성 |
| **P2** | 키움 로그 경로·모니터링 문서화 | 없음 | 오탐 방지 |
| **P3** | `webapp` 레거시 이원화 해소 | 장기 | 아키텍처 |
| **P3** | `security_scan`/`path_check` kis용 래퍼 | 없음 | 개발 규정 준수 |

**권장 실행 순서:** P0-1(인터프리터·패키지) → P0-2(스케줄러 스모크) → P1(DB) → P1(스키마/코드) → P2(알림) → P3.

---

## 2. P0 — 가상환경 (`.venv` / `venv`) 정합성

### 2.1 문제 정의
- `go100.service`(Gunicorn)와 `go100-scheduler@.service`는 **`venv`** 사용.
- 다수 크론·`start_bt_daemon.sh`·`go100-hypothesis-daemon`은 **`.venv`** 사용.
- `.venv`에서 **`import numpy` 실패**(NumPy 2.2.x 초기화 오류). Pandas 3.0.1이 동일 환경에 설치됨.
- 결과: **`.venv`로 도는 GO100 배치는 pandas 경로 진입 시 전부 실패**할 수 있음.

### 2.2 조치 계획 (택일 후 일관 적용)

#### 방안 A — 표준을 `venv`로 통일 (권장: 이미 API·스케줄러와 동일)

| 단계 | 작업 | 담당/도구 |
|------|------|-----------|
| A-1 | **인벤토리**: `crontab -l`, `/etc/systemd/system/go100*.service`, `scripts/go100/*.sh` 에서 `.venv` 참조 목록화 | 운영 |
| A-2 | **일괄 치환**: GO100·KIS 공용 크론에서 `.venv` → `venv` (또는 `source venv/bin/activate` 고정) | sed/패치 + 리뷰 |
| A-3 | **`go100-hypothesis-daemon.service`**: `ExecStart`를 `venv/bin/python3`로 변경 후 `daemon-reload` + 재시작 | systemd |
| A-4 | **`start_bt_daemon.sh`**: `source venv/bin/activate` + `venv/bin/python` 명시 | 스크립트 |
| A-5 | **스모크**: `venv/bin/python -c "import numpy,pandas; …"` , `run_paper_trading.sh` dry-run 가능 시 1회, 백테 데몬 1회 | 셸 |
| A-6 | **롤백**: git으로 crontab 백업·유닛 `.bak` 복구 | 운영 |

#### 방안 B — 표준을 `.venv`로 두고 패키지 복구

| 단계 | 작업 |
|------|------|
| B-1 | `.venv`에서 numpy/pandas **검증된 조합**으로 재설치 (예: API와 동일하게 **numpy 1.26.x + pandas 2.3.x** 로 맞추기) |
| B-2 | `go100.service` / `go100-scheduler@.service` / WS 유닛을 **`.venv`로 변경** — **API 재시작 필수**, 영향 범위 최대 |
| B-3 | Gunicorn 워커 재기동 후 전 API 스모크 |

**권장:** **방안 A** — 이미 운영 중인 API·타이머 스케줄러와 동일 `venv`로 맞추면 검증 단위가 하나로 줄어듦.

### 2.3 광범위 영향 분석 (P0)

| 영역 | 영향 | 완화 |
|------|------|------|
| **GO100 API** | 방안 B 시 **직접 영향** (워커 재시작, 짧은 502 가능) | 방안 A면 API 유닛 **변경 없음** |
| **장중 크론** | 치환 직후 다음 분에 **다른 인터프리터**로 실행 → 동작 변경·로그 경로 동일 | 장전/야간 윈도우에 배포 |
| **가설·백테** | 재시작 시 **큐/잡 상태** 초기화 가능 | 데몬 graceful stop 후 기동 |
| **비-GO100 크론** | 동일 crontab에 `.venv` 쓰는 **desk/unified 엔진** 등 **의도치 않은 치환 위험** | **GO100 관련 라인만** 선별 패치 (전역 replace 금지) |
| **퍼미션** | `venv` 소유 `go100user` 등일 경우 root 크론과 충돌 가능 | `ls -la venv` 확인 |
| **롤백** | 크롩 백업 파일 + `systemctl cat` 스냅샷 | 즉시 복구 가능 |

---

## 3. P0 — 스케줄러 `paper` / `reconcile` 실패 후속

### 3.1 문제 정의
- `go100-scheduler@paper`: `ConnectionDoesNotExistError` (중간 연결 끊김).
- `go100-scheduler@reconcile`: `TooManyConnectionsError` (Postgres 슈퍼유저 예약 슬롯 메시지).

### 3.2 조치 계획

| 단계 | 작업 |
|------|------|
| S-1 | P0 가상환경 조치 후 `systemctl start go100-scheduler@paper` / `@reconcile` **수동 1회** |
| S-2 | 실패 시 `journalctl -u go100-scheduler@paper -n 80` 재확인 — **numpy 오류 재등장 시 P0 미완료** |
| S-3 | 연결 오류만이면 **P1(풀·동시 실행)** 과 병행 |

### 3.3 광범위 영향 분석

| 영역 | 영향 |
|------|------|
| **페이퍼 포트폴리오** | 수동 실행 시 **당일 가상매매 배치**가 한 번에 돌아감 — 중복 실행 방지를 위해 타이머와 **시간 겹침 없이** 실행 |
| **리콘실** | 브로커·DB 상태에 따라 **주문 정정·알림** 트리거 가능 — `DRY_RUN` 환경변수 규약 확인 후 실행 |
| **DB 부하** | 수동 실행 + 타이머 동시면 연결 수 증가 | 피크 시간 피하기 |

---

## 4. P1 — DB 연결 수·PgBouncer·앱 풀

### 4.1 현황 (참고)
- `gunicorn-go100.conf.py`: **workers = 2**
- `database.py`: `pool_size=10`, `max_overflow=5` → 워커당 최대 **15** 연결 이론상, 2 워커면 **최대 ~30** (프로세스별 풀)
- Postgres `max_connections=100`, PgBouncer `default_pool_size=20`, `max_client_conn=200`
- 동일 DB를 쓰는 **kis-v41-api**, **다수 크론**, **스케줄러 oneshot**이 동시에 붙으면 **피크에 고갈** 가능

### 4.2 조치 계획

| 단계 | 작업 |
|------|------|
| D-1 | **장중 피크**에 `pg_stat_activity` 카운트·`application_name` 또는 유저별 분해 스냅샷 3회 이상 |
| D-2 | PgBouncer `SHOW POOLS` / `SHOW CLIENTS` 로 **클라이언트 대기** 여부 확인 |
| D-3 | 필요 시 **우선순위 낮은 배치**의 DB URL을 **6432 전용**으로 고정·직접 5432 제거 |
| D-4 | 극단적 경우만: `pool_size`/`max_overflow` 소폭 하향 **또는** postgres `max_connections` 상향 (메모리·PgBouncer와 함께 설계) |

### 4.3 광범위 영향 분석

| 영역 | 영향 |
|------|------|
| **풀 축소** | 고부하 시 **대기 시간 증가·타임아웃** 가능 | 점진 적용 + 지표 모니터링 |
| **max_connections 상향** | Postgres RAM·체크포인트 부담 | DBA 검토 |
| **URL 변경** | 잘못된 호스트/포트 시 **전 서비스 다운** | 스테이징·단일 서비스부터 |

---

## 5. P1 — `go100_live_daily_summary` 및 `portfolio_id` 불일치

### 5.1 문제 정의
- DB 실제 컬럼: `summary_id`, `user_id`, `summary_date`, … (**`portfolio_id` 없음**).
- 현재 워크스페이스 코드(`live_trading.py`, `risk_agent.py`)는 **`user_id` + `summary_date`** 기준.
- 과거 journal에는 `WHERE portfolio_id = $1` 쿼리 오류가 있음 → **배포 리비전 불일치 또는 미추적 코드** 가능.

### 5.2 조치 계획

| 단계 | 작업 |
|------|------|
| M-1 | **운영 바이너리/브랜치**에서 문자열 `go100_live_daily_summary` + `portfolio_id` **전수 grep** (서버 배포 경로 포함) |
| M-2 | **제품 결정**: 일일 요약을 **유저 단위**로 유지할지, **포트폴리오 단위**로 쪼갤지 |
| M-3a | (유저 단위 유지) 잘못된 쿼리만 제거·수정 — **스키마 변경 없음** |
| M-3b | (포트폴리오 단위) `portfolio_id` 컬럼 추가, UNIQUE `(portfolio_id, summary_date)` 또는 `(user_id, portfolio_id, summary_date)`, `update_daily_summary`·리스크 에이전트·대시보드 **전부 수정**, **기존 행 백필 정책** 수립 |

### 5.3 광범위 영향 분석 (M-3b 특히 중요)

| 영역 | 영향 |
|------|------|
| **스키마 마이그레이션** | `ON CONFLICT (user_id, summary_date)` **깨짐** → 마이그레이션 스크립트에서 **제약 재정의** 필수 |
| **한 유저·다수 LIVE 포트폴리오** | 유저 단위 summary는 **손익이 섞임** — 리스크·서킷 브레이커 의미 변경 |
| **대시보드·API** | `realized_pnl` 조회 단위 변경 → **프론트·리포트** 연쇄 수정 |
| **롤백** | 컬럼 추가 후 롤백 시 **데이터 손실** 위험 | 백업 후 적용 |
| **다운타임** | 대형 테이블에 인덱스 추가 시 **락** | 저부하 윈도우·`CONCURRENTLY` 검토 |

---

## 6. P2 — 스케줄 실패 알림

### 6.1 조치 계획

| 단계 | 작업 |
|------|------|
| N-1 | `go100-scheduler@.service`에 `OnFailure=` → 경량 `go100-scheduler-failure@.service` (curl 텔레그램 또는 `logger` + 외부 수집) |
| N-2 | 또는 `go100_scheduler.py` 최상위 `try/except`에서 **한 번만** 알림 (systemd와 중복 주의) |

### 6.2 광범위 영향 분석

| 영역 | 영향 |
|------|------|
| **노이즈** | 일시적 DB 블립 시 **알림 폭주** | 재시도·레이트 리밋 |
| **시크릿** | 텔레그램 URL에 토큰 — **`.env`만 사용** (하드코딩 금지) |
| **보안** | 실패 메시지에 **스택·SQL** 노출 가능 | 마스킹 정책 |

---

## 7. P2 — 키움 토큰 로그 이원화

### 7.1 조치 계획
- 모니터링 문서에 **정본 로그**를 `logs/cron/kiwoom_token_YYYYMMDD.log` 로 명시.
- 선택: `refresh_kiwoom_tokens.sh` 끝에 `echo` 한 줄을 stdout으로 출력해 `/var/log/go100/kiwoom_token_refresh.log`에도 흔적.

### 7.2 광범위 영향
- **거의 없음** — 운영 가독성만 개선.

---

## 8. P3 — `/root/webapp/backend` 레거시

### 8.1 조치 계획 (장기)
- `paper_trade_analyzer` 등을 `kis-autotrade-v4`로 이관하거나, 공용 패키지로 분리.
- 단기: **동일 DB 스키마 버전**·**환경변수** 체크리스트만 유지.

### 8.2 광범위 영향
- 이관 시 **import 경로·배포·크론** 전부 변경 — **별도 프로젝트**로 계획 수립 권장.

---

## 9. P3 — `security_scan.sh` / `path_check.sh`

### 9.1 조치 계획
- `project-docs/scripts/security_scan.sh`에 **인자로 TARGET_DIR** 지원, 기본은 `project-docs`.
- `path_check.sh`에 **`kis-autotrade-v4` 예외 허용** 또는 심볼릭 링크 규칙 문서화.

### 9.2 광범위 영향
- CI/로컬 스크립트 동작 변경 — **문서·훅** 동시 갱신.

---

## 10. 통합 리스크 매트릭스

| 조치 | 서비스 중단 가능성 | 데이터 변경 | 롤백 난이도 | 연쇄 범위 |
|------|-------------------|-------------|-------------|-----------|
| P0 방안 A (크론·데몬만 venv) | 낮음 | 없음 | 쉬움 | 크론·GO100 배치 |
| P0 방안 B (API까지 .venv) | **높음** | 없음 | 중간 | **전 API** |
| 스케줄러 수동 실행 | 낮음 | 있음(주문/가상) | 해당 런만 | 포트폴리오별 |
| DB 풀/URL 튜닝 | 중간 | 없음 | 중간 | **전 DB 소비자** |
| daily_summary 스키마 확장 | 중간~높음 | **있음** | 어려움 | **DB+백엔드+리스크+FE** |
| systemd OnFailure | 낮음 | 없음 | 쉬움 | 알림 채널 |

---

## 11. 검증 체크리스트 (조치 완료 정의)

- [ ] `venv/bin/python3 -c "import numpy, pandas"` 성공
- [ ] `.venv`를 쓰는 GO100 경로가 **0건**이거나, `.venv` import 성공(방안 B)
- [ ] `systemctl start go100-scheduler@paper` / `@reconcile` **exit 0** (한 번 이상)
- [ ] `curl -s http://127.0.0.1:8002/api/v1/go100/monitor/health` → `200` + `database connected`
- [ ] 장중 한 시점 `pg_stat_activity` + PgBouncer 대기 큐 **기준선 문서화**
- [ ] (스키마 조치 시) 마이그레이션 + 리스크 에이전트 스모크 + 롤백 스크립트 존재
- [ ] (알림 조치 시) 의도적 실패 테스트로 **1건** 알림 수신

---

*본 계획은 코드·설정 스냅샷(2026-04-07) 기준이며, 실제 적용 전 CEO/운영 승인·변경 창구에 맞춰 일정을 확정해야 합니다.*
