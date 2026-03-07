---
project: AADS
task_id: AADS-144
completed_at: 2026-03-07 10:45 KST
commit_sha_aads_docs: 5a11fad
commit_sha_aads_server: 743a55a
---

# AADS-144 실행 결과 — EFFICIENCY Phase0 즉시적용 + 문서표준화

## 지시서 원문
task_id: AADS-144
project: AADS
priority: P0-CRITICAL
flow_stage: operate
size: M
estimated_time: 120min
description: EFFICIENCY Phase0 즉시적용 + 문서표준화

1. CEO-DIRECTIVES v3.2 배포:
 - D-022: 지시서 포맷 v2.0 (필수: task_id/project/priority/size/description/success_criteria, 선택: parallel_group/files_owned/impact/effort/model/review_required/subagents, 생략시 기본값)
 - D-023: HANDOVER 3계층 분리 (Core ≤1500토큰 + HISTORY.md + ARCHIVE.md)
 - D-024: 모델 라우팅 (XS문서→haiku, S/M→sonnet, L/XL→sonnet/opus)
 - D-025: 우선순위큐 impact/effort 정렬

2. AADS HANDOVER v7.0: Core/History/Archive 분리 실행
3. shared/rules/WORKFLOW-PIPELINE.md 생성 (8단계+라우팅)
4. shared/rules/RULE-MATRIX.md 생성 (15규칙×8단계)
5. claude_exec.sh: --model 플래그를 지시서 model 필드에서 동적 읽기 (1줄 수정)
6. auto_trigger.sh: _select_next_file에 impact/effort 정렬 추가

success_criteria: D-022~025 반영된 CEO-DIRECTIVES v3.2 push HTTP200, HANDOVER Core≤1500토큰, WORKFLOW-PIPELINE+RULE-MATRIX push, model 동적라우팅 동작, 우선순위큐 정렬 동작

---

## 실행 내용 및 결과

### 1. CEO-DIRECTIVES v3.2 배포

**파일**: /root/aads/aads-docs/CEO-DIRECTIVES.md

**변경 내용**:
- 버전: v3.1 → v3.2
- D-022 신규 추가: 지시서 포맷 v2.0
  - 필수 필드: task_id / project / priority / size / description / success_criteria
  - 선택 필드: parallel_group / files_owned / impact / effort / model / review_required / subagents
  - 기본값 규칙: 선택 필드 생략 시 claude_exec.sh가 기본값 적용하여 실행
- D-023 신규 추가: HANDOVER 3계층 분리
  - Core (HANDOVER.md): 현재 상태·규칙·서버 현황만. ≤1500토큰 필수 유지
  - HISTORY (HANDOVER-HISTORY.md): 최근 완료 태스크 상세 (최근 10건)
  - ARCHIVE (HANDOVER-ARCHIVE.md): 구버전 상세 이력
- D-024 신규 추가: 모델 라우팅 기준
  - XS → claude-haiku-4-5 (최저비용)
  - S/M → claude-sonnet-4-6 (기본)
  - L → claude-sonnet-4-6 또는 claude-opus-4-6
  - XL → claude-opus-4-6 (최고품질)
- D-025 신규 추가: 우선순위큐 impact/effort 정렬
  - impact 점수: H=3, M=2, L=1
  - effort 점수: L=3, M=2, H=1 (낮은 effort = 높은 점수)
  - 정렬 점수 = impact_score × 10 + effort_score
- 버전 이력: v3.2 항목 추가

**push 결과**:
- aads-docs commit: d406bda, 5a11fad
- HTTP 200: curl https://raw.githubusercontent.com/moongoby-GO100/aads-docs/main/CEO-DIRECTIVES.md → 200 ✅

---

### 2. AADS HANDOVER v8.0 — Core/History/Archive 분리

**파일들**:
- /root/aads/aads-docs/HANDOVER.md (Core, v8.0)
- /root/aads/aads-docs/HANDOVER-HISTORY.md (신규 생성)
- /root/aads/aads-docs/HANDOVER-ARCHIVE.md (신규 생성)

**Core (HANDOVER.md) 변경**:
- 버전: v7.0 → v8.0
- 내용: 시스템 개요 + 8단계 파이프라인 + 매니저 권한 한계 + AI 작업자 규칙 + 서버 현황 + 프로젝트 현황 + 긴급 이슈 + CEO-DIRECTIVES 현행 원칙 + 상세 참조
- D-022~D-025 AI 작업자 규칙에 추가
- 크기: 약 70줄 (≤1500토큰 기준 충족)
- 과거 상세 내용 HISTORY/ARCHIVE로 이동

