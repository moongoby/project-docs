# CUR-V41-MANAGER-SNAPSHOT-AND-DESK2-DIAG-001-20260306

**Task ID**: T-172
**제목**: V4.1 Manager 스냅샷 시스템 구축 + DESK2 entry_rules 진단
**날짜**: 2026-03-06
**서버**: 211 (kis-autotrade-v4)
**우선순위**: P0-CRITICAL

---

[인계 확인]
직전 완료: T-125 (DESK2 멀티컨디션 Phase A)
현재 단계: Phase 2C
CEO 지시 적용: D-001, D-002
strategy_cards: 60행 (DESK1: 10, DESK2: 16, DESK3: 11, DESK4: 9, DESK5: 10, 기타: 4)
open_positions: 0건 (CLOSED: 35건)

---

## Part A — V4.1 Manager Snapshot System

### A-1. Nginx 설정 확인

**설정 파일**: `/etc/nginx/sites-enabled/kis-autotrade` (symlink to sites-available)

`trading41.newtalk.kr` HTTPS 서버블록(443):
- 현재 location 목록: `/api/v4/` → 8003, `/api/` → 8001, `/docs`, `/openapi.json`, `/ws/`, `/`
- `/manager/` location 블록 **미존재** → root 권한으로 추가 필요

**추가해야 할 Nginx location 블록** (trading41 443 서버블록 `location /` 직전에 삽입):
```nginx
location /manager/ {
    alias /root/kis-autotrade-v4/v41_manager/;
    autoindex off;
    add_header Cache-Control "no-cache, no-store, must-revalidate";
    add_header Access-Control-Allow-Origin "*";
}
```

**root에서 실행해야 하는 명령**:
```bash
# /etc/nginx/sites-available/kis-autotrade 에서
# "location / {" 직전에 위 블록 삽입 후:
nginx -t && systemctl reload nginx
```

> ⚠️ claudebot은 /etc/nginx/ 쓰기 권한 없음 (root 소유). root 계정에서 직접 수정 필요.

### A-2. 출력 디렉토리 생성

```
/root/kis-autotrade-v4/v41_manager/   ← 생성 완료 (claudebot 소유)
```

### A-3. 스냅샷 스크립트

**파일**: `scripts/v41/generate_v41_manager_snapshot.py`

스크립트가 이미 존재하였음. 컬럼명 불일치(v4_mock_trades: `strategy_name` → `strategy_id`) 등이 이미 자동 반영되어 있었으며, 실행 성공.

**수집 항목**:
| 항목 | 상태 |
|------|------|
| 서비스 상태 (kis-v41-*, redis, postgresql) | ✅ 수집 |
| API 헬스 (localhost:8003/health) | ✅ 수집 |
| v4_positions 상태별 카운트 | ✅ 수집 |
| v4_mock_trades 7일 전략별/날짜별 요약 | ✅ 수집 |
| strategy_cards desk_id별 카운트 | ✅ 수집 |
| v4_desk3_pool, v4_desk4_watchlist, v4_desk5_watchlist COUNT | ✅ 수집 |
| DB 통계 (tables count, DB size) | ✅ 수집 |
| v4_ohlcv_minute 최신 시각 | ✅ 수집 |
| funnel_score.yaml threshold, v3_ai_bonus | ✅ 수집 |
| GO100_COMMANDER_GATE_ENABLED | ✅ (미설정시 false) |

### A-4. 스크립트 실행 결과

```
$ venv/bin/python3 scripts/v41/generate_v41_manager_snapshot.py
[V41-SNAPSHOT] Generated at 2026-03-06 11:56:01 KST → /root/kis-autotrade-v4/v41_manager/
```

**생성된 파일**:
```
v41_manager/snapshot.json        (14,542 bytes)
v41_manager/mock_trades.json     (10,084 bytes)
v41_manager/desk_status.json     (851 bytes)
v41_manager/pipeline.json        (2,778 bytes)
v41_manager/_updated_at.txt      (23 bytes)
```

