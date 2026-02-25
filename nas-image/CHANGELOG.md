# 변경 이력

## 2026-02-25
- **P1 통합 테스트 완료 (NAS)**
  - 2026-02-25 18:55 KST 기준: DB INSERT(shooting_id=662)·폴더폴링 pending→completed(17초)·NAS 폴더 생성·API completed·PyMySQL 1.4.6·Docker·pick.newtalk.kr 정상
  - 보고서 §7.5: docs/reports/CUR-NASIMG-FEATURE-001-20260225.md 최종 결과 표 및 커밋(114: 1dd059f/8e71d73, NAS: ca064ae/f8bf7be) 기입
- **DB 비밀번호 이슈 해결 (NAS 배포)**
  - NAS .env에 MYSQL_PASSWORD 미설정 시 폴더 폴링 스킵. 116서버 database.php 기준 비밀번호 설정 후 정상 동작 (비밀번호 값은 문서/코드에 미기재)
- **116 서버 shooting_id 선택자 버그 수정**
  - 어드민 NAS 폴더 요청 시 shooting_id가 올바르게 전달되도록 수정 반영 (114 Cursor와 협의)
- **P1 통합 테스트 실행 (NAS 작업지시서)**
  - 스크립트: `scripts/nas_p1_integration_test.sh` (STEP 0~11: .env 확인, git pull, Docker 재빌드, 사전확인, DB 테이블, INSERT, 폴링 대기, 결과 확인, 정리, pytest, 보고 안내)
  - 보고서 §7.5: STEP별 통합 테스트 결과 표 보강 (docs/reports/CUR-NASIMG-FEATURE-001-20260225.md)
  - 통합 테스트 성공 시: DB INSERT → 폴링 → status=completed, NAS 루트+코디 2개 폴더 생성, API/로그 반영
- **P1 모델사진폴더 NAS 직접생성 (FEATURE-001)** — 지시서 버전 반영
  - app/config.py: MYSQL_HOST/PORT/DB/USER/PASSWORD (os.getenv) 추가
  - app/workers/folder_poller.py: nas_folder_request 단일 테이블 + cody_data(JSON) 기반으로 전면 수정 (get_db_connection, build_folder_structure(request), process_pending_requests, run_poll_cycle)
  - app/api/routes.py: GET /api/folder/status/{request_id}, GET /api/folder/requests 추가
  - tests/test_folder_poller.py: 지시서 테스트 11건으로 교체
  - 보고서: docs/reports/CUR-NASIMG-FEATURE-001-20260225.md 갱신
- **P1 모델사진폴더 NAS 직접생성 (FEATURE-001)** (기존)
  - requirements.txt에 PyMySQL>=1.1.0 추가
  - .env.example 및 app/config.py에 116 DB 설정 (NEWTALK_DB_HOST/PORT/NAME/USER/PASSWORD)
  - docs/DATABASE.md §8: nas_folder_request 테이블 설계, CREATE TABLE, 플로우
  - app/workers/folder_poller.py 신규: pending 조회 → contents_msg/cody_msg/cody_product_msg 기반 폴더명 조합 → mkdir (파일 삭제/수정 금지)
  - docker-compose.yml: /volume1/★제품사진 ro → rw
  - main.py: 60초 간격 _folder_poller_loop 백그라운드 등록
  - tests/test_folder_poller.py 7건 추가
  - 보고서: docs/reports/CUR-NASIMG-FEATURE-001-20260225.md
- **P1 선행: NAS → 114서버(116 DB) MySQL 접속 테스트**
  - 스크립트: `scripts/nas_mysql_114_connection_test.sh` (STEP 1~4: 포트 확인, Docker 내 mysql/pymysql 확인, TCP 테스트, 로그인 예시 안내)
  - 보고서 템플릿: docs/reports/CUR-NASIMG-DB-CONN-001-20260225.md (실행 후 결과 기입, 비밀번호/접속 문자열 미포함)

