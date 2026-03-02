# HANDOVER – NAS Image Auto (newtalk-image-auto) 
> 최종 업데이트: 2026-03-02 (v1.2 — P4-E-DEPLOY 스캐폴딩 완료 반영) 
> 관리자: CEO (moongoby) 
> 용도: 모든 AI 세션(웹 Claude, Cursor, Claude Code) 시작 시 필수 읽기 
 
--- 
 
## 1. 프로젝트 개요 
- **프로젝트명**: NAS Image Auto — 뉴톡 패션 이커머스 상품 이미지 자동화 파이프라인 
- **목표**: 촬영 원본 → A컷 선별 → 보정 → 크롭 → 인트로 생성 → 리네임 → CDN 업로드 → 114 DB 등록까지 전 과정 자동화 
- **저장소**: https://github.com/moongoby/newtalk-image-auto (main) 
- **문서 저장소**: https://github.com/moongoby/project-docs (master) → nas-image/ 디렉토리 
- **NAS**: Synology DSM, SSH newtalk@[NAS-IP] -p 2222, Docker 컨테이너 newtalk-image-auto 
- **114 서버**: SSH root@[SERVER-IP] -p [SSH-PORT], MariaDB autoda, CodeIgniter 
- **CDN**: DigitalOcean Spaces newtalk.nyc3.cdn.digitaloceanspaces.com 
- **AI API**: Google Gemini (A컷 선별, 인트로 카피 생성) 
- **FastAPI**: 포트 8100, Docker 내부 
 
### 인프라 구조 
NAS ([NAS-IP]) 
├── /volume1/★제품사진/ → Docker /data/photos/ (촬영 원본) 
├── /volume1/★제품사진/_processed → Docker /data/processed/ (처리 결과) 
├── /volume1/뉴톡/newtalk-image-auto/ → 소스코드 + 스크립트 
└── Docker: newtalk-image-auto (FastAPI :8100) 
 
114 서버 ([SERVER-IP]) 
├── MariaDB autoda → goods, goods_detail 테이블 
├── 이미지 경로: /home/danharoo/www/data/files/goods/goodscode/img/{GoodsCode}/ 
└── CodeIgniter: application/controllers/ 
 
CDN (DigitalOcean Spaces) 
└── newtalk.nyc3.cdn.digitaloceanspaces.com/img/{YYYYMM}/{filename} 
 
### 파일명 규칙 
| 이미지 종류 | 패턴 | 예시 | 
|---|---|---| 
| 관리이미지 (1:1) | {GoodsCode}-600_{N}.jpg | bl5889k62-600_1.jpg | 
| 모델사진 (3:4) | {GoodsCode}-s_{N}.jpg | bl5889k62-s_1.jpg | 
| 제품사진 | {GoodsCode}-img_{NN}.jpg | bl5889k62-img_01.jpg | 
| 인트로 | {GoodsCode}-i_{template}_{N}.jpg | bl5889k62-i_A_1.jpg | 
 
### DB 구조 (goods_detail) 
- GoodsSortImg1: 인트로 파일명 (|| 구분) 
- GoodsSortImg2: 모델사진 파일명 (|| 구분) 
- GoodsSortImg3: 제품사진 파일명 (|| 구분) 
- GoodsSortImg4: 전체 관리이미지 파일명 (|| 구분) 
- GoodsEtc60~74: 개별 이미지 URL 
 
--- 
 
## 2. 완료된 작업 
 
| Task ID | 날짜 | 커밋 | HTTP | 핵심 결과 | 
|---------|------|------|------|-----------| 
| P1-FOLDER-CREATE | ~02-24 | ✓ | — | NAS 코디 폴더 자동 생성, 실무 운영 중 | 
| P2-LABEL-OCR | ~02-24 | ✓ | — | 라벨 OCR/코디 분류 (보류, 실무 룰 확정 후 재개) | 
| PRESET-SYSTEM | 02-24 | ✓ | — | 톤 프리셋 8개 등록, 전 레이어 정상 확인 | 
| P3-ACUT-V2 | 02-26 | ✓ | — | A컷 자동 선별 v2: 상업적 매력도+감성컷, output_suffix, pytest 8 PASS | 
| P3-BATCH-RUN | 02-28 | ✓ | — | 31개 코디 배치 완료 (시크블랙14+리엘라17+α), 타임아웃3건 재실행 성공 | 
| P4-D-INTRO | 03-02 | e2f115f | 200 | 인트로 이미지 AI 생성 모듈: 템플릿 A~E, Gemini 카피, 배치, pytest 18 PASS | 
| P4-E-DEPLOY | 03-02 | fdd521e | 200 | 리네임+CDN dry-run+DB mock 파이프라인: rename_map.json, pytest 17 PASS (실배포 CEO 승인 대기) | 
 
--- 
 
## 3. 진행 중 작업 
 
| Task ID | 상태 | 내용 | 
|---------|------|------| 
| P4-A-CROP | 개발 중 | 자동 크롭 (MediaPipe Pose, 1:1/3:4) | 
| P4-B-TONE | 개발 중 | 자동 톤/노출/색감 보정 | 
| P4-C-RETOUCH | 지시서 발행 | 체형/피부 AI 보정 | 
| P4-D-INTRO | **완료** | 인트로 이미지 AI 생성 (템플릿 A~E) — 커밋 e2f115f | 
| P4-E-DEPLOY | **스캐폴딩 완료** | 리네임+CDN dry-run+DB mock — 커밋 fdd521e (실배포 CEO 승인 필요) | 
| P4-114-API | 개발 중 | 114 서버 이미지 등록 PHP API | 
 
