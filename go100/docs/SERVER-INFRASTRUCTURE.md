# GO100 서버 인프라 현황
> 최종 업데이트: 2026-02-26 | 관리자: 대표님

## 1. 서버 기본 정보
- **호스트**: root@kis-autotrade-v4 (내부 IP 10.0.1.6, 공인 IP 211.188.51.113)
- **OS**: Ubuntu 24.04.1 LTS (Noble Numbat), 커널 6.8.0-84-generic x86_64
- **CPU**: Intel Xeon Gold 5220 @ 2.20GHz, 4코어 (`nproc`=4)
- **RAM**: 15Gi total, 4.8Gi used, 10Gi available (buff/cache 포함), Swap 8Gi(915Mi used)
- **디스크**: 총 99G / 사용 82G / 여유 13G / 사용률 87% (정리 후)
- **호스팅**: (확인 가능하면 업체명/플랜 기입)

## 2. 네트워크/도메인
- **공인 IP**: 211.188.51.113 (실제 인터페이스: eth0 10.0.1.6/24)
- **도메인**: go100.newtalk.kr, trading41.newtalk.kr, v4.trading.newtalk.kr, trading.newtalk.kr
- **SSL**: Let's Encrypt (ECDSA)
  - go100.newtalk.kr: 만료 2026-05-20 (VALID: 83일)
  - trading41.newtalk.kr: 만료 2026-05-14 (VALID: 77일)
- **Nginx**: 리버스 프록시, sites-enabled에 go100.newtalk.kr / trading41.newtalk.kr 등 server_name 설정

## 3. 서비스 구성
| 서비스 | 포트 | systemd 유닛 | 상태 |
|--------|------|-------------|------|
| FastAPI 백엔드 | 8002 | go100 | active |
| Next.js 프론트 | 3000 | go100-frontend | active |
| PostgreSQL | 5432 | postgresql@16-main | active |
| Redis | 6379 | redis-server | active |
| Nginx | 80/443 | nginx | active |

## 4. 디스크 상세
### 4-1. 전체 파티션
```
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           1.6G  1.1M  1.6G   1% /run
/dev/vda2        99G   82G   13G  87% /
tmpfs           7.9G  1.7M  7.9G   1% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
tmpfs           1.6G   84K  1.6G   1% /run/user/0
```
- 블록: vda 100G, vda2에 / 마운트

### 4-2. 주요 디렉토리별 사용량
| 경로 | 사용량 | 비고 |
|------|--------|------|
| /root | 51G | 홈·백업·프로젝트 포함 |
| /var | 17G | PostgreSQL 14G, 로그 등 |
| /swapfile | 8.1G | 스왑 |
| /tmp | 4.4G | 임시 |
| /usr | 4.2G | 시스템 |
| /var/lib/postgresql | 14G | DB 데이터 |
| /root/kis-autotrade-v4 | 8.8G | 소스코드+빌드 |
| /root/backup | 33G | 백업 (정리 후) |
| /var/log | 1.8G | 로그 |
| /var/log/journal | 248M | systemd 저널 |
| /root/kis-autotrade-v4/frontend/node_modules | 1.5G | npm 의존성 |
| /root/kis-autotrade-v4/frontend/.next | 342M | Next 빌드 |

### 4-3. PostgreSQL 테이블별 용량 (상위 20)
- **DB명**: kisautotrade (문서상 autotrade는 동일 서버 내 별칭)
- **DB 총 크기**: 14 GB

| 테이블 | 용량 |
|--------|------|
| v4_ohlcv_minute_2026_01 | 1153 MB |
| v4_ohlcv_minute_2025_12 | 1086 MB |
| v4_ohlcv_minute_2025_07 | 945 MB |
| v4_ohlcv_minute_2025_09 | 935 MB |
| v4_ohlcv_minute_2025_11 | 911 MB |
| v4_ohlcv_minute_2025_04 | 860 MB |
| v4_ohlcv_minute_2025_08 | 824 MB |
| v4_ohlcv_minute_2025_03 | 793 MB |
| v4_ohlcv_minute_2025_06 | 790 MB |
| v4_ohlcv_minute_2025_10 | 789 MB |
| v4_ohlcv_minute_2026_02 | 756 MB |
| v4_ohlcv_minute_2025_05 | 755 MB |
| ohlcv_daily | 696 MB |
| market_data_min | 557 MB |
| ohlcv_1m_history | 466 MB |
| _legacy_ohlcv_1m_history_20260220 | 361 MB |
| _legacy_market_data_min_20260220 | 292 MB |
| v4_ohlcv_minute_2025_02 | 253 MB |
| v4_investor_daily | 172 MB |
| ohlcv_weekly | 50 MB |

