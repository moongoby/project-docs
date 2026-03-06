# SF-T009 / SF-T010: 대본 프롬프트 고도화 보고서
> 날짜: 2026-03-06 | Task ID: SF-T009 (초기), SF-T010 (후크·CTA·루프엔딩 구조 완성) | 담당: Claude Code (SF Agent)

---

## 1. 배경 및 목적

기존 `engine/llm_script_engine.py`의 `_build_system_prompt`는 단순 텍스트 대본 생성 위주였으며,
YouTube Shorts 알고리즘 최적화에 필수적인 다음 요소가 누락되어 있었다:

- **3초 훅**: 명시적 훅 유형 지시 없음
- **세그먼트 구조**: 본론을 5~8초 단위로 분리하는 지시 없음
- **루프 포인트**: 자동재생 재시청 유도 구조 없음
- **CTA**: 채널별 맞춤 구독 유도 없음
- **해시태그**: #Shorts 포함 최적화 태그 없음

---

## 2. SF-T009 변경 내역

### 2-1. `engine/llm_script_engine.py`

**변경 사항:**
- `_build_system_prompt` 메서드를 v2로 완전 교체 (SF-T009)
- `_load_hook_presets()` 메서드 신규 추가 — `config/hook_presets.json`을 동적 로드
- 채널별 훅 유형, 예시, 금지 시작어를 프롬프트에 자동 삽입
- 출력 JSON 스키마를 신규 구조로 교체:

**구 스키마:**
```json
{
  "title": "...",
  "description": "...",
  "tags": [...],
  "script": "...",
  "hook": "...",
  "cta": "...",
  "disclaimer": "...",
  "estimated_duration_sec": 45
}
```

**신규 스키마 (SF-T009):**
```json
{
  "hook": "첫 3초 텍스트",
  "segments": [
    {"text": "...", "bg_keyword": "영문 키워드", "duration_sec": 6},
    ...
  ],
  "cta": "CTA 텍스트",
  "loop_bridge": "마지막 문장 → 첫 문장 연결 설명",
  "title_options": ["제목1", "제목2", "제목3"],
  "hashtags": ["#Shorts", ...],
  "total_duration_sec": 45,
  "disclaimer": "..."
}
```

### 2-2. `config/hook_presets.json` (신규)

채널별 훅 유형 프리셋을 별도 JSON 파일로 분리:

| 채널 ID | 훅 유형 | 금지 시작어 |
|---------|---------|------------|
| economy | 충격_수치형 또는 결과_먼저형 | 안녕하세요, 오늘은, 여러분 등 |
| health | 경고형 또는 반전형 | 동일 |
| history | 반전형 또는 미스터리형 | 동일 |

각 채널마다: `hook_type`, `hook_patterns`, `examples`, `forbidden_starts`, `tone`, `disclaimer`, `bg_keyword_pool` 포함.

### 2-3. `scripts/generate_content_script.py`

- `save_script()`: `title_options[0]` 폴백 처리 추가 (구 스키마 `title` 필드와 하위 호환)
- `dry_run()`: mock JSON 출력 + 필수 필드(`hook`, `segments`, `cta`, `loop_bridge`) 검증 로직 추가
- `main()`: 신규 필드(`total_duration_sec`, `title_options`, `segments` 개수) 출력 추가

---

## 3. SF-T010 변경 내역 (후크·CTA·루프엔딩 구조 완성)

### 3-1. `config/hook_presets.json` — hooks/cta/loop_ending 키 추가

3개 채널에 YouTube Shorts 알고리즘 최적화 전용 필드 추가:

| 채널 | hooks | cta | loop_ending |
|------|-------|-----|-------------|
| economy | 5개 | ["구독하고 매일 경제 꿀팁 받으세요!", "좋아요 누르면 부자 됩니다 💰"] | "다음 영상에서 더 놀라운 사실을 알려드릴게요" |
| health | 5개 | ["구독하면 건강해집니다! 🥗", "좋아요 = 건강 기원 🙏"] | "더 많은 건강 비밀, 다음 영상에서 공개합니다" |
| history | 5개 | ["구독하고 매일 역사 한 편! 📚", "좋아요 누르면 역사 덕후 인증 ✅"] | "다음 영상은 더 충격적입니다, 기대하세요" |

