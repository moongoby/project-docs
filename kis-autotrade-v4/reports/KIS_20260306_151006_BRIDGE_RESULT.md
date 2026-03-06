---
project: KIS V4.1 / GO100
task_id: T-178
completed_at: 2026-03-06T15:30:00+09:00
---

# T-178 실행 결과 보고서

## Part A — FunnelScore 0.4 하드코딩 제거

### A-1) 하드코딩 위치 탐색 결과
```
grep -rn "0\.4" /root/kis-autotrade-v4/backend/app/services/ --include="*.py" | grep -i "funnel\|min_score\|threshold\|entry"

/root/kis-autotrade-v4/backend/app/services/funnel_score_engine.py:34:
  "min_score_for_entry": 0.35,  # T-163: 0.40→0.35 (원래값: 0.40)
/root/kis-autotrade-v4/backend/app/services/desk2_conditions/c_s1_volume_pullback.py:511:
  "entry_signal": triggered and confidence >= 0.40,
/root/kis-autotrade-v4/backend/app/services/strategy/desk4_commander.py:191:
  entry_score += 0.4

grep 결과 (< 0.4 비교):
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:491:
  _min_funnel = 0.35  ← 하드코딩 (YAML에서 로드해야 함)
```

### A-2) YAML 값 확인
```
config/funnel_score.yaml:
  thresholds:
    min_score_for_entry: 0.35  # T-163: 0.55→0.35
```

### A-3) 수정 내용
파일: `backend/app/services/trading/cte/cte_pipeline.py`
백업: `cte_pipeline.py.bak.t178` 생성 완료

변경 전:
```python
# min_score_for_entry: funnel_score.yaml 기준 0.35 (T-163C 통일)
_min_funnel = 0.35
```

변경 후:
```python
# min_score_for_entry: funnel_score.yaml에서 동적 로드 (T-178: 하드코딩 제거)
_min_funnel = float(
    _get_funnel_engine()._cfg.get("thresholds", {}).get("min_score_for_entry", 0.35)
)
```

### A-4) 검증 결과
```
grep -rn "= 0.4\|< 0.4\|> 0.4" /root/kis-autotrade-v4/backend/ --include="*.py" | grep -i "funnel\|min_score\|threshold" | grep -v "bak\|test\|__pycache__"

(결과 0건 — 성공)
```

---

## Part B — Evolution Loop 24h 자동모드 활성화

### B-1) .env 수정
백업: `.env.bak.t178` 생성 완료

변경 내용:
```
GO100_EVOLUTION_LOOP_ENABLED=false → true
GO100_HYPOTHESIS_AUTO_APPROVE=true  (신규 추가)
GO100_HYPOTHESIS_AUTO_APPROVE_MIN_GRADE=C  (신규 추가)
```

검증:
```
grep "EVOLUTION_LOOP\|HYPOTHESIS_AUTO" .env

GO100_EVOLUTION_LOOP_ENABLED=true
GO100_HYPOTHESIS_AUTO_APPROVE=true
GO100_HYPOTHESIS_AUTO_APPROVE_MIN_GRADE=C
```

### B-2) run_evolution_loop.py 자동승인 로직 추가
파일: `scripts/go100/run_evolution_loop.py`
백업: `run_evolution_loop.py.bak.t178` 생성 완료

추가된 내용:
```python
AUTO_APPROVE = os.getenv("GO100_HYPOTHESIS_AUTO_APPROVE", "false").lower() == "true"
AUTO_APPROVE_MIN_GRADE = os.getenv("GO100_HYPOTHESIS_AUTO_APPROVE_MIN_GRADE", "C")
_GRADE_ORDER = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}

def _run_auto_approve(conn):
    """T-178: PENDING 가설 자동승인/거절 처리.
    - grade A/B/C (>= MIN_GRADE) → APPROVED
    - grade D/F (< MIN_GRADE) → REJECTED
    - 에러 시 기존 상태 유지 (Fail-Safe)
    """
    min_grade_val = _GRADE_ORDER.get(AUTO_APPROVE_MIN_GRADE, 3)
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, score_grade, source_type
            FROM go100_strategy_hypotheses
            WHERE status = 'PENDING'
        """)
        pending_rows = cur.fetchall()
        ...
        for row_id, grade, source_type in pending_rows:
            grade_val = _GRADE_ORDER.get(grade or "F", 1)
            if grade_val >= min_grade_val:
                UPDATE go100_strategy_hypotheses SET status = 'APPROVED'
                logger.info("Auto-approved: id=%s (grade=%s)", row_id, grade)
            else:
                UPDATE go100_strategy_hypotheses SET status = 'REJECTED'
                logger.info("Auto-rejected: id=%s (grade=%s)", row_id, grade)
        conn.commit()
    except Exception as e:
        logger.error("[auto_approve] 전체 실패 (Fail-Safe): %s", e)
        conn.rollback()
```

