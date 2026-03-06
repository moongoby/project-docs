# CUR-V41-GO100-AUTONOMOUS-LOOP-DIAGNOSIS-001-20260306

**Task ID**: T-166
**제목**: GO100 백억이 군단 자율분석 루프 활성화 — 현황 진단
**날짜**: 2026-03-06
**우선순위**: P0-CRITICAL
**작업 종류**: 진단 전용 (코드 수정 없음)

---

[인계 확인]
직전 완료: T-165
현재 단계: Phase 2C Command Center
CEO 지시 적용: D-009(GO100 자율분석 루프)
strategy_cards: 미확인 (DB 접근 제한)
open_positions: 미확인 (DB 접근 제한)

---

## 1. 진단 목표

GO100 군단(에이전트)이 모의매매 결과를 자동 분석하고 파라미터 조정안을 CEO에게 제안하는
자율분석 피드백 루프 구축을 위한 현황 진단.

흐름:
```
모의매매 결과 수집 → 에이전트별 분석 → debate → commander 종합 → CEO 보고서 생성
```

---

## 2. 차단점 진단 — go100 서비스 로그

### 2.1 journalctl 접근
- `claudebot` 계정은 `adm`, `systemd-journal` 그룹 미소속
- `journalctl -u go100` 직접 열람 불가

### 2.2 /var/log/go100/ 로그 직접 확인

**morning_briefing.log (2026-03-06 08:50):**
```
google.genai.errors.ClientError: 403 PERMISSION_DENIED.
{'error': {'code': 403, 'message': 'Your API key was reported as leaked. Please use another API key.', 'status': 'PERMISSION_DENIED'}}
```
→ **Google Gemini API 키 유출로 브리핑 생성 실패**

**ai_prediction_v3_cron.log (2026-03-06 08:50):**
```
[WARNING] go100_feature_store 조회 실패, ohlcv_daily 폴백:
current transaction is aborted, commands ignored until end of transaction block
psycopg2.errors.InFailedSqlTransaction: current transaction is aborted
```
→ **DB 트랜잭션 오류로 feature_store 조회 실패**
→ AI 예측 배치 정상 실행 불가

**paper_trading_daily.log (2026-03-05 16:13):**
```
run_paper_trading_daily error: 'stock_code'
```
→ **모의매매 KeyError: 'stock_code' 발생** (매매 0건)

**paper_trading_v3_buy.log (2026-03-06 00:10):**
```
[V3 Paper] 결과: {"ok": true, "session_id": 2, "bought": [], "sold": [], "current_capital": 10000000.0}
V3 Paper 매수 0건, 매도 0건
```
→ **V3 Brain 모의매매: 실제 매매 0건** (피드백 원천 데이터 없음)

---

## 3. V4.1 → GO100 피드백 연결점 확인

### 명령:
```bash
grep -rn "mock_trades|v4_mock|trade_result|pnl_pct" /root/kis-autotrade-v4/backend/app/services/go100/
```

### 결과:
| 파일 | 발견 항목 | 비고 |
|------|----------|------|
| `paper_trading_engine_30d.py` | `pnl_pct` (내부 계산) | GO100 자체 모의매매 |
| `ai/tool_executors.py:979` | `pnl_pct` (go100_paper_trades 조회) | GO100 자체 |
| `ai/proactive_reporter.py:306` | `pnl_pct` (GO100 내부) | GO100 자체 |
| `ai/paper_trading.py:257` | `pnl_pct` (GO100 모의매매) | GO100 자체 |

**결론**: `v4_mock_trades`, `v4_mock`, `mock_trades` 참조 **0건**
→ **V4.1 모의매매 결과를 GO100 에이전트가 읽는 코드 존재하지 않음**
→ V4.1 → GO100 피드백 브리지 **미구현**

---

## 4. 에이전트 자동실행 크론 현황

### 4.1 crontab -l (root) 등록 현황

