# PHASE3-SCHEDULER-REGISTER-001 보고서
**작성일:** 2026-02-25  
**프로젝트:** KIS AutoTrade V4.1

## 1. 작업 개요
- Phase 3 데이터 스케줄러를 main.py lifespan에 등록 유지 및 shutdown 순서 정리
- 장중 자동 수집 항목: 프로그램매매(ka90004), 테마(ka90002), 틱데이터(ka10079), 조건검색

## 2. 사전 점검 결과
- **서비스 상태:** kis-v41-api, kis-v41-monitor, kis-v41-scheduler 3개 모두 `active`
- **DB 무결성:** strategy_cards=60, v4_positions OPEN=11
- **Phase 2 스케줄러:** lifespan 내 `start_phase2_scheduler()` 로 등록됨 (Phase 2 → Phase 3 start 순서)
- **Phase 3 스케줄러 파일:** 존재 (`backend/app/services/phase3_data_scheduler.py`), `start_phase3_scheduler()` 함수로 태스크 반환

## 3. Phase 3 스케줄러 구성
| 수집 항목 | API | 시간 | 주기 |
|----------|-----|------|------|
| 틱데이터 Top20 | ka10079 | 09:00~15:30 | 1분 |
| 조건검색 | 키움 | 09:00~15:30 | 5분 |
| 체결강도 증분 | 스크립트 | 16:24~16:35 | 1회/일 |
| 프로그램매매 | ka90004 | 16:25~16:40 | 1회 |
| 테마 상세 | ka90002 | 16:55~17:10 | 1회 |
| 틱데이터 정리 | - | 02:55~03:10 | 1회 (7일 보존) |

## 4. main.py 변경 사항
- **lifespan 패턴:** A (asynccontextmanager)
- **기존 등록:** Phase3DataScheduler는 이미 `start_phase3_scheduler()` 로 startup에 등록됨
- **이번 수정:** shutdown 시 **Phase 3 stop → Phase 2 stop** 역순 적용 (지시서 준수)
- **변경 줄 수:** diff 31줄

### diff 전문

```
--- /tmp/main_py_orig.py	2026-02-25 09:56:47.219075742 +0900
+++ backend/app/main.py	2026-02-25 09:56:43.312033522 +0900
@@ -265,13 +265,7 @@
             await acc_sync_task
         except asyncio.CancelledError:
             pass
-    phase2_task = getattr(app.state, "phase2_data_task", None)
-    if phase2_task:
-        phase2_task.cancel()
-        try:
-            await phase2_task
-        except asyncio.CancelledError:
-            pass
+    # Phase 3 stop 먼저, Phase 2 stop 나중 (역순, PHASE3-SCHEDULER-REGISTER-001)
     phase3_task = getattr(app.state, "phase3_data_task", None)
     if phase3_task:
         phase3_task.cancel()
@@ -279,6 +273,13 @@
             await phase3_task
         except asyncio.CancelledError:
             pass
+    phase2_task = getattr(app.state, "phase2_data_task", None)
+    if phase2_task:
+        phase2_task.cancel()
+        try:
+            await phase2_task
+        except asyncio.CancelledError:
+            pass
     if orch_task:
         orchestrator.stop()
         orch_task.cancel()
```

## 5. 검증 결과
- **문법 검증:** OK
- **import 검증:** 스탠드얼론 환경(ENCRYPTION_KEY 등 미설정)에서 전체 app import 실패. 실제 서비스(kis-v41-api) 환경에서는 정상 동작 기준.

## 6. CEO 승인 요청 사항
1. main.py 변경 승인 (shutdown 순서: Phase 3 → Phase 2)
2. kis-v41-api 서비스 재시작 승인 (변경 반영 필수)

## 7. 재시작 후 검증 계획
- `systemctl is-active kis-v41-api`
- `curl -s http://localhost:8003/health`
- `journalctl -u kis-v41-api --since "1 min ago" | grep -i "phase.3"`
- 장중 시간이면 틱데이터/조건검색 수집 로그 확인
