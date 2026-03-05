---
project: AADS
task_id: T-089
completed_at: 2026-03-05 19:15:00 KST
---

# T-089 통합 수정 실행 결과
## classify_project 화이트리스트 + 채널 확장 + KST + 폴링 + 비용 테이블

**작업자**: Claude Code (claude-sonnet-4-6)
**서버**: 68 (aads.newtalk.kr)
**완료**: 2026-03-05 19:15 KST

---

## 백업 완료

```bash
cd /root/aads/aads-server && git tag pre-T089
cp app/api/project_dashboard.py app/api/project_dashboard.py.bak.T089
cp app/api/conversations.py app/api/conversations.py.bak.T089
cp app/api/context.py app/api/context.py.bak.T089

cd /root/aads/aads-dashboard && git tag pre-T089
cp src/app/conversations/page.tsx src/app/conversations/page.tsx.bak.T089
cp src/app/tasks/page.tsx src/app/tasks/page.tsx.bak.T089
```

---

## Part 1: classify_project 화이트리스트 (project_dashboard.py)

### 1-1. VALID_PROJECTS 상수 추가
```python
VALID_PROJECTS = {'AADS', 'KIS', 'GO100', 'ShortFlow', 'NewTalk', 'NAS', 'SALES'}
```

### 1-2. _validate_project_name() 함수 추가
```python
def _validate_project_name(raw: str) -> str:
    """T-089: 화이트리스트 기반 프로젝트명 정규화"""
    if not raw or not isinstance(raw, str):
        return 'AADS'
    cleaned = raw.strip()
    if len(cleaned) > 30:
        return 'AADS'
    upper = cleaned.upper()
    MAPPING = {
        'AADS': 'AADS', 'AADS-SERVER': 'AADS', 'AADS-DASHBOARD': 'AADS',
        'KIS': 'KIS', 'KIS-AUTOTRADE-V41': 'KIS', 'KIS-AUTOTRADE-V4.1': 'KIS',
        'GO100': 'GO100', 'SHORTFLOW': 'ShortFlow', 'SF': 'ShortFlow',
        'NEWTALK': 'NewTalk', 'NAS': 'NAS', 'SALES': 'SALES',
    }
    if upper in MAPPING:
        return MAPPING[upper]
    for key, val in MAPPING.items():
        if key in upper:
            return val
    return 'AADS'
```

### 1-3. _classify_project() 모든 return 화이트리스트 통과 강제
- 모든 `return "KIS"` → `return _validate_project_name("KIS")`
- 모든 `return "GO100"` → `return _validate_project_name("GO100")`
- 모든 `return "ShortFlow"` → `return _validate_project_name("ShortFlow")`
- 모든 `return "NewTalk"` → `return _validate_project_name("NewTalk")`
- 모든 `return "SALES"` → `return _validate_project_name("SALES")`
- 모든 `return "NAS"` → `return _validate_project_name("NAS")`
- 모든 `return "AADS"` → `return _validate_project_name("AADS")`

### 1-4. title 100자 초과 시 절단
```python
title = _t[:100] if _t else filename
```
(기존 50자 제한 → 100자로 변경, replace_all=True로 두 위치 동시 수정)

### 1-5. get_directives / get_reports / get_analytics 반환 전 일괄 정규화
```python
# T-089: 반환 전 일괄 정규화
for item in unique_directives:
    item['project'] = _validate_project_name(item.get('project', 'AADS'))
```
(get_reports, get_analytics by_project에도 동일 적용)

### 검증 결과
```
=== 2. Directives 프로젝트 검증 ===
한글문장키: 0건 → PASS
  AADS: 94
  KIS: 1
```

---

## Part 2: 대화 채널 확장 + KST (conversations.py)