| 등록 여부 | 스크립트 | 주기 | 비고 |
|-----------|----------|------|------|
| ✅ 등록됨 | `run_morning_briefing.sh` | 평일 08:50 KST | Google API 키 오류로 실패 |
| ✅ 등록됨 | `generate_closing_report.py` | 평일 00:35 KST (다음날 새벽) | 정상 |
| ✅ 등록됨 | `run_paper_trading_daily.sh` | 평일 01:10 KST | 'stock_code' KeyError |
| ✅ 등록됨 | `run_paper_trading_v3.py --mode buy` | 평일 09:10 KST | 매수 0건 |
| ✅ 등록됨 | `run_paper_trading_v3.py --mode sell` | 평일 15:15 KST | |
| ✅ 등록됨 | `run_paper_trading_v3.py --mode weekly_review` | 금요일 16:30 KST | 0건 |
| ✅ 등록됨 | `daily_ai_prediction_v3.sh` | 평일 17:50 KST | DB 트랜잭션 오류 |
| ✅ 등록됨 | `run_research_pipeline.sh` | 토요일 10:00 KST | |
| ✅ 등록됨 | `lightgbm_retrainer.py` | 매월 1일/29일 01:05 KST | |
| ❌ **미등록** | `run_daily_hypothesis_pipeline.py` | (문서: 평일 15:40) | **크론 없음** |
| ❌ **미등록** | `run_strategy_evolution.sh` | (문서: 토 09:00) | **크론 없음** |
| ❌ **미등록** | `run_hypothesis_backtest.py` | (야간 배치) | **크론 없음** |
| ❌ **미등록** | `commander.run_post_market_review()` | (문서: 15:30) | **크론/트리거 없음** |

### 4.2 /etc/cron.d/ 등록 현황
| 파일 | 내용 |
|------|------|
| `go100_morning_briefing` | 평일 08:50 run_morning_briefing.sh |
| `go100_closing_report` | 평일 00:35 generate_closing_report.py |
| `go100_paper_trading` | 평일 01:10 run_paper_trading_daily.sh |

---

## 5. Evolution Loop 미작동 원인

### 5.1 코드 존재 여부

| 컴포넌트 | 파일 | 상태 |
|----------|------|------|
| 전략 진화 | `strategy_evolution.py` | ✅ 구현 완료 |
| 가설 검증 | `ai/hypothesis_engine.py` | ✅ 구현 완료 |
| HAV 백테스트 | `scripts/go100/run_hypothesis_backtest.py` | ✅ 파일 존재 |
| 일간 파이프라인 | `scripts/go100/run_daily_hypothesis_pipeline.py` | ✅ 파일 존재 |
| 에이전트 토론 | `agents/debate.py` | ✅ 구현 완료 |
| 커맨더 | `agents/commander.py` | ✅ 구현 완료 |

### 5.2 미작동 원인 분석

**가설 엔진 (`hypothesis_engine.py`)**:
- crontab 코멘트: `40 15 * * 1-5` (평일 15:40 KST)
- **실제 crontab 등록: 없음**
- 환경변수 의존: `ANTHROPIC_API_KEY` (필수), `HYP_LEVEL1~3`, `AI_DAILY_COST_LIMIT`

**전략 진화 (`run_strategy_evolution.sh`)**:
- 스크립트 내 코멘트: `0 9 * * 6` (토 09:00 KST)
- **실제 crontab 등록: 없음**

**커맨더 (`commander.py`)**:
- `GO100_COMMANDER_MODE=true` (환경변수 확인됨)
- `GO100_DESK_CHAIN_MODE=true` (환경변수 확인됨)
- `run_post_market_review()` 메서드 존재: ✅
- **호출 크론/자동 트리거: 없음**
- 아키텍처: `regime → [supply_demand, technical, news] → bull_bear_debate → risk → 최종 판단`

---

## 6. 자율분석 루프 설계서 — 누락 목록

목표 흐름:
```
[V4.1 v4_mock_trades] ─→ [수집 브리지]
                             ↓
[GO100 에이전트별 분석: regime/supply_demand/technical/news]
                             ↓
[Bull/Bear Debate (debate.py)]
                             ↓
[Commander 종합 (commander.run_post_market_review())]
                             ↓
[파라미터 조정안 생성]
                             ↓
[CEO 보고서 (go100_reports 삽입 + Telegram 발송)]
```

### 6.1 누락된 코드

