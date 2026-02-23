# Phase 7 Dashboard UI 검수 수정

**작성일시:** 2026-02-13  
**작업 유형:** 버그 수정 / 리팩터링  
**상태:** 완료  
**관련 파일:** dashboard/db.py, dashboard/pages/overview.py, script_qa.py, video_qa.py, analytics.py

---

## 1. 작업 개요

Phase 7 Dashboard 검수 결과에 따라 NameError 수정, state_machine 전이 규칙 준수(FAILED + worker retry 패턴), Supabase 클라이언트 공통화, 미사용 함수 제거를 반영하였다.

---

## 2. 변경 사항

### 2-1. dashboard/db.py (신규)
- Supabase 클라이언트 공통 모듈. `SUPABASE_URL`, `SUPABASE_KEY`(SUPABASE_SERVICE_KEY fallback), `@st.cache_resource` 적용한 `get_supabase()` 정의.
- 각 페이지에서 `from db import get_supabase`로 사용.

### 2-2. dashboard/pages/overview.py
- `SUPABASE_URL`, `SUPABASE_KEY`, `get_supabase`, `from supabase import create_client` 제거. `from db import get_supabase` 추가. `import os` 유지(YOUTUBE_CHANNELS_JSON 사용).
- `fetch_job_counts()` docstring에 TODO 추가: "Replace with RPC or materialized view when jobs > 10000".
- 미사용 `_color_state()` 삭제. st.dataframe 위에 "TODO: Cell-level state coloring requires pandas Styler or st.data_editor" 주석 추가.

### 2-3. dashboard/pages/script_qa.py
- `SUPABASE_*`, `get_supabase`, `create_client` 제거. `from db import get_supabase` 추가. 불필요한 `import os` 제거.
- **Regenerate 버튼**: `update_job_state(job_id, "SCRIPTING")` → `update_job_state(job_id, "FAILED", "Regenerate requested via Script QA")`. 주석으로 "Dashboard bypasses state_machine validation; mark FAILED so worker retry picks up from SCRIPTING via get_retry_state()" 명시. 성공 메시지: "Job marked FAILED; worker will retry from script generation."

### 2-4. dashboard/pages/video_qa.py
- `SUPABASE_*`, `get_supabase`, `create_client` 제거. `from db import get_supabase` 추가. `import os` 유지(DATA_ROOT 사용).
- **Recompose 버튼**: `update_job_state(job_id, "COMPOSING")` → `update_job_state(job_id, "FAILED", "Recompose requested via Video QA")`. 동일 패턴 주석 및 성공 메시지: "Job marked FAILED; worker will retry from composition."

### 2-5. dashboard/pages/analytics.py
- **import os** 추가(NameError 방지). `SUPABASE_*`, `get_supabase`, `create_client` 제거. `from db import get_supabase` 추가.

---

## 3. 테스트 결과

- Streamlit 앱 실행 후 Overview / Script QA / Video QA / Analytics 페이지 동작 확인 권장.
- Regenerate·Recompose 클릭 시 job이 FAILED로만 변경되며, worker의 get_retry_state() 및 재시도 로직으로 SCRIPTING/COMPOSING 복구됨.

---

## 4. 주의사항 / 후속 작업

- **Job 수 증가 시**: fetch_job_counts()는 현재 전체 select 후 count. 1만 건 이상이 되면 RPC 또는 materialized view로 전환 검토.
- **상태 색상**: Recent Jobs 테이블 state 컬럼 셀별 색상은 pandas Styler 또는 st.data_editor로 추후 구현 가능.
