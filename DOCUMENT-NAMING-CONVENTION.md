# project-docs 문서 관리 규칙
> 최종 갱신: 2026-02-24
> 관리자: CEO (moongoby)
> 적용 대상: 모든 커서(Cursor) 세션, 모든 AI 에이전트

---

## 1. 프로젝트별 폴더 구조

```
project-docs/  ← repo 루트
├── DOCUMENT-NAMING-CONVENTION.md  ← ★ 이 파일 (마스터 규칙)
│
├── go100/  ← GO100 프로젝트 전용
│   ├── CONTEXT.md  ← GO100 컨텍스트
│   ├── CURSORRULES.md  ← 커서 규칙 포인터
│   ├── ARCHITECTURE.md
│   ├── API_SPEC.md
│   ├── CHANGELOG.md
│   ├── DB_SCHEMA.md
│   ├── HANDOVER.md
│   ├── HANDOVER-YYYYMMDD.md  ← 일자별 인계서
│   ├── ISSUES.md
│   ├── PLANNING.md
│   ├── ROADMAP.md
│   ├── docs/  ← GO100 상세 기술 문서
│   │   └── DB-SCHEMA-GO100.md
│   ├── rules/  ← GO100 전용 규칙
│   │   └── go100-rules.md
│   ├── reports/  ← GO100 작업 보고서 ★
│   │   └── CUR-GO100-{TASK}-{SEQ}-{YYYYMMDD}.md
│   └── review/  ← GO100 코드 리뷰
│
├── kis-autotrade-v4/  ← V4.1 프로젝트 전용
│   ├── CONTEXT.md  ← V4.1 컨텍스트
│   ├── docs/
│   │   ├── DB-SCHEMA.md
│   │   └── API-DOCS-CATALOG.md
│   ├── rules/
│   │   ├── kis-v41-rules.md  ← V4.1 전용 규칙
│   │   ├── CLAUDE.md  ← 공통 Claude 규칙
│   │   ├── MARKET-HOURS-KR.md
│   │   └── go100-rules.md  ← GO100 규칙 (사본, 원본은 go100/rules/)
│   ├── reports/  ← V4.1 작업 보고서 ★
│   │   └── CUR-V41-{TASK}-{SEQ}-{YYYYMMDD}.md
│   └── review/  ← V4.1 코드 리뷰
```

---

## 2. 보고서 파일명 규칙

### 2-1. 형식

`CUR-{PROJECT}-{TASK_NAME}-{SEQ}-{YYYYMMDD}.md`

| 구분 | 값 | 설명 |
|------|------|------|
| `CUR` | 고정 접두어 | Cursor 작업 식별 |
| `PROJECT` | `GO100` 또는 `V41` | 프로젝트 구분 |
| `TASK_NAME` | 영문 대문자, 하이픈 구분 | 작업 내용 요약 |
| `SEQ` | `001` ~ `999` | 동일 작업의 일련번호 |
| `YYYYMMDD` | `20260224` | 작업일 (KST 기준) |

### 2-2. TASK_NAME 유형

| 유형 | 약어 | 설명 | 예시 |
|------|------|------|------|
| 버그 수정 | FIX | 일반 버그 수정 | CHATWIDGET-FIX |
| 긴급 수정 | HOTFIX | 긴급 장애 수정 | HOTFIX-SAVE-500 |
| 진단 | DIAG | 원인 분석·진단 | INDEX-DAILY-DIAG |
| 검증 | VERIFY | 기능 검증·확인 | E2E-TRADE-VERIFY |
| 감사 | AUDIT | 코드/데이터 감사 | REGIME-SOURCE-AUDIT |
| 연구 | RESEARCH | 기술 조사·연구 | REGIME-STRATEGY-RESEARCH |
| E2E 테스트 | E2E | 통합 테스트 | CARD-E2E |
| 마이그레이션 | MIGRATE | 데이터/코드 이전 | FUND-WEIGHT-CARD-MIGRATE |
| 문서 작업 | DOC | 문서 생성·정리 | DOCS-REORGANIZE |
| 스캔 | SCAN | 아키텍처·코드 스캔 | ARCHITECTURE-SCAN |
| 리뷰 | REVIEW | 코드 리뷰 | CODE-REVIEW-PIPELINE |

### 2-3. 올바른 예시

