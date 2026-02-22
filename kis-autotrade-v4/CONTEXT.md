# KIS AutoTrade V4.1 — 프로젝트 컨텍스트

> **최종 갱신**: 2026-02-23
> **문서 ID**: CONTEXT-V1.0
> **대상 서버**: 211.188.51.113
> **프로젝트 경로**: /root/kis-autotrade-v4
> **Git (Private)**: git@github.com:moongoby/go100.git
> **브랜치**: phase-2c-command-center (origin 대비 109+ commits ahead)
> **서비스 URL**: https://trading41.newtalk.kr/
> **대시보드**: https://trading41.newtalk.kr/dashboard.html
> **DESK 종목추천**: https://trading41.newtalk.kr/desk-recommend.html

---

## 1. 프로젝트 요약

한국투자증권(KIS) API 기반 자동매매 시스템.
5개 DESK(시간축별 매매 단위)가 최적 수익 종목을 발굴·추천하고,
종목에 맞는 전략을 매칭하여 자동 매수·청산까지 수행한다.

---

## 2. CEO 핵심 철학 (절대 원칙)

1. DESK는 시간축별 최고 수익 종목 추천 엔진이다. 비활성화는 없고 오직 수익률 극대화·최적화만 존재한다.
2. 전략은 생성/폐기 가능하며, 성과 좋은 전략만 살아남는다.
3. 진입 타이밍이 수익률을 결정한다. entry_time 데이터 없이는 백테스트 의미가 없다.
4. 종목 필터는 DESK의 생명이며 핵심 엔진의 한 축이다.
5. 자본 운영은 펀드 매니저의 역할이다.
6. 요일별 접근은 편협하다. 변동 자체를 예측·적용할 수 있어야 한다.

---

## 3. 절대 작업 규칙 12조

```
이 규칙은 어떤 상황에서도 위반할 수 없다.

1.  .env 파일 절대 커밋 금지
2.  ALTER TABLE / DROP TABLE 금지 (CEO 명시 승인 + 백업 시에만)
3.  kis-v41-api, kis-v41-monitor, kis-v41-scheduler 재시작 금지
    (CEO 승인 시 1회만, 전후 DB 무결성 확인)
4.  strategy_cards UPDATE는 CEO 승인 후에만
5.  v4_positions 직접 수정 금지 (SELECT만)
6.  backtest_engine_v2.py 수정은 CEO 승인 후에만
7.  오류 시 즉시 작업 중단 → 현재 상태 보고
8.  모든 작업 전 사전 확인:
    - SELECT COUNT(*) FROM strategy_cards; → 62
    - SELECT COUNT(*) FROM v4_positions WHERE status='OPEN'; → 5
    - 서비스 상태, 디스크 확인
9.  커밋 전 git diff로 .env, .bak 확인
10. 배포 전 python -m py_compile 검증
11. DB 변경 시 사전 백업 (/root/backups/)
12. 토큰 80% 도달 시 작업 중단 → 인계서 작성
```

---

## 4. Cursor 필수 규칙

```
[서버]
- 서버: 211.188.51.113
- 프로젝트: /root/kis-autotrade-v4
- 가상환경: source /root/kis-autotrade-v4/venv/bin/activate
- DB: sudo -u postgres psql -d kisautotrade
- 백업: /root/backups/

[작업지시서] 코드블록 작성, 사전확인 포함, 12조 상단 명시
[백업] 수정 전 cp, 스키마 변경 전 pg_dump
[커밋] "작업명: 요약", .env/.bak 확인, 브랜치: phase-2c-command-center
[보고서] report/ 에 .md, 사전/사후 DB 수치 포함

[세션 종료 프로토콜]
1. docs/CONTEXT.md "현재 상태" 섹션 갱신
2. bash /root/project-docs/scripts/sync_kis.sh
3. git commit (양쪽 모두)
```

---

## 5. 아키텍처 계층

```
CEO 지시
  └─ Adaptive Engine (주간 스코어링, 자금 리밸런서)
       └─ Fund Commander (펀드풀, DESK별 자본 배분)
            └─ DESK1~5 Commander (시간축별 종목 발굴·추천)
                 └─ Strategy Cards (개별 전략, is_live/is_active)
                      └─ Pipeline Orchestrator (PRE → 장중 → POST)
                           └─ Signal Engine → Risk Manager → Order Executor
                                └─ Position Manager → Promotion/Transfer Engine
```