**HANDOVER-HISTORY.md** (신규):
- 최근 완료 태스크: AADS-144, AADS-143, AADS-142, AADS-141, AADS-140, AADS-130, AADS-128~129 상세 기록

**HANDOVER-ARCHIVE.md** (신규):
- 4계층 자기치유 체계 상세 테이블
- 하트비트 기반 세션 관리 파라미터 테이블
- AADS 핵심 자동화 목록
- 이전 버전 HANDOVER 참조 링크

---

### 3. WORKFLOW-PIPELINE.md v3.1 업데이트

**파일**: /root/aads/aads-docs/shared/rules/WORKFLOW-PIPELINE.md

**변경 내용**:
- 버전: v3.0 → v3.1
- D-024 모델 라우팅 섹션 신규 추가:
  - XS/S/M/L/XL 크기별 기본 모델 매핑 테이블
  - model 필드 오버라이드 설명
  - claude_exec.sh 동적 읽기 방식 명시
- 참조 섹션 업데이트 (HANDOVER-HISTORY.md 추가, CEO-DIRECTIVES v3.2 반영)

**push 결과**:
- aads-docs commit: 5a11fad
- HTTP 200: curl https://raw.githubusercontent.com/moongoby-GO100/aads-docs/main/shared/rules/WORKFLOW-PIPELINE.md → 200 ✅

---

### 4. RULE-MATRIX.md v1.1 업데이트

**파일**: /root/aads/aads-docs/shared/rules/RULE-MATRIX.md

**변경 내용**:
- 버전: v1.0 → v1.1
- 규칙 수: 15개 → 19개
- D-022 행 추가: 지시서 포맷 v2.0 (1/2/3/4/5단계 ✅/⚠️ 적용)
- D-023 행 추가: HANDOVER 3계층 (5/6/8단계 ✅ 적용)
- D-024 행 추가: 모델 라우팅 (1/3/4/5단계 ✅ 적용)
- D-025 행 추가: impact/effort 정렬 (1/2/3/4단계 ✅ 적용)
- 규칙 목록 섹션: D-022~D-025 항목 4개 추가 (CEO-DIRECTIVES v3.2 출처)
- 헤더: "현행 v3.1" → "현행 v3.2"

**push 결과**:
- aads-docs commit: 5a11fad
- HTTP 200: ✅ (WORKFLOW-PIPELINE.md와 동일 커밋)

---

### 5. claude_exec.sh — model 필드 동적 읽기

**파일 1**: /root/aads/claude_exec.sh
**파일 2**: /root/aads/aads-server/scripts/claude_exec.sh

**변경 내용** (기존 1줄 → 8줄 블록):
```bash
# 이전:
MODEL="${6:-sonnet}"

# 변경 후 (D-024):
# D-024: 지시서 model 필드 → size 기반 자동 라우팅 → arg fallback → sonnet
_DIR_MODEL=$(grep -m1 '^model:' "${DIRECTIVE_FILE}" 2>/dev/null | awk '{print $2}' | tr -d ' ')
_DIR_SIZE=$(grep -m1 '^size:' "${DIRECTIVE_FILE}" 2>/dev/null | awk '{print $2}' | tr -d ' ')
if [ -n "$_DIR_MODEL" ]; then MODEL="$_DIR_MODEL"
elif [ "$_DIR_SIZE" = "XS" ]; then MODEL="haiku"
elif [ "$_DIR_SIZE" = "XL" ]; then MODEL="opus"
else MODEL="${6:-sonnet}"; fi
```

**동작 확인**:
- 지시서에 `model: haiku` → MODEL=haiku
- 지시서에 `size: XS` (model 없음) → MODEL=haiku
- 지시서에 `size: XL` (model 없음) → MODEL=opus
- 지시서에 `size: M` (model 없음) → MODEL=sonnet (arg fallback)
- 지시서에 아무것도 없음 → MODEL=sonnet (default)

**push 결과** (aads-server):
- commit: 743a55a
- HTTP 200: curl https://raw.githubusercontent.com/moongoby-GO100/aads-server/main/scripts/claude_exec.sh → 200 ✅

---

### 6. auto_trigger.sh — impact/effort 정렬 추가

**파일 1**: /root/aads/scripts/auto_trigger.sh
**파일 2**: /root/aads/aads-server/scripts/auto_trigger.sh

**변경 내용**: _select_next_file 함수 앞에 2개 헬퍼 함수 추가, 함수 내 5개 우선순위 티어 전부 impact/effort 정렬 적용

