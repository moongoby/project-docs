# 키움증권 REST API 데이터 수집 보고서

**작성일**: 2026-02-25
**목적**: KIS API에서 제공하지 않는 데이터를 키움증권 REST API를 통해 수집하고, 관련 인프라(자격증명 공통 모듈, 수집 스크립트, 기존 컬렉터 리팩터링)를 구축한 작업 보고

**작업·반영 이력**

| 일자 | 내용 |
|------|------|
| 2026-02-25 | 최초 작성: 키움 API 인증·테마·체결강도 수집 및 컬렉터 리팩터링 완료 보고 |

---

## 1. 배경 및 목적

### 1.1 배경

kis-autotrade-v4 프로젝트의 백테스트·실매매 엔진은 다양한 시장 데이터를 필요로 한다.
기존에는 한국투자증권(KIS) REST API를 주 데이터 소스로 사용했으나, 아래 데이터는 KIS에서 제공되지 않아 키움증권 REST API를 통해 보완이 필요했다.

| 데이터 | KIS 제공 여부 | 키움 API ID | 비고 |
|--------|:---:|:---:|------|
| 테마 그룹 목록 | ✕ | ka90001 | 전체 테마 코드·이름·등락률 |
| 테마 구성 종목 | ✕ | ka90002 | 테마별 종목 코드·주도주 여부 |
| 체결강도 일별 이력 | ✕ | ka10047 | 종목별 최대 60일간 일별 체결강도 |
| 종목별 프로그램매매 | ✕ | ka90004 | 시장 전체 프로그램 매수·매도·순매수 |

### 1.2 목적

1. 키움증권 API 인증 체계를 DB 기반으로 구축 (환경변수 빈 상태에서도 동작)
2. 테마 데이터 수집 → `v4_theme_master`, `v4_theme_stock`, `v4_theme_detail` 테이블 적재
3. 체결강도 일별 이력 수집 → `v4_trade_strength_history` 테이블 적재
4. 기존 키움 컬렉터 4종을 공통 자격증명 모듈로 리팩터링
5. 프로그램매매 컬렉터 API ID 오류 수정 (ka90003 → ka90004)

---

## 2. 키움 API 인증 체계

### 2.1 자격증명 저장 구조

키움증권 API 키는 `.env` 파일이 아닌 **DB `accounts` 테이블**에 암호화 저장되어 있다.

| account_id | broker_type | is_mock | is_active | account_number | 비고 |
|:---:|:---:|:---:|:---:|:---:|------|
| 4 | KIWOOM | true | true | 81201280 | 모의계좌 |
| 5 | KIWOOM | false | true | 52568156 | **실거래 (사용)** |
| 6 | KIWOOM | false | true | 63109343 | 실거래 |

- **암호화**: `enc_app_key` / `enc_app_secret` 컬럼 → `CryptoService` (Fernet, `ENCRYPTION_KEY` 환경변수) 복호화
- **인증 흐름**: `POST https://api.kiwoom.com/oauth2/token` → Bearer Token (23시간 TTL, Redis 캐시)

### 2.2 공통 자격증명 모듈 신규 생성

**파일**: `backend/app/services/data/kiwoom_credentials.py`

```
우선순위:
  1) 환경변수 KIWOOM_APP_KEY / KIWOOM_APP_SECRET (비어있으면 →)
  2) DB accounts 테이블에서 KIWOOM + is_active=true + is_mock=false 계정 복호화

반환: KiwoomBrokerClient 인스턴스 (또는 None)
```

- 모든 키움 데이터 컬렉터가 이 모듈을 `import`하여 자격증명 로직 중복 제거
- `_load_from_db()`: `psycopg2` → `accounts` 테이블 → `crypto_service.decrypt()` → 클라이언트 생성

### 2.3 해결한 인증 이슈

| 이슈 | 원인 | 해결 |
|------|------|------|
| "투자구분(실전/모의)이 달라서 Token를 사용할수가 없습니다" | Redis에 모의계좌 토큰이 캐싱된 상태에서 실거래 API 호출 | Redis `token:kiwoom:*`, `token_lock:kiwoom:*` 키 삭제 후 재인증 |
| `.env` KIWOOM_APP_KEY 비어있음 | 키가 DB에만 저장됨 | DB 폴백 로직 추가 (kiwoom_credentials.py) |

---

## 3. 데이터 수집 결과

### 3.1 테마 데이터 (ka90001 + ka90002)

**수집 스크립트**: `scripts/collect_kiwoom_theme.py`

