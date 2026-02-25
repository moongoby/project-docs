# CUR-NASIMG-FEATURE-001-20260225

**제목:** P1 모델사진폴더 NAS 직접생성 — PyMySQL + 폴더 폴링 워커 + API  
**작성일시:** 2026-02-25 KST  
**작업 유형:** FEATURE  
**목적:** 116서버 DB(autoda) nas_folder_request 폴링으로 ★제품사진/ 아래 모델사진 폴더 자동 생성

---

## 1. 작업 개요

- **요구사항:** 116 어드민에서 NAS 폴더생성 요청 시 DB(nas_folder_request)에 INSERT → NAS에서 1분마다 pending 조회 후 폴더 생성
- **구현 범위:** PyMySQL 추가, MYSQL_* 환경변수/config, folder_poller 워커(nas_folder_request 단일 테이블 + cody_data JSON), docker-compose rw, 폴더 상태 API, 테스트

---

## 2. 변경 사항

### 2.1 requirements.txt
- **PyMySQL>=1.1.0** 추가 (116 MySQL 접속용)

### 2.2 환경 변수 / config
- **.env** (커밋 금지, .gitignore 확인)
  - `MYSQL_HOST=114.207.244.86`, `MYSQL_PORT=3306`, `MYSQL_DB=autoda`, `MYSQL_USER=pigupuser`, `MYSQL_PASSWORD=실제비밀번호`
  - 비밀번호는 server116/application/config/database.php의 `$db['default']['password']` 사용
- **app/config.py**
  - `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DB`, `MYSQL_USER`, `MYSQL_PASSWORD` (os.getenv 기반) 추가
  - 기존 newtalk_db_* (Settings) 유지

### 2.3 폴더 폴링 워커 (app/workers/folder_poller.py)
- **스키마:** nas_folder_request 단일 테이블에 shooting_date, model_name, place_name, cody_data(JSON) 포함
- **함수**
  - `get_db_connection()`: MYSQL_* 기반 pymysql 연결 (connect_timeout=10, read_timeout=30)
  - `sanitize_folder_name(name)`: Windows/NAS 금지 문자 제거
  - `build_folder_structure(request)`: request 한 건에서 root_folder + cody_folders 생성 (cody_data JSON 파싱)
  - `create_folders_on_nas(folder_structure)`: PHOTOS_ROOT 아래 mkdir만 수행 (파일 삭제/수정 금지)
  - `update_request_status(conn, request_id, status, error_message)`: completed/failed 시 processed_at 갱신
  - `process_pending_requests()`: pending 최대 10건 조회 → processing → 폴더 생성 → completed/failed
  - `run_poll_cycle()`: MYSQL_PASSWORD 미설정 시 스킵, 그 외 process_pending_requests() 호출
  - `folder_poller_loop()`: 비동기 1분 간격 루프 (run_in_executor로 동기 DB 실행)

### 2.4 docker-compose.yml
- `/volume1/★제품사진:/data/photos` 볼륨 **ro → rw** (폴더 생성용 mkdir 허용)

### 2.5 main.py
- 기존 유지: `_folder_poller_loop()`에서 60초 간격으로 `run_poll_cycle()` 실행 (lifespan 등록)

### 2.6 API (app/api/routes.py)
- **GET /api/folder/status/{request_id}** — NAS 폴더 생성 요청 1건 상태 조회 (id, shooting_id, status, error_message, created_at, processed_at). 없으면 404.
- **GET /api/folder/requests** — 최근 폴더 생성 요청 목록 20건 (id, shooting_id, shooting_date, model_name, status, created_at, processed_at)

### 2.7 테스트 (tests/test_folder_poller.py)
- TestSanitizeFolderName: 일반/특수문자/빈값/공백
- TestBuildFolderStructure: 기본 구조, 다중 코디, 필드 누락, 다중 상품
- TestCreateFoldersOnNas: 폴더 생성, idempotent
- TestDBConnection: get_db_connection 호출 시 charset, connect_timeout 검증
- **11 passed**

