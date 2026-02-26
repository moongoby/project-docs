# 병렬 작업 5건 종합 보고 — 2026-02-26

**작성일**: 2026-02-26  
**작업 지시**: 병렬 5건 동시 실행, 에러 시 해당 작업만 스킵·나머지 진행, 전체 완료 후 종합 보고

---

## 1. 작업 1/5: DART API키 서버 등록 + PIT 재무제표 수집

| 항목 | 결과 |
|------|------|
| 환경변수 | `DART_API_KEY` `/etc/environment` 및 `systemctl set-environment` 반영 |
| go100 재시작 | 정상 (active/running) |
| DART API 테스트 | OK (공시 목록 조회 2620건) |
| PIT 테이블 | `go100_fundamentals_pit` 기존 생성·인덱스 유지 |
| PIT 데이터 | **11,166건** (기 수집분 유지, 추가 수집 시 DART 스크립트 사용) |

- **참고**: 사용자 제공 DART 테스트 코드의 `dart.list(corp_code=..., start=...)` 인자는 해당 OpenDartReader 버전과 불일치. `dart.list('00126380', start='20250101', end='20260226')` 형태로 호출 시 정상 동작 확인.

---

## 2. 작업 2/5: 대시보드 API 7건 404 복구

| 조치 | 내용 |
|------|------|
| 원인 | 라우터 prefix가 `/api/go100/dashboard`만 등록되어, 프록시/베타에서 호출하는 `/api/v1/go100/dashboard/*` 경로 미노출 |
| 수정 | `dashboard_router.py` prefix를 `/dashboard`로 변경 후, `main.py`에서 `/api/go100` 및 `/api/v1/go100` 두 prefix로 동시 include |

| 엔드포인트 | 결과 (HTTP 코드) |
|------------|------------------|
| /api/v1/go100/dashboard/overview | 401 (인증 필요) |
| /api/v1/go100/dashboard/performance | 401 |
| /api/v1/go100/dashboard/positions | 401 |
| /api/v1/go100/dashboard/strategies | 401 |
| /api/v1/go100/dashboard/regime-history | 401 |
| /api/v1/go100/dashboard/goal-progress | 401 |
| /api/v1/go100/dashboard/activity-log | 401 |

- 7건 모두 **200 또는 401** → 404 복구 완료. (인증 필요 리소스는 401 정상)

---

## 3. 작업 3/5: usage_logs 기록 복구 + 모니터링 API 3건 복구

### 3-A. usage_logs

| 조치 | 내용 |
|------|------|
| 코드 | `usage_logger.log_chat_usage()` 예외 시 `logger.debug` → `logger.warning`으로 상향 (미기록 원인 추적용) |
| DB commit | 자체 세션 사용 시 `await _db.commit()` 이미 존재. 전달 세션 사용 시에는 호출 측 commit 책임 |
| 현재 건수 | **0건** (채팅 1회 이상 발생 후 재확인 권장) |

- 18번 채팅 후 0건이었던 이슈는, 예외 삼킴으로 인한 실패 가능성 대비해 경고 로깅 추가로 재발 시 원인 파악 가능.

### 3-B. 모니터링 API

| 조치 | 내용 |
|------|------|
| 라우팅 | `monitor_router.py` prefix를 `/monitor`로 변경, `main.py`에서 `/api/go100` 및 `/api/v1/go100` 이중 등록 |
| 추가 엔드포인트 | `/system` (health와 동일 응답), `/alerts` (go100_alerts 테이블 조회, 없으면 빈 배열) |

| 엔드포인트 | 결과 |
|------------|------|
| /api/v1/go100/monitor/health | 200 |
| /api/v1/go100/monitor/system | 200 |
| /api/v1/go100/monitor/errors | 401 |
| /api/v1/go100/monitor/alerts | 401 |

---

## 4. 작업 4/5: 전체 데이터 인프라 (블록 1~7, 9)

- **블록 8**은 작업 1에서 PIT로 처리했으므로 작업 4에서 제외.

