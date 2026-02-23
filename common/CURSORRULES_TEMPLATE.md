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
