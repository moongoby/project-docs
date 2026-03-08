# CUR-V41-T286-BACKTEST-PROGRESS-001-20260308

**Task ID**: T-286
**제목**: /api/v4/backtest/progress 엔드포인트 구현 (404 해결)
**날짜**: 2026-03-08
**작성자**: Claude Code (Sonnet 4.6)
**HANDOVER**: v10.69

---

[인계 확인]
직전 완료: T-285
현재 단계: Phase 2c Command Center
CEO 지시 적용: D-001 (서비스 재시작 금지), D-002 (DB 직접 수정 금지)
strategy_cards: 60
open_positions: 0

---

## 1. 배경

HANDOVER v10.37 기록: `/api/v4/backtest/progress` → 404 (미구현)
admin.html 대시보드에서 백테스트 진행률을 조회하나 현재 404 반환.
`go100_research_iterations` 테이블에 백테스트 세션 상태가 저장됨.

---

## 2. STEP 1: 현황 파악

### 2-1. 기존 코드 유무 확인

```
grep -r "backtest/progress" /root/kis-autotrade-v4/backend/
결과: backend/app/api/v4_backtest_api.py:622:@router.get("/backtest/progress/{session_id}")
```

→ `/backtest/progress/{session_id}` (동적, session_id 필요)는 존재
→ `/backtest/progress` (정적, 집계용)는 **미존재 → 404 원인**

### 2-2. 관련 라우터 파일

```
backend/app/routers/v4_backtest.py      (prefix=/api/v4)
backend/app/api/v4_backtest_api.py      (prefix=/api/v4) ← 구현 대상
backend/app/routers/go100/backtest_router.py
backend/app/routers/backtest_router.py
```

`v4_backtest_api.py`: `router = APIRouter(prefix="/api/v4", tags=["V4 Backtest (Dashboard)"])`
main.py: `app.include_router(v4_backtest_api_router)` (no additional prefix)

### 2-3. go100_research_iterations 스키마

```sql
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name='go100_research_iterations' ORDER BY ordinal_position;
```

| column_name     | data_type                |
|-----------------|--------------------------|
| id              | integer                  |
| hypothesis_id   | integer                  |
| iteration_num   | integer                  |
| phase           | character varying         |
| params          | jsonb                    |
| result          | jsonb                    |
| profit_factor   | numeric                  |
| win_rate        | numeric                  |
| max_drawdown    | numeric                  |
| total_trades    | integer                  |
| converge_status | character varying         |
| created_at      | timestamp with time zone |

→ **`status` 컬럼 없음** → `converge_status` 사용
→ `session_id` 컬럼 없음 → `id` 매핑
→ `completed_at` 컬럼 없음 → null 반환

### 2-4. 현재 데이터 분포

```sql
SELECT converge_status, count(*) FROM go100_research_iterations GROUP BY converge_status;
 converge_status | count
-----------------+-------
 CONVERGED       |     3
```

총 3건, 전부 CONVERGED.

---

## 3. STEP 2: 엔드포인트 구현

### 구현 파일

`/root/kis-autotrade-v4/backend/app/api/v4_backtest_api.py`

### 구현 내용

기존 `@router.get("/backtest/progress/{session_id}")` 앞에 정적 라우트 삽입.

```python
@router.get("/backtest/progress")
async def backtest_progress_overview(db: AsyncSession = Depends(get_db)):
    """go100_research_iterations 기반 백테스트 전체 진행률 조회. T-286."""
    # 상태별 집계
    r_counts = await db.execute(
        text("""
        SELECT converge_status AS status, COUNT(*) AS cnt
        FROM go100_research_iterations
        GROUP BY converge_status
        """)
    )
    counts_rows = r_counts.fetchall()
    status_map: dict = {}
    for row in counts_rows:
        m = _row_to_dict(row)
        status_map[str(m.get("status") or "").upper()] = int(m.get("cnt") or 0)

    total = sum(status_map.values())
    completed = status_map.get("CONVERGED", 0)
    running = status_map.get("RUNNING", 0)
    failed = status_map.get("FAILED", 0)
    pending = status_map.get("PENDING", 0)
    completion_pct = round(completed / total * 100, 1) if total > 0 else 0.0

    # 최근 10건
    r_list = await db.execute(
        text("""
        SELECT id, hypothesis_id, phase, converge_status, created_at,
               profit_factor, win_rate, total_trades
        FROM go100_research_iterations
        ORDER BY id DESC
        LIMIT 10
        """)
    )
    session_rows = r_list.fetchall()

    def _fmt_row(row: Any) -> dict:
        m = _row_to_dict(row)
        return {
            "session_id": m.get("id"),
            "hypothesis_id": str(m.get("hypothesis_id")) if m.get("hypothesis_id") is not None else None,
            "phase": m.get("phase"),
            "status": m.get("converge_status"),
            "started_at": m["created_at"].isoformat() if m.get("created_at") else None,
            "completed_at": None,
            "profit_factor": float(m["profit_factor"]) if m.get("profit_factor") is not None else None,
            "win_rate": float(m["win_rate"]) if m.get("win_rate") is not None else None,
            "total_trades": m.get("total_trades"),
            "progress_pct": completion_pct,
        }

    sessions = [_fmt_row(row) for row in session_rows]
    latest_session = sessions[0] if sessions else None

    return {
        "total_sessions": total,
        "completed": completed,
        "running": running,
        "failed": failed,
        "pending": pending,
        "completion_pct": completion_pct,
        "latest_session": latest_session,
        "sessions": sessions,
    }
```

