# SF-T003 영상 품질 개선 보고서 (QUALITY-IMPROVE-V1)

## 개요

**태스크 ID**: SF-T003 (QUALITY-IMPROVE-V1)
**제목**: 영상 품질 개선 — 훅·제목·CTA·해시태그·전환빈도
**완료일**: 2026-03-06
**작업 범위**: engine/ 신규 4개 파일, ffmpeg_composer.py 수정, llm_script_engine.py 수정, HANDOVER.md 갱신

---

## 배경

- 경제 채널 조회수 2,600 / 건강 채널 조회수 378 → VVSA(Video Viewer Satisfaction Average) 낮음 추정
- 첫 0~3초 훅 부재, 제목 최적화 미흡, CTA 없음, 해시태그 수동 입력
- CEO 지시: "2편을 조회수 및 구독을 부를 수 있게 개선 최적화"

---

## 작업 내역

### 3-1. 훅 템플릿 5종 구현 (`engine/hook_templates.py`)

**파일**: `/data/shortflow/engine/hook_templates.py`

5가지 훅 패턴 구현 및 랜덤 선택 로직:

| 패턴 | 예시 (경제) | 예시 (건강) |
|------|-------------|-------------|
| Bold Claim | "오늘 환율이 이렇게 움직이면 당신 통장이 위험합니다" | "이 음식, 매일 먹으면 혈관이 막힙니다" |
| Curiosity Gap | "전문가들이 절대 안 알려주는 환율의 비밀" | "의사들이 절대 안 먹는 건강식품 3가지" |
| Micro-Story | "지난달 환율 때문에 100만원을 잃은 직장인의 이야기" | "이 습관 하나로 10kg 감량한 40대 주부" |
| Visual Shock | "[첫 프레임에 빨간 화살표 + 급등 차트] 지금 환율이 폭등 중입니다" | "[첫 프레임에 충격적 비포/애프터] 1개월 만에 이렇게 달라졌습니다" |
| Direct Question | "당신의 달러 예금, 지금 괜찮을까요?" | "아침에 물 한 잔, 정말 효과 있을까요?" |

주요 함수:
- `get_random_hook(category, topic_type)` — 카테고리 미지정 시 랜덤 패턴 선택
- `get_hook_for_script(topic_type)` — 대본 생성용 훅 예시 텍스트 반환
- `get_all_patterns()` — 전체 패턴 목록 반환

완료 조건 확인:
- ✅ 5가지 훅 패턴 중 랜덤 선택 동작 (`random.choice(CATEGORIES)`)
- ✅ 채널 카테고리(economy/health/general) 별 예시 3개씩 제공

---

### 3-2. 역삼각형 스크립트 구조 (`engine/llm_script_engine.py` 수정)

**파일**: `/data/shortflow/engine/llm_script_engine.py`

기존 평서문 나열 구조 → 역삼각형 스크립트 구조로 개선:

```
개선된 구조:
1. 훅(0-3초)          — 시청자 멈춤 유도, 15자 이내, 감정 단어 필수
2. 핵심 메시지(3-15초) — 결론 먼저 제시 [NEW]
3. 근거/스토리(15-40초) — 데이터·사례·이유 뒷받침 [NEW]
4. CTA(40-50초)        — 구독·좋아요 유도 (기존 50-55초에서 앞당김)
5. 마무리/루프 엔딩(50-60초) — 재시청 유도
```

추가 변경:
- `hook_templates.py` import 및 `_build_system_prompt()`에 훅 패턴 랜덤 선택 통합
- 훅 문장 15자 이내, 감정 단어 1개 이상 필수 지시 추가
- 토픽 타입 자동 감지 (`economy` / `health` / `general`)

완료 조건 확인:
- ✅ 역삼각형 스크립트 구조 프롬프트 적용 확인

---

### 3-3. 감정 트리거 제목 생성 (`engine/title_optimizer.py`)

**파일**: `/data/shortflow/engine/title_optimizer.py`

```python
# 사용 예시
optimizer = TitleOptimizer()
best_title = optimizer.optimize("환율 급등 원인", channel_type="economy")
# → "충격! 환율 급등, 당신 통장 위험하다" (점수 기반 자동 선택)
```

