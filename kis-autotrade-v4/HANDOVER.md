# HANDOVER – KIS AutoTrade V4.1 DESK 시스템
> 최종 업데이트: 2026-02-28 (VE-002 반영)
> 관리자: CEO (moongoby)
> 용도: 모든 AI 세션(웹 Claude, Cursor, Claude Code) 시작 시 필수 읽기

---

## 1. 프로젝트 개요
- KIS AutoTrade V4.1: 한국투자증권 API 기반 AI 자동매매
- 5개 DESK (60개 strategy cards, 14개 OPEN positions)
- 서버: root@211.188.51.113, DB: PostgreSQL kisautotrade
- 225 테이블, 15.7GB, 일봉 3년치 (2,611,905 rows)
- 투자자별 수급 데이터 (261,000 rows), 뉴스 214만건

---

## 2. 완료된 작업

| Task ID | 날짜 | 커밋 | HTTP | 핵심 결과 |
|---------|------|------|------|-----------|
| PHASE1-001 | 02-27 | ✓ | 200 | TOP-20 WR 78.7%, 누적 +785%, 생애주기 4클러스터 |
| PHASE2-001 | 02-28 | ✓ | 200 | 11변수, OOS 정밀도 76%, TREND WR 67.7% |
| PHASE2B-001 | 02-28 | 93e67ae | 200 | L3+X9 정밀도 90%, Birth+1min WR 95.3%, X9 AUC 0.851 |
| DB-TABLE-CATALOG | 02-28 | f263e40 | 200 | 225테이블 카탈로그 |
| ROLE-DEFINITION | 02-27 | ✓ | 확인필요 | 5-DESK 생애주기, 승격/강등 |
| PHASE2C-001 | 02-28 | ✓ | 200 | 일봉 50변수, 정밀도 82%, NEW 3.8% (실패) |
| PHASE2D-001 | 02-28 | ✓ | 200 | 개인수급 AUC<0.55, CMB4 0.636, Birth WR 97.2% |
| DESIGN-SPEC-v3.0 | 02-28 | ✓ | 200 | 패러다임 전환: DESK=풀관리, 카드=타이밍 |
| PHASE2E-001 | 02-28 | a167b87 | 200 | NEW 229종목 역추적, DESK5→4→3 100% 포착, 4 TYPE 분류 |
| VALIDATION-ENGINE-001 | 02-28 | ✓ | 200 | 가설검증엔진 5모듈, Pipeline Precision 6.9%, 97변수 |
| VALIDATION-ENGINE-002 | 02-28 | 57b6de5f | 200 | **Precision 6.9%→90.3% 달성**, 118변수, 20핵심, L3=0 발견 |

---

### SUPER-ANT-STUDY-001 (2026-02-27)
- 한국 슈퍼개미 7인 심층 조사 완료
- 조사 대상: 김정환, 남석관, 이정윤, 홍인기, 시간여행TV, 배진한, 세력주 매매 그룹
- 핵심 발견:
  - 글로벌 대가 전략과 90%+ 수렴 확인
  - 한국 고유 알파: 테마 반복성, 소형주 세력 패턴, 정치/계절 사이클, 동반수급 실시간 추적
  - P0 변수 4개 도출: THEME_CYCLE, SMALL_CAP_QUALITY, DUAL_FLOW, SEC_LEADER_FLAG v2
  - P1 변수 3개: MKT_SEASON, FORCE_ACC, D_D1_D2_ENTRY
  - P2 변수 2개: BJ_SCORE, KJH_CYCLE
- CEO 지시서: D-008-KR로 등록 완료

---

## 3. 진행 중 작업

| Task ID | 상태 | 내용 |
|---------|------|------|
| (현재 없음) | | |

---

## 4. 보류/미시작

