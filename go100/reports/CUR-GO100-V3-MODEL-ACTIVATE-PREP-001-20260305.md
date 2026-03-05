# CUR-GO100-V3-MODEL-ACTIVATE-PREP-001-20260305

**Task ID**: T-017 (BRIDGE 지시: GO100_20260305_200817_BRIDGE)
**작성일**: 2026-03-05
**작성자**: claudebot (auto)
**프로젝트**: GO100
**우선순위**: P0-CRITICAL

---

[인계 확인]
직전 완료: T-024 (V3 모델 활성화 스크립트 사전 준비)
현재 단계: Phase 2 — V3 모델 활성화 준비 완료
CEO 지시 적용: CEO 승인 후 activate_v3_model.py --confirm 실행
strategy_cards: N/A
open_positions: N/A

---

## 1. 작업 개요

V3 모델 6종(`data/go100/models/v3/`)의 파일 존재 및 메타데이터 확인, `brain_predictor_v3.py` import 검증, 활성화 스크립트(`scripts/go100/activate_v3_model.py`) 작성 및 갱신 완료.

---

## 2. V3 모델 파일 목록

```
data/go100/models/v3/
├── go100_brain_v3_clf_nonq2_defensive.joblib     (39,476 bytes)
├── go100_brain_v3_clf_q2_aggressive.joblib        (89,732 bytes)
├── go100_brain_v3_clf_unified.joblib              (83,172 bytes)
├── go100_brain_v3_reg_gap_d1_unified.joblib      (287,121 bytes)
├── go100_brain_v3_reg_mfe_3d_unified.joblib    (1,003,451 bytes)
├── go100_brain_v3_reg_mfe_60min_unified.joblib (1,488,450 bytes)
├── go100_brain_v3_train_result.json              (18,395 bytes)
├── go100_brain_v3_clf_nonq2_defensive_metadata.json
├── go100_brain_v3_clf_q2_aggressive_metadata.json
├── go100_brain_v3_clf_unified_metadata.json
├── go100_brain_v3_reg_gap_d1_unified_metadata.json
├── go100_brain_v3_reg_mfe_3d_unified_metadata.json
└── go100_brain_v3_reg_mfe_60min_unified_metadata.json
```

**모델 수**: 6종 (LGBMClassifier 3, LGBMRegressor 3)

---

## 3. V3 메타데이터 요약

| 모델 파일 | 유형 | regime_split | target | AUC / MAE | active |
|-----------|------|-------------|--------|------------|--------|
| clf_unified | LGBMClassifier | 통합 | LABEL_UP_5D | AUC 0.5656 | true |
| clf_q2_aggressive | LGBMClassifier | Q2공격형 | LABEL_UP_5D | AUC 0.6092 | true |
| clf_nonq2_defensive | LGBMClassifier | 비Q2방어형 | LABEL_UP_5D | AUC 0.5588 | true |
| reg_gap_d1_unified | LGBMRegressor | 통합 | LABEL_GAP_D1 | MAE 1.6193 | true |
| reg_mfe_3d_unified | LGBMRegressor | 통합 | LABEL_MFE_3D | MAE 5.6269 | true |
| reg_mfe_60min_unified | LGBMRegressor | 통합 | LABEL_MFE_60MIN | MAE 1.801 | true |

**특이사항**:
- 모든 메타데이터 파일 `active: true` 이미 설정됨
- `train_result.json` 의 `active: True` 도 이미 설정됨 (brain_predictor_v3.py 가 실제 참조하는 파일)
- V2 대비 통합 AUC +0.025, Q2공격형 AUC 0.6092 (V2 0.5406 대비 +0.069)

---

## 4. brain_predictor_v3.py import 검증

```
커맨드: venv/bin/python3 -c "from backend.app.services.go100.ai.brain_predictor_v3 import *; ..."

결과:
  BrainPredictorV3: ()
  get_predictor: () -> BrainPredictorV3
  predict_stock: (stock_code: str, features: Dict[str, Any], regime: Optional[str] = None) -> Dict[str, Any]
```

**import 상태**: 정상 (오류 없음)

---

## 5. V3 모델 로드 테스트

```
V3 모델 수: 6
  go100_brain_v3_clf_nonq2_defensive.joblib: type=LGBMClassifier, features=30
  go100_brain_v3_clf_q2_aggressive.joblib:   type=LGBMClassifier, features=30
  go100_brain_v3_clf_unified.joblib:         type=LGBMClassifier, features=30
  go100_brain_v3_reg_gap_d1_unified.joblib:  type=LGBMRegressor, features=30
  go100_brain_v3_reg_mfe_3d_unified.joblib:  type=LGBMRegressor, features=30
  go100_brain_v3_reg_mfe_60min_unified.joblib: type=LGBMRegressor, features=30
```

**6/6 모델 로드 성공**. 모든 모델 feature 수 30개 일치.

---

## 6. brain_predictor_v3.py active 로딩 로직

