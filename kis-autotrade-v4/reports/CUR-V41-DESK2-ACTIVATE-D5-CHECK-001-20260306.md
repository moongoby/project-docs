# T-168 DESK2 카드 활성화 + DESK3 풀 급증 원인 + D5 기록 이상 점검

**Task ID**: T-168
**날짜**: 2026-03-06
**작성자**: claudebot
**우선순위**: P0-CRITICAL

---

[인계 확인]
직전 완료: T-163D
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: D-001, D-002
strategy_cards: 전체 56건 (desk별 ACTIVE 확인)
open_positions: 미조회 (본 태스크 범위 외)

---

## 1. DESK2 카드 비활성 원인 확인

### 조회 쿼리
```sql
SELECT card_id, strategy_name, desk_id, is_active, created_at, updated_at
FROM strategy_cards WHERE desk_id='2' ORDER BY card_id
```

### 결과: 16건 전부 is_active=false

| card_id | strategy_name | is_active | updated_at |
|---------|--------------|-----------|------------|
| 6 | DESK2_데일리_class_a | false | 2026-02-24 11:37:35 |
| 7 | DESK2_종가매매_class_c | false | 2026-02-24 11:37:35 |
| 14 | DESK2_장초반레인지돌파 | false | 2026-02-24 11:37:35 |
| 15 | DESK2_VWAP회귀 | false | 2026-02-24 11:37:35 |
| 16 | DESK2_갭상승후하락베팅 | false | 2026-02-24 11:37:35 |
| 17 | DESK2_볼린저밴드돌파 | false | 2026-02-24 11:37:35 |
| 18 | DESK2_RSI역추세 | false | 2026-02-24 11:37:35 |
| 19 | DESK2_거래량스파이크 | false | 2026-02-24 11:37:35 |
| 20 | DESK2_변동성확대 | false | 2026-02-24 11:37:35 |
| 21 | DESK2_D01_3분봉_20선눌림목 | false | 2026-02-24 11:37:35 |
| 22 | DESK2_S05_거래량점화 | false | 2026-02-24 11:37:35 |
| 23 | DESK2_M01_오픈레인지돌파 | false | 2026-02-24 11:37:35 |
| 24 | DESK2_L01_VWAP반등 | false | 2026-02-24 11:37:35 |
| 25 | DESK2_M00_시초첫3분봉고가돌파 | false | 2026-02-24 11:37:35 |
| 26 | DESK2_M001_3분봉종합눌림확인 | false | 2026-02-24 11:37:35 |
| 27 | DESK2_M002_AbsoluteZero_종가매매 | false | 2026-02-24 11:37:35 |

**원인 분석**: updated_at이 모두 `2026-02-24 11:37:35`로 동일 → 이 시각에 일괄 비활성화된 것으로 추정. T-125 DESK2 멀티컨디션 Phase A 작업(2026-02-24) 당시 일괄 비활성화된 후 복구되지 않은 것으로 판단됨.

---

## 2. DESK2 카드 전체 활성화 (CEO 승인 완료)

### 실행 쿼리
```sql
UPDATE strategy_cards SET is_active=true, updated_at=NOW() WHERE desk_id='2' AND is_active=false
```

### 결과
- **변경 건수: 16건** (전체 DESK2 카드 16건 모두 활성화)
- 실행 시각: 2026-03-06 10:57:37 KST

### 활성화 후 상태 확인
16건 전부 `is_active=True`, `updated_at=2026-03-06 10:57:37` 확인 완료.

---

## 3. DESK3 풀 급증 원인 분석 (306건 vs 기존 106건)

### 3a. 상태별 집계
```
status='ACTIVE', COUNT=306
MIN(created_at)=2026-03-03 20:34:09
MAX(created_at)=2026-03-05 15:40:02
```

### 3b. 일자별 트렌드
| 날짜 | 추가 건수 |
|------|----------|
| 2026-03-03 | 106건 |
| 2026-03-04 | 100건 |
| 2026-03-05 | 100건 |
| **합계** | **306건** |

### 3c. source 분포
| source | 건수 |
|--------|------|
| SCAN | 300건 |
| DESK4_PROMOTE | 6건 |

