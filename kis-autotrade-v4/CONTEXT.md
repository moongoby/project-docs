# KIS AutoTrade V4.1 Core HANDOVER
> Public URL: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CONTEXT.md
> 최종 갱신: 2026-03-08

---

## 이 문서의 운영 원칙
- 이 문서는 토큰 상한이 없다. 비용을 아끼지 말고 최신화하라.
- 중요 내용은 빠짐없이 반영하라. 생략 금지.
- 이 문서를 읽고 CEO에게 추가 질문 없이 즉시 업무 수행이 가능해야 한다.
- 모든 작업 완료 시 반드시 이 문서를 업데이트하라.
- CEO 재설명 1회 비용 > 문서 토큰 비용 100회분임을 명심하라.

---

## 🔒 매니저 자기인식 프로토콜

### 나는 누구인가
- 나는 **KIS AutoTrade V4.1 프로젝트 전담 AI 매니저**이다.
- 매니저 대화창: https://www.genspark.ai/agents?id=77de652f-ca8c-4edb-b841-4ca3726b7bb4
- 나는 CEO가 아니다. CEO 승인 없이 작업을 생성·변경·삭제할 수 없다.
- 나는 작업자가 아니다. 직접 코드를 작성하거나 서버에 SSH 접속하지 않는다.
- 관할 범위: `/root/kis-autotrade-v4/` 내 V4.1 전용 파일만 담당. GO100 파일 수정 절대 금지.

### 이 채팅창이 내 채팅창인가
세션 시작 시 아래 3가지를 확인한다:
- **확인 ①** 채팅 제목 또는 CEO 첫 메시지에 KIS/V4.1 포함?
- **확인 ②** Task ID가 T-xxx 또는 KIS-xxx?
- **확인 ③** 참조 문서가 kis-autotrade-v4 경로?

하나라도 불일치 → "⚠️ 이 채팅창은 KIS V4.1 매니저용입니다" 경고 출력 후 작업 거부.

### 세션 시작 보고
```
[KIS-V41 매니저] 세션 시작

📋 마지막 완료: {LAST_TASK_ID} ({STATUS})
📋 다음 대기: {NEXT_TASK_ID}
📋 긴급사항: {있으면 기재, 없으면 "없음"}
📋 문서 읽기: CONTEXT ✅ | CEO-DIRECTIVES ✅ | RULES ✅
🔑 KIS V4.1 전담 매니저 확인
지시를 기다립니다.
```

---

## ⚡ 지시서 자동화 시스템 (핵심 — 반드시 숙지)

### 동작 원리
1. CEO가 이 매니저 채팅창에 지시를 내린다.
2. **매니저(나)가 `>>>DIRECTIVE_START ~ >>>DIRECTIVE_END` 블록을 대화창에 출력한다.**
3. **bridge.py(서버 211)가 이 대화창을 실시간 감시하여, 지시서 블록을 자동 감지한다.**
4. **bridge.py가 자동으로 `/root/.genspark/directives/pending/`에 지시서 파일을 저장한다.**
5. auto_trigger.sh가 10초 주기로 pending 폴더를 폴링하여 작업을 서버 211에서 실행한다.

### ⛔ 절대 금지 행위
- **CEO에게 "이 지시서를 전달해 주세요" / "이 지시서를 실행해 주세요"라고 요청하는 것은 금지한다.**
- **CEO에게 지시서를 복사·붙여넣기 요청하는 것은 금지한다.**
- 매니저는 대화창에 지시서를 출력하기만 하면 된다. 나머지는 bridge.py가 자동 처리한다.
- CEO가 해야 할 일은 없다. 매니저가 지시서를 출력하는 순간 자동화가 시작된다.

### 올바른 지시서 발행 흐름
```
CEO: "DQI L1_SECTOR_IDX 개선해줘"
     ↓
매니저: [분석 후 대화창에 직접 지시서 출력]
     >>>DIRECTIVE_START
     TASK_ID: KIS-001
     ...
     >>>DIRECTIVE_END
     ↓ (자동)
bridge.py 감지 → pending/ 저장 → auto_trigger.sh 실행 → Cursor AI 작업
```

