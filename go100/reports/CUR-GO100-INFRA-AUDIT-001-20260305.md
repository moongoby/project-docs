---
project: GO100
task_id: T-008-INFRA-AUDIT
completed_at: 2026-03-05T18:16:00+09:00
---
# T-008 인프라 통합 감사

## 1. V3 모의투자 상태

- **주의**: 지시서의 쿼리 컬럼명 오류(id→session_id, stock_code→ticker, side→trade_type) 수정 후 실행
- ACTIVE 세션: session_id=2, strategy_card_id=35, created=2026-02-27 06:54:41 UTC
- 오늘(2026-03-05) 거래: 0건
- 최근 5건: NONE (go100_paper_trades 테이블 데이터 없음)

## 2. Closing Report Cron

- /etc/cron.d/go100_closing_report: **CRON_NOT_FOUND** (파일 없음)
- generate_closing_report.py: **SCRIPT_NOT_FOUND** (/root/kis-autotrade-v4/scripts/go100/ 에 없음)
- crontab -l "closing" 검색: **NO_CLOSING_IN_CRONTAB**
- 조치 필요: closing report 스크립트 및 cron 등록 미완료 상태

## 3. Nginx WS/SSE

- SSE notifications (8002): HTTP **401** (인증 필요)
- SSE trading dashboard (8002): HTTP **401** (인증 필요)
- /ws/ 라우팅 대상:
  - go100 nginx: /ws/ 전용 라우트 없음, `/` 경로에 `Upgrade` 헤더 처리 → 8003 아님, go100_frontend(3000)로 라우팅
  - kis-autotrade nginx: `/ws/` → 8003 (V4.1 WebSocket 전담)
- 권고: GO100은 SSE 2채널(notifications/stream, dashboard/stream) 사용. FE useWebSocket 훅이 있다면 nginx go100 설정에 /ws/ 블록을 추가하여 8002로 라우팅 필요 여부 확인 요함. 현재 미설정.

---
## 저장 정보
- 서버 경로: /root/project-docs/go100/reports/CUR-GO100-INFRA-AUDIT-001-20260305.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-INFRA-AUDIT-001-20260305.md
