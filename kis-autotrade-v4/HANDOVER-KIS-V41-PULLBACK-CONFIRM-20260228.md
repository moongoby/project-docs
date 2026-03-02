# HANDOVER — 눌림확인매매 심층연구 + DESK2 전략최적화 세션 인계서

**문서 ID**: HANDOVER-KIS-V41-PULLBACK-CONFIRM-20260228
**작성일시**: 2026-02-28 KST
**작성자**: Claude Opus 4.6 (CEO 대화창 PM 세션)
**인계 대상**: 새 Claude 세션 (웹 / Cursor / Claude Code)
**목적**: 눌림확인매매(Pull-back Confirmation) 심층연구 착수 + DESK2 6전략 진입·청산 최적화 + 자본 복리 순환 통합 작업을 새 세션에서 즉시 이어갈 수 있도록 전체 맥락 인계

---

## PART 1. 필수 읽기 문서 (새 세션 시작 시 반드시 순서대로 읽을 것)

| 순서 | 문서 | URL |
|------|------|-----|
| 1 | **CEO 지시서 v1.4** | https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CEO-DIRECTIVES.md |
| 2 | **HANDOVER.md (최신 v3.2)** | https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md |
| 3 | **DESK2 기획서 v3.0** | https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/design/DESK2-DESIGN-SPEC-v3.0-20260228.md |
| 4 | **DESK2 멀티컨디션 최종 스펙** | https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/docs/DESK2-MULTI-CONDITION-FINAL-SPEC-20260228.md |
| 5 | CONTEXT | https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CONTEXT.md |
| 6 | 서버/DB 규칙 | https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/kis-v41-rules.md |
| 7 | Claude 규칙 | https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/CLAUDE.md |

**문서 레포만 퍼블릭이다. 코드 레포(kis-autotrade-v4)는 프라이빗이므로 외부 접근 불가. 접근 가능한 것은 `https://github.com/moongoby/project-docs` 뿐이다.**

---

## PART 2. 프로젝트 개요

KIS AutoTrade V4.1 — 한국투자증권 API 기반 AI 자동매매. 서버 root@[SERVER-IP], DB PostgreSQL 16 (kisautotrade), 225 테이블 15.7GB, 일봉 3년 261만행, 1분봉 4,200만+행, 뉴스 214만건, 투자자 수급 26.1만행.

5개 DESK 체계: DESK5(장기풀 D-120~D-20) → DESK4(중기풀 D-40~D-5) → DESK3(단기풀 D-10~D-1, 50~100종목) → **DESK2(당일 실행, 6전략+1탐지)** → DESK1(초단기).

핵심 철학: **"DESK는 오를 만한 종목을 풀로 관리하고, 전략 카드가 타이밍을 기다린다."** DESK=풀 관리자(리콜 우선), 전략=타이밍 감시자(정밀도×타이밍).

---

## PART 3. 전략 명칭 정리 (CEO-DIRECTIVES D-009 + D-011 확정)

### 3-1. 확정된 전략 포트폴리오 (D-011, 2026-02-28)

| ID | 전략명 (한글) | 핵심 변수 | 진입 조건 | 청산 | PF(비용 전) | PF(비용 후) | 상태 |
|----|-------------|-----------|-----------|------|------------|------------|------|
| **D6** | 상따→갭 | UL_ENTRY_TIME, UL_BID_AMOUNT | 오전 상한가+매수잔량100억+ | D+1 시초가 | 13.63 | 9.96 | **PASS** |
| **D5** | 뉴스급등 후 눌림 | NEWS_CATALYST_SCORE, MA_CONVERGENCE_1M | 1파 후 이평선 수렴 진입 | 60분 보유 | 4.21 | 2.43 | CONDITIONAL |
| **D4** | 전일상한가 눌림 | PREV_UL_FLAG, D1_MA20_1M_BREAK | D+1 20분선 돌파 | 60분 보유 | 2.43 | 1.05 | **위험** |
| **D7** | 종가배팅→갭 | CLOSE_BET_SCORE | 14:30 후 수급집중+저점상승 | D+1 시초가 | 2.12 | 1.26 | 주의 |
| **D2** | 3분봉 눌림 | PULLBACK_DEPTH_3M, VP_AT_PULLBACK | 3분봉 5/10선 터치+VP≥120 | 60분 보유 | 1.57 | 1.02 | **위험** |
| **S1** | 거래대금 폭발 후 눌림 | V_TRADE_AMT_10D_PEAK, THEME_ALIVE_FLAG | 10일 500억+유입, 5/10일선 지지+도지 | 60분 보유 | 1.44 | 1.20 | 주의 |
| **C7** | NEW 종목 탐지 | VP≥120+RSI+MA정배열+가격급등5%+ | 장중 실시간 4조건 | 60분 보유 | 1.59 | — | CONDITIONAL |

