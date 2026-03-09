# CUR-V41-KIS302-PREMARKET-HEALTHCHECK-001-20260309

**TASK_ID**: KIS-302
**PROJECT**: KIS-V41
**TITLE**: 03-10 장전 최종 시스템 헬스체크 — 서비스+DB+FunnelScore+Redis+크론 전수점검
**DATE**: 2026-03-09
**ASSIGNEE**: Cursor AI (서버 211)
**PRIORITY**: P0-CRITICAL
**STATUS**: ✅ ALL PASS (10/10)

---

## [인계 확인]
직전 완료: T-054 (Admin War Room 구현 검증)
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: D-001, D-002, D-003
strategy_cards: 60
open_positions: 0

---

## 작업 전 백업

```
cp /root/kis-autotrade-v4/config/funnel_score.yaml \
   /root/kis-autotrade-v4/config/funnel_score.yaml.bak.20260309_102400
백업 완료
```

---

## 헬스체크 결과 (10개 항목 전수점검)

### ① bridge.py PID 확인

```
ps aux | grep bridge
```

**결과:**
```
root     2405236  1.6  0.9 257508 151088 ?       Ssl  Mar08  21:37 /root/.genspark/venv/bin/python /root/.genspark/genspark_bridge.py
```

- **PID**: 2405236
- **실행 계정**: root
- **시작**: 2026-03-08 (21시간+ 가동 중)
- **상태**: ✅ PASS — bridge.py 정상 가동

---

### ② funnel_score.yaml null_fallback 확인

```
cat /root/kis-autotrade-v4/config/funnel_score.yaml | grep null_fallback
```

**결과:**
```yaml
null_fallback_score: 0.5  # T-237: 레이어 데이터 없음/NULL/0 시 Fail-Open 기본값
```

- **null_fallback_score**: 0.5
- **상태**: ✅ PASS — 0.5 정상 확인

---

### ③ 서비스 5개 active 확인

```
systemctl is-active kis-v41-api
systemctl is-active kis-v41-monitor
systemctl is-active kis-v41-scheduler
systemctl is-active postgresql
systemctl is-active redis-server
```

**결과:**

| 서비스 | 상태 | 세부 정보 |
|--------|------|-----------|
| kis-v41-api | **active** | running since 2026-03-08 14:23:25 KST (20h+) |
| kis-v41-monitor | **active** | running ✅ |
| kis-v41-scheduler | **active** | running ✅ |
| postgresql | **active** | running ✅ |
| redis-server | **active** | running ✅ |

- **상태**: ✅ PASS — 5개 서비스 모두 active

---

### ④ DB 쿼리 — strategy_cards / open_positions

```sql
SELECT COUNT(*) as strategy_cards_count FROM strategy_cards;
SELECT COUNT(*) as open_positions_count FROM v4_positions WHERE status='OPEN';
```

**결과:**
```
 strategy_cards_count
----------------------
                   60
(1 row)

 open_positions_count
----------------------
                    0
(1 row)
```

- **strategy_cards**: 60건 (예상: 60) ✅
- **open_positions (OPEN)**: 0건 (예상: 0) ✅
- **상태**: ✅ PASS

---

### ⑤ Redis ping

```
redis-cli ping
```

**결과:**
```
PONG
```

- **상태**: ✅ PASS

---

### ⑥ crontab 건수

```
crontab -l | wc -l
```

**결과:**
```
44
```

- **등록된 크론**: 44줄 (실제 cron 잡: 20건+, 주요 항목: LightGBM 재학습, 연구 파이프라인, 모의투자 V3 매수/매도/리뷰, AI 예측, 일일/주간/월간 보고서, DESK 노드 감지 등)
- **상태**: ✅ PASS (5건+ 기준 충족)

---

### ⑦ backtest/progress API 확인

```
curl -s https://trading41.newtalk.kr/api/v4/backtest/progress | head -c 200
```

**결과:**
```json
{"total_sessions":3,"completed":3,"running":0,"failed":0,"pending":0,"completion_pct":100.0,"latest_session":{"session_id":3,"hypothesis_id":null,"phase":"seed","status":"CONVERGED","started_at":"2026...
```

