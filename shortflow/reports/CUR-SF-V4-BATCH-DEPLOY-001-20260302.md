# CUR-SF-V4-BATCH-DEPLOY-001-20260302
작성일시: 2026-03-02 21:04 KST
작성자: Cursor Agent (ShortFlow)

---

## 1. 작업 개요

Directive: CUR-SF 지시서 — 2026-03-02 #001
실행 STEP: GEMINI-CODE-CLEANUP → V4-BATCH → V4-CRON → OLD-VIDEO-DELETE

---

## 2. STEP 1 — GEMINI-CODE-CLEANUP

### 스캔 결과
```
grep -rn "gemini-2.0-flash" --include="*.py" --include="*.json" --include="*.yaml" --include="*.yml" . (backups/venv 제외)
결과: 0건
```

- 실제 소스 코드(.py, .json, .yaml, .yml, .env.example)에 `gemini-2.0-flash` 참조: **0건**
- backups/ 디렉토리에만 잔존 (백업 파일 — 변경 불필요)
- 이전 커밋 `299119b` ("docs: 인계서 시스템 구축 + gemini-2.0-flash→2.5-flash 일괄 교체")에서 이미 완료
- engine/llm_script_engine.py: `model_name='gemini-2.5-flash'` 확인

**결론: GEMINI-CODE-CLEANUP 이미 완료 상태 확인**

---

## 3. STEP 2 — V4-BATCH (v4 전편 합성 + 비공개 업로드)

### 합성 실행 (신규 2편 economy + 2편 health, 기존 1편씩 이미 존재)

| 채널 | 파일명 | 결과 |
|------|--------|------|
| economy | 20260226_180813_달러_환율_급등_v4.mp4 | 합성 완료 |
| economy | 20260226_180831_달러_또_올랐다_v4.mp4 | 합성 완료 |
| health | 20260226_180916_40대부터_반드시_먹어야_할_음식_5_v4.mp4 | 합성 완료 |
| health | 20260226_180933_40대부터_반드시_먹어야_할_음식_5_v4.mp4 | 합성 완료 |

### ffprobe 검증 결과 (전편 6편)

| 파일 | 해상도 | 오디오 | 결과 |
|------|--------|--------|------|
| economy/20260226_180813_v4.mp4 | 1080x1920 | aac | PASS |
| economy/20260226_180831_v4.mp4 | 1080x1920 | aac | PASS |
| economy/20260226_180855_v4.mp4 | 1080x1920 | aac | PASS |
| health/20260226_180916_v4.mp4 | 1080x1920 | aac | PASS |
| health/20260226_180933_v4.mp4 | 1080x1920 | aac | PASS |
| health/20260226_180949_v4.mp4 | 1080x1920 | aac | PASS |

### YouTube 비공개 업로드 결과

| 채널 | 파일 | 영상 ID | 상태 |
|------|------|---------|------|
| economy (3분경제) | 20260226_180855_v4.mp4 | 6s5UU1vFCvg | private |
| economy (3분경제) | 20260226_180813_v4.mp4 | VIMxlQSSXUQ | private |
| economy (3분경제) | 20260226_180831_v4.mp4 | tpeRTVKNtng | private |
| health (건강한입) | 20260226_180949_v4.mp4 | 4ZWoA8hbkWs | private |
| health (건강한입) | 20260226_180916_v4.mp4 | RtmEvQoM7Iw | private |
| health (건강한입) | 20260226_180933_v4.mp4 | OW3_51k40LY | private |

**총 6편 비공개 업로드 성공 (CEO 승인 전까지 private 유지)**

---

## 4. STEP 3 — V4-CRON (크론 스케줄러 v4 파이프라인 교체)

### 변경 전 (v3 기반)
```cron
0 9,13,18 * * * cd /data/shortflow && venv/bin/python scripts/youtube_upload.py economy >> logs/upload_economy.log 2>&1
10 9,13,18 * * * cd /data/shortflow && venv/bin/python scripts/youtube_upload.py health >> logs/upload_health.log 2>&1
```