### 3-2. 폐기된 전략

| ID | 전략명 | 폐기 이유 | PF |
|----|--------|----------|-----|
| D1 | 시초가 진입 | PF 0.89, 모든 5축에서 < 1.3 | 0.89 |
| D3 | 대장→후발 순환 | PF 1.17, 테마 데이터 커버리지 한계 | 1.17 |
| S2 | N일선 눌림 | MA7 PF 1.27 최선, MA10 PF 0.88 최악 | 0.88~1.27 |

### 3-3. 우선순위 배분 (D-011 확정)

**D6(30%) > D7(40%) > D5+D4+D2(30%)** — D6가 유일한 PASS 전략.

---

## PART 4. 이번 세션에서 진행된 핵심 작업

### 4-1. 3개 보고서 완료 (커밋 c42384754754c55ca772131f993bed3083de6c56)

| 보고서 | 핵심 결과 |
|--------|----------|
| **MODE3-REDESIGN-001** | 2파 진입 성공률 0%→98%, PF 2.43, 거래 50→131건. RSI 50~75, 동적깊이(wave1×0.5), V_SHARP+T2, 전조시그널1+. Walk-Forward 73.9% PASS |
| **COST-ADJUSTED-SIM-001** | 왕복비용 0.47%(소형주), 전체 PF -33.6%. D6→9.96(견고), D2→1.02/D4→1.05(위험), S1→1.20 |
| **R23-DECOUPLE-001** | 6전략 2클러스터(D2-D4-D5 / D6-D7-S1), 클러스터간 중복 0%. 옵션B(PF우선+최대2동시) 수익유지율 89.8%, R19 안전장치 적용 |

GitHub: https://github.com/moongoby/project-docs/commit/c42384754754c55ca772131f993bed3083de6c56

### 4-2. 눌림 전략 설계 분석 — 핵심 진단

**CEO 지시**: "눌림 여부와 눌림확인 여부를 구분하여 보고하라", "이평선 터치 건수, 닫기 전에 오르는 건, 이평선 뚫고 하락 후 반등 건을 모두 확인하라"

**진단 결과**: 현재 DESK2 눌림 전략들은 교과서 5단계(종목선정→눌림대기→지지확인→**반등확인후매수**→손절익절) 중 **Step 4 "반등 확인 후 매수"가 전면 부재**. 모든 전략이 이평선 "터치" 또는 깊이 "도달" 시 즉시 진입하며, 반등(양봉+거래량+RSI전환) 확인 없이 포지션을 잡음. 이것이 D2 PF 1.02, D4 PF 1.05의 근본 원인.

**전략별 현황**:

| 전략 | 눌림 감지(Detection) | 반등 확인(Confirmation) | 판정 |
|------|---------------------|----------------------|------|
| D2 | 3분봉 5/10선 터치+VP≥120 | **없음** (터치=진입) | 미충족 |
| D4 | D+1 20분선 돌파 | **없음** (돌파=진입, 가짜돌파 미필터) | 미충족 |
| D5 | 1파 후 이평선 수렴 | **부분** (수렴 자체가 시간경과 내포) | 부분충족 |
| Mode3 | wave1×0.5 깊이 도달 | **없음** (깊이도달=진입) | 미충족 |
| S1 | 5/10일선 지지+도지 | **부분** (도지는 전환 신호이나 다음봉 양봉 미확인) | 부분충족 |

**이미 확보된 반등 확인 연구 자산** (구현에는 미반영):

| 연구 | 핵심 발견 | 활용 방법 |
|------|----------|----------|
| R08 VP 선행성 | VP가 가격 전환보다 **2.27분 선행** | VP 상승전환 = 반등 확인 신호 |
| PULLBACK-ANATOMY Top3 전조 | TS-C4 볼린저스퀴즈(88.6%), TS-C3 20봉신고가(85.7%), TS-B4 거래량폭발양봉(82.4%) | 전조 1개+ = 2파 성공률 82~88% |
| R04 | 시간 대기만으로 PF<1.0 (26분 대기해도 PF 0.88) | 시간이 아닌 **조건 기반 대기** 필수 |
| V_SHARP 형태 필터 | 1~3분 급등 종목 성공률 81.6% | 형태별 차등 적용 |
| Phase F TS-B4 | 거래량폭발양봉 PF 3.23 (Top1 시그널) | 반등 확인의 핵심 캔들 |

