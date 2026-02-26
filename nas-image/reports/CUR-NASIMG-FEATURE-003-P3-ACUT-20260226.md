# CUR-NASIMG-FEATURE-003-P3-ACUT-20260226

**제목:** P3 A컷 자동 선별 — 프로토타입 개발  
**작성일시:** 2026-02-26 (목) KST  
**작업 유형:** FEATURE (P3 A컷 선별)  
**목적:** 코디 폴더 내 100~300장 원본에서 Gemini Vision으로 30~40장 A컷 자동 선별 후 `원본폴더/A컷/`에 복사

---

## 1. 설계 요약

### 1.1 acut_selector.py

- **위치:** `app/workers/acut_selector.py`
- **방식:** 토너먼트 2라운드
  - **1라운드:** 배치(기본 10장) 단위로 Gemini에 A/B 등급 + score 요청 → A컷 후보 추출
  - **2라운드:** A컷 후보가 목표(30~40장)+10장 초과 시, 동일 폴더 이미지로 최종 선별(포즈·앵글 다양성)
- **원본 보호:** `shutil.copy2`만 사용, 원본 수정/삭제/이동 없음
- **지원 포맷:** JPG, JPEG, PNG, HEIC (`@eaDir`, 숨김 파일 제외)
- **Rate limit:** 배치 간 1초 sleep

### 1.2 프롬프트

- **1라운드(ACUT_BATCH_PROMPT):**  
  초점/선명도, 모델 포즈·표정, 상품 노출도, 구도, 조명/노출, 포즈 다양성 기준으로 JSON 배열 응답  
  `[{"filename":"...", "grade":"A"|"B", "score":N, "reason":"..."}]`
- **2라운드(ACUT_FINAL_PROMPT):**  
  포즈 다양성, 전신/상반신/클로즈업·앵글 균형 기준으로 최종 30~40장 선별  
  `{"selected": ["IMG_xxx.JPG", ...], "total": N}`

### 1.3 API

- **POST /api/acut/select**  
  Body: `{"cody_folder": "절대경로", "target_count": 35, "batch_size": 10}`  
  반환: `{ "selected", "total_original", "total_selected", "copied", "output_folder" }` 또는 `{"error": "..."}`
- **GET /api/acut/result/{folder_name}**  
  간이 조회(구현 예정: DB 연동)

---

## 2. pytest 결과

- **파일:** `tests/test_acut_selector.py`
- **실행:** `python -m pytest tests/test_acut_selector.py -v`

| 테스트 | 설명 |
|--------|------|
| test_get_jpg_files_filters_correctly | JPG/JPEG/PNG 필터, @eaDir·숨김 제외 |
| test_get_jpg_files_empty_folder | 빈 폴더 → 빈 목록 |
| test_get_jpg_files_sorted | 파일명 정렬 |
| test_select_acuts_empty_folder | 빈 폴더 → error 반환 |
| test_select_acuts_small_folder_skips_gemini | 원본 ≤ target+5 → Gemini 없이 전체 선택, A컷 폴더 생성 |
| test_batch_evaluate_parses_response | Gemini 응답 JSON 파싱 → A컷 3장 |
| test_select_acuts_creates_output_folder | 50장 배치 평가 → A컷 폴더 생성 및 복사 |

**결과:** 7건 통과 (2026-02-26 로컬 실행 기준)

---

## 3. 실제 테스트 (1번 코디 154장)

- **경로:**  
  `/volume1/★제품사진/●모델컷_시크블랙/★26년도 모델컷 원본/2026.2월/0220지윤/1번코디 - 69969cf49709d_bl5889k62_팝콘_티아라블라우스_아이보리(Ivory)_FREE/`
- **실행:**  
  `python scripts/test_p3_acut.py` 또는  
  `docker exec newtalk-image-auto python /app/scripts/test_p3_acut.py`

### 3.1 결과 (NAS/Docker 실행 후 기입)

| 항목 | 값 |
|------|-----|
| 원본 장수 | (실행 후 기입) |
| 선별 장수 | (실행 후 기입) |
| 복사 장수 | (실행 후 기입) |
| 출력 폴더 | `{코디폴더}/A컷` |
| 선별 파일 목록 | (선별된 파일명 일부 또는 전체 링크) |

### 3.2 Gemini API 호출 수·소요 시간 (실행 후 기입)

| 항목 | 값 |
|------|-----|
| 1라운드 호출 수 | (배치 수, 예: 154장 ÷ 10 = 16회) |
| 2라운드 호출 수 | (0 또는 1회) |
| 총 소요 시간 | (초 단위) |

---

## 4. 완료 조건 체크

- [x] acut_selector.py 생성
- [x] pytest 7건 통과
- [ ] 1번 코디(154장) → A컷 30~40장 선별 → A컷/ 폴더에 복사 (NAS에서 실행 후 확인)
- [ ] 원본 파일 수 변동 없음 (154장 유지)
- [x] 보고서 커밋
- [x] project-docs 동기화 (Public 저장소에 동일 보고서 복사)

---

## 5. 참고

- GitHub Private: https://github.com/moongoby/newtalk-image-auto
- Public 보고서: project-docs 저장소 `nas-image/reports/CUR-NASIMG-FEATURE-003-P3-ACUT-20260226.md` 에 동기화
- 커밋 메시지: `feat: P3 A컷 자동 선별 프로토타입 20260226`