**snapshot.json 주요 내용**:
```json
{
  "generated_at": "2026-03-06 11:56:01 KST",
  "services": {
    "kis-v41-api": "active",
    "kis-v41-monitor": "active",
    "kis-v41-scheduler": "active",
    "kis-v41-minute-collector": "active",
    "redis-server": "active",
    "postgresql": "active",
    "api_health": {
      "status": "degraded",
      "orchestrator_state": "TRADING",
      "database": "connected",
      "redis": "disconnected"
    }
  },
  "desk_summary": {
    "DESK5": { "WATCHING": 20 },
    "DESK4": { "WATCHING": 18 },
    "DESK3": { "ACTIVE": 306 },
    "DESK2": { "condition_files": 9개 }
  },
  "positions": { "summary": { "CLOSED": 35 } }
}
```

### A-5. 크론 등록

**root 권한 필요** (`/etc/cron.d/` 쓰기 권한 없음). root에서 실행:
```bash
echo '*/30 * * * * root cd /root/kis-autotrade-v4 && venv/bin/python3 scripts/v41/generate_v41_manager_snapshot.py >> /var/log/go100/v41_manager_snapshot.log 2>&1' > /etc/cron.d/v41_manager_snapshot
```

### A-6. URL 검증

Nginx location 블록이 추가된 후:
```bash
curl -s -o /dev/null -w "%{http_code}" https://trading41.newtalk.kr/manager/snapshot.json
# 기대값: 200
```

**현재 상태**: Nginx 미수정으로 URL 접근 불가 (root 작업 대기)

---

## Part B — DESK2 entry_rules 진단

### B-1. CTE 파이프라인에서 DESK2 조건 호출 방식 확인

**`cte_pipeline.py`** 검색 결과:
```
grep -n "desk2|DESK2|multi_condition|condition_matcher|entry_rules"
backend/app/services/cte_pipeline.py
→ 출력 없음 (파일에 DESK2 관련 코드 없음)
```

**`run_unified_engine.py`** 검색 결과:
```
grep -n "desk2|DESK2|multi_condition"
→ 출력 없음
```

### B-2. entry_rules 실제 사용 경로

`backend/app/` 전체에서 `entry_rules` 사용:
| 파일 | 용도 |
|------|------|
| `backend/app/routers/backtest_router.py` | 백테스트 실행 시 entry_rules 로드 |
| `backend/app/services/trading/v4_pipeline_orchestrator.py` | 실시간 매매 시 entry_rules.min_strength 필터 |
| `backend/app/services/strategy_card_service.py` | 카드 조회 시 entry_rules 포함 |
| `backend/app/api/v4_backtest_api.py` | 백테스트 API |
| **GO100 전용**: `go100/orderbook_backtest_engine.py`, `go100/paper_trading_engine_30d.py` | GO100 전략카드 entry_rules |

### B-3. DESK2 matcher 파이프라인 호출 여부

```
grep -rn "desk2_multi_condition_matcher|Desk2MultiConditionMatcher|condition_registry"
backend/app/services/ (desk2_conditions 제외)
→ desk_filters/pipeline.py에서만 참조
```

**`desk_filters/pipeline.py` 참조 내용**:
- `DcsEvaluator` (dcs_evaluator.py) import
- `AxisMaskEngine` (axis_mask.py) import
- `CS1VolumePullbackCondition` (c_s1_volume_pullback.py) import

→ **MultiConditionMatcher 자체는 실시간 V4.1 파이프라인에서 직접 호출되지 않음**

### B-4. DESK2 strategy_cards entry_rules 현황

```sql
SELECT card_id, strategy_name, desk_id, entry_rules FROM strategy_cards WHERE desk_id='2' LIMIT 3;
```

결과:
- `DESK2_거래량스파이크`: `{'logic': '3 consecutive up candles, vol increasing, close>prev high, MACD>signal', 'indicators': [...]}`
- `DESK2_M00_시초첫3분봉고가돌파`: `{'logic': 'close > first_3_candles_high * 1.001', 'indicators': [...]}`
- `DESK2_데일리_class_a`: `{'indicators': ['sma5_above_sma20', 'volume_surge_2x', 'rsi_below_70', 'macd_gol...']}`

### B-5. 진단 결론

| 항목 | 상태 | 판단 |
|------|------|------|
| DESK2 conditions 모듈 (C1~C7, CS1) | ✅ 존재 (T-125 완료) | 모듈 파일 준비됨 |
| MultiConditionMatcher | ✅ 존재 | 초기화 가능 |
| 실시간 파이프라인 연결 | ❌ **미연결** | orchestrator에서 호출 없음 |
| entry_rules DB 값 | ✅ dict 형태로 저장됨 | C1~C7 타입과 불일치 |
| entry_rules 업데이트 효과 | ⚠️ 제한적 | 파이프라인 연결 없이 entry_rules만 업데이트해도 C1~C7 미실행 |

