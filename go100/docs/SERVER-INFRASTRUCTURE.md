# 211 서버 인프라 현황
> 최종 업데이트: 2026-02-26 18:00 KST

---

## 1. 서버 기본 정보

| 항목 | 값 |
|------|-----|
| 호스트 | root@kis-autotrade-v4 |
| 내부 IP | [INTERNAL-IP]/24 (eth0) |
| 공인 IP | [SERVER-IP] |
| OS | Ubuntu 24.04.1 LTS (Noble Numbat) |
| 커널 | 6.8.0-84-generic x86_64 |
| CPU | Intel Xeon Gold 5220 @ 2.20GHz, 4코어 |
| RAM | 15Gi total / 5.5Gi used / 10Gi available |
| Swap | 8Gi (/swapfile) / 844Mi used |
| Python | 3.12.3 (venv: /root/kis-autotrade-v4/venv) |
| Node.js | v18.19.1, npm 9.2.0 |

---

## 2. 디스크 구성

### 2-1. 블록 디바이스
```
NAME    SIZE FSTYPE MOUNTPOINT TYPE
vda     100G                   disk   ← OS 디스크
├─vda1    1M                   part
└─vda2  100G ext4   /          part
vdb     200G                   disk   ← DB 전용 디스크 (2026-02-26 추가)
└─vdb1  200G ext4   /data      part
```

### 2-2. 파티션 사용량
| 디바이스 | 크기 | 사용 | 여유 | 사용률 | 마운트 | 용도 |
|----------|------|------|------|--------|--------|------|
| /dev/vda2 | 99G | 65G | 30G | **69%** | `/` | OS + 애플리케이션 |
| /dev/vdb1 | 196G | 14G | 172G | **8%** | `/data` | PostgreSQL DB 전용 |

fstab:
```
/dev/disk/by-uuid/a98df387-... / ext4 defaults 0 1
UUID=85c0fff9-f3ba-46d0-bdf1-9587527711aa /data ext4 defaults,noatime 0 2
/swapfile none swap sw 0 0
```

### 2-3. 주요 디렉토리 사용량
| 경로 | 사용량 | 비고 |
|------|--------|------|
| `/root` | 50G | 홈/백업/프로젝트 포함 |
| `/root/backup` | 33G | DB 백업 (62개, 7일 자동정리) |
| `/root/kis-autotrade-v4` | 9.0G | 소스코드+빌드 |
| `/root/kis-autotrade-v4/frontend/node_modules` | 1.5G | npm 의존성 |
| `/root/kis-autotrade-v4/frontend/.next` | 414M | Next.js 빌드 |
| `/root/project-docs` | 42M | 문서 레포 |
| `/data/postgresql` | 14G | PostgreSQL 데이터 |
| `/var` | 2.2G | 로그 등 (DB 이전 후 감소) |
| `/var/log` | 1.8G | 시스템/앱 로그 |
| `/usr` | 4.2G | 시스템 패키지 |

### 2-4. 디스크 용량 추이
| 날짜 | `/` 사용률 | `/` 여유 | `/data` 사용률 | 비고 |
|------|-----------|---------|---------------|------|
| 2026-02-26 (현재) | 69% | 30G | 8% (172G 여유) | vdb 200G 추가, DB 이전 완료 |
| 2026-02-26 (이전) | 87% | 13G | — | 디스크 정리 후 |
| (100% 사고일) | 100% | 0 | — | PG PANIC 발생 이력 |

---

## 3. 네트워크/도메인

| 도메인 | Nginx 설정 | 프록시 대상 | SSL 만료 |
|--------|-----------|------------|---------|
| go100.newtalk.kr | sites-enabled/go100 | 8002 (API), 3000 (프론트) | 2026-05-20 |
| trading41.newtalk.kr | sites-enabled/kis-autotrade | 8001 (레거시API), 8003 (V41프론트, 비활성) | 2026-05-14 |
| v4.trading.newtalk.kr | sites-enabled/kis-autotrade | 동일 | 동일 |
| trading.newtalk.kr | sites-enabled/kis-autotrade | 동일 | 동일 |

- SSL: Let's Encrypt (ECDSA), certbot 자동갱신

---

## 4. 서비스 구성

### 4-1. GO100 (백억이) 서비스
| 서비스 | 포트 | systemd 유닛 | 상태 | 설명 |
|--------|------|-------------|------|------|
| FastAPI 백엔드 | 8002 | `go100` | **active** | GO100 V4.1 AutoTrade API |
| Next.js 프론트 | 3000 | `go100-frontend` | **active** | GO100 대시보드 |