---

## 3. 검증

### 3.1 pytest
- **폴더 폴러 전용:** `tests/test_folder_poller.py` → **11 passed**
- 전체 테스트는 NAS Docker 재빌드 후 `sudo docker exec newtalk-image-auto python3 -m pytest tests/ -v --tb=short` 로 확인

### 3.2 .env / 비밀번호
- `.env`는 `.gitignore`에 포함되어 커밋되지 않음
- `MYSQL_PASSWORD`는 .env에만 설정, 코드/문서에 실제 값 미기재

### 3.3 NAS 배포 후 확인 (STEP 9)
- pymysql: `sudo docker exec newtalk-image-auto python3 -c "import pymysql; print('pymysql', pymysql.__version__)"`
- 볼륨 rw: `sudo docker inspect newtalk-image-auto --format='{{json .Mounts}}' | python3 -m json.tool | grep -A5 "photos"`
- 폴더 쓰기: `sudo docker exec newtalk-image-auto python3 -c "import os; os.makedirs('/data/photos/_folder_test', exist_ok=True); os.rmdir('/data/photos/_folder_test'); print('ok')"`
- API: `curl -s http://localhost:8100/api/health` → 200, `curl -s http://localhost:8100/api/folder/requests` → 200
- 로그: `sudo docker logs --tail 20 newtalk-image-auto | grep "폴더폴링"` → "[폴더폴링] 워커 시작" 확인

---

## 4. 후속 작업

1. **.env** — NAS에서 MYSQL_HOST, MYSQL_PORT, MYSQL_DB, MYSQL_USER, MYSQL_PASSWORD 설정 (비밀번호는 116 database.php 기준)
2. **116서버 DB** — nas_folder_request 테이블에 shooting_id, shooting_date, model_name, place_name, cody_data(JSON), status, error_message, created_at, processed_at 컬럼 반영 (114 Cursor와 협의)
3. **NAS Docker** — `sudo docker-compose build --no-cache && sudo docker-compose up -d`
4. **pip-cache (오프라인 빌드):** `pip download PyMySQL>=1.1.0 -d pip-cache/`

---

## 5. 참고

- **GitHub Private:** https://github.com/moongoby/newtalk-image-auto (main)
- **GitHub Public docs:** https://github.com/moongoby/project-docs (master)
- **보고서 Public:** https://github.com/moongoby/project-docs/blob/master/nas-image/reports/CUR-NASIMG-FEATURE-001-20260225.md
- **등록 확인:** `curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby/project-docs/master/nas-image/reports/CUR-NASIMG-FEATURE-001-20260225.md` → 200
- **동기화:** project-docs 동기화 후 "완료" 기재

---

## 7. P1 통합 테스트 사전 확인 (2026-02-25 KST)

### 7.1 사전확인 1~9 결과 (로컬/코드베이스 기준)

| # | 항목 | 결과 | 비고 |
|---|------|------|------|
| 1 | folder_poller.py 존재 | ✅ 통과 | `app/workers/folder_poller.py` 존재 (약 7.9KB) |
| 2 | requirements.txt PyMySQL | ✅ 통과 | `PyMySQL>=1.1.0` (18행) |
| 3 | docker-compose.yml rw | ✅ 통과 | `/volume1/★제품사진:/data/photos:rw` |
| 4 | main.py 폴링 등록 | ✅ 통과 | `_folder_poller_loop`, `run_poll_cycle`, lifespan에 태스크 등록 |
| 5 | .env MYSQL/GEMINI 키 | ⚠️ NAS에서 확인 | 로컬 .env에 키 없음. **NAS 배포 시 .env에 MYSQL_HOST, MYSQL_PASSWORD, GEMINI_API_KEY 설정 필요** (.env.example 참고) |
| 6 | Docker 컨테이너 상태 | ⏸ NAS에서 실행 | 로컬 Windows에는 Docker 미설치. **NAS에서** `sudo docker ps \| grep newtalk` 실행 |
| 7 | pymysql 설치 확인 | ⏸ NAS에서 실행 | **NAS에서** `sudo docker exec newtalk-image-auto python3 -c "import pymysql; print('pymysql', pymysql.__version__)"` |
| 8 | 폴링 워커 로그 | ⏸ NAS에서 실행 | **NAS에서** `sudo docker logs --tail 30 newtalk-image-auto \| grep -i "폴더폴링\|folder_poller\|mysql\|error"` |
| 9 | API 헬스 + /folder/requests | ⏸ NAS에서 실행 | **NAS에서** `curl -s http://localhost:8100/api/health`, `curl -s http://localhost:8100/api/folder/requests` |

