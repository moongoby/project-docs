# AI Self-Evolution Engine 설계서

| 항목 | 내용 |
|------|------|
| 문서 ID | AI-SELF-EVOLUTION-SPEC |
| 작성일 | 2026-02-28 |
| CEO 승인 | D-010, D-011 |
| 선행 | DESK2-MULTI-CONDITION-FINAL-SPEC |

---

## 1. 개요

AI가 스스로 새로운 컨디션과 전략을 발굴하고, 백테스트로 검증하고,
모의 실매매로 테스트하고, 성과를 평가해서 실전에 투입하거나 폐기하는
완전 자동화 시스템.

---

## 2. 아키텍처: 4단계 자동 파이프라인

```
┌─────────────────────────────────────────────────┐
│              AI Self-Evolution Engine            │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Stage 1  │───▶│ Stage 2  │───▶│ Stage 3  │  │
│  │Discovery │    │Validation│    │  Paper    │  │
│  │ (주간)   │    │ (자동)   │    │ Trading  │  │
│  └──────────┘    └──────────┘    └──────────┘  │
│       ▲                               │         │
│       │                               ▼         │
│  ┌──────────┐                   ┌──────────┐   │
│  │  Drift   │◀──────────────────│ Stage 4  │   │
│  │ Detector │                   │  Live    │   │
│  └──────────┘                   └──────────┘   │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │           Reporter (일일/주간/월간)       │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## 3. Stage 1: Discovery (발굴)

### 실행 주기
- 매주 일요일 06:00 (cron)
- Drift Detector 긴급 트리거 시 즉시

### 발굴 방법

#### 방법 1 — 패턴 마이닝
- 최근 20거래일 수익 거래 vs 손실 거래의 차이 변수 추출
- 상위 변수 조합으로 새 컨디션 후보 생성
- 예: "D7 BULL장 승률 60%→45% 하락 감지 → 종가위치 기준 0.70→0.80 변형 후보"

#### 방법 2 — 시그널 파라미터 변형
- 기존 18개 시그널의 파라미터 ±20% 변형
- RSI 30~50 → RSI 25~45, RSI 35~55
- MA 골든크로스 MA5/MA20 → MA3/MA15, MA7/MA25
- 거래량 배수 3× → 2.5×, 4×

#### 방법 3 — 마스크 재최적화
- 최근 20거래일의 5축 데이터로 마스크 재계산
- PF 변동 감지 → ON/OFF 전환 후보 생성

#### 방법 4 — 새 지표 도입
- 미사용 기술적 지표 자동 추가
- ATR(Average True Range), CCI, Williams %R
- Ichimoku Cloud, VWAP, Pivot Points
- 각 지표를 시그널로 변환하여 후보 등록

### 출력
- `candidates.json`: [{type, params, description}, ...]

---

## 4. Stage 2: Validation (검증)

### 프로세스
1. 직전 60거래일 데이터로 학습 (in-sample)
2. 직전 20거래일 데이터로 검증 (out-of-sample)

### 판정 기준

| 판정 | 조건 | 처리 |
|------|------|------|
| PASS | OOS PF ≥ 1.3 AND 거래수 ≥ 20 | Stage 3 진입 |
| MARGINAL | PF ≥ 1.0 AND 거래수 ≥ 10 | 파라미터 조정 후 재검증 |
| FAIL | PF < 1.0 OR 거래수 < 10 | 폐기 + 로그 |

### 출력
- `validated.json`: [{candidate, oos_pf, oos_wr, trades, verdict}, ...]

---

## 5. Stage 3: Paper Trading (모의 실매매)

### 프로세스
- KIS 모의투자 계좌에서 실시간 운영
- 시그널 발생 시 모의 주문 (실제 체결가 기록)
- 20거래일 운영 후 DCS 산정

### 판정 기준

| 판정 | 조건 | 처리 |
|------|------|------|
| PROMOTE | DCS ≥ +1.0% AND 양일 ≥ 50% | Stage 4 승격 |
| EXTEND | DCS ≥ +0.5% | 20거래일 연장 |
| DEMOTE | DCS < +0.5% OR 양일 < 40% | 폐기 |

---

## 6. Stage 4: Live Trading (실전)

### 자본 배분

| 등급 | 조건 | 자본 비중 |
|------|------|-----------|
| 신규 투입 | Stage 3 PROMOTE | 5% |
| A등급 | DCS ≥ +2%, 양일 ≥ 60% | 단계적 확대 (10%→20%→40%) |
| B등급 | DCS +0.5~2%, 양일 ≥ 50% | 유지 |
| C등급 | DCS < +0.5% OR 양일 < 50% | 축소 또는 Stage 3 강등 |

### 등급 재산정
- 20거래일 주기

---

## 7. Drift Detector (성과 이상 감지)

### 실행 주기
- 매일 장마감 후 15:40

### 감지 항목

#### Mask Drift
- 5축 셀별 PF 20거래일 이동평균 계산
- PF < 1.3 셀 감지 → 해당 셀 자동 OFF
- 예: D4 BULL 시간대 T3에서 PF 하락 → T3 OFF

#### Signal Drift
- 시그널별 승률 20거래일 이동평균
- 승률 < 30% 시 2순위 시그널로 자동 교체
- 예: TS-B4 승률 28% → TS-C1으로 교체

#### Condition Drift
- 컨디션별 일 거래수 추적
- 5거래일 연속 거래 0건 → 시장 환경 변화 판단
- Stage 1 Discovery 긴급 트리거

### 출력
- `drift_report.json` + 자동 마스크/시그널 갱신

---

## 8. Reporter (자동 보고)

### 일일 보고서 (장마감 후)
- DCS, 거래 내역, 드리프트 경고
- 파일: `report/daily/YYYY-MM-DD.md`

### 주간 보고서 (일요일)
- Stage별 현황, 신규 후보, 폐기 목록
- Discovery 결과, Validation 통과율
- 파일: `report/weekly/YYYY-WNN.md`

### 월간 보고서 (매월 1일)
- 전체 누적 성과, 전략별 기여도
- 컨디션 등급 변동 이력
- 파일: `report/monthly/YYYY-MM.md`

### 모든 보고서
- git push + CEO 알림 자동화

---

## 9. 모듈 구조

```
DESK2 AI Self-Evolution Engine
│
├── Scheduler (cron)
│   ├── 일일: 40 15 * * 1-5  python3 ai_evolution_engine.py --daily
│   └── 주간: 0  6  * * 0    python3 ai_evolution_engine.py --weekly
│
├── Stage 1: DiscoveryModule
│   ├── PatternMiner — 수익/손실 거래 패턴 분석
│   ├── SignalGenerator — 시그널 파라미터 변형
│   ├── ConditionBuilder — 새 컨디션 후보 생성
│   └── ParameterOptimizer — 기존 파라미터 미세 조정
│
├── Stage 2: ValidationModule
│   ├── Backtester — 60일 학습 + 20일 OOS
│   ├── Judge — PF ≥ 1.3 AND N ≥ 20 → PASS
│   └── Logger — 모든 후보 + 결과 기록
│
├── Stage 3: PaperTradingModule
│   ├── PaperAccountManager — KIS 모의투자 API
│   ├── SignalMonitor — 실시간 시그널 감시
│   ├── Executor — 모의 주문 실행
│   └── DCSCalculator — 일별 성과 산정
│
├── Stage 4: LiveTradingModule
│   ├── LiveAccountManager — KIS 실전 API
│   ├── PositionManager — 자본 배분 관리
│   ├── RiskManager — 일일 손실 한도
│   └── GradeAssessor — 20거래일 등급 산정
│
├── DriftDetector
│   ├── MaskDrift — 5축 PF 변동 감시
│   ├── SignalDrift — 시그널 승률 변동 감시
│   └── ConditionDrift — 거래 빈도 변동 감시
│
└── Reporter
    ├── DailyReport — DCS + 거래 내역
    ├── WeeklyReport — Stage별 현황
    └── MonthlyReport — 전체 성과 + 이력
