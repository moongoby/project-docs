# 작업지시서 #2026-0220-N 결과 보고

- **작업A**: 시그널 60일 백필 (과거 시그널 이력 생성)
- **작업B**: 웹 대시보드 프론트엔드 구축
- **작성일**: 2026-02-20

---

## PRE-FLIGHT (참고)

| 항목 | 결과 | 판정 |
|------|------|------|
| 최근 60 거래일 범위 | (DB 타임아웃으로 생략) | - |
| v4_signals 현재 행수 | (DB 타임아웃으로 생략, 1914 예상) | - |
| live_signal_generator.py 존재 | 확인됨 | OK |

---

## [작업A] 시그널 60일 백필

### STEP A-1: backfill_signals.py 생성

- **파일**: `scripts/backfill_signals.py`
- **기능**: CLI `--days 60 --top 500`, `get_trading_dates()`, `LiveSignalGenerator.generate_daily_signals(target_date, source='backfill')`, 진행률 출력, ON CONFLICT DO NOTHING, 완료 후 데스크별 분포 출력
- **LiveSignalGenerator 수정**: `generate_daily_signals(target_date, source='live')`에 `source` 파라미터 추가, INSERT 시 `source_val` 사용
- **v4_signal_api 수정**: `/stats`, `/strength-analysis`에서 `COALESCE(s.source, 'live') IN ('live', 'backfill')` 로 backfill 포함

**검증**

- `python3 -c "import scripts.backfill_signals; print('OK')"` → OK
- `md5sum scripts/backfill_signals.py` → `0c040a6c6a4a281f58ffdf4e0b3ad8df`

### STEP A-2: 백필 실행 (사용자 실행)

- DB 비밀번호: `.env`에 `PGPASSWORD` 또는 `DB_PASSWORD` 있으면 자동 사용. 없으면 아래처럼 환경변수 지정.

```bash
cd /root/kis-autotrade-v4 && source venv/bin/activate
export PGPASSWORD='[DB-PASSWORD]'   # 필요 시
python scripts/backfill_signals.py --days 60 --top 500 \
  2>&1 | tee backups/backfill_signals_20260220.log
```

- 예상: 60일 × 약 1,900건/일 ≈ 114,000건, 소요 10~30분

### STEP A-3: 백필 후 검증 (실행 후 아래 명령으로 확인)

```bash
# source별 건수·날짜 범위
PGPASSWORD='[DB-PASSWORD]' psql -h localhost -U kis_admin -d kisautotrade -c "
  SELECT source, COUNT(*) AS cnt, MIN(signal_date) AS min_date, MAX(signal_date) AS max_date
  FROM v4_signals GROUP BY source ORDER BY source;
"

# 데스크별 분포
PGPASSWORD='[DB-PASSWORD]' psql -h localhost -U kis_admin -d kisautotrade -c "
  SELECT desk_id, COUNT(*) AS cnt, AVG(signal_strength)::int AS avg_str
  FROM v4_signals GROUP BY desk_id ORDER BY desk_id;
"
```

- `/api/v4/signals/stats?days=60`, `/api/v4/signals/strength-analysis?days=60` 호출 시 backfill 데이터 포함되어 통계 반영

---

## [작업B] 웹 대시보드 프론트엔드

### STEP B-1~B-4: frontend/dashboard

- **index.html**: 헤더(시스템 상태·마지막 갱신), 탭(Overview, DESK1~5, 포지션, 자금, 분석), 각 탭용 section·card id
- **style.css**: 다크 테마(#1a1a2e, #16213e, #e0e0e0), 반응형 grid-3, 카드·테이블·손익/strength 색상
- **app.js**: API 베이스 `/api/v4`, `localStorage`+prompt API Key, fetch 시 `X-Internal-API-Key`, 탭별 로드(Overview: `/dashboard/summary`, `/signals/top`; DESK: `/signals/desk/{id}`; 포지션: `/positions/pnl-summary`, `/positions/open`, `/positions/history`; 자금: `/fund/status`, `/fund/daily-pnl`; 분석: `/signals/stats`, `/signals/strength-analysis`), 60초 자동 새로고침, `formatNumber`/`formatPnl`/`strengthBar`/`renderTable`

### STEP B-5: 정적 파일 서빙

- **main.py 백업**: `backups/main.py.bak_20260220_N` (md5: `723833fb77cba268f23b1bc9b3c434dc`)
- **main.py 수정**: `_dashboard_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "dashboard"` 후 `app.mount("/dashboard", StaticFiles(directory=str(_dashboard_dir), html=True), name="dashboard")` 추가
- **v4_dashboard_static.py**: 미생성 (StaticFiles 마운트만 사용)

### STEP B-6: API 재시작 및 테스트

- **⚠️ DANGER ZONE** — 재시작 전 OPEN 포지션 카운트 확인, 재시작 후 동일 검증 (A1)
- `systemctl restart kis-v41-api` 후 `curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/dashboard` → 200 기대
- 브라우저: `http://<서버IP>:8002/dashboard` 접속 후 API Key 입력, Overview·DESK·포지션·자금·분석 탭 및 60초 자동 새로고침 확인

---

## 서비스 확인 (전체 완료 후)

```bash
systemctl is-active kis-v41-api kis-v41-scheduler kis-v41-monitor \
  kis-webapp-api kis-v41-minute-collector kis-v41-position-monitor
```

---

## Git 커밋

```bash
cd /root/kis-autotrade-v4
git add -A && git status
git commit -m "[V4.1] feat: 시그널 60일 백필 + 웹 대시보드 프론트엔드 - 20260220"
```

---

## 롤백 절차

- **작업A**: `DELETE FROM v4_signals WHERE source = 'backfill';` 후 `rm scripts/backfill_signals.py`
- **작업B**: `rm -rf frontend/dashboard/`, main.py 원복(`cp backups/main.py.bak_20260220_N backend/app/main.py`), `systemctl restart kis-v41-api`

---

## 보고표 (실행 후 채움)

| 항목 | 결과 | 판정 |
|------|------|------|
| 백필 총 건수 | (백필 실행 후) | (≥50,000 기대) |
| /dashboard HTTP 200 | (재시작 후) | |
| OPEN 포지션 보존 | (재시작 전후 동일) | /N |
| 6개 서비스 active | (재시작 후) | /6 |