### 4-4. 디스크 증감 추이
| 날짜 | 사용률 | 여유 | 비고 |
|------|--------|------|------|
| 2026-02-26 | 87% | 13 GB | 백업·저널·캐시 정리 후 |
| (이전 100% 사고일) | 100% | 0 | PG PANIC 등 참고용 |

## 5. 백업 현황
- **백업 경로**: /root/backup/
- **현재 백업 수**: 39개 (7일 초과분 정리 후)
- **가장 오래된**: 2026-02-18 (파일 기준)
- **가장 최근**: 2026-02-26 (wave3-main-20260226-081916)
- **백업 용량**: 약 33 GB
- **자동 백업**: 있음 (cron db_backup.sh 매일 03:00)
- **권장**: 7일 보존, cron으로 자동 정리 또는 수동 `find /root/backup -maxdepth 1 -mtime +7 -exec rm -rf {} \;`

## 6. 보안
- **방화벽**: ufw active, 22/tcp·80·443 ALLOW
- **SSH**: Port 22, PermitRootLogin yes
- **fail2ban**: 설치됨, jail sshd 활성
- **SSL**: Let's Encrypt 만료일 위 Section 2 참조

## 7. 크론/스케줄 작업
- VKOSPI 수집: 18:30 월–금
- 보험 토큰 갱신: 14:30 월–금
- 디스크 모니터: 6시간마다
- DB 백업: 03:00 매일
- alert_cron: 장중 5분마다, 비장중 30분마다
- 분봉 배치: 평일 16:00, 토 02:00
- stock_universe: 19:00 월–금
- 일봉 수집: 18:00 월–금
- 레거시 테이블 DROP: 일요일 04:00
- index_daily: 18:30 월–금
- v4_market_investor_daily: 18:40 월–금
- stock_industry: 토 03:00
- Kiwoom REST: 프로그램매매 16:30, 테마 17:00, 체결강도 장중 5분·일별 16:35, 투자자 16:50, 신용/공매도 16:45  
(상세는 `crontab -l` 참조)

## 8. 주요 환경변수 (키 마스킹)
- GOOGLE_AI_API_KEY=***
- ANTHROPIC_API_KEY=***
- OPENAI_API_KEY=***
- DB 접속: localhost:5432/kisautotrade (사용자 kis_admin)
- Redis: localhost:6379

## 9. 용량 관리 가이드
### 정기 정리 (주 1회 권장)
```bash
find /root/backup -maxdepth 1 -mtime +7 -exec rm -rf {} \;
journalctl --vacuum-time=3d
npm cache clean --force
apt-get clean
```

### 디스크 80% 초과 시 긴급 대응
1. `du -sh /* | sort -rh | head -20` 로 사용처 확인
2. 백업 정리 (7일 초과 삭제)
3. PG vacuum: `sudo -u postgres vacuumdb --all --analyze`
4. 호스팅 업체 디스크 추가 문의

### 디스크 증설 옵션
- 카페24 M.2 250GB 추가: 월 10,000원
- 카페24 M.2 500GB 추가: 월 14,000원
- DB 분리(별도 서버): Phase 3–4 시점 검토

## 10. 변경 이력
| 날짜 | 변경 내용 | 작업자 |
|------|-----------|--------|
| 2026-02-26 | 최초 작성, 서버 기본정보·디스크 상세·DB 테이블 용량·서비스 구성, 디스크 정리 후 용량 기록, 용량 관리 가이드 포함 | ClaudeCode |