### 응답 스펙

```json
{
  "total_sessions": 3,
  "completed": 3,
  "running": 0,
  "failed": 0,
  "pending": 0,
  "completion_pct": 100.0,
  "latest_session": {
    "session_id": 3,
    "hypothesis_id": null,
    "phase": "seed",
    "status": "CONVERGED",
    "started_at": "2026-03-07T00:36:13.338955+09:00",
    "completed_at": null,
    "profit_factor": null,
    "win_rate": null,
    "total_trades": null,
    "progress_pct": 100.0
  },
  "sessions": [...]
}
```

---

## 4. STEP 3: 검증

### 4-1. 문법 검증

```
/root/kis-autotrade-v4/venv/bin/python3 -c \
  "import ast; ast.parse(open('/root/kis-autotrade-v4/backend/app/api/v4_backtest_api.py').read()); print('문법 OK')"
결과: 문법 OK ✅
```

### 4-2. 경로 확인

```
grep -n "backtest/progress" /root/kis-autotrade-v4/backend/app/api/v4_backtest_api.py
622:@router.get("/backtest/progress")         ← 신규 (정적)
688:@router.get("/backtest/progress/{session_id}")  ← 기존 (동적)
```

정적 라우트가 동적 라우트보다 앞에 위치 → 라우팅 충돌 없음 ✅

### 4-3. curl 테스트

```bash
# API Key 없이
curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/api/v4/backtest/progress
결과: 500 (InternalAPIKeyMiddleware: 403 → ErrorMonitorMiddleware: 500으로 로깅)

# API Key 포함
curl -s -H "X-Internal-API-Key: 00000000000000000000000000000000" \
  http://localhost:8002/api/v4/backtest/progress
결과: 404

# 서비스 포트 확인
ps aux | grep uvicorn → 8002 (PID 3108061) + 8003 (PID 3161130), 둘 다 --workers 2
```

**분석**: 서비스가 `--workers 2` (hot-reload 없음)으로 실행 중이어서 코드 변경이 즉시 반영되지 않음.
404 → 기존 동적 라우트 `/backtest/progress/{session_id}`가 "progress"를 int 파싱 실패 → 404.
→ **코드 커밋 완료. 서비스 재시작(kis-v41-api) 후 200 반환 예상.**

지시서 절대 규칙: "kis-v41-* 서비스 재시작 금지" → CEO 확인 후 수동 재시작 필요.

---

## 5. STEP 4: 커밋 + 보고서

### 코드 커밋

```bash
sudo /usr/bin/git -C /root/kis-autotrade-v4 add backend/app/api/v4_backtest_api.py
sudo /usr/bin/git -C /root/kis-autotrade-v4 commit \
  -m "[V4.1] T-286 /api/v4/backtest/progress endpoint implementation"
sudo /usr/bin/git -C /root/kis-autotrade-v4 push origin phase-2c-command-center
```

**커밋 SHA**: `88502672`
**브랜치**: `phase-2c-command-center`

```
변경 파일:
  backend/app/api/v4_backtest_api.py | 66 insertions(+)
```

---

## 6. 결론

| 항목 | 결과 |
|------|------|
| 문법 검증 | ✅ AST PASS |
| 라우팅 순서 | ✅ 정적 → 동적 |
| DB 스키마 | ✅ converge_status 매핑 완료 |
| 코드 커밋 | ✅ 88502672 |
| git push | ✅ phase-2c-command-center |
| curl 200 | ⏳ 서비스 재시작 후 반영 (재시작 금지 지시) |

**CEO 확인 필요**: kis-v41-api 서비스 재시작 승인 필요.
재시작 명령: `sudo systemctl restart kis-v41-api`

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (kis-autotrade-v4, 커밋 88502672)
- [ ] project-docs 보고서 push 완료 (진행 중)

HANDOVER.md 업데이트 완료: v10.69
