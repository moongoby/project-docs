# CUR-V41-LIVE-PAPER-PRECHECK-001
**월요일 D6/D7 모의매매 사전점검 보고서**

| 항목 | 내용 |
|------|------|
| 작업ID | LIVE-PAPER-PRECHECK-001 |
| 작성일 | 2026-03-01 (일) |
| 점검 대상 | scripts/live_paper_d6_d7.py |
| 첫 실행 예정 | 2026-03-02 (월) 08:50 KST |
| cron | `50 8 * * 1-5` |
| 점검 기준일 | 2026-02-27 (금) — 직전 거래일 |

---

## ★★★ 종합 안전 점검 결과 ★★★

| 항목 | 결과 |
|------|------|
| 모의투자 모드 (PAPER) | ✅ 하드코딩 확인 |
| 모의투자 API URL | ✅ `openapivts.koreainvestment.com:29443` |
| 모의투자 계좌 (config_id=1) | ✅ is_production=false |
| 모의투자 TR ID (V prefix) | ✅ VTTC0012U(매수), VTTC0011U(매도), VTTC8434R(잔고) |
| 실계좌(account_id=5,6) 사용 | ✅ **미사용** |
| v4_positions 쓰기 접근 | ✅ **없음** |
| v4_paper_trades 전용 기록 | ✅ 모의매매 전용 테이블 |

> **코드 검수 최종: SAFE** — `max_stocks_d7: 5` 숫자 매칭 오탐 제거 후 실계좌 접근 없음 확인.

---

## 1단계: 스크립트 소스 코드 검수

### 기본 정보
- 경로: `/root/kis-autotrade-v4/scripts/live_paper_d6_d7.py`
- 크기: 36,847 bytes (910행)

### 모드 설정
```python
CONFIG = {
    'mode': 'PAPER',           # ✅ LIVE 전환은 CEO 승인 후에만
    'kis_config_id': 1,        # ✅ 모의투자 계좌 config
    ...
}
```

### D6 로직 요약
```
감지: 09:05~15:20 매분 상한가 종목 스캔 (change_rate >= 29.5%)
필터: KOSPI+KOSDAQ 거래대금 상위 15종목
매수: 15:20 시장가 (max_stocks_d6 제한)
매도: D+1 09:01 시장가
카드: #42 [D6] 상한가->갭 모멘텀 (PAPER_LIVE)
```

### D7 로직 요약
```
감지: 14:30 단 1회 스크리닝
필터: 일간 등락 >= +5%, 종가위치 >= 0.70, KOSDAQ > -1.0%
매수: 15:20 시장가 (max_stocks_d7 제한)
매도: D+1 09:01 시장가
카드: #43 [D7] 종가배팅 트레일링 (PAPER_LIVE)
```

### API 엔드포인트 검증
| 기능 | TR ID | 타입 | 확인 |
|------|-------|------|------|
| 매수 주문 | VTTC0012U | 모의 | ✅ |
| 매도 주문 | VTTC0011U | 모의 | ✅ |
| 잔고 조회 | VTTC8434R | 모의 | ✅ |
| 현재가 조회 | FHKST01010100 | 공용 | ✅ |
| 거래대금 순위 | FHKST01010100 | 공용 | ✅ |

---

## 2단계: DB 연결 및 모의매매 테이블 확인

### v4_paper_trades 테이블
```
현재 상태: ❌ 미존재
조치: 스크립트 내 CREATE TABLE IF NOT EXISTS 포함 → 월요일 첫 실행 시 자동 생성
```

