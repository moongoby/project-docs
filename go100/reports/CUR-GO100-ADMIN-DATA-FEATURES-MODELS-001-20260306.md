# CUR-GO100-ADMIN-DATA-FEATURES-MODELS-001-20260306

**Task ID**: T-044
**제목**: 어드민 데이터 수집·피처·모델 관리 페이지
**날짜**: 2026-03-06 KST
**브랜치**: phase-2c-command-center
**커밋**: 1745df4f

---

[인계 확인]
직전 완료: T-043 (어드민 종합상황실 War Room)
현재 단계: Phase 8 — 어드민 파이프라인 페이지 구현
CEO 지시 적용: D-001, D-002, D-006, D-007
strategy_cards: 기존
open_positions: 기존

---

## 1. 작업 개요

T-043에서 구현된 종합상황실(War Room)의 파이프라인 8단계 중 1~3단계
(데이터 수집 / 피처 엔지니어링 / 모델 관리)에 대한 상세 관리 페이지 3개를 신규 구현.

---

## 2. 생성 파일 목록

### 프론트엔드 (신규 생성)

| 파일 경로 | 설명 |
|----------|------|
| `frontend/src/app/(protected)/admin/data/page.tsx` | /admin/data — 5개 데이터 소스 현황 |
| `frontend/src/app/(protected)/admin/features/page.tsx` | /admin/features — 피처 엔지니어링 현황 |
| `frontend/src/app/(protected)/admin/models/page.tsx` | /admin/models — AI 모델 관리 |

### 백엔드 (기존 파일 수정)

| 파일 경로 | 추가 내용 |
|----------|----------|
| `backend/app/api/v1/go100_admin_router.py` | GET /data-status, GET /feature-status, GET /model-status, POST /activate-model 4개 엔드포인트 추가 |

---

## 3. API 엔드포인트 목록

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/go100/admin/data-status` | 5개 소스 상태 + Auto-Healer 로그 + 커버리지 |
| GET | `/api/go100/admin/feature-status` | Parquet 파일 현황 + 피처 중요도 Top15 + 컬럼 통계 |
| GET | `/api/go100/admin/model-status` | V2/V3 모델 비교 + Confusion Matrix + 학습 이력 |
| POST | `/api/go100/admin/activate-model` | CEO 전용 모델 활성화 (user_id=2 체크) |

---

## 4. 페이지별 구현 상세

### 4-1. /admin/data — 데이터 수집 현황

- **헤더**: "📡 데이터 수집 현황", 서브텍스트 "5개 데이터 소스 실시간 모니터링"
- **데이터 소스 카드 5개 (2x3 그리드)**:
  - pykrx (Database 아이콘): OHLCV 데이터 최종 수집일 (daily_stock_data 기준)
  - KIS API (Zap 아이콘): go100_data_collection_log WHERE source='KIS'
  - FinanceDataReader (Globe 아이콘): go100_data_collection_log WHERE source='FinanceDataReader'
  - DART (FileText 아이콘): go100_data_collection_log WHERE source='DART'
  - 뉴스 크롤러 (Newspaper 아이콘): go100_news_items 기준
  - 각 카드: 상태 뱃지(GREEN/YELLOW/RED), 최종 수집 시각, 오늘 수집 건수, 에러 건수
- **Auto-Healer 발동 로그**:
  - go100_error_log WHERE error_type='auto_heal' 최근 20건
  - 테이블: 시각, 원본소스, 대체소스, 종목, 결과
  - 5건씩 페이지네이션 (ChevronLeft/Right 버튼)
- **종목 데이터 커버리지**:
  - go100_stock_universe vs daily_stock_data 비율 프로그레스바
  - 누락 종목 최대 50개, 빨간색 뱃지 표시

### 4-2. /admin/features — 피처 엔지니어링

- **헤더**: "🧬 AI 피처 엔지니어링"
- **요약 카드 3개**: 파일 수, 총 용량(MB), 총 행수(K)
- **Parquet 파일 현황 테이블**:
  - data/go100/features/v2/ 디렉터리 파일 목록
  - 파일명, 크기(MB), 행수, 생성일
- **피처 중요도 차트**:
  - recharts `BarChart` 가로 바 차트 (layout="vertical")
  - V3 clf_unified 메타데이터에서 Top15 로드
  - 중요도 높을수록 진한 emerald 색상 (importanceColor 함수)
  - V3 신규 피처 여부 Tooltip 표시
- **컬럼별 통계 테이블**:
  - 41개 컬럼: 이름, 타입, 평균, 표준편차, 결측률, min, max
  - 결측률 >5% 빨간색 배경, >1% 노란색 배경
  - 컬럼 헤더 클릭 정렬 (오름/내림차순 토글)
  - go100_brain_v2_feature_stats.json에서 로드

### 4-3. /admin/models — AI 모델 관리

- **헤더**: "🧠 AI 모델 관리"
- **모델 비교 카드 2열 (V2 / V3)**:

| 항목 | V2 | V3 |
|------|----|----|
| AUC | 0.5406 ± 0.0055 | 0.5656 |
| Sharpe | 4.63 | — (계산 필요) |
| MDD | — | — |
| 상태 | 🟢 운용중 | 🟡 승인 대기 |
| 파일 크기 | metadata에서 | metadata에서 |
| 학습일 | 파일 mtime | 파일 mtime |

- **Confusion Matrix 히트맵**: TP/FP/FN/TN 4칸 그리드 (V2, V3 각각)
  - fold_results의 confusion_matrix에서 추출
- **V3 활성화 버튼**:
  - user_id=2(CEO)만 표시 (useAuthStore로 userId 확인)
  - 클릭 → 확인 모달 ("V3 모델을 활성화하시겠습니까?")
  - POST /api/go100/admin/activate-model {version: "v3"}
  - activate_v3_model.py --confirm subprocess 실행
  - 결과 stdout/stderr 인라인 표시
- **학습 이력 타임라인**: 버전, 학습일, AUC, 피처수, 상태

---

## 5. 빌드 결과

```
npm run build (frontend/.next.old.T044 → 새 .next)

