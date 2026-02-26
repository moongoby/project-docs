# 백테스트 대시보드 구현 런북 (수정)

- 문서: BT-DASHBOARD-RUNBOOK-001
- 작성일: 2026-02-25
- 기준 기획서: BT-DASHBOARD-PLAN-001-20260225.md
- 변경: STEP 8.5 추가, STEP 10 "CEO 승인 대기" → "즉시 실행"

---

## 최종 실행 순서 (수정)

| 순서 | 단계 | 비고 |
|------|------|------|
| 1 | STEP 1 – 사전 점검 | |
| 2 | STEP 2 – DB 테이블 생성 | |
| 3 | STEP 3 – BtDataWriter | |
| 4 | STEP 4 – API | |
| 5 | STEP 5 – 라우터 등록 | |
| 6 | STEP 6 – 프론트엔드 | |
| 7 | STEP 7 – 네비게이션 | |
| 8 | STEP 8 – 검증 | |
| 9 | **STEP 8.5 – 기획서 문서 저장 & push** | **추가** |
| 10 | STEP 9 – 구현 보고서 & push | |
| 11 | **STEP 10 – 서비스 재시작 (즉시 실행)** | **승인 대기 → 즉시** |

---

## STEP 8.5 – 기획서 문서 작성 & 저장 (10분)

**파일:** `/root/kis-autotrade-v4/report/v41/BT-DASHBOARD-PLAN-001-20260225.md`

기획서 본문은 위 경로에 이미 작성되어 있음. 아래만 실행.

```bash
# 기획서를 project-docs에도 저장
cp /root/kis-autotrade-v4/report/v41/BT-DASHBOARD-PLAN-001-20260225.md \
   /root/project-docs/kis-autotrade-v4/reports/

cd /root/project-docs
git add -A
git commit -m "docs: BT-DASHBOARD-PLAN-001 백테스트 대시보드 기획서"
git push origin master

# URL 검증
curl -s -o /dev/null -w "%{http_code}" \
  https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/BT-DASHBOARD-PLAN-001-20260225.md
# 기대: 200
```

---

## STEP 10 – 서비스 재시작 (즉시)

재시작 전 상태 기록 → 재시작 → 5초 대기 후 검증 → API 엔드포인트 검증.

```bash
# 재시작 전 상태 기록
echo "=== 재시작 전 ==="
date
systemctl is-active kis-v41-api

# 재시작
sudo systemctl restart kis-v41-api

# 5초 대기 후 검증
sleep 5
echo "=== 재시작 후 ==="
systemctl is-active kis-v41-api
curl -s http://localhost:8003/health
journalctl -u kis-v41-api --since "1 min ago" | grep -i "phase\|scheduler\|started\|backtest\|bt_dashboard"
journalctl -u kis-v41-api --since "1 min ago" | tail -20

# API 엔드포인트 검증
curl -s http://localhost:8003/api/v1/backtest/sessions | python3 -m json.tool | head -5
curl -s http://localhost:8003/api/v1/backtest/readiness | python3 -m json.tool | head -10
# 기대: {"count": 0, "sessions": []}
# 기대: {"all_ready": false, "checklist": [...], "strategies": []}
```

### 재시작 실패 시 롤백

```bash
# main.py 백업에서 복원
cp /root/kis-autotrade-v4/backend/app/main.py.bak /root/kis-autotrade-v4/backend/app/main.py
sudo systemctl restart kis-v41-api
# CEO에게 실패 원인 보고
```

---

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-02-25 | STEP 8.5 추가, STEP 10 즉시 실행으로 변경, 런북 최초 작성 |
