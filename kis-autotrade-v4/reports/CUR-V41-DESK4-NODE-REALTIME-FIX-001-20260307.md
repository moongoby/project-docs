# CUR-V41-DESK4-NODE-REALTIME-FIX-001-20260307

[인계 확인]
직전 완료: T-231 (DESK 파이프라인 전 구간 수동 검증)
현재 단계: Phase 2c (Command Center)
CEO 지시 적용: D-003, D-012, D-013
strategy_cards: 60
open_positions: 0

---

## Task ID
T-239

## 제목
DESK4 v4_node_realtime 데이터 미생성 원인 분석 및 수정

## 작업 일시
2026-03-07 KST

## 배경
- T-202: v4_node_realtime에 DESK4 데이터 0건 확인
- T-213: load_watchlist() FIX-002 적용 (v4_desk4_watchlist primary 수정)
- T-213 이후에도 cron 미설치로 인해 phase 데이터가 자동 갱신되지 않음
- 이 Task(T-239): 원인 분석 + 수동 실행 검증 + 크론 파일 생성

---

## 1. 현황 분석

### 1-1. v4_node_realtime DESK4 확인
```sql
SELECT count(*) FROM v4_node_realtime WHERE desk_level=4;
-- 결과: 11
```

### 1-2. v4_desk4_watchlist 확인
```sql
SELECT count(*), status FROM v4_desk4_watchlist GROUP BY status;
-- WATCHING: 11, EXPIRED: 7
```

### 1-3. node_desk4.log 분석 (작업 시작 전)
```
-rw-rw-r-- 1 claudebot claudebot 82 Mar  6 07:05 /root/kis-autotrade-v4/logs/node_desk4.log
DESK4: {'processed': 0, 'starting_signals': 0, 'promote_signals': 0, 'errors': 0}
```
- 날짜: 2026-03-06 07:05 (T-213 FIX-002 적용 **이전**)
- processed=0, errors=0 → stock_codes 리스트가 비어서 반환

---

## 2. 근본 원인 분석

### 원인 1: load_watchlist() 순환 참조 (T-213 이전)

**이전 코드 동작 (T-213 FIX-002 이전)**:
- `load_watchlist()` → `SELECT DISTINCT stock_code FROM v4_node_realtime WHERE desk_level=4`
- v4_node_realtime DESK4 = 0건 → watchlist = [] → processed=0 → v4_node_realtime 갱신 불가
- 완전 순환 참조 데드락

**T-213 FIX-002 이후 현재 코드**:
```python
# Primary: v4_desk4_watchlist WATCHING 종목
cur.execute("SELECT DISTINCT stock_code FROM v4_desk4_watchlist WHERE status = 'WATCHING'")
primary = [r[0] for r in cur.fetchall()]  # 11종목 로드
```

### 원인 2: DESK4 일별 cron 미설치

| 크론 파일 | 설치 여부 |
|---------|---------|
| /etc/cron.d/v41_desk5_scan | ✅ 설치됨 |
| /etc/cron.d/v41_desk2_pool_link | ✅ 설치됨 |
| /etc/cron.d/v41_desk4_scan | ❌ **미설치** |

DESK4 일별 phase 갱신 cron이 없어 T-213 수동 실행 이후로 데이터가 stale 상태였음.

---

## 3. v4_node_realtime 컬럼 구조 확인

```
v4_node_realtime:
  id, stock_code, desk_level, current_phase, phase_confidence
  next_node_est_date, next_node_est_size_pct, updated_at
```

CHECK 제약: current_phase IN ('RISING','PEAK','PULLBACK','BOTTOM','STARTING')

---

## 4. node_detector_desk4.py 코드 분석

### 4-1. classify_phase() 로직
- bars < 25: 기본값 "PULLBACK" 반환
- cur_close > ma20:
  - prev_close < prev_ma20 AND vol_surge(×2배): **"STARTING"** (88 or 80)
  - vol > vol_ma20: "RISING" (75)
  - else: "RISING" (60)
- vol_ma5 < vol_ma20×0.6 AND 눌림깊이 5~12%: **"BOTTOM"** (72)
- else: **"PULLBACK"** (65)

### 4-2. upsert_realtime() 로직
- INSERT INTO v4_node_realtime (desk_level=4) ON CONFLICT UPDATE
- 11종목 × 정상 실행 확인

### 4-3. DESK3 승격 트리거
- BB상단 돌파 + 거래량 3배 + 5일 연속 기관/외국인 순매수

---

## 5. 수동 실행 결과

```bash
cd /root/kis-autotrade-v4
/root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk4
```

**실행 로그**:
```
2026-03-07 01:00:04 INFO load_watchlist FIX-002: primary(v4_desk4_watchlist)=11 secondary(v4_node_realtime)=11 total=11
2026-03-07 01:00:04 INFO DESK4 024740: phase=RISING confidence=75 promote=False
2026-03-07 01:00:04 INFO DESK4 0000D0: phase=RISING confidence=60 promote=False
2026-03-07 01:00:04 INFO DESK4 053050: phase=RISING confidence=75 promote=False
2026-03-07 01:00:04 INFO DESK4 009180: phase=RISING confidence=75 promote=False
2026-03-07 01:00:04 INFO DESK4 0068M0: phase=RISING confidence=60 promote=False
2026-03-07 01:00:04 INFO DESK4 456200: phase=RISING confidence=60 promote=False
2026-03-07 01:00:04 INFO DESK4 0084E0: phase=RISING confidence=60 promote=False
2026-03-07 01:00:04 INFO DESK4 117580: phase=RISING confidence=75 promote=False
2026-03-07 01:00:04 INFO DESK4 012700: phase=PULLBACK confidence=65 promote=False
2026-03-07 01:00:04 INFO DESK4 483030: phase=PULLBACK confidence=65 promote=False
2026-03-07 01:00:04 INFO DESK4 040420: phase=PULLBACK confidence=65 promote=False
DESK4: {'processed': 11, 'starting_signals': 0, 'promote_signals': 0, 'errors': 0}
```

