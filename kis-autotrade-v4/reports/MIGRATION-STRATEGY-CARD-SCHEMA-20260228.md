# 전략 카드 명명 체계 DB 마이그레이션 보고서

| 항목 | 내용 |
|------|------|
| 문서 ID | MIGRATION-STRATEGY-CARD-SCHEMA-20260228 |
| 작업 일시 | 2026-02-28 KST |
| CEO 지시 근거 | D-003, D-009, D-010, D-011, T-001 |
| 상태 | 완료 |

## 1. 백업

| 항목 | 값 |
|------|-----|
| 백업 파일 | `/tmp/strategy_cards_backup_20260228.sql` |
| 백업 시점 행 수 | 32행 |
| 백업 파일 크기 | 260줄 |

## 2. 스키마 변경

**12개 컬럼 ADD** (기존 컬럼 변경 없음, DROP/RENAME 없음)

| 컬럼 | 타입 | 기본값 | 용도 |
|------|------|--------|------|
| card_code | VARCHAR(20) | NULL | 전략 카드 코드 (예: '1.CH01-C3') |
| card_name | VARCHAR(50) | NULL | 전략 카드 명칭 (예: '시초강세 추격') |
| desk_id | SMALLINT | NULL | DESK 번호 (1~5) |
| situation_code | VARCHAR(3) | NULL | 상황 코드 (CH/DP/BK/GP/CL/HLD) |
| condition_code | VARCHAR(3) | NULL | 컨디션 코드 (C2/C3/C4/C6/C7, DESK2~5는 NULL) |
| card_version | SMALLINT | 1 | 카드 버전 (파라미터 변경 시 증가) |
| parent_card_code | VARCHAR(20) | NULL | 릴레이 체인 선행 카드 코드 |
| relay_order | SMALLINT | NULL | 릴레이 순서 (NULL이면 단독) |
| bar_timeframe | VARCHAR(10) | NULL | 봉 기준 (3m/5m/daily) |
| deactivated_at | TIMESTAMP | NULL | 비활성 일시 |
| deactivation_reason | TEXT | NULL | 비활성 사유 |
| legacy_strategy_id | VARCHAR(10) | NULL | 기존 전략 ID (D2, D6, D7 등) |

## 3. 기존 카드 업데이트

| go100_card_id | 기존명 | card_code | card_name | 변경 범위 |
|---------------|--------|-----------|-----------|-----------|
| 42 | [D6] 상한가→갭 모멘텀 | 1.GP01-C2 | 전상 갭매매 | 새 컬럼만 (strategy_params/risk_params/exit_rules 미변경) |
| 43 | [D7] 종가배팅 트레일링 | 1.CL01-C6 | 종가강세 배팅 | 새 컬럼만 (strategy_params/risk_params/exit_rules 미변경) |

## 4. 신규 카드 삽입

10장 삽입 (DESK1 9장 + DESK2 1장), 전부 `is_active = false`

| go100_card_id | card_code | card_name | desk | 릴레이 | legacy |
|---------------|-----------|-----------|------|--------|--------|
| 45 | 1.DP01-C2 | 전상 눌림반등 | 1 | 단독 | D4 |
| 46 | 1.CH01-C3 | 시초강세 추격 | 1 | C3 ①번 | D8 |
| 47 | 1.DP01-C3 | 시초강세 눌림 | 1 | C3 ②번 | D2 |
| 48 | 1.BK01-C3 | 시초강세 돌파 | 1 | C3 ③번 | D9 |
| 49 | 1.CH01-C4 | 장중급등 추격 | 1 | C4 ①번 | D5 |
| 50 | 1.DP01-C4 | 장중급등 눌림 | 1 | C4 ②번 | D2 |
| 51 | 1.BK01-C4 | 장중급등 돌파 | 1 | C4 ③번 | D9 |
| 52 | 1.CH01-C7 | NEW종목 추격 | 1 | C7 ①번 | D8 |
| 53 | 1.DP01-C7 | NEW종목 눌림 | 1 | C7 ②번 | D2 |
| 54 | 2.DP01 | 폭발후 눌림스윙 | 2 | 단독 | S1 |

## 5. 검증 결과

| 검증 항목 | 예상 | 실제 | 결과 |
|-----------|------|------|------|
| 총 명명 카드 수 | 12 | 12 | PASS |
| C3 릴레이 체인 | CH(1)→DP(2)→BK(3) | CH(1)→DP(2)→BK(3) | PASS |
| C4 릴레이 체인 | CH(1)→DP(2)→BK(3) | CH(1)→DP(2)→BK(3) | PASS |
| C7 릴레이 체인 | CH(1)→DP(2) | CH(1)→DP(2) | PASS |
| 단독 카드 수 | 4 | 4 | PASS |
| 기존 #42 is_active | true | true | PASS |
| 기존 #43 is_active | true | true | PASS |
| 신규 카드 is_active | 전부 false | 전부 false | PASS |
| D6/D7 엔진 호환 | strategy_params 미변경 | 미변경 | PASS |

## 6. 하위 호환성

- `go100_card_id` 기반 기존 로직 영향 없음
- `live_paper_d6_d7.py`의 `load_card_config()`는 `strategy_params->>'strategy_id' IN ('D6','D7')` 기준 조회 — 새 컬럼 무관
- 신규 카드의 `strategy_params`에는 `strategy_id` 미설정 → 엔진에 잡히지 않음
- `legacy_strategy_id` 컬럼으로 기존 전략 ID 역참조 가능
- 테스트 전략 #14, #15는 변경 없음 (card_code = NULL)

## 7. 참고

- 지시서에 "13장"이라 기재되어 있으나, 실제 INSERT SQL은 10건이며 UPDATE 2건 포함 총 12장
- 지시서의 `card_id`는 실제 스키마의 `go100_card_id`로 조정하여 실행
- 엔진 코드 수정은 이번 작업 범위 밖 (RR-1~RR-5 검증 완료 후 별도 진행)
