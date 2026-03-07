# CUR-V41-PRE-MARKET-FINAL-CHECK-001-20260307
## T-276: T-251 HANDOVER 반영 + 큐 잔류파일 정리 + 03-10 장전 최종 점검

**작성**: 2026-03-07 15:32 KST
**Task ID**: T-276
**서버**: 211 (kis-autotrade-v4)
**우선순위**: P0-CRITICAL
**의존성**: T-251 완료

---

[인계 확인]
직전 완료: T-275
현재 단계: Phase 2C Command Center
CEO 지시 적용: D-001, D-002, D-008-KR
strategy_cards: 60
open_positions: 0

---

## Part A — 큐 상태 확인

> ⚠️ 주의: `/root/.genspark/directives/pending/` 및 `running/` 경로의 파일 이동은 파이프라인 전용 시스템으로 claudebot이 수행하지 않음 (사용자 지시사항)

### 현황 (2026-03-07 15:31 KST)

| 디렉토리 | 파일 수 | 파일명 |
|----------|---------|--------|
| running/ | 2 | KIS_20260307_113204_BRIDGE.md, KIS_20260307_114051_BRIDGE.md (현재 작업) |
| pending/ | 4 | KIS_20260307_114320_BRIDGE.md, KIS_20260307_123844_BRIDGE.md, KIS_20260307_124051_BRIDGE.md, KIS_20260307_143916_BRIDGE.md |

- **기대**: running 0건, pending 0건
- **실제**: running 2건, pending 4건
- **판정**: ⚠️ 큐 잔류 존재 — root 또는 파이프라인 자동 정리 필요

---

## Part B — T-251 결과 확인

### B-1. T-251 크론 파일 설치 현황

**파일**: `/etc/cron.d/v41_data_collection` — ✅ 존재 (root가 설치 완료)

| 크론 ID | 스케줄 | 스크립트 | 상태 |
|---------|--------|----------|------|
| C-1 매크로 | 평일 17:00 KST (08:00 UTC) | scripts/collectors/macro_collector_daily.py | ✅ 설치 |
| C-2 투자자수급 | 평일 17:30 KST (08:30 UTC) | scripts/collectors/investor_collector_daily.py | ✅ 설치 |
| C-3 펀더멘탈 | 토 02:00 KST (금 17:00 UTC) | scripts/collectors/fundamental_full_collect.py | ✅ 설치 |
| C-4 정합성검증 | 평일 18:00 KST (09:00 UTC) | scripts/monitoring/data_integrity_check.py | ✅ 설치 |

**총 T-251 크론**: 4건 ✅ (v41_data_collection 1개 파일에 4개 항목)

**스크립트 파일**:
- `scripts/collectors/macro_collector_daily.py` ✅
- `scripts/collectors/investor_collector_daily.py` ✅
- `scripts/collectors/fundamental_full_collect.py` ✅
- `scripts/collectors/install_v41_data_collection_cron.sh` ✅

### B-2. 정합성 규칙 C-01~C-12 결과 (2026-03-07 15:31 KST 실행)

> 현재 토요일(주말) — SKIP 규칙은 정상 동작

| 규칙 | 심각도 | 결과 | 내용 |
|------|--------|------|------|
| C-01 | CRITICAL | ❌ FAIL | 오늘(2026-03-07) 매크로 행 0건 — 토요일 장외 (정상) |
| C-02 | CRITICAL | ⏭ SKIP | C-01 오늘 데이터 없음 → 건너뜀 |
| C-03 | WARNING  | ✅ PASS | 최근 7일 us_vix NULL=0건 |
| C-04 | ERROR    | ✅ PASS | 섹터 매핑률 100.2% (3844/3836 ≥ 78%) |
| C-05 | ERROR    | ✅ PASS | 펀더멘탈 커버리지 100.2% (3844/3836 ≥ 90%) — T-247 완료로 7.1%→100% 달성 |
| C-06 | WARNING  | ❌ FAIL | 오늘 수급 행 0건 (기준 1000) — 토요일 장외 (정상) |
| C-07 | CRITICAL | ❌ FAIL | 오늘 분봉 0건 — 토요일 장외 (정상) |
| C-08 | WARNING  | ⏭ SKIP | 주말 — 체크 불필요 |
| C-09 | WARNING  | ⏭ SKIP | 주말 — 체크 불필요 |
| C-10 | CRITICAL | ⏭ SKIP | 장 외 시간 — 체크 불필요 |
| C-11 | — | ❌ 미존재 | T-251 시점 미추가 (10개 규칙 C-01~C-10만 존재) |
| C-12 | — | ❌ 미존재 | T-251 시점 미추가 |

**총합**: PASS=3 / FAIL=3 / SKIP=4 / 주말 FAIL=3건 (모두 토요일 장외 정상)
**CRITICAL FAIL (장내 기준)**: 0건 ✅
**C-05 상태**: PASS (100.2%, T-247 기완료로 이전 이슈 해소)

---

## Part C — 03-10 장전 최종 시스템 점검

### C-1. 서비스 상태 (2026-03-07 15:31 KST)