### 2-1. REQUIRED_CHANNELS 정의
```python
REQUIRED_CHANNELS = [
    {"name": "AADS", "category": "conversation:aads"},
    {"name": "KIS", "category": "conversation:kis"},
    {"name": "SALES", "category": "conversation:sales"},
    {"name": "ShortFlow", "category": "conversation:sf"},
    {"name": "GO100", "category": "conversation:go100"},
    {"name": "NewTalk", "category": "conversation:newtalk"},
    {"name": "NAS", "category": "conversation:nas"},
    {"name": "통합지휘소", "category": "cross_msg"},
]
```

### 2-2. CHANNEL_MAP, CHANNEL_DISPLAY 확장
- go100, nas, newtalk 채널 추가

### 2-3. list_channels 엔드포인트 재작성
- DB에서 실제 데이터 있는 채널 조회
- 통합지휘소: system_memory WHERE category LIKE 'cross_msg_%' 집계
- REQUIRED_CHANNELS 순서대로 응답 구성
- 누락 채널: {count:0, last_message:null, status:"수집 미설정"}

### 2-4. KST 변환
- 기존 `_to_kst_str()` 함수 활용 (T-085에서 구현됨)
- last_message에 KST ISO 형식 적용

### 검증 결과
```
=== 3. Conversations 채널 ===
AADS: 28건, KST=True, status=ok
KIS: 89건, KST=True, status=ok
SALES: 141건, KST=True, status=ok
ShortFlow: 154건, KST=True, status=ok
GO100: 0건, KST=True, status=수집 미설정
NewTalk: 0건, KST=True, status=수집 미설정
NAS: 0건, KST=True, status=수집 미설정
통합지휘소: 0건, KST=True, status=ok
총 8개 채널 → PASS
```

---

## Part 3: 비용 추적 (project_dashboard.py + DB)

### 3-1. task_cost_log 테이블 확인 (기존 스키마)
```
Column     | Type
-----------+-----
id         | integer
task_id    | varchar(50)
session_id | varchar(100)
model      | varchar(100)
input_tokens | int
output_tokens | int
total_tokens | int
cost_usd   | numeric(12,8)
project    | varchar(100)
server     | varchar(100)
logged_at  | timestamptz
```
인덱스: idx_cost_task(task_id), idx_cost_project(project)

### 3-2. 초기 비용 시드 INSERT
```sql
INSERT INTO task_cost_log (task_id, project, model, cost_usd, logged_at) VALUES
('CEO-Test-Calculator', 'AADS', 'mixed-8-agents', 0.69, '2026-03-04 17:00:00+09'),
('T-031', 'AADS', 'claude-opus-4-6', 2.50, '2026-03-04 20:14:00+09'),
('T-073', 'AADS', 'gemini-2.0-flash', 0.15, '2026-03-05 16:30:00+09')
ON CONFLICT DO NOTHING;
```
결과: 4건 (기존 T-082 1건 + 신규 3건)

### 3-3. GET /dashboard/costs 엔드포인트 추가
```python
@router.get("/dashboard/costs")
async def get_costs():
    """비용 추적 현황 — task_cost_log 기반 (T-089)"""
```
- summary: total_entries, total_cost_usd, total_tokens
- by_project: 프로젝트별 집계
- entries: 최근 100건 (KST 변환, project 정규화)

### 3-4. analytics 비용 연동
- 기존 `task_cost_log` 쿼리 활용 (T-083에서 구현됨)
- cost_status = "active", total_cost_usd = $3.3465

