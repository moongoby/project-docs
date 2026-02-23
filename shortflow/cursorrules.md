# ShortFlow + StyleFlow Project Context for Cursor AI

## Project Overview
This repository contains two SaaS products sharing the same infrastructure:
1. **ShortFlow v3.0** (B2C) – AI YouTube Shorts automation for Coupang Partners affiliates
2. **StyleFlow v1.0** (B2B) – Shopping mall video-to-reel automation for SNS

## Server
- Host: rfree-0009, IP: 114.207.244.86
- Project: /data/shortflow, Data: /data/styleflow
- NAS: Synology 192.168.30.23 (public 183.96.69.193, SSH port 2222)

## Tech Stack
- Backend: FastAPI (Python 3.11), Supabase (PostgreSQL + Auth + RLS)
- Frontend: Next.js 14 + Tailwind CSS
- Video: FFmpeg 4.2.7, ffmpeg-python
- AI: Claude Opus 4.6 / GPT-4o (scripts), ElevenLabs / Google Cloud TTS / Edge-TTS
- Infra: Docker Compose (worker, n8n, api, dashboard, redis)
- Legacy DB: MySQL autoda (77,109 goods records)

## Key Architecture
- 10-Layer Anti-Inauthentic Engine (core differentiator)
- 2-Track pipeline: Track A (ai_generate), Track B (edit_source / NAS ingestion)
- Multi-tenant Supabase with RLS per tenant_id
- YouTube Data API v3 (OAuth 2.0, 10k units/day, user-scoped tokens)

## Coding Rules
- Python: PEP 8, type hints, docstrings
- All DB queries via Supabase client (no raw SQL in app code)
- Environment variables in .env (never hardcode secrets)
- Logging to /data/styleflow/logs/
- Error handling: max 3 retries, 30s backoff, dead-letter queue

