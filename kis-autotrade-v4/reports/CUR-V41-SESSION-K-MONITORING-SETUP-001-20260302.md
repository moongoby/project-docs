# CUR-V41-SESSION-K-MONITORING-SETUP-001 — 03-03 Virtual Run 자동 모니터링 체계 구축
> 작성: 2026-03-02 | Model: Claude Code (claude-opus-4-6)
> 커밋: kis-autotrade-v4 (이 커밋) | project-docs (이 커밋)

---

## 1. 모니터링 스크립트 구조

### 파일: `scripts/monitor_virtual_run.py`

```
VirtualRunMonitor
├── parse_log_since(time)     # /var/log/unified_engine.log 파싱
├── get_mock_trades()         # v4_mock_trades SELECT (오늘 거래)
├── get_open_positions()      # v4_mock_trades exit_price IS NULL
├── get_exit_distribution()   # 청산 모드 분포 (notes 파싱)
├── get_system_status()       # free/df/systemctl 6서비스
├── save_snapshot(action)     # JSONL 형식 스냅샷 추가
└── generate_daily_report()   # Markdown 종합 보고서 생성

5가지 액션:
  premarket    → 07:58 시스템 상태 확인
  signal       → 08:55 L3.3 결과 + 거래 수집
  periodic     → 09:30~15:00 매 30분 상태
  close        → 15:35 장 마감 최종 수집
  daily_report → 16:00 일간 보고서 생성
```

### 핵심 모니터링 항목

| # | 항목 | 수집 방법 | 기준 |
|---|------|----------|------|
| 1 | L3.3 ALLOW/BLOCK/CONDITIONAL 비율 | 로그 파싱 + notes 파싱 | E-3: 17%/73%/10% |
| 2 | v4_mock_trades 거래 기록 | DB SELECT | 전략별 분포 |
| 3 | 청산 모드 분포 | notes JSON 파싱 | D2 TIMEOUT <50% |
| 4 | Fail-Open 발동 | "supply gate error" 로그 | 0건 |
| 5 | 시스템 안정성 | free/df/systemctl | Swap <80%, ALL active |
| 6 | 에러/경고 | [ERROR]/[WARNING] 로그 | 0건 |

---

## 2. Cron 등록 내역

| 시각 | 액션 | 설명 |
|------|------|------|
| 07:58 | premarket | premarket(07:55) 3분 후 시스템 확인 |
| 08:55 | signal | signal(08:50) 5분 후 L3.3+거래 수집 |
| */30 9-14 | periodic | 매 30분 상태 수집 |
| 0,30 15 | periodic | 15시대 30분 간격 |
| 15:35 | close | close(15:30) 5분 후 최종 수집 |
| 16:00 | daily_report | 일간 보고서 생성 |

**로그**: `/var/log/virtual_monitor.log`
**스냅샷**: `/root/kis-autotrade-v4/reports/daily/{date}/snapshots.jsonl`
**보고서**: `/root/kis-autotrade-v4/reports/daily/{date}/DAILY-REPORT-{date}.md`

---

## 3. 로그 파싱 패턴

### unified_engine.log 포맷
```
2026-03-03 HH:MM:SS,mmm [LEVEL] message
```

### 탐지 패턴

| 패턴 | 카운터 | 출처 |
|------|--------|------|
| `L3.3 BLOCK:` | l33_block | signal_generator.py |
| `L3.3` + `ALLOW` | l33_allow | signal_generator.py |
| `L3.3` + `CONDITIONAL` | l33_conditional | signal_generator.py |
| `L3.3_SUPPLY` | l33_block | cte_pipeline.py blocking_layer |
| `supply gate error` | supply_gate_errors | signal_generator.py Fail-Open |
| `[SIGNAL]` + `통과` | signals_passed | run_unified_engine.py |
| `[SIGNAL]` + `차단` | signals_blocked | run_unified_engine.py |
| `[SIGNAL] 완료:` | signal_summary | run_unified_engine.py |
| `[ERROR]` | errors list | 전체 |
| `[WARNING]` | warnings list | 전체 |
| `[MONITOR] 오픈 포지션 (\d+)건` | monitor_open_count | run_unified_engine.py |

### 보조: v4_mock_trades.notes JSON

```json
{
  "approved": true/false,
  "blocking_layer": "L3.3_SUPPLY" | "SIGNAL_COMBO" | ...,
  "blocking_reason": "수급 차단: ...",
  "supply_gate": {"label": "ALLOW/BLOCK/CONDITIONAL", "score": 5, "reason": "..."}
}
```