### 원인 분석
- **정상 동작으로 확인됨**. 2026-03-03부터 일별 SCAN이 활성화되어 매일 약 100건씩 추가됨.
- 기존 106건(03-03 초기 스캔) + 03-04 100건 + 03-05 100건 = **306건** 누적
- DESK4_PROMOTE 6건: DESK4에서 승격된 종목 (정상)
- 비정상 데이터 없음. 상태는 모두 'ACTIVE'

---

## 4. D5 pnl=0 원인 분석

### 4a. 2026-03-02 이후 D5 거래 샘플 (10건)

| id | ticker | entry_price | exit_price | pnl_pct | cost_pct | blocking_layer | blocking_reason |
|----|--------|-------------|------------|---------|----------|---------------|-----------------|
| 2 | 828016 | NULL | NULL | NULL | 0.47 | SIGNAL_COMBO | 신호 조합 미통과: D5 (1/2) |
| 9 | 529671 | NULL | NULL | NULL | 0.47 | GATE | 반등확인 게이트 미통과: D5 (1조건) |
| 16 | 240762 | NULL | NULL | NULL | 0.47 | L3.3_SUPPLY | 수급 차단: synthetic_BLOCK |
| 23 | 693141 | NULL | NULL | NULL | 0.47 | L3.3_SUPPLY | 수급 차단: synthetic_BLOCK |
| 30 | 288394 | NULL | NULL | NULL | 0.47 | L3.3_SUPPLY | 수급 차단: synthetic_BLOCK |
| ... | ... | ... | ... | ... | ... | ... | ... |

### 4b. 전체 D5 통계
- **total=29건**, pnl_zero=1, pnl_pos=0, pnl_neg=0, avg_pnl=0
- 최초 거래: 2026-03-02 08:50:02
- 최근 거래: 2026-03-06 08:50:06

### 4c. 최근 D5 거래 (2026-03-06)
```
id=159, ticker=000270, blocking_layer=ATR_NETRR
  → ATR NetR:R 미달: 1.50 < 2.0 (SL=0.41%, TP=1.21%)

id=157, ticker=125703, blocking_layer=L3.1_FUNNEL
  → FunnelScore 미달: 0.241 < 0.4
```

### 원인 분석
- **pnl=0(NULL)은 정상 동작**: v4_mock_trades에 approved=false 거부 시그널이 기록됨. 실제 체결이 없어 entry_price, exit_price, pnl_pct가 NULL로 남음.
- 29건 전부 `approved=false` → 실제 매매 미실행
- blocking_layer 분포: L3.3_SUPPLY(synthetic_BLOCK), L3.1_FUNNEL(FunnelScore 미달), ATR_NETRR(R:R 미달), SIGNAL_COMBO, GATE
- 특히 T-163D 적용 후 `synthetic_BLOCK` 조건이 다수 차단 → 필터링 정상 작동
- **D5는 정상. pnl=0이 아니라 pnl=NULL(미체결 시그널 로그)**

---

## 5. D5 전략 활성 상태

### 5a. DESK5 카드 현황
| card_id | strategy_name | is_active |
|---------|--------------|-----------|
| 10 | DESK5_장기스윙_class_f | True |
| 12 | DESK5_가치투자 | True |
| 13 | DESK5_성장주모멘텀 | True |
| 54 | DESK5_배당포착 | True |
| 55 | DESK5_계절성추세 | True |
| 56 | DESK5_거시경제테마 | True |
| 57 | DESK5_섹터리더십 | True |
| 58 | DESK5_퀄리티팩터 | True |
| 59 | DESK5_저변동성 | True |
| 60 | DESK5_모멘텀팩터 | True |

**10건 전부 is_active=True** → 정상

### 5b. 전체 DESK 카드 요약
| desk_id | 전체 | 활성 |
|---------|------|------|
| 1 | 10 | 10 |
| 2 | 16 | **16** (방금 활성화) |
| 3 | 11 | 11 |
| 4 | 9 | 9 |
| 5 | 10 | 10 |

---

## 요약

| 항목 | 상태 | 조치 |
|------|------|------|
| DESK2 카드 비활성 | 2026-02-24 일괄 비활성화 후 방치 | 16건 활성화 완료 |
| DESK3 풀 306건 | 정상: 일별 SCAN 누적 (100건/일) | 이상 없음 |
| D5 pnl=0 | approved=false 미체결 시그널 로그 | 정상 동작 확인 |
| D5 활성 상태 | 10건 모두 is_active=True | 이상 없음 |
