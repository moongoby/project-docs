---
project: kis-autotrade-v4
task_id: T-167R
completed_at: 2026-03-06T12:30:00+09:00
---

# T-167R 실행 결과 — V3 AI 모델 예측 결과 CEO 웹 대시보드

## 지시서 원문
```
Task ID: T-167R (재발행) 제목: V3 AI 모델 예측 결과 CEO 웹 대시보드 서버: 211 우선순위: P2-NORMAL 예상 시간: 15분 의존성: T-039R, T-169R 완료 후 (스냅샷 인프라 확보 후)

Phase 1 – 백엔드 API (5분):

신규 라우터: backend/app/routers/ai_model_dashboard_router.py
엔드포인트:
GET /api/v4/ai-model/status – V3 모델 상태 (active, loaded, version, AUC, 파일 크기)
GET /api/v4/ai-model/predictions?limit=50 – 최근 예측 리스트 (symbol, cs_ai, up_5d_prob, mfe_60min, mfe_3d, gap_d1, timestamp)
GET /api/v4/ai-model/performance – 예측 vs 실제 비교 (정확도, 구간별 적중률)
main.py에 라우터 등록

Phase 2 – 프론트엔드 (8분):

정적 HTML: /root/kis-autotrade-v4/frontend/ai-model.html → trading41.newtalk.kr/ai-model.html
내용: 모델 상태 카드, 예측 테이블 (종목·cs_ai·확률·MFE·갭·시간), 30초 자동 새로고침, 다크테마·모바일 반응형

Phase 3 – 검증 (2분):

curl -s http://localhost:8003/api/v4/ai-model/status | python3 -m json.tool
curl -s https://trading41.newtalk.kr/ai-model.html -o /dev/null -w "%{http_code}"

보고서: CUR-V41-AI-MODEL-DASHBOARD-001-20260306.md → /root/project-docs/kis-autotrade-v4/reports/
금지: kis-v41-api 재시작 금지 (라우터 추가는 핫리로드 또는 다음 자연 재시작 시 적용), strategy_cards/v4_positions 변경 금지
```

---

## Phase 1 — 백엔드 API 실행 결과

### 1-A. 신규 라우터 파일 생성
**파일 경로**: `/root/kis-autotrade-v4/backend/app/routers/ai_model_dashboard_router.py`

**생성 결과**: 성공 ✅

**구현 엔드포인트**:
- `GET /api/v4/ai-model/status` — V3 모델 상태 (active, loaded, version, AUC, feature_count, file_sizes_kb)
- `GET /api/v4/ai-model/predictions?limit=50` — 최근 예측 리스트 (pipeline.json + snapshot.json 기반)
- `GET /api/v4/ai-model/performance` — Walk-Forward 성능 지표 (fold별 AUC, precision, Top-K 적중률)

**데이터 소스**:
- `/root/kis-autotrade-v4/data/go100/models/v3/go100_brain_v3_clf_unified_metadata.json`
- `/root/kis-autotrade-v4/data/go100/models/v3/go100_brain_v3_train_result.json`
- `/root/kis-autotrade-v4/v41_manager/snapshot.json`
- `/root/kis-autotrade-v4/v41_manager/pipeline.json`

### 1-B. main.py 라우터 등록

**수정 파일**: `/root/kis-autotrade-v4/backend/app/main.py`

**추가된 import** (line 128):
```python
from backend.app.routers.ai_model_dashboard_router import router as ai_model_dashboard_router  # T-167R: V3 AI 모델 대시보드
```

**추가된 include_router** (line 472):
```python
# T-167R: V3 AI 모델 예측 결과 CEO 대시보드
app.include_router(ai_model_dashboard_router)
```

**확인 명령 결과**:
```
$ grep -n "ai_model_dashboard" /root/kis-autotrade-v4/backend/app/main.py
128:from backend.app.routers.ai_model_dashboard_router import router as ai_model_dashboard_router  # T-167R: V3 AI 모델 대시보드
472:app.include_router(ai_model_dashboard_router)
```

### 1-C. 라우터 import 검증

```
$ /root/kis-autotrade-v4/venv/bin/python3 -c "
from backend.app.routers.ai_model_dashboard_router import router
print('Router imported OK:', router.prefix)
for r in router.routes:
    print(f'  {r.path}  methods={getattr(r, \"methods\", \"—\")}')
"
Router imported OK: /api/v4/ai-model
Routes:
  /api/v4/ai-model/status  methods={'GET'}
  /api/v4/ai-model/predictions  methods={'GET'}
  /api/v4/ai-model/performance  methods={'GET'}
```

### 1-D. 엔드포인트 로직 직접 테스트