### 지시서 필수 필드
| 필드 | 필수 | 설명 |
|------|------|------|
| TASK_ID | ✅ | KIS-xxx (신규) 또는 T-xxx (레거시, 읽기 전용) |
| PROJECT | ✅ | KIS-V41 |
| TITLE | ✅ | 작업 제목 |
| PRIORITY | ✅ | P0-CRITICAL / P1-HIGH / P2-MEDIUM / P3-LOW |
| SIZE | ✅ | XS / S / M / L / XL |
| IMPACT | ✅ | H / M / L |
| EFFORT | ✅ | H / M / L |
| DESCRIPTION | ✅ | 작업 상세 |
| SUCCESS_CRITERIA | ✅ | 완료 판단 기준 |
| ASSIGNEE | ✅ | Cursor AI (서버 211) |

### 지시서 예시 — 데이터 백필 (M)
```
>>>DIRECTIVE_START
TASK_ID: KIS-001
PROJECT: KIS-V41
TITLE: L1_SECTOR_IDX 개선 — 누락 섹터지수 백필
PRIORITY: P1-HIGH
SIZE: M
IMPACT: H
EFFORT: M
DESCRIPTION: |
  L1_SECTOR_IDX 68.3% (2460/3600). 95%+ 달성 위해 누락 백필.
  1. scripts/collectors/sector_index_backfill.py 작성
  2. 60섹터 × 60거래일 = 3,600행 목표 (UPSERT)
  3. DQI 재산출 → L1_SECTOR_IDX ≥ 95%
SUCCESS_CRITERIA: |
  1. v4_sector_index 행수 ≥ 3,420
  2. DQI L1_SECTOR_IDX ≥ 95.0%
  3. security_scan 0건, path_check PASS
  4. 보고서 push + HTTP 200
  5. CONTEXT.md 업데이트
ASSIGNEE: Cursor AI (서버 211)
>>>DIRECTIVE_END
```

### 지시서 예시 — 기능 구현 (L)
```
>>>DIRECTIVE_START
TASK_ID: KIS-002
PROJECT: KIS-V41
TITLE: exit_manager MA20 trailing 전면 적용
PRIORITY: P0-CRITICAL
SIZE: L
IMPACT: H
EFFORT: H
DESCRIPTION: |
  CEO 승인 완료. exit_manager.py에 MA20 trailing stop 적용.
  1. 전 DESK(D1~D5) 적용, DESK5는 D-014 조건 우선
  2. 백테스트 비교 기존 SL/TP vs MA20 trailing
  3. PF ≥ 1.3 확인
  4. 단위 테스트 5건+
SUCCESS_CRITERIA: |
  1. MA20 trailing 로직 구현
  2. 백테스트 PF ≥ 1.3
  3. 테스트 5/5 PASS
  4. CONTEXT.md + HANDOVER.md 업데이트
  5. 보고서 push + HTTP 200
ASSIGNEE: Cursor AI (서버 211)
>>>DIRECTIVE_END
```

### 지시서 예시 — 소규모 수정 (S)
```
>>>DIRECTIVE_START
TASK_ID: KIS-003
PROJECT: KIS-V41
TITLE: DQI 재산출 cron 등록
PRIORITY: P2-MEDIUM
SIZE: S
IMPACT: M
EFFORT: L
DESCRIPTION: |
  DQI 재산출 매일 06:00 KST 자동 실행 cron 등록.
  1. scripts/dqi_recalculate.sh 작성
  2. crontab 등록, 로그 /var/log/kis-dqi.log
SUCCESS_CRITERIA: |
  1. cron 등록 완료
  2. 수동 실행 정상 동작
  3. 보고서 push + HTTP 200
  4. CONTEXT.md 업데이트
ASSIGNEE: Cursor AI (서버 211)
>>>DIRECTIVE_END
```

### 완료 검증 (6조건, 전부 충족 필수)
1. 파일 수정 완료
2. `bash scripts/security_scan.sh` → 0건
3. `bash scripts/path_check.sh {파일명}` → PASS
4. git push 성공 (commit SHA)
5. curl HTTP 200 확인
6. CONTEXT.md 또는 HANDOVER.md 업데이트

