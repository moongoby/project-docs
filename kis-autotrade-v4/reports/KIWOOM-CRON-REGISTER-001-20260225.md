# KIWOOM-CRON-REGISTER-001 Kiwoom 데이터 수집 cron 등록 보고서

- **프로젝트**: KIS AutoTrade V4.1  
- **브랜치**: phase-2c-command-center  
- **작성일**: 2026-02-25  
- **지시서**: KIWOOM-CRON-REGISTER-001  
- **우선순위**: P1  

---

## 1. 등록된 cron 4개 상세

| 구분 | cron 표현식 | KST 실행 시각 | 스크립트 | 비고 |
|------|-------------|----------------|----------|------|
| 프로그램매매 | `30 16 * * 1-5` | 평일 16:30 | `collect_program_trades.sh` | ka90004 → v4_program_trades |
| 테마 수집 | `0 17 * * 1-5` | 평일 17:00 | `collect_theme.sh` | ka90001/ka90002 → v4_theme_* |
| 체결강도 장중 | `*/5 9-15 * * 1-5` | 평일 09:00~15:55 매 5분 | `collect_strength_intraday.sh` | 15:30 이후 스킵 |
| 체결강도 일별 | `35 16 * * 1-5` | 평일 16:35 | `collect_strength_daily.sh` | 일별 백필 |

- **시간대**: 서버 KST(Asia/Seoul) 기준.  
- **요일**: 1-5 = 월~금 평일.

---

## 2. 스크립트 경로 및 로그 경로

| 스크립트 | 경로 | 로그 파일 패턴 |
|----------|------|----------------|
| 프로그램매매 | `/root/kis-autotrade-v4/scripts/cron/collect_program_trades.sh` | `logs/kiwoom/program_trades_YYYYMMDD.log` |
| 테마 | `/root/kis-autotrade-v4/scripts/cron/collect_theme.sh` | `logs/kiwoom/theme_YYYYMMDD.log` |
| 체결강도 장중 | `/root/kis-autotrade-v4/scripts/cron/collect_strength_intraday.sh` | `logs/kiwoom/strength_intraday_YYYYMMDD.log` |
| 체결강도 일별 | `/root/kis-autotrade-v4/scripts/cron/collect_strength_daily.sh` | `logs/kiwoom/strength_daily_YYYYMMDD.log` |

- **공통**: `cd /root/kis-autotrade-v4`, `PYTHONPATH=backend`, `.venv/bin/python` 사용.  
- **로그 디렉터리**: `/root/kis-autotrade-v4/logs/kiwoom/` (없으면 스크립트에서 `mkdir -p`).

---

## 3. 드라이런 결과

- **collect_theme.sh**  
  - `bash -x scripts/cron/collect_theme.sh`  
  - 정상 완료 (시작/완료 로그 기록, Python 정상 종료).

- **collect_strength_daily.sh**  
  - `bash -x scripts/cron/collect_strength_daily.sh`  
  - 정상 기동 확인 (종목 수 많아 장시간 실행 가능).

- **collect_program_trades.sh**  
  - `bash -x scripts/cron/collect_program_trades.sh`  
  - 정상 완료.  
  - 로그 예: `[2026-02-25 15:49:07 KST] 프로그램매매 수집 시작` → `{'ok': 0, 'fail': 0, 'total': 0, 'trade_date': '2026-02-25'}` → `[2026-02-25 15:49:09 KST] 프로그램매매 수집 완료`.  
  - 장마감 후가 아닌 시간대에는 API가 빈 배열을 줄 수 있어 total=0은 정상.

---

## 4. 소스 검수 결과

- **셸 스크립트 4개**  
  - 경로: `/root/kis-autotrade-v4` 고정.  
  - PYTHONPATH=backend, 실행 바이너리 `.venv/bin/python` 일치.  
  - 로그 디렉터리/파일명 규칙 통일.

- **collect_kiwoom_program_trades.py**  
  - 진입점만 제공.  
  - `backend.app.services.data.program_trades_collector.run_program_trades_collect()` 호출.  
  - DB 연결·API 호출·v4_program_trades INSERT는 기존 collector에 위임.

- **collect_kiwoom_strength.py**  
  - `--mode intraday` / `--mode daily` 분기 추가.  
  - intraday: 장중 증분, KST 오늘 날짜만 필터하여 수집.  
  - daily: 기존 일별 백필(증분/전체는 --incremental/--full 유지).  
  - f-string 로깅/출력 제거, % 포맷 사용.

- **crontab**  
  - 4개 항목 모두 KST 기준, 요일 1-5로 등록됨.  
  - 백업: `/tmp/crontab_backup_20260225_154913.txt`.

---

## 5. 수집 데이터 테이블 현황

| 테이블 | 용도 | API/스크립트 |
|--------|------|----------------|
| v4_program_trades | 프로그램매매 | ka90004, program_trades_collector / collect_kiwoom_program_trades.py |
| v4_trade_strength_history | 체결강도 일별/장중 | ka10047, collect_kiwoom_strength.py (--mode daily/intraday) |
| v4_theme_master / v4_theme_stock / v4_theme_detail | 테마 마스터·구성종목·상세 | ka90001/ka90002, collect_kiwoom_theme.py |

- **마이그레이션**: v4_program_trades(008), v4_trade_strength_history(007), v4_theme_detail(008) 등 기존 스키마 사용.

---

## 완료 체크리스트

- [x] 현재 cron 상태 확인  
- [x] cron 스크립트 4개 작성  
- [x] 수집 Python 스크립트 존재/작성 확인 (program_trades 진입점 추가, strength --mode 추가)  
- [x] 실행 권한 부여 및 드라이런  
- [x] crontab 등록 완료  
- [x] 소스 검수 완료  
- [x] 보고서 push 후 curl 200 확인  

---

*KIWOOM-CRON-REGISTER-001 완료.*