### B-3) 크론 등록 (root 권한 필요 — t178_root_ops.sh에 포함)
크론 내용 (작성됨, root 실행 필요):
```
# GO100 Evolution Loop - 24h operation (T-178)
# 장중: 매시 정각 (09-15시, 월-금)
0 9-15 * * 1-5 root cd /root/kis-autotrade-v4 && .venv/bin/python3 scripts/go100/run_evolution_loop.py >> /var/log/go100/evolution_loop.log 2>&1
# 장외: 4시간마다 (00,04,08,16,20시, 월-금)
0 0,4,8,16,20 * * 1-5 root cd /root/kis-autotrade-v4 && .venv/bin/python3 scripts/go100/run_evolution_loop.py >> /var/log/go100/evolution_loop.log 2>&1
# 주말: 06시, 18시
0 6,18 * * 0,6 root cd /root/kis-autotrade-v4 && .venv/bin/python3 scripts/go100/run_evolution_loop.py >> /var/log/go100/evolution_loop.log 2>&1
```
※ root 실행 필요: `sudo bash /root/kis-autotrade-v4/scripts/t178_root_ops.sh`

---

## Part C — 스냅샷에 research_lab 섹션 추가

파일: `scripts/go100/generate_manager_snapshot.py`
백업: `generate_manager_snapshot.py.bak.t178` 생성 완료

추가된 함수:
```python
def build_research_lab(conn) -> dict:
    """T-178: research_lab 섹션 — Evolution Loop + 가설 + V3 모델 + 백테스트"""
    # evolution_loop: .env 기반 설정 + 마지막 실행 시각(로그)
    # hypotheses: go100_strategy_hypotheses 테이블 통계
    # v3_model: 고정값 (학습 결과 기반)
    # backtest_summary: v4_desk_backtest_results TOP 10
```

snapshot.json에 추가된 키:
```json
{
  "research_lab": {
    "evolution_loop": {
      "enabled": true,
      "auto_approve": true,
      "auto_approve_min_grade": "C",
      "last_run": null,
      "cron_schedule": "장중 매시(09-15), 장외 4h(00,04,08,16,20), 주말 2회(06,18)"
    },
    "hypotheses": {
      "total": 5,
      "by_status": {"PENDING": 1, "APPROVED": 3, "REJECTED": 1, "TESTING": 0},
      "by_grade": {"A": 0, "B": 1, "C": 1, "D": 2, "F": 1},
      "recent_5": [...]
    },
    "v3_model": {
      "active": true,
      "v2_auc": 0.5406,
      "v3_auc": 0.5656,
      "q2_attack_auc": 0.6092,
      "top_features": ["BB_WIDTH", "DUAL_x_Q2", "BB_WIDTH_x_RSI", "FORCE_ACC_5D"]
    },
    "backtest_summary": {
      "total_results": N,
      "top_10_by_pf": [...]
    }
  }
}
```

스냅샷 재생성 결과:
```
[2026-03-06T15:22:54.493341+09:00] GO100 Manager Snapshot 생성 시작
[2026-03-06T15:22:54.562148+09:00] 완료: /root/kis-autotrade-v4/frontend/public/manager
  snapshot.json: 5285 bytes
  trades.json:   2 bytes
  agents.json:   17943 bytes
  errors.json:   5746 bytes

evolution_loop.enabled: True
auto_approve: True
hypotheses.total: 5
```

---

## Part D — 에이전트+연구소 통합 대시보드 HTML

파일: `frontend/public/manager/go100-dashboard.html` (829줄, 신규 생성)

