task_id: AADS-162
project: AADS
priority: P1
size: M
model: claude-sonnet-4-6
DEPENDS_ON: AADS-161
description: |
  디자인 검증 에이전트 시스템 구축 — 시각적 회귀 감지 + 디자인 규칙 준수 확인
  
  1. .claude/agents/design-reviewer.md 생성
     - before 스크린샷: 작업 시작 전 대상 페이지 browser_screenshot → /tmp/aads_workspace/screenshots/before_{task_id}.png 저장
     - after 스크린샷: 작업 완료+배포 후 동일 페이지 browser_screenshot → after_{task_id}.png 저장
     - Claude vision 분석: before/after 이미지를 Anthropic messages API image 블록으로 전달
       → 의도된 변경 vs 비의도적 변경(레이아웃 깨짐, 텍스트 잘림, 요소 사라짐) 분류
     - 디자인 기준 검증: 다크 테마(#0a0a0a 배경), Tailwind CSS 규칙, 카드 레이아웃(rounded-lg, border-gray-800, p-4), 반응형(md:grid-cols-2 lg:grid-cols-3)
     - 판정: DESIGN_PASS / DESIGN_REVIEW_NEEDED + 상세 사유 + 문제 영역 좌표
  
  2. claude_exec.sh 수정 — QA PASS 후 디자인 검증 세션 자동 호출
     - 프론트엔드 파일(.tsx, .css, .html) 변경이 포함된 작업에만 적용
     - DESIGN_REVIEW_NEEDED 시 CEO Chat에 before/after 스크린샷 + 보고 자동 전송
     - DESIGN_PASS 시 RESULT_FILE에 design_status: PASS 기록
  
  3. 기준 스크린샷 저장소 구축
     - /tmp/aads_workspace/screenshots/baselines/ 폴더에 프로젝트별 주요 페이지 기준 이미지 저장
     - 페이지 목록: dashboard(/), tasks(/tasks), ceo-chat(/ceo-chat), ops(/ops), conversations(/conversations)
     - 최초 1회 수동 캡처 후 DESIGN_PASS될 때마다 after를 새 baseline으로 갱신
  
  4. DB 테이블 확장: design_reviews (task_id, page_url, before_path, after_path, verdict, issues_json, created_at)

success_criteria: |
  - .claude/agents/design-reviewer.md 파일 존재, vision 분석 로직 포함
  - 프론트엔드 변경 작업 시 before/after 스크린샷 자동 캡처
  - Claude vision API로 시각적 비교 분석 정상 동작
  - DESIGN_REVIEW_NEEDED 시 CEO Chat에 스크린샷 포함 보고 전송
  - baselines/ 폴더에 5개 페이지 기준 이미지 존재
  - design_reviews 테이블 생성, 레코드 삽입 정상
  - git push HTTP 200 확인
  - HANDOVER.md 업데이트 (D-031: 디자인 검증 의무화 규칙 추가)
  - 커밋 메시지: [AADS-162] feat: 디자인 검증 에이전트 시스템 구축

files_owned:
  - .claude/agents/design-reviewer.md
  - scripts/claude_exec.sh
  - app/api/ceo_chat_tools.py
  - migrations/add_design_reviews.sql

impact: H
effort: M
review_required: true
subagents: security-reviewer, doc-writer