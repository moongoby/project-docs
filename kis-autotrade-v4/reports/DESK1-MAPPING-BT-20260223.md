# DESK1-MAPPING-BT 최종 보고서 (2026-02-23)

## 작업 개요
- **작업명**: DESK1-MAPPING-BT
- **서버**: [SERVER-IP]
- **목적**: DESK1 실매매 전제조건 — v4_desk_strategy_mapping 매핑 확인·보강 후 DESK1 전용 백테스트 수행 및 실매매 투입 판단
- **절대 규칙 준수**: kis-v41-* 재시작 없음, strategy_cards ALTER/DROP/DELETE 없음, v4_positions 직접 수정 없음, backtest_engine_v2.py 수정 없음, .env/.bak 커밋 없음

---

## Phase A — 현황 파악 결과

### 1. v4_desk_strategy_mapping 테이블 구조
| 컬럼 | 타입 | 비고 |
|------|------|------|
| mapping_id | integer PK | serial |
| desk_id | integer NOT NULL | |
| card_id | integer NOT NULL | |
| stage_id | integer NOT NULL | default 1 |
| allocation_pct | numeric(5,2) NOT NULL | default 0 |
| priority | integer NOT NULL | default 0 |
| is_active | boolean NOT NULL | default true |
| valid_from, valid_until | timestamp | |
| created_at, updated_at | timestamp | |
| UNIQUE | (desk_id, card_id, stage_id) | |

### 2. 기존 매핑 (DESK1)
**DESK1 매핑은 이미 10건 존재함.**
| desk_id | card_id | stage_id | allocation_pct | is_active |
|---------|---------|----------|----------------|-----------|
| 1 | 5 | 1 | 1.50 | t |
| 1 | 38, 39, 40, 41, 42, 43, 44, 45, 46 | 1 | 1.50 each | t |

### 3. DESK1 카드 목록 (strategy_cards, desk_id='1')
| card_id | strategy_name | is_active | is_live | **backtest_compatible** |
|---------|---------------|-----------|---------|-------------------------|
| 5 | DESK1_스캘핑_class_b | t | t | **f** |
| 38 | DESK1_초단타모멘텀 | t | t | **f** |
| 39 | DESK1_갭메우기 | t | t | **f** |
| 40 | DESK1_뉴스반응스캘핑 | t | t | **f** |
| 41 | DESK1_S01_호가불균형 | t | t | **f** |
| 42 | DESK1_S02_고래추적 | t | t | **f** |
| 43 | DESK1_S03_스프레드갭 | t | t | **f** |
| 44 | DESK1_S04_플래시크래시 | t | t | **f** |
| 45 | DESK1_M03_이격도숏 | t | t | **f** |
| 46 | DESK1_H01_시장센서 | t | t | **f** |

### 4. 백테스트 엔진 매핑 로드 방식 (backtest_engine_v2.py)
- `_load_strategy_from_db(stage, desk_strategies)`:
  - `desk_strategies`가 있으면: `strategy_cards` + `v4_desk_strategy_mapping` JOIN, **WHERE s.backtest_compatible = true**
  - 조건 미충족 시 0건 → **config.py fallback** (DESK1 alloc=0%)

---

## 원인 정리 (DESK1 거래 0건)

1. **v4_desk_strategy_mapping**: DESK1×10카드 매핑 **이미 존재** (INSERT 0건 추가됨 — ON CONFLICT DO NOTHING).
2. **실제 장애**: DESK1 카드 10건 전부 **backtest_compatible = false**.
   - 엔진 쿼리 `AND s.backtest_compatible = true` 때문에 위 카드들이 모두 제외됨.
   - DB 로드 결과 0건 → "DB에 활성 전략 매핑 없음" → **config.py fallback** → DESK1 alloc=0% → DESK1 거래 0건.

---

## Phase B — INSERT 결과

- `INSERT INTO v4_desk_strategy_mapping (desk_id, card_id, ...) ON CONFLICT (desk_id, card_id, stage_id) DO NOTHING` 실행.
- **INSERT 0 0** — 기존 10건과 충돌하여 추가 삽입 없음. 매핑 현황 유지.

---

## Phase C — 백테스트 실행 결과

- **실행 명령**: `run_backtest.py --start 20251101 --end 20260221 --capital 5000000 --name DESK1-MAPPING-BT-20260223 --engine v2 --desk-strategies '[{"desk_id":1,"card_id":5},...,46}]'`
- **실제 동작**: DB에서 DESK1 카드 0건 로드(backtest_compatible=false) → config fallback → **5 DESK 전체(config)** 로 실행됨. 세션명만 `V2_DESK1-MAPPING-BT-20260223`이며, **DESK1 전용 백테스트는 아님**.
- **DESK1 전용 백테스트**를 수행하려면:
  - **권장**: strategy_cards에서 DESK1 카드 10건(5, 38~46)에 대해 **backtest_compatible = true** 로 UPDATE (kis-v41-rules: strategy_cards UPDATE는 **CEO 승인 후**에만).
  - backtest_engine_v2.py 수정(backtest_compatible 조건 완화)은 **규칙상 금지**이므로 비권장.

---

## Phase D — 결과 분석 (DESK1 전용 세션 없음)

- DESK1 전용 백테스트가 수행되지 않았으므로, **DESK1 카드별/전체 승률·PnL 요약 테이블은 해당 없음**.
- 현재 실행된(또는 완료된) 세션은 config 기반 5 DESK 백테스트이며, DESK1 alloc=0%라 DESK1 거래는 0건.

---

## Phase E — 실매매 투입 판단

| 기준 | 결과 |
|------|------|
| 거래 10건 이상 & 승률 40% 이상 | **해당 없음** — DESK1 전용 백테스트 미실행 |
| 거래 0건 | **DESK1 진입 로직 점검 필요** — 원인: backtest_compatible=false로 DB 로드 0건 → config fallback |
| 판단 | **DESK1 실매매 투입 보류**. CEO 승인 하에 DESK1 카드 10건 backtest_compatible=true 설정 후 **재백테스트** 수행 권장. |

---

## Phase F — DB 무결성

| 항목 | 확인 값 |
|------|----------|
| strategy_cards | 62건 유지 |
| v4_positions (OPEN) | 5건 유지 (직접 수정 없음) |
| v4_desk_strategy_mapping | DESK1 10건 유지, INSERT 0건 추가 |

---

## 권장 후속 조치

1. **CEO 승인 후** strategy_cards UPDATE:
   - `UPDATE strategy_cards SET backtest_compatible = true WHERE desk_id = '1' AND card_id IN (5, 38, 39, 40, 41, 42, 43, 44, 45, 46);`
2. 동일 조건으로 **DESK1 전용 백테스트 재실행** (run_backtest.py --engine v2 --desk-strategies '[...]').
3. 재실행 결과에 따라 Phase E 기준으로 실매매 소액 테스트/보류 결정.

---

## 발행·동기화

- 보고서 경로: `/root/kis-autotrade-v4/report/v41/DESK1-MAPPING-BT-20260223.md`
- 발행: `bash /root/project-docs/scripts/publish_report.sh DESK1-MAPPING-BT`
- 동기화: `bash /root/project-docs/scripts/sync_kis.sh`