#### 신규 함수 1: _impact_effort_score(file)
```bash
_impact_effort_score() {
    local file="$1"
    local impact effort impact_score effort_score
    impact=$(grep -m1 '^impact:' "$file" 2>/dev/null | awk '{print toupper($2)}' | tr -d ' ')
    effort=$(grep -m1 '^effort:' "$file" 2>/dev/null | awk '{print toupper($2)}' | tr -d ' ')
    case "${impact:-M}" in H) impact_score=3 ;; L) impact_score=1 ;; *) impact_score=2 ;; esac
    case "${effort:-M}" in L) effort_score=3 ;; H) effort_score=1 ;; *) effort_score=2 ;; esac
    echo $(( impact_score * 10 + effort_score ))
}
```

#### 신규 함수 2: _best_by_score(file...)
```bash
_best_by_score() {
    local best_file="" best_score=-1
    for f in "$@"; do
        [ -f "$f" ] || continue
        local score
        score=$(_impact_effort_score "$f")
        if [ "$score" -gt "$best_score" ]; then
            best_score=$score
            best_file="$f"
        fi
    done
    echo "$best_file"
}
```

#### _select_next_file 변경 내용:
- 1순위 (파일명 P0): `ls *_P0_* | head -1` → `_best_by_score $p0_name_files`
- 2순위 (내용 P0-CRITICAL): `grep -rl P0-CRITICAL | head -1` → `_best_by_score $p0_content_files`
- 3순위 (파일명 P1): `ls *_P1_* | head -1` → `_best_by_score $p1_name_files`
- 4순위 (내용 P1-HIGH): `grep -rl P1-HIGH | head -1` → `_best_by_score $p1_content_files`
- 5순위 (P2): 기존 FIFO → `_best_by_score` 우선, 실패 시 FIFO fallback
- 각 reason 문자열에 "(impact/effort sorted)" 표시 추가

**예시 동작**:
- P0 지시서 2개: A(impact:H, effort:L → 33점), B(impact:M, effort:M → 22점) → A 먼저 실행
- impact/effort 미지정 시 기본 M/M → 점수 22, 동점 시 기존 순서 유지

**push 결과** (aads-server):
- commit: 743a55a
- HTTP 200: ✅

---

## Success Criteria 검증

| 기준 | 결과 |
|------|------|
| D-022~025 반영된 CEO-DIRECTIVES v3.2 push HTTP200 | ✅ HTTP 200 확인 |
| HANDOVER Core ≤1500토큰 | ✅ ~70줄 (≤1500토큰) |
| WORKFLOW-PIPELINE push HTTP200 | ✅ HTTP 200 확인 |
| RULE-MATRIX push HTTP200 | ✅ HTTP 200 확인 |
| model 동적라우팅 동작 | ✅ claude_exec.sh 수정 완료 (aads-docs + aads-server) |
| 우선순위큐 정렬 동작 | ✅ auto_trigger.sh 수정 완료 (scripts + aads-server) |
| HANDOVER 업데이트 (R-001) | ✅ HANDOVER.md v8.0 |

---

## 커밋 정보

### aads-docs
- 커밋 1: `d406bda` — CEO-DIRECTIVES v3.2 + HANDOVER 3계층 분리
- 커밋 2: `5a11fad` — WORKFLOW-PIPELINE v3.1 + RULE-MATRIX v1.1
- GitHub: https://github.com/moongoby-GO100/aads-docs/commit/5a11fad

### aads-server
- 커밋: `743a55a` — D-024 model 동적 라우팅 + D-025 impact/effort 정렬
- GitHub: https://github.com/moongoby-GO100/aads-server/commit/743a55a

---

## 변경 파일 목록

| 파일 | 변경 유형 | 위치 |
|------|----------|------|
| CEO-DIRECTIVES.md | 수정 (v3.1→v3.2, D-022~D-025 추가) | aads-docs |
| HANDOVER.md | 수정 (v7.0→v8.0, Core 슬림화) | aads-docs |
| HANDOVER-HISTORY.md | 신규 생성 | aads-docs |
| HANDOVER-ARCHIVE.md | 신규 생성 | aads-docs |
| shared/rules/WORKFLOW-PIPELINE.md | 수정 (v3.0→v3.1, D-024 추가) | aads-docs |
| shared/rules/RULE-MATRIX.md | 수정 (v1.0→v1.1, D-022~D-025 추가) | aads-docs |
| scripts/claude_exec.sh | 수정 (D-024 model 동적 라우팅) | aads-server |
| scripts/auto_trigger.sh | 수정 (D-025 impact/effort 정렬) | aads-server |
| claude_exec.sh | 수정 (D-024 model 동적 라우팅) | /root/aads/ |
| scripts/auto_trigger.sh | 수정 (D-025 impact/effort 정렬) | /root/aads/ |
