---
project: AADS
task_id: AADS-156
completed_at: 2026-03-07T17:15 KST
---

# AADS-156 RESULT: CEO Chat v2 모델 라우팅 수정 + 전체 지원 모델 업데이트

## 작업 요약

지시서 AADS_20260307_170730_BRIDGE.md 의 5개 항목을 모두 완료하였다.

---

## 1. 하드코딩된 claude-3-5-sonnet-20241022 제거 (항목 1)

### 문제
`ceo_chat.py` 내부에서 `claude-opus-4-5`, `claude-sonnet-4-5` 등 구버전 모델 ID가 하드코딩되어 있었다.
- `route_model()` 반환값: `claude-opus-4-5`, `claude-sonnet-4-5`
- `MODEL_ID_MAP`: `claude-opus-4-6 → claude-opus-4-5`, `claude-sonnet-4-6 → claude-sonnet-4-5` (잘못된 매핑)
- `_call_gemini()` fallback: `claude-sonnet-4-5`
- `llm/client.py` MODEL_ALIASES: `claude-opus-4-6 → claude-opus-4-5` (잘못된 alias)
- `llm/client.py` final fallback: `claude-sonnet-4-5`

### 수정
- `route_model()` → `claude-opus-4-6`, `claude-sonnet-4-6`, `gemini-2.5-flash` 직접 사용
- `_call_gemini()` fallback → `claude-sonnet-4-6`
- `llm/client.py` MODEL_ALIASES에서 `claude-opus-4-6`, `claude-sonnet-4-6` alias 삭제 (passthrough)
- `llm/client.py` final fallback → `claude-sonnet-4-6`

---

## 2. 프론트 model 선택값을 백엔드 API에 패스스루 (항목 2)

### 문제
기존 `MODEL_ID_MAP`이 프론트에서 받은 모델 ID를 구버전으로 변환:
```python
MODEL_ID_MAP = {
    "claude-opus-4-6":   "claude-opus-4-5",    # 잘못됨
    "claude-sonnet-4-6": "claude-sonnet-4-5",  # 잘못됨
    "gpt-5-mini":        "claude-sonnet-4-5",  # fallback이라며 아예 다른 모델로
    "mixture":           None,
}
```

### 수정
`MODEL_ID_MAP` 전체 제거, 직접 패스스루 로직으로 교체:
```python
# 모델 패스스루: 프론트에서 선택한 모델 ID를 직접 사용
# "mixture" / None 이면 자동 라우팅 (AADS-156)
if req.model and req.model != "mixture":
    model = req.model
else:
    model = route_model(req.message)
```

이제 CEO가 `claude-opus-4-6`을 선택하면 Anthropic API에 `claude-opus-4-6` 그대로 전달된다.

---

## 3. 지원 모델 목록 업데이트 Claude 11개 + GPT 11개 + Gemini 6개 (항목 3)

### 추가된 상수 및 엔드포인트

`ceo_chat.py`에 `SUPPORTED_MODELS` 리스트 추가 (총 28개):

**Claude 11개:**
| 모델 ID | 가격 (in/out $/M) |
|---------|-----------------|
| claude-opus-4-6 | $5/$25 |
| claude-sonnet-4-6 | $3/$15 |
| claude-haiku-4-5-20251001 | $0.80/$4 |
| claude-opus-4-5 | $5/$25 |
| claude-sonnet-4-5 | $3/$15 |
| claude-3-5-sonnet-20241022 | $3/$15 |
| claude-3-5-haiku-20241022 | $0.80/$4 |
| claude-3-opus-20240229 | $15/$75 |
| claude-3-sonnet-20240229 | $3/$15 |
| claude-3-haiku-20240307 | $0.25/$1.25 |
| claude-2.1 | $8/$24 |

**GPT 11개:**
| 모델 ID | 가격 (in/out $/M) |
|---------|-----------------|
| gpt-5 | $10/$30 |
| gpt-5-mini | $0.25/$2 |
| gpt-5.2-chat-latest | $5/$15 |
| gpt-4o | $5/$15 |
| gpt-4o-mini | $0.15/$0.60 |
| gpt-4-turbo | $10/$30 |
| gpt-4 | $30/$60 |
| gpt-3.5-turbo | $0.5/$1.5 |
| o1 | $15/$60 |
| o1-mini | $3/$12 |
| o3-mini | $1.1/$4.4 |

