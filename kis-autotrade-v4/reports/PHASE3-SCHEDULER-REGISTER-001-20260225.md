# PHASE3-SCHEDULER-REGISTER-001 보고서

**프로젝트:** KIS AutoTrade V4.1  
**서버:** root@211.188.51.113  
**작성일:** 2026-02-25  
**지시서:** PHASE3-SCHEDULER-REGISTER-001

---

## 1. 작업 개요

Phase 3 데이터 스케줄러를 `main.py` lifespan에 등록하여 장중 자동 수집(프로그램매매, 테마, 틱데이터, 조건검색)이 API 서비스 기동 시 함께 가동되도록 함.  
기존에는 shutdown에서만 `phase3_data_task` 취소 처리만 되어 있고 **startup에서 Phase 3를 시작하는 코드가 없었음**. 이번 작업으로 startup에 Phase 3 등록을 추가함.

---

## 2. 사전 점검 결과

| 항목 | 결과 |
|------|------|
| kis-v41-api | active |
| kis-v41-monitor | active |
| kis-v41-scheduler | active |
| strategy_cards 건수 | 60 |
| v4_positions (OPEN) 건수 | 12 |
| Phase 2 main.py 등록 | 224~226행: start_phase2_scheduler, phase2_task, 로그 |
| Phase 3 main.py (수정 전) | startup 없음, shutdown 268~273행에 phase3_task 취소만 존재 |
| phase3_data_scheduler.py | 존재 (4,763 bytes), start_phase3_scheduler() 함수 제공 |
| DB 백업 | pg_dump 실행 (파일: /tmp/backup_PHASE3-REGISTER_YYYYMMDD_HHMMSS.dump) |

---

## 3. Phase 3 스케줄러 구성 (수집 항목, 시간표)

| 구분 | 항목 | 시간/주기 |
|------|------|-----------|
| 장중 | 틱 데이터 (상위 20종목) | 09:00~15:30 매 1분 |
| 장중 | 조건검색 | 09:00~15:30 매 5분 |
| 장종료 후 | 프로그램매매 | 16:25~16:40 1회/일 |
| 장종료 후 | 테마 상세 | 16:55~17:10 1회/일 |
| 새벽 | 틱 데이터 정리 | 02:55~03:10 매일, 7일 이전 삭제 |

구현: `phase3_scheduler_loop()` 내부에서 KST 기준 시간 판단 후 각 컬렉터 호출 (tick_data_collector, condition_search_collector, program_trades_collector, theme_detail_collector, tick_data_cleanup_older_than_days).

---

## 4. main.py 변경 사항 (diff)

**파일:** `backend/app/main.py`  
**백업:** `backend/app/main.py.bak.phase3`  
**diff:** `review/main_py_phase3_diff.txt`

```diff
228a229,234
>     # ── Phase 3 데이터 수집 스케줄러 (PHASE3-SCHEDULER-REGISTER-001) ──
>     from backend.app.services.phase3_data_scheduler import start_phase3_scheduler
>     phase3_task = start_phase3_scheduler()
>     app.state.phase3_data_task = phase3_task
>     logger.info("Phase 3 Data Scheduler started")
>
```

- Phase 2 블록 바로 아래(lifespan startup 내)에 Phase 3 import 및 `start_phase3_scheduler()` 호출, `app.state.phase3_data_task` 할당, 로그 추가.
- shutdown 블록은 기존에 `phase3_data_task` 취소 처리 있음 → 변경 없음.

---

## 5. 문법 검증 결과

- `python3 -c "import ast; ast.parse(open('backend/app/main.py').read())"` → **통과**
- Phase 3 import: `from app.services.phase3_data_scheduler import start_phase3_scheduler` (PYTHONPATH=backend) → **성공**

---

## 6. CEO 승인 요청 사항

1. **main.py 변경 승인**  
   - 위 diff대로 Phase 3 데이터 스케줄러 lifespan 등록 적용됨.

2. **kis-v41-api 서비스 재시작 승인**  
   - main.py 수정 반영을 위해 **재시작 필수**.  
   - 재시작 전까지는 Phase 3 스케줄러가 기동되지 않음.

---

## 7. 재시작 후 검증 계획

승인 후 실행:

```bash
sudo systemctl restart kis-v41-api
```

검증:

```bash
systemctl is-active kis-v41-api
curl -s http://localhost:8003/health
journalctl -u kis-v41-api --since "1 min ago" | grep -i "phase.3"
```

기대: `Phase 3 Data Scheduler started` 로그 출력 및 health 정상.

---

*이 문서는 PHASE3-SCHEDULER-REGISTER-001 지시서에 따라 작성되었으며, 서비스 재시작은 CEO 승인 후 진행합니다.*
