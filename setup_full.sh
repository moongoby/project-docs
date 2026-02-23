#!/bin/bash
# 114 서버 project-docs 전체 설정 스크립트
# 실행: bash /data/project-docs/setup_full.sh
set -euo pipefail

cd /data/project-docs
mkdir -p common
mkdir -p scripts

# ──────────────────────────────────────
# 1. ONBOARDING.md
# ──────────────────────────────────────
cat > ONBOARDING.md << 'EOF'
# 새 대화창 / 신규 프로젝트 온보딩

> 이 문서를 Claude 새 대화 첫 메시지에 URL로 전달하면 전체 맥락이 복원됩니다.

## GitHub 문서 허브
- Public 저장소: https://github.com/moongoby/project-docs
- 관리자: moongoby

## 등록된 프로젝트

| 프로젝트 | 서버 | 폴더 | CONTEXT | Cursor Rules |
|----------|------|------|---------|--------------|
| ShortFlow/StyleFlow | 114서버 rfree-0009 | shortflow/ | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/cursorrules.md) |
| GO100 자동매매 | kis-autotrade-v4 | go100/ | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/go100/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/go100/cursorrules.md) |
| NAS 이미지 자동화 | Synology NAS | nas-image/ | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/cursorrules.md) |

## 사용법

### 기존 프로젝트 대화 시작
아래 온보딩 문서를 읽고 작업을 이어가줘: https://raw.githubusercontent.com/moongoby/project-docs/master/ONBOARDING.md 프로젝트: [프로젝트명], 폴더: [폴더명]


### 신규 프로젝트 등록
아래 온보딩 문서를 읽고 신규 프로젝트를 등록해줘: https://raw.githubusercontent.com/moongoby/project-docs/master/ONBOARDING.md 프로젝트명: [이름], 서버: [서버정보], 폴더명: [영문폴더명]


### Claude에게 문서 검토 요청
아래 확인하고 피드백해줘: https://raw.githubusercontent.com/moongoby/project-docs/master/[폴더명]/CONTEXT.md


