---
project: KIS
task_id: T-183
completed_at: 2026-03-06 15:58 KST
---

# T-183 실행 결과 — Root 인프라 일괄 적용

## 지시서
파일: KIS_20260306_154506_BRIDGE.md
제목: Root 인프라 일괄 적용 — Nginx reload + Evolution Loop cron + 스냅샷 cron + HANDOVER v10.18 갱신

---

## Part A — Root 스크립트 실행 결과

### A-1. t173_root_ops.sh (단계별 수동 실행)

**CEO 절대 규칙 준수**: kis-v41-api, kis-v41-monitor, kis-v41-scheduler 재시작 금지.
스크립트 내 `systemctl restart kis-v41-api` 라인(L128) 제외 후 단계별 수동 실행.

**STEP 0 — Nginx 백업**
```
stdout: 이미 .bak.t173 파일 존재 (이전 T-173 실행에서 생성됨)
stderr: none
```

**STEP 1 — Nginx /manager/ 블록 확인**
```
stdout:
54:    location /manager/ {
126:    location /manager/ {
[V4.1] Nginx /manager/ 이미 존재 (kis-autotrade 파일 2곳)
47:    location /manager/ {
[GO100] Nginx /manager/ 이미 존재
stderr: none
```

**STEP 2 — cron 현황**
```
stdout:
ls /etc/cron.d/ | grep snapshot:
  go100_manager_snapshot  (2026-03-06 13:32)
  v41_manager_snapshot    (2026-03-06 13:32)
→ 2건 이미 등록됨
stderr: none
```

**STEP 4 — 서비스 재시작**
```
stdout:
[OK] nginx reload 완료        ← sudo /bin/systemctl reload nginx
[OK] go100 restart 완료       ← sudo /bin/systemctl restart go100
[OK] go100-frontend restart 완료 ← sudo /bin/systemctl restart go100-frontend
[SKIP] kis-v41-api — CEO 절대 규칙(재시작 금지) 준수
stderr: none
```

### A-2. install_cron_t178.sh (Evolution Loop cron 설치)

**시도 1**: sudo tee /etc/cron.d/go100_evolution_loop
```
stderr: sudo: a terminal is required to read the password
결과: FAIL — tee가 claudebot NOPASSWD 목록에 없음
```

**시도 2**: cat | sudo tee (동일 원인으로 FAIL)

**소스 파일 확인**:
```
-rw-rw-r-- 1 claudebot claudebot 551 Mar 6 15:32 /root/kis-autotrade-v4/scripts/go100/go100_evolution_loop.cron
내용:
# GO100 Evolution Loop — 24시간 자동 가동
0 9-15 * * 1-5 root .venv/bin/python3 scripts/go100/run_evolution_loop.py >> /var/log/go100/evolution_loop.log 2>&1
0 0,4,16,20 * * 1-5 root cd /root/kis-autotrade-v4 && .venv/bin/python3 scripts/go100/run_evolution_loop.py >> /var/log/go100/evolution_loop.log 2>&1
0 6,18 * * 0,6 root cd /root/kis-autotrade-v4 && .venv/bin/python3 scripts/go100/run_evolution_loop.py >> /var/log/go100/evolution_loop.log 2>&1
```

**결론**: B-3 검증 FAIL. Root에서 수동 실행 필요:
```bash
cp /root/kis-autotrade-v4/scripts/go100/go100_evolution_loop.cron /etc/cron.d/go100_evolution_loop
chmod 644 /etc/cron.d/go100_evolution_loop
```

---

## Part B — 검증 9항목 상세 결과

### B-1. go100.newtalk.kr/manager/snapshot.json
```
명령: curl -s -o /dev/null -w "%{http_code}" https://go100.newtalk.kr/manager/snapshot.json
결과: HTTP 200
판정: PASS ✅
```

### B-2. trading41.newtalk.kr/manager/snapshot.json
```
명령: curl -s -o /dev/null -w "%{http_code}" https://trading41.newtalk.kr/manager/snapshot.json
결과: HTTP 200
판정: PASS ✅
```

### B-3. Evolution Loop cron
```
명령: ls /etc/cron.d/ | grep evolution
결과: (출력 없음)
명령: sudo /usr/bin/crontab -u root -l | grep -c run_evolution_loop
결과: 0
판정: FAIL ❌ — /etc/cron.d/go100_evolution_loop 미설치 (root 수동 실행 필요)
```

### B-4. 스냅샷 갱신 cron
```
명령: ls /etc/cron.d/ | grep snapshot
결과:
  go100_manager_snapshot
  v41_manager_snapshot
건수: 2건
판정: PASS ✅ (≥2 달성)
```

