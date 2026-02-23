# NAS 이미지 자동화 프로젝트 CONTEXT
> 최종 갱신: 2026-02-23
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
- 원본: /volume1/★제품사진/ (ro), 결과: /volume1/★제품사진/_processed/ (rw)
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

## 바로 다음 할 일
1. Work C: 피부톤 보호 + 배경 분리 (tone_matcher.py)
2. Work D: 적응형 강도 v2 + 화이트밸런스 정규화 (tone_matcher.py)
3. NAS Docker 재빌드 (대표님 실행)

## 주의사항
- mediapipe <0.10.31 고정 (solutions API 제거 이슈)
- PhotoRoom 크레딧 소진, 제품컷은 아이폰 앱 병행
- NAS 하드웨어 제한: model_complexity=1
- 114 danharoo 계정 SFTP만, nasync 계정 사용
- SQLite 동시성: Phase 3-4에서 WAL 또는 PostgreSQL 검토

## 테스트 현황 (68 passed, 8 skipped)
- test_filename_mapper: 7p / test_image_resize: 5p 1s / test_batch_pipeline: 18p 3s
- test_e2e_pipeline: 2p 1s / test_auto_crop: 8p / test_qc_ui: 8p
- test_tone_matcher: 12p / test_auto_classify: 8p

## 비용
PhotoRoom API Basic $20/월 (1,000장, 초과 $0.02/장) - 결제 보류

## 로드맵
- 2월 4주차: Work C/D, Docker 빌드, Phase 2 완료
- 3월 초중: 실사진 테스트, Phase 3 착수
- 4월: Phase 4 (어드민 연동)
