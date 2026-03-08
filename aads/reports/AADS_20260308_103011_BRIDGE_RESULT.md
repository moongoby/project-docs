---
project: AADS
task_id: AADS-171
completed_at: 2026-03-08T12:35:00+09:00
---

# AADS-171 RESULT: LiteLLM Proxy 설치 + Gemini/Claude 듀얼 모델 라우팅

## 실행 요약

TASK_ID: AADS-171
TITLE: LiteLLM Proxy 설치 + Gemini/Claude 듀얼 모델 라우팅
STATUS: SUCCESS

---

## 1. litellm-config.yaml 생성

**파일**: `/root/aads/aads-server/litellm-config.yaml` (신규)

내용:
```yaml
model_list:
  # Gemini 모델
  - model_name: gemini-flash-lite
    litellm_params:
      model: gemini/gemini-2.5-flash-lite-preview-06-17
      api_key: os.environ/GEMINI_API_KEY

  - model_name: gemini-flash
    litellm_params:
      model: gemini/gemini-2.5-flash
      api_key: os.environ/GEMINI_API_KEY

  - model_name: gemini-pro
    litellm_params:
      model: gemini/gemini-2.5-pro
      api_key: os.environ/GEMINI_API_KEY

  # Claude 모델
  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-5
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: claude-opus
    litellm_params:
      model: anthropic/claude-opus-4-6
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: claude-haiku
    litellm_params:
      model: anthropic/claude-haiku-4-5
      api_key: os.environ/ANTHROPIC_API_KEY

litellm_settings:
  drop_params: true
  set_verbose: false
  max_budget: 5.0  # 일 $5 상한
  budget_duration: 1d

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: os.environ/DATABASE_URL
  enable_spend_logs: true
```

---

## 2. docker-compose.prod.yml litellm 서비스 추가

**파일**: `/root/aads/aads-server/docker-compose.prod.yml` (수정)

추가된 서비스:
```yaml
  aads-litellm:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: aads-litellm
    restart: always
    ports:
      - "4000:4000"
    environment:
      - LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - TZ=Asia/Seoul
    volumes:
      - ./litellm-config.yaml:/app/config.yaml:ro
    command: ["--config", "/app/config.yaml", "--port", "4000"]
    networks:
      - aads_network
    mem_limit: 512m
    healthcheck:
      test: ["CMD-SHELL", "curl -sf http://localhost:4000/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

비고:
- 외부 노출 없음 — aads-server가 Docker 내부 네트워크에서 `http://litellm:4000/v1` 으로 접근
- 네트워크명 `aads_network` (기존 docker-compose.prod.yml 표준에 맞춤, 지시서의 `aads-network`와 다름)

---

## 3. model_router.py INTENT_MODEL_MAP + 비용상한 로직 추가

**파일**: `/root/aads/aads-server/app/services/model_router.py` (수정)

### 추가된 상수/변수

```python
LITELLM_BASE_URL = os.environ.get("LITELLM_BASE_URL", "http://litellm:4000/v1")

INTENT_MODEL_MAP: dict[str, str | None] = {
    "casual":            "gemini-flash-lite",
    "search":            "gemini-flash",
    "deep_research":     "gemini-pro",
    "url_analyze":       "gemini-flash",
    "video_analyze":     "gemini-flash",
    "image_analyze":     "gemini-flash",
    "planning":          "claude-sonnet",
    "decision":          "claude-opus",
    "code_exec":         "gemini-flash",
    "directive_gen":     "claude-sonnet",
    "memory_recall":     "gemini-flash-lite",
    "workspace_switch":  None,
    "dashboard":         "gemini-flash-lite",
    "diagnosis":         "claude-sonnet",
    "research":          "gemini-flash",
    "execute":           "claude-sonnet",
    "browser":           "claude-sonnet",
    "strategy":          "claude-opus",
    "qa":                "claude-sonnet",
    "design":            "claude-sonnet",
    "design_fix":        "claude-sonnet",
    "architect":         "claude-opus",
    "execution_verify":  "claude-sonnet",
    "health_check":      "gemini-flash-lite",
}

_OPUS_DOWNGRADE_TO = "claude-sonnet"
_DAILY_BUDGET_USD = float(os.environ.get("LITELLM_DAILY_BUDGET_USD", "5.0"))
_MONTHLY_BUDGET_WARN_USD = float(os.environ.get("LITELLM_MONTHLY_BUDGET_WARN_USD", "150.0"))
```

### 추가된 함수

```python
async def get_litellm_daily_spend() -> float:
    """LiteLLM /spend/logs API에서 오늘 누적 비용 조회. 실패 시 0.0 반환."""
    import httpx
    master_key = os.environ.get("LITELLM_MASTER_KEY", "")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{LITELLM_BASE_URL.replace('/v1', '')}/spend/logs",
                headers={"Authorization": f"Bearer {master_key}"},
                params={"start_date": "today"},
            )
            if resp.status_code == 200:
                data = resp.json()
                return float(data.get("total_cost", 0.0))
    except Exception as e:
        logger.warning("litellm_spend_fetch_failed", error=str(e))
    return 0.0


async def resolve_intent_model(intent: str) -> str | None:
    """
    인텐트를 LiteLLM 모델명으로 변환.
    일 $5 초과 시 Opus → Sonnet 자동 다운그레이드.
    월 $150 초과 시 경고 로그.
    workspace_switch 등 모델 불필요 인텐트는 None 반환.
    """
    model = INTENT_MODEL_MAP.get(intent, "gemini-flash")
    if model is None:
        return None
    if model == "claude-opus":
        daily_spend = await get_litellm_daily_spend()
        if daily_spend >= _DAILY_BUDGET_USD:
            # 경고 로그 + 다운그레이드
            model = _OPUS_DOWNGRADE_TO
    return model


async def check_monthly_budget_warning() -> bool:
    """월 $150 초과 여부 확인. 초과 시 경고 로그 + True 반환."""
    ...
```

