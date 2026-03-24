# P0: LLM 가설 생성 프롬프트 개선 — JSON 스키마 강제 + indicator 카탈로그 + Few-shot + 검증 레이어

> 날짜: 2026-03-24
> 작업자: Claude Code (Opus 4.6)
> 프로젝트: GO100

[인계 확인]
직전 완료: P0-1-QUEUE-FIX
현재 단계: Phase 2C
CEO 지시 적용: D-001, D-003, D-007

---

## 배경

LLM(l2_desk_generator.py)이 가설 생성 시 자연어 조건("V_RVOL > 1.5", "RSI_14 < 30")을 생성하여 SignalEvaluator가 해석 불가 → trades=0이 238건 중 237건(99.6%).

## 수정 내용

### 작업 1: 가설 생성 프롬프트 수정 (l2_desk_generator.py)

**1-1. Indicator 카탈로그 삽입**
- `ENTRY_INDICATOR_CATALOG`: 6개 타입 (ma_cross, rsi_threshold, price_breakout, volume_surge, surge_radar, volatility_breakout)
- `EXIT_INDICATOR_CATALOG`: 4개 타입 (profit_target, stop_loss, trailing_stop, holding_days)
- 프롬프트에 "반드시 아래 type 중에서만 선택하라" 카탈로그 섹션 추가

**1-2. JSON 스키마 강제**
- entry_signal.conditions: `[{"type": "카탈로그_type", "param1": value1, ...}]` 형태 강제
- exit_signal.rules: `[{"type": "stop_loss", "pct": 5.0}, ...]` 형태 강제
- 자연어 문자열 조건 "절대 금지" 명시

**1-3. Few-shot 예시 3건 추가**
- DESK1 스캘핑: RSI 과매도 + 거래량 급등
- DESK2 데일리: 골든크로스 + 거래량
- DESK3 단기스윙: 변동성돌파 + 급등레이더

### 작업 2: 검증 레이어 (`_validate_hypothesis()`)

- `_validate_conditions()`: conditions가 list of dict인지, 각 dict에 type 키가 있고 카탈로그에 있는지 확인
- `_validate_hypothesis()`: entry_signal + exit_signal 모두 검증
- `_generate_with_validation()`: 실패 시 최대 2회 재생성 → 3회 실패 시 `status='GENERATION_FAIL'`
- 재생성 프롬프트에 실패 사유와 유효 타입 목록 포함

### 작업 3: 모순 조건 탐지

- `_CONTRADICTION_PAIRS`: 4개 모순 쌍 정의
  - 골든크로스 + RSI 과매도(<35)
  - 데드크로스 + RSI 과매수(>65)
  - 상향돌파 + 하향돌파
  - 골든크로스 + 데드크로스
- `_detect_contradictions()`: AND 결합 조건 중 물리적 모순 검사
- 모순 발견 시 warning 로그 + LLM에게 수정 요청 (재생성)

### hypothesis_rule_mapper.py 연동 수정

- 구조화된 dict 조건 직접 변환 (line 91-96): `{"type": "...", ...params}` → `{"indicator": "...", "params": {...}}`
- 새 exit_signal.rules 형식 매핑 (line 116-130): `{"type": "stop_loss", "pct": 3.0}` → `{"stop_loss_pct": 3.0}`
- 레거시 형식 호환 유지: 자연어 조건, top-level stop_loss/take_profit 필드

## 검증 체크리스트

- [x] 구현 목표: LLM 가설 생성 시 구조화된 JSON 스키마 강제 + 검증 + 모순 탐지
- [x] 검증 방법: Python 단위 테스트 (l2_desk_generator import + _validate_hypothesis + _detect_contradictions)
- [x] 완료 기준:
  - 정상 가설 → ok=True
  - 미지원 type 가설 → ok=False, reason="미지원 type: INVALID_TYPE"
  - 골든크로스+RSI<25 → 모순 경고 1건
  - 골든크로스+거래량 → 모순 경고 0건
  - hypothesis_rule_mapper: 새 형식(dict conditions, exit rules) + 레거시 형식 모두 정상 변환
- [x] 실패 기준: import 오류, 검증 로직 false positive/negative
- [x] Syntax OK: 모든 수정 파일 ast.parse 통과
- [x] 레거시 호환: 기존 자연어 조건 파싱 경로 유지

## 수정 파일

| 파일 | 변경 내용 |
|------|-----------|
| backend/app/services/go100/ai/l2_desk_generator.py | +435줄: 카탈로그, 프롬프트 개선, 검증 레이어, 모순 탐지, 재생성 로직 |
| backend/app/services/go100/ai/hypothesis_rule_mapper.py | 구조화 dict 직접 변환 + exit_signal.rules 매핑 + 레거시 호환 |

## 기대 효과

- LLM 가설 → SignalEvaluator 변환 성공률: ~0.4% → 90%+ (예상)
- trades=0 가설 비율 대폭 감소
- 물리적 모순 조건 자동 탐지로 무의미한 백테스트 방지
