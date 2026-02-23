# 뉴톡 이미지 자동화 시스템 인수인계서
**문서 버전**: 2.0
**최종 수정일**: 2026-02-23
**Public 열람**: https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/HANDOVER.md

## 1. 작업 규칙 (필수 준수)

### 1.1 보고 규칙
- 보고 대상: 대표님 (CEO) 1인
- 보고 형식: 한국어, 간결 명확
- "진행하라" 지시 시: 즉시 Cursor 지시문 생성
- 병렬 작업 가능 시: 동시에 여러 Cursor 지시문 제공
- 토큰 80% 도달 시: 문서 업데이트 후 새 대화 안내

### 1.2 Cursor 필수 규칙
- 새 모듈 → tests/ 대응 테스트 필수
- 기존 모듈 수정 → 기존 테스트 유지 확인
- 작업 완료 → pytest 결과 포함 보고
- .env 절대 Git 포함 금지
- requirements.txt 변경 시 명시
- 작업 완료 시 docs/CONTEXT.md + docs/CHANGELOG.md 업데이트
- git commit + git push 실행
- docs/ 에 작업결과 보고서 md 생성

### 1.3 서버 작업 분담
- NAS 터미널 (Docker build, SSH 테스트): 대표님 직접
- 114서버: Cursor SSH 실행
- 코드 작성/수정: Cursor
- PhotoRoom 결제 등 외부 서비스: 대표님

### 1.4 문서 버전관리
- NAS Private: github.com/moongoby/newtalk-image-auto (docs/)
- Public 열람: github.com/moongoby/project-docs (nas-image/)
- 동기화: NAS docs/ → project-docs/nas-image/ 복사 후 push

## 2. 프로젝트 현황

### 2.1 Phase 1 – 기본 이미지 처리 (100%)
Docker, PhotoRoom+rembg, 모델컷 보정 v2, 폴더 파싱, 파일명 매핑, 리사이즈, 배치 API, rsync 인프라, E2E 전송

### 2.2 Phase 2 – 톤 매칭 + QC UI (85%)
완료: AI 크랍, QC UI 슬라이더, 톤 매칭+프리셋 CRUD, 프리셋 UI, 폴더 자동 분류, Dockerfile SSH/rsync
미착수: Work C (피부톤 보호+배경 분리), Work D (적응형 강도+WB 정규화), NAS Docker 빌드

## 3. 즉시 진행할 작업

### 3.1 Work C – 피부톤 보호 + 배경 분리
파일: app/workers/tone_matcher.py
- detect_skin_mask: HSV H 0-50, S 40-200, V 80-255
- detect_person_mask: MediaPipe Pose BBox + 15% 마진
- match_tone_advanced: 의류 기본, 피부 30%, 배경 L50%+AB0%
- 테스트: tests/test_tone_advanced.py (10 cases)

### 3.2 Work D – 적응형 강도 v2 + 화이트밸런스
파일: app/workers/tone_matcher.py
- _adaptive_strength_v2: L/색온도/채도/L-std 거리 가중합
- WhiteBalanceNormalizer: LAB B채널 기반 색온도 추정
- 테스트: tests/test_wb_adaptive.py (12 cases)

### 3.3 NAS Docker 빌드 (대표님 실행)
```bash
ssh -p 2222 newtalk@192.168.30.23
cd /volume1/뉴톡/newtalk-image-auto
sudo docker-compose build
sudo docker-compose up -d
sudo docker exec newtalk-image-auto python -m pytest tests/ -v --tb=short
```

## 4. 접속 정보
- NAS SSH: ssh -p 2222 newtalk@192.168.30.23
- NAS DSM: http://192.168.30.23:5000
- Docker API: http://192.168.30.23:8100
- QC UI: http://192.168.30.23:8100/qc
- 114 서버: ssh -p 7916 -i ~/.ssh/id_ed25519 nasync@114.207.244.86
- GitHub Private: https://github.com/moongoby/newtalk-image-auto
- GitHub Public docs: https://github.com/moongoby/project-docs/tree/master/nas-image

## 5. 테스트 현황 (68 passed, 8 skipped)
test_filename_mapper 7p, test_image_resize 5p 1s, test_batch_pipeline 18p 3s, test_e2e_pipeline 2p 1s, test_auto_crop 8p, test_qc_ui 8p, test_tone_matcher 12p, test_auto_classify 8p

## 6. 알려진 이슈
- PhotoRoom 크레딧 소진, 결제 보류
- mediapipe <0.10.31 고정
- NAS 하드웨어 제한 (model_complexity=1)
- 114 danharoo SFTP만, nasync 사용
- SQLite 동시성 Phase 3-4 검토

## 7. 새 대화 시작 방법
Claude에게:
> "아래 문서를 읽고 현재 상태를 파악한 후 이어서 작업하라"
> https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/CONTEXT.md
