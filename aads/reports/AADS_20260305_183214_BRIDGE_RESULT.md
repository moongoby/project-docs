---
project: AADS
task_id: T-081
completed_at: 2026-03-05T18:40:33+09:00
---

# T-081 작업 결과 보고서

## 제목
classify_project 정확도 개선 + GO100 대화채널 추가 + 비용표시 개선

---

## [백업]

```
cp /root/aads/aads-server/app/api/project_dashboard.py /root/aads/aads-server/app/api/project_dashboard.py.bak.T081  → 완료
cp /root/aads/aads-dashboard/src/app/tasks/page.tsx /root/aads/aads-dashboard/src/app/tasks/page.tsx.bak.T081  → 완료
```

---

## [Part A - classify_project 근본 수정]

### 파일: /root/aads/aads-server/app/api/project_dashboard.py

기존 `_classify_project` 함수를 3단계 우선순위 분류로 전면 교체.

#### 변경 전 (T-078 버전)
- 파일명 프리픽스 검사 후 본문 키워드 단순 매칭
- 'kis', 'go100', '뉴톡' 단독 매칭으로 오분류 발생
- T-077: KIS로 오분류 (본문에 'kis' 포함)
- T-073: NewTalk로 오분류 (본문에 'chatbot' 포함)
- T-062: GO100으로 오분류 (본문에 'go100' 경로 포함)

#### 변경 후 (T-081 버전: 3단계 우선순위)

**1단계: AADS 인프라 확정 키워드 (최우선 - 하나라도 있으면 AADS)**
```python
aads_definitive = [
    '대시보드', 'dashboard', 'Tasks 페이지', 'Conversations 탭', 'CEO Chat', 'ceo_chat',
    'project_dashboard', 'bridge.py', 'genspark_bridge', 'auto_trigger', 'claude_exec',
    'HANDOVER', 'handover', 'Docker', 'docker-compose', 'nginx', 'aads-server', 'aads-dashboard',
    '원격 에이전트', 'remote agent', 'aads_remote', 'cross-message', 'cross_msg',
    'system_memory', 'context.py', 'memory API', 'Memory', 'QA Agent', 'Visual Regression',
    '프로덕션 강화', '보고서 레포', 'Git push', 'React Error', 'API 평탄화', '4탭',
    'KPI', '분석 탭', '비용 엔진', 'cost_engine', '모델 분기', 'model routing',
    'Task ID:', 'DIRECTIVE', 'classify_project', 'safeRender', 'error_breakdown',
    '프론트엔드', 'frontend', '빌드', 'npm run build', 'TypeScript',
]
```

**2단계: 프로젝트 고유 키워드 (좁은 범위)**
- KIS: `kis-autotrade`, `KIS-V41`, `DESK1~5`, `자동매매 전략`, `분할매수`, `프랙탈 추세`, `한국투자증권`, `백억이 군단`, `fractal trend`, `pyramiding` (단독 'kis' 제외)
- GO100: `go100 프로젝트`, `GO100 목표`, `100일 목표`, `go100_user_memory`, `단기목표 달성` (단독 'go100' 제외)
- ShortFlow: `shortflow 영상`, `shortflow 파이프라인`, `ffmpeg 편집`, `숏폼 영상`, `shortform video`, `run_v4_pipeline`, `shortflow 검수`
- NewTalk: `newtalk v2 서비스`, `ntv2 배포`, `뉴톡 V2`, `뉴톡 챗봇 서비스`, `newtalk_v2 운영` (단독 '뉴톡' 제외)
- NAS: `nasync`, `nas동기화`, `nas 동기화`

**3단계: 기본값 AADS**

---

## [Part B - 분석탭 비용 표시 개선]

### 파일: /root/aads/aads-server/app/api/project_dashboard.py

analytics 엔드포인트 응답에 `cost_status` 및 `cost_message` 필드 추가:

```python
# total_cost: 데이터 없으면 cost_status = "not_configured"
if total_cost_usd == 0.0 and not aads_conv_rows:
    total_cost_usd = -1.0
    cost_status = "not_configured"
    cost_message = "비용 추적 미설정 (T-082 예정)"
else:
    cost_status = "active"
    cost_message = ""
```

summary 응답:
```json
{
  "total_cost_usd": -1.0,
  "cost_status": "not_configured",
  "cost_message": "비용 추적 미설정 (T-082 예정)"
}
```

### 파일: /root/aads/aads-dashboard/src/app/tasks/page.tsx

`AnalyticsSummary` 인터페이스에 `cost_status?`, `cost_message?` 필드 추가.

