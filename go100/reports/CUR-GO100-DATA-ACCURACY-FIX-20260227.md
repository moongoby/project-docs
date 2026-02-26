# CUR-GO100-DATA-ACCURACY-FIX-20260227 — 데이터 정확성 긴급 조치

**날짜**: 2026-02-27
**심각도**: P0 (긴급)
**발견 경위**: 백억이 시장 브리핑 데이터 vs 실제 DB 대조 검증

---

## 1. 발견된 문제

| 문제 | 심각도 | 상세 |
|---|---|---|
| index_daily 3일 누락 | **P0** | 02-24, 02-25, 02-26 지수 미적재. KOSPI 5,846→6,307 (+7.9%) 미반영 |
| VKOSPI 스테일 데이터 | **P0** | 레짐에 02-23 VKOSPI=43.87(02-20 값) 사용. 실제 02-23=46.34, 02-24=48.12 |
| 레짐 VKOSPI 미연동 | **P1** | SIDEWAYS만 표시, VKOSPI 48(고변동성) 미반영 |
| index_daily 크론 실패 | **P0** | 근본 원인 — KIS API 토큰 오류로 매일 실패 |

---

## 2. 근본 원인 분석

### 2-1. index_daily 누락
- `collect_index_daily.sh` → `historical_backfill.py --index-only` → **KIS API 토큰 실패**
- 크론 로그: `KIS token failed. Check KIS_APP_KEY/KIS_APP_SECRET in legacy/.env`
- 스크립트는 에러를 무시하고 "수집 완료" 출력하여 발견이 늦어짐

### 2-2. VKOSPI 스테일
- `regime_detector.py`가 레짐 계산 시 `v4_vkospi_daily`에서 최신값 참조
- VKOSPI 수집(18:30)보다 레짐 계산이 먼저 실행되면 이전 날짜 값 사용
- 수집 후 레짐 테이블 역동기화 메커니즘 부재

---

## 3. 조치 내역

### 블록 0: 현황 진단

| 테이블 | 진단 결과 |
|---|---|
| ohlcv_daily | 정상 (02-26까지, 3839건/일) |
| index_daily | 02-23이 최신 (**3일 누락**) |
| go100_global_market | vkospi 컬럼 없음, 02-26 US 데이터 미완 |
| v4_market_regime_daily | 02-23이 최신, VKOSPI=43.87 (스테일) |
| v4_vkospi_daily | 02-24까지 정상 (DATA_GO_KR) |

### 블록 1: index_daily 3일 보정

pykrx로 02-24, 02-25, 02-26 지수 보정:

| 날짜 | KOSPI | KOSDAQ | KOSPI200 |
|---|---|---|---|
| 02-24 | 5,969.64 | 1,165.00 | 886.88 |
| 02-25 | 6,083.86 | 1,165.25 | 903.83 |
| **02-26** | **6,307.27** | **1,188.15** | **944.02** |

**9건 INSERT 완료.**

### 블록 2: go100_global_market VKOSPI 컬럼 + 정확값 반영

1. `ALTER TABLE go100_global_market ADD COLUMN vkospi REAL;`
2. `v4_vkospi_daily` → `go100_global_market.vkospi` 동기화 (15건)
3. `v4_market_regime_daily.vkospi` 스테일 수정 (3건)

| 날짜 | 기존 (스테일) | 수정 후 (정확) |
|---|---|---|
| 02-23 | 43.87 | **46.34** |
| 02-13 | (NULL) | **41.57** |
| 02-12 | (NULL) | **40.51** |

### 블록 3: 레짐 VKOSPI 고도화

`regime_enhanced.py` 신규 생성:

| VKOSPI 구간 | 태그 | 설명 |
|---|---|---|
| < 20 | LOW_VOL | 안정 |
| 20-30 | NORMAL | 정상 |
| 30-40 | ELEVATED | 경계 |
| **40-50** | **HIGH_VOL** | **위험** |
| >= 50 | EXTREME | 극단 공포 |

- 현재: `SIDEWAYS` → **`SIDEWAYS_HIGH_VOL`** (VKOSPI 48.12)
- `sync_vkospi_to_regime()`: v4_vkospi_daily → 레짐/글로벌마켓 일괄 동기화
- 전체 히스토리 803건 + global_market 225건 VKOSPI 동기화 완료

### 블록 4: 크론 재정비

**근본 수정**: KIS API 기반 → pykrx 기반으로 index_daily 수집 교체

| 시각 | 작업 | 변경 |
|---|---|---|
| 18:00 | ohlcv_daily 수집 | 기존 유지 (정상) |
| **18:30** | **index_daily 수집** | **pykrx 기반으로 교체** (KIS API 실패 해결) |
| 18:30 | VKOSPI 수집 | 기존 유지 (DATA_GO_KR, 정상) |
| **18:40** | **VKOSPI 레짐 동기화** | **신규 추가** |

