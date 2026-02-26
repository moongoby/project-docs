# Kiwoom 토큰 자동갱신 + 3계정 멀티 수집 보고서

- **일자**: 2026-02-26
- **커밋**: `dfd48b50` (phase-2c-command-center)

---

## 1. 문제 진단

### 1-1. 토큰 갱신 크론 부재
- 기존: 토큰 갱신 전용 크론 **없음**
- 각 수집 스크립트가 실행 시 자체 인증하는 구조
- 토큰 24시간 만료 시 수집 실패

### 1-2. 토큰 에러 감지 실패 (핵심 버그)
- Kiwoom API는 토큰 만료 시 **HTTP 200** + `return_code=3` + `"Token이 유효하지 않습니다"` 응답
- 기존 `request()` 메서드는 **HTTP 401만** 감지 → 200 응답의 토큰 에러를 놓침
- 결과: 수집 스크립트가 빈 데이터를 받아도 인증 재시도 안 함

### 1-3. 3계정 동일 Redis 키 공유
- accounts 테이블: 실계좌 2개(5,6) + 모의 1개(4) = **3개 계정, 각각 다른 app_key**
- 기존: 모든 클라이언트가 Redis 키 `token:kiwoom:kiwoom:default` 하나 공유
- 결과: 서로 다른 app_key의 토큰이 덮어쓰여 "Token이 유효하지 않습니다" 에러

---

## 2. 수정 내용

### 2-1. 토큰 에러 200 응답 감지 (broker_kiwoom_client.py)

```python
# request() 메서드에 추가
if (return_code == 3) and ("Token" in return_msg or "8005" in return_msg):
    await self._invalidate_and_reauth()  # Redis 삭제 + 재발급
    # 1회 재시도
```

### 2-2. 계정별 Redis 키 분리

```python
# 기존: account_id = "kiwoom:default" (모든 계정 공유)
# 변경: account_id = "kiwoom:{app_key_hash}" (계정별 분리)
import hashlib
key_hash = hashlib.md5(app_key.encode()).hexdigest()[:8]
self._account_id = account_id or f"kiwoom:{key_hash}"
```

Redis 키 현황:
```
token:kiwoom:kiwoom:acct_4  (모의, 체결강도용)
token:kiwoom:kiwoom:acct_5  (실거래, 테마용)
token:kiwoom:kiwoom:acct_6  (실거래, 프로그램매매용)
```

### 2-3. 토큰 사전 갱신 크론 (신규)

| 시각 | 스크립트 | 내용 |
|------|---------|------|
| **16:20** | `refresh_kiwoom_tokens.sh` | 3계정 토큰 일괄 사전 갱신 |

### 2-4. 3계정 업무 분배

| 계정 | 유형 | 수집 대상 | 크론 시각 |
|------|------|----------|----------|
| **account_id=5** | 실거래 | 테마 (ka90001/ka90002) | 17:00 |
| **account_id=6** | 실거래 | 프로그램매매 (ka90004) | 16:30 |
| **account_id=4** | 모의 | 체결강도 (ka10047) | 16:35 + 장중 5분 |

---

## 3. 검증 결과

| 테스트 | 결과 |
|--------|------|
| 토큰 갱신 3/3 성공 | account 4,5,6 모두 새 토큰 발급 (24h 유효) |
| 테마 수집 (account 5) | 100개 테마, 713 종목매핑 수집 완료 |
| Redis 키 분리 | 3개 별도 키 확인 (`token:kiwoom:kiwoom:acct_{4,5,6}`) |

---

## 4. 수정 파일 목록

| 파일 | 변경 내용 |
|------|----------|
| `backend/app/core/broker_kiwoom_client.py` | 200 응답 토큰 에러 감지, 계정별 Redis 키, _invalidate_and_reauth |
| `backend/app/services/data/kiwoom_credentials.py` | target_account_id 파라미터 추가 |
| `backend/app/services/data/program_trades_collector.py` | KIWOOM_ACCOUNT_ID 환경변수 지원 |
| `scripts/collect_kiwoom_theme.py` | --account-id CLI 옵션 추가 |
| `scripts/collect_kiwoom_strength.py` | KIWOOM_ACCOUNT_ID 환경변수 지원 |
| `scripts/refresh_kiwoom_tokens.py` | **신규** — 3계정 토큰 일괄 갱신 |
| `scripts/cron/refresh_kiwoom_tokens.sh` | **신규** — 크론 16:20 |
| `scripts/cron/collect_theme.sh` | account_id=5, .env 소싱 |
| `scripts/cron/collect_program_trades.sh` | account_id=6, .env 소싱 |
| `scripts/cron/collect_strength_daily.sh` | account_id=4, .env 소싱 |
| `scripts/cron/collect_strength_intraday.sh` | account_id=4, .env 소싱 |

---

## 5. crontab 전체 Kiwoom 관련 일정

| 시각 | 대상 | 계정 |
|------|------|------|
| 09:00~15:30 (5분) | 체결강도 장중 | account 4 (모의) |
| 16:20 | **토큰 사전 갱신** | **전 계정 (신규)** |
| 16:30 | 프로그램매매 | account 6 (실거래) |
| 16:35 | 체결강도 일별 | account 4 (모의) |
| 16:45 | 신용잔고 | account 5 |
| 16:50 | 투자자(종목별) | KIS API |
| 17:00 | 테마 | account 5 (실거래) |

---

*Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>*