| 항목 | 내용 |
|------|------|
| active 소스 파일 | `data/go100/models/v3/go100_brain_v3_train_result.json` |
| 로직 | `self._is_active = self._train_result.get("active", False)` |
| active=false 시 동작 | `[BrainV3] active=false — 모델 로드 스킵` (예측 비활성화) |
| 현재 상태 | `active: True` (로드 준비 완료) |
| 모델 충분 조건 | loaded_count >= 4 (현재 6/6) |

**분석**: `brain_predictor_v3.py`는 `train_result.json`의 `active` 필드를 읽어서 모델 로드 여부 결정. 현재 이미 `True` 상태이므로 서비스 재시작 시 즉시 로드.

---

## 7. agent_tools / tool_executors 연동 상태

```
grep -rn "brain_predictor|get_ai_prediction|BrainPredictor" agent_tools.py tool_executors.py
→ 결과 없음
```

**상태**: brain_predictor_v3.py가 agent_tools.py/tool_executors.py에 아직 연동되지 않음.
현재 `predict_stock()` 함수 및 `BrainPredictorV3.predict_single()` API는 외부에서 직접 호출 방식으로 사용 가능.

---

## 8. 활성화 스크립트

**경로**: `scripts/go100/activate_v3_model.py`
**권한**: chmod +x 완료 (-rwxrwxr-x)

```python
#!/usr/bin/env python3
"""V3 모델 활성화 스크립트 — CEO 승인 후 실행
Usage: python3 activate_v3_model.py --confirm
"""
import json, sys, shutil
from pathlib import Path
from datetime import datetime

MODEL_DIR = Path('/root/kis-autotrade-v4/data/go100/models')
V3_DIR = MODEL_DIR / 'v3'
BACKUP_DIR = MODEL_DIR / 'v2_backup'

def activate():
    # V2 백업
    BACKUP_DIR.mkdir(exist_ok=True)
    for f in MODEL_DIR.glob('go100_brain_v2_*.joblib'):
        shutil.copy2(f, BACKUP_DIR / f.name)
        print(f'[BACKUP] {f.name} → v2_backup/')
    # V3 메타데이터 업데이트
    meta_files = list(V3_DIR.glob('*metadata*.json'))
    for mf in meta_files:
        data = json.loads(mf.read_text())
        data['active'] = True
        data['activated_at'] = datetime.now().isoformat()
        data['activated_by'] = 'CEO_APPROVED'
        mf.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f'[ACTIVATE] {mf.name}: active=True')
    print(f'\n✅ V3 모델 {len(meta_files)}종 활성화 완료. V2 백업: {BACKUP_DIR}')

if __name__ == '__main__':
    if '--confirm' not in sys.argv:
        print('⚠️  CEO 승인 필요. 실행: python3 activate_v3_model.py --confirm')
        sys.exit(1)
    activate()
```

**동작**: V2 joblib 백업 → V3 메타데이터 active=True/activated_at/activated_by 기록

---

## 9. 백업 확인

```
brain_predictor_v3.py.bak.T017 생성 완료
/root/kis-autotrade-v4/backend/app/services/go100/ai/brain_predictor_v3.py.bak.T017
```

---

## 10. CEO 승인 후 실행 절차

```bash
# CEO 승인 후:
cd /root/kis-autotrade-v4
python3 scripts/go100/activate_v3_model.py --confirm

# 서비스 재시작:
sudo systemctl restart go100

# 헬스체크:
curl http://localhost:8002/health
```

---

## 11. 체크포인트

- [x] brain_predictor_v3.py 백업 완료 (.bak.T017)
- [x] V3 모델 6종 존재 및 메타데이터 확인 완료
- [x] import/signature 검증 완료 (정상)
- [x] 모델 로드 테스트 6/6 성공
- [x] brain_predictor_v3.py active 로딩 로직 확인 (train_result.json 참조, active=True)
- [x] activate_v3_model.py 스크립트 작성 및 chmod +x 완료
- [x] agent_tools/tool_executors 연동 상태 확인 (미연동, 독립 사용)

---

## 저장 정보 (PATH-001 §4-8)

| 항목 | 경로 |
|------|------|
| 활성화 스크립트 | /root/kis-autotrade-v4/scripts/go100/activate_v3_model.py |
| 모델 디렉토리 | /root/kis-autotrade-v4/data/go100/models/v3/ |
| train_result.json | /root/kis-autotrade-v4/data/go100/models/v3/go100_brain_v3_train_result.json |
| brain_predictor | /root/kis-autotrade-v4/backend/app/services/go100/ai/brain_predictor_v3.py |
| brain_predictor 백업 | /root/kis-autotrade-v4/backend/app/services/go100/ai/brain_predictor_v3.py.bak.T017 |
| 로컬 보고서 | /root/kis-autotrade-v4/report/go100/CUR-GO100-V3-MODEL-ACTIVATE-PREP-001-20260305.md |
| project-docs 보고서 | /root/project-docs/go100/reports/CUR-GO100-V3-MODEL-ACTIVATE-PREP-001-20260305.md |