### 4-3. 미완료 작업 — CEO 지시 기반 즉시 착수 과제

**CEO 마지막 지시**: "이평선 터치 건이 몇 건인가? 닫기 전에 오르는 건 그리고 이평선 뚫고 하락 후 반등 건은? 눌림확인에 대한 심층있는 연구 후 보고하라"

이 지시에 따라 아래 4개 과제를 수행해야 한다:

---

## PART 5. 즉시 수행 과제 (새 세션 최우선)

### 과제 A: 이평선 기준 눌림 분류 집계

**데이터**: 19,225건 눌림 전수(PULLBACK-ANATOMY-001에서 추출 완료, `/tmp/` JSON 파일 존재)

**분류 기준 — 6개 버킷**:
1. 5선 터치 후 반등 (이평선 미관통)
2. 5선 관통 → 10선 터치 후 반등
3. 10선 관통 → 20선 터치 후 반등
4. 20선 관통 후 반등
5. 20선 관통 후 미반등 (손실 확정)
6. 이평선 미도달 (눌림 깊이 부족)

**산출물**: 각 버킷의 건수, 승률, PF, 평균수익률, 반등까지 소요 봉수

### 과제 B: 반등 확인 신호 유효성 검증

**후보 신호 5가지**:
1. VP 전환(하락→상승) — R08에서 2.27분 선행 확인
2. RSI 바닥 형성 후 상승 전환
3. 양봉 출현(1~3봉 이내)
4. 전조 시그널 TS-C4/C3/B4 중 1개+ 동시 발생
5. 체결강도 120%+ 회복

**산출물**: 각 신호 단독 및 조합의 승률, PF, 진입지연(봉수), 기회손실률. 19,225건 전수 대입.

### 과제 C: 확인 대기 비용 분석

**핵심 질문**: 즉시 진입 vs 1봉/2봉/3봉 조건부 대기의 수익·손실 트레이드오프 정량화.

R04에서 "시간 대기만으로 PF<1.0" 확인되었으므로, **시간이 아닌 조건 기반 대기**의 우위를 수치로 증명해야 함. 전략별(D2/D4/Mode3/S1) 최적 확인 조건 도출.

### 과제 D: 이평선 관통 후 반등 패턴 심층 분석

**분석 항목**: 관통 깊이(이평선 대비 %), 관통 후 반등까지 시간, 관통 시점의 거래량/VP/RSI 특성, 반등 성공 시 수익률 vs 터치 반등 수익률 비교. 관통이 오히려 더 좋은 진입 기회인지 검증.

### 예상 보고서

**파일명**: `CUR-V41-PULLBACK-CONFIRMATION-001-20260228.md`
**경로**: `kis-autotrade-v4/reports/`
**보고 형식** (CEO 지시 REPORT-001 준수):
```
보고서: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-PULLBACK-CONFIRMATION-001-20260228.md
커밋: https://github.com/moongoby/project-docs/commit/{SHA}
HANDOVER: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/HANDOVER.md
HTTP: 200 확인 완료
```

---

## PART 6. 후속 작업 큐 (과제 A~D 완료 후)

| 순위 | 작업 | 내용 | 선행조건 |
|------|------|------|----------|
| 1 | **D2/D4 진입 필터 강화** | 과제 B 최적 확인 조건을 D2/D4에 적용, 목표 PF≥1.3 | 과제 A~D |
| 2 | **EXIT-MAXIMIZE-001** | 동적 스톱(R03 PF17.98), 트레일링(R06 50.2%), 부분청산 통합, 비용 후 PF 재산출 | 과제 A~D |
| 3 | **CROSS-RELAY-MAXIMIZE-001** | 241일 자본전환 복리 시뮬, 동시 종목 3/5/7/10, 진폭·PF 우선 정책 비교 | 1~2 |
| 4 | **INTEGRATED-MAXIMIZE-001** | 1~3 통합 241일 백테스트, 초기자본 4,000만원, Kelly 배분, Go/No-Go 판정 | 1~3 |
| 5 | **LIVE-PAPER-PRECHECK-001** | D2/D4/D5/D6/D7/S1 전체 파이프라인 모의매매 사전점검 | 4 |

---

## PART 7. 현재 진행률 매트릭스