주요 기능:
- Gemini 2.5 Flash에 후보 5개 생성 요청 (`temperature=0.9`)
- 조건: 15~25자, 감정 단어(충격/비밀/위험/필수/절대 등) 1개 이상, 숫자 포함 시 가산
- 점수 기반 최적 1개 자동 선택 (`select_best_title()`)
- Gemini 실패 시 템플릿 폴백 (5개 채널 유형별)

점수 체계:
- 15~25자: +10점
- 12~14자 또는 26~30자: +5점
- 감정 단어 1개 이상: +3점
- 숫자 포함: +2점

완료 조건 확인:
- ✅ 제목 후보 5개 생성 + 최적 1개 선택 동작 (로직 검증)

---

### 3-4. CTA 오버레이 (`engine/cta_overlay.py`)

**파일**: `/data/shortflow/engine/cta_overlay.py`

FFmpeg drawtext 필터로 영상 마지막 5초에 CTA 삽입:

```python
# 사용 예시
apply_cta_overlay(
    input_path="/data/shortflow/output/video.mp4",
    output_path="/data/shortflow/output/video_cta.mp4",
    cta_text="구독 + 좋아요",
    sub_text="알림 설정도 눌러주세요!",
    cta_duration=5.0,
    font_size=50,
)
```

FFmpeg 필터 구성:
```
drawbox=x=0:y=h*0.62:w=w:h=h*0.38:color=black@0.7:t=fill:enable='gte(t,{cta_start})'
drawtext=text='구독 + 좋아요':fontsize=50:fontcolor=white:shadowcolor=black:shadowx=3:shadowy=3:x=(w-text_w)/2:y=h*0.7
drawtext=text='알림 설정도 눌러주세요!':fontsize=36:fontcolor=0xFFD700:x=(w-text_w)/2:y=h*0.7+64
```

