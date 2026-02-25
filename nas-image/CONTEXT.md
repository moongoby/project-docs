# NAS 이미지 자동화 프로젝트 CONTEXT
> 최종 갱신: 2026-02-25
> 관리자: moongoby
> GitHub Private: https://github.com/moongoby/newtalk-image-auto

## 프로젝트 개요
패션 이커머스(뉴톡) 제품컷·모델컷 이미지 자동 보정/배경제거/리사이즈/114서버 동기화 시스템.
NAS Docker 기반. 현재 수동 12단계 → 자동화 후 촬영→QC승인→자동등록 으로 단축 목표.

## 서버 환경
- NAS: Synology DS1821+ (AMD Ryzen V1500B 4-core, 8GB RAM, DSM 7.2.1)
- IP: 사설 192.168.30.23, 공인 183.96.69.193, SSH 포트 2222, 사용자 newtalk
- Docker 24.0.2, 컨테이너 newtalk-image-auto (Python 3.11, FastAPI, port 8100)
- 프로젝트 경로: /volume1/뉴톡/newtalk-image-auto (Windows SMB: Z:\)
- 원본: /volume1/★제품사진/ (rw, P1 폴더생성 mkdir용), 결과: /volume1/★제품사진/_processed/ (rw)
- 114서버: 114.207.244.86:7916, 동기화 계정 nasync (SSH 키), 이미지 경로 /home/danharoo/www/data/files/goods/goodscode/img/{소문자코드}/
- 116서버: PHP 어드민

## 기술 스택
Python 3.11, FastAPI, OpenCV, Pillow, pillow-heif, numpy, mediapipe <0.10.31, SQLite+aiosqlite, Jinja2, Docker, rsync over SSH

## Phase 진행률
- Phase 1 (기본 이미지 처리): 100%
- Phase 2 (톤 매칭 + QC UI): 85%
- Phase 3 (배너/GIF/상세페이지): 미착수
- Phase 4 (어드민 연동/DB 자동화): 미착수

## 완료 항목
- Docker 컨테이너 + 볼륨 마운트
- PhotoRoom API + rembg 폴백 배경제거
- 모델컷 보정 v2 (노출/CLAHE/언샤프)
- 폴더 파싱, 파일명 매핑 (114 규칙)
- 리사이즈 (1200/600/300px)
- 배치 API + 워커 파이프라인
- NAS→114 rsync 인프라 (nasync, SSH 키)
- E2E 전송 테스트 검증
- AI 크랍 MediaPipe Pose (전신/상반신/반신)
- QC UI 비교 슬라이더
- 톤 매칭 엔진 + 프리셋 CRUD + 기본 프리셋 3종
- 프리셋 UI (목록/등록/미리보기/3장 비교)
- 폴더 자동 분류 (EXIF 시간 기반)
- Dockerfile SSH/rsync 추가
- GitHub 연동, Windows PC SSH 키 인증
- DB 스키마 문서화 (docs/DATABASE.md)
- **NAS 폴더 자동생성 폴링 워커 (P1)** — **완료 (통합 테스트 통과)** — 116 DB nas_folder_request 폴링, mkdir, API /folder/requests

## 최근 완료 (2026-02-25 P1 폴더생성)
- **P1 통합 테스트 완료** — 2026-02-25 18:55 KST NAS 실행: shooting_id=662·폴더폴링 17초·NAS 폴더·API completed·PyMySQL 1.4.6·Docker·pick.newtalk.kr 정상 (§7.5 보고서)
- **P1 모델사진폴더 NAS 직접생성 (FEATURE-001)**
  - requirements.txt에 PyMySQL 추가, config/.env.example에 116 DB 설정 (NEWTALK_DB_*)
  - app/workers/folder_poller.py: nas_folder_request 폴링, 상위/하위 폴더명 조합, mkdir만 수행
  - docker-compose: /data/photos ro → rw, main.py에 1분 간격 폴더 폴러 등록
  - docs/DATABASE.md §8: nas_folder_request 테이블 설계 및 생성 SQL
  - tests/test_folder_poller.py 7건 추가, 전체 96 passed 4 skipped 1 fail(기존 DB 미초기화)
- **P1 통합 테스트 스크립트** — `scripts/nas_p1_integration_test.sh` (STEP 0~11), 보고서 §7.5 STEP별 결과 표
- **P1 선행: NAS → 114서버(116 DB) MySQL 접속 테스트** (스크립트·보고서 템플릿)

## 이전 완료 (2026-02-23 소스 검수 개선)
- 톤 매칭 v2: 적응형 강도 차원별 정규화 가중치, AB채널 보호 비율 파라미터화, 피부 HSV config화, WB 배경 제외 옵션
- 배치 파이프라인: PipelineConfig/PipelineResult dataclass, run_pipeline(config) 시그니처, HEIC 변환 유틸 분리
- 자동 보정: CorrectionConfig dataclass로 파라미터 외부화
- AI 크랍: FALLBACK_RATIOS 상수화, 종횡비 검증 경고, model_complexity=1 주석
- 배경 제거: 반환값에 fallback_used 추가, API키 미설정 시 rembg 직접 사용 로그
- 파일명 매퍼: EXCLUDE_SUFFIXES config화, 15장 초과 경고
- rsync_114: sync_goods 재시도 로직 (max_retries, retry_delay, retry_count)

## 바로 다음 할 일
1. **[P3]** Gemini A-cut 선택 실험 (다음 단계)
2. **[P1]** 모델사진폴더 NAS 직접 생성 — **완료 (통합 테스트 통과, 2026-02-25 18:55 KST)**
3. Docker 테스트 전체 통과 확인 (httpx 추가 후 재빌드)
4. 실사진으로 톤 매칭/보정 검증

## 주의사항
- mediapipe <0.10.31 고정 (solutions API 제거 이슈)
- PhotoRoom 크레딧 소진, 제품컷은 아이폰 앱 병행
- NAS 하드웨어 제한: model_complexity=1
- 114 danharoo 계정 SFTP만, nasync 계정 사용
- SQLite 동시성: Phase 3-4에서 WAL 또는 PostgreSQL 검토

## 테스트 현황 (96 passed, 4 skipped, 1 fail DB미초기화)
- test_folder_poller: 7p / test_filename_mapper: 7p / test_image_resize: 5p 1s / test_batch_pipeline: 4p 1f 1s / test_batch_pipeline_v2: 4p
- test_e2e_pipeline: 2p 1s / test_auto_crop: 8p / test_qc_ui: 8p
- test_tone_matcher: 12p / test_tone_matcher_v2: 4p / test_wb_adaptive: 12p
- test_auto_corrector_v2: 3p / test_auto_classify: 8p
- test_batch_api_folder_path_returns_job_id: DB 미초기화 시 fail (lifespan 필요)

## 비용
PhotoRoom API Basic $20/월 (1,000장, 초과 $0.02/장) - 결제 보류

## 참조 문서
- 현재 상태: docs/CONTEXT.md
- 변경 이력: docs/CHANGELOG.md
- 기획: docs/PLANNING.md
- **전체 파이프라인**: docs/PIPELINE_PROCESS.md
- 아키텍처: docs/ARCHITECTURE.md
- 인수인계: docs/HANDOVER.md

## 로드맵
- 2월 4주차: Work C/D, Docker 빌드, Phase 2 완료, P1 착수
- 3월 초중: 실사진 테스트, Phase 3 (P3 A컷 선별, P4 배너/인트로 자동생성)
- 4월: Phase 4 (P5 114 DB 자동 업데이트, P6 상세페이지 자동 정렬)
