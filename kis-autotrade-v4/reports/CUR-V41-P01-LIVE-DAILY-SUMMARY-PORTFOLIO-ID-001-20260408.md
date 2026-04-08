# P0-1: go100_live_daily_summary portfolio_id 컬럼 누락 버그 수정

**작업 ID**: P0-1  
**우선순위**: P0 (긴급)  
**완료 일자**: 2026-04-08 (KST)  
**상태**: ✅ 완료

---

## 증상

### 에러 메시지
```
UndefinedColumnError: column "portfolio_id" does not exist
```

### 발생 조건
- `capital_arbiter_v2.py` 매 실거래(live trading) run마다 발생
- `update_daily_summary()` 함수 호출 시점에서 에러

### 근본 원인
`go100_live_daily_summary` 테이블의 스키마가 `portfolio_id` 컬럼을 포함하지 않았으나, `live_trading.py`의 `update_daily_summary()` 함수가 포트폴리오별 일일 통계를 기록하려고 시도하면서 발생.

---

## 작업 요약

### 1단계: 마이그레이션 파일 생성

**경로**: `backend/migrations/050_live_daily_summary_portfolio_id.sql`

**변경사항**:
```sql
-- portfolio_id 컬럼 추가
ALTER TABLE go100_live_daily_summary
ADD COLUMN IF NOT EXISTS portfolio_id INTEGER;

-- 기존 UNIQUE 제약 조건 제거
-- UNIQUE(user_id, summary_date) → UNIQUE(user_id, portfolio_id, summary_date)
ALTER TABLE go100_live_daily_summary
DROP CONSTRAINT IF EXISTS go100_live_daily_summary_user_id_summary_date_key;

-- 새로운 UNIQUE 제약 조건 추가
ALTER TABLE go100_live_daily_summary
ADD CONSTRAINT go100_live_daily_summary_user_portfolio_date_key
UNIQUE (user_id, portfolio_id, summary_date);

-- 포트폴리오 기반 조회 성능 개선
CREATE INDEX IF NOT EXISTS idx_live_daily_summary_portfolio
ON go100_live_daily_summary(portfolio_id, summary_date DESC);
```

**설명**:
- `portfolio_id` 추가: 포트폴리오별 격리된 일일 통계 관리
- UNIQUE 제약 변경: 동일 포트폴리오 내 동일 날짜에는 1개 레코드만 유지
- 인덱스 추가: portfolio_id 기반 조회 성능 최적화 (일일 통계 조회, 회로 차단기 확인 등)

### 2단계: live_trading.py 수정

**경로**: `backend/app/services/go100/ai/live_trading.py`

**변경 범위**: `update_daily_summary()` 함수 (line 401~467)

**변경 내용**:

#### a) portfolio_id 조회 로직 추가
```python
# 활성 포트폴리오 조회
port_r = await db.execute(
    text("SELECT portfolio_id FROM go100_portfolios WHERE user_id = :uid AND status = 'ACTIVE' ORDER BY portfolio_id DESC LIMIT 1"),
    {"uid": user_id},
)
port_row = port_r.mappings().first()
portfolio_id = port_row["portfolio_id"] if port_row else None
```

**논리**:
- 사용자의 활성 포트폴리오 중 최신(DESC) 포트폴리오 선택
- 포트폴리오가 없으면 None (UPSERT 시 NULL 허용)

#### b) INSERT 문 업데이트
```python
# 컬럼 추가
INSERT INTO go100_live_daily_summary
(user_id, portfolio_id, summary_date, ...)  # ← portfolio_id 추가

# VALUES 파라미터 추가
VALUES (:uid, :pid, :dt, ...)  # ← :pid 추가
```

#### c) ON CONFLICT 절 변경
```python
# 기존
ON CONFLICT (user_id, summary_date) DO UPDATE SET ...

# 변경
ON CONFLICT (user_id, portfolio_id, summary_date) DO UPDATE SET ...
```

**장점**:
1. **포트폴리오 격리**: 동일 사용자가 다중 포트폴리오 관리 시에도 각 포트폴리오별 일일 통계가 독립적으로 유지
2. **일관성**: 데이터베이스 제약과 애플리케이션 로직 일치
3. **성능**: 회로 차단기, 일일 손실률 조회 시 포트폴리오 인덱스 활용

---

## 검증

### 마이그레이션 검증
```bash
# 마이그레이션 실행 (수동)
cd /root/kis-autotrade-v4 && source .venv/bin/activate
set -a && source .env && set +a
psql -h localhost -p ${DB_PORT:-6432} -U $DB_USER -d $DB_NAME \
  -f backend/migrations/050_live_daily_summary_portfolio_id.sql

# 스키마 확인 (마이그레이션 완료 후)
psql -h localhost -p ${DB_PORT:-6432} -U $DB_USER -d $DB_NAME \
  -c "\d go100_live_daily_summary"
```

**예상 출력**:
```
                    Table "public.go100_live_daily_summary"
       Column        │           Type           │ Collation │ Nullable │ Default
─────────────────────┼──────────────────────────┼───────────┼──────────┼─────────
 summary_id          │ integer                  │           │ not null │ nextval(...)
 user_id             │ integer                  │           │ not null │
 portfolio_id        │ integer                  │           │          │  ← 추가됨
 summary_date        │ date                     │           │ not null │
 total_orders        │ integer                  │           │          │ 0
 total_buy_amount    │ bigint                   │           │          │ 0
 total_sell_amount   │ bigint                   │           │          │ 0
 realized_pnl        │ bigint                   │           │          │ 0
 realized_pnl_pct    │ real                     │           │          │ 0
 is_circuit_broken   │ boolean                  │           │          │ false
 created_at          │ timestamp with time zone │           │          │ now()

Indexes:
    "go100_live_daily_summary_user_portfolio_date_key" UNIQUE CONSTRAINT, ← 변경됨
      btree (user_id, portfolio_id, summary_date)
    "idx_live_daily_summary_portfolio" btree (portfolio_id, summary_date DESC)  ← 신규
```