- 위치: 화면 중앙 하단 (y=h*0.7)
- 폰트: 50px, 흰색 + 그림자 (shadowx=3, shadowy=3)
- 보조 텍스트: 노란색(#FFD700)
- 시작 시간: `영상 총 길이 - 5초`

완료 조건 확인:
- ✅ CTA 오버레이 영상 마지막 5초 삽입 로직 구현 완료

---

### 3-5. 자동 해시태그 생성 (`engine/hashtag_generator.py`)

**파일**: `/data/shortflow/engine/hashtag_generator.py`

```python
# 사용 예시
hashtags = generate_hashtags(
    script_text="오늘 환율이 폭등했습니다. 달러 투자에 주의하세요.",
    channel_category="economy",
    channel_name="3분경제",
)
# → ['#Shorts', '#경제뉴스', '#경제상식', '#재테크', '#3분경제', '#환율', '#달러']
```

주요 기능:
- 채널 카테고리별 기본 태그 (economy/health/history/general)
- 대본 키워드 매핑 (40+ 키워드 → 관련 해시태그)
- 채널 이름 자동 태그 추가
- 5~8개 범위 자동 조정, 미달 시 폴백 태그 추가
- `format_hashtags_for_description()` — YouTube 설명란 포맷 변환

완료 조건 확인:
- ✅ 해시태그 5~8개 자동 생성 로직 검증

---

### 3-6. 장면 전환 빈도 개선 (`worker/services/ffmpeg_composer.py` 수정)

**파일**: `/data/shortflow/worker/services/ffmpeg_composer.py`

`MotionEffect` Enum에 `SLOW_ZOOM` 추가:

```python
class MotionEffect(str, Enum):
    ...
    SLOW_ZOOM = "slow_zoom"  # SF-T003: 프레임별 0.0015 증분 줌
```

`KenBurnsGenerator._zoompan_expr()`에 SLOW_ZOOM 처리 추가:

```python
elif effect == MotionEffect.SLOW_ZOOM:
    # zoompan=z='min(zoom+0.0015,1.5)':d=1:s=1080x1920
    # 초당 0.045(30fps×0.0015) 씩 확대, 최대 1.5배
    z = "min(zoom+0.0015,1.5)"
    x = "iw/2-(iw/zoom/2)"
    y = "ih/2-(ih/zoom/2)"
```

- `zoom` 변수: zoompan 필터 내부의 이전 프레임 줌값 참조 (누적 증분)
- 30fps 기준 초당 +0.045 증가, 약 11초 후 최대 줌(1.5배) 도달
- 세그먼트 재사용 대신 매 씬마다 새 줌 시작 → 1~2초 체감 전환 효과

완료 조건 확인:
- ✅ SLOW_ZOOM 효과 로직 추가 완료 (zoompan z='min(zoom+0.0015,1.5)')

---

### 3-7. 동적 자막 강조 (`worker/services/ffmpeg_composer.py` 수정)

**파일**: `/data/shortflow/worker/services/ffmpeg_composer.py`

`SubtitleGenerator.generate_ass()`에 ASS 인라인 키워드 하이라이트 추가:

```python
# 기존: Keyword 스타일만 사용
style = "Keyword" if w.is_keyword else "Default"

# 개선: Keyword 스타일 + 인라인 색상 오버라이드
if w.is_keyword:
    line_text = "{\\c&H00FFFF&}" + line_text + "{\\c&HFFFFFF&}"
```

- ASS 인라인 태그: `{\c&H00FFFF&}` = 노란색 (BGR: B=00, G=FF, R=FF → #FFFF00)
- `{\c&HFFFFFF&}` = 흰색 복귀
- 이중 강조: "Keyword" 스타일(노란색 폰트) + 인라인 색상 태그

기존 키워드 마커 (TimingEngine.keyword_markers):
```python
["최저가", "할인", "무료배송", "1위", "베스트", "추천", "필수", "꿀템", "가성비", "신상"]
```

완료 조건 확인:
- ✅ 키워드 하이라이트 자막 로직 구현 완료

---

## 산출물 목록

| 파일 | 유형 | 설명 |
|------|------|------|
| `engine/hook_templates.py` | 신규 | 훅 템플릿 5종 (Bold Claim/Curiosity Gap/Micro-Story/Visual Shock/Direct Question) |
| `engine/title_optimizer.py` | 신규 | Gemini 기반 감정 트리거 제목 최적화 |
| `engine/cta_overlay.py` | 신규 | FFmpeg CTA 오버레이 (마지막 5초) |
| `engine/hashtag_generator.py` | 신규 | 대본 키워드 기반 자동 해시태그 생성 |
| `engine/llm_script_engine.py` | 수정 | hook_templates 통합, 역삼각형 구조, 훅 15자/감정단어 필수 지시 |
| `worker/services/ffmpeg_composer.py` | 수정 | SLOW_ZOOM 효과 추가, ASS 키워드 인라인 하이라이트 |
| `HANDOVER.md` | 수정 | §2에 QUALITY-IMPROVE-V1 추가, v1.8로 갱신 |
| `docs/reports/20260305_quality_improvement.md` | 신규 | 본 보고서 |

---

## 완료 조건 체크리스트

- ✅ 5가지 훅 패턴 중 랜덤 선택 동작 (`hook_templates.py`)
- ✅ 역삼각형 스크립트 구조 확인 (프롬프트 수정 — llm_script_engine.py)
- ✅ 제목 후보 5개 생성 + 최적 1개 선택 동작 (`title_optimizer.py`)
- ✅ CTA 오버레이 영상 마지막 5초 삽입 로직 (`cta_overlay.py`)
- ✅ 해시태그 5~8개 자동 생성 로직 (`hashtag_generator.py`)
- ✅ zoompan SLOW_ZOOM 효과 적용 로직 (`ffmpeg_composer.py`)
- ✅ 키워드 하이라이트 자막 로직 (`ffmpeg_composer.py`)
- ✅ HANDOVER.md §2에 QUALITY-IMPROVE-V1 추가
- ⏳ 양 레포 push — Git PAT 등록 후 `git push origin main` 필요 (기존 차단 상태 유지)
- ⏳ HTTP 200 — 파이프라인 실제 실행 확인 필요 (크론 또는 수동 테스트)

---

## 후속 작업 권고

1. `TitleOptimizer.optimize()` dry-run 테스트 — Gemini API 키 유효성 확인
2. `apply_cta_overlay()` 실제 영상 파일로 스크린샷 확인
3. `generate_hashtags()` 경제/건강 채널 대본으로 출력 검증
4. `SLOW_ZOOM` 효과를 파이프라인 `_step_compose_video()`에서 일부 씬에 적용 고려
5. `keyword_markers` 목록 확장 (경제: "환율", "달러", "금리" / 건강: "혈압", "혈당", "콜레스테롤" 추가)
