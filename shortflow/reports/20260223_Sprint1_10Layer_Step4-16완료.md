# Sprint 1 – 10-Layer 엔진 Step 4~16 완료

**작성일시:** 2026-02-23
**작업 유형:** 신규 개발
**상태:** 완료
**관련 파일:**
- `engine/script_variation.py`, `engine/voice_variation.py`, `engine/bgm_variation.py`
- `engine/metadata_variation.py`, `engine/upload_pattern.py`, `engine/narrative_injection.py`
- `engine/structural_variation.py`, `engine/cross_video_checker.py`
- `engine/collision_avoidance.py`, `engine/style_seed.py`
- `engine/anti_inauthentic.py` (전 레이어 연동)
- `templates/script_archetypes/*.txt` (7개), `templates/structural_patterns/*.json` (4개)
- `templates/visual_components.json`, `engine/test_10layer_integration.py`

---

## 1. 작업 개요

Sprint 1 Step 4부터 Step 16까지 진행하여 10-Layer 양산형 회피 엔진의 나머지 레이어를 구현하고, 오케스트레이터에 전부 연동한 뒤 통합 테스트를 실행·통과시켰다.

## 2. 변경 사항

### Step 4: Layer 2 – Script Variation
- **engine/script_variation.py**: `ScriptVariation` 유지, `select_archetype(recent_archetypes)`, `get_phrases()` / `get_phrases_result()` (기존 연동 유지)
- **templates/script_archetypes/**: 7개 아키타입 txt (experience_review, comparison, question_hook, ranking, problem_solving, trend_alert, twist_hook), 각 `=== INTRO ===` / `=== BODY ===` / `=== OUTRO ===` 5문장씩

### Step 5: Layer 3 – Voice Variation
- **engine/voice_variation.py**: 기존 `VoiceVariation`, `VoiceParamsResult`, `get_voice_params(recent_params)` (프리셋·rate/pitch/pause) 유지

### Step 6: Layer 4 – BGM Variation
- **engine/bgm_variation.py**: 기존 `BGMVariation`, `BGMResult`, `select_bgm(category, recent_bgms)` (카테고리별 라이브러리, 볼륨·오프셋) 유지

### Step 7: Layer 5 – Metadata Variation
- **engine/metadata_variation.py**: `MetadataVariation`, `MetadataResult`
- 제목 공식 10가지(기획서 3.3), `generate_metadata(product_name, price, category, brand, recent_titles, **kwargs)` → title, description, tags (고정 5 + 동적 10~15)

### Step 8: Layer 6 – Upload Pattern
- **engine/upload_pattern.py**: `UploadPattern`, 기본 슬롯 09:00/13:00/18:00 KST, ±30분 오프셋, 주말 1~2건, 월 1~2회 휴일
- `get_next_slot(current_date, recent_uploads)` → `Optional[datetime]`

### Step 9: Layer 8 – Narrative Injection
- **engine/narrative_injection.py**: `NarrativeInjection`, 템플릿 기반(LLM 없음)
- `generate_opinion(product_attrs)` → 상품 속성(소재, 색상, 핏, 가격대, 용도, 계절) 기반 1~2문장

### Step 10: Layer 9 – Structural Variation
- **engine/structural_variation.py**: `StructuralVariation`, 4가지 패턴(standard, reverse_price_first, question_start, comparison_start)
- **templates/structural_patterns/**: 4개 json (order 등)
- `select_pattern(recent_patterns)`, `get_pattern_config()`

### Step 11: Layer 10 – Cross-Video Checker
- **engine/cross_video_checker.py**: `CrossVideoChecker`
- pHash(imagehash 선택), 오디오 FFmpeg 추출 해시 대체, 텍스트 TF-IDF(sklearn 선택) 또는 Jaccard
- 임계값 0.85, `check(current_video_path, recent_video_paths, current_script, recent_scripts)` → (similar: bool, scores: dict)

### Step 12: Collision Avoidance
- **engine/collision_avoidance.py**: `CollisionAvoidance`, `AssignedCombination`
- product_id 기준 중복 감지, 사용자별 아키타입·레이아웃·보이스 조합 강제 배정

### Step 13: Style Seed
- **engine/style_seed.py**: `StyleSeedManager`, `StyleSeed`
- 사용자별 색상 테마, 텍스트 스타일, TTS 톤 프리셋 (user_id 시드 기반)

### Step 14~16: 템플릿·오케스트레이터·테스트
- **templates/visual_components.json**: 5 컴포넌트 × 5 변형 참조
- **engine/anti_inauthentic.py**: Layer 2~6, 8~10 및 CollisionAvoidance, StyleSeed 연동
  - `suggest_bgm`, `suggest_metadata`, `suggest_upload_slot`, `suggest_opinion`, `suggest_structure`, `check_cross_video`, `assign_combination`, `get_style_seed`
- **engine/test_10layer_integration.py**: import, evaluate, suggest_*(1~9), style_seed, collision, cross_video 검증

## 3. 테스트 결과

- `python3 -m engine.test_10layer_integration` 실행: 4단계(Imports, evaluate, suggest layers, cross_video_check) 모두 통과.

## 4. 주의사항 / 후속 작업

- Layer 10: imagehash·sklearn 미설치 시 프레임/텍스트는 fallback(파일 해시·Jaccard)으로 동작. 필요 시 `worker/requirements.txt` 등에 imagehash, scikit-learn 추가 검토.
- 파이프라인 워커에서 `suggest_*`·`check_cross_video`·`assign_combination` 실제 호출 연동은 Sprint 4 등에서 진행 예정.
- BGM 라이브러리 실제 파일 경로·DB 연동은 설정/배포 단계에서 확장.
