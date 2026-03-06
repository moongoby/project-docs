# SF-T016: Pipeline v5 통합 보고서

**작성일**: 2026-03-06
**Task ID**: SF-T016
**우선순위**: P0-CRITICAL
**상태**: ✅ 완료

---

## 1. 개요

SF-T009(프롬프트v2), SF-T011(메타데이터), SF-T013(PerformanceTracker), SF-T014(ContentPlanner)가 각각 독립 모듈로 구현된 상태에서, 이 모든 모듈을 통합한 `run_v5_pipeline.py`를 신규 생성하고 크론을 v4 → v5로 교체함.

---

## 2. v5 파이프라인 흐름

```
[1] ContentPlanner.plan_today(1)     → 오늘 주제 1건 선정 (Gemini 2.5 Flash 트렌드 기획)
[2] LLMScriptEngine.generate(topic)  → 후크·세그먼트·CTA·루프엔딩 JSON 대본 (v2 프롬프트)
[3] Edge-TTS                         → 음성 합성 (pilot_video_e2e_v4.py)
[4] Pexels 스톡 다운로드             → bg_keyword 기반
[5] FFmpeg v4 합성                   → 1080x1920, H.264, 자막 하단 20%
[6] upload_metadata.json 적용        → YouTube 업로드 (QA 판정 privacy)
[7] PerformanceTracker.append_to_registry() → video_registry.json 자동 등록 (version=v5)
[8] 완료 로그                        → 주제·angle·영상ID·QA score 기록
```

---

## 3. 생성 파일

| 파일 | 설명 |
|------|------|
| `scripts/run_v5_pipeline.py` | v5 파이프라인 메인 스크립트 (신규) |
| `backups/shortflow_pre_T016_20260306_191859.tar.gz` | 작업 전 전체 백업 |
| `backups/crontab_pre_T016_20260306.bak` | 크론 백업 |

---

## 4. 주요 변경 사항

### 4.1 주제 선정 단계 추가 (Step 1)

```python
from engine.content_planner import ContentPlanner
planner = ContentPlanner(channel_id)
topics = planner.plan_today(count=1)  # 또는 dry_run 시 planner.dry_run(count=1)
topic = topics[0] if topics else FALLBACK_TOPICS[channel]
```

- ContentPlanner 실패 시 채널별 폴백 주제 자동 사용
- dry_run 모드에서는 Gemini API 호출 없이 mock 주제 반환

### 4.2 대본 생성에 topic/angle 전달 (Step 2)

```python
channel_config = {
    "channel_name": CHANNEL_NAMES[channel],
    "channel_id": channel,
    "topic": topic["topic"],     # SF-T014 ContentPlanner 선정 주제
    "angle": topic.get("angle", ""),  # 영상 각도
}
result = engine.generate(channel_config=channel_config, subject=topic_str)
```

- SF-T009에서 이미 프롬프트에 topic/angle 변수 존재 → 자연스럽게 연결

### 4.3 메타데이터 적용 (Step 6)

```python
ch_meta = UPLOAD_METADATA.get(channel, {})
description = _build_description(channel, title, hook=hook, cta=cta)
tags = ch_meta.get("tags", _get_tags(channel))
upload_title = f"{script_title} | {channel_name}"[:100]
```

- `config/upload_metadata.json` 기반 description_template/tags 적용
- title_options[0] > title > topic['topic'] > raw_title 순 우선

### 4.4 video_registry 자동 등록 (Step 7)

```python
PerformanceTracker.append_to_registry(channel, video_id, title=reg_title, version="v5")
```

- v4 대비 version="v5" 태그 추가로 구분 가능

### 4.5 --dry-run 플래그

```bash
python3 scripts/run_v5_pipeline.py economy --dry-run
```

- ContentPlanner: `dry_run()` 호출 (Gemini API 호출 없음)
- 대본 생성: mock 데이터 반환 (LLM API 호출 없음)
- 영상 합성·업로드: 완전 스킵
- 메타데이터 미리보기: 주제/angle/keyword/제목/태그/설명/hook/CTA 출력

---

## 5. 크론 교체 결과