## 공통 템플릿 (common/)
- [CONTEXT 템플릿](https://raw.githubusercontent.com/moongoby/project-docs/master/common/CONTEXT_TEMPLATE.md)
- [Cursor Rules 템플릿](https://raw.githubusercontent.com/moongoby/project-docs/master/common/CURSORRULES_TEMPLATE.md)
- [인계서 템플릿](https://raw.githubusercontent.com/moongoby/project-docs/master/common/HANDOVER_TEMPLATE.md)
- [보고서 템플릿](https://raw.githubusercontent.com/moongoby/project-docs/master/common/REPORT_TEMPLATE.md)
- [Git 규칙](https://raw.githubusercontent.com/moongoby/project-docs/master/common/GIT_CONVENTION.md)
- [보안 규칙](https://raw.githubusercontent.com/moongoby/project-docs/master/common/SECURITY_RULES.md)
- [동기화 가이드](https://raw.githubusercontent.com/moongoby/project-docs/master/common/SYNC_GUIDE.md)

## 운영 규칙
- 작업 완료 → CONTEXT.md 갱신
- 대화 종료 → 인계서 작성
- 보고서 → project-docs/[폴더]/reports/에 발행
- .env, credentials, API키, 코드 → Public 저장소 포함 절대 금지
EOF

# ──────────────────────────────────────
# 2. CONTEXT 템플릿
# ──────────────────────────────────────
cat > common/CONTEXT_TEMPLATE.md << 'EOF'
# [프로젝트명] CONTEXT
> 최종 갱신: YYYY-MM-DD
> 관리자: moongoby

## 프로젝트 개요
- 목적:
- 서비스 유형: (B2C SaaS / B2B SaaS / 내부 도구 / 자동매매 등)
- 연관 프로젝트:

## 서버 환경
- 호스트명:
- IP:
- OS:
- 디스크: (전체/사용/여유/사용률)
- 프로젝트 경로:
- GitHub: (private repo URL)

## 기술 스택
- 언어:
- 프레임워크:
- DB:
- 기타:

## 완료 항목
- [ ]

## 진행 중
-

## 다음 작업 (우선순위)
1.
2.
3.

## 핵심 파일 경로
-

## 핵심 상수/설정
-
EOF

# ──────────────────────────────────────
# 3. Cursor Rules 템플릿
# ──────────────────────────────────────
cat > common/CURSORRULES_TEMPLATE.md << 'EOF'
# [프로젝트명] Cursor Rules
> 프로젝트:
> 서버:
> GitHub:
> 최종 갱신: YYYY-MM-DD

### 1. 프로젝트 구조
- 프로젝트 루트:
- 문서: docs/

### 2. 코딩 규칙
- Python: PEP8, type hints, docstrings 필수
- Shell: bash, set -euo pipefail
- 비밀정보: .env 파일에만 저장, git 포함 금지
- 로그: 표준 logging 모듈 사용

### 3. Git 규칙
- 커밋 메시지: [type] 설명
- type: feat, fix, docs, config, refactor, test, report, sync, context
- 작업 완료 후 반드시 push
- .gitignore 필수 항목: .env, __pycache__/, *.pyc, node_modules/, .next/cache/

### 4. 백업 규칙
- 변경 전 백업 경로: backups/YYYYMMDD_HHMMSS/

### 5. 컨텍스트 복원
- docs/CONTEXT.md를 모든 작업 완료 후 최신화
- 새 대화 시작 시 CONTEXT.md 내용을 첫 메시지로 전달

### 6. 인계서 규칙
- 대화 80% 시점 또는 종료 시 인계서 작성
- 경로: docs/handover/YYYYMMDD_주제.md

### 7. 보고서 발행
- 내부 보관: docs/reports/YYYYMMDD_작업명.md
- Claude 검토용 발행: project-docs/[폴더명]/reports/YYYYMMDD_HHmm_작업명.md
- 발행 후 git push → Claude에게 raw URL 전달

### 8. 문서 동기화
- 동기화 스크립트: bash /data/project-docs/scripts/sync_[폴더명].sh
- cursorrules 변경 시 project-docs에도 반영
EOF

# ──────────────────────────────────────
# 4. 인계서 템플릿
# ──────────────────────────────────────
cat > common/HANDOVER_TEMPLATE.md << 'EOF'
# 작업 인계서
> 작성일: YYYY-MM-DD HH:MM
> 프로젝트:
> 작업자: Claude + moongoby

## 이번 대화 주제
-

## 완료된 작업
1.
2.
3.

## 변경된 파일

| 파일 | 변경 내용 |
|------|----------|
|      |          |

## 주요 결정사항
-

## 다음 작업
1.
2.

## CONTEXT.md 갱신 여부
- [ ] 갱신 완료
- [ ] 갱신 필요 (사유:                )

## 참고
- 관련 커밋:
- 관련 문서:
EOF

# ──────────────────────────────────────
# 5. 보고서 템플릿
# ──────────────────────────────────────
cat > common/REPORT_TEMPLATE.md << 'EOF'
# 작업 보고서
> 작성일시: YYYY-MM-DD HH:MM
> 프로젝트:
> 작업자: Cursor / Claude
> 유형: feat / fix / config / refactor

## 작업 상태: 완료 / 부분완료 / 실패

## 작업 내용
-

## 변경된 파일

| 파일 | 변경 내용 |
|------|----------|
|      |          |

## 테스트 결과
-

## 커밋 정보
- 해시:
- 메시지:

## 다음 작업
-

## 비고
-
EOF

# ──────────────────────────────────────
# 6. Git 규칙
# ──────────────────────────────────────
cat > common/GIT_CONVENTION.md << 'EOF'
# Git 커밋/브랜치 규칙
> 모든 프로젝트 공통 적용

## 커밋 메시지 형식
[type] 간결한 설명 (한글 가능)


## type 목록
- **feat**: 새 기능
- **fix**: 버그 수정
- **docs**: 문서 변경
- **config**: 설정 변경 (.env, .cursorrules, docker 등)
- **refactor**: 리팩토링 (기능 변경 없음)
- **test**: 테스트 추가/수정
- **report**: 작업 보고서
- **sync**: 문서 동기화
- **context**: CONTEXT.md 갱신
- **handover**: 인계서 작성

## 브랜치 전략
- main/master: 운영 브랜치 (직접 push)
- feature/기능명: 대규모 기능 개발 시에만 분기

## 필수 .gitignore 항목
.env credentials/ pycache/ *.pyc node_modules/ .next/cache/ *.pack backups/ *.log


## push 규칙
- 모든 작업 완료 후 반드시 push
- 커밋 없이 퇴근/대화 종료 금지
EOF

# ──────────────────────────────────────
# 7. 보안 규칙
# ──────────────────────────────────────
cat > common/SECURITY_RULES.md << 'EOF'
# 보안 규칙
> 모든 프로젝트 공통 적용

## 절대 금지 항목 (Public 저장소)
- .env 파일
- API 키 / Secret Key
- DB 비밀번호
- OAuth credentials (client_secret.json 등)
- SSH 개인키
- 토큰 (GitHub PAT, YouTube OAuth token 등)
- 소스 코드 (Private 저장소에서만 관리)

## .env 관리
- 각 서버의 프로젝트 루트에 .env 파일로 관리
- .gitignore에 반드시 .env 포함
- 예시 파일(.env.example)은 값 없이 키만 기록하여 git 등록 가능

## SSH 키 관리
- moongoby 계정 등록 키 목록:
  - newtalk (114서버)
  - GitHub CLI (114서버)
  - GO100-server (GO100 서버)
- 키 추가/삭제 시 https://github.com/settings/keys 에서 관리

## Public 저장소(project-docs) 등록 전 체크리스트
- [ ] .env, credentials 포함 여부 확인
- [ ] API 키/토큰 하드코딩 여부 확인
- [ ] 소스 코드 포함 여부 확인
- [ ] 개인정보 포함 여부 확인
- [ ] `git diff --cached` 로 커밋 내용 최종 확인
EOF

# ──────────────────────────────────────
# 8. 동기화 가이드
# ──────────────────────────────────────
cat > common/SYNC_GUIDE.md << 'EOF'
# 문서 동기화 가이드
> 각 프로젝트 서버 → project-docs Public 저장소 동기화 방법

## 동기화 대상
- CONTEXT.md
- cursorrules (원본 .cursorrules → 사본 cursorrules.md)
- 최신 인계서 3개
- 보고서

## 동기화 스크립트 작성 규칙

### 로컬 서버 (114서버 등 git 직접 접근 가능)
```bash
#!/bin/bash
SRC="/프로젝트/docs"
DST="/data/project-docs/[폴더명]"
cp ${SRC}/CONTEXT.md ${DST}/
cp /프로젝트/.cursorrules ${DST}/cursorrules.md
ls -t ${SRC}/handover/2*.md 2>/dev/null | head -3 | while read f; do cp "$f" ${DST}/handover/; done
cd /data/project-docs && git add -A
git diff --cached --quiet || { git commit -m "[sync] [폴더명] $(date +%Y%m%d_%H%M)"; git push origin master; }
```

### 원격 서버 (NAS 등 SSH 접근)
```bash
#!/bin/bash
NAS_HOST="admin@192.168.30.23"
NAS_PORT="2222"
NAS_SRC="/프로젝트경로/docs"
DST="/data/project-docs/[폴더명]"
scp -P ${NAS_PORT} ${NAS_HOST}:${NAS_SRC}/CONTEXT.md ${DST}/
scp -P ${NAS_PORT} ${NAS_HOST}:/프로젝트경로/.cursorrules ${DST}/cursorrules.md
cd /data/project-docs && git add -A
git diff --cached --quiet || { git commit -m "[sync] [폴더명] $(date +%Y%m%d_%H%M)"; git push origin master; }
```

## 동기화 실행 시점
- CONTEXT.md 변경 시
- cursorrules 변경 시
- 대화 종료 시 (인계서 작성 후)
- 보고서 발행 시

## 등록된 동기화 스크립트
| 프로젝트 | 서버 | 스크립트 |
|----------|------|----------|
| ShortFlow | 114서버 | /data/project-docs/scripts/sync_shortflow.sh |
| GO100 | GO100서버 | /root/project-docs/scripts/sync_go100.sh |
| NAS Image | 114서버(원격) | /data/project-docs/scripts/sync_nas_image.sh |
EOF

# ──────────────────────────────────────
# 9. 신규 프로젝트 자동 생성 스크립트
# ──────────────────────────────────────
cat > scripts/new_project.sh << 'SCRIPT_EOF'
#!/bin/bash
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "사용법: bash scripts/new_project.sh [폴더명] [프로젝트 설명]"
  echo "예시: bash scripts/new_project.sh my-app '내 앱 프로젝트'"
  exit 1
fi

FOLDER=$1
DESC=$2
BASE="/data/project-docs"

echo "=== ${FOLDER} 프로젝트 문서 구조 생성 ==="

mkdir -p ${BASE}/${FOLDER}/handover
mkdir -p ${BASE}/${FOLDER}/reports

cp ${BASE}/common/CONTEXT_TEMPLATE.md ${BASE}/${FOLDER}/CONTEXT.md
cp ${BASE}/common/CURSORRULES_TEMPLATE.md ${BASE}/${FOLDER}/cursorrules.md
cp ${BASE}/common/HANDOVER_TEMPLATE.md ${BASE}/${FOLDER}/handover/
cp ${BASE}/common/REPORT_TEMPLATE.md ${BASE}/${FOLDER}/reports/

echo "=== README.md에 행 추가 ==="
echo "| ${FOLDER} | ${DESC} | (서버미정) | [CONTEXT](./${FOLDER}/CONTEXT.md) | Rules |" >> ${BASE}/README.md

echo "=== Git 커밋 & push ==="
cd ${BASE}
git add -A
git commit -m "[init] ${FOLDER} 프로젝트 문서 구조 생성" || true
git push origin master || true

echo ""
echo "✅ 완료!"
echo "CONTEXT URL: https://raw.githubusercontent.com/moongoby/project-docs/master/${FOLDER}/CONTEXT.md"
echo "Rules URL: https://raw.githubusercontent.com/moongoby/project-docs/master/${FOLDER}/cursorrules.md"
echo ""
echo "다음 단계: CONTEXT.md와 cursorrules.md 내용을 프로젝트에 맞게 수정하세요."
SCRIPT_EOF
chmod +x scripts/new_project.sh

# ──────────────────────────────────────
# 10. README.md (덮어쓰기)
# ──────────────────────────────────────
cat > README.md << 'README_EOF'
# 프로젝트 문서 허브
관리자: moongoby | 최종 갱신: 2026-02-23

## 등록 프로젝트
| 프로젝트 | 설명 | 서버 | CONTEXT | Cursor Rules |
|----------|------|------|---------|--------------|
| shortflow | ShortFlow v3.0 + StyleFlow v1.0 | 114서버 | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/cursorrules.md) |
| go100 | GO100 자동매매 | kis-autotrade-v4 | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/go100/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/go100/cursorrules.md) |
| nas-image | NAS 이미지 자동화 | Synology NAS | [CONTEXT](https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/CONTEXT.md) | [Rules](https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/cursorrules.md) |

## 공통 문서 (common/)
| 문서 | 용도 | URL |
|------|------|-----|
| CONTEXT 템플릿 | 새 프로젝트 CONTEXT 작성 | [raw](https://raw.githubusercontent.com/moongoby/project-docs/master/common/CONTEXT_TEMPLATE.md) |
| Cursor Rules 템플릿 | 새 프로젝트 .cursorrules 작성 | [raw](https://raw.githubusercontent.com/moongoby/project-docs/master/common/CURSORRULES_TEMPLATE.md) |
| 인계서 템플릿 | 대화 종료 시 인계서 | [raw](https://raw.githubusercontent.com/moongoby/project-docs/master/common/HANDOVER_TEMPLATE.md) |
| 보고서 템플릿 | 작업 완료 보고서 | [raw](https://raw.githubusercontent.com/moongoby/project-docs/master/common/REPORT_TEMPLATE.md) |
| Git 규칙 | 커밋/브랜치 규칙 | [raw](https://raw.githubusercontent.com/moongoby/project-docs/master/common/GIT_CONVENTION.md) |
| 보안 규칙 | .env, 키, 코드 관리 | [raw](https://raw.githubusercontent.com/moongoby/project-docs/master/common/SECURITY_RULES.md) |
| 동기화 가이드 | 서버→GitHub 동기화 방법 | [raw](https://raw.githubusercontent.com/moongoby/project-docs/master/common/SYNC_GUIDE.md) |

## Claude 새 대화 시작법
아래 온보딩 문서를 읽고 작업을 이어가줘:
https://raw.githubusercontent.com/moongoby/project-docs/master/ONBOARDING.md
프로젝트: [프로젝트명], 폴더: [폴더명]

## 신규 프로젝트 추가 (114 서버)
```bash
bash /data/project-docs/scripts/new_project.sh [폴더명] '[설명]'
```

## 규칙
- 코드, .env, credentials, API키 절대 포함 금지
- 기획서, 아키텍처, CONTEXT, 인계서, cursorrules, 보고서만 관리
- cursorrules.md는 검토용 사본 (원본은 각 프로젝트 .cursorrules)
README_EOF

# ──────────────────────────────────────
# 11. Git 커밋 & push
# ──────────────────────────────────────
git add -A
git status
if git diff --cached --quiet; then
  echo "변경 사항 없음, 커밋 생략."
else
  git commit -m "[config] 공통 문서 체계 구축: ONBOARDING, 7개 공통 템플릿, 신규 프로젝트 스크립트, README 전면 갱신"
  git push origin master || echo "push 실패 시 수동으로: cd /data/project-docs && git push origin master"
fi

# ──────────────────────────────────────
# 12. 검증
# ──────────────────────────────────────
echo ""
echo "=== 파일 구조 ==="
find /data/project-docs -type f \( -name "*.md" -o -name "*.sh" \) | grep -v .git | sort
echo ""
echo "=== 최근 커밋 ==="
git log --oneline -5