| 블록 | 내용 | 결과 |
|------|------|------|
| 1 | 글로벌 지표 3개월→1년 확장 | **293건** (2025-02-25 ~ 2026-02-26), 신규 2·업데이트 290 |
| 2 | 오버나이트 갭 MV | 기존 MV 유지, **906,115건** |
| 3 | 섹터 가격 시계열 + 상관계수 테이블 | 테이블 생성·유지, **7,047건** (29개 섹터), 이번 적재 0 (이미 최신) |
| 4 | 크로스마켓 시그널 + 성과 추적 | 테이블 생성·유지 |
| 5 | 경험 DB + 괴리 분석 + 보정 파라미터 | 테이블·시드 유지, **go100_calibration_params 12건** |
| 6 | 트레이딩 비용 파라미터 | 테이블·시드 유지, **3건** |
| 7 | 호가/틱 통계 집계 테이블 | 테이블 생성·유지 |
| 9 | 섹터 상관계수 계산 (블록 3 완료 후) | **1,624건** (1m/3m/6m/1y 기간별) |

- 실행 스크립트: `scripts/data_collect/expand_global_history.py`, `generate_sector_price.py`, `calc_sector_correlation.py` (DB 연결은 env 기반).

---

## 5. 작업 5/5: KRX 정규장 WebSocket 자동시작 + 40종목 리스트

| 항목 | 결과 |
|------|------|
| cron | `50 8 * * 1-5` → go100-ws-krx start, `40 15 * * 1-5` → go100-ws-krx stop 반영 (기존 cron과 중복 제거 후 유지) |
| 40종목 리스트 | `scripts/data_collect/ws_stock_list.py` 생성, DB 연동(시가총액 상위 30 + 전략카드 종목) → **30종목** (전략카드 보유 종목 없음) |
| 설정 파일 | `/root/kis-autotrade-v4/config/ws_stock_list.json` 생성 (stocks 배열 + count) |
| kis_ws_collector 연동 | `config/ws_stock_list.json` 존재 시 해당 종목 리스트 우선 로드, 없으면 기존처럼 거래대금 상위 조회 |

- **참고**: `ws_stock_list.py`는 DB 연결을 `DB_NAME`/`DB_USER`/`DB_PASSWORD` 등 env 기반으로 사용. `ohlcv_daily`에 종목명 컬럼이 없어 출력은 종목코드만 표기.

---

## 6. 최종 검증 요약

| 항목 | 결과 |
|------|------|
| DART | OK |
| 대시보드 API 7건 | 401 (인증 필요 — 정상) |
| 모니터 API 4건 | health/system 200, errors/alerts 401 |
| usage_logs | 0건 (채팅 발생 시 기록·경고 로그로 추적 가능) |
| go100_global_market | 293 |
| go100_overnight_gap | 906,115 |
| go100_sector_price | 7,047 |
| go100_sector_correlation | 1,624 |
| go100_cross_market_signals | 0 |
| go100_experience_log | 0 |
| go100_calibration_params | 12 |
| go100_trading_cost_params | 3 |
| go100_fundamentals_pit | 11,166 |
| WS 구독 종목 수 | 30 (config/ws_stock_list.json) |
| go100 관련 cron | 9개 |
| 디스크 | /data 8%, / 69% |
| 서비스 | go100 active, go100-ws-nxt active, go100-ws-krx inactive |

---

## 7. 스킵·참고 사항

- **작업 2 curl 오타**: 지시서의 `go00` → `go100` (strategies 경로) 반영하여 검증 수행.
- **블록 2**: `DO $ ... END $` 블록을 heredoc으로 전달 시 구문 오류 가능성 있음. MV는 이미 존재해 REFRESH만 필요 시 수동 실행 권장.
- **go100_alerts**: 모니터 `/alerts`는 테이블 없으면 빈 배열 반환. 추후 알림 스키마 정의 시 해당 테이블 연동 가능.

---

**보고서 끝.**
