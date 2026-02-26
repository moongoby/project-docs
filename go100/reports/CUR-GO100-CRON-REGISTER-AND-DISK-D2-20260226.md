# CUR-GO100-CRON-REGISTER-AND-DISK-D2 (2026-02-26)

## 크론 등록 결과
| # | 크론 | 스케줄 | 스크립트 | 테스트 |
|---|------|--------|----------|--------|
| 1 | 모닝 브리핑 | 08:50 월~금 | daily_reports.py --type morning | PASS |
| 2 | 장마감 리포트 | 15:40 월~금 | daily_reports.py --type closing | PASS |
| 3 | 페이퍼 트레이딩 | 16:10 월~금 | paper_trading_daily.py | PASS |
| 4 | 주간 보고 | 토 09:00 | daily_reports.py --type weekly | PASS |
| 5 | 이벤트 알림 | */5 장중 월~금 | daily_reports.py --type event | PASS |
| 6 | 헬스 모니터 | */5 매일 | health_monitor.py | PASS |

## 디스크 정리 2차
- 정리 전: 89% (84GB/99GB)
- 정리 후: 89% (84GB/99GB)
- 회수 용량: 0GB (7일 초과 백업 없음, journal/npm/apt/tmp 정리 수행)
- 로그 로테이션: /etc/logrotate.d/go100 등록

## 전체 GO100 크론 목록
```
30 8 * * 1-5 cd /root/kis-autotrade-v4 && .venv/bin/python scripts/data_collect/collect_global_market.py >> /var/log/go100_global_market.log 2>&1
50 8 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/.venv/bin/python scripts/go100/daily_reports.py --type morning >> /var/log/go100-morning-briefing.log 2>&1
40 15 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/.venv/bin/python scripts/go100/daily_reports.py --type closing >> /var/log/go100-closing-report.log 2>&1
10 16 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/.venv/bin/python scripts/go100/paper_trading_daily.py >> /var/log/go100-paper-trading.log 2>&1
0 9 * * 6 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/.venv/bin/python scripts/go100/daily_reports.py --type weekly >> /var/log/go100-weekly-report.log 2>&1
*/5 9-15 * * 1-5 cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/.venv/bin/python scripts/go100/daily_reports.py --type event >> /var/log/go100-event-alert.log 2>&1
*/5 * * * * cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/.venv/bin/python scripts/go100/health_monitor.py >> /var/log/go100-health-monitor.log 2>&1
```
