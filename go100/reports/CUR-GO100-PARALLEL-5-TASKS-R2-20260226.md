# 2차 병렬 작업 5건 종합 보고 (2026-02-26)

## 개요
- **작업일**: 2026-02-26  
- **원칙**: 에러 시 해당 작업만 스킵, 나머지 계속 진행 후 종합 보고  

---

## 작업 1/5: usage_logs 근본 원인 해결

### 현상
- 18회 채팅 후 `go100_usage_logs` 0건

### 원인
- **누락 경로**: `_log_usage()`가 호출되지 않는 응답 경로 다수 존재  
  - 온보딩 환영 메시지 early return  
  - goal_setup 1턴 동기 응답  
  - optimize_existing 예외 분기  
  - market_briefing, live_start/live_enable/live_status/live_stop  
  - sector_analysis, risk_check, rebalance  
- **에러 은닉**: `usage_logger`에서 예외 시 `logger.warning`만 사용해 원인 추적 어려움

### 조치
1. **ai_router.py**  
   - 온보딩 return 직전 `_log_usage("onboarding", reply)` 추가  
   - goal_setup 1턴: `_handle_goal_first_turn` 반환 후 `_log_usage("goal_setup", ...)` 추가, 예외 분기에도 `_log_usage` 추가  
   - optimize_existing 예외 분기에 `_log_usage(..., is_err=True)` 추가  
   - market_briefing 성공/예외 모두 `_log_usage` 추가  
   - live_start, live_enable, live_status, live_stop 성공/예외 모두 `_log_usage` 추가  
   - sector_analysis, risk_check, rebalance 성공/예외 모두 `_log_usage` 추가  
2. **usage_logger.py**  
   - 예외 시 `logger.error(..., exc_info=True)`로 변경해 traceback 기록  

### 검증
- **채팅 엔드포인트**: `POST /api/go100/ai/chat` (인증 필요).  
- 인증된 프론트/클라이언트에서 채팅 1회 이상 수행 후  
  `SELECT count(*) FROM go100_usage_logs` 로 1건 이상 확인 가능.  
- 현재 DB 기준 0건인 이유: 수정 반영 후 아직 인증 채팅 미실행.  

### 결과
- **상태**: 수정 완료.  
- **추가**: `systemctl restart go100` 적용됨.  

---

## 작업 2/5: 크로스마켓 시그널 수집 스크립트 + cron 등록

### 내용
- **스크립트**: `scripts/data_collect/collect_cross_market_signals.py`  
  - `go100_global_market` 최근 80일 데이터 조회  
  - SOX→반도체, USD/KRW→외국인, US10Y→성장주, VIX→변동성 시그널 생성  
  - `go100_cross_market_signals`에 INSERT (ON CONFLICT DO NOTHING)  
- **DB 연결**: `.env`의 `DATABASE_URL_SYNC` 또는 `DB_*` 사용하도록 수정  
- **SQL 수정**: `data_date >= (NOW() - INTERVAL '80 days')::date` (date 타입 비교)

### 실행 결과
- 크로스마켓 시그널 **3건** 적재  
  - usd_krw_foreign_flow (bullish)  
  - us10y_growth_stocks (bullish)  
  - vix_market_complacency (neutral)  

### Cron
- `0 7 * * 1-5` (월~금 07:00 KST)  
- 로그: `/var/log/go100-cross-signal.log`  

### 결과
- **상태**: 성공  

---

## 작업 3/5: 미등록 크론 5건 등록

### 등록 스크립트 및 스케줄
| 용도           | 스크립트 | Cron | 로그 |
|----------------|----------|------|------|
| 모닝 브리핑   | `scripts/go100/run_morning_briefing.sh`  | 50 8 * * 1-5  | /var/log/go100/morning.log |
| 장마감 리포트 | `scripts/go100/run_closing_report.sh`    | 40 15 * * 1-5 | /var/log/go100/closing.log |
| 페이퍼 트레이딩 | `scripts/go100/run_paper_trading.sh`   | 10 16 * * 1-5 | /var/log/go100/paper.log |
| 주간 보고     | `scripts/go100/run_weekly_report.sh`     | 0 9 * * 6     | /var/log/go100/weekly.log |
| 헬스 모니터   | `scripts/go100/run_health_monitor.sh`    | */5 * * * *   | /var/log/go100/health_monitor.log |