### 변경 후 (v4 파이프라인)
```cron
# === ShortFlow v4 파이프라인 크론 (2026-03-02 교체) ===
# economy: 09:00 / 13:00 / 18:00 KST (대본생성→v4합성→비공개업로드)
0 9,13,18 * * * cd /data/shortflow && venv/bin/python scripts/run_v4_pipeline.py economy >> logs/upload_economy.log 2>&1
# health: 09:10 / 13:10 / 18:10 KST
10 9,13,18 * * * cd /data/shortflow && venv/bin/python scripts/run_v4_pipeline.py health >> logs/upload_health.log 2>&1
```

### 신규 스크립트: `scripts/run_v4_pipeline.py`
- LLM 대본 생성 (Gemini 2.5 Flash → Claude 폴백) → v4 영상 합성 → YouTube 비공개 업로드
- 스케줄 시간 동일 유지 (economy 09/13/18, health +10분)
- 구 scheduled_upload.sh 기반 크론은 주석 처리 비활성화

---

## 5. STEP 4 — OLD-VIDEO-DELETE (v1/v3 테스트 영상 삭제)

### 삭제 완료 (18건, 실패 0건)

#### v1 단색배경 (10편)
| 채널 | 영상 ID | 결과 |
|------|---------|------|
| economy | MJ67w3RC6WY | 삭제 완료 |
| economy | F4XzKFOjHC8 | 삭제 완료 |
| economy | sII3HTMbW9M | 삭제 완료 |
| economy | 8C3ZVXSWI5Q | 삭제 완료 |
| economy | wiFHsK1Xv6s | 삭제 완료 |
| health | GWTg7Q0m4Eo | 삭제 완료 |
| health | Kjm85E2_nZo | 삭제 완료 |
| health | D8o9kQv3uNk | 삭제 완료 |
| health | qxDNvO-QxbM | 삭제 완료 |
| health | k_DioBh1E8E | 삭제 완료 |

#### v3 스톡배경 (6편)
| 채널 | 영상 ID | 결과 |
|------|---------|------|
| economy | A0hKCxBRyHM | 삭제 완료 |
| economy | KR_SJC0bcas | 삭제 완료 |
| economy | mpB4VvUCIN4 | 삭제 완료 |
| health | 0GoqZ8wlYTk | 삭제 완료 |
| health | jnjMEtVUfSY | 삭제 완료 |
| health | _A3lEw_hxIM | 삭제 완료 |

#### UPLOAD-TEST (2편)
| 채널 | 영상 ID | 결과 |
|------|---------|------|
| economy | ZwysqK_puMY | SKIP (이미 삭제됨) |
| health | nZkJ9PjviH4 | SKIP (이미 삭제됨) |

---

## 6. 커밋 정보

- commit SHA: `f833106`
- 커밋 메시지: `[SF] V4-BATCH/CRON/DELETE: v4 전편 합성+업로드, v4 파이프라인 크론 교체, v1/v3 테스트 영상 삭제`
- push: main → origin/main 성공

### 신규 파일
- `scripts/run_v4_pipeline.py` — v4 풀 파이프라인 크론 스크립트
- `scripts/upload_v4_batch.py` — v4 배치 업로드 스크립트
- `scripts/delete_old_videos.py` — v1/v3 테스트 영상 삭제 스크립트

---

## 7. 보안 스캔

```
security_scan: 0건 (211.188.*, genspark_dev@, kill.switch 미검출)
.env/토큰 커밋 없음 확인
```

---

## 8. 저장 정보

```
완료일시: 2026-03-02 21:04 KST
서버 경로: /data/shortflow
보고서: /data/project-docs/shortflow/reports/CUR-SF-V4-BATCH-DEPLOY-001-20260302.md
GitHub ShortFlow: https://github.com/moongoby/shortflow/commit/f833106
GitHub project-docs: https://github.com/moongoby/project-docs
커밋 SHA: f833106
security_scan: PASS (0건)
path_check: PASS
HANDOVER 업데이트: 완료 예정 (별도 커밋)
```
