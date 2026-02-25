# 뉴톡 이미지 자동화 — 문서 관리 규칙
> 최종 갱신: 2026-02-23 KST
> 프로젝트 코드: NASIMG
> Public 문서 위치: https://github.com/moongoby/project-docs/tree/master/nas-image

---

## 1. 문서 저장소 구조

### 1.1 Private Repo (소스코드 + 문서 원본)
github.com/moongoby/newtalk-image-auto (branch: main)
```
└── docs/
    ├── CONTEXT.md       # 프로젝트 현재 상태
    ├── CHANGELOG.md     # 변경 이력
    ├── PLANNING.md      # 기획서
    ├── PIPELINE_PROCESS.md  # 전체 파이프라인 프로세스 (AS-IS/TO-BE, P1~P6)
    ├── ARCHITECTURE.md  # 아키텍처
    ├── HANDOVER.md      # 인수인계서
    ├── DATABASE.md      # DB 스키마
    ├── DOC_RULES.md     # 문서 관리 규칙 (본 문서)
    ├── reports/        # 작업 보고서
    │   └── CUR-NASIMG-{TASK}-{SEQ}-{YYYYMMDD}.md
    └── handover/       # 대화 인계서
        └── YYYYMMDD_주제.md
```

### 1.2 Public Docs Repo (문서 공유용)
github.com/moongoby/project-docs (branch: master)
```
└── nas-image/
    ├── CONTEXT.md
    ├── CHANGELOG.md
    ├── PLANNING.md
    ├── PIPELINE_PROCESS.md
    ├── ARCHITECTURE.md
    ├── HANDOVER.md
    ├── DATABASE.md
    ├── DOC_RULES.md
    ├── cursorrules.md
    └── reports/
        └── CUR-NASIMG-{TASK}-{SEQ}-{YYYYMMDD}.md
```

---

## 2. 보고서 파일명 규칙

### 2.1 네이밍 패턴
`CUR-NASIMG-{TASK}-{SEQ}-{YYYYMMDD}.md`

| 구분 | 설명 | 예시 |
|------|------|------|
| CUR | Cursor 작업 접두사 (고정) | CUR |
| NASIMG | 프로젝트 코드 (고정) | NASIMG |
| TASK | 작업 유형 (대문자, 하이픈 연결) | E2E-TEST, TONE-REVIEW, PIPELINE-REVIEW |
| SEQ | 순번 (001부터) | 001, 002 |
| YYYYMMDD | 작성일 (KST 기준) | 20260223 |

### 2.2 보고서 유형별 TASK 코드

| TASK 코드 | 용도 |
|-----------|------|
| E2E-TEST | 실사진 E2E 파이프라인 테스트 |
| TONE-REVIEW | 톤매칭 소스 검수 |
| PIPELINE-REVIEW | 배치 파이프라인 소스 검수 |
| CORRECT-REVIEW | 자동보정 소스 검수 |
| DOCKER-BUILD | Docker 빌드/배포 보고 |
| BUG-FIX | 버그 수정 보고 |
| FEATURE | 신규 기능 구현 보고 |
| HOTFIX | 긴급 수정 보고 |
| REFACTOR | 리팩터링 보고 |
| DEPLOY | 배포 보고 |
| DB-CONN | DB 접속/폴링 테스트 (P1 선행 등) |
| HANDOVER | 대화 인계서 |

### 2.3 보고서 예시 파일명
- `CUR-NASIMG-E2E-TEST-001-20260223.md`
- `CUR-NASIMG-TONE-REVIEW-001-20260223.md`
- `CUR-NASIMG-PIPELINE-REVIEW-001-20260223.md`
- `CUR-NASIMG-DOCKER-BUILD-001-20260223.md`
- `CUR-NASIMG-BUG-FIX-001-20260224.md`

---

## 3. 보고서 저장 경로

### 3.1 서버 경로
- **Private**: `/volume1/뉴톡/newtalk-image-auto/docs/reports/CUR-NASIMG-{TASK}-{SEQ}-{YYYYMMDD}.md`
- **Public**: `/volume1/뉴톡/project-docs/nas-image/reports/CUR-NASIMG-{TASK}-{SEQ}-{YYYYMMDD}.md`