**핵심 발견**:
- DESK2 `strategy_cards.entry_rules`는 현재 `min_strength`, `indicators` 형식 JSON
- C1~C7 컨디션 모듈(`desk2_conditions/`)은 `desk_filters/pipeline.py` 경로로만 호출됨
- V4.1 실시간 매매 파이프라인(`v4_pipeline_orchestrator.py`)과 `desk2_conditions` 사이에 공식 연결 인터페이스 없음
- **entry_rules DB 업데이트보다 파이프라인 연결 작업(T-173+ 예정)이 선행되어야 함**

---

## Part C — 테스트 결과

### 테스트 실행

```bash
venv/bin/python3 -m pytest tests/ \
  --ignore=tests/test_api_endpoints.py \
  --ignore=tests/test_evolution_loop.py \
  --tb=short -q
```

**결과**: 746 passed, 8 failed, 22 warnings (4분 9초)

**기존 실패 (T-172와 무관)**:
| 테스트 | 실패 원인 |
|--------|----------|
| `test_funnel_integration.py::test_growth_score_engine_classify_stock` | 기존 임계값 이슈 |
| `test_growth_score.py::test_07_classify_none` | 기존 임계값 이슈 |
| `test_replay_bridge.py` (3건) | replay 브릿지 스펙 미일치 |
| `test_unified_engine.py::TestExitManager::test_time_close` | TypeError 기존 |
| `test_funnel_score_engine.py::test_score_l2_dual_flow_high` | LGBMRegressor feature names |
| `test_growth_score_fix.py::test_threshold_relaxation` | 임계값 관련 기존 |

→ T-172 작업으로 인한 신규 실패 없음 ✅

### 스크립트 직접 테스트

```bash
venv/bin/python3 scripts/v41/generate_v41_manager_snapshot.py
# → [V41-SNAPSHOT] Generated at 2026-03-06 11:56:01 KST → /root/kis-autotrade-v4/v41_manager/
cat v41_manager/snapshot.json | python3 -m json.tool | head -40  # 유효 JSON 확인
```

---

## 성공 기준 점검

| 기준 | 상태 |
|------|------|
| `scripts/v41/generate_v41_manager_snapshot.py` 실행 성공 | ✅ |
| `v41_manager/*.json` 5개 파일 생성 | ✅ |
| DESK2 entry_rules 사용 경로 파악 완료 | ✅ |
| Nginx `/manager/` location 블록 추가 | ⚠️ root 작업 대기 |
| 크론 `/etc/cron.d/v41_manager_snapshot` 등록 | ⚠️ root 작업 대기 |
| URL https://trading41.newtalk.kr/manager/snapshot.json → 200 | ⚠️ Nginx 수정 후 확인 필요 |
| HANDOVER.md v10.14 push | pending |

---

## Root 실행 필요 사항 (요약)

```bash
# 1) Nginx location 블록 추가 (trading41 443 서버블록에)
# /etc/nginx/sites-available/kis-autotrade 편집:
#   "location / {" 직전에 아래 삽입:
#
#   location /manager/ {
#       alias /root/kis-autotrade-v4/v41_manager/;
#       autoindex off;
#       add_header Cache-Control "no-cache, no-store, must-revalidate";
#       add_header Access-Control-Allow-Origin "*";
#   }

nginx -t && systemctl reload nginx

# 2) 크론 등록
echo '*/30 * * * * root cd /root/kis-autotrade-v4 && venv/bin/python3 scripts/v41/generate_v41_manager_snapshot.py >> /var/log/go100/v41_manager_snapshot.log 2>&1' > /etc/cron.d/v41_manager_snapshot

# 3) URL 확인
curl -s -o /dev/null -w "%{http_code}" https://trading41.newtalk.kr/manager/snapshot.json
```

---

## 다음 단계 (T-173 예정)

1. Nginx location 블록 root 추가 완료 후 URL 검증
2. DESK2 실시간 파이프라인 연결 (`v4_pipeline_orchestrator.py` ↔ `MultiConditionMatcher`)
3. DESK2 strategy_cards entry_rules를 C1~C7 형식으로 마이그레이션

HANDOVER.md 업데이트 완료: (커밋해시 pending)
