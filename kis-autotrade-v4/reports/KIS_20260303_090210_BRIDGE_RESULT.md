---
project: KIS-AutoTrade-V4.1
task_id: CUR-V41-EMERGENCY-MONITOR-001
completed_at: "2026-03-03 09:06 KST"
directive_file: KIS_20260303_090210_BRIDGE.md
executor: claudebot (claude-sonnet-4-6)
---

# CUR-V41-EMERGENCY-MONITOR-001 긴급 엔진 진단 + 매매 감시 결과

## 실행 시각
- 지시 발행: 2026-03-03 08:55 KST
- 진단 시작: 2026-03-03 09:01 KST
- 보고서 작성: 2026-03-03 09:06 KST

---

## PHASE 1: 긴급 진단 결과

### 파일 존재 여부

| 파일 | 존재 여부 | 비고 |
|------|-----------|------|
| logs/unified_engine.log | ❌ 없음 | 지시 내용 일치 |
| run_unified_engine.py (루트) | ❌ 없음 | 별도 실행 스크립트 미존재 |
| scripts/monitor_virtual_run.py | ❌ 없음 | 없음 |
| logs/shadow/ | ❌ 없음 | 권한 문제로 생성 불가 (go100user 소유) |
| backend/app/services/unified_engine/engine.py | ✅ 존재 | 백엔드 모듈로 존재 |

### 실행 중인 관련 프로세스

| 프로세스 | PID | 상태 |
|---------|-----|------|
| daily_scheduler.py (virtual 엔진 포함) | 3029739 | ✅ ALIVE (Feb24부터) |
| v4_position_monitor.py | 3029747 | ✅ ALIVE (Feb24부터) |
| position_monitor.py | 3029738 | ✅ ALIVE (Feb24부터) |
| FastAPI backend (port 8002) | 2149148 | ✅ ALIVE |
| data_miner.py | 2129821 | ✅ ALIVE |
| kis_ws_collector | 2173739 | ✅ ALIVE |
| collect_kiwoom_strength.py | 2173362 | ✅ ALIVE |

**진단 결론**: `run_unified_engine.py`는 독립 스크립트로 존재하지 않음.
UnifiedEngine은 `backend/app/services/unified_engine/engine.py` 모듈로 존재하며,
**daily_scheduler (PID 3029739)를 통해 virtual 모드로 이미 실행 중**.

---

## PHASE 2: 로그 디렉토리 생성 + 엔진 시작

### 실행 결과

```
mkdir -p /root/kis-autotrade-v4/logs/shadow
→ 실패: Permission denied (go100user 소유 디렉토리, claudebot 쓰기 불가)
```

```
python3 scripts/monitor_virtual_run.py premarket
→ 실행 불가: 파일 미존재
```

```
nohup python3 run_unified_engine.py --mode virtual
→ 실행 불가: 파일 미존재
```

### 대체 판단
- Virtual 엔진이 daily_scheduler를 통해 이미 운용 중
- 오전 08:50 KST에 premarket 신호 생성 완료 (7건 DB 확인)
- 별도 엔진 시작 불필요

---

## PHASE 3: 매매 실시간 감시 스냅샷

### 기준 시각: 2026-03-03 09:06 KST

```
[KIS-MONITOR] 09:06 KST
거래: 7건 (D2:1건, D4:1건, D5:1건, D6:1건, D7:1건, D-ORB:1건, S1:1건)
승인: 3건 | 차단: 4건 | 청산: 0건 (장 시작 직후, 미청산)
평균손익: N/A (미청산)
D4 Shadow: 0건 (shadow 디렉토리 미존재)
에러: 0건 (app_2026-03-03.log 기준)
scheduler_error.log: 547라인 (누적)
엔진: ALIVE (daily_scheduler PID 3029739)
```

### 전략별 상세 (08:50 KST premarket 신호)

| 전략 | 티커 | 방향 | 진입가 | 승인여부 | 차단사유 | CS점수 | EQS점수 |
|------|------|------|--------|----------|----------|--------|---------|
| D2 | 884760 | BUY | ₩67,721 | ✅ 승인 | - | 74 | 62 |
| D4 | 702721 | BUY | - | ❌ 차단 | L3.3_SUPPLY: 수급차단(synthetic_BLOCK) | - | - |
| D5 | 529671 | BUY | - | ❌ 차단 | GATE: 반등확인 게이트 미통과 D5(1조건) | 92 | 58 |
| D6 | 182487 | BUY | ₩80,322 | ✅ 승인 | - | 86 | 54 |
| D7 | 956527 | BUY | - | ❌ 차단 | L3.3_SUPPLY: 수급차단(synthetic_BLOCK) | - | - |
| D-ORB | 645820 | BUY | ₩147,818 | ✅ 승인 | - | 59 | 68 |
| S1 | 196979 | BUY | - | ❌ 차단 | L3.3_SUPPLY: 수급차단(synthetic_BLOCK) | - | - |

- source: VIRTUAL_KIS_MOCK
- 승인 3건 / 차단 4건 (승인율 43%)
- 미청산 7건 전부 (장 개시 직후)

---

## PHASE 4: 종합 평가

### 시스템 상태

| 항목 | 상태 |
|------|------|
| 엔진 생존 | ✅ ALIVE |
| 매매 신호 생성 | ✅ 정상 (7건) |
| API 서버 | ✅ 정상 |
| 포지션 모니터 | ✅ 정상 |
| unified_engine.log | ❌ 미존재 (독립 실행 안 됨) |
| D4 Shadow | ❌ 0건 (shadow 디렉토리 미존재) |
| 긴급 알림 필요 | ✅ shadow 디렉토리 생성 권한 필요 (root) |

### 조치 필요 사항

1. **logs/shadow 디렉토리**: root 권한으로 `mkdir -p /root/kis-autotrade-v4/logs/shadow && chown go100user:go100user ...` 필요
2. **run_unified_engine.py 독립 스크립트**: 필요 시 root가 생성해야 함 (현재 백엔드 모듈만 존재)
3. **monitor_virtual_run.py**: 미존재, 지시서의 스크립트 경로 오류로 판단

### 거래 0건 지속 여부
- 7건 거래 기록 (08:50 KST), 30분 이상 0건 아님 → **긴급 알림 불필요**

---

## 권한 제약 요약 (claudebot)

- `/root/kis-autotrade-v4/` 쓰기 불가 (go100user 소유)
- Phase 2의 일부 작업(shadow 디렉토리 생성, 독립 엔진 실행)은 root 실행 필요
- **실질적 virtual 매매는 daily_scheduler를 통해 정상 작동 중**

---

## 체크포인트

- [x] PHASE 1 진단 완료
- [x] PHASE 2 시도 (파일 미존재/권한 문제 기록)
- [x] PHASE 3 스냅샷 (09:06 KST) 완료
- [x] PHASE 4 보고서 작성 완료
- [ ] project-docs push (HANDOVER.md 업데이트): root 권한 필요 → done_watcher.sh 처리 예정
