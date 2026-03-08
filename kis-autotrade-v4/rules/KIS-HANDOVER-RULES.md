# KIS AutoTrade V4.1 — HANDOVER RULES v1.0
> 최종 업데이트: 2026-03-08 | 신규 생성

---

## 1. 문서 체계 (4계층)

| 계층 | 파일 | 읽기 시점 |
|------|------|-----------|
| Core | CONTEXT.md | 매 세션 필수 |
| Directives | CEO-DIRECTIVES.md | 매 세션 필수 |
| Rules | 이 파일 + kis-v41-rules.md | 온보딩/규칙확인 |
| History | HANDOVER.md | 이전 작업 참조 |

---

## 2. 지시서 자동화 파이프라인

### 핵심: bridge.py 자동 감지
- bridge.py(서버 211)는 Genspark AI 매니저 채팅창 대화를 **실시간 감시**한다.
- `>>>DIRECTIVE_START ~ >>>DIRECTIVE_END` 블록이 감지되면 **자동으로** `/root/.genspark/directives/pending/`에 저장한다.
- auto_trigger.sh가 10초 주기로 pending을 폴링하여 KIS → 서버 211 로컬 실행한다.

### ⛔ 절대 금지
- 매니저가 CEO에게 지시서 전달을 요청하는 것은 금지한다.
- 매니저는 대화창에 지시서 블록을 출력하기만 하면 된다.
- CEO가 수동으로 개입할 필요가 없다.

### 8단계 파이프라인 (KIS 적용)
1. CEO → KIS 매니저 대화창에 지시
2. 매니저 → 대화창에 `>>>DIRECTIVE_START` 지시서 출력
3. bridge.py → 자동 감지 → pending/ 저장
4. auto_trigger.sh → 사전 검증 (WORKDIR, 중복, 의존성)
5. auto_trigger.sh → 서버 211 로컬 실행
6. Cursor AI → 코드 수정 + 테스트 + push
7. 결과 보고 → RESULT 파일 + CONTEXT 업데이트 + HTTP 200
8. 교차 검증 → session_watchdog + git-push 확인

---

## 3. 매니저 역할

### 할 수 있는 것
1. GitHub raw URL 크롤링
2. 문서 분석/진단 (DQI, FunnelScore)
3. **대화창에 지시서 출력** (bridge.py가 자동 처리)
4. 보고서 작성/집계
5. URL 모니터링
6. CEO에게 의견 제시

### 할 수 없는 것
1. SSH 접속
2. DB 조회/수정
3. git push/commit
4. 서비스 재시작
5. 시크릿 접근
6. $5 초과 작업 (CEO 승인 필요)
7. GO100 파일 수정 지시
8. **CEO에게 지시서 전달 요청** (자동화됨)

---

## 4. 작업자(Cursor AI) 규칙

### FLOW (D-016)
Find → Layout → Operate → Wrap-up (소규모는 Operate→Wrap만)

### 완료 6조건
1. 파일 수정 완료
2. security_scan → 0건
3. path_check → PASS
4. git push 성공 (SHA)
5. HTTP 200
6. CONTEXT.md 또는 HANDOVER.md 업데이트

### 절대 금지
1. kis-v41-* 재시작 (CEO 승인만)
2. strategy_cards ALTER/DROP/DELETE
3. v4_positions 직접 편집
4. .env/.bak 커밋
5. GO100 파일 수정
6. 토큰 절약 이유로 정보 생략

### 커밋: `[V4.1] {type}: {description}`
### 보고서: `CUR-V41-{TASK}-{SEQ}-{YYYYMMDD}.md`

---

## 5. 서비스 경계 (모노리포)

| 영역 | V4.1 | GO100 | 공유 |
|------|------|-------|------|
| 라우터 | routers/v4_*.py | routers/go100/*.py | main.py |
| 서비스 | services/v4_* | services/go100/**/* | core/ |
| DB | ohlcv_daily, strategy_cards 등 | go100_* 접두사 | kisautotrade DB |
| 커밋 | [V4.1] | [GO100] | [SHARED] |

---

## 6. 승인 권한

| 대상 | 승인자 |
|------|--------|
| DB 스키마, 서비스 재시작, strategy_cards UPDATE, 코드 레포 직접 수정, 자본 변경, $5 초과 | **CEO 직접** |
| 위 항목 외 | Genspark 지휘소 AI (`>>>DIRECTIVE` 블록 = CEO 승인) |

---

## 7. 대화창 라우팅

| 작업 대상 | 대화창 |
|-----------|--------|
| KIS V4.1 | https://www.genspark.ai/agents?id=77de652f-ca8c-4edb-b841-4ca3726b7bb4 |
| GO100 | https://www.genspark.ai/agents?id=167071cf-c8b5-476a-8953-6168dd6c910c |
| CEO 통합지휘소 | bridge.py 자동 발송 전용 (Cursor 수동 보고 금지) |

---

## 8. Task ID 전환

| 구분 | 체계 | 범위 |
|------|------|------|
| 레거시 | T-001 ~ T-283 | 읽기 전용, 신규 발행 금지 |
| 신규 | KIS-001 ~ | 모든 신규 작업 |

---

## 9. 변경 이력
| 버전 | 날짜 | 변경 |
|------|------|------|
| v1.0 | 2026-03-08 | 신규 생성 — 지시서 자동화 반영, 9개 섹션 |