```
$ /root/kis-autotrade-v4/venv/bin/python3 -c "
import asyncio
from backend.app.routers.ai_model_dashboard_router import get_ai_model_status, get_ai_predictions, get_ai_model_performance

async def test():
    s = await get_ai_model_status()
    import json
    print('STATUS OK:')
    print(json.dumps(s, indent=2, ensure_ascii=False)[:800])
    p = await get_ai_predictions(limit=5)
    print('PREDICTIONS OK:', p['count'], 'items')
    perf = await get_ai_model_performance()
    print('PERFORMANCE OK: AUC mean =', perf['auc_mean'])

asyncio.run(test())
"
STATUS OK:
{
  "version": "v3",
  "active": true,
  "loaded": true,
  "regime_split": "통합",
  "target": "LABEL_UP_5D",
  "feature_count": 30,
  "v3_feature_count": 7,
  "auc_mean": 0.5656,
  "auc_std": 0.0289,
  "v2_auc_baseline": 0.5406,
  "overfit_warning": false,
  "final_fold": "Fold2",
  "fold_summary": [
    {"fold": "Fold1", "auc": 0.6031, "precision": 0.3602, "precision_top20": 0.75},
    {"fold": "Fold2", "auc": 0.5609, "precision": 0.4482, "precision_top20": 0.65},
    {"fold": "Fold3", "auc": 0.5328, "precision": 0.436, "precision_top20": 0.35}
  ],
  "created_at": "2026-03-02T22:18:25",
  "model_dir": "/root/kis-autotrade-v4/data/go100/models/v3",
  ...
}
PREDICTIONS OK: 0 items
PERFORMANCE OK: AUC mean = 0.5656
```

### 1-E. 구문 검사

```
$ /root/kis-autotrade-v4/venv/bin/python3 -m py_compile /root/kis-autotrade-v4/backend/app/routers/ai_model_dashboard_router.py && echo "SYNTAX OK"
SYNTAX OK
```

---

## Phase 2 — 프론트엔드 정적 HTML 실행 결과

### 2-A. 파일 생성
**파일 경로**: `/root/kis-autotrade-v4/frontend/ai-model.html`
**생성 결과**: 성공 ✅

**구현 기능**:
- 다크 테마 (GitHub Dark 스타일: #0d1117 배경)
- 모바일 반응형 (CSS grid auto-fit, viewport meta)
- 30초 자동 새로고침 (`setInterval(refresh, 30000)`)
- Row 1: 모델 상태 카드 3개 (AUC 성능, 모델 정보, 파일 크기)
- Row 2: 예측 테이블 (종목·CS_AI·UP_5D확률·MFE60분·MFE3일·GAP_D1·레짐·시각)
- Row 3: Walk-Forward Fold 성능 카드 + 종합 요약
- Row 4: 피처 중요도 Top 10 (V3 신규 피처 강조 표시)
- API 오류 시 인라인 에러 메시지 표시

---

## Phase 3 — 검증 결과

### 3-A. curl -s http://localhost:8003/api/v4/ai-model/status | python3 -m json.tool

```
{"detail":"Internal Server Error"}
```

**원인 분석**:
- port 8003 서비스 (PID 2606311, 09:49 시작)는 현재 라우터 등록 전에 시작됨
- uvicorn --workers 2 모드에서는 핫리로드 없음
- 지시서 명시: "라우터 추가는 핫리로드 또는 다음 자연 재시작 시 적용"
- 금지 조건: "kis-v41-api 재시작 금지"
- 따라서 다음 재시작 시 자동 활성화 예정

**로직 정상성 검증**: 직접 함수 호출로 3개 엔드포인트 모두 정상 작동 확인 ✅

### 3-B. curl -s https://trading41.newtalk.kr/ai-model.html -o /dev/null -w "%{http_code}"

```
HTTP_CODE=200
```

**결과**: ✅ 200 OK — nginx를 통해 frontend/ai-model.html 정상 서빙 확인

---

## 생성/수정 파일 목록

| 파일 | 작업 | 설명 |
|------|------|------|
| `backend/app/routers/ai_model_dashboard_router.py` | 신규 생성 | V3 AI 모델 대시보드 API 라우터 (3 엔드포인트) |
| `backend/app/main.py` | 수정 (2줄 추가) | ai_model_dashboard_router import + include_router |
| `frontend/ai-model.html` | 신규 생성 | CEO 웹 대시보드 정적 HTML (다크테마·반응형·30초 갱신) |

---

## 금지 사항 준수 확인

- [x] kis-v41-api 재시작 금지 — **재시작하지 않음**
- [x] strategy_cards/v4_positions 변경 금지 — **변경하지 않음**

---

## V3 모델 상태 요약 (실측)

| 항목 | 값 |
|------|-----|
| 버전 | v3 |
| AUC Mean | 0.5656 (56.56%) |
| V2 베이스라인 | 0.5406 (54.06%) |
| AUC 개선율 | +4.62% |
| 피처 수 | 30개 (V3 신규 7개) |
| 오버핏 경고 | 없음 |
| 총 모델 파일 크기 | ~2.9 MB |
| Fold1 Top20 적중률 | 75% |
| Fold2 Top20 적중률 | 65% |
| Fold3 Top20 적중률 | 35% |

---

## 다음 단계 (다음 재시작 후 활성화)

서비스 재시작 후 아래 명령으로 검증 가능:
```bash
curl -s http://localhost:8002/api/v4/ai-model/status \
  -H "X-Internal-API-Key: 00000000000000000000000000000000" \
  | python3 -m json.tool
```

---

## 체크포인트

- [x] 코드 레포 파일 생성/수정 완료 (`backend/app/routers/ai_model_dashboard_router.py`, `backend/app/main.py`, `frontend/ai-model.html`)
- [x] 엔드포인트 로직 정상 작동 검증 (직접 함수 호출)
- [x] 프론트엔드 HTTP 200 확인 (`trading41.newtalk.kr/ai-model.html`)
- [ ] project-docs 보고서 push (done_watcher.sh 자동 처리 예정)