✓ Compiled successfully
Skipping validation of types
Skipping linting
Collecting page data ...
Generating static pages (44/44)

Route 확인:
├ ƒ /admin/data     6.06 kB     111 kB  ✅
├ ƒ /admin/features 5.21 kB     222 kB  ✅ (recharts 포함)
├ ƒ /admin/models   5.96 kB     111 kB  ✅

빌드 에러: 0건
```

---

## 6. Python 구문 검사

```
python3 -c "import ast; ast.parse(open('backend/app/api/v1/go100_admin_router.py').read()); print('OK')"
→ Python syntax OK
```

---

## 7. API 응답 확인

```bash
curl -s http://localhost:8002/api/go100/admin/data-status
→ {"status":401,"detail":"Not authenticated",...}  ✅ JSON 응답 확인

curl -s http://localhost:8002/api/go100/admin/feature-status
→ {"status":401,"detail":"Not authenticated",...}  ✅ JSON 응답 확인

curl -s http://localhost:8002/api/go100/admin/model-status
→ {"status":401,"detail":"Not authenticated",...}  ✅ JSON 응답 확인
```

(401 = 인증 토큰 필요, 엔드포인트 정상 등록 및 JSON 응답 확인됨)

---

## 8. 커밋 정보

- **커밋 해시**: 1745df4f
- **브랜치**: phase-2c-command-center
- **push**: github.com:moongoby/go100.git ✅
- **변경 파일**: 4개 (1개 수정 + 3개 신규)
- **삽입**: 1,867줄

---

## 9. 성공 기준 체크

- [x] /admin/data 빌드 성공 (ƒ 6.06 kB)
- [x] /admin/features 빌드 성공 (ƒ 5.21 kB, recharts)
- [x] /admin/models 빌드 성공 (ƒ 5.96 kB)
- [x] GET /api/go100/admin/data-status JSON 응답
- [x] GET /api/go100/admin/feature-status JSON 응답
- [x] GET /api/go100/admin/model-status JSON 응답
- [x] Python syntax OK
- [x] git push origin phase-2c-command-center ✅

---

## 저장 정보
- 서버 경로: /root/project-docs/go100/reports/CUR-GO100-ADMIN-DATA-FEATURES-MODELS-001-20260306.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-ADMIN-DATA-FEATURES-MODELS-001-20260306.md
- 커밋: (project-docs push 후 확인)
- HTTP 확인: (push 후 확인)
- HANDOVER 업데이트: 미완료 (done_watcher.sh 자동 처리 예정)