### 4-2. KIS V4.1 (레거시) 서비스
| 서비스 | 포트 | systemd 유닛 | 상태 | 설명 |
|--------|------|-------------|------|------|
| Web API (레거시) | 8001 | `kis-webapp-api` | **active** | 레거시 웹 플랫폼 |
| V4.1 프론트 | 8003 | `kis-v41-frontend` | **inactive** | 비활성 |
| Trading Engine | — | `kis-trading-engine` | **active** | 통합 트레이딩 스케줄러 |
| Scalping | — | `kis-scalping` | **active** | 스캘핑 스케줄러 |
| V4.1 Scheduler | — | `kis-v41-scheduler` | **active** | V4.1 메인 스케줄러 |
| V4.1 Monitor | — | `kis-v41-monitor` | **active** | 포지션 모니터 |
| V4.1 Position Monitor | — | `kis-v41-position-monitor` | **active** | 포지션 모니터 (보조) |

### 4-3. 인프라 서비스
| 서비스 | 포트 | systemd 유닛 | 상태 | 버전 |
|--------|------|-------------|------|------|
| PostgreSQL | 5432 | `postgresql@16-main` | **active** | 16.10 |
| Redis | 6379 | `redis-server` | **active** | 7.0.15 (메모리 1.44M) |
| Nginx | 80/443 | `nginx` | **active** | — |

---

## 5. 데이터베이스

### 5-1. 기본 정보
| 항목 | 값 |
|------|-----|
| DB명 | kisautotrade |
| 사용자 | kis_admin |
| 호스트 | localhost:5432 |
| data_directory | **`/data/postgresql/16/main`** (vdb1 디스크) |
| config_file | `/etc/postgresql/16/main/postgresql.conf` |
| DB 총 크기 | **14 GB** |
| 테이블 수 | **207개** |
| 접속 방식 | peer auth (`sudo -u postgres psql -d kisautotrade`) |

### 5-2. 테이블 용량 (상위 20)
| 테이블 | 용량 | 비고 |
|--------|------|------|
| v4_ohlcv_minute_2026_01 | 1,153 MB | 분봉 (월별 파티션) |
| v4_ohlcv_minute_2025_12 | 1,086 MB | |
| v4_ohlcv_minute_2025_07 | 945 MB | |
| v4_ohlcv_minute_2025_09 | 935 MB | |
| v4_ohlcv_minute_2025_11 | 911 MB | |
| ohlcv_1m_history | 896 MB | 레거시 분봉 |
| v4_ohlcv_minute_2025_04 | 860 MB | |
| v4_ohlcv_minute_2025_08 | 824 MB | |
| v4_ohlcv_minute_2025_03 | 808 MB | |
| v4_ohlcv_minute_2026_02 | 806 MB | |
| market_data_min | 792 MB | 레거시 분봉 |
| v4_ohlcv_minute_2025_06 | 790 MB | |
| v4_ohlcv_minute_2025_10 | 789 MB | |
| v4_ohlcv_minute_2025_05 | 755 MB | |
| ohlcv_daily | 696 MB | 일봉 |
| v4_ohlcv_minute_2025_02 | 257 MB | |
| go100_news_items | 256 MB | 뉴스/공시 (수집 중) |
| v4_investor_daily | 172 MB | 투자자 수급 |
| ohlcv_weekly | 50 MB | 주봉 |
| orderbook_snapshots | 42 MB | 호가 스냅샷 |

---

## 6. 크론/스케줄 작업

### 6-1. 시간순 전체 일정 (평일 기준)