> **참고**: 03-02 로그에는 L3.3 관련 로그가 없음 (Session H 코드 커밋 후 서비스 미재시작).
> 03-03부터 cron이 새 코드(`venv/bin/python`)를 직접 실행하므로 L3.3 활성화됨.

---

## 4. Dry-Run 결과 (2026-03-02)

### 액션별 테스트

| 액션 | 결과 | 출력 |
|------|------|------|
| premarket | PASS | Services: ALL OK, Swap: 73.8%, Errors: 0 |
| signal | PASS | Trades: 7건 (D6:1/D5:1/D4:1/D2:1/S1:1/D7:1/D-ORB:1), L3.3: 로그 없음 |
| periodic | PASS | Trades: 7, Open: 7, Errors: 0, Swap: 73.8% |
| close | PASS | Trades: 7, Open: 7, L3.3: 0/0/0, Errors: 0 |
| daily_report | PASS | DAILY-REPORT-20260302.md 생성 (3.0KB) |

### 파일 생성 확인

```
reports/daily/2026-03-02/
├── DAILY-REPORT-20260302.md  (3.0KB)
└── snapshots.jsonl           (17.9KB, 4 entries)
```

### 기존 테스트 비파괴 확인

```
CTE 94 passed, 1 warning in 0.26s ← ALL PASS
(desk2 test_orchestration_v2 1건 기존 실패 — Session K 무관)
```

---

## 5. 03-03 모니터링 시간표

```
07:55  [ENGINE] premarket
07:58  [MONITOR] premarket → 시스템 상태, 로그 에러
08:50  [ENGINE] signal
08:55  [MONITOR] signal → L3.3 비율, 거래 기록, Fail-Open
09:00  [ENGINE] monitor (*/1분)
09:00  [MONITOR] periodic
09:30  [MONITOR] periodic
10:00  [MONITOR] periodic
  ...  (매 30분)
15:00  [MONITOR] periodic
15:30  [ENGINE] close
15:30  [MONITOR] periodic
15:35  [MONITOR] close → 최종 수집
16:00  [MONITOR] daily_report → 보고서 생성
```

---

## 6. 일간 보고서 예시

03-02 dry-run 결과:

```markdown
# Virtual Run Daily Report — 2026-03-02

## 1. 요약
| 지표 | 값 | 기준 | 판정 |
|------|-----|------|------|
| L3.3 ALLOW | 0건 (0.0%) | E-3 기준 17% | OK |
| L3.3 BLOCK | 0건 (0.0%) | E-3 기준 73% | OK |
| 총 거래 | 7건 | — | — |
| 전략별 분포 | D-ORB:1/D2:1/D4:1/D5:1/D6:1/D7:1/S1:1 | — | — |
| 오픈 포지션 | 7건 | LIMIT 5 | WARNING |
| 에러 | 0건 | 0 | OK |
| Fail-Open 발동 | 0건 | 0 | OK |

종합 판정: NORMAL
```

---

## 7. 알림 채널 현황

| 채널 | 상태 | 비고 |
|------|------|------|
| Telegram | 미설정 | GO100_TELEGRAM_BOT_TOKEN 비어있음 |
| Slack | 코드 존재 | slack_service.py 있으나 웹훅 미설정 |
| Email | 코드 존재 | alert_service.py 있으나 설정 미확인 |

**현재 조치**: 로그 파일 기록 + 일간 보고서 생성만. 알림 채널 필요 시 추후 설정.

---

## 8. 보고서 Push 정책

**방안 B 채택: CEO 확인 후 수동 push**

일간 보고서는 서버 로컬에만 저장됨:
```
/root/kis-autotrade-v4/reports/daily/{date}/DAILY-REPORT-{date}.md
```

CEO 확인 후 push 명령:
```bash
cp /root/kis-autotrade-v4/reports/daily/2026-03-03/DAILY-REPORT-20260303.md \
   /root/project-docs/kis-autotrade-v4/reports/
cd /root/project-docs
git add -A && git commit -m "[V4.1] Daily Report 2026-03-03" && git push origin master
```

---

## 9. 수정 파일 목록

| 파일 | 변경 유형 | 핵심 변경 |
|------|----------|----------|
| `scripts/monitor_virtual_run.py` | 신규 | 5액션 모니터링 스크립트 (352행) |
| `reports/daily/` | 신규 디렉토리 | 일간 스냅샷/보고서 저장소 |
| crontab | 수정 | 6개 모니터링 cron 추가 |
| `/var/log/virtual_monitor.log` | 신규 | 모니터링 로그 파일 |
