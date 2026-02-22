# DOC-VERSION-AUDIT 보고서

**작업지시서**: DOC-VERSION-AUDIT  
**서버**: 211.188.51.113  
**경로**: /root/kis-autotrade-v4  
**일시**: 2026-02-23  
**성격**: 읽기 전용 (수정 없음)

---

## 사전 확인 결과

| 항목 | 기대값 | 실제 | 결과 |
|------|--------|------|------|
| strategy_cards COUNT | 62 | 62 | ✅ |
| v4_positions OPEN | 5 | 5 | ✅ |
| kis-v41-api | active (running) | active (running) | ✅ |
| kis-v41-monitor | active (running) | active (running) | ✅ |
| df -h / | - | 53% used (45G avail) | ✅ |

---

## 1. 전체 .md 파일 목록 (경로, 생성일, 최종수정일, 커밋수)

프로젝트 내 .md 파일은 **venv/node_modules/.venv 제외** 기준으로 **약 270개 이상** 존재한다.

- **docs/**: 루트 문서·아키텍처·기획·인계·API 포털 등 (약 250개 이상, kis-api-portal/excel-full 포함)
- **report/**: 작업/감사 보고서 43개
- **backend/migrations/README.md**, **CLAUDE.md**, **.cursor/rules/kis-v41-rules.md**
- **frontend/README.md** (프로젝트 루트에는 README.md 없음)

**주요 문서만 요약 (git 이력 기준):**

| 경로 | 최초 커밋 | 최종 커밋 | 커밋 수 |
|------|-----------|-----------|---------|
| ./CLAUDE.md | 2026-02-21 11:29 | 2026-02-22 00:55 | 29 |
| ./docs/HANDOVER-V50-20260214.md | 2026-02-13 23:12 | 2026-02-13 23:12 | 1 |
| ./docs/HANDOVER-CORRECTIONS.md | 2026-02-14 00:20 | 2026-02-14 00:20 | 1 |
| ./docs/architecture-v1.0.md | 2026-02-21 10:42 | 2026-02-21 10:42 | 1 |
| ./docs/v41-architecture-v1.1.md | (동일 커밋) | 2026-02-21 | 1 |
| ./docs/go100-architecture-v1.0.md | 2026-02-21 10:42 | 2026-02-21 10:42 | 1 |
| ./docs/go100-architecture-v1.1.md | 2026-02-21 10:42 | 2026-02-21 10:42 | 1 |
| ./docs/architecture/README.md | 2026-02-22 00:54 | 2026-02-22 00:54 | 1 |
| ./docs/architecture/v41-adaptive-architecture-spec.md | 2026-02-22 00:54 | 2026-02-22 00:54 | 1 |
| ./docs/architecture/v41-development-plan-spec.md | 2026-02-22 00:54 | 2026-02-22 00:54 | 1 |
| ./docs/architecture/v41-phase-a-code-spec.md | 2026-02-22 00:54 | 2026-02-22 00:54 | 1 |
| ./docs/design/strategy_card_system_design_20260220.md | 2026-02-20 18:45 | 2026-02-20 18:45 | 1 |
| ./docs/data_requirements_20260220.md | 2026-02-20 15:34 | 2026-02-20 15:34 | 1 |
| ./docs/CHART-FEATURE-PLAN.md | 2026-02-14 01:49 | 2026-02-14 01:49 | 1 |
| ./docs/PHASE6-MIGRATION-PLAN.md | (존재) | - | 1 |
| ./docs/REAL_MOCK_PARALLEL_PLAN.md | (존재) | - | 1 |

report/ 내 .md는 대부분 **git 미추적**(신규 생성·수정 후 미커밋)이며, ls -la 기준 최종 수정일 2026-02-21~2026-02-23.

---

## 2. 기획서 존재 여부: **Y (부분)**

- **파일명**:  
  - `docs/CHART-FEATURE-PLAN.md` (차트 기능 기획)  
  - `docs/REAL_MOCK_PARALLEL_PLAN.md`  
  - `docs/PHASE6-MIGRATION-PLAN.md`  
  - `docs/architecture/v41-development-plan-spec.md` (V4.1 개발 실전 기획, Phase 2-B~6)  
  - `docs/architecture/v41-phase-a-code-spec.md` (Phase A 코드 명세)  
  - `docs/data_requirements_20260220.md` (데이터 요구사항)
- **버전 표기**: **Y** (v41-* spec은 문서 버전 V4.1, 일부는 파일명에 일자 포함)
- **최종 수정일**: 2026-02-14 ~ 2026-02-22 (git 기준)
- **커밋 이력 수**: 대부분 1~2회, 개발 기획 spec은 1회

**종합**: 서비스 전체 PRD/요구사항 정의서라는 단일 “기획서”는 없고, **기능/단계별 계획·명세 문서는 존재**하며 버전/일자 표기가 일부 적용됨.

---

## 3. 아키텍처 문서 존재 여부: **Y**

- **파일명**:  
  - `docs/v41-architecture-v1.1.md` (V4.1 시스템 아키텍처, 문서 버전 1.1)  
  - `docs/go100-architecture-v1.1.md` (GO100 아키텍처, 문서 버전 1.1)  
  - `docs/architecture-v1.0.md` (v1.0 통합, 최신은 v1.1 분리 문서로 안내)  
  - `docs/go100-architecture-v1.0.md` (구버전, v1.1로 이동 안내)  
  - `docs/architecture/README.md` (아키텍처 폴더 인덱스)  
  - `docs/architecture/v41-adaptive-architecture-spec.md`  
  - `docs/architecture/v41-development-plan-spec.md`  
  - `docs/architecture/v41-phase-a-code-spec.md`  
  - `docs/design/strategy_card_system_design_20260220.md` (전략 카드 DB 설계)  
  - `docs/new_strategies_design.md` (신규 전략 규칙 설계)
- **버전 표기**: **Y** (문서 버전 1.0/1.1, 코드 버전 4.1.0, Git 태그 v4.1.0-phase6-batch3 명시)
- **최종 수정일**: 2026-02-20 ~ 2026-02-22 (git 기준)
- **포함 내용**:  
  - **모듈 구조**: V4.1/GO100 서비스 개요, 계층, 디렉터리 구조  
  - **DB 설계**: strategy_cards, v4_desk_strategy_mapping, v4_signals, v4_trades, v4_strategy_performance, v4_backtest_profile, universe 버전화 등  
  - **API 설계**: 라우터·엔드포인트 요약 (상세는 별도 API 문서)  
  - **배포/운영**: 서버 경로, systemd, Nginx, 브랜치·태그

---

## 4. 인계서 존재 여부: **Y**

- **파일명**:  
  - `docs/HANDOVER-V50-20260214.md` (Handover V5.0, 문서 ID: HANDOVER-V50-20260214)  
  - `docs/HANDOVER-CORRECTIONS.md` (인계 보정)
- **버전**: V5.0 (2026-02-14)
- **최종 수정일**: 2026-02-13 ~ 2026-02-14 (git 기준)
- **커밋 이력**: 각 1회

---

## 5. README 상태

- **프로젝트 루트**: **README.md 없음** (상위 디렉터리 `/root/kis-autotrade-v4`에 README.md 미존재)
- **내용 요약**:  
  - `frontend/README.md`: 프론트엔드 프로젝트 설명  
  - `docs/architecture/README.md`: 아키텍처 문서 인덱스, V4.1 문서 버전·작성일·상위 폴더 안내  
  - `backend/migrations/README.md`: 마이그레이션 관련 안내  
  - `docs/api/kisapi/README.md`, `docs/kis-api-portal/` 하위 README 등: API/포털 설명
- **최종 수정일**: git 기준 2026-02-13 ~ 2026-02-22 (파일별 상이)

---

## 6. CHANGELOG 존재: **N**

- 프로젝트 전용 **CHANGELOG.md / 변경이력.md / release notes** 파일 없음.
- `report/` 내 `*HISTORY*`, `*변경*` 등 파일명 검색 시: `DASHBOARD-HISTORY-REPORT-20260222.md` 등 “히스토리” 보고서만 존재 (변경 이력 전용 문서 아님).
- 문서 내 “버전 이력” 표는 **아키텍처 문서 내부** (v41-architecture-v1.1.md, go100-architecture-v1.1.md, architecture-v1.0.md)에 있음.

---

## 7. report 디렉토리 내용

- **위치**: `/root/kis-autotrade-v4/report/`
- **파일 수**: **43개** .md
- **성격**: 작업 완료/감사/점검 보고서 (BT-*, GO100-*, DESK-*, DASH-*, CUR-*, STRAT-*, BUNDLE4*, OPTIMIZATION-INFRA-AUDIT, REGIME-BACKFILL-DESK-ROLE-AUDIT, OVERLAP-REGIME-CROSS 등)
- **일자**: 2026-02-21 ~ 2026-02-23 (파일명·수정일 기준)
- **버전 관리**: 대부분 **git 미추적** 또는 최근 추가로 커밋 0~1회로 추정 (report/ 전용 git 이력 미집계).

---

## 8. git 태그/브랜치 기반 버전 관리: **Y (제한적)**

- **태그 목록**: `v4.1.0-phase6-batch3` (1개)
- **브랜치 목록**:  
  - 로컬: `main`, `phase-2c-command-center` (현재 체크아웃)  
  - 원격: `remotes/origin/genspark_ai_developer`, `remotes/origin/master`, `remotes/origin/phase-2c-command-center`
- **최근 커밋**: GO100 전략저장/상세/토글, BT 엔진 업그레이드, UNIFIED-SAVE, MY-STRATEGY-FIX, CARD-DETAIL-FIX 등 (커밋 메시지에 작업지시/이슈 약어 반영)

---

## 9. 문서 버전 관리 종합 평가

| 구분 | 상태 | 비고 |
|------|------|------|
| **기획서** | **미관리** | 단일 PRD 없음; 기능/단계별 계획·명세는 있으나 체계적 버전·이력 관리 부재 |
| **아키텍처** | **관리됨** | v1.0/v1.1 구분, 문서 버전·날짜·최신 문서 안내 있음. 다만 커밋 이력은 1~2회 수준 |
| **인계서** | **관리됨** | HANDOVER-V50, HANDOVER-CORRECTIONS 존재, 문서 ID·일자 명시. 이력은 소수 커밋 |
| **CHANGELOG** | **부재** | 프로젝트 단위 CHANGELOG 없음. 변경 이력은 아키텍처 문서 내 표에 일부 반영 |

---

## 10. 개선 권장사항

1. **프로젝트 루트 README.md**  
   - 프로젝트명, 목적, 구조, 실행 방법, 환경 변수·설정 요약, 문서/아키텍처 링크를 한 페이지에 정리해 두는 것을 권장.

2. **CHANGELOG 도입**  
   - `CHANGELOG.md`를 두고, 릴리스/배포 단위별로 변경 요약(날짜, 버전, 주요 변경)을 기록하면 문서·코드 버전 추적에 유리함.

3. **기획서 통합/인덱스**  
   - “기획서” 또는 “요구사항” 디렉터리(또는 `docs/plan/`)를 두고, PRD·기능 기획·데이터 요구사항 문서를 모으고 `README` 또는 인덱스 md로 링크해 두는 것을 권장.

4. **report/ 버전 관리**  
   - report/ 내 보고서를 git에 포함할지 정책을 정한 뒤, 포함한다면 커밋 메시지에 보고서 ID·일자를 넣어 추적하기 쉽게 하는 것을 권장.

5. **문서 버전 표기 일관화**  
   - 중요한 문서에는 상단에 “문서 버전, 최종 수정일, 변경 요약” 블록을 두어(아키텍처 문서처럼) 일관 적용하는 것을 권장.

---

## 11. strategy_cards COUNT

**62** ✅

---

## 12. v4_positions OPEN

**5** ✅

---

## 13. 이슈

- **없음.** 사전 확인 항목 충족, DB/서비스 이상 없음. 문서 감사만 수행했으며 코드/DB/설정 변경 없음.

---

*DOC-VERSION-AUDIT 완료. 수정 금지.*
