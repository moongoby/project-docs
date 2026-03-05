---
project: AADS
task_id: T-074
completed_at: 2026-03-05T16:46:27+09:00
---

# T-074 실행 결과 보고

Task: T-074
Status: completed

---

## [백업]

```
cp /root/aads/aads-dashboard/src/app/tasks/page.tsx /root/aads/aads-dashboard/src/app/tasks/page.tsx.bak.T074
cp /root/aads/aads-server/app/api/project_dashboard.py /root/aads/aads-server/app/api/project_dashboard.py.bak.T074
```

실행 결과: 백업 완료

---

## [Part A - 분석탭 g.reduce 에러 수정]

파일: `/root/aads/aads-dashboard/src/app/tasks/page.tsx`

### 변경 내용

AnalyticsTab 내 `data.by_project`, `data.by_server`, `data.daily_trend`, `data.error_distribution` 접근 시 Array.isArray() 안전 체크 추가:

```typescript
// 수정 전
const maxTasks = Math.max(...(data.daily_trend || []).map((d) => d.tasks), 1);
const errorDist = data.error_distribution || [];
const totalErrors = errorDist.reduce((sum, e) => sum + e.count, 0) || 1;
// ... data.by_project.length, data.by_project.map(), data.by_server.map(), data.daily_trend.slice() 직접 사용

// 수정 후
const dailyTrend = Array.isArray(data.daily_trend) ? data.daily_trend : [];
const byProject = Array.isArray(data.by_project) ? data.by_project : [];
const byServer = Array.isArray(data.by_server) ? data.by_server : [];
const maxTasks = Math.max(...dailyTrend.map((d) => d.tasks), 1);
const errorDist = Array.isArray(data.error_distribution) ? data.error_distribution : [];
const totalErrors = errorDist.reduce((sum, e) => sum + e.count, 0) || 1;
// ... byProject.length, byProject.map(), byServer.map(), dailyTrend.slice() 로컬 변수 사용
```

분석탭: g.reduce 에러 해결 - **완료** (Array.isArray 안전 체크로 배열이 아닌 값 fallback 처리)

---

## [Part B - classify_project 정확도 개선]

파일: `/root/aads/aads-server/app/api/project_dashboard.py`

### 변경 내용

```python
# 수정 전 (T-072)
def _classify_project(content: str) -> str:
    """보고서/지시서 내용에서 프로젝트 자동 분류 (T-072: 키워드 매핑 강화)"""
    mappings = [
        (['kis-autotrade', 'KIS', 'kis_autotrade', '주식', 'autotrade'], 'KIS'),
        (['shortflow', 'ShortFlow', '쇼츠', 'shorts', '템빨'], 'ShortFlow'),
        (['newtalk', 'NewTalk', '뉴톡'], 'NewTalk'),
        (['nas', 'NAS', 'nasync'], 'NAS'),
        (['go100', 'GO100', 'go_100'], 'GO100'),
    ]
    content_lower = content.lower()
    for keywords, project in mappings:
        if any(kw.lower() in content_lower for kw in keywords):
            return project
    return 'AADS'

# 수정 후 (T-074)
def _classify_project(content: str) -> str:
    """보고서/지시서 내용에서 프로젝트 자동 분류 (T-074: 정확도 개선 - AADS 1순위)"""
    content_lower = content.lower()
    # 1순위: AADS 자체 작업 (가장 먼저 체크)
    aads_keywords = ['aads', 'dashboard', 'ceo chat', 'ceo 채팅', '대시보드', 'handover',
                     'tasks 페이지', 'task-history', 'project_dashboard',
                     'cost', '비용', '분석', 'remote', '원격', 'bridge', '브릿지',
                     'memory', 'context api', '계층 메모리', '모델 분기', '실행 엔진']
    if any(kw in content_lower for kw in aads_keywords):
        return 'AADS'
    # 2순위: 프로젝트별 (정확 매칭)
    if any(kw in content_lower for kw in ['kis-autotrade', 'kis_autotrade', '주식', 'autotrade', '백억이']):
        return 'KIS'
    if any(kw in content_lower for kw in ['shortflow', '쇼츠', 'shorts', '템빨', 'youtube short']):
        return 'ShortFlow'
    if any(kw in content_lower for kw in ['newtalk', '뉴톡', 'newtalk_v2']):
        return 'NewTalk'
    if any(kw in content_lower for kw in ['nasync', 'nas동기화']):
        return 'NAS'
    if any(kw in content_lower for kw in ['go100', 'go_100']):
        return 'GO100'
    # 기본값
    return 'AADS'
```

분류정확도:
- "CEO 채팅 v2" → 'ceo 채팅' 키워드로 AADS 분류 ✓
- "HANDOVER" → 'handover' 키워드로 AADS 분류 ✓
- 'nas' 단독 키워드 제거 → 'nasync'/'nas동기화'만 사용 (dashboard의 'nas' 오매칭 방지) ✓
- 'kis' 단독 제거 → 'kis-autotrade'/'kis_autotrade' 정확 매칭 ✓

