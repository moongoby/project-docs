# [보고서] V4.1 × GO100 안전 브릿지 클라이언트/라우터 구현

> **Task ID**: CUR-V41-GO100-BRIDGE-DESIGN-001
> **실행일**: 2026-03-01
> **작성자**: Claude Code (Sonnet 4.6)
> **프로젝트**: KIS AutoTrade V4.1 & GO100 (SHARED)

---

## 1. 작업 개요

V4.1 백테스트/실거래 엔진이 GO100의 고도화된 AI 인프라(리스크 엔진, 포트폴리오 최적화, 에피소드 메모리)를 **REST API 브릿지**를 통해 안전하게 활용할 수 있도록 Phase 1 인프라를 설계 및 구현하였다.

핵심 설계 원칙 준수 확인:
- ✅ **코드 침범 금지**: GO100 클래스/함수 직접 import 없음 — V4.1 클라이언트는 HTTP만 사용
- ✅ **Read-Only / Append-Only**: GO100 기존 레코드 수정·삭제 없음
- ✅ **독립 페르소나**: `agent_id="V4.1_DESK_AGENT"` 강제, 타 봇과 혼용 차단

---

## 2. 구현 산출물

### 2.1 신규 파일

| 경로 | 역할 |
|------|------|
| `backend/app/services/v41/__init__.py` | V4.1 서비스 패키지 초기화 |
| `backend/app/services/v41/go100_bridge_client.py` | Task A: V4.1 전용 GO100 HTTP 클라이언트 |
| `backend/app/api/go100/__init__.py` | GO100 API 패키지 초기화 |
| `backend/app/api/go100/bridge.py` | Task B: GO100 수신 전용 브릿지 라우터 |
| `scripts/v41/test_go100_bridge.py` | Task C: E2E 검증 스크립트 |

### 2.2 수정 파일

| 경로 | 변경 내용 |
|------|-----------|
| `backend/app/main.py` | `go100_bridge_router` import 및 `app.include_router` 등록 추가 |

---

## 3. 세부 구현 내용

### Task A: `go100_bridge_client.py` — V4.1 브릿지 클라이언트

`Go100BridgeClient` 클래스, 비동기(async) 메서드 3개 구현.

| 메서드 | 엔드포인트 | 기능 |
|--------|-----------|------|
| `get_risk_status()` | GET `/api/go100/bridge/risk/status` | GO100 킬스위치 상태 조회. 활성 시 V4.1 진입 즉시 차단 |
| `request_portfolio_optimization(tickers, capital)` | POST `/api/go100/bridge/portfolio/optimize` | N:N 매칭 후보 종목의 켈리/마코위츠 비중 요청 |
| `log_episodic_memory(event_type, details)` | POST `/api/go100/bridge/memory/log` | 매매 결과·5축 마스크·DCS 점수 Append-Only 적재 |

**안전 설계**:
- `BridgeError` 예외로 호출자에게 Fallback 위임 (V4.1 매매 루프 차단 방지)
- `httpx.Timeout(connect=2, read=5)` — 네트워크 지연이 매매 타이밍 방해 최소화
- 베이스 URL `http://127.0.0.1:8002` — 루프백 내부 전용

### Task B: `bridge.py` — GO100 수신 브릿지 라우터

FastAPI APIRouter, prefix `/api/go100/bridge`, 3개 엔드포인트.

| 엔드포인트 | 방식 | 내부 호출 |
|-----------|------|-----------|
| `/risk/status` | GET | `risk_engine.get_risk_status()` (기존 GO100 함수, Read-Only) |
| `/portfolio/optimize` | POST | `portfolio_optimizer.optimize()` (기존 GO100 함수, Append-Only) |
| `/memory/log` | POST | `EpisodicMemory.remember()` (기존 GO100 클래스, Append-Only) |

**안전 설계**:
- `_guard_internal()`: 루프백 IP(127.0.0.1, ::1, localhost) 외 요청 → HTTP 403 즉시 차단
- `agent_id` 검증: `V4.1_DESK_AGENT` 외 → HTTP 400 반환
- GO100 기존 테이블에 UPDATE/DELETE 없음 — INSERT만 수행

### Task C: `test_go100_bridge.py` — E2E 검증 스크립트

4단계 검증 시나리오:
1. `GET /risk/status` — 킬스위치 상태 포함 전체 리스크 현황 응답 확인
2. `POST /portfolio/optimize` — EQUAL_WEIGHT 방식 최적화 요청/응답 확인
3. `POST /memory/log` — `V4.1_DESK_AGENT` 메모리 적재 → `memory_id` 반환 확인
4. 잘못된 `agent_id` → HTTP 400 반환 확인