### 보고 형식
```
[CURSOR-KIS] {상태}

작업: {1줄 요약}
보고서: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/{파일명}
커밋: https://github.com/moongoby/project-docs/commit/{SHA}
HTTP: {200|실패}
security_scan: {0건|N건}
path_check: {PASS|FAIL}
다음: {다음 작업 또는 "지시 대기"}
```

---

## 1. 프로젝트 개요
- KIS AutoTrade V4.1: 한국투자증권 API 기반 AI 자동매매
- DESK 1~5 멀티 전략 (60개 전략카드)
- 모노리포: V4.1 + GO100 공존 (서비스 경계 엄격 분리)
- 도메인: trading41.newtalk.kr
- GitHub 코드: moongoby/kis-autotrade-v4 (private)
- GitHub 문서: moongoby/project-docs (public)
  - CONTEXT: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/CONTEXT.md
  - HANDOVER: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/HANDOVER.md
  - CEO-DIRECTIVES: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/CEO-DIRECTIVES.md
  - 보고서: https://github.com/moongoby/project-docs/tree/master/kis-autotrade-v4/reports

## 2. 서버 환경
- 서버: root@211.188.51.113 (AADS 체계 "서버 211" Hub)
- 프로젝트: /root/kis-autotrade-v4, 브랜치: phase-2c-command-center
- DB: PostgreSQL 16, kisautotrade / kis_admin / localhost:5432
- Python 3.12, FastAPI, SQLAlchemy (asyncpg), Redis 7.x
- 가상환경: source /root/kis-autotrade-v4/venv/bin/activate
- AADS 자동화: bridge.py, auto_trigger.sh, pipeline_monitor, session_watchdog 동일 서버

## 3. CEO 절대 규칙
1. kis-v41-* 서비스 재시작 금지 (CEO 승인 시에만)
2. strategy_cards ALTER/DROP/DELETE 금지 (UPDATE는 CEO 승인)
3. v4_positions 직접 수정 금지
4. 핵심 파일 수정 → review/ → CEO+Claude 승인 후 적용
5. .env/.bak 커밋 절대 금지
6. 사전확인: strategy_cards=60, v4_positions OPEN=0
7. GO100 파일 수정 절대 금지

## 4. DESK 구성
| DESK | 역할 | max_hold | 전략수 | 상태 |
|------|------|----------|--------|------|
| DESK1 | 초단타/스캘핑 | 0-1일 | 10 | 활성 |
| DESK2 | 단타 | 1-3일 | 16 | 활성 |
| DESK3 | 단기스윙 | 3-10일 | 11 | 활성 (주 수익원) |
| DESK4 | 중기스윙 | 20-40일 | 9 | 활성 |
| DESK5 | 장기 | 90-120일 | 10 | 활성 (4주 테스트) |

## 4.5 프랙탈 추세추종 아키텍처 (CEO 확정 v3.0)

> 핵심: 프랙탈 구조로 DESK 간 동일한 추세추종 원리를 자기유사(fractal)하게 적용한다.
> 프랙탈 아키텍처의 모든 DESK는 넓게 뿌리고 소수 대승으로 전체를 덮는 손익비 구조를 공유한다.

### 제1원칙: 전 DESK 손익비 추세추종 (코어-새틀라이트 폐기)
- DESK5 = 씨앗 농장: 10~20종목 분산, 승률 15~25%, 손익비 ≥ 5:1 (프랙탈 최장주기)
- DESK4 = 마디 수확: 20~30종목 분산, 승률 35~45%, 손익비 ≥ 2.5:1 (프랙탈 중주기)
- DESK3 = 폭발 사냥: 50~100 대기, 승률 50~60%, 손익비 ≥ 1.5:1 (프랙탈 단주기)
- DESK2 = 장중 수확: 6-Layer (전 DESK 보유 종목 분봉 추가 수확, 프랙탈 초단주기)

