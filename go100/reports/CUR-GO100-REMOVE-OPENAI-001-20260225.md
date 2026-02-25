# CUR-GO100-REMOVE-OPENAI-001 보고서

**작성일**: 2026-02-25 14:35 KST
**우선순위**: P1
**상태**: **완료**
**BATCH-002 WAVE 1-B 검수**: 2026-02-25 15:45 KST — llm_client.py 에러 메시지·cost_tracker PROVIDER_TO_VENDOR에서 OpenAI 제거 반영 (커밋 252f9207).

---

## 1. 목표

OpenAI 의존성 완전 제거. AsyncOpenAI → LLMGateway, FAILOVER_CHAINS에서 OpenAI 제거, OPENAI_API_KEY 없이 정상 동작.

## 2. 변경 내역

### 2.1 Core LLM Layer

| 파일 | 변경 |
|------|------|
| `backend/app/core/llm_models.py` | `Vendor.OPENAI` enum 제거 |
| `backend/app/core/llm_gateway.py` | OpenAIClient import 제거, FAILOVER_CHAINS c2sc를 `("anthropic", "claude-haiku-4-5")`로 변경, openai_key 초기화 삭제, CircuitBreaker 목록에서 openai 제거 |
| `backend/app/core/llm_clients/__init__.py` | OpenAIClient import/export 제거 |
| `backend/app/core/llm_clients/openai_client.py` | **파일 삭제** |
| `backend/app/core/llm_cost_tracker.py` | `("openai", "gpt-4.1-mini")` 가격 테이블 제거 |

### 2.2 Services LLM Layer

| 파일 | 변경 |
|------|------|
| `backend/app/services/llm/providers.py` | `OpenAIProvider` 클래스 전체 삭제 (118줄) |
| `backend/app/services/llm/gateway.py` | OpenAIProvider import 제거, c2sc 라우팅을 `anthropic/claude-sonnet-4-6`으로 변경, `_get_provider()`에서 openai 분기 제거 |
| `backend/app/services/llm/cost_tracker.py` | `gpt-4.1-mini` 가격 정보 제거 |

### 2.3 Package Dependencies

| 파일 | 변경 |
|------|------|
| `backend/requirements.txt` | `openai>=1.50.0` 제거 (주석 처리) |

## 3. FAILOVER_CHAINS 변경

### Before
```python
"c2sc": [("anthropic", "claude-sonnet-4-6"), ("openai", "gpt-4.1-mini")],
```

### After
```python
"c2sc": [("anthropic", "claude-sonnet-4-6"), ("anthropic", "claude-haiku-4-5")],
```

## 4. GO100 코드 영향

GO100 서비스 코드는 **변경 없음**. 이미 LLMGateway를 사용 중:

| 파일 | 사용 방식 | 변경 필요 |
|------|-----------|-----------|
| `go100/ai/llm_client.py` | `LLMGateway.send()` with FREE_CHAT/DESIGN_CHAT | 없음 |
| `go100/optimizer/backtest_optimizer.py` | `LLMGateway.send()` with DESIGN_CHAT | 없음 |

## 5. 검증

- go100 서비스 재시작 성공 (OpenAI import 없이)
- Goal 1턴 (Gemini Flash free_chat) 정상 동작
- DESIGN_CHAT 호출 시 Anthropic로만 시도 (OpenAI 폴백 없음)
- CircuitBreaker에서 openai 제거되어 불필요한 메모리 사용 방지

## 6. LLM 아키텍처 v2.0

```
┌─────────────────────────────────────────────┐
│              LLM Gateway                     │
├──────────────┬──────────────────────────────┤
│ free_chat    │ Gemini Flash                 │
│ design_chat  │ Claude Sonnet 4.6 → 4.5     │
│ c2sc         │ Claude Sonnet 4.6 → Haiku   │
│ strategy_rev │ Claude Opus 4.6 → Sonnet    │
│ cs           │ Gemini Flash → Haiku        │
├──────────────┼──────────────────────────────┤
│ Vendors      │ Google, Anthropic            │
│ OpenAI       │ ❌ 완전 제거                  │
└──────────────┴──────────────────────────────┘
```

## 보고 요약

- **제거 범위**: Core 5개 파일 + Services 3개 파일 + requirements.txt
- **삭제 코드**: OpenAIClient (123줄), OpenAIProvider (118줄), 총 ~250줄 제거
- **대체**: c2sc 폴백을 `claude-haiku-4-5`로 변경 (비용 효율적)
- **GO100 영향**: 없음 (이미 LLMGateway 사용)
- **검증**: 서비스 재시작 및 API 호출 정상
