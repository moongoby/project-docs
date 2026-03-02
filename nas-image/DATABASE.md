# 뉴톡 이미지 자동화 시스템 — 데이터베이스 구조
**최종 갱신**: 2026-02-25 (KST)
**DB 엔진**: SQLite 3 (aiosqlite 비동기 래퍼)
**DB 경로**: /app/data/db/jobs.db (Docker 내부), /volume1/뉴톡/newtalk-image-auto/data/db/jobs.db (NAS)
**보안 참고**: 내부 작업 관리용 DB, 사용자 개인정보 없음, Public 공개 가능

## 1. 테이블 목록
- **image_queue** — 이미지 처리 작업 큐 (단건/배치 작업 등록)
- **image_result** — 작업 결과 (출력 경로, 상태, QC 승인/반려)
- **tone_presets** — 톤 매칭 프리셋 (LAB 통계값, 브랜드/시즌/태그)

## 2. 테이블별 스키마

### image_queue
| cid | 컬럼명 | 타입 | NOT NULL | 기본값 | PK |
|-----|--------|------|----------|--------|----|
| 0 | job_id | TEXT | 1 | - | 1 |
| 1 | source_path | TEXT | 1 | - | 0 |
| 2 | mode | TEXT | 1 | - | 0 |
| 3 | status | TEXT | 1 | 'queued' | 0 |
| 4 | message | TEXT | 0 | - | 0 |
| 5 | created_at | TEXT | 1 | - | 0 |
| 6 | preset_id | INTEGER | 0 | - | 0 |
| 7 | match_strength | REAL | 0 | - | 0 |
| 8 | advanced_matching | INTEGER | 0 | - | 0 |
| 9 | skin_protection | INTEGER | 0 | - | 0 |
| 10 | bg_separation | INTEGER | 0 | - | 0 |
| 11 | normalize_wb | INTEGER | 0 | - | 0 |
| 12 | wb_strength | REAL | 0 | - | 0 |

*preset_id ~ wb_strength는 init_db 시 ALTER TABLE로 추가되는 컬럼(배치 톤 매칭용).*

### image_result
| cid | 컬럼명 | 타입 | NOT NULL | 기본값 | PK |
|-----|--------|------|----------|--------|----|
| 0 | job_id | TEXT | 1 | - | 1 |
| 1 | output_path | TEXT | 0 | - | 0 |
| 2 | status | TEXT | 1 | - | 0 |
| 3 | message | TEXT | 0 | - | 0 |
| 4 | updated_at | TEXT | 1 | - | 0 |

- **FOREIGN KEY**: job_id → image_queue(job_id)

### tone_presets
| cid | 컬럼명 | 타입 | NOT NULL | 기본값 | PK |
|-----|--------|------|----------|--------|----|
| 0 | id | INTEGER | 1 | AUTOINCREMENT | 1 |
| 1 | name | TEXT | 1 | - | 0 |
| 2 | description | TEXT | 0 | - | 0 |
| 3 | brand | TEXT | 0 | - | 0 |
| 4 | season | TEXT | 0 | - | 0 |
| 5 | tags | TEXT | 0 | - | 0 |
| 6 | stats_json | TEXT | 1 | - | 0 |
| 7 | image_path | TEXT | 0 | - | 0 |
| 8 | thumbnail_path | TEXT | 0 | - | 0 |
| 9 | use_count | INTEGER | 1 | 0 | 0 |
| 10 | created_at | TEXT | 1 | - | 0 |
| 11 | updated_at | TEXT | 1 | - | 0 |

