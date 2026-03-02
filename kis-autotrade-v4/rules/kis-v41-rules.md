# KIS AutoTrade V4.1 + GO100 모노리포 — 서비스 경계 규칙

## 이 프로젝트는 2개의 독립 서비스가 하나의 레포에 공존합니다.
## 작업 시 반드시 어느 서비스에 대한 작업인지 먼저 확인하세요.

---

## 서비스 A: KIS AutoTrade V4.1 (자동매매 엔진)
- 용도: 한국투자증권 API 기반 자동매매, 실시간 데이터 수집, 데스크 전략
- 백엔드 라우터: /api/v4/*, /api/v1/dashboard, /api/v1/trade, /api/v1/settings
- 백엔드 파일: backend/app/routers/v4_*.py, backend/app/services/v4_*, backend/app/services/data/*
- 프론트엔드: frontend/src/app/(protected)/ (go100 폴더 제외 전부)
- 프론트엔드 페이지: /dashboard, /trade, /backtest, /strategy-cards, /portfolio, /accounts, /admin, /monitoring, /reports, /settings, /notifications
- systemd: go100-ws-krx, go100-ws-nxt (WS 수집기)
- 크론: collect_*.sh, scripts/data_collect/*, 키움 관련 스크립트
- DB 테이블 (V4.1 전용): ohlcv_daily, v4_ohlcv_minute, v4_tick_data, v4_orderbook_realtime, index_daily, v4_vkospi_daily, v4_investor_daily, v4_market_regime_daily, stock_universe, stock_fundamentals, strategy_cards, v4_users, accounts, v4_positions, v4_orders
- 절대 GO100 파일을 수정하지 마세요.

## 서비스 B: GO100 (AI 주식 어시스턴트 "백억이")
- 용도: AI 채팅 기반 전략 설계/백테스트/페이퍼/실매매 SaaS
- 도메인: go100.newtalk.kr
- 백엔드 라우터: /api/go100/*
- 백엔드 파일: backend/app/routers/go100/*.py, backend/app/services/go100/**/*
- 프론트엔드: frontend/src/app/(protected)/go100/**/*
- 프론트엔드 컴포넌트: frontend/src/go100/**/*
- systemd: go100 (FastAPI 메인 — 공유), go100-frontend (Next.js — 공유)
- 크론: scripts/go100/*.sh
- DB 테이블 (GO100 전용): go100_strategy_cards, go100_backtest_runs, go100_portfolios, go100_positions, go100_orders, go100_trades, go100_goals, go100_user_profile, go100_usage_logs, go100_global_market, go100_sector_price, go100_sector_correlation, go100_overnight_gap, go100_cross_market_signals, go100_fundamentals_pit, go100_orderbook_daily_stats, go100_tick_daily_stats, go100_calibration_params, go100_trading_cost_params, go100_data_integrity_log, go100_alerts, go100_experience_log
- 절대 V4.1 파일을 수정하지 마세요.

## 공유 인프라 (양쪽 모두 사용, 수정 시 양쪽 영향 확인 필수)
- backend/app/main.py (라우터 등록)
- backend/app/core/ (config, security, database)
- backend/app/models/ (SQLAlchemy 모델)
- frontend/src/app/layout.tsx, middleware.ts
- .env (환경변수)
- PostgreSQL kisautotrade DB
- Redis
- Nginx 설정

## 작업 규칙
1. 작업 시작 전 "이 작업은 V4.1/GO100/공유 중 어디에 해당하는가?" 먼저 판단
2. V4.1 작업 시 GO100 폴더(routers/go100, services/go100, go100/) 절대 수정 금지
3. GO100 작업 시 V4.1 폴더(routers/v4_*, services/v4_*) 절대 수정 금지
4. 공유 인프라 수정 시 양쪽 서비스 영향도 반드시 명시
5. 커밋 메시지 prefix: [V4.1], [GO100], [SHARED]
6. DB 테이블 생성 시 GO100은 go100_ prefix 필수
7. 크론 스크립트: V4.1은 scripts/collect_*.sh 또는 scripts/data_collect/, GO100은 scripts/go100/

## 9. Genspark CEO 통합지휘 대화 규칙 (2026-03-03 추가)

### 9-1. 작업 완료의 정의
- "완료"란 아래 4가지가 **모두** 충족된 상태만을 의미한다:
  1. 로컬 파일 수정 완료
  2. `bash scripts/security_scan.sh` → 0건
  3. `git add -A && git commit && git push origin master` 성공
  4. `curl` HTTP 200 확인
- 위 4가지 중 하나라도 미충족이면 "작업 진행중"으로 보고한다
- **push 전에 "완료"라고 보고하는 것은 금지**

### 9-2. CEO 대화창 보고 형식 (필수)
CEO 통합지휘 대화창에 보고할 때 반드시 아래 형식을 사용한다:

```
[CURSOR-KIS] {상태}

작업: {작업 내용 1줄 요약}
보고서: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/{파일명}
커밋: https://github.com/moongoby/project-docs/commit/{SHA}
HTTP: {200|실패}
security_scan: {0건|N건}
path_check: {PASS|FAIL}
다음: {다음 작업 또는 "지시 대기"}
```

{상태} 값: `push 완료` | `작업 진행중` | `문제 발생` | `지시 대기`

### 9-3. 파일명 규칙 재확인
- 보고서 파일명은 **영문 대문자, 숫자, 하이픈만** 사용
- 형식: `CUR-V41-{TASK}-{SEQ}-{YYYYMMDD}.md`
- 한글, 공백, 언더스코어, 소문자 **금지**
- 예시: `CUR-V41-CEO-DIRECTIVE-CONFIRM-001-20260302.md` ✅
- 금지: `CUR-V41-CEO-지시확인-001-20260302.md` ❌

### 9-4. push 전 필수 체크리스트
모든 commit/push 전에 아래 순서를 반드시 실행한다:
```bash
cd /root/project-docs
bash scripts/security_scan.sh          # 1) 보안 스캔 → 0건 확인
bash scripts/path_check.sh {파일명}    # 2) 경로/네이밍 검증
git add -A && git diff --cached --stat # 3) 변경 내역 확인
git commit -m "[V4.1] {type}: {설명}"  # 4) 커밋
git push origin master                 # 5) push
sleep 5                                # 6) 캐시 대기
curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/{파일명}  # 7) HTTP 200 확인
```

### 9-5. Genspark Claude 지시 블록 파싱
CEO 통합지휘 대화창의 Claude가 >>>DIRECTIVE_START ~ >>>DIRECTIVE_END 블록으로 지시를 내린다.
- 이 블록 안의 내용을 순서대로 실행한다
- 실행 불가능한 항목이 있으면 실행하지 않고 사유를 보고한다
- 블록 외부의 [상황 판단], [참고]는 맥락 정보이며 실행 대상이 아니다

### 9-6. 세션 시작/복원 프로토콜
Genspark 대화창에 첫 메시지를 보낼 때 아래 형식을 사용한다:
```
[CURSOR-KIS] 세션 시작
- HANDOVER: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md
- CEO-DIRECTIVES: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CEO-DIRECTIVES.md
- 최근 작업: {마지막 완료 작업 1줄}
- CEO 방향: {있으면 기재, 없으면 "없음"}
```

### 9-7. project-docs 동기화 의무
- KIS 프로젝트는 공통 문서(common/) 관리를 겸임한다
- scripts/verify.sh, scripts/path_check.sh, scripts/security_scan.sh 수정 시 다른 4개 프로젝트에 영향이 없는지 확인한다
- 동기화: bash /root/project-docs/scripts/sync_kis.sh
