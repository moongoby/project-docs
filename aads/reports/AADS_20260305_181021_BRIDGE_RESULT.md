---
project: AADS
task_id: T-080
completed_at: 2026-03-05T18:24:19+09:00
---

# T-080 실행 결과: 분석 탭 KPI 정상화 (성공률, 비용, 평균작업시간)

## Task: T-080
## Status: completed

---

## 1. 백업 완료

```
cp /root/aads/aads-dashboard/src/app/tasks/page.tsx /root/aads/aads-dashboard/src/app/tasks/page.tsx.bak.T080
cp /root/aads/aads-server/app/api/project_dashboard.py /root/aads/aads-server/app/api/project_dashboard.py.bak.T080
```

---

## 2. Part A - 백엔드 수정: /root/aads/aads-server/app/api/project_dashboard.py

### 문제 진단
기존 `get_analytics()` 함수는 `go100_user_memory` cross_msg 데이터를 기반으로 태스크 상태를 집계하였으나, 이 데이터에서는 completed/error가 0으로 집계되어:
- total_tasks: 74 (cross_msg 건수, 실제 지시서 수와 무관)
- completed_tasks: 0 → success_rate: 0.0%
- cost: 0.0 (aads_conversations 테이블 데이터 없음)
- avg_task_duration_min: 0.0 (하드코딩)

### 수정 내용

**`from collections import defaultdict` 추가** (line 15)

**`get_analytics()` 함수 전면 재작성 (T-070 → T-080)**

Part 1: 지시서 파일 기반 통계
- DIRECTIVES_RUNNING_DIR + DIRECTIVES_DONE_DIR에서 모든 .md 파일 파싱
- total_tasks = len(all_directives)
- completed_tasks = status == "completed" 카운트
- error_tasks = status == "error" 카운트
- running_tasks = status == "running" 카운트
- success_rate = round(completed / (completed + error) * 100, 1) — completed+error 분모 사용
- avg_task_duration_min: 파일명 YYYYMMDD_HHMMSS → mtime 차이(분)로 계산, 유효범위 0~480분, 데이터 없으면 -1.0 반환
- by_project: _classify_project + _parse_directive_file 결과로 프로젝트별 completed/error/total 집계
- daily_trend: created_at[:10] 날짜 기반 최근 7일 분포
- error_distribution: _classify_error 결과 (auth_expired, permission_denied, task_failure 등) 카운트

Part 2: DB 쿼리 (비용/서버별)
- aads_conversations: project별 토큰/비용 집계 (데이터 없으면 total_cost_usd = -1.0 반환)
- go100_user_memory cross_msg: REMOTE_211, REMOTE_114 서버 상태 (online/offline)
- by_project 최종: directives 데이터 + conversations 데이터 병합

---

## 3. Part B - 프론트엔드 수정: /root/aads/aads-dashboard/src/app/tasks/page.tsx

### 수정 내용

**success_rate 계산 방식 변경** (AnalyticsTab)
```typescript
// 변경 전:
const successRate = s.total_tasks > 0 ? Math.round((s.completed_tasks / s.total_tasks) * 100) : 0;

// 변경 후 (T-080):
const successRate = (s.completed_tasks + s.error_tasks) > 0
  ? Math.round((s.completed_tasks / (s.completed_tasks + s.error_tasks)) * 100)
  : 0;
```

**총 비용 KPI 카드**: total_cost_usd < 0이면 "추적 미설정" 표시
```tsx
{s.total_cost_usd < 0 ? "추적 미설정" : `$${s.total_cost_usd.toFixed(2)}`}
```

**평균 작업시간 KPI 카드**: avg_task_duration_min < 0이면 "데이터 부족" 표시
```tsx
{s.avg_task_duration_min < 0 ? "데이터 부족" : `${s.avg_task_duration_min.toFixed(1)}분`}
```

---

## 4. 빌드/배포

### Next.js 빌드
```
cd /root/aads/aads-dashboard && npm run build

결과: ✓ Compiled successfully in 17.0s
빌드 에러: 0
```