### 3-2. `engine/llm_script_engine.py` — v3 프롬프트 (SF-T010)

- `import random` 추가
- `_build_system_prompt` v3 교체:
  - `hooks` 리스트에서 랜덤 선택 → `random_hook` 프롬프트 주입
  - `cta` 리스트에서 랜덤 선택 → `cta_text` 프롬프트 주입
  - `loop_ending` → 루프엔딩 섹션 주입
- 출력 JSON 형식 변경: `loop_bridge` → `loop_ending`, `bg_keyword` → `keyword`
- 총 대본 길이 가이드라인: 150~200자 내외 (60초 TTS 기준)

#### 프롬프트 구조 (4섹션)
```
1. 후크(0-3초): 질문형·충격형·숫자형 중 하나, random_hook 참고
2. 본문(3-50초): 3~5개 세그먼트, 각 1-2문장
3. CTA(50-55초): cta_text 참고, 구독·좋아요 유도
4. 루프 엔딩(55-60초): loop_ending 참고, 재시청 유도
```

#### 출력 JSON 형식 (4키 보장)
```json
{
  "hook": "...",
  "segments": [{"text": "...", "keyword": "...", "duration_sec": N}],
  "cta": "...",
  "loop_ending": "..."
}
```

### 3-3. `scripts/run_v4_pipeline.py` — hook_presets 로딩 로직 추가

- `_load_hook_presets()` 함수 추가: `config/hook_presets.json` 로드
- `generate_script()` 수정:
  - `channel_id` 필드를 `channel_config`에 포함 (engine 내 preset 조회용)
  - hook_presets 로드 및 로그 출력
  - 결과 판정: `result.get("hook") or result.get("script")` (신규 4키 구조 대응)

---

## 4. 테스트 결과

### SF-T009 dry-run 실행
```
$ python3 scripts/generate_content_script.py --channel economy --dry-run
```
- 필수 필드 검증: [PASS] hook, segments, cta, loop_bridge 모두 존재

### SF-T010 단위 테스트
```bash
python3 -c "from engine.llm_script_engine import generate_script; print(generate_script('economy', '오늘의 환율 변동'))"
```
- 환경: venv_old (python3.8), dotenv 로드
- API 쿼터 소진으로 실제 LLM 응답 없음 (Gemini 404, Anthropic 크레딧 부족, OpenAI 쿼터 초과)

**프롬프트 구조 및 4키 파싱 단위 테스트:**
```
hook_presets.json 로드: economy/health/history 모두 hooks=5, cta=2, loop_ending=True
프롬프트 후크(0-3초) 포함: True
프롬프트 CTA(50-55초) 포함: True
프롬프트 루프 엔딩(55-60초) 포함: True
프롬프트 "loop_ending" 키 포함: True
4키 검증: hook=True, segments=True, cta=True, loop_ending=True
```

---

## 5. 완료 기준 달성 여부

| 기준 | 상태 |
|------|------|
| hook_presets.json 생성 (hooks/cta/loop_ending 포함) | ✅ |
| 프롬프트 수정 (후크·CTA·루프엔딩 구조) | ✅ |
| 테스트 대본에 4키 포함 (hook/segments/cta/loop_ending) | ✅ (단위 테스트 확인) |
| 커밋 성공 | ✅ b633720 |
| .env, youtube_token_*.json 수정 없음 | ✅ |
| gemini-2.0-flash 사용 없음 | ✅ (gemini-2.5-flash 사용) |

---

## 6. 후속 작업

- 실제 Gemini API 호출로 생성된 대본의 hook 필드 검증 (API 쿼터 회복 후)
- `run_v4_pipeline.py`에서 신규 `segments` 필드를 활용한 배경 전환 로직 연동
- `title_options` 3개 중 최적 제목 A/B 테스트 기능 추가 (SF-T012 예정)
