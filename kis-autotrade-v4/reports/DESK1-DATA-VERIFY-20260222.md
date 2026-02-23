# DESK1-DATA-VERIFY 결과 보고 (스캘핑 데이터 인프라 검증)

**작업일:** 2026-02-22  
**서버:** 211.188.51.113  
**경로:** /root/kis-autotrade-v4  
**작업 성격:** 읽기 전용 검증 (DB/파일 수정 없음)

---

## 사전 확인 결과

| 항목 | 기준 | 결과 |
|------|------|------|
| strategy_cards COUNT | 59 | **59** ✓ |
| v4_positions OPEN | 5 | **5** ✓ |
| kis-v41-api | active | **active (running)** ✓ |
| kis-v41-monitor | active | **active (running)** ✓ |
| kis-v41-scheduler | - | 확인됨 |
| df -h / | - | 41% 사용, 56G 가용 ✓ |

---

## STEP 1: 테이블 존재 및 스키마

- **v4_scalping\***  
  - `v4_scalping_universe` (존재)  
  - `v4_scalping_signals` (존재)  
- **v4_orderbook\***  
  - `v4_orderbook_realtime` (존재)  
- 스키마: `\d` 출력으로 컬럼/인덱스/제약 확인 완료.

---

## STEP 2: 정적 풀 데이터 (v4_scalping_universe)

- **COUNT:** 708행  
- **샘플 10건:** stock_code, stock_name, market, avg_trade_value_20d, avg_atr_pct_20d, close_price 등 정상. created_date 2026-02-21.

---

## STEP 3: 수집기 스크립트

- `scripts/collection/orderbook_collector.py`: 존재, `py_compile` 통과 (PASS)  
- `scripts/collection/scalping_universe_builder.py`: 존재, `py_compile` 통과 (PASS)  

---

## STEP 4: systemd orderbook-collector

- **파일:** `/etc/systemd/system/kis-v41-orderbook-collector.service` 존재 (584 bytes)  
- **내용:** WorkingDirectory/ExecStart/Environment 등 정상, "월요일 장전에 시작" 주석 있음.  
- **상태:** inactive (dead) — 지침상 월요일 장 전 활성화 예정으로 **정상**.

---

## STEP 5: 분봉 수집기

- **kis-v41-minute-collector:** inactive (dead) — 지침상 월요일 장 전 활성화 예정으로 **정상**.

---

## STEP 6: git 상태

- **최근 커밋 (oneline -5):**  
  - b61e68e1 DASH-FIX: fix dashboard API authentication error (nginx X-Internal-API-Key injection)  
  - 4f8fef24 feat: CUR-GO100-STRATEGY-CARD-FIX  
  - 07c03316 feat: CUR-GO100-STRATEGY-INTEGRATE  
  - 573d1ca8 DESK1-DATA: add scalping universe builder, orderbook collector, and signal tables  
  - 1665d40f feat: CUR-GO100-BUNDLE4D ...  
- **브랜치:** phase-2c-command-center (ahead of origin by 109 commits)  
- **변경:** report/GO100-STRATEGY-CARD-FIX-REPORT-20260222.md 수정, scripts/cur_go100_fix_prep.sh 미추적.

---

## 보고 양식 (최종)

```
--- DESK1-DATA-VERIFY 결과 ---
v4_scalping_universe: 존재여부(Y), 행수(708)
v4_orderbook_realtime: 존재여부(Y)
v4_scalping_signals: 존재여부(Y)
orderbook_collector.py: 존재여부(Y), 문법검증(PASS)
scalping_universe_builder.py: 존재여부(Y), 문법검증(PASS)
systemd 서비스 등록: 존재여부(Y), 상태(inactive)
minute-collector 상태: inactive
최근 커밋: (b61e68e1, DASH-FIX: fix dashboard API authentication error (nginx X-Internal-API-Key injection))
strategy_cards COUNT: (59)
v4_positions OPEN: (5)
이슈 사항: 없음
--- 보고 끝 ---
```

---

*테이블/스크립트/서비스는 모두 존재하며, 미존재 시 생성하지 않고 보고만 함. DB 및 파일 수정 없이 검증만 수행.*
