# AADS 인수인계서 — 최신 상태

**버전:** 5.16 (T-076 기준)
**최종 수정:** 2026-03-05 KST
**담당:** AADS 운영팀

---

## 1. 시스템 개요

AADS(AI Agent Dispatch System)는 여러 프로젝트(KIS, GO100, ShortFlow, NewTalk V2, NAS)의
AI 에이전트 작업을 중앙에서 관리하는 대시보드 및 API 서비스입니다.

**주요 접속:**
- 대시보드: https://aads.newtalk.kr
- API Base: https://aads.newtalk.kr/api/v1
- Git: github.com/moongoby-GO100/aads-server (server), moongoby-GO100/aads-dashboard (frontend), moongoby-GO100/aads-docs (docs)

**서버 구성:**
- 68서버 (68.183.183.11): AADS 웹 서비스 (Docker: aads-server, aads-dashboard, aads-postgres, aads-redis)
- 211서버 (KIS AutoTrade): KIS/GO100 에이전트
- 114서버 (114.207.244.86): ShortFlow, NewTalk V2, NAS + REMOTE_114 에이전트

---

## 2. 완료된 주요 태스크

| Task | 제목 | 상태 | 완료일 |
|------|------|------|--------|
| T-061 | aads_remote_agent.py 스크립트 작성 | DONE | 2026-03-05 |
| T-062 | REMOTE_114 원격 에이전트 배포 | **DONE** (heartbeat 실증) | 2026-03-05 |
| T-070 | 비용/시간 분석 API + task_history 완료시각 수정 | DONE | 2026-03-05 |
| T-072 | React Error #31 수정 + Tasks 페이지 4탭 구조 | DONE | 2026-03-05 |
| T-073 | CEO Chat v2 — 계층 메모리 + 컨텍스트 DB + 모델 분기 엔진 | DONE | 2026-03-05 |
| T-074 | Tasks 분석탭 g.reduce 에러 수정 + classify_project 정확도 개선 | DONE | 2026-03-05 |
| T-076 | Remote Agent 114서버 배포 확인 + NTV2 SEEDER-001 검증 | **DONE** | 2026-03-05 |

---

## 3. 원격 에이전트 현황

### REMOTE_114 (114서버)
- **파일:** /root/aads-remote/aads_remote_agent.py
- **서비스:** systemd aads-remote-agent-114 (또는 유사)
- **상태:** 🟢 ONLINE — heartbeat 정상 (5분 간격)
- **최신 heartbeat:** 2026-03-05T17:13:49+09:00
- **agent_id:** REMOTE_114
- **포트:** 9900 (내부 HTTP)
- **AADS에 기록된 작업 수:** 22건
- **프로젝트:** ShortFlow ✅, NTV2 (service=inactive, DB OK), NAS ✅

### REMOTE_211 (211서버/KIS)
- **상태:** 🟢 ONLINE — heartbeat 정상
- **최신 heartbeat:** 2026-03-05T17:13:20+09:00
- **기록 작업 수:** 28건

---

## 4. T-062 완료 증거

T-062가 "PARTIAL"로 기록되었으나 실제로는 완료된 상태:

1. **AADS Analytics API 확인:**
   ```json
   {"server": "REMOTE_114", "tasks": 22, "status": "online", "last_report": "2026-03-05T17:13:49+09:00"}
   ```

2. **Health Check 응답:**
   ```
   GET http://server-114:9900/health
   → {"status": "ok", "agent_id": "REMOTE_114", "timestamp": "2026-03-05T17:15:42"}
   ```

3. **Heartbeat 내용 (매 5분 전송):**
   ```json
   {"agent_id": "REMOTE_114", "system": {"uptime": "5 weeks 5 days", "agent_uptime_sec": 6320}}
   ```

4. **이전 SSH 배포 실패 후 재시도:** server-114 자체 세션에서 로컬 배포 완료된 것으로 추정

---

## 5. NTV2 SEEDER-001 상태

**상태:** DONE (데이터 존재 확인)

**DB 레코드 (2026-03-05 확인):**
- users: 17 (≥ 6 ✅)
- products: 46 (≥ 20 ✅)
- orders: 6
- purchase_orders: 36

**API 스모크 테스트 결과:**
- POST /api/auth/login (인증): 200 OK ✅
- GET /api/products (상품목록): 200 OK, 45개 ✅
- GET /api/orders (주문): 200 OK, 6건 ✅
- GET /api/purchase-orders (배송/발주): 200 OK, 13건 ✅
- GET /api/settlements (정산): 404 (경로 확인 필요 ⚠️)

---

## 6. 보류/미완료 사항

| 과제 | 상태 | 우선순위 | 비고 |
|------|------|---------|------|
| NTV2-VERIFY-001 | pending | P0 | 203라우트 + 97테이블 전수 검증 |
| NTV2-V1FIX-002 | pending | P0 | DO→newtalk.kr 이미지 URL 치환 |
| SF-FASHION-001 | pending | P0 | ShortFlow 패션채널 시크블랙 |
| SF-QUALITY-001 | pending | P1 | AADS Quality Gate 실연동 |
| FRONTEND-AUDIT-001 | pending | P1 | NTV2 프론트엔드 감사 |
| V1-HOTFIX-001 | 보류 | P0 | CEO 승인 대기 |

---

## 7. 기술 스택 / 환경

### 68서버 AADS 서비스
```
docker compose -f /root/aads/aads-server/docker-compose.prod.yml ps
aads-server    :8100 (FastAPI)
aads-dashboard :3100 (Next.js)
aads-postgres  :5432 (PostgreSQL)
aads-redis     :6379 (Redis)
```

### 인증 키
- `AADS_MONITOR_KEY`: 모니터링 읽기 전용 키 (cat /root/.env.aads)
- `AADS_REMOTE_KEY`: 원격 에이전트 쓰기 키 (/root/aads-remote/.env.aads-remote on 68서버)

### SSH 접근
- 211서버 → 114서버: port 7916 (claudebot 키 미등록 문제 있음, root 계정으로 접근 필요)
- 211서버 → 68서버: SSH 키 미등록

---

## 8. 버전 이력

| 버전 | Task | 주요 변경 |
|------|------|---------|
| 5.13 | T-072 | Tasks 4탭 구조, React Error #31 수정 |
| 5.14 | T-073 | CEO Chat v2 (계층 메모리 + 모델 분기) |
| 5.15 | T-074 | 분석탭 에러 수정 + classify_project 개선 |
| 5.16 | T-076 | REMOTE_114 배포 확인 + NTV2 SEEDER 검증 |

---

*최종 수정: 2026-03-05 KST | Claude Sonnet 4.6*