| 항목 | 결과 |
|------|------|
| API | ka90001 (테마그룹별요청) + ka90002 (테마구성종목요청) |
| 엔드포인트 | `POST /api/dostk/thme` |
| 테마 그룹 수 | **100개** → `v4_theme_master` |
| 테마-종목 매핑 | **569건** (100개 테마, 472개 종목) → `v4_theme_stock` |
| 테마 상세 (raw JSON) | **100건** → `v4_theme_detail` |
| 실패 | 0건 |
| 수집 일시 | 2026-02-25 |

**DB 적재 현황**:

| 테이블 | 행 수 | 주요 컬럼 |
|--------|------:|------|
| `v4_theme_master` | 100 | theme_code, theme_name, is_active, last_updated |
| `v4_theme_stock` | 569 | theme_code, stock_code, stock_name, is_leader, mapped_date |
| `v4_theme_detail` | 100 | theme_code, theme_name, detail (JSONB), collected_at |

### 3.2 체결강도 일별 이력 (ka10047)

**수집 스크립트**: `scripts/collect_kiwoom_strength.py`

| 항목 | 결과 |
|------|------|
| API | ka10047 (체결강도추이일별) |
| 엔드포인트 | `POST /api/dostk/mrkcond` |
| 대상 종목 | **3,844개** (stock_universe 활성 종목 전체) |
| 수집 데이터 | **219,892건** (종목당 평균 ~59일) |
| DB 신규 삽입 | **219,328건** |
| 데이터 범위 | 2025-11-26 ~ 2026-02-24 (약 60 거래일) |
| 유효 종목 수 | 3,757개 (비거래 종목 제외) |
| 실패 | **0건** |
| 소요 시간 | 576초 (약 9.6분) |
| 처리 속도 | ~6.7 stocks/s (rate limit 준수) |

**DB 적재 현황**:

| 테이블 | 행 수 | 주요 컬럼 |
|--------|------:|------|
| `v4_trade_strength_history` | 219,892 | stock_code, recorded_at, strength, buy_amount |

### 3.3 프로그램매매 (ka90004) — 컬렉터 수정 완료, 데이터 장중 수집 예정

| 항목 | 상태 |
|------|------|
| API | ka90004 (종목별프로그램매매현황) |
| 엔드포인트 | `POST /api/dostk/stkinfo` |
| 컬렉터 | `backend/app/services/data/program_trades_collector.py` (수정 완료) |
| 현재 데이터 | **0건** (장마감 후 API가 빈 응답 반환) |
| 수집 예정 | 장중 16:30 자동 수집 시 적재 |

---

## 4. 코드 변경 내역

### 4.1 신규 생성 파일 (3건)

| 파일 | 용도 | 줄 수 |
|------|------|:---:|
| `backend/app/services/data/kiwoom_credentials.py` | 키움 자격증명 공통 로더 (env → DB 폴백) | 90 |
| `scripts/collect_kiwoom_theme.py` | 테마 수집 스크립트 (ka90001 + ka90002) | 345 |
| `scripts/collect_kiwoom_strength.py` | 체결강도 일별 이력 수집 스크립트 (ka10047) | 211 |

### 4.2 수정 파일 (4건)

| 파일 | 변경 내용 |
|------|------|
| `backend/app/services/data/program_trades_collector.py` | API ID ka90003→**ka90004** 수정, 경로 `/api/dostk/stkinfo` 수정, bulk fetch 방식 변경, `_get_kiwoom_client()` → 공통 모듈 사용, `is_active = 1` → `= true` 수정 |
| `backend/app/services/data/theme_detail_collector.py` | `_get_kiwoom_client()` → 공통 `kiwoom_credentials` 모듈 사용 |
| `backend/app/services/data/tick_data_collector.py` | `_get_kiwoom_client()` → 공통 `kiwoom_credentials` 모듈 사용 |
| `backend/app/services/data/condition_search_collector.py` | `_get_kiwoom_client()` → 공통 `kiwoom_credentials` 모듈 사용 |

### 4.3 컬렉터 의존 구조 (변경 후)

```
kiwoom_credentials.py (공통)
  ├── program_trades_collector.py  (ka90004)
  ├── theme_detail_collector.py    (ka90002)
  ├── tick_data_collector.py       (실시간)
  └── condition_search_collector.py (조건검색)

scripts/ (독립 수집)
  ├── collect_kiwoom_theme.py      (ka90001 + ka90002)
  └── collect_kiwoom_strength.py   (ka10047)
```

