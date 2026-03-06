# SF-T014: AI Content Planner v1 — 구현 보고서

작성일: 2026-03-06
작업자: Claude Sonnet 4.6 (claudebot)
태스크: SF-T014

---

## 1. 개요

Gemini 2.5 Flash 기반으로 채널별 트렌드 주제를 자동 기획하는 AI Content Planner 엔진을 구현했다.
D-001(복합분석) 원칙에 따라 트렌드성·중복 회피·채널 적합성을 종합해 상위 주제를 선별한다.

---

## 2. 구현 파일

| 파일 | 역할 |
|------|------|
| `engine/content_planner.py` | ContentPlanner 클래스 본체 |
| `scripts/plan_content.py` | CLI 진입점 |
| `data/topic_history_economy.json` | economy 채널 주제 이력 |
| `data/topic_history_health.json` | health 채널 주제 이력 |
| `data/topic_history_history.json` | history 채널 주제 이력 |
| `data/plans/` | 일별 기획 결과 JSON 저장 디렉토리 |

---

## 3. ContentPlanner 클래스 상세

### `__init__(channel_id)`
- `config/hook_presets.json` (SF-T009) 로드 → `hook_preset`, `bg_keyword_pool`
- `data/topic_history_{channel}.json` 로드 → `topic_history`
- 채널-카테고리 매핑: `economy→경제/금융`, `health→건강/영양`, `history→역사`

### `_get_trending_topics(count=5)`
- Gemini 2.5 Flash (`gemini-2.5-flash`) 호출
- `.env`에서 `GEMINI_API_KEY` 로드 (환경변수 우선, 없으면 `.env` 파일 직접 파싱)
- JSON 파싱 실패 시 재시도 1회, 그래도 실패 시 빈 리스트 반환
- `gemini-2.0-flash` 사용 금지 조건 준수

### `_score_topics(topics)` — 100점 만점
| 기준 | 조건 | 점수 |
|------|------|------|
| 트렌드성 | estimated_interest=high | +40 |
| 트렌드성 | estimated_interest=medium | +25 |
| 트렌드성 | estimated_interest=low | +10 |
| 중복도 | topic_history 유사 단어 포함 | -20 |
| 채널 적합성 | bg_keyword_pool 매칭 | +20 |
| Pexels 키워드 | 영문 2단어 이상 | +10 |
| Pexels 키워드 | 1단어 | +5 |

### `plan_today(count=3)`
- 후보 5개 생성 → 점수 산정 → 상위 count건 선택
- hook_presets에서 hook 예시 매칭
- topic_history append + 저장
- `data/plans/plan_{channel}_{YYYYMMDD}.json` 저장

### `dry_run(count=3)`
- Gemini 호출 없이 채널별 mock 주제로 로직 전체 테스트
- economy: 환율·ETF·부동산·금리·세금 관련 5개 mock
- health: 공복·마그네슘·다이어트·수면·면역 관련 5개 mock
- `data/plans/plan_{channel}_{YYYYMMDD}_dryrun.json` 저장

---

## 4. CLI 사용법

```bash
# 단일 채널 실행
python3 scripts/plan_content.py --channel economy --count 3

# 전체 채널 (economy + health)
python3 scripts/plan_content.py --all

# Gemini 호출 없이 dry-run
python3 scripts/plan_content.py --channel economy --dry-run
python3 scripts/plan_content.py --all --dry-run
```

---

## 5. dry-run 테스트 결과

### economy 채널 (3분경제)
```
[DRY-RUN] 채널: 3분경제  날짜: 2026-03-06
[1] 환율 급등 대처법          score=70  high
[2] ETF 초보 투자 가이드      score=70  high
[3] 금리 인하 수혜 주식        score=70  high
총 3개 주제 기획 완료 ✓
```

### health 채널 (건강한입)
```
[DRY-RUN] 채널: 건강한입  날짜: 2026-03-06
[1] 아침 공복에 먹으면 안 되는 음식  score=70  high
[2] 마그네슘 결핍 증상 5가지          score=70  high
[3] 다이어트 중 먹어도 되는 야식      score=55  medium
총 3개 주제 기획 완료 ✓
```

**결론**: 점수 산정 로직, hook 매칭, plans/ 파일 저장 모두 정상 동작.

---

## 6. git 커밋

```
commit b9d1510
[SF] SF-T014: AI Content Planner v1 — Gemini 트렌드 기반 주제 기획 + topic_history
7 files changed, 446 insertions(+)
```

---

## 7. 의존성

- `google-generativeai` (venv 설치됨)
- `config/hook_presets.json` (SF-T009 산출물)
- `.env` → `GEMINI_API_KEY`

---

## 8. 다음 단계

- `plan_today()` 실제 Gemini 호출 테스트 (GEMINI_API_KEY 확인 후)
- 크론에 `plan_content.py --all` 등록 (매일 오전 기획 자동화)
- history 채널 mock 데이터 추가
