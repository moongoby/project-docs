# 변경 이력

## 2026-02-23
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