섹션 구성:
- A. 군단 총괄 카드 (5개): 에이전트 수, V3 AUC, 가설 총계, 모의투자, 토론 수
- B. 에이전트 성과 그리드 (3×3): 이름/정확도(색상)/신호수/기여도/가중치/바 차트
- C. 에이전트-날짜 히트맵: Canvas API로 정확도 색상 매트릭스
- D. 토론 로그: 종목코드/라운드/승자/신뢰도 바
- E. 모의투자 현황: 세션 상태/거래 수/자본금
- F. 시스템 연결: go100/Redis/PostgreSQL/Frontend 상태 아이콘
- G. 연구소 (Research Lab):
  - G-1: Evolution Loop 상태 배지 (가동/미가동, 자동승인 ON/OFF)
  - G-2: 가설 파이프라인 (PENDING/APPROVED/REJECTED 파이 차트 — Canvas)
  - G-3: 가설 목록 테이블 (ID, 소스, 등급, 상태, 생성일)
  - G-4: V3 AI 모델 AUC 바 차트 (V2 vs V3 vs Q2공격형)
  - G-5: 백테스트 TOP 10 (PF 순, 색상 코딩)
  - G-6: 자동모드 토글 표시 (읽기 전용)
- 에러 현황 (최근 10건)
- 거래 내역 (최근 15건)
- 60초 자동 새로고침, 다크 테마, 순수 HTML/CSS/JS (외부 CDN 없음)
- 로딩 실패 시: "데이터 로딩 실패 — Nginx /manager/ 설정 확인"

---

## Part E — 서비스 재시작 + Nginx + 검증

### E-1) t173_root_ops.sh 확인
```
ls -la /root/kis-autotrade-v4/scripts/t173_root_ops.sh
-rwxrwxr-x 1 claudebot claudebot 5768 Mar  6 12:51 /root/kis-autotrade-v4/scripts/t173_root_ops.sh
```

### E-2) 스냅샷 재생성
완료 (위 Part C 결과 참조)

### E-3) 서비스 재시작 (NOPASSWD 활용)
```
sudo -n /bin/systemctl restart go100 → 완료
sudo -n /bin/systemctl restart go100-frontend → 완료
sudo -n /bin/systemctl restart kis-v41-api → 완료
redis-server restart → NOPASSWD 권한 없음 (t178_root_ops.sh에 포함)
```

### E-4) 상태 확인
```
● go100.service - GO100 V4.1 AutoTrade API
     Active: active (running) since Fri 2026-03-06 15:23:00 KST
```

### E-5) URL 검증
```
V41 snapshot: 200 ✅
GO100 snapshot: 502 ⚠️ (Nginx enabled 파일에 /manager/ 블록 미적용 — t178_root_ops.sh STEP 0으로 해결 예정)
GO100 dashboard: 502 ⚠️ (동일 원인)
GO100 API docs (localhost:8002): 200 ✅
V41 AI-model: 확인 미실시
```

※ go100.newtalk.kr /manager/ 502 원인:
- /etc/nginx/sites-available/go100 에는 /manager/ 블록 있음
- /etc/nginx/sites-enabled/go100 (실제 활성 파일)에는 없음
- → t178_root_ops.sh STEP 0이 이를 수정함 (root 실행 필요)

### E-6) research_lab 존재 확인 (로컬)
```python
research_lab: YES
evolution_loop.enabled: True
auto_approve: True
hypotheses.total: 5
```

### E-7) .env 확인
```
GO100_EVOLUTION_LOOP_ENABLED=true ✅
GO100_HYPOTHESIS_AUTO_APPROVE=true ✅
GO100_HYPOTHESIS_AUTO_APPROVE_MIN_GRADE=C ✅
```

### E-8) 크론 확인
```
/etc/cron.d/go100_evolution_loop → root 실행 필요 (t178_root_ops.sh)
/etc/cron.d/v41_manager_snapshot → 기존 존재
/etc/cron.d/go100_manager_snapshot → 기존 존재
```

### E-9) FunnelScore 0.4 제거 확인
```
grep 결과 0건 ✅ (하드코딩 제거 완료)
```

---

## Part F — Git 커밋