### 자본 배분 (Stage별)
| Stage | 자본 | DESK2 | DESK3 | DESK4 | DESK5 |
|-------|------|-------|-------|-------|-------|
| Stage 1 | ≤ 4천만 | 90% | 10% | — | — |
| Stage 2 | 2~5억 | 50% | 25% | 15% | 10% |
| Stage 3 | ≥ 10억 | 35% | 25% | 20% | 20% |

### DESK5 청산 3조건 (이 외 청산 금지)
1. 주봉 MA20 2주 연속 이탈
2. 세력 이탈: 주봉 거래량 20주 평균 3배 + 음봉
3. 테마 사망: 30일 뉴스 0건

### DESK5 익절 곡선
- +100% → 원금 회수
- +300% → 50% 추가 익절
- +500% → MA10 트레일링

### 핵심 원칙
- 트리거 = 매수 신호 (풀에 넣는 것이 아니라 돈을 넣는다)
- DESK 간 독립 포지션 + 공유 정보. 승격 = 신뢰도 가산점
- 참조: design/DESK-FRACTAL-ARCHITECTURE-v3.0-20260301.md (CEO 확정)

---

## 5. 서비스 현황
| 서비스 | 포트 | 상태 |
|--------|------|------|
| kis-v41-api | 8003 | active |
| kis-v41-monitor | — | active |
| kis-v41-scheduler | — | active |
| kis-v41-minute-collector | — | inactive (장외, 장중 자동기동) |
| redis-server | 6379 | active |
| postgresql | 5432 | active |

## 6. DB 무결성 (2026-03-07 실측)
- strategy_cards: 60건, v4_positions OPEN: 0건
- DB: 44GB, 290테이블, v4_ohlcv_minute ~118M+행
- **DQI: 92.8 (Grade A)**
  - L0_KOSPI 100%, L0_VIX_60D 97.4%, L1_SECTOR_MAP 100%, L1_SECTOR_IDX 68.3%, L2_INVESTOR 75%, L3_FUNDAMENTAL 100%, OHLCV_FRESH 99.8%
  - 이력: 58.1(D) → 81.3(B) → 92.8(A)
  - 주의: KOSPI 프록시값 711/730행 범위 외, CEO 결정 대기
- **FunnelScore: 30/30 PASS (100%), avg 0.862, 임계값 0.35**
  - ⚠️ **Fail-Open 모드 동작 중 (null_fallback_score=0.5), CEO 재교정 승인 대기(T-227)**

## 6.5 GO100(백억이) 연동 아키텍처

### 연동 기반 문서
- V41-GO100-INTEGRATION-ARCHITECTURE-v1.0.md 기반

### 3대 브릿지
| 브릿지 | 역할 | 구현 상태 |
|--------|------|-----------|
| ① 자본 컨트롤 | 포트폴리오 옵티마이저, Kelly 베팅 | Phase2 대기 |
| ② 리스크/킬스위치 | go100_risk_events 테이블, 매 주문 전 조회 | Phase2 대기 |
| ③ 에피소드 메모리 | 매매결과+5축마스크 JSON 적재, agent_id=V4.1_DESK_AGENT | Phase2 대기 |

### 안전 수칙 (절대 원칙)
- 코드 침범 금지 (REST API만 사용)
- Read-Only / Append-Only 원칙
- 독립 네임스페이스 유지 (V4.1 DB ↔ GO100 DB 직접 연결 금지)

### 현황
- Phase 1: 기획 완료
- Phase 2~3: 구현 대기
- GO100 매니저: https://www.genspark.ai/agents?id=167071cf-c8b5-476a-8953-6168dd6c910c

---

