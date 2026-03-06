Task ID: T-235 — CEO P0 변수 SMALL_CAP_QUALITY + SEC_LEADER_FLAG v2 구현

상태: BLOCKED (선행 작업 T-230 미완료)

사유:
- 지시서에 선행 작업으로 T-230(감사 + THEME_CYCLE/DUAL_FLOW 완료 후)이 명시되어 있으나, 해당 변수 구현·검증이 아직 이루어지지 않음.
- SMALL_CAP_QUALITY/SEC_LEADER_FLAG v2까지 일괄 반영 시 FunnelScore 전체 구조가 동시에 변하므로, T-230 결과 없이 진행하는 것은 리스크 과다.

요청사항:
- 먼저 T-230을 통해 4종 변수 감사·2종 구현을 완료하고, FunnelScore 영향도를 검증한 뒤 T-235를 재지시하는 것이 안전.
