# D6/D7 모의 실매매 스크립트 문서

| 항목 | 내용 |
|------|------|
| 스크립트 | `scripts/live_paper_d6_d7.py` |
| 작성일 | 2026-02-28 |
| CEO 지시 | D-010, D-011, DESK2 최종설계서 §11 |
| 상태 | 모의투자 모드 (PAPER) |

---

## 1. 개요

DESK2 멀티-컨디션 엔진의 즉시 투입 전략 D6(상따→갭)과 D7(종가배팅→갭)을
KIS 모의투자 API를 통해 자동 운영하는 스크립트.

- **D6**: 장중 상한가 감지 → 종가 매수 → D+1 시초가 매도
- **D7**: 14:30 스크리닝 → 종가 매수 → D+1 시초가 매도

---

## 2. 실행 환경

```
서버: root@211.188.51.113
경로: /root/kis-autotrade-v4/scripts/live_paper_d6_d7.py
Python: 3.12.3 (venv)
의존성: psycopg2, httpx, numpy
KIS API: 모의투자 계좌 (config_id=1, is_production=false)
로그: /var/log/d6d7_paper.log
```

---

## 3. Cron 등록

```cron
50 8 * * 1-5 cd /root/kis-autotrade-v4 && source venv/bin/activate && python scripts/live_paper_d6_d7.py >> /var/log/d6d7_paper.log 2>&1
```

- 평일 08:50 시작 → 15:40 자동 종료
- 기존 go100/kis-v41 서비스와 독립 프로세스 (서비스 재시작 없음)

---

## 4. 모듈 구조

### 4.1 KISClient

KIS API 독립 클라이언트. `kis_configs` 테이블에서 자격증명 로드.

```python
class KISClient:
    def __init__(self, config_id: int)
    def get_current_price(stock_code) -> dict     # 현재가 조회
    def get_volume_rank(market) -> list            # 거래대금 상위
    def place_market_buy(stock_code, quantity)      # 시장가 매수
    def place_market_sell(stock_code, quantity)     # 시장가 매도
    def get_balance() -> dict                      # 잔고 조회
```

### 4.2 D6Scanner

장중 1분 주기 상한가 감지.

- 코스피+코스닥 거래대금 상위 30 조회
- 등락률 ≥ 29.5% (상한가) 종목 감지
- 오전(10시 전) 감지 우선
- 최대 `max_stocks_d6`건 (기본 3, DB 카드에서 덮어씀)

### 4.3 D7Scanner

14:30 1회 스크리닝.

- 코스닥 등락률 체크 (BEAR OFF: ≤ -1%)
- 거래대금 상위 15 중 필터:
  1. 등락률 ≥ 5%
  2. 종가위치 ≥ 0.70
- 종가위치 높은 순 정렬
- 최대 `max_stocks_d7`건 (기본 5, DB 카드에서 덮어씀)

### 4.4 OrderExecutor

KIS API 주문 실행.

- 전략별 종목당 투입금 = `allocated_amount / max_stocks` (DB 전략카드)
- 수량 = `capital_per_stock // current_price`
- 모의투자 TR_ID 사용 (VTTC0012U/VTTC0011U)

### 4.5 DCSRecorder

거래 기록 + 일일 DCS 산정.

- `v4_paper_trades` 테이블 자동 생성
- 매수/매도 기록
- 일일 DCS = Σ(pnl_pct)

---

## 5. 운영 타임라인

```
08:50  시작, 초기화
09:00  전일 매수분 시초가 매도
09:05  D6 스캐너 시작 (1분 주기)
14:30  D7 스크리닝 (1회)
15:20  D6/D7 종가 매수
15:40  DCS 계산, 종료
```

---

## 6. DB 전략카드 연동

스크립트 시작 시 `go100_strategy_cards`에서 D6/D7 카드를 읽어 설정 반영:

| 카드 필드 | CONFIG 반영 |
|-----------|-------------|
| `allocated_amount` | 종목당 투입금 (allocated / max_stocks) |
| `max_stocks` | 최대 동시 보유 종목 |
| `risk_params.hard_stop` | 하드스톱 % |
| `risk_params.stop_loss_pct` | 손절 % |
| `risk_params.trailing` | 트레일링 스톱 파라미터 |
| `exit_rules` | 부분청산 설정 |
| `is_active` | 전략 활성/비활성 (비활성 시 해당 전략 스킵) |

프론트엔드에서 카드 설정 변경 → 다음 실행 시 자동 반영.

---

## 7. 자본 배분 (기본값)

| 전략 | 종목당 | 최대 종목 | 총 배분 |
|------|--------|-----------|---------|
| D6 | 500만원 | 3 | 1,500만원 |
| D7 | 500만원 | 5 | 2,500만원 |

---

## 8. 리스크 관리

- **하드스톱**: -5% (D6/D7 공통)
- **BEAR OFF**: 코스닥 등락률 ≤ -1% 시 D7 스킵
- **모드 전환**: `CONFIG['mode']` = 'PAPER' → 'LIVE' (CEO 승인 후)

---

## 9. CLI 옵션

```bash
# 전체 운영 (기본)
python scripts/live_paper_d6_d7.py

# 매도만 실행 (전일 매수분)
python scripts/live_paper_d6_d7.py --sell-only

# 현재 잔고 확인
python scripts/live_paper_d6_d7.py --status

# 오늘 DCS 확인
python scripts/live_paper_d6_d7.py --dcs
```

---

## 10. 검증 근거

| 전략 | PF | 승률 | 연간 건수 | 근거 |
|------|-----|------|-----------|------|
| D6 | 13.63 | 77.8% | 36 | VE-003 Phase A |
| D7 | 2.12 | 53.4% | 369 | VE-003 Phase A + Phase E 마스크 |

---

*문서 끝*