| 시각 | 작업 | 스크립트 | 비고 |
|------|------|---------|------|
| 03:00 매일 | DB 백업 | `db_backup.sh` | |
| 03:30 일요일 | 저널 정리 | `journalctl --vacuum-time=3d` | |
| 03:45 일요일 | npm 캐시 정리 | `npm cache clean --force` | |
| 04:00 매일 | 백업 7일 초과 삭제 | `find /root/backup ...` | |
| 04:00 일요일 | 레거시 테이블 DROP | `drop_legacy_tables.py` | |
| 매 6시간 | 디스크 모니터 | `disk_monitor.sh` | |
| 매 5분 (항시) | 헬스 모니터 | `health_monitor.py` | GO100 |
| **08:30** | 글로벌 마켓 수집 | `collect_global_market.py` | |
| **08:50** | 모닝 브리핑 생성 | `daily_reports.py --type morning` | GO100 |
| **09:00~15:30** (5분) | 체결강도 장중 증분 | `collect_strength_intraday.sh` | Kiwoom acct 4 |
| **09:00~15:30** (5분) | alert_cron | `alert_cron.sh` | |
| **09:00~15:30** (5분) | 이벤트 알림 체크 | `daily_reports.py --type event` | GO100 |
| **14:30** | 보험 토큰 갱신 | `data_miner.py --refresh-tokens` | |
| **15:40** | 장마감 리포트 | `daily_reports.py --type closing` | GO100 |
| **16:00** | 분봉 배치 수집 | `minute_batch_cron.sh` | |
| **16:10** | 페이퍼 트레이딩 일일처리 | `paper_trading_daily.py` | GO100 |
| **16:20** | **Kiwoom 토큰 사전 갱신** | `refresh_kiwoom_tokens.sh` | **3계정 일괄** |
| **16:30** | 프로그램매매 수집 | `collect_program_trades.sh` | Kiwoom acct 6 |
| **16:35** | 체결강도 일별 백필 | `collect_strength_daily.sh` | Kiwoom acct 4 |
| **16:45** | 신용잔고/공매도 수집 | `collect_credit_balance.sh` | |
| **16:50** | 투자자 수급 수집 | `collect_investor_daily.sh` | Kiwoom |
| **17:00** | 테마 수집 | `collect_theme.sh` | Kiwoom acct 5 |
| **17:10** | 뉴스/공시 수집 | `collect_news_daily.sh` | KIS API |
| **18:00** | 일봉 수집 | `collect_ohlcv_daily.py` | |
| **18:30** | VKOSPI 수집 | `collect_vkospi_alt.py` | |
| **18:30** | 지수 일봉 수집 | `collect_index_daily.sh` | |
| **18:40** | 시장 투자자 수집 | `collect_market_investor.py` | |
| **19:00** | stock_universe 수집 | `collect_stock_universe.py` | |
| **19:30** | 재무제표 수집 | `collect_financials.py` | |
| 토 02:00 | 분봉 배치 (주말) | `minute_batch_cron.sh` | |
| 토 03:00 | 산업/업종 수집 | `collect_stock_industry.py` | |
| 토 09:00 | 주간 보고 | `daily_reports.py --type weekly` | GO100 |
| 비장중 (30분) | alert_cron | `alert_cron.sh` | |

### 6-2. Kiwoom 계정 배분
| 계정 | 유형 | 담당 | 크론 |
|------|------|------|------|
| account_id=4 | 모의 | 체결강도 (장중+일별) | 09:00~15:30 5분, 16:35 |
| account_id=5 | 실거래 | 테마, 신용잔고 | 17:00, 16:45 |
| account_id=6 | 실거래 | 프로그램매매 | 16:30 |

---

## 7. 백업 현황

| 항목 | 값 |
|------|-----|
| 백업 경로 | `/root/backup/` |
| 현재 백업 수 | 62개 |
| 가장 오래된 | 2026-02-18 |
| 가장 최근 | 2026-02-26 |
| 백업 용량 | 약 33 GB |
| 자동 백업 | 매일 03:00 (`db_backup.sh`) |
| 자동 정리 | 매일 04:00 (7일 초과 삭제) |

---

## 8. 보안

| 항목 | 설정 |
|------|------|
| 방화벽 | ufw active — 22/tcp, 80/tcp, 443/tcp ALLOW |
| SSH | Port 22, PermitRootLogin yes |
| fail2ban | 활성 (jail: sshd) |
| SSL | Let's Encrypt (certbot 자동갱신) |

---

## 9. 주요 환경변수 (키 마스킹)

```
GOOGLE_AI_API_KEY=***
ANTHROPIC_API_KEY=***
OPENAI_API_KEY=***
DB: localhost:5432/kisautotrade (kis_admin)
Redis: localhost:6379
```

---

## 10. 용량 관리 가이드

### 정기 정리 (cron 자동화됨)
```bash
# 매일 04:00 — 7일 초과 백업 삭제
find /root/backup -maxdepth 1 -mtime +7 -exec rm -rf {} \;
# 주 1회 일요일 — 저널/캐시 정리
journalctl --vacuum-time=3d
npm cache clean --force
```

### `/` 80% 초과 시 긴급 대응
1. `du -sh /* | sort -rh | head -20` 로 사용처 확인
2. 백업 정리 (7일 초과 삭제)
3. PG vacuum: `sudo -u postgres vacuumdb --all --analyze`
4. /var/log 대형 로그 truncate

### `/data` 용량 예측
- 현재 DB 14GB, 월 증가량 ~1GB (분봉 주력)
- 172GB 여유 → 약 **14년 이상** 여유

---

## 11. 변경 이력

| 날짜 | 변경 내용 | 작업자 |
|------|-----------|--------|
| 2026-02-26 | 최초 작성 | ClaudeCode |
| 2026-02-26 | **전면 최신화**: vdb 200G 디스크 추가 반영, DB data_directory `/data` 이전 반영, 전 systemd 서비스 목록 추가 (KIS V4.1 포함), 크론 시간순 정리 (Kiwoom 3계정 배분 포함), DB 테이블 용량 갱신, 디스크 용량 추이 갱신 | ClaudeCode |
