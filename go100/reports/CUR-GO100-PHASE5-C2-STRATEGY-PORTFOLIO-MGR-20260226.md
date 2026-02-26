# CUR-GO100-PHASE5-C2-STRATEGY-PORTFOLIO-MGR (2026-02-26)

## 개요

여러 전략 카드를 하나의 포트폴리오로 묶어 자금 배분, 통합 리스크 관리, 리밸런싱을 수행하는 **Strategy Portfolio Manager** 구현.  
Goal Engine(C-1)이 추천한 전략 조합을 실제 포트폴리오로 실체화하는 계층.

---

## 사전 작업 결과

- `.cursorrules` 확인: GO100 규칙은 `.cursor/rules/go100-rules.md` 참조
- **go100_strategy_cards**: 22건 (is_active true 14, false 8)
- **go100_portfolios** / **go100_positions**: 기존 카드별 포트폴리오·포지션 테이블 유지
- **v4_sector_stock_mapping** / **v4_sector_correlation**: 스키마 존재, mapping 건수 0
- **백업**: `backend/app` → `/root/backup/app-phase5-c2-portfolio-{timestamp}/`

---

## DB 스키마

### 신규 테이블 3개

| 테이블 | 설명 |
|--------|------|
| `go100_strategy_portfolios` | 전략 포트폴리오 묶음 (user_id, goal_id, total_capital, status) |
| `go100_portfolio_allocations` | 전략별 배분 (portfolio_id, card_id, allocation_pct, allocation_amount, strategy_type, max_mdd_limit) |
| `go100_strategy_portfolio_snapshots` | 일일 스냅샷 (portfolio_id, snapshot_date, total_value, total_pnl, total_pnl_pct, drawdown_pct, peak_value, allocation_detail) |

- 마이그레이션: `backend/migrations/029_go100_strategy_portfolio_mgr.sql`
- 기존 `go100_portfolio_snapshots`(카드별 포트폴리오)와 구분하기 위해 전략 포트폴리오용 스냅샷 테이블명을 **go100_strategy_portfolio_snapshots**로 생성

---

## 구현 요약

### 1. 신규 모듈 `backend/app/services/go100/ai/portfolio_manager.py`

| 함수 | 기능 |
|------|------|
| `create_portfolio(user_id, goal_id, total_capital, strategies, db)` | go100_strategy_portfolios + go100_portfolio_allocations INSERT, portfolio_id 반환 |
| `get_portfolio_summary(user_id, db)` | ACTIVE 포트폴리오 요약(목표, 배분, 리스크 등급) |
| `calculate_portfolio_risk(portfolio_id, db)` | 개별 MDD, 가중평균 MDD, **v4_sector_correlation** 기반 분산효과, 통합 예상 MDD, 리스크 등급 |
| `check_rebalance_needed(portfolio_id, db)` | 배분 괴리 5%p, MDD 한도 초과, 레짐 변화, 30일 경과 등으로 필요 여부·사유·긴급도 반환 |
| `suggest_rebalance(portfolio_id, db)` | 현재 vs 목표 배분, 증액/감액 제안 |
| `get_portfolio_performance(portfolio_id, days, db)` | go100_strategy_portfolio_snapshots 기반 성과·MDD·vs KOSPI |

### 2. data_queries.py 추가

- `get_portfolio_with_allocations(user_id, db)` — ACTIVE 전략 포트폴리오 1건 + 배분 + 카드명
- `get_portfolio_snapshots(portfolio_id, days, db)` — 전략 포트폴리오 스냅샷 최근 N일

### 3. ai_router.py 연동

- **portfolio_status**: `get_portfolio_summary()` 우선 사용 → 통합 포트폴리오 뷰; 리밸런싱 필요 시 안내 문구 추가
- **risk_check**: 전략 포트폴리오 있으면 `calculate_portfolio_risk()` → 통합 리스크 + 분산효과; 없으면 기존 카드별 MDD
- **신규 인텐트 rebalance**: `check_rebalance_needed` + `suggest_rebalance` 조합 응답
- C2SC 인텐트 16개로 확장, 키워드 폴백에 리밸런싱 추가

### 4. response_formatter.py

- `rebalance` 인텐트용 헤더·푸터 추가

---

## V4.1 연동

- **v4_sector_correlation**: 최신 calc_date 기준 평균 상관계수로 분산효과 계산 (예: (1 - avg_corr) * 15%p 완화)
- **v4_market_regime_daily**: 리밸런싱 필요 여부 판단 시 최근 2일 레짐 변화 반영
- **go100_goals**: 포트폴리오 요약 시 goal_id로 연결된 목표 표시

---

## 검증

- `systemctl restart go100` 후 서비스 정상 기동 확인
- DB: `go100_strategy_portfolios`, `go100_portfolio_allocations` 테이블 존재 및 0건 확인

테스트 예시 (토큰 필요):

```bash
# 포트폴리오 현황 (전략 포트폴리오 없으면 기존 카드 목록 노출)
curl -s -X POST https://go100.newtalk.kr/api/go100/ai/chat \
  -H "Authorization: Bearer {TOKEN}" -H "Content-Type: application/json" \
  -d '{"message":"내 포트폴리오 현황"}'

# 리스크 체크 (전략 포트폴리오 있으면 통합 리스크+분산효과)
curl -s -X POST https://go100.newtalk.kr/api/go100/ai/chat \
  -H "Authorization: Bearer {TOKEN}" -H "Content-Type: application/json" \
  -d '{"message":"포트폴리오 위험도 분석해줘"}'

# 리밸런싱
curl -s -X POST https://go100.newtalk.kr/api/go100/ai/chat \
  -H "Authorization: Bearer {TOKEN}" -H "Content-Type: application/json" \
  -d '{"message":"리밸런싱 필요해?"}'
```

---

## Git

- **kis-autotrade-v4**: phase-2c-command-center 브랜치에 커밋 예정
- **project-docs**: go100/reports 보고서 추가 후 master 푸시

---

## 완료 체크리스트

- [x] 신규 테이블 3개: go100_strategy_portfolios, go100_portfolio_allocations, go100_strategy_portfolio_snapshots
- [x] 신규 모듈 portfolio_manager.py (6개 함수)
- [x] V4.1 v4_sector_correlation 연동 (분산효과)
- [x] 핸들러 확장: portfolio_status, risk_check + 리밸런싱 인텐트
- [x] data_queries: get_portfolio_with_allocations, get_portfolio_snapshots
- [x] go100 서비스 재시작 및 기동 확인