| 번호 | 누락 항목 | 우선순위 | 설명 |
|------|----------|----------|------|
| C-1 | V4.1 피드백 브리지 | P0 | v4_mock_trades → GO100 분석 입력 변환 스크립트 없음 |
| C-2 | 파라미터 조정안 생성기 | P0 | 분석 결과 → 파라미터 제안 코드 없음 |
| C-3 | CEO 자동 보고서 생성 | P1 | 파라미터 조정안 → CEO용 리포트 포매팅 없음 |

### 6.2 누락된 설정/크론

| 번호 | 누락 항목 | 등록 위치 | 권장 주기 |
|------|----------|----------|----------|
| CR-1 | `run_daily_hypothesis_pipeline.py` 크론 | crontab | 평일 15:40 KST |
| CR-2 | `run_strategy_evolution.sh` 크론 | crontab | 토 09:00 KST |
| CR-3 | `run_hypothesis_backtest.py` 크론 | crontab | 평일 야간(예: 01:00 KST) |
| CR-4 | `commander.run_post_market_review()` 트리거 | crontab | 평일 15:35 KST |
| CR-5 | V4.1 브리지 스크립트 크론 | crontab | 평일 16:00 KST |

### 6.3 누락된 API 키/환경변수 수정

| 번호 | 항목 | 현재 상태 | 조치 |
|------|------|-----------|------|
| ENV-1 | Google Gemini API Key | **유출됨 (403 PERMISSION_DENIED)** | 키 교체 필수 |
| ENV-2 | ANTHROPIC_API_KEY | 확인 필요 | hypothesis_engine 필수 |
| ENV-3 | DB 트랜잭션 복구 | feature_store 접근 실패 | connection/rollback 처리 필요 |

### 6.4 누락된 DB 구조

- `v4_mock_trades` → `go100_agent_analysis` 매핑 테이블: 없음
- 파라미터 조정 이력 테이블 (`go100_param_proposals`): 없음

---

## 7. 현재 작동 중인 기능 (정상)

| 기능 | 상태 | 비고 |
|------|------|------|
| Morning Briefing (구조) | ⚠️ 부분 작동 | Gemini 오류로 요약 실패, 빈 리포트 생성됨 |
| Closing Report 크론 | ✅ 등록됨 | 실행 여부 확인 필요 |
| Paper Trading V3 크론 | ⚠️ 실행되나 0건 | stock_code KeyError 및 매수 조건 미충족 |
| DESK 체인 (환경변수) | ✅ true | 크론 트리거 없어 미실행 |
| Commander 코드 | ✅ 구현됨 | 자동 실행 트리거 없음 |
| Debate 코드 | ✅ 구현됨 | 자동 실행 트리거 없음 |
| Hypothesis Engine 코드 | ✅ 구현됨 | 크론 미등록 |
| Strategy Evolution 코드 | ✅ 구현됨 | 크론 미등록 |

---

## 8. 결론 및 후속 조치 권고

### 핵심 차단점 (우선순위 순)

1. **[P0-BLOCKER] Google Gemini API 키 유출** — 키 교체 없이 브리핑/AI 예측 모두 실패
2. **[P0-MISSING] V4.1→GO100 피드백 브리지 미구현** — v4_mock_trades를 GO100이 읽는 코드 없음
3. **[P0-MISSING] 파라미터 조정안 자동 생성 코드 없음** — 분석 결과를 제안 형식으로 변환하는 로직 없음
4. **[P1-CRON] 가설검증/전략진화/커맨더 크론 미등록** — 코드는 준비됐으나 자동 실행 안됨
5. **[P1-BUG] paper_trading_daily `'stock_code'` KeyError** — V3 모의매매 0건의 직접 원인

### 후속 T-167 권고 작업 내용
- Gemini API 키 교체 (root 수행)
- V4.1 → GO100 피드백 브리지 스크립트 신규 작성
- 파라미터 조정안 → CEO 보고서 자동 생성기 작성
- hypothesis/evolution/commander crontab 등록
- paper_trading_daily `'stock_code'` 키 오류 수정

---

## 체크포인트

- [x] 코드 레포 커밋: 해당 없음 (진단 전용)
- [ ] project-docs 보고서 push: done_watcher.sh 통해 자동 처리 예정
