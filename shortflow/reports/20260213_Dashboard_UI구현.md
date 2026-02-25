# Phase 7: Streamlit Dashboard UI 구현

**작성일시:** 2026-02-13  
**작업 유형:** 신규 개발  
**상태:** 완료  
**관련 파일:** dashboard/app.py, dashboard/pages/overview.py, script_qa.py, video_qa.py, analytics.py, requirements.txt, Dockerfile, docker-compose.yml

---

## 1. 작업 개요

ShortFlow 파이프라인 운영을 위한 Streamlit 대시보드를 구현하였다. Overview(Job 현황·Quota·최근 Job), Script QA(스크립트 승인/거절/재생성), Video QA(영상 미리보기·승인/업로드 대기·거절/재합성), Analytics(기간별 생산·실패 분석·처리 시간) 4개 페이지를 제공한다.

---

## 2. 변경 사항

### 2-1. dashboard/app.py (전체 교체)
- `st.set_page_config`: page_title, page_icon 🎬, layout wide, initial_sidebar_state expanded.
- 사이드바: "🎬 ShortFlow" 타이틀, `st.sidebar.radio`로 "📊 Overview", "📝 Script QA", "🎥 Video QA", "📈 Analytics" 선택.
- 선택된 페이지에 따라 `pages.overview`, `pages.script_qa`, `pages.video_qa`, `pages.analytics`의 `render()` 호출.

### 2-2. dashboard/pages/overview.py (신규)
- **Supabase**: `@st.cache_resource`로 `get_supabase()` (SUPABASE_URL, SUPABASE_SERVICE_KEY 또는 SUPABASE_KEY).
- **헬퍼**: `fetch_job_counts()` → state별 count, `fetch_recent_jobs(limit)` → 최근 20건, `get_today_stats()` → 오늘 total/completed/qa_pending/failed_dead.
- **상단 메트릭**: Total Jobs Today, Completed, QA Pending, Failed/Dead (4 columns).
- **2단 레이아웃**: 왼쪽 Pipeline Status (state별 st.bar_chart), 오른쪽 YouTube Quota (YOUTUBE_CHANNELS_JSON 파싱·채널명 나열, TODO: 런타임 quota는 worker 메모리 관리).
- **Recent Jobs**: st.dataframe, id/pick_id/state/retry_count/error_message(50자)/created_at/updated_at.
- **Refresh**: st.button("🔄 Refresh") → st.rerun().
- DB 실패 시 st.error 표시.

### 2-3. dashboard/pages/script_qa.py (전체 교체)
- QA_PENDING/COMPOSED 상태이면서 artifacts.script_id가 있는 job의 pick_id 목록 조회.
- st.selectbox로 pick_id 선택 → 해당 pick_id의 최신 script 로드.
- 오른쪽: Title, Hook, CTA, Tags(콤마 구분), Description, Scenes(expander별 narration/visual_prompt/duration_hint) 수정 가능.
- **✅ Approve**: scripts.status='approved', 수정 내용 저장. Job은 QA_PENDING 유지(영상 QA 후 최종 승인).
- **❌ Reject**: scripts.status='rejected', qa_note 저장, job state=FAILED, 거절 사유 입력.
- **🔄 Regenerate**: job state=SCRIPTING으로 업데이트.

### 2-4. dashboard/pages/video_qa.py (전체 교체)
- QA_PENDING 이면서 artifacts.video_path가 있는 job 목록 조회.
- 각 job에 대해: st.video(video_path), st.image(thumbnail_path), scene count·스크립트 요약.
- 경로: DATA_PATH(기본 /data/shortflow) 기준으로 절대/상대 경로 해석. docker-compose에서 /data/shortflow 볼륨 마운트 필요(TODO 주석).
- **✅ Approve & Queue Upload**: job state=QA_APPROVED.
- **❌ Reject**: 거절 사유 입력, job state=FAILED.
- **🔄 Recompose**: job state=COMPOSING.

### 2-5. dashboard/pages/analytics.py (전체 교체)
- 기간 선택: st.date_input start_date, end_date (기본 최근 7일).
- **Daily Production**: 기간 내 updated_at 기준 COMPLETED 건수 일별 st.line_chart.
- **Pipeline Stage Distribution**: 전체 job state별 count st.bar_chart.
- **Failure Analysis**: FAILED/DEAD_LETTER의 error_message 키워드(첫 단어·예외 클래스) 상위 10개 st.bar_chart.
- **Upload Quota Usage**: 기간 내 UPLOADED/COMPLETED 일별 건수 st.bar_chart.
- **Job Duration Analysis**: 최근 100건 created_at~updated_at 평균 처리 시간 st.metric (분 단위).
- pandas + st.line_chart/st.bar_chart만 사용(plotly 미사용).

### 2-6. requirements.txt
- streamlit>=1.30.0, supabase>=2.0.0, pandas>=2.0.0, python-dateutil>=2.8.0, python-dotenv>=1.0.1. (plotly 제거)

### 2-7. Dockerfile
- CMD에 `--server.headless=true` 추가.

### 2-8. docker-compose.yml
- dashboard 서비스 volumes에 `:ro` 추가 (./data:/data/shortflow:ro).

---

## 3. 테스트 결과

- 로컬/Docker에서 `streamlit run app.py` 또는 컨테이너 기동 후 http://localhost:8501 접속으로 4개 페이지 동작 확인 권장.
- Supabase·env(SUPABASE_URL, SUPABASE_KEY 등) 설정 필요.

---

## 4. 주의사항 / 후속 작업

- **영상 경로**: Dashboard 컨테이너에서 영상 파일 접근을 위해 `/data/shortflow/data` 볼륨이 마운트되어 있어야 함. 현재 docker-compose는 `./data:/data/shortflow`로 마운트되어 있으며, worker가 저장하는 경로가 동일한 루트를 사용하면 접근 가능.
- **Quota 현황**: Overview의 YouTube Quota는 채널 목록만 표시. 일일 사용량은 YouTubeUploadManager가 메모리에서 관리하므로 DB/API 연동 시 확장(TODO).
- **스크립트 QA**: 승인 시 job은 QA_PENDING 유지. 영상 QA에서 최종 Approve 시 QA_APPROVED로 전이 후 업로드 대기.