**결과**: processed=11 / RISING×8 / PULLBACK×3 / STARTING=0 / errors=0

---

## 6. v4_node_realtime DESK4 검증

```sql
SELECT stock_code, desk_level, current_phase, phase_confidence, updated_at
FROM v4_node_realtime WHERE desk_level=4 ORDER BY updated_at DESC;
```

| stock_code | current_phase | phase_confidence | updated_at |
|------------|---------------|-----------------|-----------|
| 040420 | PULLBACK | 65 | 2026-03-07 01:00:05 |
| 483030 | PULLBACK | 65 | 2026-03-07 01:00:05 |
| 012700 | PULLBACK | 65 | 2026-03-07 01:00:05 |
| 117580 | RISING | 75 | 2026-03-07 01:00:04 |
| 0084E0 | RISING | 60 | 2026-03-07 01:00:04 |
| 456200 | RISING | 60 | 2026-03-07 01:00:04 |
| 0068M0 | RISING | 60 | 2026-03-07 01:00:04 |
| 009180 | RISING | 75 | 2026-03-07 01:00:04 |
| 053050 | RISING | 75 | 2026-03-07 01:00:04 |
| 0000D0 | RISING | 60 | 2026-03-07 01:00:04 |
| 024740 | RISING | 75 | 2026-03-07 01:00:04 |

**성공 기준 달성: 11행 ≥ 1행 ✅**

---

## 7. DESK5→DESK4 전이 경로 점검

### 7-1. v4_desk5_watchlist 현황
```sql
SELECT count(*), status FROM v4_desk5_watchlist GROUP BY status;
-- WATCHING: 20
```

### 7-2. DESK5→DESK4 전이 메커니즘
**현재 구현된 경로**:
- `desk4_node_scanner.py` `_run_full()`: `v4_desk_positions WHERE desk='DESK5' AND status='OPEN'` 조회 → T4-4 트리거 가산점 (+boolean)
- 즉, DESK5 보유 종목이 DESK4 스캔에서 T4-4 조건으로 유리하게 평가됨

**현재 미구현된 경로** (설계 의도 vs 실제):
- v4_desk5_watchlist → v4_desk4_watchlist **자동 propagation 없음**
- D-012 프랙탈 아키텍처: "DESK5→4→3 파이프라인" 개념적으로 존재하나 코드 구현은 T4-4 보너스 수준에 머무름
- DESK5 watchlist 20종목 → DESK4 watchlist 11종목: 별도 스캔 기준으로 독립적으로 채워짐

### 7-3. 결론: DESK5→4 전이 경로는 "T4-4 트리거 보너스" 수준으로 간접 구현됨
- v4_desk_positions DESK5 OPEN → desk4 full scan에서 T4-4=True 가산
- 직접 propagation (v4_desk5_watchlist → v4_desk4_watchlist) 미구현 → P2 후속 구현 권고

---

## 8. 수정 내용

### 8-1. scripts/desk4/v41_desk4_scan.cron 신규 생성
```cron
# DESK4 노드 감지 (매일 16:05 KST = 07:05 UTC, 평일)
5 7 * * 1-5 root cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk4 >> /root/kis-autotrade-v4/logs/node_desk4.log 2>&1

# DESK4 전수 스캔 (매주 월요일)
5 7 * * 1 root cd /root/kis-autotrade-v4 && ... python3 scripts/desk4/desk4_node_scanner.py --mode full
```

### 8-2. scripts/desk4/install_desk4_scan.sh 신규 생성
root 수동 설치용:
```bash
bash /root/kis-autotrade-v4/scripts/desk4/install_desk4_scan.sh
# 또는:
sudo cp /root/kis-autotrade-v4/scripts/desk4/v41_desk4_scan.cron /etc/cron.d/v41_desk4_scan
sudo chmod 644 /etc/cron.d/v41_desk4_scan
```

⚠️ **root 수동 설치 필요**: claudebot은 /etc/cron.d/ write 권한 없음

---

## 9. 성공 기준 달성 여부

| 기준 | 결과 |
|------|------|
| v4_node_realtime DESK4 >= 1행 | ✅ 11행 확인 |
| 원인 식별 | ✅ 순환참조(T-213 해소) + 크론 미설치 |
| 수동 실행 성공 | ✅ processed=11/11 |
| DESK5→4 전이 경로 점검 | ✅ T4-4 보너스 간접구현 확인 |
| 크론 파일 생성 | ✅ scripts/desk4/v41_desk4_scan.cron |

---

## 10. 후속 조치 필요

| 항목 | 우선순위 | 담당 |
|------|---------|------|
| /etc/cron.d/v41_desk4_scan 설치 | P1 | root 수동 |
| DESK5→DESK4 직접 propagation 구현 | P2 | 후속 Task |
| STARTING phase 발생 조건 최적화 (현재 0건) | P2 | 후속 Task |

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-DESK4-NODE-REALTIME-FIX-001-20260307.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-DESK4-NODE-REALTIME-FIX-001-20260307.md
- 커밋: (push 후 업데이트)
- HTTP 확인: (push 후 확인)
- HANDOVER 업데이트: 완료 예정