### 7.2 미완료 시 즉시 실행 (NAS 기준)

- **.env에 MYSQL 정보 없음** → `MYSQL_HOST=114.207.244.86`, `MYSQL_PORT=3306`, `MYSQL_DB=autoda`, `MYSQL_USER=pigupuser`, `MYSQL_PASSWORD=***` 추가 (비밀번호는 server116 `application/config/database.php` 참조)
- **.env에 GEMINI_API_KEY 없음** → 114서버 ShortFlow `.env`에서 복사: `cat /data/shortflow/.env | grep GEMINI_API_KEY`
- **Docker 미빌드** → `sudo docker-compose build --no-cache && sudo docker-compose up -d`
- **pip-cache (오프라인)** → `pip download PyMySQL>=1.1.0 -d pip-cache/`

### 7.3 DB 테이블 생성 확인 (NAS에서 116 DB 접속)

```bash
mysql -h 114.207.244.86 -P 3306 -u pigupuser -p autoda -e "DESCRIBE nas_folder_request;"
```

테이블 없으면:

```sql
CREATE TABLE IF NOT EXISTS nas_folder_request (
  id INT AUTO_INCREMENT PRIMARY KEY,
  shooting_id INT NOT NULL,
  shooting_date VARCHAR(20) DEFAULT NULL,
  model_name VARCHAR(100) DEFAULT NULL,
  place_name VARCHAR(100) DEFAULT NULL,
  cody_data TEXT NOT NULL,
  status ENUM('pending','processing','completed','failed') DEFAULT 'pending',
  error_message TEXT DEFAULT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  processed_at DATETIME DEFAULT NULL,
  INDEX idx_status (status),
  INDEX idx_shooting_id (shooting_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 7.4 통합 테스트 STEP 1~7 (NAS에서 사전확인 통과 후)

- **STEP 1** — 테스트 데이터 INSERT (shooting_id=9999)
- **STEP 2** — 폴링 대기 약 70초
- **STEP 3** — DB status/processed_at 확인
- **STEP 4** — NAS 폴더 `2026-02-25_통합테스트모델_스튜디오A` 및 코디 하위폴더 확인
- **STEP 5** — Docker 로그 `[폴더폴링] 요청 #N 완료` 확인
- **STEP 6** — `curl -s http://localhost:8100/api/folder/requests` JSON 확인
- **STEP 7** — `DELETE FROM nas_folder_request WHERE shooting_id=9999;` 정리

**성공 기준:** DB pending → 1분 내 completed, NAS 루트폴더+코디 2개 생성, 로그·API 반영.

### 7.5 통합 테스트 결과 (NAS 실행 후 기입)

