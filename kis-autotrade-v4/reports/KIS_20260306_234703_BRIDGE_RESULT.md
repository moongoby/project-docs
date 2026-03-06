Task ID: T-221 — 백테스트 승자 가설 실전 적용 (hypothesis_winners)

상태: BLOCKED (선행 작업 T-219 미완료)

사유:
- 지시서에 선행 작업으로 T-219(exit_manager 수정 후)가 명시되어 있으나, /root/kis-autotrade-v4/report 내 `Task ID: T-219` 관련 보고서 및 구현 완료 기록이 없음.
- exit_manager PF/SL 로직 변경 없이 hypothesis_winners.yaml만 선반영 시, 실전/백테스트 일관성 훼손 위험이 있어 CEO D-008-KR 의도에 반함.

요청사항:
- 먼저 T-219(exit_manager 수정) 완료 및 보고서 발행 후, T-221을 재지시하거나 자동 실행 허용 필요.