- 각 스크립트: `cd /root/kis-autotrade-v4`, `source venv/bin/activate`, Python/쉘 로직 실행.  
- 기존 `daily_reports.py`/`health_monitor.py` 등과 중복될 수 있어, 현재 **go100 관련 cron 15건** 존재.  

### 결과
- **상태**: 성공 (스크립트 생성 및 cron 등록 완료)  

---

## 작업 4/5: 시드 데이터 생성 (백테스트 3건 + 대표님 목표/포트폴리오)

### 내용
- **스크립트**: `/tmp/generate_seed_data.py` (실행 후 삭제 가능)  
  - `go100_backtest_runs`: 이미 13건 존재 → 시드 미추가  
  - `go100_goals`: 대표님(user_id=2) 목표 1건 추가 (1억→3억, 5년)  
  - `go100_portfolios`: 대표님 포트폴리오 1건 추가 (전략카드 1개 연동)  
  - `go100_user_profile`: 테이블/컬럼 구조 불일치로 INSERT 실패 (preferred_style 등 컬럼 없음)  

### DB 현황 (작업 후)
| 테이블 | 건수 |
|--------|------|
| go100_backtest_runs | 13 |
| go100_goals         | 6  |
| go100_portfolios    | 2  |
| go100_user_profile  | 0 (스키마 정리 후 재실행 권장) |

### 결과
- **상태**: 부분 성공 (목표·포트폴리오 시드 반영, 백테스트는 기존 데이터 유지, 프로파일은 스키마 정합 후 재진행 권장)  

---

## 작업 5/5: Agentic Architecture 사전 준비 (agent_tools.py 스캐폴딩)

### 내용
- **파일**: `backend/app/services/go100/ai/agent_tools.py`  
- **역할**: data_queries 등 기존 함수를 LLM function calling 도구로 래핑할 스키마 정의 (v2.0 Week 2~4용)  
- **도구 수**: **21개**  
  - 시장 3, 종목 4, 업종/섹터 3, 포트폴리오/전략 3, 레짐/시그널 3, 매매 2, 보고서 1, 목표/프로파일 2  
- **TOOL_EXECUTORS**: 추후 구현 예정  

### 검증
- `python -c "from backend.app.services.go100.ai.agent_tools import get_tool_count, get_tool_names; ..."`  
- **Agent Tools 등록: 21개** 정상 인식  

### 결과
- **상태**: 성공  

---

## 종합 현황 (최종 확인 기준)

| 항목 | 결과 |
|------|------|
| go100_usage_logs | 0건 (코드 수정 완료, 인증 채팅 후 증가 예상) |
| go100_cross_market_signals | 3건 (당일 시그널 적재) |
| go100 cron | 15건 |
| go100_backtest_runs | 13건 |
| go100_goals | 6건 |
| go100_portfolios | 2건 |
| Agent Tools | 21개 |
| go100 / go100-ws-nxt / go100-frontend / postgresql | active |
| 디스크 /data | 8% 사용 |
| 디스크 / | 69% 사용 |

---

## 결론
- **작업 1**: usage_logs 누락 경로 보완 및 에러 로깅 강화 완료.  
- **작업 2**: 크로스마켓 시그널 스크립트·cron·당일 3건 적재 완료.  
- **작업 3**: 모닝/장마감/페이퍼/주간/헬스 크론 5건 스크립트 생성 및 등록 완료.  
- **작업 4**: 목표·포트폴리오 시드 반영. 백테스트는 기존 유지, 프로파일은 스키마 정리 후 재실행 권장.  
- **작업 5**: agent_tools.py 21개 도구 스캐폴딩 완료.  

에러 시 해당 작업만 스킵하고 나머지를 진행한 원칙에 따라, 부분 실패(작업 4 프로파일)는 보고에 명시하고 나머지는 목표대로 반영 완료.