---

## [Part C - 시간 KST 변환]

### Backend (project_dashboard.py)

`_to_kst_str()` 헬퍼 함수 추가:

```python
def _to_kst_str(dt_or_str) -> str:
    """datetime 또는 문자열을 KST ISO 형식으로 변환 (T-074)"""
    if not dt_or_str:
        return ""
    if isinstance(dt_or_str, datetime):
        dt = dt_or_str if dt_or_str.tzinfo else dt_or_str.replace(tzinfo=timezone.utc)
        return dt.astimezone(KST).strftime("%Y-%m-%dT%H:%M:%S+09:00")
    s = str(dt_or_str)
    try:
        s_clean = s.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s_clean)
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(KST).strftime("%Y-%m-%dT%H:%M:%S+09:00")
    except Exception:
        return s
```

task-history에서 started_at/finished_at KST 변환:

```python
# 수정 전
started_at = content.get("started_at", str(r["created_at"]))
finished_at = content.get("finished_at", content.get("completed_at", ""))

# 수정 후
started_at = _to_kst_str(content.get("started_at") or r["created_at"])
finished_at = _to_kst_str(content.get("finished_at") or content.get("completed_at", ""))
```

### Frontend (page.tsx)

`toKST()` 헬퍼 함수 추가:

```typescript
function toKST(dtStr: string | null | undefined, len = 16): string {
  if (!dtStr) return "-";
  try {
    const d = new Date(dtStr);
    if (isNaN(d.getTime())) return dtStr.slice(0, len);
    const kst = d.toLocaleString("ko-KR", { timeZone: "Asia/Seoul", hour12: false });
    const m = kst.match(/(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{1,2}):(\d{2})/);
    if (m) {
      const [, y, mo, day, h, min] = m;
      const full = `${y}-${mo.padStart(2,"0")}-${day.padStart(2,"0")} ${h.padStart(2,"0")}:${min}`;
      return full.slice(0, len);
    }
    return dtStr.slice(0, len);
  } catch {
    return dtStr.slice(0, len);
  }
}
```

적용 위치:
- DirectivesTab: `started_at`/`completed_at` → `toKST()`
- RemoteTab: `started_at`/`finished_at` → `toKST(len=19)`
- RemoteTab 서버카드 `last_ping` → `toKST(len=19)`

시간: KST 표시 확인 - **완료**

---

## [Part D - 빌드배포검증]

### npm run build

```
> aads-dashboard@0.1.0 build
> next build

▲ Next.js 16.1.6 (Turbopack)
  Creating an optimized production build ...
✓ Compiled successfully in 16.4s
  Running TypeScript ...
  Collecting page data using 7 workers ...
  Generating static pages using 7 workers (13/13) in 834.5ms
  Finalizing page optimization ...

Route (app)
┌ ○ /
├ ○ /tasks
... (13 routes total)

ƒ Proxy (Middleware)
```

Build: 에러수 **0**

### docker restart

```
docker restart aads-server aads-dashboard
→ aads-server Up (healthy)
→ aads-dashboard Up (healthy)
```

### curl 검증

```
curl -s -o /dev/null -w '%{http_code}' -L https://aads.newtalk.kr/tasks → 200
```

HTTP 200 확인 ✓

---

## [Part E - Git Push]

### aads-server

커밋: `f9a7929`
메시지: `fix(T-074): classify_project accuracy + KST timezone`
변경: `app/api/project_dashboard.py` (51 insertions, 18 deletions)
Push: `→ github.com/moongoby-GO100/aads-server.git main -> main` ✓

### aads-dashboard

커밋: `55e59ae`
메시지: `fix(T-074): analytics tab g.reduce fix + KST display`
변경: `src/app/tasks/page.tsx` (36 insertions, 13 deletions)
Push: `→ github.com/moongoby-GO100/aads-dashboard.git main -> main` ✓

### aads-docs

커밋: `7e219a2`
메시지: `docs(T-074): HANDOVER v5.16 + classify_project + KST + g.reduce fix`
변경: `HANDOVER.md` (v5.15 → v5.16, T-074 테이블 행 추가)
Push: `→ github.com/moongoby-GO100/aads-docs.git main -> main` ✓

Git: SHA 3개 — **f9a7929(server) / 55e59ae(dashboard) / 7e219a2(docs)**

---

## 최종 요약

| 항목 | 결과 |
|------|------|
| 분석탭 g.reduce 에러 | ✅ 해결 (Array.isArray 체크 + 로컬 변수) |
| 분류정확도 | ✅ AADS 1순위 — CEO채팅/HANDOVER → AADS |
| 시간 KST 표시 | ✅ backend _to_kst_str + frontend toKST() |
| Build 에러수 | ✅ 0 |
| Git SHA | f9a7929 / 55e59ae / 7e219a2 |
| HTTP /tasks | ✅ 200 |