- **HTTP 응답**: 200 OK ✅
- **total_sessions**: 3 (completed: 3, running: 0, failed: 0)
- **completion_pct**: 100.0%
- **latest_session**: CONVERGED
- **상태**: ✅ PASS

---

### ⑧ trades/unified 10만건+ 확인

```
curl -s https://trading41.newtalk.kr/api/v4/trades/unified
```

**결과 (summary):**
```json
{
  "summary": {
    "total_count": 105526,
    "win_rate": 46.23,
    "profit_factor": 2.1033,
    "avg_pnl_pct": 1.7141,
    "cum_pct": 180499.0963,
    "mdd_pct": 100.0,
    "max_win_pct": 103.6515,
    "max_loss_pct": -38.1955
  },
  "pagination": {
    "page": 1, "limit": 50, "total": 105526, "pages": 2111
  }
}
```

- **total_count**: 105,526건 (예상: 10만건+) ✅
- **win_rate**: 46.23%
- **profit_factor**: 2.1033
- **cum_pct**: 180,499% (누적 수익률)
- **상태**: ✅ PASS

---

### ⑨ GO100 모의투자 세션 ACTIVE 확인

```sql
SELECT session_id, strategy_card_id, status
FROM go100_paper_trading_sessions
WHERE status='ACTIVE';
```

**결과:**
```
 session_id | strategy_card_id | status
------------+------------------+--------
          2 |               35 | ACTIVE
          3 |               55 | ACTIVE
          4 |               56 | ACTIVE
          5 |               57 | ACTIVE
          6 |               58 | ACTIVE
          7 |               59 | ACTIVE
(6 rows)
```

- **ACTIVE 세션**: 6개 (예상: 6개) ✅
- session_id 2-7, strategy_card_id 35, 55-59
- **상태**: ✅ PASS

---

### ⑩ go100 서비스 상태

```
systemctl status go100
```

**결과:**
```
● go100.service - GO100 V4.1 AutoTrade API
     Active: active (running) since Mon 2026-03-09 09:07:33 KST; 1h 16min ago
```

- **go100**: active (running) ✅
- **시작 시각**: 2026-03-09 09:07:33 KST
- **상태**: ✅ PASS

---

## 전체 결과 요약

| # | 항목 | 예상값 | 실제값 | 판정 |
|---|------|--------|--------|------|
| ① | bridge.py PID | 존재 | PID 2405236 (root, 21h+) | ✅ PASS |
| ② | funnel_score null_fallback | 0.5 | 0.5 | ✅ PASS |
| ③ | 서비스 5개 active | 모두 active | 5/5 active | ✅ PASS |
| ④ | strategy_cards / open_positions | 60 / 0 | 60 / 0 | ✅ PASS |
| ⑤ | redis-cli ping | PONG | PONG | ✅ PASS |
| ⑥ | crontab 건수 | 5건+ | 44줄 (20잡+) | ✅ PASS |
| ⑦ | backtest/progress 200 OK | 200 | 200, CONVERGED 100% | ✅ PASS |
| ⑧ | trades/unified 10만건+ | 100,000+ | 105,526건 | ✅ PASS |
| ⑨ | GO100 ACTIVE 세션 | 6개 | 6개 (session 2-7) | ✅ PASS |
| ⑩ | go100 서비스 | active | active (running 09:07 KST) | ✅ PASS |

**최종 판정: ✅ 10/10 ALL PASS — 03-10 장전 시스템 이상 없음**

---

## 특이사항

- trades/unified: `len(response)` = 3 (dict keys: summary/pagination/trades). 실제 total_count = 105,526건으로 10만건+ 충족
- kis-v41-api: 2026-03-08 14:23:25 KST 재시작 이후 20시간+ 안정 가동
- go100: 2026-03-09 09:07:33 KST 재시작 (오전 장 개시 전 정상 기동 확인)
- bridge.py: 2026-03-08부터 21시간+ 무중단 가동 중

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (이 태스크는 코드 변경 없음, 헬스체크만)
- [ ] project-docs 보고서 push 완료 (진행 중)