```

---

## 10. 구현 로드맵

| 순서 | 작업 | 기간 | 의존성 |
|------|------|------|--------|
| 1 | DB 테이블 설계 (candidates, paper_trades, live_trades, drift_logs) | 1일 | — |
| 2 | DiscoveryModule 구현 (방법 1~4) | 2일 | #1 |
| 3 | ValidationModule 구현 (백테스터 + 판정) | 2일 | #1 |
| 4 | PaperTradingModule 구현 (KIS 모의투자 연동) | 3일 | #1, #3 |
| 5 | DriftDetector 구현 | 1일 | #1 |
| 6 | Reporter 구현 (일일/주간/월간) | 1일 | #1~5 |
| 7 | Scheduler + 통합 테스트 | 1일 | #1~6 |
| 8 | Stage 1~2 자동 실행 시작 | CEO 승인 | #7 |
| 9 | Stage 3 모의 실매매 시작 | #8 후 20거래일 | #8 |
| 10 | Stage 4 실전 투입 | CEO 승인 | #9 |

---

## 11. DB 테이블 설계 (신규)

### v4_evolution_candidates
```sql
CREATE TABLE v4_evolution_candidates (
    id SERIAL PRIMARY KEY,
    candidate_type VARCHAR(20),     -- signal_param, new_indicator, mask, condition
    description TEXT,
    params JSONB,
    stage VARCHAR(10),              -- discovery, validation, paper, live, disposed
    oos_pf REAL,
    oos_wr REAL,
    oos_trades INT,
    verdict VARCHAR(10),            -- PASS, MARGINAL, FAIL
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### v4_paper_trades
```sql
CREATE TABLE v4_paper_trades (
    id SERIAL PRIMARY KEY,
    strategy VARCHAR(10),           -- D6, D7, D2, D4, D5, S1
    stock_code VARCHAR(12),
    buy_date DATE,
    sell_date DATE,
    buy_price INT,
    sell_price INT,
    pnl_pct REAL,
    condition_tag VARCHAR(20),
    signal_tag VARCHAR(10),
    market_state VARCHAR(10),       -- BULL, FLAT, BEAR
    candidate_id INT REFERENCES v4_evolution_candidates(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### v4_drift_logs
```sql
CREATE TABLE v4_drift_logs (
    id SERIAL PRIMARY KEY,
    drift_type VARCHAR(20),         -- mask, signal, condition
    target VARCHAR(50),             -- 셀/시그널/컨디션 식별자
    metric_before REAL,
    metric_after REAL,
    action_taken TEXT,              -- OFF, SWAP, TRIGGER_DISCOVERY
    detected_at TIMESTAMP DEFAULT NOW()
);
```

### v4_evolution_grades
```sql
CREATE TABLE v4_evolution_grades (
    id SERIAL PRIMARY KEY,
    strategy VARCHAR(10),
    period_start DATE,
    period_end DATE,
    dcs_avg REAL,
    positive_days_pct REAL,
    grade CHAR(1),                  -- A, B, C
    capital_pct REAL,
    created_at TIMESTAMP DEFAULT NOW()
);
```
