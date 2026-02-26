# BT-DASHBOARD-IMPL-001 백테스트 대시보드 구현 보고서

**작성일:** 2026-02-25  
**지시서:** CURSOR BT-DASHBOARD-IMPL-001  
**프로젝트:** KIS AutoTrade V4.1  
**브랜치:** phase-2c-command-center  

---

## 1. 개요

CEO 기획 7대 질문에 대응하는 백테스트 대시보드의 DB·API·프론트엔드 골격을 구현하였다.

| 질문 | 대응 엔드포인트/기능 |
|------|----------------------|
| Q1 발굴 현황 | `/sessions/{id}/discoveries`, `/discovery-stats` |
| Q2 진입/청산 타이밍 | `/sessions/{id}/trades`, `/exit-analysis` |
| Q3 의도 검증 | `/sessions/{id}/intent-analysis` |
| Q4 의도 거래 수익률 | `/sessions/{id}/performance`, `/daily-pnl` |
| Q5 목표 달성 | `/sessions/{id}/goal-tracking` |
| Q6 수익률 추이 | `/trend`, `/trend/sessions` |
| Q7 실매매 가능성 | `/readiness` |

---

## 2. DB 테이블 생성 결과

**파일:** `scripts/migrations/create_bt_dashboard_tables.sql`

| 테이블 | 설명 |
|--------|------|
| `v4_bt_sessions` | 백테스트 세션 (전략, 기간, 자본, 성과지표, pass_criteria 등) |
| `v4_bt_discoveries` | 발굴 기록 (조건코드, 종목, 점수, 전략 전달 여부) |
| `v4_bt_trades` | 거래 기록 (진입/청산, PnL, 의도 검증 필드) |
| `v4_bt_versions` | 버전 이력 (변경 전/후 파라미터·성과, improvement) |

**실행 (운영 DB에서):**
```bash
pg_dump -Fc kisautotrade > /tmp/backup_BT-DASHBOARD-IMPL_$(date +%Y%m%d_%H%M%S).dump
psql -d kisautotrade -f /root/kis-autotrade-v4/scripts/migrations/create_bt_dashboard_tables.sql
```

**검증:**
```bash
psql -d kisautotrade -c "
SELECT table_name,
       (SELECT COUNT(*) FROM information_schema.columns c WHERE c.table_name = t.table_name AND c.table_schema='public') AS cols
FROM information_schema.tables t
WHERE table_schema='public' AND table_name LIKE 'v4_bt_%'
ORDER BY table_name;
"
```
기대: 4개 테이블.

---

## 3. BtDataWriter 구현 결과

**파일:** `backend/app/services/trading/desk2/tests/bt_data_writer.py`

- `create_session`, `update_session_result`: 세션 생성 및 결과 업데이트
- `write_discovery`: 발굴 기록 (100건마다 bulk commit)
- `write_trade`: 거래 1건 INSERT 후 commit
- `write_version`: 버전 이력 INSERT
- `flush_discoveries`: 남은 발굴 commit
- 규칙 준수: `datetime.now(timezone.utc)`, `logger.info("msg %s", var)`, `psycopg2.extras.Json` 사용

**다음 단계:** `desk2_backtester.py`에서 BtDataWriter 인스턴스 생성 후 세션/발굴/거래 기록 연동 (기존 nohup 프로세스에는 미적용).

---

## 4. API 엔드포인트 목록