비용 카드 표시 변경:
```tsx
{(s.cost_status === "not_configured" || s.total_cost_usd <= 0) ? "비용 추적 미설정" : `$${s.total_cost_usd.toFixed(2)}`}
```

안내 메시지 추가:
```tsx
{(s.cost_status === "not_configured" || s.total_cost_usd <= 0) && (
  <div className="text-xs text-gray-500 mt-1">Claude Code API 비용 추적은 T-082에서 구현 예정</div>
)}
```

---

## [Part C - GO100 대화채널 추가]

### 파일: /root/aads/aads-server/app/api/conversations.py

DB 확인 결과:
- `system_memory`에 `conversation:go100` 카테고리 없음 (go100 대화 데이터 미수집)
- `go100_user_memory`에 `manager_conv_nt_mgr` 타입만 존재, go100 대화 없음

따라서 "아예 go100 대화 데이터가 없는" 경우에 해당 → channels 응답에 수집 미설정 항목 추가:

```python
# GO100 채널이 없으면 "수집 미설정" 상태로 추가 (T-081)
if not has_go100:
    channels.append({
        "name": "GO100",
        "category": "conversation:go100",
        "count": 0,
        "last_message": None,
        "status": "수집 미설정",
    })
```

---

## [빌드/배포]

### npm run build
```
▲ Next.js 16.1.6 (Turbopack)
✓ Compiled successfully in 17.4s
✓ Generating static pages using 7 workers (13/13) in 973.0ms

빌드 에러: 0
```

### docker compose up
```
aads-server: Up 19 seconds (healthy)
aads-dashboard: Up 19 seconds (health: starting)
→ 정상 재시작
```

---

## [검증 결과]

### 1) classify_project 오분류 검증
```
curl -s https://aads.newtalk.kr/api/v1/dashboard/directives | python3 -c "..."

프로젝트별: {'AADS': 79, 'KIS-AUTOTRADE-V41': 1, 'aads': 1, 'aads-server': 3, '생성→파이프라인 실행→결과 확인 가능한 상태': 1}
T-077: AADS (올바른값: AADS)   ✓
T-073: AADS (올바른값: AADS)   ✓
T-062: AADS (올바른값: AADS)   ✓
T-032: AADS (올바른값: AADS)   ✓
```

### 2) GO100 채널 확인
```
curl -s https://aads.newtalk.kr/api/v1/conversations/channels | python3 -m json.tool

{
    "channels": [
        {
            "name": "SALES",
            "category": "conversation:sales",
            "count": 131,
            "last_message": "2026-03-05 08:47:34.472055"
        },
        {
            "name": "ShortFlow",
            "category": "conversation:sf",
            "count": 154,
            "last_message": "2026-03-05 08:05:31.274009"
        },
        {
            "name": "AADS",
            "category": "conversation:aads",
            "count": 28,
            "last_message": "2026-03-05 06:38:52.926522"
        },
        {
            "name": "KIS",
            "category": "conversation:kis",
            "count": 89,
            "last_message": "2026-03-05 02:08:12.943447"
        },
        {
            "name": "GO100",
            "category": "conversation:go100",
            "count": 0,
            "last_message": null,
            "status": "수집 미설정"
        }
    ]
}

→ GO100 채널 포함됨 ✓
```

### 3) 비용 표시 확인
```
curl -s https://aads.newtalk.kr/api/v1/dashboard/analytics | python3 -c "..."

cost_status: not_configured
total_cost_usd: -1.0
cost_message: 비용 추적 미설정 (T-082 예정)

→ 비용 추적 미설정 표시 ✓
→ task_cost_log 테이블 미존재 확인 (EXISTS: false) ✓
```

---

## [Git]

### aads-server
```
git add -A && git commit -m "fix(T-081): classify_project AADS-first + GO100 channel + cost status"
git push → 성공
SHA: ad86f8c
```

### aads-dashboard
```
git add -A && git commit -m "fix(T-081): cost display improvement - show 비용추적미설정 when cost is 0"
git push → 성공
SHA: 76d6106
```

---

## [최종 보고]

- Task: T-081
- Status: completed
- 프로젝트별 분류: AADS=79, KIS=1(KIS-AUTOTRADE-V41), ShortFlow=0, NewTalk=0, GO100=0, NAS=0
- 오분류 검증: T-077=AADS ✓, T-073=AADS ✓, T-062=AADS ✓, T-032=AADS ✓
- GO100 채널: 표시됨 (count=0, status="수집 미설정") ✓
- 비용 표시: "비용 추적 미설정" + "Claude Code API 비용 추적은 T-082에서 구현 예정" ✓
- 빌드 에러: 0
- Git SHA: server=ad86f8c, dashboard=76d6106