| 항목 | 선행조건 | 우선순위 |
|------|----------|----------|
| Phase 2 진입최적화 | 2E 완료 후 발굴확정 | 다음 |
| Phase 3 청산최적화 | Phase 2 완료 | 그다음 |
| Phase 4 DESK3-5 확장 | Phase 3 완료 | 후순위 |
| Phase 5 DESK3-5 전략 | Phase 4 완료 | 후순위 |
| Phase 6 통합테스트 | Phase 5 완료 | 최종 |
| 기획서 v3.1 | 2E 결과반영 | 2E 직후 |
| BT-BLANK-SLATE-001 | 재커밋 필요 | 문서정리 |

---

## 5. 핵심 발견 (누적)

### 발굴
- L3+X9 = 최강 조합 (정밀도 90%, REPEAT 종목)
- NEW(42.1%) D-1 예측불가 (AUC 최대 0.644)
- 일봉 패턴만으로 NEW 적중 3.8% (실패)
- 개인수급 단독 무의미, CMB4(수급분산) 0.636
- Phase 2E: DESK5→4→3 역추적 recall 100%, 4 TYPE 분류 (Slow/Mid/Short/Sudden)
- Pipeline Precision = 6.9% → **Scorecard P92로 90.3% 달성**
- 생존자 편향 확인: DESK3 이벤트만으로는 precision 부족, 추가 필터 필수
- 가설 검증 엔진 5모듈 구축 완료 (118변수, 10-Axis 107조건 검증)
- "강하게 오른 놈이 또 오른다" = REPEAT이 수익 핵심
- **L3 = 0 for ALL NEW stocks: L3 기반 필터는 REPEAT에만 적용 가능**
- **NEW 종목 핵심 변수: V_TRADE_AMOUNT, V_RVOL, P_CHG_5D, N_D1_COUNT, SEC_LEADER_FLAG, OBV_NEW_HIGH**
- **D-offset(D-3,D-5,D-10) 선행 지표 발견 실패 — 동시 지표 특성 재확인**
- **Wyckoff/VCP 패턴: 급등 초기 종목에 부적합 (발생률 ~0%)**
- **CAN SLIM 펀더멘털: 판별력 미약 (AUC < 0.6)**
- **SEC_LEADER_FLAG (AUC 0.838) = NEW 종목 발굴 핵심 신규 변수**

- **한국 슈퍼개미 공통 원리**: 거래량/수급이 최강 변수(글로벌 동일), 테마 반복성이 한국 고유 알파, 소형주(700억 이하)+흑자+테마 조합이 급등 공식, 대장주 1등만 매매(2등 금지), 세력 매집→보합(120일선 수렴)→돌파가 Wyckoff+VCP와 동일 구조, 사계절론(Q2 공격/Q4 방어)이 시장 방향 M 변수와 연결
- **SEC_LEADER_FLAG AUC 0.838** → v2로 업그레이드 시 거래대금 1위+최초 돌파 조건 추가 예정
- **DUAL_FLOW**: 기관+외국인 동시 순매수가 한국 시장 최강 수급 신호 (이정윤 3년 100억 전략의 핵심)

### 다음 단계 (D-008-KR)
- [ ] P0: feature_engine.py에 THEME_CYCLE_100B_COUNT, THEME_CYCLE_UL_COUNT 추가
- [ ] P0: universe_builder.py에 SMALL_CAP_QUALITY 플래그 추가
- [ ] P0: feature_engine.py에 DUAL_FLOW_5D, DUAL_FLOW_20D 추가
- [ ] P0: SEC_LEADER_FLAG를 v2로 업그레이드 (거래대금 1위 + 최초 돌파)
- [ ] P1: MKT_SEASON 분기별 공격도 가중치 구현
- [ ] P1: FORCE_ACC (120일선 수렴도 + 급등봉 횟수 + 갭상승) 추가
- [ ] P1: strategy_card에 "대장주 장대양봉 D+1" 카드 추가
- [ ] P2: BJ_SCORE 100점 스코어카드 구현
- [ ] P2: KJH_CYCLE (5년 우상향 + PER 밴드) 구현

### 진입
- Birth Point + 1min WR 95.3%
- 09:05 고정진입 비효율
- 유형별(TREND/REVERSAL/BORDER) 진입 필요
- 신고가 돌파, 박스 돌파, 눌림목 반등 트리거 정의됨

