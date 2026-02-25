# CUR-GO100-DATA-ACCURACY-001

## 데이터 정확성 및 응답 가독성 개선

**날짜**: 2026-02-26  
**상태**: 완료

---

## 작업 요약

백억이(GO100 AI) 응답의 데이터 정확성 검증 강화 및 사용자-facing 포맷(날짜, 종목 리스트, 스크리닝 안내) 통일.

## 변경 사항

### 1. response_filter.py — 거래량 배수 검증

- **추가**: `_find_volume_ratios()` — 텍스트에서 "N배" 패턴 추출 (예: `1500배`, `거래량 600배`)
- **검증**: 500배 초과 시 `HallucinationReport.high_volume_ratios`에 적재
- **경고**: `sanitize_reply()`에서 "거래량 500배 초과 수치는 데이터 오류일 수 있어 확인이 필요합니다" 문구 추가
- **적용 대상**: LLM 생성 응답(strategy, optimize 등)에만 적용

### 2. stock_screening — 요청 조건 vs 실행 조건 안내

- **screening_engine.py**
  - `get_requested_screening_label(message)` 추가  
    - 키워드 매핑: 이평선/정배열 → "이평선 정배열", 저평가 → "저평가", 기관매수 → "기관 매수", 상한가/급등 등
  - `format_screening_result()`: 종목당 줄바꿈·들여쓰기 구조화 (종목 라인 `  **N. 이름**`, 상세 `\n    ...`)
- **ai_router.py `_handle_stock_screening()`**
  - 요청 라벨 ≠ 실제 실행 라벨일 때 상단에 안내 추가:
    - `⚠️ 요청하신 조건은 현재 준비 중입니다. 대신 **[실제조건]**으로 검색합니다.`

### 3. 종목 리스트 응답 가독성

- **상승/하락/거래량/시총 상위 10종목** (ai_router `_handle_stock_info()`)
  - 한 줄 나열 → **종목당 1줄 + 들여쓰기** (`  N. 종목명(코드) ...`)
- **스크리닝 결과** (screening_engine `format_screening_result()`)
  - momentum_up / foreign_buy: 각 종목 블록 앞에 `  ` 들여쓰기, 상세 라인 `    ` 4칸

### 4. 날짜 포맷 통일

- **형식**: `20260225` / `YYYY-MM-DD` → **`2026-02-25(화)`** 형태로 사용자 표기 통일
- **적용 위치**: 이미 `_fmt_date()`로 적용됨
  - 개별 종목 시세: "최근 종가: N원 (**2026-02-25(화)** 기준)"
  - 수급 일자, 5거래일 시세, 시장 브리핑 기준일, 5일 추이

### 5. 5거래일 데이터 표기

- **시장 브리핑** (ai_router `_handle_market_briefing()`)
  - 기존: `5일 추이: 2026-02-25(화): 2,750.1 → 2026-02-24(월): ...` (한 줄)
  - 변경: **줄바꿈 리스트**
    ```
    5일 추이:
      2026-02-25(화): 2,750.1
      2026-02-24(월): ...
    ```

## 변경 파일

| 파일 | 변경 |
|------|------|
| `backend/app/services/go100/ai/response_filter.py` | 거래량 배수 500배 초과 검증 및 경고 |
| `backend/app/services/go100/screening_engine.py` | `get_requested_screening_label()`, 종목 포맷 들여쓰기 |
| `backend/app/routers/go100/ai_router.py` | 스크리닝 조건 불일치 안내, 상위 종목 들여쓰기, 5일 추이 줄바꿈 |

## 검증 포인트

- `systemctl restart go100` 후:
  1. **"삼전 얼마야"** → 날짜가 `2026-02-25(화) 기준` 형태로 표시
  2. **"상한가 종목"** → 종목당 1줄, 들여쓰기 구조화
  3. **"이평선 정배열 종목"** → 상단에 `⚠️ 요청하신 조건은 현재 준비 중입니다. 대신 **모멘텀 상승**으로 검색합니다.` 안내 포함

---

*Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>*
