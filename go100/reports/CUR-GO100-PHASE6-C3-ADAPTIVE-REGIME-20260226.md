# CUR-GO100-PHASE6-C3-ADAPTIVE-REGIME (2026-02-26)

## 개요
시장 레짐(상승/횡보/하락/위기) 변화 감지 시 포트폴리오 전략을 자동 조정하는 Adaptive Regime Engine 구현.

**목표**: "장이 나빠지면 자동으로 방어 모드" — 레짐 변화 → 전략 배분 자동 조정 제안 → 사용자 승인 또는 "조정 실행해줘"로 즉시 반영.

---

## 사전 확인 결과

- **v4_market_regime_daily**: 컬럼 `date`, `regime`, `regime_score`, `vkospi` 등 (스키마 확인 완료)
- **레짐 값**: DB에는 `SIDEWAYS`, `MILD_TREND_UP`, `MILD_TREND_DOWN` 등 저장
- **매핑**: 엔진 내부에서 5레짐 키로 정규화 (`strong_bull`, `bull`, `sideways`, `bear`, `crisis`)
- **백업**: `/root/backup/app-phase6-c3-regime-YYYYMMDD-HHMMSS/` 생성 완료

---

## 구현 내용

### 1. 신규 파일 `backend/app/services/go100/ai/regime_engine.py`

| 기능 | 함수 | 설명 |
|------|------|------|
| 레짐 변화 감지 | `detect_regime_change(db)` | v4_market_regime_daily 최근 5일 조회, 전환일·추세·VKOSPI 라벨 반환 |
| 배분 매트릭스 | `get_regime_strategy_map()` | 5레짐 × 3성향 = 15가지 권장 배분 (읽기 전용) |
| 조정 제안 | `generate_adjustment(portfolio_id, db)` | 현재 레짐 + goal risk_appetite → 목표 배분, 현재와 diff → adjustments |
| 조정 실행 | `apply_adjustment(portfolio_id, adjustment, db)` | go100_portfolio_allocations UPDATE, 스냅샷에 regime_adjustment 이벤트 기록 |
| 레짐 이력 | `get_regime_history(days, db)` | 최근 N일 레짐 + 전환 포인트 플래그 |
| 응답 포맷 | `format_regime_response(regime_data, adjustment)` | 사용자용 한글 문자열 (레짐 분석 + 조정 제안) |

- **REGIME_ALLOCATION_MATRIX**: (regime, risk_profile) → { strategy_type: allocation_pct }
  - risk_profile: `aggressive`, `moderate`, `conservative` (go100_goals.risk_appetite)
  - 포트폴리오에 없는 전략 유형은 조정 시 제외하고, 기존 유형만 100%로 스케일하여 반영

### 2. ai_router.py 연동

- **신규 인텐트 `regime`**
  - 키워드: `시장 레짐`, `시장 상태`, `방어 모드`, `공격 모드`, `레짐 어때`, `레짐 어떻게`, `레짐은`, `조정 필요해`
  - 핸들러: `_handle_regime(user_id, db)` → `detect_regime_change` + `generate_adjustment`(포트폴리오 있으면) → `format_regime_response` 반환

- **market_briefing**
  - 마지막에 안내 문구 추가: "레짐에 따른 포트폴리오 조정이 필요하면 '현재 시장 레짐은?'이라고 물어보세요."

- **portfolio_status**
  - 레짐 기반 조정 필요 시: `generate_adjustment` 호출 후 adjustments 있으면 "시장 레짐에 따른 배분 조정이 필요해 보여요. '현재 시장 레짐은?' 또는 '조정 실행해줘'라고 하시면 반영해 드립니다." 추가

- **rebalance + "조정 실행해줘"**
  - 메시지에 "조정 실행", "적용해줘", "조정 반영", "반영해줘" 포함 시:
    - `generate_adjustment` → `apply_adjustment` 실행
    - 성공 시: "레짐에 따른 포트폴리오 배분 조정을 반영했어요."

- **rebalance** 키워드에 `조정 실행해줘`, `조정 반영해줘`, `적용해줘` 추가

---

## 검증

- `regime_engine.py`: 문법 및 로직 검토 완료 (lint 통과)
- ai_router: regime 인텐트·rebalance 메시지 인자·레짐 import 반영 완료

서비스 재시작 및 실제 채팅 검증:

```bash
systemctl restart go100
# curl -s -X POST https://go100.newtalk.kr/api/go100/ai/chat \
#   -H "Authorization: Bearer {TOKEN}" -H "Content-Type: application/json" \
#   -d '{"message":"현재 시장 레짐은?"}'
# curl -s -X POST ... -d '{"message":"포트폴리오 조정 필요해?"}'
```

---

## Git

- **kis-autotrade-v4**: `feat(go100): Phase 6 C-3 Adaptive Regime Engine` 커밋 후 `phase-2c-command-center` 푸시
- **project-docs**: 본 보고서 추가 후 `docs(go100): Phase 6 C-3 Adaptive Regime Engine 보고서` 커밋 푸시

---

## 완료 요약

- 5레짐 × 3성향 = 15가지 배분 매트릭스
- 레짐 변화 자동 감지 + 포트폴리오 조정 제안
- v4_market_regime_daily 연동 (date, regime, regime_score, vkospi)
- market_briefing / portfolio_status 레짐 안내 추가
- "조정 실행해줘" → apply_adjustment 트리거