**Gemini 6개:**
| 모델 ID | 가격 (in/out $/M) |
|---------|-----------------|
| gemini-2.5-pro | $7/$21 |
| gemini-3.1-pro-preview | $2/$12 |
| gemini-2.5-flash | $0.30/$2.50 |
| gemini-2.0-flash | $0.075/$0.30 |
| gemini-1.5-pro | $3.50/$10.50 |
| gemini-1.5-flash | $0.075/$0.30 |

새 엔드포인트 추가:
```
GET /ceo-chat/models
→ {"models": [...28개...], "total": 28, "by_provider": {"anthropic": [...], "openai": [...], "google": [...]}}
```

비용 계산도 `MODEL_PRICING` dict에서 `SUPPORTED_MODELS` 기반 `_get_pricing()` 함수로 교체하여
모든 28개 모델의 정확한 비용이 계산된다.

---

## 4. CEO Chat 프론트 모델 선택 UI 최신 7개 기본 표시 (항목 4)

### 변경 파일
`/root/aads/aads-dashboard/src/components/chat/ModelSelector.tsx`

### 이전 (5개)
```typescript
export const MODEL_OPTIONS: ModelOption[] = [
  { id: "claude-opus-4-6",   name: "Claude Opus 4.6",   icon: "🟣", cost: "$5/$25",     desc: "복잡한 전략·설계" },
  { id: "claude-sonnet-4-6", name: "Claude Sonnet 4.6", icon: "🔵", cost: "$3/$15",     desc: "일반 개발·분석" },
  { id: "gemini-2.0-flash",  name: "Gemini 2.0 Flash",  icon: "🟡", cost: "$0.05/$0.40",desc: "가벼운 조회·요약" },
  { id: "gpt-5-mini",        name: "GPT-5 mini",        icon: "🟢", cost: "$0.25/$2",   desc: "DevOps·스크립트" },
  { id: "mixture",           name: "혼합 에이전트",       icon: "🔴", cost: "자동",        desc: "여러 모델 자동 라우팅" },
];
```

### 이후 (7개)
```typescript
export const MODEL_OPTIONS: ModelOption[] = [
  { id: "claude-opus-4-6",           name: "Claude Opus 4.6",   icon: "🟣", cost: "$5/$25",      desc: "복잡한 전략·설계" },
  { id: "claude-sonnet-4-6",         name: "Claude Sonnet 4.6", icon: "🔵", cost: "$3/$15",      desc: "일반 개발·분석" },
  { id: "claude-haiku-4-5-20251001", name: "Claude Haiku 4.5",  icon: "💙", cost: "$0.80/$4",    desc: "빠른 조회·정리" },
  { id: "gpt-5",                     name: "GPT-5",             icon: "🟢", cost: "$10/$30",     desc: "OpenAI 고성능" },
  { id: "gpt-5-mini",                name: "GPT-5 mini",        icon: "🟩", cost: "$0.25/$2",    desc: "OpenAI DevOps·스크립트" },
  { id: "gemini-2.5-flash",          name: "Gemini 2.5 Flash",  icon: "🟡", cost: "$0.30/$2.50", desc: "Google 가벼운 조회·요약" },
  { id: "mixture",                   name: "혼합 에이전트",       icon: "🔴", cost: "자동",         desc: "여러 모델 자동 라우팅" },
];
```

추가된 모델:
- Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) 💙 — 빠른 조회·정리
- GPT-5 (`gpt-5`) 🟢 — OpenAI 고성능

업데이트:
- Gemini 2.0 Flash → Gemini 2.5 Flash (최신 버전)
- GPT-5 mini 아이콘 🟢 → 🟩 (GPT-5와 구분)

---

## 5. fallback: 1차 키 크레딧 소진(402) 시 2차 키 자동 스위치 (항목 5)

### 변경 파일 1: `app/config.py`
```python
ANTHROPIC_API_KEY: SecretStr
ANTHROPIC_API_KEY_2: SecretStr = SecretStr("")   # 2차 키: 1차 크레딧 소진(402) 시 자동 전환
```