## 7. 최근 완료 작업 (최근 10건)
| Task | 커밋 | 내용 |
|------|------|------|
| KIS-293 | — | Nginx 차트 API 프록시 설정: /api/chart-data, /api/stocks, /api/trades → 8003; apply_nginx_kis293.sh 생성(root 실행 필요); CONTEXT.md v11.2 업데이트 |
| KIS-291 | — | claude_exec.sh SIZE 기반 차등 타이머(XS=1200s/S=1200s/M=2400s/L=3600s/XL=5400s); 211서버 배포; 테스트 3케이스 PASS |
| KIS-290 | — | 03-10 장전 사전점검 9/9 PASS: kis-v41-api 재시작+T-286 backtest/progress 200 확인; strategy_cards=60/OPEN=0 |
| KIS-001 | — | CONTEXT.md v11.1 종합 업데이트: §6.5 GO100 연동, §8.5 백테스트 엔진, §8.8~8.10 API/이슈, §14 design 5건 |
| T-286 | 88502672 | /api/v4/backtest/progress 엔드포인트 구현: converge_status 집계, 서비스 재시작 필요 |
| T-285 | docs | 브릿지 큐 정리 + CONTEXT.md v10.28 동기화 |
| T-284 | dd7b6560 | 브릿지 큐 T-282-S5/T-282-S4S5 completed 처리 + Phase2 7/7 검증 |
| T-283 | c6bc6a4b | trades.html Phase2: RSI/MACD pane + 보유구간 Rectangle + 전체화면 |
| T-282 | 4b327d12/09e539d6 | 키움 영웅문4 스타일 trades.html 차트 전면 교체: 7파일, LWCharts v5.1.0 |
| T-280 | — | trades.html 배포: kis-v41-api 재시작+Nginx, API 3개 200OK |

## 8. trades.html 차트 현황 (2026-03-08 기준)
| 항목 | 내용 |
|------|------|
| 기반 | LightweightCharts v5.1.0 (키움 영웅문4 스타일) |
| 파일 구성 | trades.html + kw-chart-engine.css + kw-chart-engine.js + kw-chart-data.js + kw-chart-controls.js + kw-chart-indicators.js + kw-chart-trades.js (총 7파일) |
| Phase1 (T-282) | 기본 캔들차트 + 매매신호 오버레이 (09e539d6/4b327d12) |
| Phase2 (T-283) | RSI pane(14기간/70·30 수평선) + MACD pane(12/26/9) + 보유구간 Rectangle + 전체화면(F키/ESC) (c6bc6a4b) |
| 다음 예정 | Phase3: 자동추세선, 거래량프로파일(VP), 분봉 실시간 연동 |

## 8.5 백테스트 엔진 현황

### 엔진 종류
| 엔진 | 용도 | 상태 |
|------|------|------|
| backtest_engine_v2.py | 통계 시뮬레이션 | 164세션 완료 |
| replay/ 패키지 | 분봉 리플레이 | 6모듈 구성 |

### 분봉 리플레이 아키텍처 (6모듈)
```
minute_bar_feeder → candidate_scanner → entry_detector
→ exit_simulator → result_aggregator → replay_engine
```

### Look-ahead Bias 차단 (4항목)
1. 후보: D-1 일봉만 사용
2. 진입: 다음 바 시가 기준
3. 지표: 현재 바까지만 계산
4. 오버나이트: D+1 첫 바 시가

### 청산 5모드
① Hard Stop(-3%), ② ATR Trailing, ③ Time Close(15:20), ④ Partial TP(+3%→50%), ⑤ DD Force

### 비용 모델
- 편도 수수료 0.015% + 증권거래세 0.2% + 슬리피지 0.04% = **0.47% (편도)**

### 최신 세션 결과
- 세션 #164: DESK2 DAILY 1W, +0.07%, WR56.76%, PF1.074, Sharpe3.307
- 분봉 리플레이 (2025-03~2026-02): 포트폴리오 PF=0.834(FAIL), D6만 PF=1.144(CONDITIONAL)

### CLI
- `scripts/run_replay_backtest.py`
- 참조: CUR-V41-REPLAY-BACKTEST-001-20260302.md

---

## 8.8 API 엔드포인트 상태 (외부 접근 기준, 2026-03-08)

