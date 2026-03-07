task_id: AADS-164
title: "CEO Chat LangGraph 에이전트 개별 호출 시스템 구축"
priority: P0-CRITICAL
size: XL
impact: H
effort: H
model: claude-opus-4-6
server: 68
workdir: /root/aads/aads-server
review_required: true
subagents: ["security-reviewer", "test-writer", "doc-writer"]

description: |
  CEO Chat에서 LangGraph 에이전트 개별 호출 시스템 구축
  — "QA 진행해", "디자인 검수해", "설계 검토해" 등 자연어로 에이전트 직접 실행
  
  1. ceo_chat.py Intent Classifier 확장
     - 기존 6개 → 10개 인텐트 확장
     - 추가 인텐트 + 키워드:
       qa: QA, 테스트, 검증, 품질, 점검, 동작확인
       design: 디자인, 검수, 화면검수, UI검수, 시각, 레이아웃
       design_fix: 디자인개선, UI개선, 화면수정, 스타일수정
       architect: 설계, 아키텍처, 구조, 기술비교, 기술검토
     - 우선순위: execute > qa > design > design_fix > architect > browser > dashboard > diagnosis > research > strategy
  
  2. 에이전트 개별 호출 핸들러 구현 (ceo_chat.py 내)
     
     a) _handle_qa_intent():
        - qa_node(state) + judge_node(state) 순차 호출
        - state 구성: CEO 메시지에서 대상 페이지/엔드포인트 추출
        - 대상 미지정 시 DashboardCollector로 최근 변경 태스크 조회 → 해당 페이지 자동 타겟
        - Playwright browser_navigate → browser_snapshot으로 실제 UI 상태 수집하여 state에 주입
        - fetch_url로 API 엔드포인트 스모크 테스트 결과 수집
        - judge_node가 PASS/FAIL 판정 → CEO에게 상세 리포트 반환
        - 비용: qa_node(Sonnet $0.10) + judge_node(Gemini 3.1 Pro $0.08) ≈ $0.18/회
     
     b) _handle_design_intent():
        - browser_navigate → browser_screenshot으로 현재 페이지 캡처
        - baselines/ 폴더에 기준 이미지 있으면 before/after 비교
        - Claude vision API: 스크린샷 + 디자인 기준(다크테마, Tailwind, 카드레이아웃) 프롬프트 전달
        - DESIGN_PASS / DESIGN_REVIEW_NEEDED + 구체적 이슈 목록 반환
        - 비용: Sonnet vision 1회 ≈ $0.15/회
     
     c) _handle_design_fix_intent():
        - _handle_design_intent() 먼저 실행하여 이슈 목록 도출
        - developer_node(state)에 이슈 목록 + 대상 파일 주입
        - developer_node가 코드 수정 → 수정 내용을 CEO에게 보고
        - CEO "진행해" 승인 시 → directive 생성 → 파이프라인 투입
        - 비용: design($0.15) + developer(Sonnet $0.12) ≈ $0.27/회
     
     d) _handle_architect_intent():
        - architect_node(state) 호출
        - CEO 메시지에서 비교 대상 추출 (예: "react-markdown vs MDX")
        - 설계 JSON + 비교표 + 권장안 반환
        - 비용: Opus $0.25/회
  
  3. 에이전트 호출용 경량 state 빌더
     - _build_agent_state(intent, message, context) 함수
     - CEO 메시지 + ContextManager 컨텍스트 + DashboardCollector 데이터로 AADSState 최소 구성
     - 불필요한 필드는 기본값 (iteration_count=0, llm_calls_count=0 등)
     - 각 에이전트 노드가 요구하는 필드만 채워서 전달
  
  4. CEO Chat 응답 포맷 통일
     - 에이전트 결과를 CEO 친화적 마크다운으로 변환
     - QA: "## QA 결과\n### API 테스트\n- /health: ✅ 200\n### UI 검증\n- /tasks: ✅\n### 판정: PASS"
     - Design: "## 디자인 검수\n### 검증 페이지\n[스크린샷]\n### 이슈\n1. 카드 간격\n### 판정: REVIEW_NEEDED"
     - Architect: "## 설계 검토\n### 비교\n| 항목 | A | B |\n..."
  
  5. DB 테이블 생성
     - agent_executions (id, session_id, intent, agent_name, model_used, input_tokens, output_tokens, cost_usd, result_json, verdict, created_at)
     - CEO Chat 세션 내 에이전트 호출 이력 추적
     - /ops 페이지에서 에이전트별 사용량·비용·성공률 조회 가능
  
  6. 기존 에이전트 노드 호환성 보강
     - qa_node, judge_node, architect_node, developer_node, researcher_node가 
       경량 state로 호출 시 에러 없이 동작하는지 검증
     - 누락 필드에 대한 .get() 기본값 처리 보강
     - 각 노드의 LLM 호출이 cost_tracker에 정상 기록되는지 확인

success_criteria: |
  - classify_intent()가 10개 인텐트 정상 분류 (기존 6개 + qa/design/design_fix/architect)
  - CEO Chat에서 "QA 진행해" → qa_node + judge_node 실행 → PASS/FAIL 판정 응답
  - CEO Chat에서 "디자인 검수해" → 스크린샷 캡처 + vision 분석 → DESIGN_PASS/REVIEW_NEEDED 응답
  - CEO Chat에서 "디자인 개선해" → design 분석 + developer_node 수정안 → 응답
  - CEO Chat에서 "설계 검토해" → architect_node 설계 JSON → 응답
  - agent_executions 테이블 생성, 에이전트 호출마다 레코드 삽입
  - 각 에이전트 호출 비용이 cost_tracker에 기록
  - 기존 6개 인텐트(execute/browser/dashboard/diagnosis/research/strategy) 정상 동작 유지
  - git push HTTP 200 확인 (aads-server)
  - HANDOVER.md 업데이트
  - 커밋 메시지: "[AADS] feat: AADS-164 CEO Chat LangGraph 에이전트 개별 호출 시스템"

files_owned:
  - app/api/ceo_chat.py
  - app/services/pipeline_qa.py
  - app/services/pipeline_design.py
  - app/services/agent_state_builder.py
  - migrations/add_agent_executions.sql
  - HANDOVER.md

completion_report:
  file: reports/AADS-164-RESULT.md
  handover_update: true
  telegram_notify: true