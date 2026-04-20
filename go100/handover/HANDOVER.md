# GO100 인수인계서 L1 — 현재 상태 요약
> 최종 업데이트: 2026-04-20 | v18.2 (GO100-V5-P2-9 사이트맵 경로 리다이렉트 추가) | 이전 버전: v18.1 (2026-04-20)
> 상세 정보 → [HANDOVER-DETAIL.md](HANDOVER-DETAIL.md) | 이력 → [HANDOVER-ARCHIVE.md](HANDOVER-ARCHIVE.md)

---

## 현재 상태

| 항목 | 값 |
|------|-----|
| 진행률 | **99%** (T-055 완료 기준) |
| 브랜치 | `phase-2c-command-center` |
| 모델 | V3 Brain 활성화 (AUC 0.5656) |
| 모의투자 | session_id 2~7 ACTIVE (2026-02-27~03-29) |
| 실계좌 | 잠금 — CEO 승인 필수 |
| Agent Loop | 20라운드 / 10도구 (D-008 전면 개방) |
| 마지막 HANDOVER 갱신 | v18.1 / 2026-04-20 |

---

## 새 대화창 즉시 체크리스트

1. 이 파일 읽기 완료
2. `.cursorrules`, `CLAUDE.md` 읽기
3. `systemctl status go100 && systemctl status go100-frontend` 확인
4. `psql -d kisautotrade -c "\dt go100_*"` 테이블 확인
5. `.env` 에서 KIS_APP_KEY, KIS_APP_SECRET, DART_API_KEY, GO100_TELEGRAM_* 확인

---

## 다음 우선 작업

| 우선순위 | 태스크 | 상태 |
|----------|--------|------|
| 1 | **30일 모의투자 1사이클 완주** (session_id=2~7, ~03-29) | 기간 만료 — 결과 검토 필요 |
| 2 | **T-056~T-061 10대 무기 장착** | CEO 지시 대기 |
| 3 | 소액 실매매 3일 검증 | 모의투자 완주 + CEO 승인 후 |
| 4 | SaaS 결제 연동 (Stripe/토스페이먼츠) | 설계 완료, CEO 승인 대기 |

---

## 03-09 이후 주요 변경 (2026-03-09~04-20)

| 날짜 | 커밋 | 내용 |
|------|------|------|
| 04-20 | `6bd70fdb` | GO100-V5-P2-9 — 사이트맵 경로 리다이렉트 10개 추가 (next.js page.tsx, /ai/chat → /llm 등) |
| 03-27 | `958e29b` | Phase 3 — run_unified_engine load_active_strategy_cards |
| 03-27 | `ff74b54` | Phase 1 — 전략카드 기반 CTE 파이프라인 |
| 03-23 | `3a3a8d6` | v4_desk_config 시드 데이터 + 스케줄러 에러 로그 |
| 03-23 | `947c0cc` | paper trading monitor dashboard 구현 |
| 03-23 | `fd1b5a5` | backtest result dashboard with charts |
| 03-23 | `0f7d44f` | hypothesis center search/filter 강화 |
| 03-23 | `19834a9` | flock lock + PID guard for backtest worker dedup |
| 03-23 | `089de17` | bridge go100_strategy_hypotheses → v4_hav_hypotheses on PASS |
| 03-23 | `65e5369` | P0 cron path + pipeline promote stage + backtest dedup fix |
| 03-16 | `14766a0` | 뉴스매매 백테스트 분석 결과 및 진화 메모리 추가 |

---

## 핵심 규칙

- 백억이 = GO100 AI 에이전트 이름
- 대표님(user_id=2) = CEO, 보고체 사용
- GO100 작업 시 V4.1 파일 절대 수정 금지
- 실계좌 매매: CEO 승인 필수, `GO100_LIVE_TRADING_ENABLED=false` 유지
- 커밋 prefix: `[GO100]`, `[V4.1]`, `[SHARED]`
