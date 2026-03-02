# CUR-NAS-P4E-DEPLOY-001-20260302

**작성일**: 2026-03-02 KST  
**작업자**: CURSOR-NAS #4  
**Task ID**: P4-E-DEPLOY  
**커밋**: `fdd521e`  
**HTTP**: 200

---

## 1. 작업 개요

처리 완료된 이미지를 최종 파일명으로 리네임 → CDN(DigitalOcean Spaces) 업로드 → 114 DB(goods_detail) 등록까지의 배포 파이프라인 구현.

선행 모듈(P4-A~D) 완료 전 **설계 + 스캐폴딩 + dry-run/mock 구현**까지 완료.  
실배포(CDN 실업로드 + DB 실등록)는 **CEO 승인 후** 진행.

---

## 2. 구현 내용

### Phase 1: 리네임 엔진 (`app/workers/file_renamer.py`)

| 이미지 종류 | 소스 패턴 | 최종 파일명 |
|---|---|---|
| 관리이미지 (1:1) | `_crop_1x1.jpg` | `{GoodsCode}-600_{N}.jpg` |
| 모델사진 (3:4) | `_retouched.jpg` | `{GoodsCode}-s_{N}.jpg` |
| 제품사진 | 원본 제품컷 | `{GoodsCode}-img_{NN}.jpg` |
| 인트로 | `_intro_{tmpl}_{N}.jpg` | `{GoodsCode}-i_{tmpl}_{N}.jpg` |

**추가 구현:**
- `rename_map.json` 자동 저장 (`_renamed/` 폴더)
- 인트로 정규식 패턴 정확화 (`_intro_([A-E])_(\d+)` 추출)
- 원본 파일 절대 수정/삭제 금지 — `shutil.copy2()` 복사

### Phase 2: CDN 업로드 (`app/workers/image_uploader.py`)

- **dry_run=True 또는 DO_SPACES_KEY 미설정 시**: 실제 업로드 없이 URL 목록 시뮬레이션 반환
- **실업로드**: boto3 S3 호환, nyc3.digitaloceanspaces.com, `img/{YYYYMM}/{파일명}` 경로
- 반환값에 `cdn_dry_run: bool` 추가로 dry-run 여부 명시

### Phase 3: DB 등록 (`app/workers/image_uploader.py`)

- **db_mock=True 시**: 실제 DB 쿼리 없이 `db_updated=True` 반환
- **실등록**: `goods_detail` 테이블 `GoodsSortImg1~4`, `GoodsEtc60~74` 업데이트
- 반환값에 `db_mock: bool` 추가로 mock 여부 명시

### FastAPI 엔드포인트 (`app/api/deploy_router.py`)

```
POST /api/deploy/run    — 리네임 + 업로드 + DB 등록 (cdn_dry_run, db_mock 파라미터)
GET  /api/deploy/status/{job_id} — 작업 상태 조회
```

---

## 3. 테스트 결과

| TC | 테스트명 | 결과 |
|---|---|---|
| TC-01 | rename_map.json 저장 검증 | ✅ PASS |
| TC-02 | 인트로 파일명 패턴 변환 검증 | ✅ PASS |
| TC-03 | CDN dry-run 모드 검증 | ✅ PASS |
| TC-04 | DB mock 모드 검증 | ✅ PASS |
| TC-05 | 전체 파이프라인 dry-run 통합 테스트 | ✅ PASS |

**pytest 결과**: 17 passed, 0 failed

---

## 4. 사전 스캔 결과

| 항목 | 결과 |
|---|---|
| DO_SPACES_KEY | 미설정 → dry-run 자동 전환 |
| DB_114_PASS | 미설정 → mock 모드 권장 |
| Docker 내부 경로 | `/data/processed/{코디}/_renamed/` |

---

## 5. CEO 승인 필요 체크포인트

| # | 항목 | 현재 상태 |
|---|---|---|
| #1 | CDN 실업로드 | **CEO 승인 필수** (현재 dry-run) |
| #2 | 실상품 DB UPDATE | **CEO 승인 필수** (현재 mock) |

---

## 6. 완료 조건 체크

- [x] 리네임 엔진 실구현 동작
- [x] CDN 모듈 구현 (dry-run 포함)
- [x] DB 등록 모듈 구현 (mock 포함)
- [x] pytest 5케이스+ PASS (17 PASS)
- [x] 보고서 push → GitHub HTTP 200
- [ ] HANDOVER.md 업데이트 (진행 중)

---

## 7. 저장 정보 블록

```
커밋: fdd521e
브랜치: main
리포: newtalk-image-auto (private)
보고서: project-docs/nas-image/reports/CUR-NAS-P4E-DEPLOY-001-20260302.md
HTTP: 200
```

---

## 8. 보안 스캔

- `.env` / API 키 하드코딩 없음 ✅
- DO_SPACES_KEY/SECRET: 환경변수로만 로드 ✅
- DB 비밀번호: 환경변수로만 로드 ✅