| 파일명 | 저장 위치 |
|--------|-----------|
| `CUR-GO100-CHATWIDGET-FIX-004-20260223.md` | `go100/reports/` |
| `CUR-GO100-INDEX-DAILY-FIX-001-20260223.md` | `go100/reports/` |
| `CUR-GO100-REGIME-SOURCE-AUDIT-001-20260223.md` | `go100/reports/` |
| `CUR-V41-ARCHITECTURE-SCAN-001-20260223.md` | `kis-autotrade-v4/reports/` |
| `CUR-V41-STRATEGY-CARDS-COUNT-DIAG-001-20260223.md` | `kis-autotrade-v4/reports/` |
| `CUR-V41-BT-ENGINE-UPGRADE-001-20260223.md` | `kis-autotrade-v4/reports/` |

### 2-4. 잘못된 예시 (사용 금지)

| 잘못된 파일명 | 문제점 |
|--------------|--------|
| `20260223-HOTFIX-SAVE-500.md` | CUR- 접두어·PROJECT 없음 |
| `ARCHITECTURE-FULL-SCAN-V1.2-20260223.md` | CUR- 접두어·PROJECT 없음 |
| `CODE-REVIEW-PIPELINE-20260223.md` | CUR-·PROJECT 없음, SEQ 없음 |
| `CUR-GO100-FIX-20260223.md` | TASK_NAME 너무 짧음, SEQ 없음 |

---

## 3. 저장 위치 규칙

### 3-1. 프로젝트별 분리 저장 (절대 규칙)

| 보고서 접두어 | 저장 폴더 | 비고 |
|--------------|-----------|------|
| `CUR-GO100-*` | `go100/reports/` | GO100 전용 |
| `CUR-V41-*` | `kis-autotrade-v4/reports/` | V4.1 전용 |

**교차 저장 금지**: GO100 보고서를 `kis-autotrade-v4/reports/`에 저장하거나, V4.1 보고서를 `go100/reports/`에 저장하지 않는다.

### 3-2. 판별 기준

보고서가 어느 프로젝트인지 불분명할 때:

| 조건 | 분류 |
|------|------|
| go100_* 테이블 관련 | GO100 |
| GO100 API (/api/go100/*) 관련 | GO100 |
| GO100 프론트엔드 (src/go100/*) 관련 | GO100 |
| go100/go100-frontend 서비스 관련 | GO100 |
| strategy_cards, v4_positions 등 V4.1 테이블 관련 | V4.1 |
| V4.1 API (/api/v1/*) 관련 | V4.1 |
| kis-v41-* 서비스 관련 | V4.1 |
| DESK 1~5 전략 운영 관련 | V4.1 |
| 공통 DB (index_daily 등) 이슈라도 GO100에서 발행 | GO100 |
| 공통 DB 이슈라도 V4.1에서 발행 | V4.1 |

---

## 4. 인계서 규칙

| 문서 | 파일명 | 위치 |
|------|--------|------|
| GO100 인계서 | `HANDOVER-YYYYMMDD.md` | `go100/` |
| V4.1 인계서 | `HANDOVER-YYYYMMDD.md` | `kis-autotrade-v4/` |

인계서에는 반드시 포함: 서버 환경, 진행 중인 작업, 대기 작업, CEO 결정 대기 항목, 필수 읽기 URL.

---

## 5. 커서 지시서 작성 시 필수 포함

모든 커서 작업 지시서에 아래를 **반드시 명시**:

- **보고서 저장 경로**
  - 서버: `/root/project-docs/{go100|kis-autotrade-v4}/reports/CUR-{PROJECT}-{TASK}-{SEQ}-{YYYYMMDD}.md`
  - GitHub: `https://github.com/moongoby/project-docs/blob/master/{go100|kis-autotrade-v4}/reports/CUR-{PROJECT}-{TASK}-{SEQ}-{YYYYMMDD}.md`
- **확인 명령**
  - `curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby/project-docs/master/{go100|kis-autotrade-v4}/reports/CUR-{PROJECT}-{TASK}-{SEQ}-{YYYYMMDD}.md` → 200

---

## 6. 규칙 문서 자체의 관리

| 문서 | 위치 | 역할 |
|------|------|------|
| `DOCUMENT-NAMING-CONVENTION.md` | repo 루트 | 마스터 규칙 (이 파일) |
| `go100/rules/DOCUMENT-RULES.md` | GO100 rules | GO100용 사본 + 요약 |
| `kis-autotrade-v4/rules/DOCUMENT-RULES.md` | V4.1 rules | V4.1용 사본 + 요약 |

규칙 변경 시 **마스터(루트)**를 먼저 수정하고, 각 프로젝트 사본에 동기화한다.

---

## 7. 변경 이력

| 일자 | 내용 |
|------|------|
| 2026-02-24 | 최초 작성 (CUR-GO100-DOCS-NAMING-RULE-001) |
