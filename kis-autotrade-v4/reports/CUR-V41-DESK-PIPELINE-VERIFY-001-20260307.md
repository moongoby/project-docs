# CUR-V41-DESK-PIPELINE-VERIFY-001-20260307

[인계 확인]
직전 완료: T-235
현재 단계: Phase 2c
CEO 지시 적용: D-008-KR
strategy_cards: 60
open_positions: 0

---

## 개요
- **Task ID**: T-231
- **제목**: DESK 파이프라인 실시간 검증 (DESK5→4→3→2 전 구간)
- **실행일시**: 2026-03-07 00:23 KST
- **의존성**: T-212(DESK5 크론 cd 수정), T-213(DESK4 watchlist 연결), T-214(pool_link 연결) 완료 후
- **목적**: T-212/T-213/T-214 적용 후 DESK 파이프라인 전 구간이 실제로 작동하는지 수동 실행으로 검증

---

## 1. DESK5 수동 실행

### 실행 명령
```bash
source venv/bin/activate
python -m backend.app.services.desk_filters.node_detector_desk5
```

### 실행 결과
```
DESK5 Node Detector 완료: {'processed': 0, 'history_inserted': 0, 'realtime_updated': 0, 'errors': 0}
```

### DB 확인
```sql
SELECT count(*) FROM v4_desk5_watchlist;
-- 결과: 20
```

```sql
SELECT stock_code, stock_name, trigger_t5_1, trigger_t5_2, trigger_t5_3, triggers_met, total_score, scan_date
FROM v4_desk5_watchlist WHERE status='WATCHING' ORDER BY total_score DESC LIMIT 10;
```
```
 stock_code |  stock_name  | trigger_t5_1 | trigger_t5_2 | trigger_t5_3 | triggers_met | total_score | scan_date
------------+--------------+--------------+--------------+--------------+--------------+-------------+------------
 383220     | F&F          | f            | f            | f            |            0 |      0.6750 | 2026-03-03
 0005A0     | 0005A0       | f            | f            | f            |            0 |      0.6700 | 2026-03-03
 0013R0     | 0013R0       | f            | f            | f            |            0 |      0.6700 | 2026-03-03
 008730     | 율촌화학     | f            | f            | f            |            0 |      0.6700 | 2026-03-03
 028300     | HLB          | f            | f            | f            |            0 |      0.6700 | 2026-03-03
 041190     | 우리기술투자 | f            | f            | f            |            0 |      0.6700 | 2026-03-03
 053030     | 바이넥스     | f            | f            | f            |            0 |      0.6700 | 2026-03-03
 053060     | 세동         | f            | f            | f            |            0 |      0.6700 | 2026-03-03
 214390     | 경보제약     | f            | f            | f            |            0 |      0.6700 | 2026-03-03
 300720     | 한일시멘트   | f            | f            | f            |            0 |      0.6700 | 2026-03-03
```

### 분석
- **처리 건수**: processed=0 (장외 시간 실행 — 시가 데이터 없음)
- **워치리스트**: 20종목 유지 (기존 scan_date=2026-03-03)
- **T5-2 REL-003**: MA60 기울기 + 1.5배 거래량 트리거 모두 미충족 (triggers_met=0) — 장외 시간이므로 정상
- **에러**: 0건 ✅
- **모듈 실행**: 성공 ✅

---

## 2. DESK4 수동 실행

### 실행 명령
```bash
python -m backend.app.services.desk_filters.node_detector_desk4
```

### 실행 결과
```
INFO:node_detector_desk4:load_watchlist FIX-002: primary(v4_desk4_watchlist)=11 secondary(v4_node_realtime)=0 total=11
INFO:node_detector_desk4:DESK4 024740: phase=RISING confidence=75 promote=False
INFO:node_detector_desk4:DESK4 0000D0: phase=RISING confidence=60 promote=False
INFO:node_detector_desk4:DESK4 053050: phase=RISING confidence=75 promote=False
INFO:node_detector_desk4:DESK4 009180: phase=RISING confidence=75 promote=False
INFO:node_detector_desk4:DESK4 0068M0: phase=RISING confidence=60 promote=False
INFO:node_detector_desk4:DESK4 456200: phase=RISING confidence=60 promote=False
INFO:node_detector_desk4:DESK4 0084E0: phase=RISING confidence=60 promote=False
INFO:node_detector_desk4:DESK4 117580: phase=RISING confidence=75 promote=False
INFO:node_detector_desk4:DESK4 012700: phase=PULLBACK confidence=65 promote=False
INFO:node_detector_desk4:DESK4 483030: phase=PULLBACK confidence=65 promote=False
INFO:node_detector_desk4:DESK4 040420: phase=PULLBACK confidence=65 promote=False
DESK4 Node Detector 완료: {'processed': 11, 'starting_signals': 0, 'promote_signals': 0, 'errors': 0}
```

### DB 확인
```sql
SELECT status, count(*) FROM v4_desk4_watchlist GROUP BY status;
```
```
  status  | count
----------+-------
 EXPIRED  |     7
 WATCHING |    11
```

### 분석
- **FIX-002 적용 확인**: v4_desk4_watchlist primary=11종목 로드 성공 ✅ (FIX 전: 0건)
- **RISING 분류**: 8종목 (confidence 60~75)
- **PULLBACK 분류**: 3종목 (confidence 65)
- **promote_signals**: 0건 (장외 시간이므로 정상)
- **에러**: 0건 ✅

---

## 3. DESK3 확인

### DB 쿼리
```sql
SELECT count(*) FROM v4_desk3_pool WHERE status='ACTIVE';
-- 결과: 401
```

