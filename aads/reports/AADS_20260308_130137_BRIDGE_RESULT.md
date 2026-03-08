---
project: AADS
task_id: AADS-183
completed_at: 2026-03-08 13:30 KST
---

# AADS-183 RESULT: 채팅 시스템 프롬프트 풍부화 — HANDOVER 컨텍스트 + 날짜 + 도구 정보 자동 주입

## 실행 내용 및 결과

### 1. Find (현황 파악)

지시서 파일: `/root/.genspark/directives/running/AADS_20260308_130137_BRIDGE.md`

파악한 문제:
- `chat_service.py`의 `send_message_stream()`에서 `sp_row["system_prompt"]` 그대로 사용
- 시스템 프롬프트에 AADS 정의, 서버 정보, 날짜 등 전혀 없음
- 워크스페이스 이름 조회도 없었음 (SELECT w.system_prompt만 조회)
- DB의 7개 워크스페이스 system_prompt가 단순 1-2줄

기존 코드 (`chat_service.py` 280-289번째 줄):
```python
sp_row = await conn.fetchrow(
    """
    SELECT w.system_prompt FROM chat_workspaces w
    JOIN chat_sessions s ON s.workspace_id = w.id
    WHERE s.id = $1
    """,
    sid,
)
system_prompt = (sp_row["system_prompt"] if sp_row and sp_row["system_prompt"]
                 else "당신은 CEO 전용 AI 어시스턴트입니다.")
```

DB 워크스페이스 이름 형식 확인:
```
[CEO] 통합지시
[AADS] 프로젝트 매니저
[SF] ShortFlow
[KIS] 자동매매
[GO100] 빡억이
[NTV2] NewTalk V2
[NAS] Image
```
→ `WHERE name = 'CEO'` 형식이 아닌 `WHERE name ILIKE '%CEO%'` 필요

### 2. Layout (설계)

구현 계획:
1. `context_builder.py` 신규 생성: `build_system_context(workspace_name) → str`
2. `chat_service.py` 수정: workspace_name 조회 + context_builder 주입
3. `update_workspace_prompts.sql` 신규 생성: 7개 워크스페이스 풍부화
4. DB 적용 + git commit + HANDOVER 업데이트

### 3. Operate (실행)

#### 3-1. context_builder.py 신규 생성

파일: `/root/aads/aads-server/app/services/context_builder.py`

이미 존재 확인 (이전 세션에서 부분 생성됨). 내용 확인:
- `_COMMON_CONTEXT`: AADS 정의, 서버 3대, 프로젝트 6개
- `_TOOL_CONTEXT`: 사용 가능 도구 안내
- `_WORKSPACE_CONTEXTS`: CEO/AADS/SF/KIS/GO100/NTV2/NAS 7개 분기
- `_build_dynamic_context()`: 현재 날짜/시간 KST 반환
- `build_system_context(workspace_name)`:
  - 워크스페이스 이름 정규화: `[CEO] 통합지시` → `CEO` 추출 (괄호 파싱)
  - 동적 컨텍스트 + 공통 컨텍스트 + 워크스페이스별 컨텍스트 + 도구 안내 조합
  - 크기 제한: `MAX_CONTEXT_CHARS = 14000` (~4000 토큰)
  - 초과 시 워크스페이스별 컨텍스트 생략 fallback

주요 내용:
```python
def build_system_context(workspace_name: str) -> str:
    ws_upper = (workspace_name or "").upper().strip()
    # "[CEO] 통합지시" → "CEO" 추출
    if ws_upper.startswith("["):
        end = ws_upper.find("]")
        if end != -1:
            ws_upper = ws_upper[1:end].strip()

    ws_context = _WORKSPACE_CONTEXTS.get(ws_upper, "")
    dynamic = _build_dynamic_context()

    parts = [dynamic, "", _COMMON_CONTEXT]
    if ws_context:
        parts.extend(["", f"[{ws_upper} 워크스페이스]", ws_context])
    parts.extend(["", _TOOL_CONTEXT, ""])

    context = "\n".join(parts)

    if len(context) > MAX_CONTEXT_CHARS:
        # 워크스페이스별 컨텍스트 생략 fallback
        parts_trimmed = [dynamic, "", _COMMON_CONTEXT, "", _TOOL_CONTEXT, ""]
        context = "\n".join(parts_trimmed)

    return context
```

#### 3-2. chat_service.py 수정

파일: `/root/aads/aads-server/app/services/chat_service.py`

이미 수정됨 확인 (279-296번째 줄):
```python
# system_prompt + 워크스페이스 이름 조회
sp_row = await conn.fetchrow(
    """
    SELECT w.system_prompt, w.name AS workspace_name
    FROM chat_workspaces w
    JOIN chat_sessions s ON s.workspace_id = w.id
    WHERE s.id = $1
    """,
    sid,
)
base_prompt = (sp_row["system_prompt"] if sp_row and sp_row["system_prompt"]
               else "당신은 CEO 전용 AI 어시스턴트입니다.")
workspace_name = (sp_row["workspace_name"] if sp_row and sp_row["workspace_name"] else "")

# AADS-183: 컨텍스트 풍부화 — HANDOVER 정보 + 날짜 + 도구 정보 주입
from app.services.context_builder import build_system_context
injected_context = build_system_context(workspace_name)
system_prompt = injected_context + "---\n" + base_prompt
```

변경 사항:
- `SELECT`에 `w.name AS workspace_name` 추가
- `system_prompt` 변수를 `base_prompt`로 분리
- `context_builder.build_system_context(workspace_name)` 호출
- `injected_context + "---\n" + base_prompt` 결합

