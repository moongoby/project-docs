# DESK 역할 분담 적용 로드맵

> 문서번호: DESK-ROLE-SEPARATION-ROADMAP
> 버전: 1.0
> 일자: 2026-02-26
> 상위 문서: DESK-ROLE-SEPARATION-FRAMEWORK.md, DESK2-DISCOVERY-STRATEGY-SPEC.md

---

## 섹션 13. 다른 DESK 적용 가이드

이 프레임워크는 DESK1·3·4·5에도 동일하게 적용 가능합니다.

| DESK | 발굴 역할 | 전략 역할 |
|------|-----------|-----------|
| **DESK1** (초단타/스캘핑) | 틱 레벨에서 비정상적 움직임 감지 | 1분 이내 진입·청산 |
| **DESK2** (단타) | 7조건 발굴 (갭·장초반·VI·장중급등·조정·업종·과매도) | watchlist 기반 stalking, CS Score 경쟁 | 
| **DESK3** (단기스윙 3~10일) | 일봉 기준 추세 전환·돌파 종목 감지 | 일봉 기반 진입 타이밍·보유·청산 |
| **DESK4** (중기스윙 20~40일) | 주봉 기준 추세 형성·업종 변화 종목 감지 | 주봉 기반 포지션 구축·관리 |
| **DESK5** (장기 90~120일) | 펀더멘탈+기술적 저점 종목 감지 | 분할 매수·장기 보유·목표가 관리 |

각 DESK에서 **역할 분담 테스트(프레임워크 섹션 2)**를 동일하게 적용하면, 역할 침범을 방지할 수 있습니다.

---

## 전체 STAGE 1~4 일정

### STAGE 1 – 발굴 재설계 (P0, 약 4시간)
**커서 ID:** DESK2-DISCOVERY-REDESIGN-001

| 순서 | 파일 | 작업 |
|------|------|------|
| 1 | models/discovery_signal.py | eligible_strategies, state_data, time_slot, discovery_type 추가 |
| 2 | layer1_discovery/c1_gap_discovery.py | 체결강도·스프레드 제거, 새 점수 체계 |
| 3 | layer1_discovery/c2_opening_strong.py | 박스 돌파 제거, 장 초반 강세 감지 |
| 4 | layer1_discovery/c3_vi_explosion.py | 호가 잔량 제거, 새 점수 |
| 5 | layer1_discovery/c4_intraday_surge.py | VWAP 크로스 제거, 장중 급등 감지 |
| 6 | layer1_discovery/c5_pullback_discovery.py | 피보나치·양봉 제거, 급등 후 조정 감지 |
| 7 | layer1_discovery/c6_sector_lag.py | 상관계수 제거, 대장주-후발주 감지 |
| 8 | layer1_discovery/c7_oversold_rebound.py | 볼린저 반등 제거, 과매도 감지 |
| 9 | desk2_config.yaml | discovery_redesign 섹션 추가 |

### STAGE 2 – 전략 재설계 (P0, 약 5시간)
**커서 ID:** DESK2-STRATEGY-REDESIGN-001

watchlist 기반 stalking, 발굴에서 분리된 판단 로직 이관, CS Score 독립 계산.

### STAGE 3 – 오케스트레이션 + 백테스터 수정 (P1, 약 3시간)
**커서 ID:** DESK2-ORCHESTRATION-REDESIGN-001

복수 전략 CS Score 경쟁 로직, 최고 점수 전략 선택.

### STAGE 4 – 백테스트 재실행 및 검증 (P1, 약 2시간)
**커서 ID:** DESK2-REDESIGN-BT-001

동일 기간 재실행하여 v1.0 대비 성과 비교.
