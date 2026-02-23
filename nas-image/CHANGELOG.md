# 변경 이력

## 2026-02-23
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
