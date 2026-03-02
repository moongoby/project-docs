# CUR-V41-BRIDGE-PERIODIC-30MIN-001-20260302

## 작업 요약
genspark_bridge.py 정기 보고 주기 6시간 → 30분 변경

## 변경 내용

### 제거
- `PERIODIC_REPORT_HOURS_KST = {7, 13, 19, 1}` 상수 제거
- `last_periodic_report_hour` 딕셔너리 (프로젝트별) 제거
- 폴링 루프 내 6시간 주기 조건 블록 제거
- `build_status_report()` 함수 제거 (프로젝트별 개별 보고)

### 추가
- `PERIODIC_REPORT_INTERVAL_SEC = 1800` 상수 추가 (30분)
- `last_periodic_report_time: datetime | None` 단일 변수 추가
- `build_unified_status_report()` 함수 추가: 6개 프로젝트 전체 통합 형식
- 폴링 루프 종료 후 30분 경과 시 CEO 지휘소 + 텔레그램 발송 로직

### 보고 형식 (신규)
```
[통합현황] YYYY-MM-DD HH:MM KST
KIS: {서비스상태} | 최근커밋: {SHA} | 미완료작업 없음
GO100: {서비스상태} | 최근커밋: {SHA} | 미완료작업 없음
AADS: 최근커밋: {SHA} | 미완료작업 없음
SF: 최근커밋: {SHA} | 미완료작업 없음
NAS: 최근커밋: {SHA} | 미완료작업 없음
NTV2: 최근커밋: {SHA} | 미완료작업 없음
```

### 특이 사항
- `last_periodic_report_time is None` (최초 기동) 시 첫 폴링 사이클 완료 즉시 발송
- 실증: 재시작 후 55초 만에 첫 통합 현황 보고 발송 확인 (16:13:25 KST)
- 텔레그램 설정 미구성으로 텔레그램 발송 `실패(설정 없음)` — 별도 조치 필요

## 검증 결과
- systemctl status: `active (running)` ✅
- 첫 보고 시각: 2026-03-02 16:13:47 KST (서비스 기동 후 ~55초)
- CEO 지휘소 메시지 전송: `Genspark 메시지 전송 완료 (432자)` ✅
- 텔레그램: `실패(설정 없음)` — telegram_report 모듈 설정 필요

## 대상 파일
- `/root/.genspark/genspark_bridge.py`
