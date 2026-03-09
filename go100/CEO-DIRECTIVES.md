# CEO DIRECTIVES – GO100 백억이 AI 투자 에이전트
> 최종 업데이트: 2026-02-28 (v1.0)
> 관리자: CEO (moongoby)
> 용도: 모든 AI 세션에서 필수 읽기. 이 문서의 지시를 위반하는 설계/구현은 무효.

---

## 1. 사고방식 원칙

### D-001 단순 사고 금지
- "하나를 던지면 10을 생각하고 연구해서 반영하라"
- 단일 변수, 단일 시점, 단일 관점 분석은 불충분
- 복합계, 다층 구조, 다시점 분석이 기본

### D-002 백억이의 본질
- 백억이(GO100)는 증권사급 AI 투자 에이전트
- 핵심 기능: 대화형 조건검색 + 자동매매 + 자율 전략 진화
- 사용자가 "삼성전자 어때?"라고 물으면 시장 분석·종목 분석·포트폴리오 제안·백테스트까지 한 번에 수행
- 최종 목표: 사용자 개입 최소화, AI 자율 투자 의사결정

### D-003 Agent 아키텍처
- LLM: Gemini 2.5 Flash (주), Anthropic Claude Sonnet (폴백)
- Agent Loop: **최대 20라운드, 라운드당 최대 10도구** (전면 개방, T-051 기준 — 기존: 5라운드/3도구)
- 도구: agent_tools.py(정의) + tool_executors.py(실행) 구조
- 현재 57개 도구, 스크리닝 필터 35+
- 환경변수 GO100_AGENT_MODE로 ON/OFF 전환
- 환각 방지: hallucination_guard.py 5중 방어 체계 (T-051 적용)

### D-004 데이터 신뢰성
- Freshness Warning: 6개 도구에 데이터 신선도 경고 탑재
- 무결성 체커: */2 장중, */15 장외 자동 실행
- Auto Healer: pykrx → KIS API → FinanceDataReader → DART 4단계 복구
- 이중소스: pykrx + DART 교차검증 필수
- 데이터 없이 분석하지 말 것 — "데이터 부족" 명시 후 대안 제시

### D-005 실매매 전 검증 필수
- 실매매 진입 순서: 30일 모의투자 → 자기리뷰(run_self_review) → Telegram 알림 검증 → CEO 승인
- CEO 승인 없는 실매매 전환 절대 금지
- Kill Switch 해제는 CEO(user_id=2)만 가능

