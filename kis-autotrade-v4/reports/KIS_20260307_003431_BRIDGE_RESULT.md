---
project: KIS AutoTrade V4.1
task_id: T-239
completed_at: 2026-03-07 01:15 KST
---

# T-239 DESK4 v4_node_realtime 데이터 미생성 원인 분석 및 수정 — 실행 결과

## 지시서 원문
Task ID: T-239 제목: DESK4 v4_node_realtime 데이터 미생성 원인 분석 및 수정 서버: 211 (kis-autotrade-v4) 우선순위: P1-HIGH 예상 시간: 30분 의존성: T-226

배경: T-202 결과에서 v4_node_realtime에 DESK4 데이터가 0건. T-213에서 watchlist(11종목) 로드는 수정되었으나 phase 데이터가 생성되지 않아 DESK4 트리거 불가.

수행 내용:
- node_detector_desk4.py 코드 분석: v4_node_realtime INSERT/UPDATE 로직 확인
- SELECT count(*) FROM v4_node_realtime WHERE desk_level=4 — 0건이면:
- node_detector가 INSERT하는 조건 확인
- watchlist 11종목에 대해 수동 실행 후 INSERT 여부 확인
- 필요 시 node_detector_desk4.py에 watchlist→node_realtime 전파 로직 추가
- 수동 실행 후 v4_node_realtime DESK4 행 수 ≥ 1 확인
- DESK5→4 전이 경로도 점검 (v4_desk5_watchlist → v4_desk4_watchlist 전파 로직)

성공 기준: v4_node_realtime DESK4 데이터 ≥ 1행 + 원인 식별 보고서: CUR-V41-DESK4-NODE-REALTIME-FIX-001-20260309.md 완료 후: HANDOVER 갱신 + git push

---

## 단계별 실행 내용 및 결과

### 단계 1: 인계서 확인

#### HANDOVER.md 확인 (v10.43)
- 최신 업데이트: T-229/T-230/T-237/T-234/T-228/T-231 완료 확인
- T-239 진행 중(running) 상태 확인

#### CEO-DIRECTIVES.md 확인
- D-003: DESK의 본질 = 풀 관리 + 전략 트리거 대기
- D-012: 프랙탈 추세추종 아키텍처 v2.0 (DESK5→4→3 파이프라인)
- D-013: 전 DESK 손익비 추세추종 원칙

---

### 단계 2: 초기 DB 상태 확인

#### 명령어:
```sql
SELECT count(*) FROM v4_node_realtime WHERE desk_level=4;
```

#### 결과:
```
 count
-------
    11
(1 row)
```

→ 0건이 아닌 **11건** 존재. T-213 FIX-002 이후 수동 실행으로 생성된 데이터.

#### v4_node_realtime DESK4 상세:
```
 stock_code | desk_level | current_phase | phase_confidence |          updated_at
------------+------------+---------------+------------------+-------------------------------
 040420     |          4 | PULLBACK      |               65 | 2026-03-07 00:22:57.862113+09
 483030     |          4 | PULLBACK      |               65 | 2026-03-07 00:22:57.821217+09
 012700     |          4 | PULLBACK      |               65 | 2026-03-07 00:22:57.779144+09
 117580     |          4 | RISING        |               75 | 2026-03-07 00:22:57.739576+09
 0084E0     |          4 | RISING        |               60 | 2026-03-07 00:22:57.698794+09
 456200     |          4 | RISING        |               60 | 2026-03-07 00:22:57.656514+09
 0068M0     |          4 | RISING        |               60 | 2026-03-07 00:22:57.616518+09
 009180     |          4 | RISING        |               75 | 2026-03-07 00:22:57.57713+09
 053050     |          4 | RISING        |               75 | 2026-03-07 00:22:57.536961+09
 0000D0     |          4 | RISING        |               60 | 2026-03-07 00:22:57.491+09
 024740     |          4 | RISING        |               75 | 2026-03-07 00:22:57.447151+09
(11 rows)
```

#### v4_desk4_watchlist 상태:
```
 count |  status
-------+----------
     7 | EXPIRED
    11 | WATCHING
(2 rows)
```

---

### 단계 3: node_detector_desk4.py 코드 분석

#### 파일 위치:
`/root/kis-autotrade-v4/backend/app/services/desk_filters/node_detector_desk4.py`