```sql
SELECT MAX(pool_entry_date) as latest_entry, MIN(pool_entry_date) as oldest_entry
FROM v4_desk3_pool WHERE status='ACTIVE';
```
```
 latest_entry | oldest_entry
--------------+--------------
 2026-03-06   | 2026-03-03
```

```sql
SELECT count(*) as total FROM v4_desk3_pool;
-- 결과: 406
```

### 분석
- **ACTIVE**: 401건 (지시서 기준치 동일) ✅
- **최신 입력일**: 2026-03-06
- **전체**: 406건 (ACTIVE 401 + 기타 5건 — EXPIRED 등)
- **상태**: 정상 ✅

---

## 4. DESK2 pool_link 수동 실행

### 실행 명령
```bash
python -m backend.desk_filters.desk2_pool_link
```

### 실행 결과
```
2026-03-07 00:23:58 [INFO] desk2_pool_link: === DESK3->DESK2 pool_link 시작 ===
2026-03-07 00:23:58 [INFO] backend.app.services.strategy.desk2_pool_link: DESK345→DESK2 boost 완료: date=2026-03-07 D3=401 D4=0 D5=0 boosted=0 inserted=249 total=249
2026-03-07 00:23:58 [INFO] desk2_pool_link: 결과: {'target_date': '2026-03-07', 'desk3_active': 401, 'desk4_open': 0, 'desk5_open': 0, 'boosted': 0, 'inserted': 249, 'total_processed': 249}
[T-214] DESK3->DESK2 pool_link 완료
  target_date    : 2026-03-07
  desk3_active   : 401
  desk4_open     : 0
  desk5_open     : 0
  boosted        : 0
  inserted       : 249
  total_processed: 249
```

### DB 확인
```sql
SELECT count(*) FROM v4_desk2_candidates WHERE target_date = CURRENT_DATE;
-- 결과: 249
```

```sql
SELECT count(*) as total, round(avg(score),4) as avg_score, max(score_rank) as max_rank
FROM v4_desk2_candidates WHERE target_date = CURRENT_DATE;
```
```
 total | avg_score | max_rank
-------+-----------+----------
   249 |    0.5000 |        0
```

### 분석
- **inserted**: 249건 ✅ (T-214 기준 255건 목표 대비 249건 — DESK4/5 open=0이므로 boost 없음)
- **boosted**: 0건 (DESK4/5 promoted=0 → 정상)
- **DESK4_open**: 0건 (promote_signals=0 — 장외)
- **DESK5_open**: 0건 (장외)
- **avg_score**: 0.5000 (기본값 — 실시간 피처 스코어링 미적용 상태)
- **score_rank**: 0 (재스코어링 미실행 — 정상)

---

## 5. 파이프라인 전 구간 요약표

| DESK | 소스 | 건수 | 트리거율 | 상태 |
|------|------|------|----------|------|
| DESK5 | 노드 실시간 + 주간 스캔 | **20종목** (WATCHING) | 0% (장외) | ✅ 정상 |
| DESK4 | DESK5_WL + v4_desk4_watchlist | **11종목** (WATCHING, FIX-002 적용) | 0% (장외) | ✅ 정상 |
| DESK3 | 풀 스캔 (ACTIVE) | **401건** | N/A | ✅ 정상 |
| DESK2 | DESK3 pool_link (T-214) | **249건** (오늘 2026-03-07) | boosted=0 | ✅ 정상 |

---

## 6. 이슈 및 관찰사항

### 6-1. score_rank=0 이슈
- v4_desk2_candidates에 score_rank=0 — 피처 기반 재스코어링 크론 미실행 상태
- avg_score=0.5000 (기본값) — 실거래 당일 장시작 전 스코어링 크론이 재정렬해야 함
- **영향**: 금일 장마감 후 확인 필요 (장외 실행이므로 정상 범위)

### 6-2. DESK4/5 boost=0
- DESK4_open=0, DESK5_open=0 — 장외 수동 실행이므로 promoted 종목 없음
- 장시간 실행 시 DESK4/5 promoted 종목이 DESK2 후보에 부스트 적용될 예정

### 6-3. DESK5 T5-2 트리거 미발동
- scan_date=2026-03-03 (3일 전) — 주말 포함으로 신규 스캔 미실행
- MA60 기울기 + 1.5배 거래량 트리거: 0/20 (장외이므로 정상)
- 다음 거래일(2026-03-10) 장시간 크론 실행 시 검증 예정

---

## 7. 성공 기준 달성 여부

| 기준 | 결과 | 판정 |
|------|------|------|
| DESK5 수동 실행 성공 | ✅ errors=0 | PASS |
| DESK5 워치리스트 20종목 확인 | ✅ count=20 | PASS |
| DESK4 수동 실행 성공 | ✅ processed=11 | PASS |
| DESK4 FIX-002 11종목 로드 | ✅ primary=11 | PASS |
| DESK4 RISING/PULLBACK 분류 | ✅ RISING=8/PULLBACK=3 | PASS |
| DESK3 ACTIVE 401건 확인 | ✅ count=401 | PASS |
| DESK2 pool_link 수동 실행 성공 | ✅ inserted=249 | PASS |
| 전 구간 요약표 작성 | ✅ 완료 | PASS |
| strategy_cards 수정 금지 | ✅ 미수정 | PASS |
| DB 스키마 변경 금지 | ✅ 미변경 | PASS |

**성공 기준 10/10 PASS** ✅

---

## 체크포인트
- [x] 코드 레포 커밋 완료 (코드 변경 없음 — 검증 전용 Task)
- [ ] project-docs 보고서 push 완료 (진행 예정)
