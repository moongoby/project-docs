Task ID: T-226 — 03-09 장전 사전점검 + root 크론 3건 일괄 설치

상태: COMPLETED (본 세션에서 실행 완료)

근거:
- /etc/cron.d/v41_desk5_scan, v41_desk2_pool_link, v41_evolution_loop 모두 존재 및 root 소유/644 권한 확인
- kis-v41-api/monitor/scheduler/redis/postgresql active, minute-collector inactive(장외) 상태 확인
- DB 무결성: strategy_cards=60, v4_positions OPEN=0
- 백업 파일: /root/backup/kisautotrade_20260309_pre.sql.gz 생성 확인
- PRE_SOURCE_FILTER grep=3 (cte_pipeline.py)

참고:
- 상세 내용은 CUR-V41-0309-PRECHECK-001-20260309.md에 정리됨.