#### load_watchlist() FIX-002 확인 (T-213 적용 완료):
```python
def load_watchlist(self) -> List[str]:
    # Primary: v4_desk4_watchlist WATCHING 종목
    cur.execute("SELECT DISTINCT stock_code FROM v4_desk4_watchlist WHERE status = 'WATCHING'")
    primary = [r[0] for r in cur.fetchall()]  # 11종목

    # Secondary: v4_node_realtime (보조 참조, 빈 경우 무시)
    cur.execute("SELECT DISTINCT stock_code FROM v4_node_realtime WHERE desk_level = 4")
    secondary = [r[0] for r in cur.fetchall()]  # 11종목

    # 중복 제거, primary 우선
    combined = primary + [s for s in secondary if s not in primary_set]
    return combined  # 총 11종목
```

#### classify_phase() 로직:
- bars < 25: 기본값 "PULLBACK" 반환
- cur_close > ma20:
  - prev_close < prev_ma20 AND vol_surge(×2배): "STARTING" (88 or 80)
  - vol > vol_ma20: "RISING" (75)
  - else: "RISING" (60)
- vol_ma5 < vol_ma20×0.6 AND 눌림깊이 5~12%: "BOTTOM" (72)
- else: "PULLBACK" (65)

#### upsert_realtime() 로직:
```python
INSERT INTO v4_node_realtime
    (stock_code, desk_level, current_phase, phase_confidence, ...)
VALUES (%s, 4, %s, %s, %s, %s, NOW())
ON CONFLICT (stock_code, desk_level) DO UPDATE
    SET current_phase = EXCLUDED.current_phase,
        phase_confidence = EXCLUDED.phase_confidence,
        ...
        updated_at = NOW()
```

---

### 단계 4: 로그 파일 분석

#### 명령어:
```bash
ls -la /root/kis-autotrade-v4/logs/node_desk4.log
cat /root/kis-autotrade-v4/logs/node_desk4.log
```

#### 결과:
```
-rw-rw-r-- 1 claudebot claudebot 82 Mar  6 07:05 /root/kis-autotrade-v4/logs/node_desk4.log
DESK4: {'processed': 0, 'starting_signals': 0, 'promote_signals': 0, 'errors': 0}
```

**핵심 발견**: 로그 생성 시간 = 2026-03-06 07:05 → T-213 FIX-002 적용 **이전**에 실행된 것.
T-213 이전에는 load_watchlist()가 v4_node_realtime(0행)을 읽어 순환참조 데드락 발생.

---

### 단계 5: 크론 설치 현황 확인

#### 명령어:
```bash
ls /etc/cron.d/ | grep -i desk
```

#### 결과:
```
(아무것도 없음)
```

#### v41 크론 목록:
```
v41_desk2_pool_link  ← 설치됨
v41_desk5_scan       ← 설치됨
v41_evolution_loop   ← 설치됨
v41_manager_snapshot ← 설치됨
v41_research_loop    ← 설치됨
```

**v41_desk4_scan = 설치되지 않음** ← 이것이 2번째 근본 원인

---

### 단계 6: DESK5→DESK4 전이 경로 점검

#### v4_desk5_watchlist 현황:
```
SELECT count(*), status FROM v4_desk5_watchlist GROUP BY status;
-- WATCHING: 20
```

#### 전이 경로 분석:

**desk4_node_scanner.py `_run_full()` 코드**:
```python
# DESK5 보유 종목
with conn.cursor(cursor_factory=RealDictCursor) as cur:
    cur.execute(
        "SELECT DISTINCT stock_code FROM v4_desk_positions WHERE desk='DESK5' AND status='OPEN'"
    )
    desk5_holdings = {r["stock_code"] for r in cur.fetchall()}

...
t4_4 = sc in desk5_holdings and ind["vol_ratio_5"] >= _t4_4_vol
```

**결론**: DESK5→DESK4 전이는 v4_desk_positions DESK5 OPEN 종목에 T4-4 트리거 보너스 형태로 간접 구현됨.
v4_desk5_watchlist → v4_desk4_watchlist 직접 propagation 코드는 없음 (P2 후속 구현 권고).

---

### 단계 7: 수동 실행

#### 명령어:
```bash
cd /root/kis-autotrade-v4
/root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk4
```

