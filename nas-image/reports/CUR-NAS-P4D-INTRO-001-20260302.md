# CUR-NAS-P4D-INTRO-001-20260302

**작성일시:** 2026-03-02 21:40 KST  
**Task ID:** P4-D-INTRO  
**작업 유형:** FEATURE  
**목적:** A컷 모델 사진 → 인트로 이미지 AI 생성 모듈 (템플릿 5종, Gemini 카피 연동, FastAPI 엔드포인트)

---

## 1. 사전 스캔 결과

| 항목 | 결과 |
|------|------|
| Docker 한글 폰트 | `fonts/` 디렉토리 비어있음 → **Dockerfile에 `fonts-nanum` 추가** |
| 기존 Gemini API 코드 | `acut_selector.py`에 `google.generativeai` 패턴 확인 → 동일 패턴 재사용 |
| requirements.txt | `Pillow>=10.0.0`, `pillow-heif>=0.16.0`, `google-generativeai>=0.8.0` 이미 포함 |
| `.env` GEMINI_API_KEY | `AIzaSyCX6kqDQ7bB_X9xEpjiPla_Ifc0ZgDXiKo` 등록 확인 |
| 기존 구현 현황 | `intro_generator.py` + `intro_router.py` 스켈레톤 존재 → **directive 스펙에 맞게 업데이트** |

---

## 2. 구현 내용

### 2-1. `app/workers/intro_generator.py`

**추가/변경 사항:**
- `_generate_catchphrases()`: **PROHIBITED_CONTENT fallback** 추가 (`blocked` 키워드 감지 → 기본 5개 문구 반환)
- `_get_font()`: 번들 폰트 없을 때 시스템 나눔폰트(`/usr/share/fonts/truetype/nanum/`) → PIL 기본폰트 순 fallback
- `_scan_acut_images()`: `/data/photos/{코디폴더}/_acut_v2/` 이미지 스캔 함수 추가
- `generate_intro()`: `templates` 파라미터 추가 (빈 리스트 = 자동선택)
- `generate_intro_from_folder()`: 코디폴더 기반 스캔 + 생성 함수 추가
- `batch_generate_intro()`: 복수 코디 배치 함수 추가 (개별 실패 무시 후 계속 진행)

**템플릿 5종 구현 완료:**

| 코드 | 이름 | 구성 | 출력 해상도 |
|------|------|------|------------|
| A | 캐치프레이즈형 | 배경 모델사진 + AI 카피 오버레이 | 860×1200px |
| B | 포인트 설명형 | 모델컷 + POINT 1~3 텍스트 박스 | 860×1600px |
| C | 멀티 앵글형 | 3분할 그리드 레이아웃 | 860×900px |
| D | 리뷰 포커스형 | 베이지 배경 + 별점 + 리뷰 문구 | 860×1200px |
| E | 코디 제안형 | 전신컷 그리드 + 스타일링 문구 | 860×1400px |

### 2-2. `app/api/intro_router.py`

**엔드포인트 업데이트 (prefix: `/api/v1/intro`):**

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/api/v1/intro` | 코디폴더 기반 단건 인트로 생성 (BackgroundTask) |
| `POST` | `/api/v1/intro/batch` | 복수 코디 배치 인트로 생성 |
| `POST` | `/api/v1/intro/generate` | 이미지 직접 지정 방식 (기존 호환) |
| `GET` | `/api/v1/intro/templates` | 템플릿 목록 조회 |
| `GET` | `/api/v1/intro/status/{job_id}` | 작업 상태 조회 |

### 2-3. `Dockerfile`

- `fonts-nanum` + `fontconfig` apt 패키지 추가
- Docker 빌드 시 한글 폰트 자동 설치 (`fc-cache -fv`)

---

## 3. 입출력 경로

```
입력: /data/photos/{코디폴더}/_acut_v2/     (P3 A컷 결과)
출력: /data/processed/{goods_code}/_intro/   (인트로 이미지)
파일명: {goods_code}-i_{template}_1.jpg
예시: bl5889k62-i_A_1.jpg, bl5889k62-i_C_1.jpg
```

---

## 4. pytest 결과

```
============================= test session starts =============================
tests/test_intro_generator.py — 18 PASSED in 12.53s
```

### 5케이스 필수 확인

| # | 케이스 | 클래스 | 결과 |
|---|--------|--------|------|
| TC-01 | 템플릿 C 단건 생성 (이미지 합성 정상 확인) | `TestTemplateCGeneration` | ✅ PASS |
| TC-02 | 템플릿 A 단건 생성 (Gemini 카피 + 합성) | `TestTemplateAWithGemini` | ✅ PASS |
| TC-03 | Gemini PROHIBITED_CONTENT fallback 동작 | `TestGeminiProhibitedContentFallback` | ✅ PASS |
| TC-04 | 빈 A컷 폴더 예외 처리 | `TestEmptyAcutFolder` | ✅ PASS |
| TC-05 | 배치 모드 복수 코디 생성 | `TestBatchMode` | ✅ PASS |

---

## 5. 완료 조건 체크

- [x] 최소 템플릿 A + C 정상 생성 동작
- [x] pytest 5케이스 전체 PASS (실제 18케이스)
- [x] 테스트 코디 1개 이상 인트로 결과물 생성 확인
- [x] PROHIBITED_CONTENT fallback 구현
- [x] 코디폴더 자동 스캔 (`_acut_v2/`) 구현
- [x] 배치 엔드포인트 구현
- [x] Dockerfile 한글 폰트 추가
- [ ] 보고서 push → GitHub HTTP 200 확인
- [ ] HANDOVER.md 섹션 3 상태 업데이트

---

## 6. 주의사항 / 다음 단계

- `google-generativeai` deprecated 경고 → 향후 `google-genai`로 마이그레이션 필요 (현재 동작에는 영향 없음)
- 실제 NAS Docker에서 `fonts-nanum` apt 설치 필요 → **Docker rebuild 필요**
- 인트로 품질은 CEO 검수 대상 (D-005) — 실제 코디 적용 후 스크린샷 확인 권장

---

## 저장 정보

- 서버 경로: `z:\newtalk-image-auto\docs\reports\CUR-NAS-P4D-INTRO-001-20260302.md`
- GitHub: https://github.com/moongoby/project-docs/blob/master/nas-image/reports/CUR-NAS-P4D-INTRO-001-20260302.md
- 커밋: (push 후 기입)
- HTTP 확인: (push 후 기입)
- HANDOVER 업데이트: 진행 중
- 완료일시: 2026-03-02 21:40 KST
