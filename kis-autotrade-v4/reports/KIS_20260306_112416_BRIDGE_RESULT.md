---
project: KIS V4.1
task_id: T-168R
completed_at: 2026-03-06T11:40:00+09:00
---

# T-168R 실행 결과: DESK2 카드 활성화 상태 확인

## 지시서 원문
Task ID: T-168R
제목: DESK2 카드 활성화 상태 확인 (T-168 축소 재발행)
서버: 211 (kis-autotrade-v4)
우선순위: P1-HIGH
예상 시간: 8분
의존성: 없음

배경: T-168이 20분 타임아웃 종료. 핵심 쿼리만 축소 실행.

---

## 실행 내용 및 결과

### Step 0: strategy_cards 스키마 확인

지시서의 `desk` 컬럼이 실제로는 `desk_id`임을 발견. 스키마 먼저 확인 후 쿼리 수정.

```
=== strategy_cards Schema ===
('card_id', 'bigint')
('user_id', 'bigint')
('account_id', 'bigint')
('strategy_name', 'character varying')
('strategy_type', 'character varying')
('strategy_params', 'jsonb')
('allocated_amount', 'numeric')
('max_stocks', 'integer')
('is_live', 'boolean')
('is_active', 'boolean')
('desk_id', 'character varying')
('created_at', 'timestamp with time zone')
('updated_at', 'timestamp with time zone')
('entry_rules', 'jsonb')
('exit_rules', 'jsonb')
('risk_params', 'jsonb')
('buy_phases', 'jsonb')
('sell_phases', 'jsonb')
('promotion_rules', 'jsonb')
('demotion_rules', 'jsonb')
('backtest_compatible', 'boolean')
('priority', 'integer')
('version', 'integer')
```

**발견**: `desk` 컬럼 없음. 실제 컬럼명은 `desk_id` (VARCHAR). 값은 '1','2','3','4','5' 숫자 문자열.
DESK2 = desk_id = '2'

---

### Step 1: DESK별 전략카드 활성/비활성 현황

```sql
SELECT desk_id, is_active, COUNT(*) FROM strategy_cards GROUP BY desk_id, is_active ORDER BY desk_id, is_active
```

```
=== Strategy Cards by Desk ===
('1', True, 10)
('2', True, 16)
('3', True, 11)
('4', True, 9)
('5', True, 10)
(None, False, 1)
(None, True, 3)
```

**해석**:
- DESK1(desk_id='1'): 10개 전체 활성
- DESK2(desk_id='2'): 16개 전체 활성
- DESK3(desk_id='3'): 11개 전체 활성
- DESK4(desk_id='4'): 9개 전체 활성
- DESK5(desk_id='5'): 10개 전체 활성
- desk_id=NULL: 1개 비활성, 3개 활성 (레거시/미분류)
- **총합**: 60개 활성, 1개 비활성

---

### Step 2: DESK2 카드 상세 (desk_id='2')

```sql
SELECT card_id, strategy_name, desk_id, is_active, strategy_type, entry_rules->>'conditions' as conditions, created_at
FROM strategy_cards WHERE desk_id='2' ORDER BY is_active DESC, card_id LIMIT 20
```

```
=== desk_id=2 Cards Detail (DESK2) ===
(6,  'DESK2_데일리_class_a',              '2', True, 'BUILTIN', None, 2026-02-20 19:17:40.883749+09:00)
(7,  'DESK2_종가매매_class_c',            '2', True, 'BUILTIN', None, 2026-02-20 19:17:40.883749+09:00)
(14, 'DESK2_장초반레인지돌파',            '2', True, 'BUILTIN', None, 2026-02-20 21:25:16.959207+09:00)
(15, 'DESK2_VWAP회귀',                   '2', True, 'BUILTIN', None, 2026-02-20 21:25:16.959207+09:00)
(16, 'DESK2_갭상승후하락베팅',            '2', True, 'BUILTIN', None, 2026-02-20 21:25:16.959207+09:00)
(17, 'DESK2_볼린저밴드돌파',             '2', True, 'BUILTIN', None, 2026-02-20 21:25:16.959207+09:00)
(18, 'DESK2_RSI역추세',                  '2', True, 'BUILTIN', None, 2026-02-20 21:25:16.959207+09:00)
(19, 'DESK2_거래량스파이크',             '2', True, 'BUILTIN', None, 2026-02-20 21:25:16.959207+09:00)
(20, 'DESK2_변동성확대',                 '2', True, 'BUILTIN', None, 2026-02-20 21:25:16.959207+09:00)
(21, 'DESK2_D01_3분봉_20선눌림목',       '2', True, 'BUILTIN', None, 2026-02-20 21:25:16.959207+09:00)
(22, 'DESK2_S05_거래량점화',             '2', True, 'BUILTIN', None, 2026-02-20 21:25:16.959207+09:00)
(23, 'DESK2_M01_오픈레인지돌파',         '2', True, 'BUILTIN', None, 2026-02-20 21:25:16.959207+09:00)
(24, 'DESK2_L01_VWAP반등',              '2', True, 'BUILTIN', None, 2026-02-20 21:25:16.959207+09:00)
(25, 'DESK2_M00_시초첫3분봉고가돌파',   '2', True, 'BUILTIN', None, 2026-02-20 21:25:16.959207+09:00)
(26, 'DESK2_M001_3분봉종합눌림확인',    '2', True, 'BUILTIN', None, 2026-02-20 21:25:16.959207+09:00)
(27, 'DESK2_M002_AbsoluteZero_종가매매','2', True, 'BUILTIN', None, 2026-02-20 21:25:16.959207+09:00)
```