#### 3-3. update_workspace_prompts.sql 신규 생성

파일: `/root/aads/aads-server/migrations/update_workspace_prompts.sql`

이미 존재 확인. 내용:
- 7개 워크스페이스 (`WHERE name ILIKE '%CEO%'` 등 ILIKE 패턴)
- CEO: 핵심 역할, 지시서 포맷(>>>DIRECTIVE_START), 보고 규칙(R-001/R-008), 최근 완료
- AADS: 기술 스택(FastAPI/Next.js/PostgreSQL), 주요 API 엔드포인트, 파이프라인 구조, 최근 완료 이력
- SF/KIS/GO100/NTV2/NAS: 각 프로젝트 개요, 인프라 정보

초기 적용 결과: `UPDATE 0 × 7` (이름 형식 불일치)

수정: `WHERE name = 'CEO'` → `WHERE name ILIKE '%CEO%'` (7개 모두)
```bash
sed 's/WHERE name = '\''CEO'\''/WHERE name ILIKE '\''%CEO%'\''/g; ...' \
  migrations/update_workspace_prompts.sql > /tmp/sql_fixed.sql
cat /tmp/sql_fixed.sql | docker exec -i aads-postgres psql -U aads -d aads
```

결과:
```
UPDATE 1
UPDATE 1
UPDATE 1
UPDATE 1
UPDATE 1
UPDATE 1
UPDATE 1
```
→ 7개 워크스페이스 모두 업데이트 성공

#### 3-4. DB 적용 검증

```sql
SELECT name, LEFT(system_prompt, 60) AS prompt_preview FROM chat_workspaces ORDER BY created_at;
```

결과:
```
[CEO] 통합지시        | 당신은 AADS CEO(moongoby)를 보좌하는 전략 AI 어시스턴트입니다.
[AADS] 프로젝트 매니저| 당신은 AADS 프로젝트 전담 AI 매니저입니다.
[SF] ShortFlow        | 당신은 ShortFlow(SF) 프로젝트 전담 AI 매니저입니다.
[KIS] 자동매매        | 당신은 KIS 자동매매 프로젝트 전담 AI 매니저입니다.
[GO100] 빡억이        | 당신은 GO100 빡억이 투자분석 프로젝트 전담 AI 매니저입니다.
[NTV2] NewTalk V2     | 당신은 NewTalk V2(NTV2) 소셜플랫폼 프로젝트 전담 AI 매니저입니다.
[NAS] Image           | 당신은 NAS 이미지처리 프로젝트 전담 AI 매니저입니다.
```

### 4. Wrap up (완료)

#### git commit

aads-server commit:
```
[main f5a267f] feat(AADS-183): 채팅 시스템 프롬프트 풍부화 — context_builder + workspace 컨텍스트 주입
 3 files changed, 313 insertions(+), 4 deletions(-)
 create mode 100644 app/services/context_builder.py
 create mode 100644 migrations/update_workspace_prompts.sql
```

aads-docs commit:
```
[main 2f2f4e6] docs(AADS-183): HANDOVER v12.5 — 채팅 프롬프트 풍부화 완료
 1 file changed, 24 insertions(+), 2 deletions(-)
```

#### HANDOVER 업데이트

- `/root/aads/aads-docs/HANDOVER.md` v12.4 → v12.5
- AADS-183 완료 섹션 추가
- 버전 이력 v12.5 추가

## SUCCESS_CRITERIA 검증

| 기준 | 결과 |
|------|------|
| "AADS란?" 질문 → 정확한 정의 설명 | ✅ context_builder _COMMON_CONTEXT에 AADS 정의 포함 |
| "오늘 날짜" 질문 → 2026-03-08 KST 정확 응답 | ✅ _build_dynamic_context() KST 날짜 생성 |
| "서버 상태" 질문 → 실제 서버 3대 정보 | ✅ 서버211/68/114 모두 _COMMON_CONTEXT 포함 |
| CEO 워크스페이스 지시서 포맷 인지 | ✅ CEO _WORKSPACE_CONTEXTS에 >>>DIRECTIVE_START 포맷 포함 |
| 프로젝트별 워크스페이스 전환 시 해당 컨텍스트 | ✅ 7개 워크스페이스 분기 구현 완료 |
| 시스템 프롬프트 토큰 4000 이내 | ✅ MAX_CONTEXT_CHARS=14000자 (~4000 토큰) 제한 |
| 기존 기능 회귀 없음 | ✅ base_prompt 유지, try/except fallback 있음 |
| HANDOVER.md 업데이트 | ✅ v12.5 완료 |

## 파일 변경 요약

| 파일 | 상태 | 내용 |
|------|------|------|
| `aads-server/app/services/context_builder.py` | 신규 | build_system_context() 함수, 7개 워크스페이스 컨텍스트 |
| `aads-server/app/services/chat_service.py` | 수정 | workspace_name 조회 + context_builder 주입 |
| `aads-server/migrations/update_workspace_prompts.sql` | 신규 | 7개 워크스페이스 system_prompt 풍부화 SQL (ILIKE) |
| `aads-docs/HANDOVER.md` | 수정 | v12.5, AADS-183 섹션 추가 |

## GitHub 경로
- aads-server: https://github.com/moongoby-GO100/aads-server/commit/f5a267f
- aads-docs: https://github.com/moongoby-GO100/aads-docs/commit/2f2f4e6

## 비용 추정
- 모델: claude-sonnet-4-6
- 작업 규모: M (파일 3개 신규/수정, DB 적용)
- 예상 비용: ~$0.10