### AS-IS (v4)
```
30 7  * * * cd /data/shortflow && venv/bin/python scripts/run_v4_pipeline.py economy >> /data/shortflow/logs/upload_economy.log 2>&1
0  12 * * * cd /data/shortflow && venv/bin/python scripts/run_v4_pipeline.py economy >> /data/shortflow/logs/upload_economy.log 2>&1
0  19 * * * cd /data/shortflow && venv/bin/python scripts/run_v4_pipeline.py economy >> /data/shortflow/logs/upload_economy.log 2>&1
40 7  * * * cd /data/shortflow && venv/bin/python scripts/run_v4_pipeline.py health  >> /data/shortflow/logs/upload_health.log 2>&1
10 12 * * * cd /data/shortflow && venv/bin/python scripts/run_v4_pipeline.py health  >> /data/shortflow/logs/upload_health.log 2>&1
10 19 * * * cd /data/shortflow && venv/bin/python scripts/run_v4_pipeline.py health  >> /data/shortflow/logs/upload_health.log 2>&1
```

### TO-BE (v5)
```
30 7  * * * cd /data/shortflow && /data/shortflow/venv/bin/python3 scripts/run_v5_pipeline.py economy >> /data/shortflow/logs/v5_economy.log 2>&1
0  12 * * * cd /data/shortflow && /data/shortflow/venv/bin/python3 scripts/run_v5_pipeline.py economy >> /data/shortflow/logs/v5_economy.log 2>&1
0  19 * * * cd /data/shortflow && /data/shortflow/venv/bin/python3 scripts/run_v5_pipeline.py economy >> /data/shortflow/logs/v5_economy.log 2>&1
40 7  * * * cd /data/shortflow && /data/shortflow/venv/bin/python3 scripts/run_v5_pipeline.py health  >> /data/shortflow/logs/v5_health.log 2>&1
10 12 * * * cd /data/shortflow && /data/shortflow/venv/bin/python3 scripts/run_v5_pipeline.py health  >> /data/shortflow/logs/v5_health.log 2>&1
10 19 * * * cd /data/shortflow && /data/shortflow/venv/bin/python3 scripts/run_v5_pipeline.py health  >> /data/shortflow/logs/v5_health.log 2>&1
```

- run_v4_pipeline.py는 폴백용으로 유지 (삭제 안 함)

---

## 6. dry-run 테스트 결과

### 6-1. economy 채널 (2026-03-06 19:29)

```
[2026-03-06 19:29:13] === v5 파이프라인 시작: economy | dry_run=True ===
[2026-03-06 19:29:13] [Step 1] ContentPlanner 주제 선정 시작 (channel=economy, dry_run=True)
[2026-03-06 19:29:13] [Step 1] ContentPlanner 주제 선정 완료: 환율 급등 대처법
[2026-03-06 19:29:13] [Step 2] 대본 생성 시작: 환율 급등 대처법 (angle=달러 강세 시 재테크 전략)
[2026-03-06 19:29:13] [Step 2] [DRY-RUN] 대본 생성 스킵 → 목업 반환
[2026-03-06 19:29:13] 대본 저장: .../economy/20260306_192913_환율_급등_대처법.json
[2026-03-06 19:29:13] [DRY-RUN] 영상 합성·업로드 스킵
[2026-03-06 19:29:13] [DRY-RUN] 주제     : 환율 급등 대처법
[2026-03-06 19:29:13] [DRY-RUN] angle    : 달러 강세 시 재테크 전략
[2026-03-06 19:29:13] [DRY-RUN] keyword  : exchange rate dollar
[2026-03-06 19:29:13] [DRY-RUN] 제목     : 환율 급등 대처법 | 3분경제
[2026-03-06 19:29:13] [DRY-RUN] 태그     : ['경제', '재테크', '주식', '환율', '투자']
[2026-03-06 19:29:13] [DRY-RUN] 설명(앞80): 환율 급등 대처법\n\n이걸 모르면 손해! ...
[2026-03-06 19:29:13] [DRY-RUN] hook     : 이걸 모르면 손해! 환율 급등 대처법
[2026-03-06 19:29:13] [DRY-RUN] CTA      : 구독·좋아요 부탁드립니다!
[2026-03-06 19:29:13] === v5 파이프라인 dry-run 완료: economy ===
```

