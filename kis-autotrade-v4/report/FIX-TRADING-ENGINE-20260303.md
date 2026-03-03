# 거래 엔진 장애 수정 및 trading.html 개선 보고서

**작업일**: 2026-03-03
**담당**: Claude
**대상 프로젝트**: trading41.newtalk.kr (V4.1 플랫폼)

---

## 1. 거래 엔진 PRAGMA/boolean 오류 수정

### 원인
`kis-trading-engine.service`가 매 분 실행하는 두 스크립트에 SQLite 전용 문법이 PostgreSQL DB에 전송되어 매번 실패.

| 파일 | 문제 | 수정 |
|------|------|------|
| `realtime_signal_generator_fixed.py:173` | `PRAGMA busy_timeout=30000` → PostgreSQL SyntaxError | 해당 라인 제거 |
| `realtime_general_market_auto_trade.py:544` | `PRAGMA busy_timeout=30000` → PostgreSQL SyntaxError | 해당 라인 제거 |
| `realtime_signal_generator_fixed.py:57-58` | `is_active = 1`, `auto_trading_enabled = 1` → boolean = integer 오류 | `= true` 로 수정 |
| `realtime_general_market_auto_trade.py:74-75` | `is_active = 1`, `auto_trading_enabled = 1` → boolean = integer 오류 | `= true` 로 수정 |

### 수정 후 동작
- 신호 생성기: 활성 사용자 7명 감지, 실매매 모드 정상 실행
- 자동매매: DB 쿼리 정상, KIS API 연결 시도 중
- KIS VTS(모의투자) 서버 500 에러는 KIS 서버 측 문제 (코드 무관)

### moongoby@gmail.com KIS 설정 현황
- `is_production = false` (VTS 모의투자 서버 연결)
- `account_number = 50160697` (VTS 계좌)
- `token_expires_at = 2026-03-04` (유효)

---

## 2. trading.html 종목명(코드) 형식 전체 적용

### 변경 파일: `/var/www/trading.newtalk.kr/js/trading.js`

| 위치 | 이전 | 이후 |
|------|------|------|
| L710 (trades 섹션) | `${stockName}` | `${stockName}(${stockCode})` |
| L763 (orderList) | `${stockName} <span class="order-code">` | `${stockName}(${stockCode})` |
| L831 (positions h4) | `<h4>${stockName}` + 별도 `.position-code` div | `<h4>${stockName}(${stockCode})` |
| L965 (signals) | 별도 `.stock-name` + `.stock-code` span | `${stock_name}(${stock_code})` |
| L1035 (pending buy) | 별도 `.stock-name` + `.stock-code` span | `${stockName}(${stockCode})` |
| L1102 (pending exit) | 별도 `.stock-name` + `.stock-code` span | `name(code)` 통합 |

### 변경 파일: `/var/www/trading.newtalk.kr/js/desk2-live.js`

| 위치 | 이전 | 이후 |
|------|------|------|
| L51 (candidates) | `코드 이름` (코드 우선) | `이름(코드)` |
| L70 (signals) | 코드만 | `이름(코드)` (stock_name 있을 경우) |
| L98 (positions) | 코드만 | `이름(코드)` (stock_name 있을 경우) |
| L122 (closed) | 코드만 | `이름(코드)` (stock_name 있을 경우) |

---

## 3. trading.html 실데이터 연동 현황

### Nginx 라우팅 (최종 상태)
- `/api/v4/*` → 8003 (V4.1 API)
- `/api/*` (v1 포함) → 8001 (Legacy WebApp - 실 KIS 데이터)
- `/api/v1/live-trading/` → 8001 경유 (실데이터)

### 8001 live-trading 데이터
- `autotrade_positions` 테이블: CLOSED 83건 + FAILED 1건 (최근 2026-02-13)
- 현재 OPEN 포지션: 없음 (모든 포지션 청산 완료)
- `account_snapshots`: 2026-02-04 기준 잔고 5억 (stale)
- 모의거래 데이터(`v4_mock_trades`, "VIRTUAL_KIS_MOCK") → trading.html에 미노출 (8001 경유)

### v4_positions 상태
| 상태 | 건수 | 기간 |
|------|------|------|
| CLOSED | 24 | 2026-02-19 ~ 2026-03-03 |
| SELL_FAILED | 7 | 2026-02-20 ~ 2026-03-03 |
| OPEN | 0 | — |

`kis-v41-position-monitor.service`: v4_positions WHERE status='OPEN' 조회 → 0건 → 가격 업데이트 없음

---

## 4. 향후 과제

1. `account_snapshots` 갱신: KIS API 잔고 직접 조회 후 스냅샷 업데이트 필요
2. KIS VTS AppKey 만료 문제: 각 사용자별 KIS 앱키 재등록 필요
3. moongoby 실매매 전환: `kis_configs.is_production = true` + 실계좌 앱키 설정 필요
