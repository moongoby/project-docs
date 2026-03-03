# CUR-NAS-P4C-RETOUCH-001-20260303

**작성일**: 2026-03-03 KST  
**작업자**: CURSOR-NAS #4  
**Task ID**: P4-C-RETOUCH  
**커밋**: `e4c996a`  
**HTTP**: 200

---

## 1. 작업 개요

P4-B 톤보정 결과물(`_toned/`)에 대해 MediaPipe Pose + Face Mesh 기반 체형/피부 AI 보정.  
인체 미검출 시 원본 복사 + `all_skipped=true` fallback, 모든 결과에 sidecar 메타데이터 JSON 생성.

---

## 2. 구현 내용

### 체형/피부 보정 엔진 (`app/workers/body_retoucher.py`)

| 항목 | 기법 | 제한 |
|---|---|---|
| 허리 슬리밍 | Gaussian 가중 워핑 (cv2.remap) | 10% |
| 어깨 볼륨 | Gaussian 가중 워핑 | 10% |
| 다리 길이 | 하체 영역 세로 스트레치 | 10% |
| 턱선 V라인 | Face Mesh jawline → 워핑 | 10% |
| 피부톤 균일화 | LAB L채널 정규화 | 10% |
| 문신 삭제 | HSV 마스크 + cv2.inpaint | ON/OFF |

### 파일명 및 경로

| 항목 | 내용 |
|---|---|
| 입력 | `/data/processed/{코디}/_toned/` |
| 출력 | `/data/processed/{코디}/_retouched/` |
| 보정 이미지 | `{원본stem}_retouched.jpg` |
| 메타데이터 | `{원본stem}_retouch_meta.json` |
| Fallback | 인체 미검출 → 원본 복사 + `all_skipped: true` |
| 프리셋 경로 | `/data/config/retouch_presets.json` |

### FastAPI 엔드포인트 (`app/api/retouch_router.py`)

```
POST /api/v1/retouch                    — 단건 보정 (동기)
POST /api/v1/retouch/batch              — 배치 보정
GET  /api/v1/retouch/presets            — 프리셋 목록 조회
PUT  /api/v1/retouch/presets/{preset_id} — 프리셋 수정 (범위 검증)
```

---

## 3. 테스트 결과

| TC | 테스트명 | 결과 |
|---|---|---|
| TC-01 | 전신 감지 → _retouched.jpg 생성 확인 | ✅ PASS |
| TC-02 | 인체 미검출 → 원본 복사 + all_skipped=True + meta JSON | ✅ PASS |
| TC-03 | retouch_meta.json sidecar 내용 확인 | ✅ PASS |
| TC-04 | 보정 강도 clamp 10% 이내 검증 | ✅ PASS |
| TC-05 | 빈 폴더 graceful 처리 | ✅ PASS |

**pytest 결과**: 13 passed, 0 failed

---

## 4. 완료 조건 체크

- [x] 체형 보정 5개 항목 (허리/어깨/다리/V라인/피부톤)
- [x] 피부 보정 2개 항목 (문신삭제/피부톤균일화)
- [x] 모델별 프리셋 시스템 (`/data/config/retouch_presets.json`)
- [x] 모든 값 ±10% clamp 강제 (MAX_SHIFT_RATIO = 0.10)
- [x] 메타데이터 JSON sidecar (`_retouch_meta.json`)
- [x] FastAPI 4개 엔드포인트 (/api/v1/retouch 경로 표준화)
- [x] 인체 미검출 fallback (원본 복사 + all_skipped)
- [x] pytest 5케이스+ PASS (13 PASS)
- [x] 보고서 push → GitHub HTTP 200
- [ ] HANDOVER.md 업데이트 (진행 중)

---

## 5. 저장 정보 블록

```
커밋: e4c996a
브랜치: main
리포: newtalk-image-auto (private)
보고서: project-docs/nas-image/reports/CUR-NAS-P4C-RETOUCH-001-20260303.md
HTTP: 200
```

---

## 6. 보안 스캔

- `.env` / API 키 하드코딩 없음 ✅
- Docker 내부 경로(`/data/...`)만 사용 ✅
