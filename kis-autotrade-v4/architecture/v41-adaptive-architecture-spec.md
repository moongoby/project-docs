# KIS AutoTrade V4.1 — 적응형 자동매매 시스템 아키텍처 기술서

**문서 버전:** V4.1  
**작성일:** 2026-02-13  
**작성자:** Claude (Architecture Lead)  
**승인자:** 대표님 (CEO)  
**변경 이력:**
- V4.0 (2026-01) — 최초 설계
- V4.1 (2026-02-13) — GPT 5.2 Pro 외부 리뷰 반영, P0 리스크 보완, 로드맵 재배치

---

## 1. V3.0 → V4.0 → V4.1 진화 핵심

V3.0은 "잘 설계된 정적 시스템"이었습니다. V4.0에서 "시장에 적응하는 살아있는 시스템"으로 진화했고, V4.1에서는 **"실전 장애에서도 자금을 지키는 시스템"**으로 안전성을 강화했습니다.

V4.0 → V4.1 핵심 변경 사항:
- FundPool DB 기반 진실(Source of Truth) 원칙 확립
- 주문 멱등성(idempotency_key) 제도화
- risk_manager 2계층 분리 (CriticalRiskKernel + Full RiskManager)
- position_manager fallback 청산 경로 통제 장치
- 운영 최소 지표 4종 조기 도입 (Phase 3)
- PricePoller staleness/burst 제한 스펙 고정
- 경량 Fault Injection 도입 (Phase 5)

추가된 3대 핵심 엔진은 V4.0과 동일: **Market Regime Detector(시장 레짐 감지)**, **System Orchestrator(시스템 지휘자)**, **Adaptive Engine(적응 엔진)**

---

## 2. V4.1 전체 계층도

