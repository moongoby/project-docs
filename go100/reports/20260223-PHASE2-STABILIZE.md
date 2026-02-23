# CUR-GO100-PHASE2-STABILIZE 보고서
작성일: 2026-02-23
커밋: dead44f1 (layout ISS-001 주석 보강)

## 해결 이슈
- **ISS-001**: ChatWidget 표시 → 로딩 중·**미인증 시**에도 FAB 노출, fixed/z-[9999] 유지
- **ISS-002**: 백테스트 드롭다운 GO100 → 기존 구현 확인( for-backtest 병합, [GO100] 접두사, universe 안내)
- **ISS-003**: 전략 저장 E2E → 라우터 500 시 logger.exception, FE 에러 시 응답 본문(상세) 로깅
- **.cursorrules**: 이미 보완됨(빌드 검증, sync, 보고서, 필수 참조 문서)

## 변경 파일 (이번 커밋)
- `backend/app/routers/go100/strategy_router.py` — logging 추가, 500 시 logger.exception
- `frontend/src/app/(protected)/layout.tsx` — 미인증 시에도 ChatWidget 렌더
- `frontend/src/components/chat/StrategyCardSaveButton.tsx` — 에러 시 응답 본문 console.error
- `docs/ISSUES.md` — ISS-001 설명에 미인증 시 노출 추가

## 검증 결과
- API: POST /api/go100/strategy-cards (인증 없음) → 401
- Health: go100 200, go100-frontend go100/backtest 200, strategy-cards 307
- 프론트엔드 빌드: 성공, BUILD_ID > 커밋 시간

## 롤백 절차 (STEP 8)
```bash
sudo systemctl stop go100 go100-frontend
cd /root/kis-autotrade-v4
git revert HEAD --no-edit
cd frontend && npm run build
sudo systemctl start go100 go100-frontend
sleep 10
curl -s http://localhost:8002/health
```