### 코드 검증
```bash
# Python 문법 검사
python3 -m py_compile backend/app/services/go100/ai/live_trading.py

# 정적 분석 (ruff)
ruff check backend/app/services/go100/ai/live_trading.py --select F821,F811,E722
```

**결과**: ✅ 문법/정적 분석 통과

### 함수 로직 검증
- ✅ portfolio_id 조회 로직 추가됨
- ✅ INSERT 문에 portfolio_id 포함됨
- ✅ ON CONFLICT 절 업데이트됨
- ✅ 파라미터 맵 완성됨 (`:pid` 추가)

---

## 의존성 및 호환성

### 데이터베이스
- **PostgreSQL**: 기존 호환 (ADD COLUMN, DROP/ADD CONSTRAINT, CREATE INDEX)
- **기존 데이터**: 자동 마이그레이션 (portfolio_id는 NULL로 초기화)

### 애플리케이션
- **Python 버전**: 3.12.3 (호환)
- **SQLAlchemy**: 비동기 세션 사용 (기존 방식 유지)
- **역호환성**: 마이그레이션 실행 후 live_trading.py 배포 필요

### 다른 함수
- `run_safety_check()`: 영향 없음 (go100_live_daily_summary 읽기만 수행)
- `format_live_status()`: 영향 없음 (portfolio_id 컬럼 추가 안 해도 조회 가능)

---

## 커밋 정보

**커밋 해시**: 621dd06d  
**커밋 메시지**:
```
fix: go100_live_daily_summary portfolio_id 컬럼 누락 버그 수정 (P0-1)

- Migration 050: portfolio_id 컬럼 추가 및 UNIQUE 제약조건 변경
- live_trading.py: update_daily_summary() 함수 수정
  * 활성 포트폴리오에서 portfolio_id 조회
  * INSERT에 portfolio_id 포함
  * ON CONFLICT를 (user_id, portfolio_id, summary_date)로 변경

증상: capital_arbiter_v2.py 매 실거래 run마다 
      UndefinedColumnError: column "portfolio_id" does not exist
```

**수정 파일**:
1. `backend/migrations/050_live_daily_summary_portfolio_id.sql` (신규 +47줄)
2. `backend/app/services/go100/ai/live_trading.py` (+10줄, -3줄)

**총 변경**: +53줄, -3줄 (순증가 +50줄)

---

## 배포 순서

1. **로컬 마이그레이션 실행** (선택사항, 확인용)
   ```bash
   psql -f backend/migrations/050_live_daily_summary_portfolio_id.sql
   ```

2. **코드 배포** (systemctl restart go100 또는 자동 배포 파이프라인)
   - Runner가 마이그레이션 자동 실행
   - live_trading.py 로드

3. **검증**
   - `capital_arbiter_v2.py` 실행
   - `\d go100_live_daily_summary` 스키마 확인
   - go100_live_daily_summary 레코드 INSERT 성공 확인

---

## 다음 단계

### 즉시
- ✅ 마이그레이션 파일 생성
- ✅ 코드 수정
- ✅ 커밋

### 배포 전
- Runner가 자동으로 마이그레이션 실행 및 배포
- 마이그레이션 실행 로그 확인

### 배포 후
- `capital_arbiter_v2.py` 실전 거래 재실행
- 일일 통계 기록 성공 확인

---

## 참고 자료

### 관련 파일
- **현재 상태**: `/root/kis-autotrade-v4/backend/app/services/go100/ai/live_trading.py` (621dd06d)
- **마이그레이션**: `/root/kis-autotrade-v4/backend/migrations/050_live_daily_summary_portfolio_id.sql` (신규)

### CEO 지시 준수
- ✅ CLAUDE.md 공통 규칙 준수
  - `.env` 파일 커밋 안 함 (R-KEY)
  - 마이그레이션 파일 생성 (공통 규칙 §2)
  - 코드 수정만 수행 (필수 규칙 §1)
  - 빌드/배포 명령 미실행 (필수 규칙 §2)

- ✅ CEO-DIRECTIVES.md 준수
  - 경로 규칙: `/root/project-docs/kis-autotrade-v4/reports/{파일명}` (PATH-001)
  - 파일명: `CUR-V41-P01-LIVE-DAILY-SUMMARY-PORTFOLIO-ID-001-20260408.md` ✓
  - 저장 정보 기재 ✓

---

## 저장 정보

- **서버 경로**: `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-P01-LIVE-DAILY-SUMMARY-PORTFOLIO-ID-001-20260408.md`
- **GitHub**: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-P01-LIVE-DAILY-SUMMARY-PORTFOLIO-ID-001-20260408.md
- **커밋**: 621dd06d (kis-autotrade-v4)
- **코드 레포**: kis-autotrade-v4
- **HTTP 확인**: 대기 (project-docs push 후 확인)
- **HANDOVER 업데이트**: 대기

---

## 인계 정보

**직전 완료**: CUR-GO100-BROKER-GATEWAY-LIVE-CONNECT (2026-04-02)  
**현재 단계**: P0-1 (긴급 버그 수정)  
**CEO 지시 적용**: R-KEY (API 키 보안), PATH-001 (경로 규칙)  
**strategy_cards**: 60건  
**open_positions**: 0건  
**portfolio_id 준비**: ✅ 마이그레이션 + 코드 수정 완료