--- 
 
## 4. 보류/미시작 
 
| 항목 | 선행조건 | 우선순위 | 
|------|----------|----------| 
| P2 라벨 OCR 재개 | 실무 룰 확정 | 보류 | 
| P3 v1/v2 비교 피드백 | 실무자 검토 | P4 병행 | 
| P4 통합 파이프라인 | P4 개별 모듈 완료 | P4 직후 | 
| P5 배치 스케줄러 | P4 통합 완료 | 후순위 | 
 
--- 
 
## 5. 핵심 발견 (누적) 
 
### 인프라 
- Docker 내부 경로: /data/photos/ (NAS /volume1/★제품사진/) 
- NAS SSH 유저(newtalk)는 Docker 권한 없음 → DSM 스케줄러(root) 필수 
- 스크립트 CRLF → sed -i 's/\r$//' 변환 필수 
- Docker 내부에서 /volume1/ 접근 불가 → Python 스크립트 대체 
 
### P3 A컷 선별 
- Gemini PROHIBITED_CONTENT 차단 → fallback 상위 N장 복사 
- ≤target_count 코디는 전체 복사 (정상) 
- 200장+ 코디 타임아웃 → timeout 1200초 해결 
- output_suffix 미적용 추정 (v1+v2 A컷 폴더 병합) 
 
### P4-D 인트로 생성 
- 폰트: Dockerfile에 fonts-nanum 추가 (apt), 없을 때 PIL 기본폰트 fallback 
- Gemini PROHIBITED_CONTENT fallback 필수 구현 완료 
- 출력 경로: /data/processed/{goods_code}/_intro/ 
- 파일명: {goods_code}-i_{template}_1.jpg (A~E) 
- API: POST /api/v1/intro (코디폴더 기반), POST /api/v1/intro/batch 
 
### 상세페이지 구조 
- 4카테고리: 관리(600), 인트로(i), 모델(s), 제품(img) 
- 실무: 촬영→분류→보정→크롭→인트로→리네임→업로드 
- 모델 보정: 가슴/어깨/허리/엉덩이/다리/문신/피부톤/턱선 — 모델별 프리셋 
 
### 벤치마킹 
- 아뜨랑스/프롬비기닝/난닝구 분석 완료 
- 인트로 5종 템플릿: A캐치프레이즈, B포인트, C멀티앵글, D리뷰, E코디제안 
 
--- 
 
## 6. 웹 Claude 인수인계 사항 
 
### 최신 상태 (2026-03-02) 
- P3 배치 31코디 완료, 실무자 피드백 대기 
- P4-D-INTRO 완료 (템플릿 A~E, pytest 18 PASS) 
- P4-E-DEPLOY 스캐폴딩 완료 (리네임+CDN dry-run+DB mock, pytest 17 PASS — 실배포 CEO 승인 대기)
- P4-A-CROP, P4-B-TONE, P4-114-API 개발 중 
- P4-C-RETOUCH 지시서 발행 상태 
 
### 웹 Claude가 해야 할 일 
1. P4 커서 결과 수신 → 각 모듈 보고서 교차검증 
2. P3 실무자 피드백 → A컷 폴더 정리 지시서 
3. P4 모듈 완료 후 → 통합 파이프라인 연결 지시서 
4. CEO-DIRECTIVES.md 갱신 요청 
 
### 대표님 확인 필요 
1. P3 A컷 70장(v1+v2 병합) 실무자 품질 확인 
2. P4-C 모델별 보정 프리셋 구체화 
3. P4-D 인트로 품질 검수 (샘플 확인) 
4. DO_SPACES_KEY/SECRET .env 등록 
5. Docker rebuild 필요 (fonts-nanum 추가됨) 
 
### 주의사항 
- Docker rebuild 필요: Dockerfile에 fonts-nanum 추가됨 
- requirements.txt 변경 없음 (Pillow, google-generativeai 기존 포함) 
- google.generativeai deprecated → 향후 google.genai 마이그레이션 권장 
 
--- 
 
## 7. 업데이트 규칙 
- 매 Task 완료 시 이 파일 업데이트 + push 
- 섹션 2: 완료 Task 행 추가 
- 섹션 3: 진행 상태 갱신 
- 섹션 5: 신규 발견 추가 
- 섹션 6: 웹 Claude 인수인계 최신화 
- push 후 확인: curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/HANDOVER.md 
 
--- 
 
## 8. 버전 이력 
 
| 버전 | 날짜 | 변경 | 
|------|------|------| 
| v1.0 | 2026-02-28 | 초판 — P1~P3 완료, P4 지시서 발행, 인프라/파일명/DB 구조 문서화 | 
| v1.1 | 2026-03-02 | P4-D-INTRO 완료 반영, P4-A/B/114-API 개발 중 상태 갱신 | 
| v1.2 | 2026-03-02 | P4-E-DEPLOY 스캐폴딩 완료 반영 (dry-run/mock, fdd521e) | 
