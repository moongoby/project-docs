Task ID: T-200 제목: 03-07 장전 사전점검 + T-187/T-189 코드 적용 검증 우선순위: P0-CRITICAL 예상 소요: 20분 선행: 없음 (03-07 08:30 KST 이전 완료)

배경: T-187에서 exit_manager.py SL/TP/TIMEOUT이 변경되었고(854466b8), T-189에서 BEAR FunnelScore 동적 threshold가 적용되었다(7df7dc81). 03-07 장개시 전에 코드가 실제 런타임에 반영되는지 검증해야 한다.

수행 내용:

서비스 상태 확인: systemctl status kis-v41-api kis-v41-monitor kis-v41-scheduler kis-v41-minute-collector redis-server postgresql
Redis 연결 확인: curl -s http://localhost:8003/health | python3 -m json.tool → redis:connected 확인
DB 무결성: psql -c "SELECT count(*) FROM strategy_cards" → 60건, SELECT count(*) FROM v4_positions WHERE status='OPEN' → 0건
exit_manager.py 런타임 값 확인: grep -n "sl_pct\|tp_pct\|timeout_min" /root/kis-autotrade-v4/backend/app/services/trading/exit_manager.py → D-ORB SL 0.018/TP 0.01/TIMEOUT 90, D4 SL 0.015, D6 TP 0.01/TIMEOUT 90 확인
FunnelScore BEAR threshold 확인: grep -n "bear_min_score" /root/kis-autotrade-v4/backend/config/funnel_score.yaml → 0.28 확인, grep -n "bear\|macro_regime" /root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py → BEAR 동적 분기 존재 확인
크론 확인: crontab -l && ls /etc/cron.d/ → monitor_virtual_run 5개 액션, data_integrity, snapshot 등 확인
일봉/분봉 데이터 최신성: psql -c "SELECT max(date) FROM v4_ohlcv_daily" → 03-06, psql -c "SELECT max(collected_at) FROM v4_ohlcv_minute" → 03-06 확인
KIS 토큰 유효성: curl -s http://localhost:8003/api/v4/health/kis-token | python3 -m json.tool

성공 기준: 8항목 ALL PASS. 1건이라도 FAIL 시 즉시 원인 보고 후 수정. 금지: kis-v41-* 서비스 재시작 금지(점검만), strategy_cards 변경 금지. 백업: 불필요 (읽기 전용 점검). 보고서: CUR-V41-0307-PRECHECK-001-20260307.md 보고 규칙: push 후 GitHub URL + 커밋 URL + HANDOVER URL + HTTP 200 확인 필수 (CEO-DIRECTIVES 섹션 4-9).