## File Roles
- engine/*.py – Core processing modules (video editing, AI, TTS, anti-inauthentic)
- worker/pipeline_worker.py – Main job processor
- api/main.py + routers/ – FastAPI endpoints
- dashboard/ – Next.js frontend
- templates/ – Visual components, script archetypes, structural patterns
- scripts/ – Batch execution, auth setup, schedulers
- credentials/ – OAuth tokens, API keys (git-ignored)

## Database Tables
- Supabase: tenants, channels, products, jobs, analytics (ShortFlow)
- Supabase: sf_tenants, sf_brands, sf_channels, sf_videos, sf_upload_schedule (StyleFlow)
- MySQL autoda: goods, cody_msg, cody_product_msg (legacy, read-only)

## Important Constants
- ORIGINALITY_THRESHOLD=70 (auto-upload cutoff)
- CROSS_VIDEO_SIMILARITY_THRESHOLD=0.85
- UPLOAD_OFFSET_MINUTES=30
- YOUTUBE_DAILY_LIMIT=6 (10,000 units / 1,600 per upload)
- Video output: 1080x1920, H.264 High, AAC 44.1kHz, 29.97fps

---

## Work Rules (필수 준수)

### 1. 백업 규칙

- 파일 수정 전 반드시 백업본 생성
  - 위치: `/data/shortflow/backups/YYYYMMDD_HHMMSS/`
  - 명령: `cp -a <원본파일> /data/shortflow/backups/$(date +%Y%m%d_%H%M%S)/`
- 백업 디렉토리가 없으면 자동 생성: `mkdir -p /data/shortflow/backups/$(date +%Y%m%d_%H%M%S)/`
- 백업 대상: 수정 또는 삭제되는 모든 파일 (신규 생성 파일은 제외)
- 백업 보존: 최근 7일, 7일 초과분은 수동 정리

### 2. 보고서 규칙

- 모든 작업 완료 후 작업 보고서를 생성한다
  - 위치: `/data/shortflow/docs/reports/YYYYMMDD_작업명.md`
  - 디렉토리 없으면 자동 생성: `mkdir -p /data/shortflow/docs/reports/`
- 보고서 필수 항목:
  ```
  # 작업 보고서: [작업명]
  
  **작성일시:** YYYY-MM-DD HH:MM
  **작업 유형:** [신규 개발 / 버그 수정 / 설정 변경 / 리팩토링]
  **상태:** [완료 / 진행중 / 실패]
  **관련 파일:** [변경된 파일 목록]
  
  ## 1. 작업 개요
  [무엇을 왜 했는지]
  
  ## 2. 변경 사항
  [파일별 변경 내용 상세]
  
  ## 3. 테스트 결과
  [실행 명령, 출력 결과, 성공/실패]
  
  ## 4. 주의사항 / 후속 작업
  [다음에 해야 할 것, 주의할 점]
  ```

### 3. Git 커밋 규칙

- 기능 단위로 커밋한다 (파일 1개 변경이라도 의미 있는 단위면 커밋)
- 커밋 메시지 형식:
  ```
  [타입] 간결한 설명 (한국어)
  
  - 상세 변경 내용 1
  - 상세 변경 내용 2
  ```
- 타입 종류:
  - `[feat]` 새 기능
  - `[fix]` 버그 수정
  - `[refactor]` 리팩토링
  - `[docs]` 문서
  - `[config]` 설정 변경
  - `[test]` 테스트
- 커밋 전 확인:
  ```bash
  cd /data/shortflow
  git add -A
  git status   # 변경 파일 확인
  git diff --cached --stat   # 추가된 내용 확인
  git commit -m "[타입] 설명"
  ```
- git 초기화가 안 되어 있으면 먼저 실행:
  ```bash
  cd /data/shortflow
  git init
  git add -A
  git commit -m "[config] 프로젝트 초기 커밋"
  ```

### 4. .gitignore 규칙

- `/data/shortflow/.gitignore`에 아래 항목이 반드시 포함되어야 한다:
  ```
  .env
  credentials/
  *.pyc
  __pycache__/
  backups/
  /data/styleflow/raw/
  /data/styleflow/output/
  /data/styleflow/logs/
  *.log
  node_modules/
  .next/
  ```

### 5. 배포/실행 규칙

- Docker 컨테이너 관련 변경 시:
  ```bash
  cd /data/shortflow
  docker-compose down
  docker-compose up -d
  docker-compose ps   # 상태 확인
  docker-compose logs --tail=20   # 로그 확인
  ```
- Python 스크립트 단독 테스트 시:
  ```bash
  cd /data/shortflow
  python3 -c "from engine.모듈명 import 클래스명; print('import OK')"
  ```
- 배포 후 반드시 동작 확인하고, 실패 시 백업에서 즉시 롤백

### 6. 디스크 주의사항

- 루트 디스크(/)에 대용량 파일 생성 금지
- `/data/shortflow`, `/data/styleflow`는 서브 디스크(goodscode 11TB) 심볼릭 링크
- 대용량 데이터(영상, 이미지, 로그)는 반드시 `/data/styleflow/` 하위에 저장
- 작업 전 디스크 여유 확인: `df -h / && df -h /data/shortflow`

### 7. 작업 흐름 요약

모든 작업은 아래 순서를 따른다:

1. `df -h /` 디스크 확인
2. 수정 대상 파일 백업
3. 코드 작성/수정
4. 테스트 실행 및 결과 확인
5. git add + commit
6. 필요 시 docker-compose 재시작
7. 동작 확인
8. 작업 보고서 작성

### 8. GitHub 규칙

- 저장소: git@github.com:moongoby/shortflow.git (private)
- 모든 커밋 후 반드시 push:
  ```bash
  git push origin main
  ```
- 문서 변경 시 커밋 메시지: `[docs] 변경 설명`
- 코드 변경 시 커밋 메시지: `[feat/fix/refactor] 변경 설명`
- push 실패 시 원인 확인 후 재시도, 3회 실패 시 보고서 작성
- 대용량 파일(영상, 이미지, 로그)은 .gitignore에 의해 제외됨을 확인

### 9. 컨텍스트 복원 규칙
- 모든 작업 완료 후 반드시 `docs/CONTEXT.md`를 최신 상태로 갱신
- 갱신 항목: 완료 목록, 진행 중 항목, 다음 작업, 변경 파일, 핵심 결정사항
- CONTEXT.md는 3000자 이내 요약 유지 (토큰 절약)
- 커밋 메시지: `[context] 컨텍스트 파일 갱신`

### 10. 대화 인계 규칙
- 대화 종료 시 `docs/handover/` 에 `YYYYMMDD_HHmm_인계서.md` 작성
- 템플릿: `docs/handover/HANDOVER_TEMPLATE.md` 사용
- 인계서에는 "이번 대화 변경분"만 기록 (전체 상태는 CONTEXT.md 참조)
- 새 대화 시작 시 아래 두 파일을 첫 메시지로 전달:
  1. `cat /data/shortflow/docs/CONTEXT.md`
  2. 직전 인계서 내용
- 커밋 메시지: `[handover] 대화 인계서 작성`

### 12. 작업 보고서 자동 발행 규칙
- 작업 완료 시 보고서를 Public 저장소에 발행
- 경로: /data/project-docs/shortflow/reports/YYYYMMDD_HHmm_작업명.md
- 발행 절차:
  1. 보고서 작성 (REPORT_TEMPLATE.md 사용)
  2. /data/project-docs/shortflow/reports/ 에 저장
  3. CONTEXT.md 갱신
  4. project-docs에 커밋 + push:
     cd /data/project-docs && git add -A
     git commit -m "[report] shortflow: 작업명"
     git push origin master
- 보고서 필수 항목:
  1. 작업일시
  2. 작업 유형 (feat/fix/refactor/config)
  3. 완료 상태 (성공/부분완료/실패)
  4. 변경된 파일 목록
  5. 작업 내용 요약
  6. 테스트 결과
  7. 다음 작업
- Claude 확인 URL: https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/reports/파일명.md
- CONTEXT.md도 함께 갱신하여 push