### 검증 결과
```
=== 4. Analytics 비용 ===
cost_status: active
total_cost_usd: 3.3465
→ PASS

=== 5. Costs API ===
{
    "status": "ok",
    "summary": {
        "total_entries": 4,
        "total_cost_usd": 3.3465,
        "total_tokens": 2000
    },
    "by_project": [
        {"project": "AADS", "entries": 4, "cost_usd": 3.3465, "tokens": 2000}
    ],
    "entries": [
        {"task_id": "T-082", "model": "claude-sonnet-4-6", "cost_usd": 0.0065, "logged_at": "2026-03-05T18:53:51+09:00"},
        {"task_id": "T-073", "model": "gemini-2.0-flash", "cost_usd": 0.15, "logged_at": "2026-03-05T16:30:00+09:00"},
        {"task_id": "T-031", "model": "claude-opus-4-6", "cost_usd": 2.5, "logged_at": "2026-03-04T20:14:00+09:00"},
        {"task_id": "CEO-Test-Calculator", "model": "mixed-8-agents", "cost_usd": 0.69, "logged_at": "2026-03-04T17:00:00+09:00"}
    ]
}
```

---

## Part 4: 프론트엔드 자동 갱신 (aads-dashboard)

### 4-1. conversations/page.tsx

**30초 폴링 추가:**
```typescript
useEffect(() => {
  fetchChannels();
  const _id = setInterval(() => fetchChannels(), 30_000);
  return () => clearInterval(_id);
}, [fetchChannels]);
```

**KST 시각 표시:**
```typescript
const now = new Date();
const kst = new Date(now.getTime() + 9 * 60 * 60 * 1000);
setLastRefreshed(kst.toISOString().replace("T", " ").slice(11, 19) + " KST");
```

**count=0 채널 수집미설정 UI:**
```typescript
// Channel 인터페이스에 status?: string 추가
// 사이드바 채널 목록에 inactive 플래그 추가
// isInactive → 회색 배경 + "미설정" 배지 표시
```

### 4-2. tasks/page.tsx

**비용 KPI 개선:**
```typescript
{s.cost_status === "active" && s.total_cost_usd > 0
  ? `$${s.total_cost_usd.toFixed(2)}`
  : "데이터 수집중"}
```
- 실제 금액 있으면 `$3.35` 표시
- 없으면 "데이터 수집중" 표시
- active 상태에서 "task_cost_log 집계" 안내 메시지

### npm build 결과
```
▲ Next.js 16.1.6 (Turbopack)
✓ Compiled successfully in 20.4s
✓ Generating static pages (13/13)
0 TypeScript errors
```

---

## Part 5: Git 커밋 hook (3레포)

### commit-msg hook 설치
```bash
cat > /root/aads/aads-server/.git/hooks/commit-msg << 'HOOK'
#!/bin/bash
COMMIT_MSG=$(cat "$1")
if echo "$COMMIT_MSG" | grep -qxE '(and|Claude Code|update|fix|test|wip|.)'; then
  echo "ERROR: 무의미 커밋 메시지 거부. 형식: feat(T-XXX): 설명"
  exit 1
fi
exit 0
HOOK
chmod +x /root/aads/aads-server/.git/hooks/commit-msg
```
- aads-server: ✅
- aads-dashboard: ✅
- aads-docs: ✅

### .gitignore *.bak* 처리
- .gitignore 파일이 root 소유 (쓰기 권한 없음 - claudebot user)
- 대신 `git rm --cached $(git ls-files '*.bak*')` 실행:
  - aads-server: 17개 bak 파일 캐시에서 제거
  - aads-dashboard: 16개 bak 파일 캐시에서 제거

---

## 빌드 / 배포 / 검증

### npm build
```
✓ Compiled successfully in 20.4s
0 errors
13 pages generated
```

### Docker compose 배포
```bash
cd /root/aads/aads-server && DOCKER_BUILDKIT=0 docker compose -f docker-compose.prod.yml up -d --build
```
결과:
```
Container aads-server  Started (healthy)
Container aads-dashboard  Started
Container aads-postgres  Running (healthy)
Container aads-redis  Running (healthy)
```

### 전체 검증 결과

**=== 1. Health ===**
```
HTTP 200 → PASS
```

**=== 2. Directives 프로젝트 검증 ===**
```
한글문장키: 0건 → PASS
  AADS: 94
  KIS: 1
```