| 서비스 | 상태 | 비고 |
|--------|------|------|
| go100.service | ✅ active running | FastAPI localhost:8002 |
| go100-frontend.service | ✅ active running | Next.js localhost:3000 |
| kis-v41-api.service | ✅ active running | FastAPI localhost:8003 |
| kis-v41-monitor.service | ✅ active running | 포지션 모니터 |
| kis-v41-scheduler.service | ✅ active running | 스케줄러 |
| postgresql@16-main.service | ✅ active running | DB 정상 |
| redis-server.service | ✅ active running | Redis 서버 정상 |

**Redis 연결**: `redis-cli ping` → PONG ✅

### C-2. API 헬스체크

| 엔드포인트 | HTTP | 결과 |
|-----------|------|------|
| localhost:8002/health | 200 | `{"status":"degraded","redis":"disconnected"}` ⚠️ |
| localhost:8002/api/v4/health | 200 | `{"detail":"Internal Server Error"}` ❌ |

> ⚠️ **주의**: Redis 서버 자체는 정상(PONG)이지만 go100 API(8002) 내부 Redis 클라이언트 연결 끊김 감지.
> → `sudo systemctl restart go100` 권장 (root 수동 실행 필요)

### C-3. 크론 전체 목록

**v41_* 크론 파일**: 6개

| 파일 | 설명 |
|------|------|
| v41_data_collection | T-251: 매크로/수급/펀더멘탈/정합성 4건 |
| v41_desk2_pool_link | DESK3→DESK2 pool_link 크론 |
| v41_desk5_scan | DESK5 시드 스캔 크론 |
| v41_evolution_loop | GO100 진화 루프 크론 |
| v41_manager_snapshot | V4.1 매니저 스냅샷 크론 |
| v41_research_loop | 리서치 백테스트 루프 크론 |

### C-4. DB 핵심 지표 (2026-03-07 15:31 KST)

| 지표 | 값 | 판정 |
|------|-----|------|
| strategy_cards | 60 | ✅ |
| open_positions | 0 | ✅ (장외 정상) |
| scalping_universe | 1,354 | ✅ |
| dqi_kospi_90d (1800-3500 범위%) | 0.0% | ⚠️ KOSPI 정규화 저장 (실제값 ~275) |
| dqi_vix_60d_null_pct | 2.6% | ✅ (T-270 백필 완료, 기준 <10%) |
| fundamental_coverage | 100.0% | ✅ (T-247 완료) |
| sector_mapping_pct | 99.1% | ✅ (T-248/T-260 완료) |

> ⚠️ **KOSPI 정규화 주의**: v4_macro_daily.kr_kospi = ~275.31 (27531÷100으로 저장됨)
> 원래 쿼리 `WHERE kr_kospi BETWEEN 1800 AND 3500`은 0건 반환.
> 실측: 90일 57행 중 1800-3500 범위 0건, 200-400 범위 2건.
> → L0_KOSPI 재백필 CEO 결정 대기 (T-270 부분 수정됨)

---

## Part D — HANDOVER v10.60 갱신

HANDOVER.md v10.60: T-276 큐 정리 + 03-10 장전 최종 점검 결과
(섹션2 완료 작업 추가, 섹션6 웹 Claude 사항 갱신, 버전 이력 v10.60 추가)

---

## 03-10 장전 체크리스트

| 항목 | 상태 | 비고 |
|------|------|------|
| ☑ T-251 크론 파일 존재 | ✅ PASS | 4건 설치완료 |
| ☑ 정합성 체크 실행 결과 기록 | ✅ PASS | PASS=3/FAIL=3/SKIP=4 |
| ☑ 서비스 6개 상태 확인 | ✅ PASS | 전부 active running |
| ☑ Redis ping | ✅ PASS | PONG |
| ☑ DB 핵심 지표 7개 기록 | ✅ PASS | |
| ☑ strategy_cards=60 | ✅ PASS | |
| ☑ open_positions=0 | ✅ PASS | 장외 정상 |
| ☐ API Redis 연결 복구 | ⚠️ 필요 | go100 API /health degraded → 재시작 필요 |
| ☐ KOSPI 재백필 | ⚠️ CEO 결정 대기 | 실제 KOSPI 730행 UPDATE |
| ☐ DESK4 scan 크론 | ⚠️ root 필요 | install_desk4_scan.sh 수동 설치 |

---

## Root 수동 실행 필요 사항

| 순서 | 명령 | 이유 |
|------|------|------|
| 1 (긴급) | `sudo systemctl restart go100` | API Redis disconnected 복구 |
| 2 | `sudo bash /root/kis-autotrade-v4/scripts/desk4/install_desk4_scan.sh` | DESK4 일별 크론 미설치 (T-239 발견) |
| 3 (CEO 승인 후) | KOSPI 재백필 스크립트 실행 | yfinance 실제 KOSPI 730행 UPDATE → DQI Grade A 유지 |
| 4 (CEO 승인 후) | T-245R 2026-03-10 검증 크론 | 03-10 장 마감 후 KPI 검증 |

---

## 완료 기준 체크

- [x] running/pending 큐 상태 확인 완료 (이동 불가 - 파이프라인 전용)
- [x] T-251 크론 파일 존재 확인 ✅
- [x] 정합성 체크 실행 결과 기록 ✅
- [x] 서비스 6개 상태 확인 ✅
- [x] DB 핵심 지표 7개 기록 ✅
- [ ] HANDOVER v10.60 push (진행 중)
- [ ] 보고서 HTTP 200 확인 (push 후)
- [x] root 수동 실행 필요 사항 명시 ✅