## 2026-02-24
- **PIPELINE_PROCESS.md 신규 생성** — 전체 자동화 파이프라인 프로세스 정의 (AS-IS/TO-BE, P1~P6 상세, 로드맵, 기술 참조)
- PLANNING.md: TO-BE 워크플로우를 PIPELINE_PROCESS와 동기화, Phase 3/4 로드맵 구체화 (P3~P6)
- CONTEXT.md: 바로 다음 할 일에 P1(모델사진폴더 NAS 직접 생성) 추가, 참조 문서에 PIPELINE_PROCESS.md 추가
- **QC 프리셋 등록 오류 수정 (BUG-FIX-001)**
  - 증상: 등록 버튼 클릭 시 폼만 리셋되고 목록에 미등록
  - 원인: 폼 기본 제출(native submit)으로 같은 페이지 GET 재로드 → API 미호출
  - 수정: preset_register.html에 `onsubmit="return false;"`, `action="#"` 추가
  - 부가: 수정 페이지용 `isEdit`/`presetId` 템플릿 주입, 목록 썸네일 fallback URL (`/api/preset/{id}/image`)
  - 보강: API에서 `analyze_image()` 실패 시 400 + 한글 메시지 반환(stats_json NOT NULL 안전), Jinja2 필터 공백 정리
  - 보고서: docs/reports/CUR-NASIMG-BUG-FIX-001-20260224.md

## 2026-02-23
- DB 스키마 문서화 (docs/DATABASE.md) — 테이블 구조, 인덱스, 114서버 연동 참조
- requirements.txt에 httpx 추가 (TestClient 의존성)
- Docker 빌드 성공 (오프라인 pip-cache, libgl1 수정)
- **소스 검수 개선사항 일괄 적용**
  - 톤 매칭 엔진 v2: 적응형 강도 차원별 정규화 가중치(ADAPTIVE_WEIGHTS), AB채널 보호 비율(ab_protection_ratio) 파라미터화, 피부 HSV(SKIN_HSV_*) config화, WhiteBalanceNormalizer 배경 제외(exclude_background) 옵션
  - 배치 파이프라인 리팩터링: PipelineConfig/PipelineResult dataclass, run_pipeline(source_path, config) 시그니처, HEIC 변환 convert_heic_to_jpg 유틸 분리
  - 자동 보정 파라미터 외부화: CorrectionConfig dataclass (target_brightness, CLAHE, sharpen, jpeg_quality)
  - AI 크랍: FALLBACK_RATIOS 상수화, 종횡비 3:1/1:3 초과 시 warning, model_complexity=1 주석(NAS 하드웨어 제한)
  - 배경 제거: 반환값 (output_path, thumbnail_path, fallback_used), PhotoRoom API키 미설정 시 rembg 직접 사용 및 로그
  - 파일명 매퍼: EXCLUDE_SUFFIXES config화(-Photoroom, -rembg), 15장 초과 시 warning
  - rsync_114: sync_goods에 max_retries, retry_delay, 재시도 후 retry_count 결과 포함
- 신규 테스트: test_tone_matcher_v2.py, test_batch_pipeline_v2.py, test_auto_corrector_v2.py
- GitHub 저장소 연동 (moongoby/newtalk-image-auto, private)
- .gitignore 정리 (.env, __pycache__, data/db 제거)
- Windows PC → NAS SSH 키 인증 설정
- NAS Git Server 설치
- 문서 관리 체계 구축 (CONTEXT.md, CHANGELOG.md, .cursorrules)
- Dockerfile 오프라인 빌드 전환: pip-cache/ 로컬 whl 설치 (NAS SSL 에러 대응)
- .dockerignore 생성
- 문서 보완: HANDOVER 테스트현황 갱신, 작업규칙 보완 (git경로 보고, 한국시간)

## 2026-02-22
- 파일명 매핑 모듈 (7 tests)
- 리사이즈 모듈 테스트 (5 tests)
- 배치 API 통합 테스트 (18 tests)
- E2E 파이프라인 + rsync 114 동기화 모듈 (2 tests)
- AI 크랍 MediaPipe Pose (8 tests)
- QC UI 비교 슬라이더 (8 tests)
- 톤 매칭 엔진 + 프리셋 CRUD API (12 tests)
- 폴더 자동 분류 EXIF 기반 (8 tests)
- Dockerfile openssh-client, rsync, tests/ 추가
- NAS→114 동기화 인프라 (nasync 계정, SSH 키)

## 2026-02-21
- Docker 컨테이너 실행, 볼륨 마운트
- PhotoRoom API + rembg 폴백
- 모델컷 보정 v2
- 폴더 파싱, .env 관리
- 114서버 이미지 구조 파악
- nasync 계정 생성, SSH 키 등록
- NAS→114 rsync 전송 성공