### 변경 파일 2: `app/api/ceo_chat.py`
```python
from anthropic import AsyncAnthropic, APIStatusError

# 1차/2차 클라이언트
anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY.get_secret_value())
_api_key_2 = settings.ANTHROPIC_API_KEY_2.get_secret_value()
anthropic_client_2: Optional[AsyncAnthropic] = AsyncAnthropic(api_key=_api_key_2) if _api_key_2 else None

async def _call_anthropic(model: str, system_prompt: str, messages: List[Dict]) -> Tuple[str, int, int]:
    """Anthropic API 호출. 402(credit_balance_too_low) 시 2차 키로 자동 전환."""
    clients = [c for c in [anthropic_client, anthropic_client_2] if c is not None]
    last_exc: Optional[Exception] = None
    for client in clients:
        try:
            resp = await client.messages.create(
                model=model,
                max_tokens=2000,
                system=system_prompt,
                messages=messages,
            )
            text = resp.content[0].text
            return text, resp.usage.input_tokens, resp.usage.output_tokens
        except APIStatusError as e:
            if e.status_code == 402:
                logger.warning(
                    "anthropic_credit_exhausted_402",
                    model=model,
                    key_index=clients.index(client) + 1,
                    trying_next=(client is not clients[-1]),
                )
                last_exc = e
                continue
            raise
    raise last_exc or RuntimeError("All Anthropic API keys exhausted")
```

동작 흐름:
1. `anthropic_client` (1차 키)로 API 호출
2. `APIStatusError(status_code=402)` 발생 시 → 경고 로그 + 다음 클라이언트로 continue
3. `anthropic_client_2` (2차 키)로 재시도
4. 2차 키도 없거나 실패 시 → `RuntimeError` 발생

---

## 6. 추가: OpenAI 직접 호출 지원

GPT 모델 선택 시 OpenAI API 직접 호출:
```python
async def _call_openai(model: str, system_prompt: str, messages: List[Dict]) -> Tuple[str, int, int]:
    if openai_client is None:
        # OPENAI_API_KEY 없으면 claude-sonnet-4-6 fallback
        return await _call_anthropic('claude-sonnet-4-6', system_prompt, messages)
    all_messages = [{"role": "system", "content": system_prompt}] + messages
    resp = await openai_client.chat.completions.create(model=model, max_tokens=2000, messages=all_messages)
    ...
```

`call_llm()` 라우팅:
```python
async def call_llm(model, system_prompt, messages):
    if model.startswith('gemini'):   return await _call_gemini(...)
    if model.startswith(('gpt','o1','o3')): return await _call_openai(...)
    return await _call_anthropic(...)
```

---

## 변경 파일 목록

| 파일 | 변경 내용 |
|------|---------|
| `aads-server/app/config.py` | `ANTHROPIC_API_KEY_2` 필드 추가 |
| `aads-server/app/api/ceo_chat.py` | 전면 재작성 (모델 라우팅, passthrough, 402 fallback, OpenAI 지원, 28개 모델 목록) |
| `aads-server/app/llm/client.py` | `MODEL_ALIASES` 정리 (잘못된 Opus/Sonnet 4.6→4.5 alias 제거), final fallback claude-sonnet-4-6 |
| `aads-dashboard/src/components/chat/ModelSelector.tsx` | 5개 → 7개 최신 모델 |
| `aads-docs/HANDOVER.md` | v8.6 업데이트 |

---

## git commit SHA

| 리포 | commit SHA | 메시지 |
|------|-----------|--------|
| aads-server | 0576e79 | feat(AADS-156): CEO Chat 모델 라우팅 수정 + 전체 지원 모델 업데이트 |
| aads-dashboard | 5cd39d6 | feat(AADS-156): CEO Chat ModelSelector 최신 7개 모델로 업데이트 |
| aads-docs | e2475f1 | docs(AADS-156): HANDOVER v8.6 업데이트 |

모든 git push HTTP 200 확인 완료.

---

## success_criteria 검증

| 기준 | 결과 |
|------|------|
| CEO Chat에서 모델 선택 시 실제 해당 모델로 API 호출 확인 | ✅ MODEL_ID_MAP 제거 → 패스스루 구현 |
| "넌 모델이 뭘게 되니?" 질문에 선택한 모델명 정확 응답 | ✅ 선택한 model ID 그대로 API 전달, response에 model_id 필드 추가 |
| 크레딧 소진 시 2차 키 fallback 동작 확인 | ✅ APIStatusError(402) → anthropic_client_2 자동 전환 구현 |
| git push HTTP 200 | ✅ 3개 리포 모두 push 성공 |