### 3.2 GitHub URL
- **Private**: https://github.com/moongoby/newtalk-image-auto/blob/main/docs/reports/CUR-NASIMG-{TASK}-{SEQ}-{YYYYMMDD}.md
- **Public**: https://github.com/moongoby/project-docs/blob/master/nas-image/reports/CUR-NASIMG-{TASK}-{SEQ}-{YYYYMMDD}.md

### 3.3 등록 확인 명령
```bash
curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/reports/CUR-NASIMG-{TASK}-{SEQ}-{YYYYMMDD}.md
# → 200 이면 정상 등록
```

---

## 4. 문서 동기화 절차

### 4.1 Private → Public 동기화
```bash
cd /volume1/뉴톡/newtalk-image-auto
git add -A && git commit -m "작업 내용" && git push origin main

cd /volume1/뉴톡/project-docs
git pull origin master
cp /volume1/뉴톡/newtalk-image-auto/docs/CONTEXT.md nas-image/CONTEXT.md
cp /volume1/뉴톡/newtalk-image-auto/docs/CHANGELOG.md nas-image/CHANGELOG.md
cp /volume1/뉴톡/newtalk-image-auto/docs/HANDOVER.md nas-image/HANDOVER.md
cp /volume1/뉴톡/newtalk-image-auto/docs/DATABASE.md nas-image/DATABASE.md
cp /volume1/뉴톡/newtalk-image-auto/docs/PLANNING.md nas-image/PLANNING.md
cp /volume1/뉴톡/newtalk-image-auto/docs/PIPELINE_PROCESS.md nas-image/PIPELINE_PROCESS.md
cp /volume1/뉴톡/newtalk-image-auto/docs/ARCHITECTURE.md nas-image/ARCHITECTURE.md
cp /volume1/뉴톡/newtalk-image-auto/docs/DOC_RULES.md nas-image/DOC_RULES.md
cp /volume1/뉴톡/newtalk-image-auto/.cursorrules nas-image/cursorrules.md
cp -r /volume1/뉴톡/newtalk-image-auto/docs/reports/ nas-image/reports/
git add -A
git commit -m "[sync] 문서 동기화 (KST $(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M'))"
git push origin master
```

### 4.2 동기화 후 확인
```bash
git log --oneline -3
curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/DOC_RULES.md
# → 200
```

---

## 5. 핵심 문서 역할

| 문서 | 역할 | 갱신 시점 |
|------|------|-----------|
| CONTEXT.md | 프로젝트 현재 상태, 새 대화 시작점 | 매 작업 완료 시 |
| CHANGELOG.md | 날짜별 변경 이력 | 매 작업 완료 시 |
| HANDOVER.md | 인수인계서, 접속정보, 작업규칙 | 인계 시 |
| PLANNING.md | AS-IS/TO-BE, 로드맵 | Phase 변경 시 |
| PIPELINE_PROCESS.md | 전체 파이프라인 프로세스 (P1~P6, 로드맵) | 파이프라인 변경 시 |
| ARCHITECTURE.md | 시스템 구조, 모듈, API | 구조 변경 시 |
| DATABASE.md | DB 스키마, 테이블, 관계 | 테이블 변경 시 |
| DOC_RULES.md | 문서 관리 규칙 (본 문서) | 규칙 변경 시 |
| cursorrules.md | Cursor 작업 규칙 | 규칙 변경 시 |

---

## 6. Cursor 작업 완료 보고 템플릿

작업 완료 시 반드시 아래 형식으로 보고:

```
=== 작업 완료 보고 ===
보고서: docs/reports/CUR-NASIMG-{TASK}-{SEQ}-{YYYYMMDD}.md
GitHub: https://github.com/moongoby/project-docs/blob/master/nas-image/reports/CUR-NASIMG-{TASK}-{SEQ}-{YYYYMMDD}.md
확인: curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/reports/CUR-NASIMG-{TASK}-{SEQ}-{YYYYMMDD}.md → 200
Private: https://github.com/moongoby/newtalk-image-auto (main)
Public:  https://github.com/moongoby/project-docs (master)
최근 커밋: {해시} {메시지}
동기화: 완료/미완료
KST: YYYY-MM-DD HH:MM:SS
```