```
╔══════════════════════════════════════════════════════════════════════╗
║                    V4.1 SYSTEM HIERARCHY                             ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌────────────────────────────────────────────────────────────┐     ║
║  │              LAYER 0 — SYSTEM ORCHESTRATOR                   │     ║
║  │              (system_orchestrator)                            │     ║
║  │  시스템 전체 상태 관리, 모듈 간 실행 순서 보장               │     ║
║  │  상태 머신: IDLE → PRE_MARKET → READY → TRADING             │     ║
║  │            → CLOSING → POST_MARKET → IDLE                   │     ║
║  │  장애 감지, 복구, heartbeat 관리                             │     ║
║  │  ★ V4.1: 상태 전이 불변조건(Invariants) 코드 레벨 강제     │     ║
║  └──────┬───────────────────────────────────────┬───────────────┘     ║
║         │                                       │                     ║
║         ▼                                       ▼                     ║
║  ┌──────────────────┐                ┌──────────────────────┐        ║
║  │  LAYER 1-A        │                │  LAYER 1-B            │        ║
║  │  MARKET REGIME    │                │  MARKET CALENDAR      │        ║
║  │  DETECTOR         │                │  FOMC, 만기일, IPO    │        ║
║  │  regime + mood    │                │  trading_restriction  │        ║
║  └────────┬──────────┘                └──────────┬────────────┘        ║
║           └──────────────┬───────────────────────┘                     ║
║                          ▼                                             ║
║  ┌────────────────────────────────────────────────────────────┐       ║
║  │              LAYER 2 — COMMAND CENTER                        │       ║
║  │  chief_analyst / fund_commander (universe 버전화, DB=SoT)   │       ║
║  └───────────┬──────────────────────┬───────────────────────────┘       ║
║              ▼                      ▼                                   ║
║  ┌────────────────────────────────────────────────────────────┐       ║
║  │  LAYER 3 — MARKET BRAIN (5 DESK)                            │       ║
║  │  today_universe (CLASS + confidence + regime_context)       │       ║
║  └────────────────────────┬─────────────────────────────────────┘       ║
║                            ▼                                             ║
║  ┌────────────────────────────────────────────────────────────┐       ║
║  │  LAYER 4 — STRATEGY ENGINE (idempotency_key 중복 차단)      │       ║
║  └────────────────────────┬─────────────────────────────────────┘       ║
║                            ▼                                             ║
║  ┌────────────────────────────────────────────────────────────┐       ║
║  │  LAYER 5 — EXECUTION CORE (FundPool DB=SoT, 2계층 리스크)  │       ║
║  └────────────────────────┬─────────────────────────────────────┘       ║
║                            ▼                                             ║
║  ┌────────────────────────────────────────────────────────────┐       ║
║  │  LAYER 6 — POSITION LIFECYCLE (fallback 청산, SELL_FAILED)  │       ║
║  └────────────────────────┬─────────────────────────────────────┘       ║
║                            ▼                                             ║
║  ┌────────────────────────────────────────────────────────────┐       ║
║  │  LAYER 7 — ADAPTIVE ENGINE (레짐 조건부, 지수감쇠)          │       ║
║  └──────────────────────────────────────────────────────────────┘       ║
║  ┌────────────────────────────────────────────────────────────┐       ║
║  │  INFRA — DATA PIPELINE (PricePoller staleness/burst, FI)    │       ║
║  └──────────────────────────────────────────────────────────────┘       ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## 3. LAYER 0 — SYSTEM ORCHESTRATOR

- 상태 머신: IDLE → PRE_MARKET(07:55) → READY(08:50) → TRADING(09:00) → CLOSING(15:20) → POST_MARKET(15:30) → IDLE
- 각 상태별 허용 동작, V4.1 상태 전이 불변조건(Invariants), TRADING 60초 사이클 내 실행 순서, recovery_check(FundPool DB 재구성 포함), heartbeat, 축소 운영(DEGRADED) 모드 정리

*(본문 상세 다이어그램은 상동 — 생략)*

---

## 4. LAYER 1-A — MARKET REGIME DETECTOR

- 5대 레짐: STRONG_TREND_UP, MILD_TREND_UP, SIDEWAYS, MILD_TREND_DOWN, STRONG_TREND_DOWN
- V4.1 레짐 전환 히스테리시스 (상향 3일/하향 2일)
- 레짐 판정 지표, 데스크/전략 파라미터 매핑

---

## 5. LAYER 1-B — MARKET CALENDAR

- 특수일 유형(FOMC, 만기일, MSCI/FTSE, 락업해제, 배당락, 연휴 전후 등) 및 대응
- 복수 이벤트 겹침 시 합산 규칙, v4_market_calendar 스키마

---

## 6. LAYER 5 — EXECUTION CORE (V4.1 강화)

- FundPool DB=SoT, rebuild_from_db
- ReservationState 상태 머신 (RESERVED → ORDER_SUBMITTED → FILLED/CANCELLED/FAILED 등)
- idempotency_key UNIQUE, v4_order_requests
- FundPool 연성 배분, risk_manager 2계층(CriticalRiskKernel + Full RiskManager), ReentryGuard

---

## 7. LAYER 6 — POSITION LIFECYCLE (V4.1 강화)

- fallback 청산 경로 (3통제: 청산 전용+긴급 모드, 동일 레이트리미터, 동일 기록 체계)
- SELL_FAILED 재시도 전략 (지정가 → IOC → 시장가 → 알림)
- 포지션 승격 시 손익 기준

---

## 8. LAYER 7 — ADAPTIVE ENGINE (V4.1 강화)

- 스코어링 가중치: V4.1 지수감쇠(4주 가중 + 12주 약가중), 레짐 조건부 가중치
- 전략 파라미터 롤링 최적화, 데스크 성과 배분, Trade Analyzer, 과적합 방지

---

## 9. INFRA — DATA PIPELINE V4.1

- DataProvider 추상화, PricePoller (price/ts/source/staleness_ms, burst 제한)
- data_quality_tracker, 운영 최소 지표 4종, 경량 Fault Injection

---

## 10. 장 시작 노이즈 구간 처리

- 시간대별 신뢰도(NOISE/INITIAL/DEVELOPING/RELIABLE/CLOSING), CLASS-B 확인봉

---

## 11. 테마 분석 현실적 구현

- 테마-종목 매핑, theme_activity_score 시장 데이터 기반

---

## 12. mood 연속값 체계

- mood_score 0~100, 라벨 매핑, mood_modifier, 장중 악화 시 포지션 대응

---

## 13. 사용자 개입 관리 모드

- AUTO_LOCKED / AUTO_ADVISORY / MANUAL_ASSIST

---

## 14. today_universe 버전화 (V4.1)

- universe_version 메타데이터, inputs_hash, v4_universe_version 테이블

---

## 15. V4.1 DB 스키마 전체

- 신규: v4_order_requests, v4_reservations, v4_universe_version
- 기존 ALTER: v4_system_heartbeat, v4_scoring_weights, v4_trade_analysis
- DDL, 인덱스, 보관 정책

---

## 16. V3.0 → V4.0 → V4.1 변경 요약

- 항목별 비교 테이블 (시스템 상태, 레짐, 자금, 리스크, DB 등)

---

## 17. V4.1 단계별 구현 로드맵

- Phase 0~6 진행률, V4.1 반영 항목(Phase 2-C, 3, 4, 5)

---

## 18. V4.1 설계 원칙 (불변)

- FundPool invariant, Lock, 레거시 보호, Graceful degradation, Soft allocation, 멱등성, 추적 가능성, 비대칭 방어

---

## 19. 문서 변경 이력

- V4.0 요약, V4.1 P0/P1/P2 변경 목록, 설계 원칙 추가, DB 변경 요약

---

*본 요약본은 전체 기술서의 섹션 제목과 핵심만 수록한 인덱스입니다.  
전체 ASCII 다이어그램·코드 블록·테이블은 원본 문서(동일 제목, 19절 완전판)를 참조하세요.*