#### 전체 출력:
```
2026-03-07 01:00:04,501 INFO load_watchlist FIX-002: primary(v4_desk4_watchlist)=11 secondary(v4_node_realtime)=11 total=11
2026-03-07 01:00:04,551 INFO DESK4 024740: phase=RISING confidence=75 promote=False
2026-03-07 01:00:04,603 INFO DESK4 0000D0: phase=RISING confidence=60 promote=False
2026-03-07 01:00:04,674 INFO DESK4 053050: phase=RISING confidence=75 promote=False
2026-03-07 01:00:04,734 INFO DESK4 009180: phase=RISING confidence=75 promote=False
2026-03-07 01:00:04,800 INFO DESK4 0068M0: phase=RISING confidence=60 promote=False
2026-03-07 01:00:04,871 INFO DESK4 456200: phase=RISING confidence=60 promote=False
2026-03-07 01:00:04,923 INFO DESK4 0084E0: phase=RISING confidence=60 promote=False
2026-03-07 01:00:04,982 INFO DESK4 117580: phase=RISING confidence=75 promote=False
2026-03-07 01:00:05,034 INFO DESK4 012700: phase=PULLBACK confidence=65 promote=False
2026-03-07 01:00:05,091 INFO DESK4 483030: phase=PULLBACK confidence=65 promote=False
2026-03-07 01:00:05,145 INFO DESK4 040420: phase=PULLBACK confidence=65 promote=False
DESK4: {'processed': 11, 'starting_signals': 0, 'promote_signals': 0, 'errors': 0}
```

---

### 단계 8: v4_node_realtime DESK4 최종 검증

#### 명령어:
```sql
SELECT stock_code, desk_level, current_phase, phase_confidence, updated_at
FROM v4_node_realtime WHERE desk_level=4 ORDER BY updated_at DESC;
```

#### 결과:
```
 stock_code | desk_level | current_phase | phase_confidence |          updated_at
------------+------------+---------------+------------------+-------------------------------
 040420     |          4 | PULLBACK      |               65 | 2026-03-07 01:00:05.141811+09
 483030     |          4 | PULLBACK      |               65 | 2026-03-07 01:00:05.08716+09
 012700     |          4 | PULLBACK      |               65 | 2026-03-07 01:00:05.030232+09
 117580     |          4 | RISING        |               75 | 2026-03-07 01:00:04.979653+09
 0084E0     |          4 | RISING        |               60 | 2026-03-07 01:00:04.91985+09
 456200     |          4 | RISING        |               60 | 2026-03-07 01:00:04.865554+09
 0068M0     |          4 | RISING        |               60 | 2026-03-07 01:00:04.797307+09
 009180     |          4 | RISING        |               75 | 2026-03-07 01:00:04.72913+09
 053050     |          4 | RISING        |               75 | 2026-03-07 01:00:04.656831+09
 0000D0     |          4 | RISING        |               60 | 2026-03-07 01:00:04.599681+09
 024740     |          4 | RISING        |               75 | 2026-03-07 01:00:04.546738+09
(11 rows)
```

**성공 기준 달성: 11행 ≥ 1행 ✅**

#### 최종 확인:
```sql
SELECT count(*) as desk4_rows FROM v4_node_realtime WHERE desk_level=4;
-- 결과: 11
```

---

### 단계 9: 크론 파일 생성

#### 생성 파일 1: /root/kis-autotrade-v4/scripts/desk4/v41_desk4_scan.cron
```cron
# V4.1 DESK4 스캔 크론 (T-239)
# 설치: sudo cp /root/kis-autotrade-v4/scripts/desk4/v41_desk4_scan.cron /etc/cron.d/v41_desk4_scan
#        sudo chmod 644 /etc/cron.d/v41_desk4_scan

SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# DESK4 노드 감지 (매일 16:05 KST = 07:05 UTC, 평일)
5 7 * * 1-5 root cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 -m backend.app.services.node_detector_engine desk4 >> /root/kis-autotrade-v4/logs/node_desk4.log 2>&1

# DESK4 전수 스캔 (매주 월요일 16:05 KST)
5 7 * * 1 root cd /root/kis-autotrade-v4 && source /root/kis-autotrade-v4/venv/bin/activate && set -a && source /root/kis-autotrade-v4/.env && set +a && python3 /root/kis-autotrade-v4/scripts/desk4/desk4_node_scanner.py --mode full >> /root/kis-autotrade-v4/logs/cron/desk4_full_scan_$(date +\%Y\%m\%d).log 2>&1
```