### Docker 빌드 및 배포
```
DOCKER_BUILDKIT=0 docker build -t aads-server-aads-server:latest /root/aads/aads-server/ -f /root/aads/aads-server/Dockerfile
→ Successfully built 751ae712acdb
→ Successfully tagged aads-server-aads-server:latest

docker stop aads-server && docker rm aads-server
docker compose -f /root/aads/aads-server/docker-compose.prod.yml up -d aads-server
→ Container aads-server Started

DOCKER_BUILDKIT=0 docker build -t aads-server-aads-dashboard:latest /root/aads/aads-dashboard/ -f /root/aads/aads-dashboard/Dockerfile
→ Successfully built c8a7b88b1cc0
→ Successfully tagged aads-server-aads-dashboard:latest

docker stop aads-dashboard && docker rm aads-dashboard
docker compose -f /root/aads/aads-server/docker-compose.prod.yml up -d aads-dashboard
→ Container aads-dashboard Started
```

---

## 5. 검증 결과

### curl 검증 (지시서 명령)
```
curl -s https://aads.newtalk.kr/api/v1/dashboard/directives | python3 -c "import sys,json; d=json.load(sys.stdin); print('success_rate:', d.get('success_rate','없음'), 'total:', d['total'])"
→ 실행 결과: total: 82 completed: 51 error: 20 running: 0 (before new T-080 tasks added)
```

### Analytics API 전체 검증
```
curl -s https://aads.newtalk.kr/api/v1/dashboard/analytics

=== ANALYTICS SUMMARY ===
total_tasks: 96
completed_tasks: 64
error_tasks: 20
running_tasks: 1
success_rate: 76.2
total_cost_usd: -1.0  (→ 프론트엔드: "추적 미설정")
avg_task_duration_min: 15.4  (→ 프론트엔드: "15.4분")
active_servers: 2

=== BY_SERVER ===
{'server': 'REMOTE_211', 'tasks': 40, 'status': 'online', 'last_report': '2026-03-05T18:18:24+09:00'}
{'server': 'REMOTE_114', 'tasks': 36, 'status': 'online', 'last_report': '2026-03-05T18:18:57+09:00'}
{'server': 'AADS_WEB_CLAUDE_SALES_MARKETING_MGR', 'tasks': 1, 'status': 'offline', 'last_report': '2026-03-05T06:51:46+09:00'}
{'server': 'QA_OPS_MGR_SALES_MARKETING_MGR', 'tasks': 1, 'status': 'offline', 'last_report': '2026-03-05T06:56:09+09:00'}

=== DAILY_TREND ===
{'date': '2026-02-27', 'tasks': 0, 'cost_usd': 0.0}
{'date': '2026-02-28', 'tasks': 0, 'cost_usd': 0.0}
{'date': '2026-03-01', 'tasks': 0, 'cost_usd': 0.0}
{'date': '2026-03-02', 'tasks': 0, 'cost_usd': 0.0}
{'date': '2026-03-03', 'tasks': 19, 'cost_usd': 0.0}
{'date': '2026-03-04', 'tasks': 31, 'cost_usd': 0.0}
{'date': '2026-03-05', 'tasks': 44, 'cost_usd': 0.0}

=== ERROR_DISTRIBUTION ===
{'error_type': 'permission_denied', 'count': 12}
{'error_type': 'task_failure', 'count': 5}
{'error_type': 'auth_expired', 'count': 3}
```

---

## 6. KPI 목표 달성 여부

| KPI | 목표 | 실제 결과 | 달성 |
|-----|------|-----------|------|
| 성공률 | >60% | 76.2% | ✓ |
| 에러 분류 auth_expired | 데이터 확인 | 3 | ✓ |
| 에러 분류 permission_denied | 데이터 확인 | 12 | ✓ |
| 에러 분류 task_failure | 데이터 확인 | 5 | ✓ |
| 비용 표시 | "추적 미설정" | 추적 미설정 | ✓ |
| 평균작업시간 | N분 | 15.4분 | ✓ |
| 빌드 에러 | 0 | 0 | ✓ |
| REMOTE_211 | online | online | ✓ |
| REMOTE_114 | online | online | ✓ |

---

## 7. Git SHA

- aads-server: 649eeac (fix(T-080): analytics KPI calculation + success rate + error distribution)
- aads-dashboard: 84d1fda (fix(T-080): analytics tab KPI display + safe rendering)

---

## 8. URL

https://aads.newtalk.kr/tasks → 분석 탭
