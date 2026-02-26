# CUR-GO100-AI-BACKTEST-OPT-001 보고서
> 작성일: 2026-02-24  
> 작업: 백억이 백테스트 기반 자동 최적화 구현

## 변경 사항

### DB
- **go100_optimization_runs** 테이블 신규 생성 (마이그레이션 `026_go100_optimization_runs_cur_backtest_opt.sql`)
- **go100_strategy_cards**: `version`, `parent_card_id`, `optimization_source` 컬럼 추가 (postgres 소유 테이블에 ALTER 별도 실행)

### Backend
- `backend/app/services/go100/optimizer/backtest_optimizer.py` (신규) — 백테스트 → LLM 분석 → 파라미터 조정 → 새 카드 생성 루프
- `backend/app/routers/go100/optimizer_router.py` — 기존 fit/exit/desk 엔드포인트 유지, 백테스트 최적화 API 4개 추가
- `backend/app/services/go100/ai/intent_router.py` — `optimize_existing` 의도 분기 추가
- `backend/app/routers/go100/ai_router.py` — 채팅 시 `optimize_existing` 감지 시 BacktestOptimizer 호출 후 응답 반환

### Frontend
- `frontend/src/go100/api/go100Api.ts` — `startBacktestOptimization`, `getOptimizationRuns`, `getOptimizationRunDetail`, `applyOptimizationResult` 및 타입 추가

### API 엔드포인트
| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | /api/go100/optimizer/backtest-optimize | 백테스트 기반 자동 최적화 시작 |
| GET  | /api/go100/optimizer/runs/{card_id} | 카드별 최적화 이력 조회 |
| GET  | /api/go100/optimizer/run/{opt_run_id} | 개별 최적화 실행 상세 |
| POST | /api/go100/optimizer/apply/{opt_run_id} | 최적화 결과 적용(최적 버전 카드 활성화) |

### 채팅 연동
- 사용자 메시지에 "최적화", "개선", "수익률 올려", "MDD 줄여" 등 키워드 포함 시 `optimize_existing` 분기
- `card_id`/`go100_card_id` 미지정 시 최근 수정된 활성 카드 1건으로 최적화 실행

## 테스트 결과
- [x] Python 문법 확인 통과
- [ ] pytest 통과 (venv 환경에서 별도 실행)
- [x] tsc --noEmit 통과
- [ ] npm run build (실행 중 확인)
- [x] DB 테이블 go100_optimization_runs 생성 확인
- [x] go100_strategy_cards version, parent_card_id, optimization_source 컬럼 확인
- [ ] 서비스 재시작 및 헬스체크 (kis-v41-* 재시작 금지, go100만 재시작 가능 시 수행)
- [ ] 최적화 API 호출 테스트 (인증 필요)

## 다음 단계
- Phase 3: 모의매매 결과 기반 실전 최적화 (CUR-GO100-AI-PAPER-OPT-001)
- 채팅 위젯에서 "이 전략 최적화해줘" 시 body에 `go100_card_id` 전달하면 해당 카드 기준 최적화

## 규칙 준수
- kis-v41-* 서비스 재시작 없음
- strategy_cards 테이블 ALTER/DROP/DELETE 없음 (go100_strategy_cards에 ADD COLUMN만)
- v4_positions 미수정
- .env/.bak 미커밋
- 실계좌(account_id=5,6) 미사용
- 변경 파일 헤더: `# CUR-GO100-AI-BACKTEST-OPT-001, 2026-02-24`
- go100_* 파일/테이블만 수정
- 작업 전 백업 생성 완료
