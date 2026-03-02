# 뉴톡 이미지 자동화 시스템 아키텍처
**문서 버전**: 2.0
**최종 수정일**: 2026-02-23
**Public 열람**: https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/ARCHITECTURE.md

## 1. 시스템 구성도

```
[아이폰 촬영] → [NAS DS1821+] → [Docker: newtalk-image-auto]
                    │                      │
                    │ SMB (Z:)             ├─ FastAPI (port 8100)
                    │                      ├─ 이미지 처리 워커
                    ▼                      ├─ QC UI (웹)
              [Windows PC]                 ├─ SQLite DB
              [Cursor IDE]                 └─ rsync sync
                                                │
                    ┌───────────────────────────┘
                    ▼
              [114 서버]          [116 서버]
              이미지 CDN/DB       PHP 어드민
              cafe24 호스팅       뉴톡 관리자
```

## 2. 서버 정보

### 2.1 NAS (이미지 처리 서버)
- 하드웨어: Synology DS1821+, AMD Ryzen V1500B 4-core, 8GB RAM
- OS: DSM 7.2.1
- IP: 사설 [NAS-IP], 공인 [NAS-PUBLIC-IP]
- SSH: 포트 [NAS-SSH-PORT], 사용자 newtalk
- Docker: 24.0.2
- 컨테이너: newtalk-image-auto (Python 3.11, FastAPI, uvicorn, 포트 8100)

### 2.2 114 서버 (이미지 CDN/DB)
- 호스팅: cafe24, IP [SERVER-IP], SSH 포트 7916
- 디스크: /dev/sdb1 (11TB, 4.7TB 사용, 5.7TB 가용)
- 이미지 경로: /home/danharoo/www/data/files/goods/goodscode/img/{소문자상품코드}/
- CDN: https://cdn.newtalk.kr/data/files/goods/goodscode/img/{GoodsCode}/{파일명}
- DB: goods_detail (GoodsEtc60~74, GoodsSortImg1~4), goods_image (~76,892건)
- 동기화 계정: nasync (uid 1008, SSH 키 인증, danharoo 그룹)
- danharoo 계정은 sftp_users → SFTP만 가능

### 2.3 116 서버 (PHP 어드민)
- 뉴톡 관리자 시스템
- 설정: upload_serve_domain = https://www.newtalk.kr
- 업로드 코드: application/controllers/products.php, application/libraries/Upload_handler.php

## 3. Docker 구성

### 3.1 docker-compose.yml 볼륨
- /volume1/★제품사진/ → /data/photos/ (ro)
- /volume1/★제품사진/_processed/ → /data/processed/ (rw)
- ./data/db → /app/data/db
- ./data/logs → /app/data/logs
- ~/.ssh/id_ed25519 → /root/.ssh/id_ed25519 (ro)
- ~/.ssh/known_hosts → /root/.ssh/known_hosts (ro)

### 3.2 Dockerfile 패키지
Python 3.11, FastAPI, uvicorn, OpenCV, Pillow, pillow-heif, numpy, mediapipe <0.10.31, SQLite+aiosqlite, Jinja2, aiofiles, openssh-client, rsync

### 3.3 환경변수 (.env)
PHOTOS_ROOT, PROCESSED_ROOT, PHOTOROOM_API_KEY, DB_DIR, LOG_DIR, SYNC_114_ENABLED, SYNC_114_USER, SYNC_114_HOST, SYNC_114_PORT, SYNC_114_SSH_KEY, SYNC_114_REMOTE_BASE

## 4. 모듈 구조

```
app/
├── main.py, config.py
├── api/ (routes.py, qc_routes.py)
├── workers/ (bg_remover, auto_corrector, auto_crop, tone_matcher, auto_classify, batch_pipeline)
├── parsers/ (folder_parser)
├── queue/ (job_manager – SQLite)
├── utils/ (image_utils, filename_mapper)
├── sync/ (rsync_114)
├── qc/ (image_resolver)
├── templates/ (qc_list, qc_detail, preset_list, preset_register, classify)
├── static/ (css/, js/)
tests/ (68 passed, 8 skipped)
docs/ (PLANNING, ARCHITECTURE, HANDOVER, CONTEXT, CHANGELOG)
```

## 5. API 엔드포인트

### 이미지 처리
GET /api/health, POST /api/process, POST /api/process/batch, GET /api/status/{job_id}, GET /api/sessions

### QC
POST /api/approve/{job_id}, POST /api/reject/{job_id}, GET /qc, GET /qc/{goods_code}, GET /qc/image/*

### 프리셋
POST /api/preset/register, GET /api/preset/list, GET/PUT/DELETE /api/preset/{id}

### 분류
POST /api/classify, POST /api/classify/reclassify, POST /api/classify/confirm

## 6. 데이터 흐름

```
[NAS /volume1/★제품사진/] → Docker (/data/photos/ ro)
  → folder_parser → auto_classify (EXIF)
  → batch_pipeline:
      모델컷: [WB] → [톤 매칭] → [노출/CLAHE/언샤프] → [AI 크랍]
      제품컷: [PhotoRoom/rembg] → [PNG→JPEG] → [썸네일]
  → resize (1200/600/300)
  → filename_mapper (114 규칙)
  → /data/processed/{goods_code}/114/
  → rsync → 114서버 goodscode/img/{code}/
```

## 7. 114 서버 파일명 규칙
- 제품컷: {code}_01.jpg ~ _15.jpg
- 모델컷: {code}-s_1.jpg ~
- 리사이즈: {code}-600_1.jpg, {code}-300_1.jpg
- 썸네일: thumbnail/ 하위
- 상품코드 소문자 변환 필수

## 8. 네트워크 및 보안
- NAS SSH: newtalk@[NAS-IP]:[NAS-SSH-PORT] (키 인증)
- NAS→114: nasync@[SERVER-IP]:7916 (키 인증, cafe24 방화벽 NAS IP 허용)
- Docker API: localhost:8100 (내부 전용)
- PhotoRoom: x-api-key 헤더
- .env: .gitignore 제외
- 원본 볼륨: 읽기전용