#### 생성 파일 2: /root/kis-autotrade-v4/scripts/desk4/install_desk4_scan.sh

#### /etc/cron.d/ 설치 시도:
```bash
sudo /usr/bin/cp /root/kis-autotrade-v4/scripts/desk4/v41_desk4_scan.cron /etc/cron.d/v41_desk4_scan
# → sudo: a terminal is required to read the password
# claudebot은 /etc/cron.d/ write 권한 없음 → root 수동 설치 필요
```

---

### 단계 10: 보고서 작성 및 push

#### 보고서 파일:
- 로컬: `/root/kis-autotrade-v4/report/v41/CUR-V41-DESK4-NODE-REALTIME-FIX-001-20260307.md`
- project-docs: `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-DESK4-NODE-REALTIME-FIX-001-20260307.md`

#### push 결과:
```
[master 94aa9b6] docs: T-239 DESK4 v4_node_realtime 원인분석+수정 보고서 (20260307)
 1 file changed, 241 insertions(+)
 create mode 100644 kis-autotrade-v4/reports/CUR-V41-DESK4-NODE-REALTIME-FIX-001-20260307.md
To github.com:moongoby/project-docs.git
   6cc5023..94aa9b6  master -> master
```

#### HTTP 확인:
```bash
curl -s -o /dev/null -w "%{http_code}" "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-DESK4-NODE-REALTIME-FIX-001-20260307.md"
# → 200
```

---

### 단계 11: HANDOVER.md 업데이트

#### 추가 내용:
- v10.44 섹션: T-239 완료 내용 기록
- 섹션 2 완료된 작업 테이블: T-239 행 추가

#### push 결과:
```
[master d27dbb3] docs: HANDOVER 업데이트 (T-239 완료)
 1 file changed, 1 insertion(+)
To github.com:moongoby/project-docs.git
   4df817b..d27dbb3  master -> master
```

#### HTTP 확인:
```bash
curl -s -o /dev/null -w "%{http_code}" "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md"
# → 200
```

---

### 단계 12: kis-autotrade-v4 코드 커밋

#### 커밋 결과:
```
[phase-2c-command-center 7c9252d4] [V4.1] feat: T-239 DESK4 v4_node_realtime cron 생성 + 원인분석 보고서
 3 files changed, 271 insertions(+)
 create mode 100644 report/v41/CUR-V41-DESK4-NODE-REALTIME-FIX-001-20260307.md
 create mode 100644 scripts/desk4/install_desk4_scan.sh
 create mode 100644 scripts/desk4/v41_desk4_scan.cron
```

---

## 최종 성공 기준 달성 현황

| 기준 | 결과 |
|------|------|
| v4_node_realtime DESK4 >= 1행 | ✅ **11행** 확인 (2026-03-07 01:00 KST) |
| 원인 식별 | ✅ ①순환참조(T-213 해소) ②cron 미설치 |
| 수동 실행 성공 | ✅ processed=11/11 errors=0 |
| DESK5→4 전이 경로 점검 | ✅ T4-4 보너스 간접구현 확인 |
| 크론 파일 생성 | ✅ scripts/desk4/v41_desk4_scan.cron |
| 보고서 push HTTP 200 | ✅ 94aa9b6 / HTTP 200 |
| HANDOVER 업데이트 | ✅ d27dbb3 / HTTP 200 |
| 코드 커밋 | ✅ 7c9252d4 |

---

## 후속 조치 필요사항

| 항목 | 우선순위 | 담당 |
|------|---------|------|
| /etc/cron.d/v41_desk4_scan 설치 (`bash /root/kis-autotrade-v4/scripts/desk4/install_desk4_scan.sh`) | P1 | root 수동 |
| DESK5→DESK4 직접 propagation 구현 (v4_desk5_watchlist → v4_desk4_watchlist) | P2 | 후속 Task |
| STARTING phase 발생 조건 최적화 (현재 0건) | P2 | 후속 Task |

---

## CEO 보고 형식 (REPORT-001)

보고서: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-DESK4-NODE-REALTIME-FIX-001-20260307.md
커밋: https://github.com/moongoby/project-docs/commit/94aa9b6
HANDOVER: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/HANDOVER.md
HTTP: 200 확인 완료

HANDOVER.md 업데이트 완료: d27dbb3