**2026-02-25 원격 실행 시도 요약:**  
NAS SSH 접속 후 STEP 1~2까지 실행 시도. STEP 1(.env 키 확인) 통과, git pull 완료. **Docker 빌드 단계에서 `sudo` 비밀번호 입력 필요로 비대화형 원격 실행 중단.**  
→ **NAS 터미널에 직접 로그인한 뒤** 아래 스크립트 실행 후 §7.5 표를 채울 것.  
- 전체 자동 실행 스크립트: `./scripts/nas_run_p1_remote.sh` (STEP 1~9 + 결과를 `p1_test_result.txt`에 저장)  
- 또는 지시서 단계별: `./scripts/nas_p1_integration_test.sh`  
- pip-cache에 PyMySQL 없으면:  
  `wget -P pip-cache/ https://files.pythonhosted.org/packages/c5/29/5114dc18bad3ed1d2e7df7969790f1b15e648d7d3ba6dc19f904bb6d6f57/pymysql-1.1.1-py3-none-any.whl`

| STEP | 항목 | 결과 | 비고 |
|------|------|------|------|
| 0 | NAS 경로 이동 | ✅ (원격 시도 시 확인) | find로 /volume1/뉴톡/newtalk-image-auto 진입 |
| 1 | .env MYSQL/GEMINI 키 | ✅ MYSQL_PASSWORD=*** 존재 | 원격 실행 시 확인됨 |
| 1 | pip-cache PyMySQL | ⚠️ whl 없음 → wget 시도 | Docker 단계 전에 중단되어 wget 결과 미확인 |
| 2 | git pull | ✅ Already up to date | |
| 2 | Docker 재빌드/기동 | ❌ 중단 | sudo 비밀번호 필요 (NAS에서 직접 실행 시 입력 후 진행) |
| 3-1 | pymysql 버전 | (NAS 실행 후 기입) | 예: pymysql 1.1.0 |
| 3-2 | 폴링 워커 로그 | (NAS 실행 후 기입) | [폴더폴링] 워커 시작 등 |
| 3-3 | API /api/health | (NAS 실행 후 기입) | 200 |
| 3-4 | API /api/folder/requests | (NAS 실행 후 기입) | 200 + JSON |
| 3-5 | 볼륨 rw 쓰기 | (NAS 실행 후 기입) | 쓰기 성공 / 정리 완료 |
| 4 | DB 테이블 존재/생성 | (NAS 실행 후 기입) | DESCRIBE 또는 CREATE 완료 |
| 5 | INSERT shooting_id=9999 | (NAS 실행 후 기입) | INSERT 성공, id=N |
| 6 | 폴링 대기 70초 | (NAS 실행 후 기입) | KST 시각 기록 |
| 7-1 | DB status/processed_at | (NAS 실행 후 기입) | status=completed 여부 |
| 7-2 | NAS 루트폴더 | (NAS 실행 후 기입) | 2026-02-25_통합테스트모델_스튜디오A |
| 7-3 | NAS 코디 하위폴더 2개 | (NAS 실행 후 기입) | 1번코디, 2번코디 |
| 7-4 | Docker 로그 완료 메시지 | (NAS 실행 후 기입) | [폴더폴링] 요청 #N 완료 |
| 7-5 | API /folder/requests 응답 | (NAS 실행 후 기입) | shooting_id=9999 표시 |
| 8 | DB 테스트 데이터 삭제 | (NAS 실행 후 기입) | DELETE 완료 N건 |
| 9 | pytest test_folder_poller | (NAS 실행 후 기입) | passed 개수 |
| 9 | pytest 전체 | (NAS 실행 후 기입) | passed/skipped/failed |
| **판정** | **성공/실패** | **(NAS 전체 실행 후 기입)** | |
| (실패 시) | 에러 로그 | (해당 시 전문 붙여넣기) | |

**실행 스크립트:**  
- `./scripts/nas_p1_integration_test.sh` (NAS SSH에서 프로젝트 루트 실행)  
- `./scripts/nas_run_p1_remote.sh` (STEP 1~9 일괄 실행, 결과 `p1_test_result.txt` 저장)

---

## 8. 커밋 해시 (작업 완료 후 기입)

- **ca064ae** feat: NAS 폴더 자동생성 폴링 워커 (P1) - PyMySQL + folder_poller + API + MYSQL_* config