**파일:** `backend/app/routers/bt_dashboard.py`  
**prefix:** `/api/v1/backtest`

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/sessions` | 세션 목록 (strategy, status, limit) |
| GET | `/sessions/{session_id}` | 세션 상세 |
| GET | `/sessions/{session_id}/discoveries` | 발굴 목록 |
| GET | `/sessions/{session_id}/discovery-stats` | 조건별/종목별 통계 |
| GET | `/sessions/{session_id}/trades` | 거래 목록 |
| GET | `/sessions/{session_id}/exit-analysis` | 청산 유형별 분석 |
| GET | `/sessions/{session_id}/intent-analysis` | 의도 검증 |
| GET | `/sessions/{session_id}/performance` | 수익률(전략/의도/시간대) |
| GET | `/sessions/{session_id}/goal-tracking` | 6개 기준 게이지·진단 |
| GET | `/sessions/{session_id}/daily-pnl` | 일별 PnL (에쿼티 커브) |
| GET | `/trend` | 버전별 수익률 추이 |
| GET | `/trend/sessions` | 세션별 수익률 추이 |
| GET | `/readiness` | 실매매 준비도 체크리스트·기대수익 |

**검증 (프로젝트 루트, venv 활성화):**
```bash
cd /root/kis-autotrade-v4
source .venv/bin/activate
PYTHONPATH=/root/kis-autotrade-v4/backend python3 -c "
from backend.app.routers.bt_dashboard import router
print('Routes:', len(router.routes))
"
```
기대: 13 routes.

---

## 5. 프론트엔드 페이지·컴포넌트

| 구분 | 경로/파일 |
|------|-----------|
| 세션 목록 | `app/(protected)/admin/backtest/page.tsx` |
| 세션 상세 | `app/(protected)/admin/backtest/[sessionId]/page.tsx` |
| API·훅 | `lib/api/backtest-dashboard.ts`, `lib/hooks/useBacktestDashboard.ts` |
| 컴포넌트 | `components/admin/backtest/DiscoveryPanel.tsx` |
| | `components/admin/backtest/TradeTimeline.tsx` |
| | `components/admin/backtest/IntentVerification.tsx` |
| | `components/admin/backtest/PerformancePanel.tsx` |
| | `components/admin/backtest/GoalTracking.tsx` |
| | `components/admin/backtest/TrendChart.tsx` |
| | `components/admin/backtest/ReadinessCheck.tsx` |

- 세션 목록: 전략/상태 필터, 세션 카드(거래수, 승률, 총수익률, Calmar, PF, PASS/FAIL 배지), 클릭 시 `/admin/backtest/{sessionId}` 이동.
- 세션 상세: 상단 요약 카드 + 7탭(발굴 현황, 거래 타이밍, 의도 검증, 수익률 분석, 목표 달성, 수익률 추이, 실매매 준비도).
- recharts 사용: BarChart, PieChart, LineChart (조건별 발굴, 청산 유형, 일별 누적 PnL, 세션 추이).

---

## 6. 네비게이션

- **Sidebar:** 관리자 메뉴 하단에 "백테스트 분석" 추가, 경로 `/admin/backtest`, 아이콘 BarChart2.
- **대상:** `components/layout/Sidebar.tsx` (showAdmin 시 노출).

---

## 7. 검증 결과

| 항목 | 결과 |
|------|------|
| DB 마이그레이션 SQL | 작성 완료 (4테이블·인덱스) |
| BtDataWriter import | OK (venv 기준) |
| bt_dashboard 라우터 | 13 routes (venv 기준) |
| main.py 라우터 등록 | `bt_dashboard_router` 추가 완료 |
| 프론트 빌드 | PerformancePanel Tooltip formatter 타입 수정 후 재빌드 권장 |

---

## 8. 절대 규칙 준수

- kis-v41-api, kis-v41-monitor, kis-v41-scheduler **재시작 안 함** (CEO 승인 필요).
- strategy_cards, v4_positions 테이블 **INSERT/UPDATE/DELETE 없음**.
- datetime.now() 미사용 → `datetime.now(timezone.utc)` 사용.
- from typing import Any 미사용.
- f-string 로깅 미사용 → `logger.info("msg %s", var)` 형식.
- 기존 nohup 백테스트 프로세스 동작에는 변경 없음.

---

## 9. 다음 단계

1. **DB:** 운영 DB에서 백업 후 `create_bt_dashboard_tables.sql` 실행 및 위 검증 쿼리로 4테이블 확인.
2. **백테스터 연동:** `desk2_backtester.py`에 BtDataWriter 주입 후 세션 생성·발굴·거래·버전 기록 호출 추가.
3. **서비스 재시작:** main.py에 bt_dashboard_router 추가 반영을 위해 **장 마감 후(15:30 이후)** kis-v41-api 재시작 시 CEO 승인 후 진행.
4. **프론트:** `npm run build` 재실행하여 타입/린트 통과 확인.

---

**문서 끝**
