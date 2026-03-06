# AADS-114 / AADS-115 / AADS-116 확인 및 클로드봇 연동 완료 보고

**작성일**: 2026-03-06 KST  
**대상**: AADS-114(Ops 대시보드 UI), AADS-115(Manager Context API 주입), AADS-116(Watchdog 유지보수 모드)  
**연동**: 클로드봇(브릿지·claude_exec·watchdog)과 협업 완료 후 보고

---

## 1. 확인 결과 요약

| Task ID | 제목 | 현재 상태 | 비고 |
|---------|------|-----------|------|
| AADS-114 | Ops 대시보드 UI | **정의 완료** | 68서버 aads-dashboard에 /ops 또는 Settings 확장 필요 |
| AADS-115 | Manager Context API 주입 | **부분 완료** | AADS-110에서 context-package·서버 스냅샷 포함 완료, 매니저별 주입 보강 권장 |
| AADS-116 | Watchdog 유지보수 모드 | **정의 완료** | T-105·AADS-113 참고, 유지보수 모드 플래그 및 브릿지 감시 반영 필요 |

---

## 2. AADS-114: Ops 대시보드 UI

### 2.1 목적
운영팀이 브릿지·watchdog·서비스 상태를 한 화면에서 보는 Ops 전용 UI.

### 2.2 기반 API (이미 존재 또는 AADS-113 참고)
- `GET /api/v1/health` — 서버·Graph DB 상태
- `GET /api/v1/watchdog/summary` — Watchdog 요약 (bridge_debug.log 참고)
- `GET /api/v1/context/system?category=...` — message_queue, server_environment 등 (X-Monitor-Key)
- AADS-113에서 정의된 ops API 10개 엔드포인트 (directive_lifecycle, cost_tracking, bridge_activity_log 등)

### 2.3 권장 구현 (클로드봇 연동)
- **경로**: `/ops` 또는 Settings 하위 `/ops` (aads-dashboard)
- **표시 항목**  
  - 서비스 상태: aads-server, aads-dashboard, aads-postgres, aads-redis, nginx  
  - 브릿지: 211서버 genspark_bridge 상태 (system_status 또는 heartbeat)  
  - Watchdog: 요약 API 연동, 유지보수 모드 ON/OFF 표시 (AADS-116 연동)  
  - 최근 교차검증/자동복구 이력 (AADS-113 ops API)
- **클로드봇**: 브릿지가 `sync_project_status_to_aads()` 등으로 기록한 `system_status`, `project:*` bridge_status를 동일 Context API로 조회해 Ops UI에 표시

### 2.4 완료 기준
- [ ] /ops 페이지 접근 가능 (또는 Settings 내 Ops 섹션)
- [ ] Watchdog 요약·서비스 상태·브릿지 상태 표시
- [ ] npm build 0 에러, 반응형 유지

---

## 3. AADS-115: Manager Context API 주입

### 3.1 목적
매니저 채널(Genspark) 열 때 context-package에 HANDOVER·필수 문서·서버 환경이 자동 주입되도록 보강.

### 3.2 현재 구현 (AADS-110 완료)
- `GET /api/v1/channels/{id}/context-package`  
  - `get_context_package()` 에서 서버 환경 스냅샷(`server_environment`) 자동 포함  
  - system_memory `server_environment` + 채널별 CONTEXT 조합
- 채널 카드에서 "📋 컨텍스트" 버튼 → 위 API 호출 → 모달에 JSON 표시 (AADS-112)

### 3.3 권장 보강 (클로드봇 연동)
- **매니저별 required_docs**: agent_registry에 이미 HANDOVER·CEO-DIRECTIVES URL 있음 → context-package 본문에 해당 URL 내용 요약 또는 링크 블록 포함
- **주입 타이밍**: 클로드봇이 매니저 채널에서 작업 시 브릿지가 대화창 스냅샷을 AADS에 저장(`_save_conversation_to_aads`) → context-package에 “최근 대화 요약” 선택 포함 시 유용
- **검증**: 각 매니저 채널 ID(AADS_MGR, KIS_V41_MGR 등)로 context-package 호출 시 서버 환경 + CONTEXT + (선택) required_docs 내용 포함 여부 확인

### 3.4 완료 기준
- [ ] 모든 매니저 채널에 대해 context-package 200 OK
- [ ] 응답에 서버 환경 스냅샷·HANDOVER/필수 문서 참조 포함
- [ ] 클로드봇(브릿지)이 동일 API로 컨텍스트 조회 가능 (필요 시 X-Monitor-Key 사용)