상세: [architecture/v41-architecture-v1.1.md](./architecture/v41-architecture-v1.1.md)

---

## 6. DESK 정의

| DESK | 시간축 | max_hold | 라이브/전체 | 역할 | 충족도 |
|------|--------|----------|-------------|------|--------|
| DESK1 | 초단타 | 0-1일 | 10/10 | 호가·분봉 스캘핑 | 미검증 |
| DESK2 | 단타 | 1-3일 | 10/16 | 일봉/분봉 단기 | 분봉 최적화 필요 |
| DESK3 | 단기스윙 | 3-10일 | 9/11 | 핵심 수익원 | 충분 |
| DESK4 | 중기스윙 | 20-40일 | 6/9 | 추세 추종 | 충분 |
| DESK5 | 장기 | 90-120일 | 1/10 | 장기 모멘텀 | 미달 |

---

## 7. 현재 상태 스냅샷

### 서비스

| 서비스 | 포트 | 상태 |
|--------|------|------|
| kis-v41-api | 8003 | active |
| kis-v41-monitor | - | active |
| kis-v41-scheduler | - | active |
| kis-v41-minute-collector | - | inactive (월요일 활성화) |
| kis-v41-orderbook-collector | - | inactive (월요일 활성화) |

### DB 무결성

| 항목 | 기준값 |
|------|--------|
| strategy_cards | **62** |
| v4_positions OPEN | **5** (49, 51, 55, 58, 61) |
| DB 크기 | 6,152 MB |
| v4_ohlcv_minute | 19,468,781행 |
| v4_scalping_universe | 708 종목 |
| v4_market_regime_daily | 59행 |
| 디스크 | 53% (45GB free) |

### OPEN 포지션

| ID | 종목 | DESK |
|----|------|------|
| 49 | 221800 | DESK1 |
| 51 | 001510 | DESK2 |
| 55 | 001290 | DESK3 |
| 58 | 373110 | DESK4 |
| 61 | 360140 | DESK2 |

### DESK 자금 배분

| DESK | 비율 | 배정 | 사용 | 잔여 | 포지션 |
|------|------|------|------|------|--------|
| DESK1 | 25% | 483,904,076 | 34,707,400 | 449,196,676 | 1 |
| DESK2 | 15% | 89,977,268 | 38,510,307 | 51,466,961 | 2 |
| DESK3 | 25% | 149,962,113 | 20,391,305 | 129,570,808 | 1 |
| DESK4 | 20% | 150,927,427 | 25,934,675 | 124,992,752 | 1 |
| DESK5 | 15% | 124,976,536 | 0 | 124,976,536 | 0 |

---

## 8. 프로모션 시스템

- 구현: split_transfer_engine.py, pipeline_orchestrator, lifecycle.py
- 실행: 0건
- 결함: min_profit_pct만 체크 (설계는 다중 조건)

---

## 9. 백테스트 엔진 (2026-02-23 업그레이드)

16개 컬럼 추가: entry/exit datetime·price, MFE/MAE, regime, commission 등

| 세션 | DESK | 모드 | ROI | 승률 | MDD | 거래수 |
|------|------|------|-----|------|-----|--------|
| 63 | 검증 | daily | - | - | - | 94 |
| 62 | DESK2 | 분봉 | **-23.25%** | 34.24% | 23.32% | 1,171 |
| 61 | DESK2 | daily | +7.48% | 41.55% | 7.38% | 503 |
| 60 | DESK3 | daily | +32.23% | - | - | - |

핵심: 분봉(-23%) vs 일봉(+7%) → 분봉 진입 최적화 필수

---

## 10. 분석 결과 요약

### OVERLAP-GUARD
- 19개 종목 DESK2·DESK3 동시 진입, DESK2가 수익 상쇄
- 타 DESK 간 중복 차단 미구현 → CEO 정책 대기

### REGIME-STRATEGY-CROSS
- DESK2: 하락·횡보장 취약
- DESK3: 전 레짐 양수
- DESK2_장초반레인지돌파: STRONG_DOWN -2.57 (최악)

### 종목-전략 매칭
- 최적 보유: 1-3일(효율), 4-7일(절대수익), 15일+ 마이너스
- 소형+고변동성(5-10B, ATR≥4%): 최고 그룹

---

## 11. 작업 큐