## 3. 테이블별 설명
- **image_queue**: 이미지 처리 작업 큐. 단건/배치 API에서 생성, 워커가 queued → processing, 완료 시 image_result에 기록. QC UI에서 조회/승인/반려. preset_id, match_strength, advanced_matching, skin_protection, bg_separation, normalize_wb, wb_strength는 배치 톤 매칭 옵션.
- **image_result**: 작업별 결과 1:1. output_path, status(completed/approved/rejected), message(QC 반려 사유 등). INSERT OR REPLACE로 갱신.
- **tone_presets**: 톤 매칭 프리셋. LAB 채널 통계(stats_json), 브랜드/시즌/태그, 미리보기 이미지 경로. CRUD API로 관리, 기본 프리셋 3종은 ensure_default_presets()로 초기화.

## 4. 인덱스
- **image_queue**: PRIMARY KEY (job_id) — SQLite 기본 인덱스
- **image_result**: PRIMARY KEY (job_id) — SQLite 기본 인덱스
- **tone_presets**: PRIMARY KEY (id) — SQLite 기본 인덱스  
*추가 인덱스 없음. list_sessions / list_presets는 LIMIT 소량 조회.*

## 5. 관계도
```
image_queue (1) ----< (1) image_result
    job_id (PK)            job_id (PK, FK → image_queue.job_id)

image_queue.preset_id ──> tone_presets.id (논리 참조, FK 미정의)
```
- image_result.job_id는 image_queue.job_id에 대한 FOREIGN KEY 정의됨.
- image_queue.preset_id는 tone_presets.id를 참조하나, SQLite FK 제약은 미설정(선택 적용).

## 6. 향후 변경 예정
- Phase 3-4: WAL 모드 또는 PostgreSQL 전환 검토
- Phase 4: 114서버 goods_detail, goods_image 테이블 연동 예정
  - goods_detail: GoodsEtc60~74 (제품컷 경로), GoodsSortImg1~4 (정렬 이미지)
  - goods_image: ~76,892건, 상품별 이미지 메타데이터

## 7. 114서버 DB 참조 정보 (읽기 전용, Phase 4 연동 대상)
- 서버: [SERVER-IP]
- DB: MySQL (cafe24 호스팅)
- 주요 테이블: goods_detail, goods_image
- 연동 방식: Phase 4에서 API 또는 직접 DB 연결로 이미지 경로 자동 업데이트

## 8. 116서버 DB(autoda) — nas_folder_request (P1 폴더생성 폴링)
- **서버**: [SERVER-IP]:3306 (116서버 MySQL)
- **DB명**: autoda
- **용도**: 116 어드민 "NAS 폴더생성" 버튼 시 INSERT → NAS 폴러가 1분마다 pending 조회 후 폴더 생성, 상태 업데이트

### nas_folder_request (116서버 DB에 생성)
| 컬럼명 | 타입 | NOT NULL | 기본값 | 설명 |
|--------|------|----------|--------|------|
| id | INT AUTO_INCREMENT | ✓ | - | PK |
| shooting_id | INT | ✓ | - | 촬영 ID (contents_msg 등 조인 키) |
| status | ENUM('pending','processing','completed','failed') | - | 'pending' | 처리 상태 |
| error_message | TEXT | - | NULL | 실패 시 오류 메시지 |
| created_at | DATETIME | - | CURRENT_TIMESTAMP | 요청 생성 시각 |
| processed_at | DATETIME | - | NULL | 처리 완료 시각 |

**인덱스**: `INDEX idx_status (status)`

**생성 SQL (116서버에서 실행)**:
```sql
CREATE TABLE nas_folder_request (
  id INT AUTO_INCREMENT PRIMARY KEY,
  shooting_id INT NOT NULL,
  status ENUM('pending','processing','completed','failed') DEFAULT 'pending',
  error_message TEXT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  processed_at DATETIME NULL,
  INDEX idx_status (status)
);
```

**플로우**:
- 116 PHP: `INSERT INTO nas_folder_request (shooting_id) VALUES (?);`
- NAS 폴러: `SELECT * FROM nas_folder_request WHERE status = 'pending';` → 폴더 생성 후 `UPDATE ... SET status='completed', processed_at=NOW();` 또는 `status='failed', error_message=?`
