# KIS AutoTrade V4.1 — 코드 검수 디렉토리

## 용도
중요 소스 변경 시 적용 전 검수를 위한 임시 업로드 공간.
CEO가 Claude에게 URL을 전달 → Claude 검수 → 승인/반려 → 적용 후 이 디렉토리에서 삭제.

## 검수 대상 (필수 검수 파일 목록)
아래 파일을 수정할 때는 **반드시** 이 디렉토리에 업로드 후 검수를 받아야 한다:

### V4.1 핵심 파일
- backend/app/services/trading/v4_pipeline_orchestrator.py (파이프라인 전체 흐름)
- backend/app/services/trading/strategy_engine.py (전략 엔진)
- backend/app/services/trading/risk_manager.py (리스크 관리)
- backend/app/services/trading/order_executor.py (주문 실행)
- backend/app/services/trading/position_manager.py (포지션 관리)
- backend/app/services/trading/split_transfer_engine.py (프로모션 엔진)
- backend/app/services/trading/lifecycle.py (포지션 라이프사이클)
- backend/app/services/fund/* (자금 관리 전체)
- backend/app/services/adaptive/* (어댑티브 엔진 전체)
- backend/app/services/market/regime_detector.py (레짐 감지)
- scripts/backtest/backtest_engine_v2.py (백테스트 엔진)
- backend/app/services/data_pipeline/collector_minute.py (분봉 수집기)
- backend/app/main.py (FastAPI 진입점)
- CLAUDE.md (프로젝트 규칙)
- .cursor/rules/*.md (Cursor 규칙)

### GO100 핵심 파일
- backend/app/services/go100/live_trading/* (실거래 엔진)
- backend/app/services/go100/risk/* (리스크 관리)
- backend/app/services/go100/scheduler/* (스케줄러)

## 파일 업로드 규칙
1. 파일명: `{원본파일명}__REVIEW__{작업ID}.py` (또는 .md)
   예시: `v4_pipeline_orchestrator__REVIEW__OVERLAP-GUARD.py`
2. 파일 상단에 검수 헤더 주석 추가 (아래 템플릿 참조)
3. 민감정보(API키/비밀번호/토큰) 포함 시 업로드 금지 — 해당 라인은 `# [REDACTED]`로 대체

## 검수 헤더 템플릿 (파일 최상단에 삽입)
```python
# ═══════════════════════════════════════
# CODE REVIEW REQUEST
# 작업ID: {작업명}
# 대상파일: {원본 경로}
# 변경사유: {왜 수정하는지}
# 변경요약: {무엇을 바꿨는지 3줄 이내}
# 영향범위: {어떤 기능에 영향을 주는지}
# 검수요청일: {YYYY-MM-DD}
# ═══════════════════════════════════════
```

## 프로세스
```
[Cursor 작업 중 핵심 파일 수정 필요]
    ↓
[1] 수정 완료된 파일을 review/ 디렉토리에 복사
    cp {수정파일} /root/project-docs/kis-autotrade-v4/review/{파일명}__REVIEW__{작업ID}.py
    ↓
[2] 검수 헤더 삽입
    ↓
[3] 보안 검사 + git push
    bash /root/project-docs/scripts/push_review.sh {작업ID}
    ↓
[4] 사용자에게 검수 URL 보고 — 여기서 작업 일시 중단
    "검수 요청: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/review/{파일명}"
    ↓
[5] CEO가 Claude에게 URL 전달 → Claude 검수 (로직/보안/규칙준수/영향범위)
    ↓
[6-A] 승인 → Cursor에 "검수 승인, 적용 진행" 전달
[6-B] 반려 → Cursor에 "검수 반려, 수정사항: ..." 전달
    ↓
[7] 적용 완료 후 review/ 디렉토리에서 검수 파일 삭제
    bash /root/project-docs/scripts/clean_review.sh
```

## CEO → Claude 검수 요청 예시
"이 파일 검수해줘: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/review/v4_pipeline_orchestrator__REVIEW__OVERLAP-GUARD.py"