### CREATE TABLE 스크립트 (자동 실행됨)
```sql
CREATE TABLE IF NOT EXISTS v4_paper_trades (
    id BIGSERIAL PRIMARY KEY,
    strategy VARCHAR(10) NOT NULL,
    card_id INTEGER,
    stock_code VARCHAR(10) NOT NULL,
    buy_date DATE NOT NULL,
    sell_date DATE,
    buy_price INTEGER NOT NULL,
    sell_price INTEGER,
    quantity INTEGER NOT NULL,
    pnl_pct NUMERIC(8,4),
    pnl_amount BIGINT,
    conditions JSONB,
    status VARCHAR(20) DEFAULT 'OPEN',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 전략 카드 현황
| 카드 | card_id | card_code | status | is_active |
|------|---------|-----------|--------|-----------|
| D6 | #42 | D6-GAP-MOM | PAPER_LIVE | true |
| D7 | #43 | D7-EOD-TRAIL | PAPER_LIVE | true |

### v4_positions 충돌 여부
- OPEN 포지션: 14건 (desk_id 2/3/4)
- live_paper는 **v4_paper_trades 전용** → v4_positions 와 완전 분리 ✅

### KIS Config 확인
```
config_id=1: 존재, is_production=false ✅
계좌번호: XXXX**** (모의투자 전용)
```

---

## 3단계: cron 실행 환경 점검

| 항목 | 결과 |
|------|------|
| cron 등록 | ✅ `50 8 * * 1-5` |
| 실행 명령 | `cd /root/kis-autotrade-v4 && source venv/bin/activate && python scripts/live_paper_d6_d7.py` |
| 로그 경로 | `/var/log/d6d7_paper.log` |
| Python 경로 | `/root/kis-autotrade-v4/venv/bin/python` ✅ |
| 필수 패키지 | psycopg2, httpx, numpy ✅ |

### 공휴일 필터링 검토
```
현재: 공휴일 필터링 로직 미포함
영향: 공휴일에 cron 실행 시 시장 마감으로 주문 불가 (API 오류 → exception catch)
권고: KRX 휴장일 목록 추가 또는 장 시작 여부 API 확인 로직 추가
```

---

## 4단계: Dry-run 테스트 (2026-02-27 금)

### D6 시그널 (상한가 감지)
| 종목코드 | 종목명 | 등락률 | 종가 | 거래량 |
|---------|--------|--------|------|--------|
| 054620 | APS | **+31.3%** | 6,500원 | 1,095,197 |

- **1건 감지** (연 기대 36건 → 일 평균 0.14건, 정상)
- Phase A D6 백테스트 결과와 일치: 상한가 종목 1건

### D7 시그널 (종가배팅 대상, 상위 10건)
| 종목코드 | 종목명 | 등락률 | 종가위치 |
|---------|--------|--------|---------|
| 051915 | LG화학우 | +10.7% | 1.000 |
| 054620 | APS | +31.3% | 1.000 |
| 089230 | THE E&M | +12.5% | 1.000 |
| 040160 | 누리플렉스 | +11.2% | 0.980 |
| 092220 | KEC | +5.4% | 0.944 |
| 053030 | 바이넥스 | +6.7% | 0.761 |
| 085910 | 네오티스 | +21.3% | 0.746 |
| 067920 | 이글루 | +5.5% | 0.738 |
| 043340 | 에쎈테크 | +6.4% | 0.726 |
| 053080 | 케이엔솔 | +5.1% | 0.708 |

- **10건 감지** (연 기대 380건 → 일 평균 1.6건, 이날은 활발)
- Phase A D7 기준 부합: 등락 5%↑, 종가위치 0.70↑, 거래대금 상위

### 일관성 검증
```
D6: 1건 감지 (기대: 0~5건/일) → ✅ 정상
D7: 10건 감지 (기대: 0~10건/일) → ✅ 정상 상한선
```

> ⚠ D7 054620(APS)는 D6 상한가 종목과 중복 감지됨. 동일 종목 D6+D7 동시 매수 방지 로직 확인 필요.

---

## 5단계: 장애 시나리오 대비

| 시나리오 | 현황 | 권고 |
|---------|------|------|
| API 타임아웃 (10초 초과) | exception catch → log.error, 재시도 없음 | 3회 재시도 + backoff 추가 |
| 모의투자 API 점검 (일 06:30~08:00) | 08:50 시작으로 통상 문제 없음 | 시작 전 API 헬스체크 추가 권고 |
| 스크립트 비정상 종료 | 로그 파일만 기록 | 알림 메일/슬랙 추가 |
| DB 연결 실패 | psycopg2 exception → 전체 종료 | DB 연결 재시도 로직 추가 |
| 공휴일 실행 | 필터 없음 → API 오류 catch | 휴장일 필터 추가 |

### 수동 실행 방법
```bash
# 정상 실행
cd /root/kis-autotrade-v4
source venv/bin/activate
python scripts/live_paper_d6_d7.py

# 상태 확인 (로그)
tail -f /var/log/d6d7_paper.log

# 주문 없이 상태만 확인
python scripts/live_paper_d6_d7.py --status   # (플래그 추가 필요)
```

---

## 월요일 첫 실행 체크리스트

```
□ 08:45 KST: 서버 SSH 접속 가능 확인
□ 08:45 KST: /var/log/d6d7_paper.log 모니터링 준비
□ 08:50 KST: cron 자동 실행 (수동 확인 불필요)
□ 09:00 KST: 로그에 "D6 카드(#42) 로드" 메시지 확인
□ 09:00 KST: v4_paper_trades 테이블 자동 생성 확인
□ 15:20 KST: 매수 주문 실행 여부 로그 확인
□ D+1 09:01 KST: 매도 주문 실행 여부 로그 확인
□ D+1 09:10 KST: v4_paper_trades 결과 INSERT 확인
```

---

## 검수 결과

- [x] 모의투자 계좌 번호가 실계좌와 다른지 확인 (config_id=1, is_production=false)
- [x] PAPER_TRADE 모드 하드코딩 확인 (CONFIG.mode = 'PAPER')
- [x] 매수/매도 API가 모의투자 전용 URL 사용 확인 (VTTC prefix)
- [x] v4_positions에 INSERT/UPDATE 없음 확인
- [x] dry-run 결과 Phase A D6/D7 백테스트 시그널과 유사 (D6 1건, D7 10건)
- [ ] GitHub push: 보고서 push 완료 후 HTTP 200 확인

---

## 산출물 목록

| 파일 | 경로 |
|------|------|
| D6 시그널 | /tmp/live_paper_precheck_d6_signals.json |
| D7 시그널 | /tmp/live_paper_precheck_d7_signals.json |
| Dry-run 로그 | /tmp/live_paper_precheck_dryrun_log.txt |
| 환경 감사 | /tmp/live_paper_precheck_env_audit.json |