파일 변경:
- `scripts/collect_index_daily.sh` → pykrx 기반으로 교체 (기존 백업: `.bak.kis`)
- `scripts/go100/run_vkospi_regime_sync.sh` → 신규

### 블록 5: tool_executors 패치

`get_market_regime()` 확장:
- `v4_vkospi_daily`에서 정확한 VKOSPI 참조 (레짐 테이블의 스테일 값 대신)
- `enhanced_regime`, `vol_tag`, `risk_warning` 필드 추가
- 백억이 브리핑에 변동성 경고 자동 포함

`get_global_market()` 확장:
- `vkospi` 컬럼 포함하여 조회

---

## 4. 수정 후 크론 타임라인 (평일)

| 시각 | 작업 | 상태 |
|---|---|---|
| */5 | 헬스 모니터 | 기존 |
| 07:00 | 크로스마켓 시그널 | 기존 |
| 08:30 | 글로벌 마켓 수집 | 기존 |
| 08:50 | 모닝 브리핑 | 기존 |
| 09:00~15:30 | 장중 이벤트/알림 | 기존 |
| 15:40 | 장마감 리포트 + KRX WS 종료 | 기존 |
| 16:10 | 페이퍼 트레이딩 일일 처리 | 기존 |
| 16:40 | 호가 집계 | 기존 |
| 16:50 | 틱 집계 | 기존 |
| 17:00 | 갭 MV REFRESH | 기존 |
| 18:00 | ohlcv_daily 수집 | 기존 |
| **18:30** | **index_daily 수집 (pykrx)** | **수정** |
| 18:30 | VKOSPI 수집 (DATA_GO_KR) | 기존 |
| **18:40** | **VKOSPI 레짐 동기화** | **신규** |
| 18:40 | 투자자 수급 수집 | 기존 |
| 19:00 | stock_universe 수집 | 기존 |
| 19:30 | 재무제표 수집 | 기존 |

---

## 5. 파일 목록

| 경로 | 크기 | 변경 유형 |
|---|---|---|
| `backend/app/services/go100/ai/regime_enhanced.py` | 6KB | 신규 |
| `backend/app/services/go100/ai/tool_executors.py` | ~30KB | 수정 (get_market_regime, get_global_market) |
| `scripts/collect_index_daily.sh` | 2.3KB | 교체 (KIS→pykrx) |
| `scripts/collect_index_daily.sh.bak.kis` | — | 기존 백업 |
| `scripts/go100/run_daily_index_collect.sh` | 2.3KB | 신규 |
| `scripts/go100/run_vkospi_regime_sync.sh` | 1KB | 신규 |

DB 변경:
| 변경 | 내용 |
|---|---|
| `go100_global_market` ADD COLUMN | `vkospi REAL` 추가 |
| `index_daily` INSERT 9건 | 02-24/25/26 × KOSPI/KOSDAQ/KOSPI200 |
| `v4_market_regime_daily` UPDATE 803건 | VKOSPI 정확값 동기화 |
| `go100_global_market` UPDATE 225건 | VKOSPI 정확값 동기화 |

---

## 6. 검증 결과

| 항목 | Before | After | 판정 |
|---|---|---|---|
| index_daily 최신일 | 02-23 | **02-26** | ✅ |
| KOSPI 최신 | 5,846.09 | **6,307.27** | ✅ |
| VKOSPI 02-23 (레짐) | 43.87 (스테일) | **46.34** (정확) | ✅ |
| VKOSPI 최신 | 없음 | **48.12** (02-24) | ✅ |
| 강화 레짐 | SIDEWAYS | **SIDEWAYS_HIGH_VOL** | ✅ |
| 리스크 경고 | 없음 | **고변동성 경고** | ✅ |
| index_daily 크론 | KIS 실패 | **pykrx 기반** | ✅ |
| VKOSPI 동기화 크론 | 없음 | **18:40 신규** | ✅ |
| go100 서비스 | active | active | ✅ |

---

## 7. 잔여 사항

| 항목 | 상태 | 비고 |
|---|---|---|
| 02-25, 02-26 VKOSPI | 미수집 | DATA_GO_KR T-1일 지연. 다음 영업일 자동 수집 예정 |
| v4_market_regime_daily 02-24~26 | 미생성 | 레짐 계산은 Orchestrator가 PRE_MARKET에서 실행. 다음 영업일 자동 생성 |
| go100_global_market 02-25/26 VIX/US | 부분 누락 | 글로벌 마켓 수집(08:30)에서 자동 반영 예정 |

---

*P0 긴급 조치 완료. 근본 원인(KIS API 토큰 실패 + VKOSPI 스테일) 해결됨.*
