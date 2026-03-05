# SERVER-114 운영 작업 보고서

**작성일시**: 2026-03-05 14:56 KST
**작성자**: Claude Code (server-114 자동화)
**대상 서버**: rfree-0009.cafe24.com (server-114)
**보고 범위**: 2026-03-05 오전~오후 작업 전체

---

## 1. 문서 레포(project-docs) 누락 보고서 복구 push

### 배경
server-211 SSH 인바운드 차단으로 NTV2 BRIDGE_RESULT 파일들이 GitHub project-docs에 미push 상태였음.

### 처리 결과

| 파일 | 경로 | 상태 |
|------|------|------|
| `V1-HOTFIX-001-report.md` | `newtalk-v2-api/reports/` | ✅ push 완료 |
| `V1-PATH-CHECK-001-report.md` | `newtalk-v2-api/reports/` | ✅ push 완료 |
| `nas-image/HANDOVER.md` | v1.5 — P4-114-API 완료 업데이트 | ✅ push 완료 |

- V1-HOTFIX-002-report.md: server-211 전용 파일, 이 서버에 없음 (별도 조치 필요)

---

## 2. server-116 Claude Code 설정 동기화

### 배경
server-116(116.120.58.155, cafe24 CentOS 7)에 Claude Code가 설치되어 있으나 GLIBC 버전 불일치로 실행 불가 상태.

### 처리 결과

| 항목 | 내용 | 상태 |
|------|------|------|
| Node.js v16.20.2 설치 | nvm 경유, CentOS 7 glibc 2.17 호환 | ✅ |
| `~/.claude/settings.json` | Bash/Edit/Read/Write/mcp 전체 허용 동기화 | ✅ |
| `ANTHROPIC_API_KEY` | `~/.bashrc` 등록 | ✅ |
| Claude Code 실행 | v2.1.69 정상 확인 | ✅ |

---

## 3. server-211 → server-116 SSH 접속 설정

### 배경
server-211 SSH 인바운드 전면 차단 상태. server-211에서 server-116으로 아웃바운드 연결은 가능하므로 키 사전 등록 방식 채택.

### 처리 결과

| 항목 | 내용 |
|------|------|
| 키 생성 | `id_ed25519_211to116` (server-114 `/root/.ssh/` 보관) |
| server-116 등록 | `~/.ssh/authorized_keys` 공개키 추가 완료 |
| 접속 검증 | server-114 → server-116 키 접속 성공 확인 |
| server-211 전달 | AADS API `message_queue`로 private key + 설정 명령 발송 |

server-211에서 AADS 메시지 수신 후 private key 설치 시 즉시 사용 가능.

---

## 4. server-116 서비스 상태 확인

| 항목 | 상태 |
|------|------|
| 업타임 | 132일 (안정) |
| CPU / Memory | 2.3% / 40% (정상) |
| 디스크 | 53% 사용 (여유 충분) |
| Apache 2.4.39 | ✅ 운영 중 |
| AADS Remote Agent (9900) | ✅ 운영 중 |
| ShortFlow | server-114에 존재 (server-116 아님) |

⚠️ **주의**: PHP 5.4.16 — EOL, 보안 업그레이드 권장

---

## 5. ShortFlow 서비스 확인

**위치**: server-114 `/data/shortflow` (Docker Compose)

| 컨테이너 | 포트 | 상태 | 업타임 |
|---------|------|------|--------|
| shortflow-worker | 8000 | ✅ healthy | 7일 |
| shortflow-n8n | 5678 | ✅ Up | 11일 |
| shortflow-dashboard | 8501 | ✅ Up | 11일 |
| shortflow-saas-dashboard | 3001 | ✅ Up | 7일 |

⚠️ n8n: `POST execute` 웹훅 미등록 오류 — 워크플로우 트리거 확인 필요

---

## 6. AADS Remote Agent (server-114) 신규 설치

### 배경
server-114에 AADS 상태 보고 에이전트가 없었음.

### 설치 결과

| 항목 | 내용 |
|------|------|
| 설치 경로 | `/root/aads-remote/` |
| 런타임 | Python 3.11.14 (pyenv), aiohttp 3.13.3 |
| 포트 | 9900 |
| 엔드포인트 | `/health`, `/status`, `/tasks` |
| 인증 | Bearer 토큰 (`aads_remote_114_key_2026`) |
| systemd | `aads-remote-agent.service` — enabled, active |
| 보고 주기 | 5분 (300초) |
| 모니터 대상 | shortflow, newtalk_v2, nas |

```
curl http://localhost:9900/health
→ {"status":"ok","agent_id":"REMOTE_114","timestamp":"..."}
```

---

## 7. 미결 사항

| 항목 | 내용 | 우선순위 |
|------|------|---------|
| V1-HOTFIX-002 push | server-211 파일, SSH 복구 후 처리 필요 | 중 |
| server-211 SSH 인바운드 복구 | 포트 7916 차단 여부 확인 필요 | 높음 |
| server-116 PHP 업그레이드 | 5.4 → 7.x+ | 낮음 |
| ShortFlow n8n 웹훅 | POST execute 미등록 오류 점검 | 중 |

---

*보고서 자동 생성: Claude Code (server-114) — 2026-03-05 14:56 KST*