### B-5. 서비스 상태
```
명령: sudo /bin/systemctl is-active <svc>
결과:
  kis-v41-api: active
  go100: active
  go100-frontend: active
  redis-server: active
  nginx: active
  postgresql: active
판정: PASS ✅ (6/6 active)
```

### B-6. Redis PING
```
명령: redis-cli ping
결과: PONG
판정: PASS ✅
```

### B-7. RESEARCH 가설 건수
```
명령: sudo /usr/bin/psql -h localhost -U kis_admin -d kisautotrade -t -c "SELECT count(*) FROM go100_strategy_hypotheses WHERE source_type='RESEARCH'"
결과: 11
판정: PASS ✅ (≥5 달성, T-180 RES-201~205 5건 포함)
```

### B-8. .env Evolution Loop 확인
```
명령: grep "GO100_EVOLUTION_LOOP_ENABLED" /root/kis-autotrade-v4/.env
결과: GO100_EVOLUTION_LOOP_ENABLED=true
판정: PASS ✅
```

### B-9. data/go100/research/ 디렉토리
```
명령: ls -la /root/kis-autotrade-v4/data/go100/research/
결과: drwxrwxr-x 2 claudebot claudebot 4096 Mar 6 15:32 .
판정: PASS ✅ (존재)
```

### B 검증 요약표
| # | 항목 | 결과 |
|---|------|------|
| B-1 | go100.newtalk.kr/manager/snapshot.json | 200 ✅ PASS |
| B-2 | trading41.newtalk.kr/manager/snapshot.json | 200 ✅ PASS |
| B-3 | Evolution Loop cron (/etc/cron.d/) | ❌ FAIL — root 설치 필요 |
| B-4 | 스냅샷 cron 2건 | ✅ PASS |
| B-5 | 서비스 6개 active | ✅ PASS |
| B-6 | Redis PONG | ✅ PASS |
| B-7 | RESEARCH 가설 11건 (≥5) | ✅ PASS |
| B-8 | GO100_EVOLUTION_LOOP_ENABLED=true | ✅ PASS |
| B-9 | data/go100/research/ 존재 | ✅ PASS |
**총계: 8/9 PASS** (B-3만 FAIL)

---

## Part C — HANDOVER.md + 보고서 push

### C-1. HANDOVER.md v10.18 갱신
```
파일: /root/project-docs/kis-autotrade-v4/HANDOVER.md
변경:
- 버전 헤더: v10.17 → v10.18 (T-183, T-180 내용 추가)
- 완료 작업 테이블: T-183, T-180 행 추가
- 버전 이력: v10.18 행 추가
```

### C-2. 보고서 작성
```
파일명: CUR-V41-ROOT-INFRA-T183-001-20260306.md
경로: /root/project-docs/kis-autotrade-v4/reports/
크기: 133 insertions
```

### C-3. Git push
```
cd /root/project-docs
git add kis-autotrade-v4/HANDOVER.md kis-autotrade-v4/reports/CUR-V41-ROOT-INFRA-T183-001-20260306.md
git commit: d5ed841
git push: d5ed841..ac1d94a master → master (2회 push: 본문 + 커밋해시 업데이트)
최종 커밋: ac1d94a
stdout:
  [master d5ed841] [V4.1] T-183: Root 인프라 일괄적용 — Nginx+cron+EvolutionLoop 자동가동 확인 8/9 PASS + HANDOVER v10.18
  To github.com:moongoby/project-docs.git
     8c7fecc..d5ed841  master -> master
  [master ac1d94a] docs: T-183 보고서 커밋해시 업데이트 (d5ed841)
  To github.com:moongoby/project-docs.git
     d5ed841..ac1d94a  master -> master
stderr: none
```

### C-4. HTTP 200 확인
```
보고서: curl 200 ← https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-ROOT-INFRA-T183-001-20260306.md
HANDOVER: curl 200 ← https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md
```

### C-5. 링크 정보
```
보고서: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-ROOT-INFRA-T183-001-20260306.md
커밋: https://github.com/moongoby/project-docs/commit/ac1d94a
HANDOVER: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/HANDOVER.md
HTTP: 200 확인 완료
```

---

## 잔여 과제 (Root 수동 실행 필요)

```bash
# B-3 해결: Evolution Loop cron 등록
cp /root/kis-autotrade-v4/scripts/go100/go100_evolution_loop.cron /etc/cron.d/go100_evolution_loop
chmod 644 /etc/cron.d/go100_evolution_loop
echo "[OK] $(ls -la /etc/cron.d/go100_evolution_loop)"
```

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (T-183은 인프라 작업 — 코드 변경 없음, phase-2c-command-center)
- [x] project-docs 보고서 push 완료 (GitHub raw URL 200 확인)

HANDOVER.md 업데이트 완료: ac1d94a
