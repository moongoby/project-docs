# 인수인계: Wave 3 Main (W3-B, W3-C)

**작성일**: 2026-02-26  
**범위**: data_queries 완전 분리(W3-B), Gemini Function Calling 실험(W3-C)

---

## 1. W3-B: data_queries 완전 분리

**티켓**: CUR-GO100-DATA-QUERIES-MODULARIZE-001

### 완료 내용

- **ai_router.py** 내 raw SQL 3건 제거 → **data_queries.py** async 함수로 이전.
- 추가된 함수:
  - `get_latest_card_id_for_user(user_id, db)` — 최적화 시 card_id 미지정 시 사용
  - `get_backtest_result_detail(run_id, db)` — `/evaluate`에서 result_detail 조회
  - `get_strategy_card_for_optimize(card_id, user_id, db)` — `/optimize`에서 전략 카드 조회
- **완료 조건**: ai_router.py에 `db.execute`/`text(` 0건. `systemctl restart go100` 후 서비스 정상 기동 확인.

### 보고서

- `/root/project-docs/go100/reports/CUR-GO100-DATA-QUERIES-MODULARIZE-001-20260226.md`

### 인수인가 확인

- 15건 curl 테스트는 유효 Bearer 토큰으로 실행 시 PASS 기준. (보고서 내 테스트 시나리오 목록 참고)

---

## 2. W3-C: Gemini Function Calling 실험

**티켓**: CUR-GO100-FUNCTION-CALLING-EXPERIMENT-001

### 완료 내용

- **신규 파일**: `backend/app/services/go100/ai/function_calling.py`
  - Tool 5개: search_stock, get_stock_price, get_stock_fundamentals, get_investor_flow, get_top_stocks
  - 각 툴은 **data_queries** 동일 함수와 연결.
  - `run_stock_info_with_fc(message, db)`: FC 루프 후 최종 응답 텍스트 및 메트릭 반환.
- **환경변수**: `GO100_FC_EXPERIMENT=true` → stock_info 시 FC 방식, `false` 또는 미설정 → 기존 `_handle_stock_info`.
- **ai_router.py**: stock_info 분기에서 `is_fc_experiment_enabled()` 일 때 `run_stock_info_with_fc` 호출.

### 보고서

- `/root/project-docs/go100/reports/CUR-GO100-FUNCTION-CALLING-EXPERIMENT-001-20260226.md`
- 비교표(응답시간/정확도/비용/자연스러움/할루시네이션) 포함. 운영 측정 권장.

### 인수인가 확인

- FC 사용 시 `GOOGLE_AI_API_KEY`(또는 `GEMINI_API_KEY`) 필요.
- `google-genai` 패키지 필요 (`pip install google-genai`).

---

## 3. 변경 파일 요약

| 구분 | 파일 |
|------|------|
| W3-B | `backend/app/services/go100/ai/data_queries.py` (함수 3개 추가) |
| W3-B | `backend/app/routers/go100/ai_router.py` (raw SQL 제거, data_queries 호출로 교체) |
| W3-C | `backend/app/services/go100/ai/function_calling.py` (신규) |
| W3-C | `backend/app/routers/go100/ai_router.py` (stock_info FC 분기 및 import 추가) |

---

## 4. GitHub 푸시

다음 명령으로 보고서·인수인계 문서 푸시:

```bash
cd /root/project-docs
git add go100/reports/CUR-GO100-DATA-QUERIES-MODULARIZE-001-*.md \
        go100/reports/CUR-GO100-FUNCTION-CALLING-EXPERIMENT-001-*.md \
        go100/HANDOVER-*-WAVE3-MAIN.md
git commit -m "docs(go100): Wave 3 Main W3-B + W3-C 보고서

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
git push origin master
```

---

*Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>*