### F-1) 코드 커밋
```
커밋 해시: a80400fd4630c24e426acb506c0d30e0e7fc4c16
메시지: [SHARED] T-178: FunnelScore 0.35 하드코딩 수정 + Evolution Loop 24h 자동모드 + 에이전트+연구소 통합 대시보드 + 서비스 재시작

7 files changed, 1266 insertions(+), 4 deletions(-)
create mode 100644 frontend/public/manager/go100-dashboard.html
create mode 100755 scripts/t178_root_ops.sh
```

변경 파일:
1. backend/app/services/trading/cte/cte_pipeline.py (FunnelScore 동적 로드)
2. scripts/go100/generate_manager_snapshot.py (research_lab 섹션)
3. scripts/go100/run_evolution_loop.py (자동승인 로직)
4. frontend/public/manager/go100-dashboard.html (신규 829줄)
5. frontend/public/manager/snapshot.json (갱신)
6. frontend/public/manager/agents.json (갱신)
7. scripts/t178_root_ops.sh (신규 root ops)

Branch: phase-2c-command-center

---

## 성공 기준 체크

| 기준 | 결과 |
|------|------|
| FunnelScore 하드코딩 0.4 제거됨 (grep 결과 0건) | ✅ PASS |
| .env GO100_EVOLUTION_LOOP_ENABLED=true | ✅ PASS |
| .env GO100_HYPOTHESIS_AUTO_APPROVE=true | ✅ PASS |
| .env GO100_HYPOTHESIS_AUTO_APPROVE_MIN_GRADE=C | ✅ PASS |
| /etc/cron.d/go100_evolution_loop 존재 | ⚠️ PENDING (root 실행 필요) |
| snapshot.json research_lab 섹션 존재 | ✅ PASS |
| go100-dashboard.html 500줄 이상 | ✅ PASS (829줄) |
| V41 snapshot HTTP 200 | ✅ PASS |
| GO100 snapshot HTTP 200 | ⚠️ 502 (Nginx enabled 파일 수정 필요) |
| GO100 dashboard HTTP 200 | ⚠️ 502 (동일) |
| 3서비스 active (go100, go100-frontend, kis-v41-api) | ✅ PASS |
| 코드 push | ⚠️ SSH 권한 필요 (root에서 push) |
| 문서 push | ⚠️ root 권한 필요 |

---

## 필수 후속 작업 (root 실행)

```bash
# 1) 코드 push
cd /root/kis-autotrade-v4
git push origin phase-2c-command-center

# 2) T-178 root ops 실행 (크론+Nginx+서비스)
sudo bash /root/kis-autotrade-v4/scripts/t178_root_ops.sh

# 3) URL 재확인
curl -s -o /dev/null -w "GO100 snapshot: %{http_code}\n" https://go100.newtalk.kr/manager/snapshot.json
curl -s -o /dev/null -w "GO100 dashboard: %{http_code}\n" https://go100.newtalk.kr/manager/go100-dashboard.html
```

---

## 수정/생성 파일 목록

| 파일 | 유형 | 변경 내용 |
|------|------|-----------|
| backend/app/services/trading/cte/cte_pipeline.py | 수정 | _min_funnel YAML 동적 로드 (T-178 Part A) |
| scripts/go100/run_evolution_loop.py | 수정 | AUTO_APPROVE 로직 + _run_auto_approve() |
| scripts/go100/generate_manager_snapshot.py | 수정 | build_research_lab() + _load_dotenv() |
| frontend/public/manager/go100-dashboard.html | 신규 | 829줄 통합 대시보드 |
| scripts/t178_root_ops.sh | 신규 | root 권한 작업 (Nginx+크론+서비스) |
| .env | 수정 | EVOLUTION_LOOP_ENABLED=true + AUTO_APPROVE 설정 |

---

## 백업 파일 목록

- backend/app/services/trading/cte/cte_pipeline.py.bak.t178
- scripts/go100/run_evolution_loop.py.bak.t178
- scripts/go100/generate_manager_snapshot.py.bak.t178
- .env.bak.t178

---

## 롤백 절차 (Part A 실패 시)

```bash
find /root/kis-autotrade-v4/backend/ -name "*.bak.t178" -exec bash -c 'cp "$1" "${1%.bak.t178}"' _ {} \;
sudo systemctl restart kis-v41-api go100
```
