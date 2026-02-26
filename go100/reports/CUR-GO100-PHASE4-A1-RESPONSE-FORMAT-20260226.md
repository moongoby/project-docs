# CUR-GO100-PHASE4-A1-RESPONSE-FORMAT-20260226

- **티켓**: Phase 4 A-1 응답 포매팅 표준화
- **작성일**: 2026-02-26
- **목표**: 백억이 모든 인텐트 응답에 3파트 구조(헤더+본문+푸터) 일관 적용

## 1. 완료 사항

### 1-1. 신규 모듈

- **`backend/app/services/go100/ai/response_formatter.py`**
  - `format_timestamp()`: KST 기준시점 문자열 `YYYY-MM-DD(요일) HH:MM 기준`
  - `format_header(intent, **kwargs)`: 인텐트별 아이콘+제목+기준시점 (Part A)
  - `format_footer(intent)`: 인텐트별 다음 액션 제안 (Part C)
  - `format_response(intent, body, **header_kwargs)`: Part A + 본문 + Part C 조합
  - `INTENT_HEADERS` / `INTENT_FOOTERS`: 15개 인텐트 매핑

### 1-2. ai_router.py 적용

| 인텐트 | 적용 내용 |
|--------|-----------|
| stock_info | 개별 종목: 본문만 `_format_stock_report` → `format_response("stock_info", body, stock_name=, stock_code=)`. 상위 종목/폴백: `stock_name`/`stock_code=""` 로 헤더 생성 |
| market_briefing | 본문만 구성 후 `format_response("market_briefing", body)` |
| portfolio_status | 본문만 구성 후 `format_response("portfolio_status", body)` (빈 카드/목표 케이스 포함) |
| stock_screening | `format_response("stock_screening", body)` (기존 경고 문구 포함) |
| sector_analysis | 본문만 구성 후 `format_response("sector_analysis", body)` |
| trade_history | 본문만 구성 후 `format_response("trade_history", body)` |
| backtest_status | 카드 지정/목록/없음 모두 `format_response("backtest_status", body)` |
| risk_check | 본문만 구성 후 `format_response("risk_check", body)` |
| strategy_explain | 본문만 구성 후 `format_response("strategy_explain", body)` |
| compare_strategies | 본문만 구성 후 `format_response("compare_strategies", body)` |
| help | `run_help_flow()` 결과의 `reply_to_user`를 `format_response("help", ...)` 로 래핑 후 반환 |
| goal_setup | 기존 플로우 유지 (선택지가 다음 액션이므로 푸터 미적용) |
| strategy | 비동기 완료 시 `sanitize_reply()` 후 `format_footer("strategy")` append |
| optimize_existing | 비동기 완료 시 `sanitize_reply()` 후 `format_footer("optimize_existing")` append |

### 1-3. llm_router.py C2SC 인터셉터

- `_try_data_backed_response()`는 go100 핸들러 결과의 `reply_to_user`를 그대로 반환.
- 핸들러가 이미 `format_response()`로 포맷된 문자열을 반환하므로 **추가 수정 없이** 자유대화 스트리밍 경로에서도 동일 포맷 적용됨.

### 1-4. 백업

- `/root/backup/go100-routers-phase4-a1-YYYYMMDD-HHMMSS/`
- `/root/backup/go100-ai-services-phase4-a1-YYYYMMDD-HHMMSS/`

## 2. 응답 구조 표준 (검증 포인트)

모든 응답에서 확인할 것:

1. **헤더**: `{아이콘} **{제목}**` + `_{YYYY-MM-DD(요일) HH:MM 기준}_`
2. **본문**: 기존 데이터 섹션 그대로
3. **푸터**: `---` 구분선 + `💡 다음 액션 제안`

## 3. 검증 방법

```bash
# 서비스 재시작
systemctl restart go100

# 예시 (TOKEN은 실제 Bearer 토큰으로 교체)
curl -s -X POST https://go100.newtalk.kr/api/go100/ai/chat \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message":"삼전 얼마야"}' | python3 -m json.tool

curl -s -X POST https://go100.newtalk.kr/api/go100/ai/chat \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message":"오늘 장 어때"}' | python3 -m json.tool

curl -s -X POST https://go100.newtalk.kr/api/go100/ai/chat \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message":"내 포트폴리오"}' | python3 -m json.tool

curl -s -X POST https://go100.newtalk.kr/api/go100/ai/chat \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message":"반도체 업종"}' | python3 -m json.tool

curl -s -X POST https://go100.newtalk.kr/api/go100/ai/chat \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message":"안녕"}' | python3 -m json.tool
```

각 응답의 `reply_to_user`에서 위 3파트 구조 확인.

## 4. Git

- **소스 레포**: `feat(go100): Phase 4 A-1 응답 포매팅 표준화 엔진` → phase-2c-command-center
- **문서 레포**: `docs(go100): Phase 4 A-1 응답 포매팅 표준화 보고서` → master

---

*문서 끝.*