**=== 3. Conversations 채널 ===**
```
AADS: 28건, KST=True, status=ok
KIS: 89건, KST=True, status=ok
SALES: 141건, KST=True, status=ok
ShortFlow: 154건, KST=True, status=ok
GO100: 0건, KST=True, status=수집 미설정
NewTalk: 0건, KST=True, status=수집 미설정
NAS: 0건, KST=True, status=수집 미설정
통합지휘소: 0건, KST=True, status=ok
총 8개 채널 → PASS
```

**=== 4. Analytics 비용 ===**
```
cost_status: active
total_cost_usd: 3.3465
→ PASS
```

**=== 5. Costs API ===**
```json
{
    "status": "ok",
    "summary": {
        "total_entries": 4,
        "total_cost_usd": 3.3465,
        "total_tokens": 2000
    },
    "by_project": [
        {
            "project": "AADS",
            "entries": 4,
            "cost_usd": 3.3465,
            "tokens": 2000
        }
    ],
    "entries": [
        {
            "task_id": "T-082",
            "project": "AADS",
            "model": "claude-sonnet-4-6",
            "input_tokens": 1200,
            "output_tokens": 800,
            "total_tokens": 2000,
            "cost_usd": 0.0065,
            "logged_at": "2026-03-05T18:53:51+09:00"
        },
        {
            "task_id": "T-073",
            "project": "AADS",
            "model": "gemini-2.0-flash",
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.15,
            "logged_at": "2026-03-05T16:30:00+09:00"
        },
        {
            "task_id": "T-031",
            "project": "AADS",
            "model": "claude-opus-4-6",
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 2.5,
            "logged_at": "2026-03-04T20:14:00+09:00"
        },
        {
            "task_id": "CEO-Test-Calculator",
            "project": "AADS",
            "model": "mixed-8-agents",
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.69,
            "logged_at": "2026-03-04T17:00:00+09:00"
        }
    ]
}
```

---

## Git 커밋

### aads-server
```
커밋: 28f7bc3eeffb93554bfd0bf1347599d174ab2d9c
메시지: feat(T-089): 통합 수정 — classify 화이트리스트 + 채널 확장 + KST + 비용 + hook
브랜치: main
push: To https://github.com/moongoby-GO100/aads-server.git
       c287c07..28f7bc3  main -> main
```

### aads-dashboard
```
커밋: ee7627bc015da8d2ee8cc0ca5479ccf0348dbc9e
메시지: feat(T-089): 통합 수정 — 30초 폴링 + 비용 KPI + 채널 UI
브랜치: main
push: To https://github.com/moongoby-GO100/aads-dashboard.git
      9befeff..ee7627b  main -> main
```

### aads-docs
```
커밋: e8229c5
메시지: [AADS] docs: T-089 통합 수정 보고서 + HANDOVER v5.19
브랜치: main
push: To https://github.com/moongoby-GO100/aads-docs.git
      acd29b9..e8229c5  main -> main
```

---

## HANDOVER 업데이트

- HANDOVER.md v5.18 → v5.19 업데이트
- T-089 완료 항목 테이블에 추가
- 보고서: /root/aads/aads-docs/reports/T-089-RESULT.md 작성

---

## 보고 형식 (AADS 매니저 대화창)

[CURSOR-AADS] push 완료
작업: T-089 통합 수정 5파트 (classify+채널+KST+비용+hook)
보고서: https://github.com/moongoby-GO100/aads-docs/blob/main/reports/T-089-RESULT.md
커밋(server): https://github.com/moongoby-GO100/aads-server/commit/28f7bc3eeffb93554bfd0bf1347599d174ab2d9c
커밋(dashboard): https://github.com/moongoby-GO100/aads-dashboard/commit/ee7627bc015da8d2ee8cc0ca5479ccf0348dbc9e
HTTP: 200
HANDOVER: v5.19 업데이트 완료
다음: 지시 대기
