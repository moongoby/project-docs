# CUR-NASIMG-FEATURE-002-20260225

**제목:** P2 라벨감지 + OCR + 코디 자동분류 워커  
**작성일시:** 2026-02-25 KST  
**작업 유형:** FEATURE (P2)  
**목적:** 촬영자 homes 업로드 사진을 라벨 감지·상품코드 OCR → 코디 폴더 매칭 → ★제품사진 코디 폴더로 복사(원본 보호)

---

## 1. 개요

- **배경:** 촬영자 3명(송안나, 어요나, 정다연)이 NAS `/volume1/homes/{촬영자명}/`에 업로드한 사진 중, 행거링 라벨 촬영 → 모델사진 연속 촬영 흐름을 자동 인식하여 P1에서 생성된 코디 폴더로 분류.
- **수단:** Gemini OCR(라벨 판별·상품코드 추출), 116 DB(cody_product_msg/cody_msg) 코디 매칭, EXIF 시간순 정렬 후 복사만 수행(원본 삭제/이동 금지).

---

## 2. 모듈 구조

| 모듈 | 경로 | 기능 |
|------|------|------|
| label_detector | app/workers/label_detector.py | is_label_image(), extract_product_code() — Gemini 호출, 정규식 검증 |
| cody_matcher | app/workers/cody_matcher.py | get_cody_by_product_code(), find_shooting_folder(), find_cody_folder() |
| photo_sorter | app/workers/photo_sorter.py | sort_photos_for_shooting() — homes 수집·EXIF 정렬·라벨/사진 분기·복사 |
| folder_poller | app/workers/folder_poller.py | process_sort_pending_requests(), run_sort_poll_cycle() — sort_status 폴링 |

---

## 3. 설정 (app/config.py, .env)

| 항목 | 환경변수 | 기본값 | 비고 |
|------|----------|--------|------|
| 촬영자 루트 | HOMES_ROOT | /data/homes | Docker: /volume1/homes 마운트 |
| Gemini API 키 | GEMINI_API_KEY | (없음) | .env에만 저장, 커밋 금지 |
| Gemini 모델 | GEMINI_MODEL | gemini-2.0-flash | |
| 라벨 신뢰도 | LABEL_DETECT_CONFIDENCE | 0.8 | (현재 코드에서 aspect 필터만 사용) |
| 분류 폴링 간격 | PHOTO_SORT_INTERVAL | 300 | 5분 |

---

## 4. API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /api/sort/status/{shooting_id} | 분류 상태 조회 (status, sort_status) |
| GET | /api/sort/results/{shooting_id} | 분류 결과 상세 (코디별 사진 수) |
| POST | /api/sort/trigger/{shooting_id} | 수동 분류 트리거 |

---

## 5. Docker 변경사항

- **docker-compose.yml**
  - 볼륨 추가: `/volume1/homes:/data/homes:ro` (읽기 전용 — 원본 보호)
  - 기존 `/volume1/★제품사진:/data/photos:rw` 유지

---

## 6. 테스트 결과

- **test_label_detector.py:** 프롬프트 구성, 상품코드 정규식, 괄호 제거 로직 — 7 passed
- **test_cody_matcher.py:** get_cody_by_product_code(DB 컬럼 매핑), find_shooting_folder, find_cody_folder — 8 passed
- **test_photo_sorter.py:** 반환 구조, 다른 날짜 무시, HEIC 확장자, 원본 삭제 안 함, @eaDir 무시 — 6 passed  

**총 21 passed** (2026-02-25, P2 컬럼명 반영 후)

---

## 7. 의존성 및 완료 사항

- **114 Cursor DB 조사 반영 (2026-02-25)**
  - nas_folder_request: `sort_status`, `md_name` 컬럼 사용 확정 — 폴링에서 이미 반영됨.
  - cody_matcher.py: 실제 DB 컬럼명 반영 완료.
    - cody_msg: `codyCode`, `codyNumber`, `shooting_id`
    - cody_product_msg: `codyCode`, `codyProdCode`, `codyProdName`, `shooting_id` (cody_id 없음) — ✅ codyProdCode 확정
    - 조인: `cody_msg`와 `cody_product_msg`는 `codyCode + shooting_id`로 조인 — ✅ 조인 키 확정
  - get_cody_by_product_code 쿼리: `WHERE cp.codyProdCode = %s AND c.shooting_id = %s` (정확 일치)
- **md_name fallback:** nas_folder_request.md_name이 NULL이면 contents_msg.MDName으로 DB 조회 후 homes/{md_name}/ 사용.
- **sort_status:** status='completed' AND sort_status='pending'만 분류 대상. 시작 시 'processing', 완료 시 'completed', 에러 시 'failed'.
- **pip-cache:** `pip download google-generativeai -d pip-cache/` (NAS 오프라인 빌드용). 오프라인이면 별도 다운로드 필요 — TODO: requirements.txt에 주석 반영.

---

## 8. 보고서 위치

- **Private:** https://github.com/moongoby/newtalk-image-auto/blob/main/docs/reports/CUR-NASIMG-FEATURE-002-20260225.md
- **Public:** https://github.com/moongoby/project-docs/blob/master/nas-image/reports/CUR-NASIMG-FEATURE-002-20260225.md

---

*한국시간(KST) 기준 기록. DB 비밀번호/GEMINI_API_KEY 문서·코드 기재 금지.*