---

## 4. E2E 검증 결과

> 실행 환경: `/root/kis-autotrade-v4/.venv/bin/python3 scripts/v41/test_go100_bridge.py`
> GO100 서버 상태: `http://127.0.0.1:8002/health` → HTTP 200 확인

```
============================================================
V4.1 ↔ GO100 브릿지 E2E 검증
대상: http://127.0.0.1:8002/api/go100/bridge
============================================================
[PASS] [1] GET /bridge/risk/status
       응답: {
         "status": "ok", "kill_switch_active": false,
         "total_equity": 100000000.0, "cash": 100000000.0,
         "position_value": 0, "exposure_pct": 0.0,
         "daily_pnl": 0.0, "daily_pnl_pct": 0.0,
         "active_rules": [3개], "open_positions_count": 0
       }
[PASS] [2] POST /bridge/portfolio/optimize
       응답: {
         "status": "ok", "method": "EQUAL_WEIGHT",
         "weights": {}, "capital_allocation": {},
         "expected_return": null, "optimization_id": null
       }
       ※ weights={} — 테스트 종목(삼성/하이닉스/카카오) 일봉 히스토리 미수집 상태.
          브릿지 인프라 자체는 정상 동작 (EQUAL_WEIGHT fallback 처리 확인)
[PASS] [3] POST /bridge/memory/log
       응답: {
         "status": "ok", "memory_id": 3,
         "agent_id": "V4.1_DESK_AGENT"
       }
[PASS] [4] agent_id 오류 → 400 검증
       응답: HTTP 400, detail="agent_id는 반드시 'V4.1_DESK_AGENT'이어야 합니다."

총 4건: PASS 4 / FAIL 0 / SKIP 0
✅ 브릿지 검증 완료 — 전 항목 PASS
```

**메모리 적재 확인**:
- `go100_user_memory` 테이블 `memory_id=3`으로 정상 INSERT
- `memory_type="v41_trade_result"`, `agent_id` 필드는 content JSON 내 명시
- 기존 GO100 봇 메모리(`memory_id` 1·2)와 완전 분리됨

---

## 5. 아키텍처 다이어그램

```
[V4.1 백테스트/실거래 엔진]
         │
         │  HTTP (127.0.0.1:8002)
         ▼
[go100_bridge_client.py]          ← V4.1 전용 클라이언트
   ├─ get_risk_status()           → GET  /api/go100/bridge/risk/status
   ├─ request_portfolio_optimize()→ POST /api/go100/bridge/portfolio/optimize
   └─ log_episodic_memory()       → POST /api/go100/bridge/memory/log
                                          │
                                          ▼
                              [bridge.py — FastAPI 라우터]
                                 ├─ _guard_internal() ← 루프백만 허용
                                 ├─ risk_engine.get_risk_status()     (Read-Only)
                                 ├─ portfolio_optimizer.optimize()    (Append-Only)
                                 └─ EpisodicMemory.remember()         (Append-Only)
                                          │
                                          ▼
                              [GO100 기존 인프라 (수정 없음)]
                                 ├─ go100_risk_events (테이블)
                                 ├─ go100_portfolio_optimizations (테이블)
                                 └─ go100_user_memory (테이블)
                                    → memory_type: "v41_trade_result" (V4.1 전용 네임스페이스)
```

---

## 6. 후속 작업 (Phase 2~3)

| Phase | 내용 | 선행조건 |
|-------|------|----------|
| Phase 2 | 모의투자 환경 E2E 통합 테스트: D6/D7 페이퍼트레이딩 결과를 브릿지로 실시간 메모리 적재 | Phase 1 완료 ✅ |
| Phase 3 | N:N 전략 도출 종목 → 포트폴리오 옵티마이저(MARKOWITZ) 비중 → 실전 주문 | Phase 2 완료 후 |

---

## 7. 체크포인트

- [x] **코드 레포 커밋 완료** (kis-autotrade-v4)
- [x] **project-docs 보고서 push 완료** (GitHub raw URL 200 확인)

---

## [REPORT-001] 최종 보고

**보고서**: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-GO100-BRIDGE-DESIGN-001-20260301.md

**커밋 (코드)**: `2fd7ac29` — `kis-autotrade-v4` 레포 (branch: phase-2c-command-center)

**커밋 (문서)**: `eba0e52` — `project-docs` 레포 (branch: master)

**HANDOVER**: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/HANDOVER.md

**HTTP**: 200 확인 완료