**결과**: ✅ PASS (exit code 0)

### 6-2. health 채널 (2026-03-06 19:29)

```
[2026-03-06 19:29:16] === v5 파이프라인 시작: health | dry_run=True ===
[2026-03-06 19:29:16] [Step 1] ContentPlanner 주제 선정 시작 (channel=health, dry_run=True)
[2026-03-06 19:29:16] [Step 1] ContentPlanner 주제 선정 완료: 아침 공복에 먹으면 안 되는 음식
[2026-03-06 19:29:16] [Step 2] 대본 생성 시작: 아침 공복에 먹으면 안 되는 음식 (angle=위산 과다·혈당 스파이크 원인 식품)
[2026-03-06 19:29:16] [Step 2] [DRY-RUN] 대본 생성 스킵 → 목업 반환
[2026-03-06 19:29:16] 대본 저장: .../health/20260306_192916_아침_공복에_먹으면_안_되는_음식.json
[2026-03-06 19:29:16] [DRY-RUN] 영상 합성·업로드 스킵
[2026-03-06 19:29:16] [DRY-RUN] 주제     : 아침 공복에 먹으면 안 되는 음식
[2026-03-06 19:29:16] [DRY-RUN] angle    : 위산 과다·혈당 스파이크 원인 식품
[2026-03-06 19:29:16] [DRY-RUN] keyword  : healthy breakfast food
[2026-03-06 19:29:16] [DRY-RUN] 제목     : 아침 공복에 먹으면 안 되는 음식 | 건강한입
[2026-03-06 19:29:16] [DRY-RUN] 태그     : ['건강', '다이어트', '음식', '영양소', '건강정보']
[2026-03-06 19:29:16] [DRY-RUN] hook     : 이걸 모르면 손해! 아침 공복에 먹으면 안 되는 음식
[2026-03-06 19:29:16] [DRY-RUN] CTA      : 구독·좋아요 부탁드립니다!
[2026-03-06 19:29:16] === v5 파이프라인 dry-run 완료: health ===
```

**결과**: ✅ PASS (exit code 0)

---

## 7. 로컬 커밋

```
커밋: 02195c8
메시지: [SF] SF-T016: Pipeline v5 통합 — Planner→프롬프트v2→메타데이터→Tracker 자동 연결
변경: 16 files changed, 2831 insertions(+), 57 deletions(-)
```

---

## 8. 완료 기준 체크리스트

- [x] run_v5_pipeline.py 생성
- [x] ContentPlanner 통합 (plan_today/dry_run)
- [x] topic/angle → LLMScriptEngine 전달
- [x] upload_metadata.json 메타데이터 적용
- [x] PerformanceTracker.append_to_registry(version="v5") 자동 등록
- [x] --dry-run 플래그 구현
- [x] 크론 v4 → v5 교체 (economy/health 6슬롯)
- [x] crontab 백업 (`backups/crontab_pre_T016_20260306.bak`)
- [x] dry-run PASS (economy 채널, 19:29 KST)
- [x] dry-run PASS (health 채널, 19:29 KST)
- [x] data/qa_logs/.gitkeep 디렉터리 생성
- [x] backups/crontab_pre_T016.txt 저장
- [x] backups/crontab_post_T016.txt 저장
- [x] 로컬 커밋 완료
- [x] HANDOVER.md §2 갱신 (T005/T008/T009/T011/T013/T014/T015/T016/T017 전체 정비)
- [x] run_v4_pipeline.py 유지 (폴백용)

---

## 9. 의존성

| Task | 상태 | 연결 방식 |
|------|------|-----------|
| SF-T009 (프롬프트v2) | ✅ 완료 | channel_config에 topic/angle 전달 |
| SF-T011 (메타데이터) | ✅ 완료 | upload_metadata.json → _build_description() |
| SF-T013 (PerformanceTracker) | ✅ 완료 | append_to_registry(version="v5") |
| SF-T014 (ContentPlanner) | ✅ 완료 | plan_today(1) / dry_run(1) |

---

*생성: Claude Sonnet 4.6 | SF-T016 완료 2026-03-06 KST*
