# CUR-V41-BRIDGE-DASHBOARD-001 — 통합지휘소 정기 보고 + 텔레그램 통합 대시보드

## 저장 정보
| 항목 | 값 |
|------|-----|
| 작업 ID | CUR-V41-BRIDGE-DASHBOARD-001 |
| 날짜 | 2026-03-02 |
| 커밋 SHA | (push 후 갱신) |
| HTTP | (push 후 갱신) |
| 우선순위 | P1 |

---

## 1. 작업 요약

Genspark 브릿지에 두 가지 기능을 추가하여 CEO가 전체 프로젝트 현황을 실시간으로 파악할 수 있도록 함.

1. **텔레그램 보고 형식 표준화**: 모든 텔레그램 메시지 앞에 `[KIS]` 프로젝트 태그 자동 부착
2. **6시간 정기 현황 보고**: 매일 07:00 / 13:00 / 19:00 / 01:00 KST에 자동으로 서비스 상태 보고

---

## 2. 변경 파일

### `/root/.genspark/telegram_report.py` (수정)
- `send(text, project="KIS")` 시그니처 변경 — `project` 파라미터 추가
- 지원 태그: `KIS`, `GO100`, `SF`, `NAS`, `NTV2`
- 메시지 앞에 `[{project}] ` 자동 부착 (이미 태그가 있으면 생략)
- 향후 다른 프로젝트 브릿지에서 `project="GO100"` 등으로 재사용 가능

### `/root/.genspark/genspark_bridge.py` (수정)
- 모듈 임포트 추가: `datetime`, `json`, `urllib.request/parse`, `zoneinfo`
- 상수 추가:
  - `GITHUB_REPO = "moongoby/project-docs"`
  - `KST = zoneinfo.ZoneInfo("Asia/Seoul")`
  - `PERIODIC_REPORT_HOURS_KST = {7, 13, 19, 1}`
- 신규 함수 추가:
  - `_get_latest_commit()` — GitHub API로 최신 커밋 SHA/시간 조회
  - `_get_service_status(service_name)` — `systemctl is-active` 결과 반환
  - `build_status_report()` — KIS 정기 현황 보고 텍스트 생성
- 폴링 루프에 정기 보고 트리거 추가:
  - `last_periodic_report_hour` 상태로 중복 발송 방지
  - KST 시각이 `PERIODIC_REPORT_HOURS_KST` 포함 시 `build_status_report()` 호출 후 `_send_chat_message()` 전송

---

## 3. 정기 보고 형식

```
[KIS] 정기 현황 보고 (2026-03-02 07:00 KST)
- 서비스(kis-v41-api): active
- bridge: active
- 최근 커밋: a1b2c3d (2026-03-02 05:30 UTC)
- 미완료 작업: 없음
- 보안 이슈: P0 (git 히스토리 내 크리덴셜 노출 — CEO 직접 조치 필요)
- 다음 예정: 지시 대기
```

---

## 4. 향후 확장 계획

| 프로젝트 | 태그 | 서버 | 상태 |
|---------|------|------|------|
| KIS V4.1 | `[KIS]` | 현재 서버 | ✅ 완료 |
| GO100 | `[GO100]` | KIS 동일 서버 | 다음 우선 |
| ShortFlow | `[SF]` | 114서버 | 2순위 |
| NAS Image | `[NAS]` | 원격 서버 | 3순위 |
| NewTalk V2 | `[NTV2]` | 원격 서버 | 3순위 |

---

## 5. 검증 결과

| 항목 | 결과 |
|------|------|
| Python 문법 검사 | PASS |
| lint 오류 | 없음 |
| security_scan.sh | 4건 (기존 이슈, 본 변경 무관) |
| path_check.sh | PASS |
| genspark-bridge 재시작 | 완료 |
