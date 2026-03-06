# StyleFlow 릴스 자동화 시스템 Phase 1

**작성일시:** 2026-02-21
**작업 유형:** 신규 개발
**상태:** 완료
**관련 파일:**  
`engine/editor.py`, `engine/db_connector.py`, `engine/sync_nas.sh`, `engine/watcher.py`,  
`engine/requirements.txt`, `scripts/batch_reels_chicblack.py`,  
`.env` (NEWTALK_DB_* 추가), `.gitignore` (/data/styleflow/ 추가)

---

## 1. 작업 개요

작업지시서에 따라 StyleFlow 릴스 자동화 Phase 1을 수행했다.  
한글 폰트 설치·수정된 릴스 테스트, 자동 편집 엔진(ReelEditor), 뉴톡 DB 연동, NAS 동기화 스크립트, 파일 워처, 11개 MOV 일괄 생성 및 인덱스 페이지를 구현·검증했다.

## 2. 변경 사항

### 2.1 Task 1: 한글 폰트 + 수정된 릴스 테스트
- `apt install fonts-nanum` 실행, `fc-cache -fv` 적용.
- Nanum 폰트 경로: `/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf`.
- `reel_outfit_check_002.mp4` 생성: transpose 미사용(아이폰 메타데이터 자동 회전), 한글 폰트 적용, 오디오 유지(`-c:a aac`). 출력 1080x1920(세로) 확인.

### 2.2 Task 2: engine/editor.py
- **ReelEditor** 클래스: MOV 경로 + 상품 정보 dict → MP4 릴스(9:16, 1080x1920).
- FFmpeg subprocess 호출, transpose 미사용, 한글 폰트 경로 상수 사용.
- 템플릿 A(Outfit Check) 구현: 상품명·가격·브랜드 drawtext.
- 템플릿 B~E: 스텁(현재 A로 폴백).
- `get_video_info()`(ffprobe), `generate_reel()`, `batch_generate()` 제공.
- 로그: `/data/styleflow/logs/editor_YYYYMMDD.log`.

### 2.3 Task 3: engine/db_connector.py
- autoda DB 접속: pymysql, `.env`에서 `NEWTALK_DB_HOST/USER/PASSWORD/NAME/PORT` 로드(python-dotenv).
- 함수: `get_chicblack_products_with_cody(limit)`, `get_product_by_code(code)`, `get_cody_products_by_cody_code(cody_code)`, `product_to_reel_info(row)`.
- `.env`에 뉴톡 DB 변수 추가(비밀번호는 환경에서 확인 후 설정).

### 2.4 Task 4: engine/sync_nas.sh
- NAS → 114 서버 영상 동기화: `ssh nas` + tar 파이프.
- 대상: `/data/styleflow/raw/chicblack`, 원격 `/volume1/★웹팀 작업폴더/릴스 영상` 하위 날짜(YYYYMMDD) 폴더.
- 이미 동기화된 폴더(파일 수 동일) 스킵.
- 로그: `/data/styleflow/logs/sync_YYYYMMDD.log`.
- 실행 권한 부여(`chmod +x`). crontab 예: `*/30 * * * * /data/shortflow/engine/sync_nas.sh`.

### 2.5 Task 5: engine/watcher.py
- watchdog으로 `/data/styleflow/raw/` 감시.
- 새 MOV 감지 시 30초 대기 후 자동 편집(ReelEditor, 템플릿 A).
- DB에서 상품 정보 조회 시도, 실패 시 기본 상품 정보 사용.
- 실행: `python -m engine.watcher` (프로젝트 루트에서). 의존성: `watchdog`, `pymysql`, `python-dotenv`.

### 2.6 Task 6: 11개 MOV 일괄 생성 + 인덱스
- `scripts/batch_reels_chicblack.py`: `raw/chicblack/20260220` 11개 MOV → 템플릿 A 적용, 11개 MP4 생성 완료.
- `/data/styleflow/output/chicblack/index.html` 생성: MP4 목록·비디오 링크로 브라우저에서 확인 가능.

### 2.7 기타
- `.gitignore`에 `/data/styleflow/` 추가.
- `engine/requirements.txt`: pymysql, python-dotenv, watchdog.
- Python 3.8 호환: `dict[str, Any]` → `Dict[str, Any]` 등 typing 수정.

## 3. 테스트 결과

- 한글 폰트: 설치 및 fc-list 확인 완료.
- reel_outfit_check_002.mp4: FFmpeg 성공, 1080x1920, 한글·오디오 유지.
- ReelEditor: batch_generate 11/11 성공.
- 인덱스 페이지: `output/chicblack/index.html` 존재, MP4 13개(기존 2 + 신규 11) 링크.
- DB 연동: 코드 및 .env 구성 완료. 실제 쿼리 실행은 DB 비밀번호 설정 후 가능.
- sync_nas.sh: 스크립트 검증 완료. 실제 NAS 동기화는 `ssh nas` 접속 가능 환경에서 실행 필요.

## 4. 주의사항 / 후속 작업

- **NEWTALK_DB_PASSWORD**: `.env`에 실제 비밀번호 설정 후 DB 조회·워처 자동 상품 매핑 사용 가능.
- **브라우저 확인**: `http://114.207.244.86:8888/` 등에서 `output/chicblack/`를 서빙하도록 웹 서버 docroot 설정 시 index.html로 전체 릴스 확인 가능.
- **템플릿 B~E**: 추후 길이·자막·BGM 등 스펙에 맞게 구현 필요.
- **BGM**: 저작권 프리 BGM 추가는 별도 작업.
- **crontab**: NAS 동기화 30분마다 실행 시 `crontab -e`에 `*/30 * * * * /data/shortflow/engine/sync_nas.sh` 등록 권장.
- **백업**: DB/설정 변경 전 mysqldump·cp .bak 규칙 유지.