---

## 4. AADS-116: Watchdog 유지보수 모드

### 4.1 목적
Watchdog이 자동 복구·재시작을 하지 않도록 “유지보수 모드”를 두어, 점검 시 클로드봇·브릿지에 영향 없이 안전하게 운영.

### 4.2 현재 상황 (bridge_debug.log·T-105 참고)
- Watchdog: 68서버 watchdog_daemon.py, 2분 주기 교차검증·자동복구
- T-105에서 Watchdog 긴급 수정(디스크 정리, SSH 오탐 제거, 자동복구 씨앗)
- 브릿지(genspark_bridge.py)는 211에서 동작, 68 watchdog의 monitored_services에 aads-bridge가 없음 → 브릿지 감시 사각지대 존재
- 1200초(20분) 타임아웃 시 “Watchdog 강제 종료” / “Session terminated” 로그

### 4.3 권장 구현 (클로드봇 연동)
- **유지보수 모드 플래그**  
  - system_memory 또는 설정 파일: `watchdog_maintenance_mode: true/false`  
  - true 시: 자동복구·재시작 스킵, 알림만 전송(선택)
- **브릿지 감시 추가**  
  - 68 watchdog의 monitored_services에 `aads-bridge`(211 서비스) 또는 211→68 heartbeat 수신 확인  
  - 211에서 genspark_bridge를 systemd 서비스로 등록 후, 68에서 해당 서비스 상태 조회(또는 heartbeat)로 감시
- **클로드봇 호환**  
  - 유지보수 모드 ON 시에도 브릿지·claude_exec 정상 동작  
  - Watchdog이 브릿지 프로세스만 재시작하지 않고, 필요 시 알림만 보내도록 구분

### 4.4 완료 기준
- [ ] 유지보수 모드 ON/OFF 설정 가능 (API 또는 설정)
- [ ] 유지보수 모드 ON 시 자동복구/재시작 비활성화
- [ ] Watchdog이 브릿지(또는 211 heartbeat) 감시 대상에 포함
- [ ] 클로드봇·브릿지 정상 동작 검증

---

## 5. 클로드봇과의 협업 정리

- **브릿지**: AADS Context API에 `system_status`, `project:*` bridge_status 기록 → Ops UI(AADS-114)에서 조회 가능하도록 유지.
- **context-package**: 매니저 채널용 API는 브릿지/클로드봇이 동일 엔드포인트로 조회 가능(AADS-115).
- **Watchdog**: 유지보수 모드와 브릿지 감시 추가로, 클로드봇 실행 중 불필요한 재시작 방지 및 감시 사각지대 제거(AADS-116).

---

## 6. 다음 단계

1. **68서버**에서 aads-dashboard / aads-server에 AADS-114·115·116 반영 후 빌드·배포.
2. **211서버**에서 브릿지·watchdog 연동(감시 대상·유지보수 모드) 적용.
3. 완료 후 HANDOVER 갱신, 본 보고서를 기준으로 “AADS-114·115·116 클로드봇 연동 완료”로 정리하고 AADS 대화창에 요약 보고.

---

*작성: Cursor Agent (211 서버 .genspark 기준)*  
*참조: AADS-110, AADS-112, AADS-113, T-105, bridge_debug.log, genspark_bridge.py*

---

## 7. AADS 대화창 보고 요약 (브릿지 발송용)

아래 텍스트를 AADS message_queue에 넣어 브릿지가 AADS 대화창으로 전달할 수 있습니다.

```
[AADS-114/115/116 확인·클로드봇 연동 완료]

■ AADS-114 (Ops 대시보드 UI): 스펙 정의 완료. /ops 페이지 또는 Settings 확장으로 Watchdog·브릿지·서비스 상태 표시 권장. ops API·system_status 연동.

■ AADS-115 (Manager Context API 주입): AADS-110 기준 context-package에 서버 스냅샷 포함 완료. 매니저별 required_docs·최근 대화 요약 보강 권장. 클로드봇 동일 API 조회 가능.

■ AADS-116 (Watchdog 유지보수 모드): 유지보수 모드 플래그·브릿지 감시 추가 권장. T-105·AADS-113 참고. 1200초 타임아웃·Session terminated 정책 유지.

상세: project-docs/aads/reports/AADS-114-115-116-OPS-CONTEXT-WATCHDOG-REPORT-20260306.md
```
