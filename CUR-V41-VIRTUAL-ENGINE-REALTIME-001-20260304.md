# CUR-V41-VIRTUAL-ENGINE-REALTIME-001 — V4.1 실시간 가상매매 엔진 개선 및 NXT 확장

> 날짜: 2026-03-04  
> 작업자: Claude Code  
> 상태: COMPLETED

---

## [인계 확인]
직전 완료: CUR-V41-DEDUP-GUARD-001  
현재 단계: Phase Virtual Run 고도화  
CEO 지시 적용: D-001, D-002, D-007  
strategy_cards: 60  
open_positions: 14  

---

## 1. 작업 배경

텔레그램 CRITICAL 알림 수신 (09:01 KST):
- v4_tick_data WS 중단 → 장 시작 직후 자동 복구됨
- v4_orderbook_realtime WS 중단 → 자동 복구됨
- v4_vkospi_daily 2건 실패 → 공공데이터 API T+2 지연으로 조치 불가 (내일 자동 수집 예정)

사용자 요청: V4.1 실시간 가상매매 엔진 확인 + 모든 과정 DB 저장 + NXT 시장 확장

---

## 2. 기존 엔진 문제점 발견

| 문제 | 내용 |
|------|------|
| **synthetic 종목코드** | signal 액션이 임의 6자리 숫자 종목을 생성 → tick 데이터 매칭 불가 |
| **monitor 로직 부재** | 오픈 포지션 조회만 하고 실시간 TP/SL 청산 로직 없음 |
| **백데이터 저장 없음** | 청산 과정의 데이터가 DB에 누적되지 않음 |

---

## 3. 개선 내용

### 3-1. action_signal — 실제 종목코드 사용
- v4_tick_data에서 최근 30분 활성 종목(상위 50개) 조회
- 신호 생성 시 실제 종목코드 + 현재가로 교체
- v4_virtual_trades_full에 신호 전체 기록 (차단 포함)

### 3-2. action_monitor — 실시간 TP/SL 청산 구현
```
전략별 TP/SL:
  D2:    SL 3%,  TP None, timeout 60min
  D4:    SL 1%,  TP 5%,   timeout 60min
  D5:    SL 2.5%,TP None, timeout 60min
  D6/D7: SL 3%,  TP None, timeout 60min
  S1:    SL 3%,  TP None, timeout None
  D-ORB: SL 2.5%,TP 5%,   timeout 60min
```
- v4_tick_data → v4_orderbook_realtime 순서로 현재가 조회
- 청산 시: v4_mock_trades 업데이트 + v4_virtual_trades_full 저장 + exit_events.jsonl 기록

### 3-3. 백데이터용 DB 테이블 신규 생성
```sql
v4_virtual_trades_full       -- 신호~청산 전 과정 (차단 포함, 백데이터 핵심)
v4_virtual_monitor_snapshots -- 1분마다 포지션 가격 궤적 (MFE/MAE 계산용)
```

### 3-4. action_nxt_signal — NXT 시장 확장
- 세션 구분: NXT_AM(08:00~08:50) / NXT_PM(15:40~18:00) / NXT_NIGHT(18:00~20:00)
- 전략: D6, D7, D-ORB, D5 위주
- source 태그: VIRTUAL_NXT_AM / VIRTUAL_NXT_PM / VIRTUAL_NXT_NIGHT

---

## 4. 저장 데이터 체계

```
v4_mock_trades           : 장중 신호 + 청산 기록 (기존)
v4_virtual_trades_full   : 백데이터용 전체 이력 (신규, 차단 포함)
v4_virtual_monitor_snapshots : 1분 가격 궤적 (신규)
reports/daily/{date}/exit_events.jsonl : 청산 이벤트 JSONL
reports/daily/{date}/snapshots.jsonl   : 30분 모니터링 스냅샷 (기존)
/var/log/unified_engine.log            : 1분 monitor 로그
/var/log/unified_engine_nxt.log        : NXT 신호 로그 (신규)
```

---

## 5. Cron 스케줄 (전체)

| 시간 | 액션 | 설명 |
|------|------|------|
| 07:55 | premarket | 장 전 준비 |
| 08:05, 08:30 | nxt_signal (AM) | NXT 오전 시간외 신호 |
| 08:50 | signal | 정규장 신호 생성 |
| 09:00~15:00 (1분) | monitor | 실시간 TP/SL 청산 |
| 15:30 | close | 장 마감 강제청산 |
| 15:45, 16:30, 17:30 | nxt_signal (PM) | NXT 오후 시간외 |
| 16:00~19:00 (1분) | monitor | NXT 포지션 모니터 |
| 18:10, 19:10 | nxt_signal (NIGHT) | NXT 야간 신호 |
| 20:05 | close | NXT 장 마감 청산 |

---

## 6. 테스트 결과

```
[SIGNAL] D6 000087 통과 price=14,190
[SIGNAL] D-ORB 000180 통과 price=1,623
[MONITOR] 000180 [D-ORB] entry=1,623 cur=1,572 pnl=-3.61% → SL(2.5%)
→ 청산 완료: id=77 pnl=-3.61% [SL(2.5%)] → DB+JSONL 저장
```
- v4_mock_trades: exit_price, pnl_pct 저장 ✅
- v4_virtual_trades_full: 8건 (1건 청산) ✅
- exit_events.jsonl: {"ts":..., "ticker":"000180", "pnl_pct":-3.612, "reason":"SL(2.5%)"} ✅

---

## 7. 체크포인트

- [x] 코드 커밋 완료 (run_unified_engine.py 개선)
- [x] DB 테이블 생성 (v4_virtual_trades_full, v4_virtual_monitor_snapshots)
- [x] Cron NXT 확장 등록
- [ ] project-docs 보고서 push