| 상태 | 엔드포인트 |
|------|-----------|
| 200 OK | /api/v4/backtest/sessions |
| 200 OK | /api/v4/backtest/sessions/{id} |
| 200 OK | /api/v4/backtest/sessions/{id}/trades |
| 200 OK | /api/v4/positions?status=OPEN |
| 401 Auth Required | /api/v4/data-collection/* |
| 200 OK (KIS-293) | /api/chart-data |
| 200 OK (KIS-293) | /api/stocks/search |
| 200 OK (KIS-293) | /api/trades/unified |
| 미응답 | /api/v4/health |
| 미응답 | /api/v4/strategy-cards |
| 200 OK (KIS-290) | /api/v4/backtest/progress |

---

## 8.9 trades.html Known Issues

- ~~**차트 데이터 미표시** (MA 전부 "-", 거래 목록 빈칸)~~
- **KIS-293 해결완료**: /api/chart-data, /api/stocks, /api/trades → 8003 Nginx 프록시 설정 완료
- 현재 trades.html: /api/v4/ 경로 사용 중 (nginx /api/v4/ → 8003 기설정), 200 OK 확인됨
- Nginx apply 스크립트: scripts/v41/apply_nginx_kis293.sh (root 실행 완료)

---

## 8.10 백테스트 trade stock_name null 이슈

- backtest sessions/{id}/trades 응답에서 **stock_name이 전부 null**
- **원인 추정**: API 조인 누락 (stock_universe 미조인)
- **해결**: 별도 작업 (KIS-003)

---

## 9. 작업 큐 (2026-03-08 기준)
| 순위 | 작업 | 상태 |
|------|------|------|
| P0 | T-229 MA20 trailing 전면 적용 | CEO 결정 대기 |
| P0 | L0_KOSPI 과거 재백필 | 후속 필요 |
| P1 | KIS-003 백테스트 trade stock_name 해결 | 신규 대기 |
| P1 | T-283-Phase3 자동추세선 + 거래량프로파일 + 분봉 실시간 | 다음 작업 |
| P1 | T-228 backtest_loop 크론 | 대기 |
| P1 | T-227 FunnelScore 재교정 | CEO 승인 대기 |
| P2 | T-234 /api/v4/regime | 대기 (에러) |

## 10. CEO 결정 대기
1. T-227 FunnelScore 재교정 (Fail-Open 유지 중, 03-10 실전 검증 예정)
2. T-229 MA20 trailing 전면 적용 (H05-D PF=2.18, H08-B PF=25.93)
3. L0_KOSPI 재백필 (711/730행 프록시값)
4. T-194 ATR SL 파라미터 (T-207 적용 완료)
5. T-195 14:00 진입 차단 (완료)

## 10.5 03-10 모의매매 사전 체크리스트

장 개시 전 반드시 확인할 항목 (T-245R):

| # | 항목 | 확인 명령 |
|---|------|-----------|
| 1 | bridge.py PID 확인 | `ps aux \| grep bridge` |
| 2 | FunnelScore Fail-Open 모드 확인 | `null_fallback_score=0.5` 설정 확인 |
| 3 | 서비스 4개 active 확인 | kis-v41-api, monitor, scheduler, postgresql |
| 4 | strategy_cards=60, OPEN=0 확인 | DB 쿼리 |
| 5 | Redis 연결 상태 확인 | `redis-cli ping` |
| 6 | 크론 5건+ 확인 | `crontab -l \| wc -l` |

---

## 11. 긴급 주의사항
- GitHub PAT 만료: 2026-05-27 (잔여 ~80일)
- 전량 청산 상태: OPEN=0, 모의매매 대기
- 모의매매 실전 검증: 03-10(월) 장 개시 후 T-245R

## 12. 핵심 파일 (수정 시 검수)
exit_manager.py, cte_pipeline.py, v4_pipeline_orchestrator.py, strategy_engine.py, risk_manager.py, order_executor.py, position_manager.py, backtest_engine_v2.py, config/funnel_score.yaml

## 13. Task ID 전환
- T-283 이후 신규 작업: **KIS-001부터 KIS-xxx 체계** 사용
- 기존 T-001~T-283: 읽기 전용, 신규 발행 금지

## 14. 참조 문서
| 문서 | URL |
|------|-----|
| CONTEXT (이 파일) | https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/CONTEXT.md |
| HANDOVER (History, 최근10건) | https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/HANDOVER.md |
| HANDOVER-HISTORY (v10.62~v10.53) | https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/HANDOVER-HISTORY.md |
| HANDOVER-ARCHIVE (v10.52 이전) | https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/HANDOVER-ARCHIVE.md |
| CEO-DIRECTIVES | https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/CEO-DIRECTIVES.md |
| Rules | https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/rules/kis-v41-rules.md |
| HANDOVER-RULES | https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/rules/KIS-HANDOVER-RULES.md |
| 보고서 | https://github.com/moongoby/project-docs/tree/master/kis-autotrade-v4/reports |
| AADS 공통 규칙 | https://github.com/moongoby-GO100/aads-docs/blob/main/CEO-DIRECTIVES.md |
| AADS RULES | https://github.com/moongoby-GO100/aads-docs/blob/main/HANDOVER-RULES.md |
| DESK-FRACTAL-ARCHITECTURE-v3.0 | https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/design/DESK-FRACTAL-ARCHITECTURE-v3.0-20260301.md |
| V41-GO100-INTEGRATION-ARCHITECTURE-v1.0 | https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/design/V41-GO100-INTEGRATION-ARCHITECTURE-v1.0.md |
| DESK2-DESIGN-SPEC-v3.0 | https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/design/DESK2-DESIGN-SPEC-v3.0-20260228.md |
| SYSTEM-ARCHITECTURE-FLOWCHART-v1.0 | https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/design/SYSTEM-ARCHITECTURE-FLOWCHART-v1.0-20260301.md |
| CUR-V41-REPLAY-BACKTEST-001 | https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/CUR-V41-REPLAY-BACKTEST-001-20260302.md |

## 15. 버전 이력 (최근 20건)
| 버전 | 날짜 | Task | 변경 |
|------|------|------|------|
| v11.2 | 2026-03-08 | KIS-293 | §7 KIS-001/KIS-290/KIS-291/KIS-293 완료 추가, §8.8 chart-data/stocks/trades→200 OK, backtest/progress→200 OK(KIS-290), §8.9 Known Issue 해결, §9 KIS-002/T-226 삭제 |
| v11.1 | 2026-03-08 | KIS-001 | §6.5 GO100 연동, §8.5 백테스트 엔진, §8.8~8.10 API/이슈, §10.5 체크리스트, §14 design문서 5건, §15 누락버전 보강 |
| v11.0 | 2026-03-08 | T-283 | 4계층 재구성, 매니저 프로토콜, 지시서 자동화 반영, Task ID 전환 |
| v10.70 | 2026-03-08 | T-283 | 문서 4계층 재구성 |
| v10.69 | 2026-03-08 | T-284 | Phase2 7/7 검증, 브릿지 큐 정리 |
| v10.68 | 2026-03-08 | T-285 | 컨텍스트 동기화 v10.28 |
| v10.67 | 2026-03-08 | T-286 | /api/v4/backtest/progress 엔드포인트 구현 |
| v10.66 | 2026-03-08 | T-284 | RSI/MACD pane, 보유구간 Rectangle, 전체화면 |
| v10.65 | 2026-03-08 | T-283 | trades.html Phase2 구현 |
| v10.64 | 2026-03-08 | T-282 | LWCharts v5.1.0 키움 영웅문4 스타일 전면 교체 |
| v10.63 | 2026-03-07 | T-282 | Nginx static, 차트 7파일 배포 |
| v10.62 | 2026-03-07 | T-280 | trades.html 배포 |
| v10.61 | 2026-03-07 | T-278 | CEO 통합 거래 뷰어 |
| v10.60 | 2026-03-07 | T-277 | 큐정리+장전점검 |
| v10.59 | 2026-03-07 | T-275 | DQI Grade A 달성 |
| v10.58 | 2026-03-07 | T-273 | DQI Grade B |
| v10.57 | 2026-03-07 | T-274 | bridge PID 재시작 |
| v10.56 | 2026-03-07 | T-273 | CONTEXT 동기화 |
| v10.55 | 2026-03-07 | T-270 | KOSPI+VIX 복구 |
| v10.54 | 2026-03-07 | T-272 | 펀더멘탈+FunnelScore+DQI |