| 영역 | 연구 | 검증 | 최적화 | 구현 |
|------|------|------|--------|------|
| 종목 발굴 | 100% | 100% | — | 60% |
| 진입 타이밍 — 눌림 감지 | 100% | 90% | 70% | 60% |
| 진입 타이밍 — **눌림 확인** | **40%** | **0%** | **0%** | **0%** |
| 청산 최적화 | 80% | 40% | 20% | 0% |
| 자본 복리 순환 | 80% | 40% | 0% | 0% |
| 전략 디커플링 | 100% | 100% | — | 0% |
| 비용 모델 | 100% | 100% | — | 0% |

**핵심 병목**: 눌림 확인(Confirmation) 검증 0% — 이것이 D2/D4 PF 1.02~1.05의 직접적 원인이며, 연구 자산은 확보되어 있으나 통합 검증 미수행.

---

## PART 8. 핵심 연구 수치 요약 (새 세션 즉시 참조용)

**발굴**: L3+X9 정밀도 90.3%, Birth+1min WR 95.3%, SEC_LEADER_FLAG AUC 0.838

**비용**: 왕복 0.47%(소형주)/0.31%(대형주), 전체 PF -33.6%

**눌림 19,225건**: 2파 발생률 73.9%, RSI 중앙값 56.4(30~50 구간 밖), 깊이 0~1% 성공률 91.5%, V_SHARP 81.6%, T2(09:30~10:30) 79.6%, 전조 Top3 성공률 82~88%

**파동 자본순환**: W1 30%→W2 100% 최적, Dynamic 스톱 PF 17.98, VP 2.27분 선행, 거래대금 50% 소진 시 다음파 27.7%

**교차종목**: 동시급등 84.7종목, 5~7종목 분산 PnL +370%

**디커플링**: 2클러스터(D2-D4-D5 / D6-D7-S1), 옵션B 수익유지 89.8%

**Mode3 재설계**: RSI50~75, depth wave1×0.5, WF 73.9% PASS, PF 2.43

---

## PART 9. CEO 보고 규칙 (절대 준수)

1. 작업 완료 시 **반드시 git push 먼저**, 서버 로컬 경로로 보고하지 말 것
2. **GitHub 브라우저 URL**로 보고 (CEO-DIRECTIVES 섹션 4-9)
3. HANDOVER.md 업데이트 필수
4. HTTP 200 확인 필수
5. 파일명: `CUR-V41-{TASK}-{SEQ}-{YYYYMMDD}.md`
6. 커밋 prefix: `[V4.1]`
7. 교차 저장 금지 (V4.1 보고서는 `kis-autotrade-v4/reports/`에만)

---

## PART 10. 절대 규칙

1. **kis-v41-* 서비스 재시작 금지**
2. **strategy_cards ALTER/DROP/DELETE 금지**
3. **v4_positions 직접 편집 금지**
4. **.env / .bak 커밋 금지**
5. **원본 테이블 READ ONLY**
6. DB 접근: `sudo -u postgres python3` 또는 `sudo -u postgres psql -d kisautotrade`
7. 가상환경: `source /root/kis-autotrade-v4/venv/bin/activate`
8. PYTHONPATH: `/root/kis-autotrade-v4/backend`

---

## PART 11. 새 세션 즉시 실행 가이드

**Step 1**: PART 1의 문서 7개를 순서대로 읽는다.

**Step 2**: 본 인계서의 PART 5 (과제 A~D)를 확인한다.

**Step 3**: 서버 접속 후 기존 JSON 파일 존재 확인:
```bash
ls -la /tmp/pullback_anatomy_*.json
ls -la /tmp/mode3_redesign_*.json
ls -la /tmp/cost_adjusted_*.json
ls -la /tmp/r23_*.json
```

**Step 4**: 과제 A~D 순서대로 실행. 19,225건 눌림 데이터(PULLBACK-ANATOMY-001)를 이평선 기준으로 재분류하고, 반등 확인 신호를 조합 검증한다.

**Step 5**: 보고서 `CUR-V41-PULLBACK-CONFIRMATION-001-20260228.md` 작성 → push → GitHub URL로 CEO에게 보고.

**Step 6**: 과제 A~D 완료 후 PART 6 후속 작업 큐에 따라 D2/D4 필터 강화 → EXIT-MAXIMIZE → CROSS-RELAY → 통합 백테스트 순서로 진행.

---

*HANDOVER-KIS-V41-PULLBACK-CONFIRM-20260228 작성 완료*