---

## 5. 키움 REST API 검증 결과

### 5.1 검증 완료 API

| API ID | 이름 | 경로 | 상태 | 비고 |
|:---:|------|------|:---:|------|
| ka90001 | 테마그룹별요청 | `/api/dostk/thme` | **정상** | 100개 테마 반환 |
| ka90002 | 테마구성종목요청 | `/api/dostk/thme` | **정상** | 테마별 구성종목 반환 |
| ka90004 | 종목별프로그램매매현황 | `/api/dostk/stkinfo` | **정상** (장중만) | 장마감 후 빈 응답 |
| ka10047 | 체결강도추이일별 | `/api/dostk/mrkcond` | **정상** | 60일 이력 반환 |

### 5.2 장중 전용 API (현재 수집 불가)

| API ID | 이름 | 상태 | 비고 |
|:---:|------|:---:|------|
| ka10046 | 체결강도추이시간별 | 장중만 | 장 시간 외 0건 |
| ka90004 | 종목별프로그램매매현황 | 장중만 | 장마감 후 빈 배열 |

### 5.3 미사용 확인 API

| API ID | 이름 | 상태 |
|:---:|------|:---:|
| ka90003 | 프로그램순매수상위50 | **URI 불일치** — 해당 엔드포인트에서 지원하지 않는 API ID |

---

## 6. 전체 데이터 인벤토리 현황

수집 작업 완료 후 주요 테이블 현황:

| 테이블 | 행 수 | 데이터 소스 | 상태 |
|--------|------:|:---:|:---:|
| `stock_universe` (활성) | 3,844 | KIS | 완료 |
| `ohlcv_daily` | 2,604,226 | KIS | 완료 |
| `v4_investor_daily` | 171,261 | KIS | 완료 |
| `v4_sector_daily` | 14,999 | KIS | 완료 |
| `v4_theme_master` | 100 | **키움** | **신규** |
| `v4_theme_stock` | 569 | **키움** | **신규** |
| `v4_theme_detail` | 100 | **키움** | **신규** |
| `v4_trade_strength_history` | 219,892 | **키움** | **신규** |
| `v4_program_trades` | 0 | **키움** | 장중 수집 예정 |

---

## 7. 실행 방법

### 7.1 테마 수집

```bash
cd /root/kis-autotrade-v4
source .venv/bin/activate
PYTHONPATH=/root/kis-autotrade-v4 python scripts/collect_kiwoom_theme.py
# 옵션: --max-themes 10   (테마 수 제한)
#       --test-auth        (인증 테스트만)
```

### 7.2 체결강도 일별 이력 수집

```bash
cd /root/kis-autotrade-v4
source .venv/bin/activate
PYTHONPATH=/root/kis-autotrade-v4 python scripts/collect_kiwoom_strength.py
# 옵션: --max-stocks 100   (종목 수 제한)
#       --batch-size 100    (DB 저장 배치 크기)
```

### 7.3 프로그램매매 수집 (장중)

```python
from backend.app.services.data.program_trades_collector import run_program_trades_collect
result = run_program_trades_collect()  # 장마감 후 16:30 1회
```

---

## 8. 향후 과제

| 우선순위 | 항목 | 상태 |
|:---:|------|:---:|
| P0 | 프로그램매매 장중 자동 수집 cron 설정 (16:30) | 미착수 |
| P1 | 테마 데이터 일 1회 자동 수집 cron 설정 (17:00) | 미착수 |
| P1 | 체결강도 일별 이력 증분 수집 (신규 데이터만) | 미착수 |
| P2 | 체결강도 시간별 (ka10046) 장중 수집 | 미착수 |
| P2 | 키움 API 추가 활용 (신용잔고, 공매도, 업종지수 등) | 미착수 |

---

## 보고 요약

- **키움증권 REST API** 인증 체계를 DB 암호화 자격증명 기반으로 구축
- **테마 데이터** 100개 그룹, 569건 종목 매핑, 100건 상세 정보 신규 수집 완료
- **체결강도 일별 이력** 3,757종목 × 60일 = 219,892건 신규 수집 완료 (0건 실패)
- **공통 모듈** `kiwoom_credentials.py` 생성, 기존 컬렉터 4종 리팩터링 완료
- **프로그램매매 컬렉터** API ID 오류 수정 (ka90003 → ka90004), 장중 수집 준비 완료
- **총 변경 파일**: 신규 3건 + 수정 4건 = **7건**