**해석**:
- DESK2 카드 총 16개, 전부 is_active=True
- strategy_type=BUILTIN (모두 동일)
- entry_rules→conditions = NULL (멀티컨디션 매처 미연결 상태)
- 최초 생성: 2026-02-20 (T-125 이전)
- card_id 6,7은 2020-02-20 첫 배치, 14~27은 같은 날 두 번째 배치

---

### Step 3: DESK2 조건 파일 존재 확인

```bash
ls -la /root/kis-autotrade-v4/backend/app/services/desk2_conditions/
```

```
=== DESK2 Condition Files ===
total 172
drwxrwxr-x  3 claudebot claudebot  4096 Mar  6 10:15 .
drwxrwxrwx 38 go100user go100user  4096 Mar  6 11:05 ..
-rw-rw-r--  1 claudebot claudebot  7557 Mar  6 10:13 axis_mask.py
-rw-rw-r--  1 claudebot claudebot  3824 Mar  5 19:35 base_condition.py
-rw-rw-r--  1 claudebot claudebot  5542 Mar  5 19:36 c1_ul_expected.py
-rw-rw-r--  1 claudebot claudebot  7101 Mar  5 19:38 c2_prev_ul.py
-rw-rw-r--  1 claudebot claudebot  7097 Mar  6 09:52 c3_open_strength.py
-rw-rw-r--  1 claudebot claudebot  8698 Mar  6 09:53 c4_intraday_surge.py
-rw-rw-r--  1 claudebot claudebot 10429 Mar  6 09:54 c5_theme_simultaneous.py
-rw-rw-r--  1 claudebot claudebot  6457 Mar  5 19:36 c6_close_strong.py
-rw-rw-r--  1 claudebot claudebot 14751 Mar  6 10:13 c7_new_stock_detect.py
-rw-rw-r--  1 claudebot claudebot  5834 Mar  6 10:14 condition_registry.py
-rw-rw-r--  1 claudebot claudebot 20501 Mar  5 22:05 c_s1_volume_pullback.py
-rw-rw-r--  1 claudebot claudebot 18431 Mar  5 21:54 dcs_evaluator.py
-rw-rw-r--  1 claudebot claudebot  8972 Mar  6 10:15 desk2_multi_condition_matcher.py
-rw-rw-r--  1 claudebot claudebot  1516 Mar  6 10:14 __init__.py
drwxrwxr-x  2 claudebot claudebot  4096 Mar  6 10:17 __pycache__
-rw-rw-r--  1 claudebot claudebot  4812 Mar  6 10:14 signal_matcher.py
```

**해석**:
- C1~C7 모두 존재: c1_ul_expected.py, c2_prev_ul.py, c3_open_strength.py, c4_intraday_surge.py, c5_theme_simultaneous.py, c6_close_strong.py, c7_new_stock_detect.py
- 추가 파일: axis_mask.py, base_condition.py, condition_registry.py, c_s1_volume_pullback.py, dcs_evaluator.py, desk2_multi_condition_matcher.py, signal_matcher.py, __init__.py
- 총 15개 파일 (T-125 Phase A 완성 산출물 전부 존재)
- 최신 수정: 2026-03-06 (오늘) c3~c5, c7, axis_mask, desk2_multi_condition_matcher