| 순위 | 작업 | 상태 |
|------|------|------|
| P0 | MINUTE-COLLECTOR-STATUS | Cursor 투입, 결과 대기 |
| P1 | DESK2-MINUTE-REBT | 수집기 확인 후 |
| P2 | DESK5-CARD-BT | P1 후 |
| P3 | OVERLAP-GUARD 구현 | CEO 정책 후 |
| P4 | REGIME-FILTER 구현 | CEO 승인 후 |
| P5 | DESK1-LIVE-PREP | 월요일 09:00 전 |
| P6 | index_daily OHLC=0 재수집 | CEO 승인 후 |
| P7 | PRD 기획서 | CEO 원본 후 |
| P8 | 아키텍처 v1.2 | P7 후 |
| P9 | report/ 커밋 | 정책 후 |
| P10 | DRY_RUN → LIVE | 전체 최적화 후 |

---

## 12. CEO 결정 대기

1. DESK 간 중복 매수: 전 시스템 1포지션 vs DESK당 1포지션
2. 레짐 기반 DESK2 진입 제한 여부
3. 레짐 전환 방어 모드 (48h 축소) 여부
4. strategy_cards 61, 62 처리
5. index_daily OHLC=0 재수집 승인

---

## 13. 실패 교훈 (반복 금지)

1. 대시보드 덮어쓰기 (2/20): 레거시 UI 교체 금지. 별도 경로.
2. DESK2 분봉 -23%: 분봉 최적화 없이 라이브 금지.
3. 프로모션 불완전: min_profit_pct만 체크.
4. DESK 간 중복: 19개 종목 동시 진입.

---

## 14. 핵심 파일 경로

| 구분 | 경로 |
|------|------|
| FastAPI | backend/app/main.py |
| 파이프라인 | backend/app/services/trading/v4_pipeline_orchestrator.py |
| 전략 엔진 | backend/app/services/trading/strategy_engine.py |
| 리스크 | backend/app/services/trading/risk_manager.py |
| 주문 | backend/app/services/trading/order_executor.py |
| 포지션 | backend/app/services/trading/position_manager.py |
| 프로모션 | backend/app/services/trading/split_transfer_engine.py |
| 라이프사이클 | backend/app/services/trading/lifecycle.py |
| 펀드 | backend/app/services/fund/ |
| 어댑티브 | backend/app/services/adaptive/ |
| 레짐 | backend/app/services/market/regime_detector.py |
| 백테스트 | scripts/backtest/backtest_engine_v2.py |
| 분봉수집 | backend/app/services/data_pipeline/collector_minute.py |
| 호가수집 | scripts/collection/orderbook_collector.py |
| DESK추천API | backend/app/api/v4_desk_recommend.py |
| CLAUDE.md | ./CLAUDE.md |
| cursor rules | .cursor/rules/kis-v41-rules.md |

---

## 15. 커밋 로그

| 해시 | 날짜 | 내용 |
|------|------|------|
| 556ddb17 | 2026-02-23 | BT-ENGINE-UPGRADE + REGIME-BACKFILL |
| d0a09050 | 2026-02-22 | DESK-RECOMMEND: 종목추천 + API |
| b61e68e1 | 2026-02-22 | DASH-FIX: nginx API key |
| 573d1ca8 | 2026-02-21 | DESK1 scalping data infra |

---

## 16. 문서 구조

Private (/root/kis-autotrade-v4/docs/):
```
docs/
├── CONTEXT.md                  ← 이 파일 (마스터 원본)
├── architecture/
│   └── v41-architecture-v1.1.md
├── handover/
│   ├── HANDOVER-V50-20260214.md
│   └── HANDOVER-V60-20260223.md
└── plan/
    ├── README.md               (CEO 원본 대기)
    ├── PRD-v1.0-original.md    (예정)
    └── PRD-v1.1-current.md     (예정)
```

Public (project-docs/kis-autotrade-v4/):
위 구조와 동일. sync_kis.sh로 자동 동기화.

Public URL:
https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CONTEXT.md

---

## 17. 새 AI 세션 시작

이 CONTEXT.md를 읽은 후:
1. 절대 규칙 12조 + Cursor 규칙 숙지
2. 현재 상태(섹션 7) 기준값 사전 확인
3. 작업 큐(섹션 11) 우선순위 확인
4. CEO 결정 대기(섹션 12) 확인
5. 실패 교훈(섹션 13) 숙지
6. 상세 필요 시 architecture/, handover/ 참조

---

## 18. 동기화

```bash
bash /root/project-docs/scripts/sync_kis.sh
```