### D-006 서비스 경계 — V4.1 파일 수정 금지
- GO100 작업 시 V4.1 소속 파일 절대 수정 금지 (역도 동일)
- V4.1 라우터: /api/v4/*, GO100 라우터: /api/go100/*
- 서비스 경계: /root/kis-autotrade-v4/.cursorrules, SERVICE_BOUNDARY.md 참조
- 공유 인프라(.env, main.py, nginx) 수정 시 양쪽 영향 반드시 명시

### D-007 컨텍스트 패키지 시스템
- 모든 AI 세션 시작 시 필수 읽기: HANDOVER.md + CEO-DIRECTIVES.md + 관련 설계서
- 이전 맥락 없이 작업하면 같은 실수 반복
- 매 작업 완료 시 HANDOVER.md 업데이트 의무
- HANDOVER.md 미업데이트는 작업 미완료로 간주

### D-008 능력 전면 개방 (2026-03-09, T-051)
> CEO 지시: "능력 전면 개방, 실계좌만 잠금, 모의투자 적극 활용, 환각 자가 진화"

- **Agent Loop**: 5R/3T → **20R/10T 전면 개방**
- **V3 모델**: 활성화 완료 (AUC 0.5656, brain_predictor_v3.py)
- **모의계좌 실매매**: 전면 개방 — CEO 승인 불필요
- **실계좌 전환**: 잠금 유지 — CEO(user_id=2) 승인 필수 (D-005 유지)
- **환각 자가 진화**: hallucination_guard.py 5중 방어 체계 구축
  1. 실시간 Freshness 검증 (6도구 freshness_warning)
  2. 다중 소스 교차검증 (pykrx + DART + KIS)
  3. Agent 출력 근거 추적 (도구 호출 로그 필수)
  4. CEO 오버라이드 파서 (parse_ceo_overrides)
  5. Evolution Loop 자가 검증 후 반영

---

## 2. 기술적 지시

### T-001 신고가 돌파 전략
- screen_stocks에 new_high 필터 탑재
- 52주 신고가 + 거래량 2배 이상 동반이 핵심 조건
- 매물대 소멸 원리: 모든 보유자가 수익 → 매도 압력 감소 → 적은 매수세로 급등

### T-002 Agent 도구 등록 규칙
- 정의: agent_tools.py에 도구명·설명·파라미터 스키마
- 실행: tool_executors.py에 래퍼 함수
- 감사: 모든 도구 호출은 로그 기록 (도구명, 파라미터, 결과 요약, 소요시간)
- 등록 후 반드시 E2E 테스트 통과 확인

### T-003 리스크 엔진
- check_pre_trade: 모든 매수 주문 전 필수 호출
- 규칙: 포지션 한도, 섹터 집중도, 총 노출, 일일 P&L 한도
- Kill Switch: 한도 초과 시 자동 활성화, 해제는 CEO(user_id=2) 전용
- risk_engine.py → paper_trading_engine_30d.py 연동 완료

### T-004 로드맵
1. Phase 0~4 (완료): Agent Mode, E2E, 크론, 시드, 메모리, 갭, 모의투자, 전략 편집
2. Phase 5 (완료): 자기리뷰, Telegram, 포트폴리오 최적화, 개인화
3. Phase 6 (진행): 리스크 엔진, KIS 주문 게이트웨이
4. Phase 7 (다음): 30일 모의투자 1사이클, 소액 실매매, 전체 QA
5. Phase 8: SaaS 준비 (셀프서비스, 마켓플레이스)
6. Phase 9: 라이브 런칭

---

## 3. 절대 규칙 (위반 시 작업 무효)

1. V4.1 파일 수정 금지 (kis-v41-* 서비스 재시작 금지 포함)
2. strategy_cards ALTER/DROP/DELETE 금지 (UPDATE는 CEO 승인 후)
3. v4_positions 직접 편집 금지
4. .env / .bak 커밋 금지
5. Kill Switch 해제는 CEO(user_id=2) 전용
6. 작업 완료 시 HANDOVER.md 업데이트 필수
7. 보고서 GitHub push + HTTP 200 확인 필수
8. 경로 규칙(PATH-001) 준수 필수 — 아래 섹션 4 참조
9. 보고 시 반드시 GitHub 브라우저 URL로 보고 (REPORT-001) — 아래 섹션 4-9 참조

---

## 4. 경로 규칙 (PATH-001) — 위반 시 보고서 미제출 처리

### 4-1. 프로젝트별 저장 경로 (교차 저장 금지)

| 프로젝트 | 보고서 경로 (서버) | GitHub 경로 |
|---------|-------------------|-------------|
| GO100 | /root/project-docs/go100/reports/ | go100/reports/ |
| V4.1 | /root/project-docs/kis-autotrade-v4/reports/ | kis-autotrade-v4/reports/ |

GO100 보고서를 kis-autotrade-v4/reports/에 넣거나, V4.1 보고서를 go100/reports/에 넣으면 무효.

### 4-2. 파일명 규칙

```
CUR-{PROJECT}-{TASK_NAME}-{SEQ}-{YYYYMMDD}.md
```

| 구분 | GO100 | V4.1 |
|------|-------|------|
| PROJECT | GO100 | V41 |
| 예시 | CUR-GO100-P5-3-PORTFOLIO-OPTIMIZER-001-20260227.md | CUR-V41-ARCHITECTURE-SCAN-001-20260223.md |

V4.1 DESK 계열 보고서는 `DESK2-{TASK}-{SEQ}-{YYYYMMDD}.md`도 허용.

**금지 패턴:**
- `20260223-HOTFIX-SAVE-500.md` (날짜 선행, prefix 없음)
- `report.md` (식별 불가)
- `HOTFIX-001.md` (날짜 없음)
- `CUR-GO100-FIX-20260223.md` (TASK_NAME 너무 짧음, SEQ 없음)

### 4-3. 날짜 규칙

파일명 YYYYMMDD = 작업 완료일 (KST 기준). 보고서 작성일이 아니라 코드·테스트 완료일.

### 4-4. HANDOVER.md 단일 파일 규칙

| 프로젝트 | 최신 인계서 (항상 이 파일이 최신) | 아카이브 |
|---------|-------------------------------|---------|
| GO100 | go100/HANDOVER.md | go100/HANDOVER-YYYYMMDD-VN.md (읽기 전용) |
| V4.1 | kis-autotrade-v4/HANDOVER.md | 별도 보관 불필요 (단일 파일 운영 중) |

새 세션 AI는 HANDOVER.md 하나만 읽으면 최신 상태 파악 가능해야 한다.

### 4-5. CEO-DIRECTIVES.md 경로

| 프로젝트 | 경로 |
|---------|------|
| GO100 | go100/CEO-DIRECTIVES.md |
| V4.1 | kis-autotrade-v4/CEO-DIRECTIVES.md |

### 4-6. 커밋 메시지 prefix

| 프로젝트 | prefix | 예시 |
|---------|--------|------|
| GO100 | [GO100] | [GO100] feat: P5-3 포트폴리오 최적화 엔진 |
| V4.1 | [V4.1] | [V4.1] feat: DESK2 HAV 엔진 개발 |
| 공유 | [SHARED] | [SHARED] config: .env 포트 변경 |
| 문서 | [DOCS] | [DOCS] handover: GO100 인계서 v10 |

### 4-7. push 전 셀프 검증 스크립트 (필수 실행)

작업 완료 후 git add 전에 아래 5단계를 반드시 실행:

```bash
#!/bin/bash
# === PATH-001 셀프 검증 ===

# 1) 보고서가 올바른 프로젝트 경로에 있는가?
echo "=== [1/5] 경로 확인 ==="
REPORT_FILE="$1"  # 인자로 보고서 파일명 전달
if [[ "$REPORT_FILE" == CUR-GO100-* ]] || [[ "$REPORT_FILE" == *-GO100-* ]]; then
    EXPECTED_DIR="/root/project-docs/go100/reports/"
elif [[ "$REPORT_FILE" == CUR-V41-* ]] || [[ "$REPORT_FILE" == DESK2-* ]]; then
    EXPECTED_DIR="/root/project-docs/kis-autotrade-v4/reports/"
else
    echo "⚠️ 파일명에서 프로젝트 식별 불가: $REPORT_FILE"
    exit 1
fi
ls "${EXPECTED_DIR}${REPORT_FILE}" && echo "✅ 경로 OK" || echo "❌ 파일 없음!"

# 2) 파일명 규칙 검증 (CUR-PROJECT-TASK-SEQ-DATE.md)
echo "=== [2/5] 파일명 규칙 ==="
if echo "$REPORT_FILE" | grep -qP '^(CUR-(GO100|V41)-[A-Z0-9-]+-\d{3}-\d{8}|DESK2-[A-Z0-9-]+-\d{3}-\d{8})\.md$'; then
    echo "✅ 파일명 OK"
else
    echo "⚠️ 파일명 규칙 불일치 — 허용: CUR-{GO100|V41}-TASK-SEQ-DATE.md 또는 DESK2-TASK-SEQ-DATE.md"
fi

# 3) 교차 저장 검사
echo "=== [3/5] 교차 저장 검사 ==="
CROSS=$(git diff --cached --name-only 2>/dev/null | grep -E "^go100/.*DESK2|^go100/.*CUR-V41|^kis-autotrade-v4/.*CUR-GO100")
if [ -z "$CROSS" ]; then
    echo "✅ 교차 저장 없음"
else
    echo "❌ 교차 저장 발견: $CROSS"
    exit 1
fi

# 4) HANDOVER.md 업데이트 확인
echo "=== [4/5] HANDOVER 업데이트 ==="
git diff --cached --name-only | grep -q "HANDOVER.md" && echo "✅ HANDOVER 변경 있음" || echo "⚠️ HANDOVER.md 미변경 — 업데이트 필요"

# 5) push 후 HTTP 200 확인 (push 완료 후 실행)
echo "=== [5/5] HTTP 확인 (push 후 실행) ==="
echo "git push 후 아래 실행:"
echo "curl -s -o /dev/null -w '%{http_code}' https://raw.githubusercontent.com/moongoby/project-docs/master/${EXPECTED_DIR#/root/project-docs/}${REPORT_FILE}"
```

이 스크립트를 /root/project-docs/scripts/path_check.sh로 저장하고 chmod +x 부여.

### 4-8. 보고서 본문 하단 필수 기재

모든 보고서 맨 하단에 아래 형식으로 저장 정보 기재:

```markdown
---
## 저장 정보
- 서버 경로: /root/project-docs/{go100|kis-autotrade-v4}/reports/{파일명}
- GitHub: https://github.com/moongoby/project-docs/blob/master/{경로}/{파일명}
- 커밋: {SHA}
- HTTP 확인: {200|미확인}
- HANDOVER 업데이트: {완료|미완료}
```

본문에 적은 경로와 실제 push 경로가 다르면 작업 미완료 처리.

### 4-9. CEO 보고 규칙 (REPORT-001) — 위반 시 미보고 처리

작업 완료 후 CEO에게 보고할 때:

1. **반드시 git push 먼저 완료**한다
2. **서버 로컬 경로로 보고하지 않는다**
   - ❌ "보고서: /root/project-docs/go100/reports/CUR-GO100-P5-3-..."
   - ❌ "저장 완료했습니다"
   - ❌ "/root/project-docs에 push 했습니다"
3. **반드시 GitHub 브라우저 URL로 보고한다**
   - ✅ https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-P5-3-PORTFOLIO-OPTIMIZER-001-20260227.md
   - ✅ https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/DESK2-VALIDATION-ENGINE-001-20260228.md

4. **보고 형식 (필수)**:

보고서: https://github.com/moongoby/project-docs/blob/master/{프로젝트}/reports/{파일명}  
커밋: https://github.com/moongoby/project-docs/commit/{SHA}  
HANDOVER: https://github.com/moongoby/project-docs/blob/master/{프로젝트}/HANDOVER.md  
HTTP: 200 확인 완료

5. **URL이 실제로 접근 가능한지 확인 후 보고**:
```bash
# push 후 반드시 실행
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  "https://raw.githubusercontent.com/moongoby/project-docs/master/{프로젝트}/reports/{파일명}")
echo "HTTP: $HTTP_CODE"
# 200이 아니면 보고하지 말고 원인 파악
```
- push 안 하고 "작성 완료"로 보고하면 미완료 처리
- 서버 경로만 적고 GitHub URL 없으면 미보고 처리

---

## 5. 버전 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| v1.0 | 2026-02-28 | 초판 — D-001~D-007, T-001~T-004, PATH-001, 절대 규칙 |
| v1.1 | 2026-03-09 | D-003 Agent Loop 20R/10T 전면 개방, 도구 수 57개 갱신, hallucination_guard.py 추가. D-008 능력 전면 개방 지시 신규 추가 (T-051) |