---

### Step 4: 오늘 모의매매 현황

```sql
SELECT COUNT(*), ROUND(AVG(pnl_pct)::numeric,3) FROM v4_mock_trades WHERE created_at >= '2026-03-06'
```

```
=== Today Mock Trades ===
(11, None)
```

**상세 (v4_mock_trades 실제 컬럼명: id, trade_date, ticker, strategy_id, direction, ...)**:

```sql
SELECT id, ticker, strategy_id, direction, pnl_pct, created_at
FROM v4_mock_trades WHERE created_at >= '2026-03-06' ORDER BY created_at DESC LIMIT 15
```

```
=== Today Mock Trades Detail ===
(164, '001540', 'D-ORB', 'BUY', None, 2026-03-06 08:50:11.257559)
(163, '0005G0', 'D7',    'BUY', None, 2026-03-06 08:50:10.262333)
(162, '001290', 'S1',    'BUY', None, 2026-03-06 08:50:09.367495)
(161, '001275', 'D2',    'BUY', None, 2026-03-06 08:50:08.201959)
(160, '0010E0', 'D4',    'BUY', None, 2026-03-06 08:50:07.397798)
(159, '000270', 'D5',    'BUY', None, 2026-03-06 08:50:06.497681)
(158, '001067', 'D6',    'BUY', None, 2026-03-06 08:50:01.769414)
(157, '125703', 'D5',    'BUY', None, 2026-03-06 08:30:08.586844)
(156, '284915', 'D-ORB', 'BUY', None, 2026-03-06 08:30:07.908985)
(155, '941017', 'D7',    'BUY', None, 2026-03-06 08:30:07.090240)
(154, '804899', 'D6',    'BUY', None, 2026-03-06 08:30:02.624935)
```

**해석**:
- 오늘(2026-03-06) 총 11건 BUY 진입
- 전략: D-ORB×2, D7×2, S1×1, D2×1, D4×1, D5×2, D6×2
- pnl_pct = NULL (미체결 또는 청산 미기록)
- 08:30 배치(4건) + 08:50 배치(7건) - 장전 모의매매로 추정

---

## 종합 진단

| 항목 | 상태 | 비고 |
|------|------|------|
| DESK2 카드 수 | 16개 | card_id 6,7,14~27 |
| DESK2 카드 is_active | 전부 True | 비활성 카드 없음 |
| DESK2 entry_rules.conditions | NULL | 멀티컨디션 미연결 |
| C1~C7 조건 파일 | 전부 존재 | 15개 파일 완비 |
| desk2_multi_condition_matcher.py | 존재 | 2026-03-06 최신 |
| 오늘 mock trade | 11건 (BUY only) | pnl_pct NULL |

### 핵심 발견사항

1. **desk_id 컬럼명 불일치**: 지시서에서 `desk` 컬럼이라 표기했으나 실제는 `desk_id`
2. **DESK2 = desk_id='2'**: 문자열 '2' (숫자 아님)
3. **entry_rules→conditions = NULL**: 모든 DESK2 카드에 멀티컨디션이 연결되지 않음 → C3~C7 조건 파일은 완성됐으나 카드 entry_rules에 아직 주입 미완료
4. **mock trade 청산 미기록**: pnl_pct=NULL → SELL 거래 없거나 청산 로직 미작동

### 다음 액션 제안

- DESK2 카드 entry_rules에 멀티컨디션 매처 연결 (T-125 Phase B 해당)
- mock trade SELL/청산 로직 점검 (pnl_pct NULL 원인 파악)

---

## 스키마 정정 (지시서 대비 실제)

| 지시서 컬럼 | 실제 컬럼 | 비고 |
|------------|---------|------|
| desk | desk_id | VARCHAR, 값: '1'~'5' |
| name | strategy_name | VARCHAR |
| signal_combo | entry_rules (jsonb) | conditions 키가 NULL |
| action (mock trades) | direction | 'BUY'/'SELL' |
| card_id (mock trades) | strategy_id | VARCHAR, 전략 코드 |

---

## 실행 환경
- Python: /root/kis-autotrade-v4/venv/bin/python3
- DB: localhost:5432/kisautotrade (kis_admin)
- 실행 시각: 2026-03-06 11:40 KST
- DB 변경: 없음 (READ ONLY)
- 서비스 재시작: 없음
- strategy_cards 수정: 없음
