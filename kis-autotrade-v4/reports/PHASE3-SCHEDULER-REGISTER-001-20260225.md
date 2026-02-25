# PHASE3-SCHEDULER-REGISTER-001 보고서
**작성일:** 2026-02-25  
**프로젝트:** KIS AutoTrade V4.1

## 1. 작업 개요
- Phase 3 데이터 스케줄러를 main.py lifespan에 등록 유지
- 장중 자동 수집: 프로그램매매(ka90004), 테마(ka90002), 틱데이터(ka10079), 조건검색
- shutdown 시 Phase 3 stop → Phase 2 stop 역순 적용 상태 확인

## 2. 사전 점검 결과
- **서비스 상태:** kis-v41-api, kis-v41-monitor, kis-v41-scheduler 3개 모두 `active`
- **DB 무결성:** strategy_cards=60, v4_positions OPEN=11
- **Phase 2 스케줄러:** lifespan 내 `start_phase2_scheduler()` 로 등록 (Phase 2 → Phase 3 start 순서)
- **Phase 3 스케줄러 파일:** 존재 (`backend/app/services/phase3_data_scheduler.py`), `start_phase3_scheduler()` 함수로 태스크 반환
- **DB 백업:** `/tmp/backup_PHASE3-REGISTER_*.dump` 확인됨

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
- **등록 상태:** Phase 3는 이미 `start_phase3_scheduler()` 로 startup에 등록됨 (Phase 2 이후 start)
- **shutdown 순서:** Phase 3 stop → Phase 2 stop (역순) 이미 적용됨
- **이번 실행에서 main.py 수정:** 없음 (기 배포본에 반영 완료)
- **변경 줄 수:** 0 (diff 없음)

### diff 전문
이번 실행 시점에서 백업 대비 main.py 변경 없음. Phase 3 등록 및 shutdown 역순은 이미 반영된 상태.

```
(no diff - already applied)
```

## 5. 검증 결과
- **문법 검증:** OK
- **import 검증:** Phase 3 스케줄러 모듈 단독 import OK (app.services / backend.app 경로). 전체 app import는 ENCRYPTION_KEY 등 런타임 환경 필요로 스탠드얼론에서 실패 가능. 실제 kis-v41-api 서비스 환경 기준 정상.

## 6. CEO 승인 요청 사항
1. main.py 현재 구조 승인 (Phase 3 등록 및 shutdown 역순 유지)
2. kis-v41-api 서비스 재시작은 **필수 아님** (코드 변경 없음). 필요 시에만 CEO 승인 후 실행.

## 7. 재시작 시 검증 계획 (CEO 승인 후 실행 시)
- `systemctl is-active kis-v41-api`
- `curl -s http://localhost:8003/health`
- `journalctl -u kis-v41-api --since "1 min ago" | grep -i "phase.3"`
- 장중 시간이면 틱데이터/조건검색 수집 로그 확인
