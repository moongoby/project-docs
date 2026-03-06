# SF-T017: QA Score Engine v2 구현 보고서

**작성일**: 2026-03-06
**Task ID**: SF-T017
**우선순위**: P1-HIGH

---

## 개요

SF-T002에서 구현된 QA 스코어 엔진 v1을 SF-T009/T011의 새 구조(후크·CTA·루프·메타데이터)에 맞춰 v2로 재설계.
CEO 지시 D-002(품질 최우선)에 따라 85점 이상만 업로드 허용하는 게이트 역할 수행.

---

## 구현 내용

### 1. engine/qa_score_engine.py (v2)

4항목 25점 만점 체계:

| 항목 | 메서드 | 만점 | 평가 기준 |
|------|--------|------|-----------|
| 대본 품질 | `score_script()` | 25점 | 후크(7), 세그먼트≥3(6), CTA(4), 루프엔딩(4), 제목≤50자(4) |
| 영상 품질 | `score_video()` | 25점 | 해상도1080×1920(8), FPS29-30(4), H.264(4), AAC(4), 길이15-60s(5) |
| 오디오/TTS | `score_audio()` | 25점 | TTS대본존재(10), 적정길이30-55s(8), bg_keyword전체(7) |
| 메타데이터 | `score_metadata()` | 25점 | 제목≤100자(5), 해시태그포함(5), 태그≥5개(5), CTA문구(5), 면책조항(5) |

합산 85점 이상 → PASS (업로드 허용)

### 2. scripts/run_qa_check.py (CLI)

```
python3 scripts/run_qa_check.py \
  --script output/economy_script.json \
  --video output/economy.mp4 \
  --title "제목" --description "설명" --tags "경제,재테크,shorts"
```

### 3. run_v5_pipeline.py QA 게이트 (SF-T016 연동 대기)

SF-T016 파일(`run_v5_pipeline.py`)이 아직 생성되지 않아 직접 삽입 불가.
아래 코드를 FFmpeg 합성 후, 업로드 전에 삽입 필요:

```python
from engine.qa_score_engine import QAScoreEngine
qa = QAScoreEngine()
qa_result = qa.evaluate_all(script_result, video_path, title, description, tags)
if not qa_result['pass']:
    logger.warning(f"QA FAIL: {qa_result['total']}/{qa_result['threshold']} — 업로드 건너뜀")
    continue
logger.info(f"QA PASS: {qa_result['total']}/100")
```

---

## Dry-run 테스트 결과

```python
mock = {
    'hook': '테스트 후크',
    'segments': [
        {'text': 's1', 'bg_keyword': 'money'},
        {'text': 's2', 'bg_keyword': 'chart'},
        {'text': 's3', 'bg_keyword': 'bank'}
    ],
    'cta': '구독!',
    'loop_bridge': '다음편',
    'title_options': ['짧은 제목'],
    'total_duration_sec': 45
}
qa.score_script(mock)   # → 25/25
qa.score_audio(mock)    # → 25/25
qa.score_metadata('테스트 제목', '#경제 #재테크 구독 🔔 ⚠️ 투자조언아님', ['경제','재테크','shorts','쇼츠','투자'])  # → 25/25
```

**출력**: `{'scores': {'script': 25, 'audio': 25, 'metadata': 25}, 'total': 75, 'threshold': 85, 'pass': False}`

- script: 25/25 ✅
- audio: 25/25 ✅
- metadata: 25/25 ✅
- video: 0/25 (mock 테스트에 MP4 없음 — 실제 파이프라인에서 실행 시 video score 추가)
- 실제 영상 포함 시 예상 합계: 100/100

---

## Git 커밋

```
489ae57 [SF] SF-T017: QA Score Engine v2 — 4항목 25점 만점, 85점 게이트
```

---

## 완료 기준 달성 여부

- [x] `engine/qa_score_engine.py` v2 생성
- [x] `scripts/run_qa_check.py` CLI 생성
- [x] dry-run mock 테스트 정상 실행
- [x] 로컬 커밋 완료 (commit 489ae57)
- [ ] `run_v5_pipeline.py` QA 게이트 삽입 — SF-T016 완료 후 수행 예정
