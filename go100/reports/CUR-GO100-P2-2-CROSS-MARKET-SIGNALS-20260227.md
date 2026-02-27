# CUR-GO100-P2-2 — Cross-Market Signal 수집기

**일시:** 2026-02-27  
**작업 ID:** P2-2 Cross-Market Signal 수집기  
**목적:** 해외 시장 시그널(SOX→반도체, USD/KRW→외인, US10Y→성장주, CSI300) 자동 수집 및 모닝 브리핑 연동

---

## 1. 요약

- **테이블:** `go100_cross_market_signals` 마이그레이션 추가 (034).
- **수집 스크립트:** `scripts/go100/collect_cross_market_signals.py` — yfinance로 4종 시그널 수집, 전일 대비 변동률 기반 방향성/신뢰도 계산 후 UPSERT.
- **실행 스크립트:** `scripts/go100/run_cross_market_signals.sh` — 크론 07:00 등록 권장.
- **모닝 브리핑:** `get_cross_market_signals` 도구가 위 테이블에서 최신 시그널을 반환하도록 `tool_executors.py` 연동 완료.

---

## 2. 테이블 스키마 (1단계)

**파일:** `backend/migrations/034_go100_cross_market_signals.sql`

| 컬럼 | 타입 | 설명 |
|------|------|------|
| signal_id | BIGSERIAL | PK |
| signal_date | DATE | 시그널 기준일 |
| signal_type | VARCHAR(50) | SOX_SEMI, USDKRW_FOREIGN, US10Y_GROWTH, CSI300_OPEN |
| value | FLOAT | 수치값 (지수/환율/금리 등) |
| direction | VARCHAR(20) | BULLISH / BEARISH / NEUTRAL |
| confidence | FLOAT | 0~1 신뢰도 (변동률 크기 기반) |
| raw_data | JSONB | symbol, close, prev_close, change_pct 등 |
| created_at | TIMESTAMP | 생성/갱신 시각 |

- **UNIQUE(signal_date, signal_type)** 로 동일일·동일 타입 중복 방지, 재수집 시 ON CONFLICT DO UPDATE.

---

## 3. 수집 스크립트 (2단계)

**파일:** `scripts/go100/collect_cross_market_signals.py`

- **데이터 소스:** yfinance  
  - SOX: `^SOX` → SOX_SEMI (반도체)  
  - USD/KRW: `KRW=X` → USDKRW_FOREIGN (외인)  
  - 미국 10년물: `^TNX` → US10Y_GROWTH (성장주)  
  - 중국: `000300.SS` → CSI300_OPEN (CSI300)

- **방향성:** 전일 종가 대비 당일(또는 최신) 종가 변동률(%)  
  - 변동률 > 0.2% → BULLISH  
  - 변동률 < -0.2% → BEARISH  
  - 그 외 → NEUTRAL  

- **confidence:** `min(1.0, abs(change_pct) / 2.0)` (2% 변동 = 1.0)

- **실행 예:**  
  `python scripts/go100/collect_cross_market_signals.py [--days 5]`

---

## 4. 크론 등록 (3단계)

**실행 스크립트:** `scripts/go100/run_cross_market_signals.sh`

- **권장 크론 라인 (매일 07:00, 평일):**

```cron
# Cross-Market Signal 수집 (GO100 P2-2)
0 7 * * 1-5 /root/kis-autotrade-v4/scripts/go100/run_cross_market_signals.sh >> /var/log/go100/cross_market.log 2>&1
```

- **로그 디렉터리:**  
  `/var/log/go100/` 가 없으면 생성 후 권한 설정  
  `sudo mkdir -p /var/log/go100 && sudo chown $USER /var/log/go100`

- **마이그레이션 선행 실행 (1회):**  
  `psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f backend/migrations/034_go100_cross_market_signals.sql`

---

## 5. 모닝 브리핑 연동 (4단계)

- **tool_executors.py**  
  - `get_cross_market_signals(days=7)`  
  - `go100_cross_market_signals`에서 `signal_date`, `signal_type`, `value`, `direction`, `confidence`, `raw_data` 조회.  
  - 반환: `{ "signals": [ { "date", "type", "value", "direction", "confidence", "desc" } ], "count" }`  
  - `desc`는 시그널 타입별 한글 라벨 + 방향 + 전일대비 변동률(예: "SOX(반도체) BULLISH (전일대비 +0.5%)").

- **agent_tools.py**  
  - 도구 설명을 "SOX→반도체, USD/KRW→외국인, US10Y→성장주, CSI300→중국"으로 정리.

---

## 6. 생성/수정 파일 목록

| 구분 | 파일 | 설명 |
|------|------|------|
| 신규 | backend/migrations/034_go100_cross_market_signals.sql | 테이블 + UNIQUE + 인덱스 |
| 신규 | scripts/go100/collect_cross_market_signals.py | yfinance 수집 + 방향/신뢰도 + UPSERT |
| 신규 | scripts/go100/run_cross_market_signals.sh | 크론용 실행 스크립트 |
| 수정 | backend/app/services/go100/ai/tool_executors.py | get_cross_market_signals 신규 스키마 반영, _cross_market_signal_desc 추가 |
| 수정 | backend/app/services/go100/ai/agent_tools.py | get_cross_market_signals 설명(VIX→CSI300 등) 수정 |

---

## 7. 검증

- 마이그레이션 적용 후 수집 스크립트 1회 실행:
  - `cd /root/kis-autotrade-v4 && source .env && source venv/bin/activate && python scripts/go100/collect_cross_market_signals.py --days 5`
- DB 확인:
  - `SELECT signal_date, signal_type, value, direction, confidence FROM go100_cross_market_signals ORDER BY signal_date DESC, signal_type LIMIT 20;`
- 에이전트 채팅에서 "크로스마켓 시그널 알려줘" 등으로 `get_cross_market_signals` 호출 시 위 테이블 기준 최신 시그널이 나오는지 확인.

---

**문서 끝.**