### 데이터
- 히스토리컬 호가/틱 미보유 (실시간만)
- 프로그램매매 1일분만 존재
- ohlcv_daily 3년치로 MA60, MA120 계산 가능 (Phase 2C에서 미활용)

---

## 6. 웹 Claude 인수인계 사항

> Cursor/Claude Code는 작업 완료 시 이 섹션을 반드시 업데이트한다.
> 웹 Claude는 새 세션 시작 시 이 섹션을 최우선 확인한다.

### 최신 상태 (2026-02-28, VE-002 완료)
- VALIDATION-ENGINE-002 완료: **Pipeline Precision 6.9% → 90.3% 달성**
- 118개 변수 (97 기존 + 21 신규), 10-Axis 107조건 검증
- Scorecard 기반 필터링: AUC≥0.75, 20변수, P92 임계값
- Walk-Forward 안정: Mean 87.3% ± 0.8%, Min 86.5%
- **핵심 발견: L3=0 for ALL NEW stocks — NEW/REPEAT 분리 필수**
- 코드 수정: `feature_engine.py`(+Wyckoff/VCP/OBV/CANSLIM/Sector), `universe_builder.py`(+assign_control_dates)

### 웹 Claude가 해야 할 일
1. **발굴 방식 확정**: Scorecard P92 (90.3%) 기반 발굴 vs 추가 최적화
2. **NEW vs REPEAT 분리 설계**: NEW(scorecard) + REPEAT(L3+X9) 통합 파이프라인
3. **Phase 2 진입최적화 시작**: scorecard 통과 종목에 Birth Point 진입 구현
4. 기획서 v3.1 업데이트: Precision 90.3%, NEW/REPEAT 분리, 20변수 scorecard 반영
5. CEO-DIRECTIVES에 D-008(NEW/REPEAT 분리), T-005(Scorecard 풀 필터) 추가 검토

### 대표님 확인 필요 사항
- Scorecard P92 (Pool 93, Recall 62%) vs P95 (Pool 55, Recall 38%) 선택
- NEW vs REPEAT 분리 전략 승인
- Phase 2 진입최적화 착수 시점

### 주의사항
- CEO "단순 사고 금지" 원칙 (D-001)
- 수급이 본질 (D-002), 개인매매 포함
- DESK = 풀관리, 타이밍 정확히 알 필요 없음 (D-003)
- 신고가 돌파 매매 로직 필수 (D-005)
- **Scorecard 필터 필수: DESK3 이벤트만으로 풀 운영 불가**
- **L3는 REPEAT에만 유효, NEW는 별도 파이프라인**

---

## 7. 업데이트 규칙

### Cursor/Claude Code
1. 작업 시작 전: 이 파일 + CEO-DIRECTIVES.md cat으로 읽기
2. 보고서 상단에 체크포인트 기록 (직전Task, 현재단계, CEO지시, cards/positions)
3. 작업 완료 후: 섹션 2~6 업데이트
4. 섹션 6 "웹 Claude 인수인계" 반드시 갱신
5. git push + HTTP 200 확인
6. 보고서 마지막에 "HANDOVER 업데이트: {커밋해시}" 기록

### 웹 Claude
1. 새 세션: 이 파일 크롤링
2. 섹션 6 최우선 확인
3. 지시서에 이 파일 업데이트 의무 포함

---

## 버전 이력
| 버전 | 날짜 | 변경자 | 변경 |
|------|------|--------|------|
| v1.0 | 2026-02-28 | 웹Claude | 초판 – Phase 1~2E 현황 |
| v1.1 | 2026-02-28 | Opus4.6 | 2E 완료, VALIDATION-ENGINE-001 완료, Precision 6.9% |
| v1.2 | 2026-02-28 | Opus4.6 | VE-002 완료, Precision 90.3% 달성, L3=0 발견, 118변수, NEW/REPEAT 분리 |
| v1.3 | 2026-02-27 | — | 한국 슈퍼개미 7인 전략 통합, D-008-KR 등록, P0 변수 4개·P1 3개·P2 2개 도출, 글로벌 대가 90%+ 수렴 확인 |