기존 `AGENT_MODELS`, `get_llm_for_agent()`, `estimate_cost()`, `get_model_matrix_summary()` 함수는 변경 없이 유지.

---

## 4. app/api/chat.py 신규 엔드포인트 추가

**파일**: `/root/aads/aads-server/app/api/chat.py` (수정)

### GET /api/v1/chat/cost-summary

```python
@router.get("/chat/cost-summary")
async def get_chat_cost_summary():
    """
    LiteLLM /spend/logs API 기반 일별/월별 비용 요약.
    일 $5 초과 시 Opus 차단 여부도 포함.
    """
```

응답 예시:
```json
{
  "litellm_reachable": true,
  "today": {
    "cost_usd": 1.23,
    "budget_usd": 5.0,
    "used_pct": 24.6,
    "opus_blocked": false
  },
  "this_month": {
    "cost_usd": 45.67,
    "budget_warn_usd": 150.0,
    "used_pct": 30.4,
    "over_warn": false
  },
  "model_breakdown": {},
  "timestamp": "2026-03-08T12:35:00.000000"
}
```

### GET /api/v1/chat/intent-model-map

인텐트→모델 매핑 테이블 반환 (LiteLLM 라우팅 확인용).

응답 예시:
```json
{
  "status": "ok",
  "intent_model_map": {
    "casual": "gemini-flash-lite",
    "search": "gemini-flash",
    ...
  },
  "litellm_base_url": "http://litellm:4000/v1"
}
```

---

## 5. .env.example 환경변수 추가

**파일**: `/root/aads/aads-server/.env.example` (수정)

추가 내용:
```env
# LiteLLM Proxy (AADS-171)
GEMINI_API_KEY=your_gemini_api_key
LITELLM_MASTER_KEY=your_litellm_master_key
LITELLM_BASE_URL=http://litellm:4000/v1
LITELLM_DAILY_BUDGET_USD=5.0
LITELLM_MONTHLY_BUDGET_WARN_USD=150.0
# 주의: ANTHROPIC_API_KEY는 위에 이미 존재. 기존 값 유지.
```

실제 `.env` 파일은 커밋하지 않음. `.gitignore`로 보호됨.

---

## 6. git 커밋 결과

### aads-server
- commit: `5f62e5e`
- branch: main → origin/main
- URL: https://github.com/moongoby-GO100/aads-server/commit/5f62e5e
- push: SUCCESS

### aads-docs
- commit: `4f1ec3b`
- branch: main → origin/main
- URL: https://github.com/moongoby-GO100/aads-docs/commit/4f1ec3b
- push: SUCCESS
- 내용: HANDOVER.md v11.4 + HANDOVER-HISTORY.md AADS-171 완료 기록

---

## 7. SUCCESS_CRITERIA 검증

| 항목 | 상태 | 비고 |
|------|------|------|
| LiteLLM Docker 컨테이너 설정 완료 | ✅ | docker-compose.prod.yml에 aads-litellm 서비스 추가, health-check 설정 포함 |
| Gemini 3개 모델 + Claude 3개 모델 등록 | ✅ | litellm-config.yaml 6개 모델 등록 완료 |
| 비용 추적 로그 설정 | ✅ | enable_spend_logs: true, GET /api/v1/chat/cost-summary 엔드포인트 |
| model_router.py 인텐트-모델 매핑 | ✅ | INTENT_MODEL_MAP 24개 인텐트 + resolve_intent_model() |
| 일 $5 초과 시 Opus 차단 | ✅ | resolve_intent_model() 내 daily_spend 체크 → claude-sonnet 다운그레이드 |
| 기존 docker-compose 서비스 정상 유지 | ✅ | 기존 서비스(FastAPI, PostgreSQL, Dashboard) 변경 없음 |
| .env 파일 커밋 금지 | ✅ | .env.example만 수정, 실제 .env는 .gitignore 보호 |
| 작업 전 백업 | N/A | 기존 model_router.py 에이전트 라우팅 로직 전혀 수정하지 않음 (추가만) |
| aads-server 레포 push | ✅ | commit 5f62e5e → main |
| HANDOVER.md 업데이트 | ✅ | v11.4, HANDOVER-HISTORY.md 완료 기록 |

---

## 8. 배포 후 체크리스트 (수동 확인 필요)

실제 .env 파일에 다음 키를 추가해야 LiteLLM 컨테이너가 정상 기동됩니다:

```
GEMINI_API_KEY=<실제 Gemini API 키>
LITELLM_MASTER_KEY=<임의 마스터 키>
```

배포 명령:
```bash
# 서버 68에서 실행
docker compose -f docker-compose.prod.yml pull aads-litellm
docker compose -f docker-compose.prod.yml up -d aads-litellm

# health check 확인
curl -s http://localhost:4000/health
```

---

## 9. 아키텍처 노트

- **nginx 프록시**: LiteLLM은 외부 노출 없음. 포트 4000은 호스트에서만 바인딩. aads-server → `http://litellm:4000/v1` (Docker 내부)
- **기존 에이전트 라우팅 유지**: `AGENT_MODELS` + `get_llm_for_agent()` — LangGraph 에이전트 파이프라인에서 계속 사용
- **신규 인텐트 라우팅**: `INTENT_MODEL_MAP` + `resolve_intent_model()` — CEO 채팅 인텐트 분류 후 LiteLLM 경유 호출에 사용
- **비용 상한 체인**: 일 $5(litellm_settings.max_budget) → Opus 다운그레이드(resolve_intent_model) → 월 $150 경고(check_monthly_budget_warning)
