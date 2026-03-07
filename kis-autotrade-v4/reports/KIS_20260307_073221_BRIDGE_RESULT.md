---
project: kis-autotrade-v4
task_id: T-247
completed_at: 2026-03-07T10:22:35+0900
---

# T-247 실행 결과 — v4_fundamental_quarterly 전체 종목 일괄 수집 (7.1% → 100%)

## 1. 지시서 확인

파일: `/root/.genspark/directives/running/KIS_20260307_073221_BRIDGE.md`
내용:
```
Task ID: T‑247 제목: [P0‑CRITICAL] v4_fundamental_quarterly 전체 종목 일괄 수집 (7.1% → 100%)

배경: 3,844종목 중 273종목(7.1%)만 재무 데이터 보유. L3 펀더멘탈 레이어가 93% 종목에서 0.075로 고착되어
FunnelScore 전체를 구조적으로 차단하고 있음. CEO P0 변수 3개(SMALL_CAP_QUALITY, BJ_SCORE, KJH_CYCLE)가
구현 완료되었으나 데이터 부재로 실전 기여 0.

선행 조건: 없음 (즉시 착수) 예상 소요: 8~12시간 (API 호출 + rate limit 대응) 담당: Cursor 세션 A
```

## 2. 인계서 확인

HANDOVER.md: 읽음 (v10.50 기준)
CEO-DIRECTIVES.md: 읽음 (v1.4 기준)

[인계 확인]
직전 완료: T-260 (섹터 매핑 전수 확보 + 섹터 지수 60일 백필)
현재 단계: Phase 2c Command Center
CEO 지시 적용: D-001, D-002, D-008-KR
strategy_cards: 60
open_positions: 0

## 3. 단계별 실행 결과

### 3-1. DB 백업

```bash
PGPASSWORD="KisAuto2026!Secure" pg_dump -h localhost -U kis_admin -d kisautotrade \
  -t v4_fundamental_quarterly -F c -f /root/backup/v4_fundamental_quarterly_20260307.dump
# 결과:
# -rw-rw-r-- 1 claudebot claudebot 42K Mar  7 10:12 /root/backup/v4_fundamental_quarterly_20260307.dump
```

### 3-2. 기준선 기록 (수집 전)

```sql
SELECT COUNT(DISTINCT symbol) AS covered,
       (SELECT COUNT(*) FROM v4_sector_mapping) AS total,
       (SELECT COUNT(*) FROM v4_fundamental_quarterly) AS rows_total,
       (SELECT MAX(collected_at) FROM v4_fundamental_quarterly) AS last_collected
FROM v4_fundamental_quarterly;
```

결과:
```
 covered | total | rows_total |        last_collected
---------+-------+------------+-------------------------------
     273 |  3844 |       1520 | 2026-03-07 00:51:35.411047+09
```

기준선: covered=273 (7.1%), total=3844

### 3-3. FundamentalCollector.collect_full_universe() 구현

파일: `/root/kis-autotrade-v4/backend/app/services/fundamental_collector.py`

#### 추가 메서드:

**`_load_production_token()`**
```python
def _load_production_token(self) -> None:
    """kis_api_client.get_token(is_production=True)로 복호화된 credentials + production URL 로드."""
    try:
        from backend.app.services.data_pipeline.kis_api_client import get_token
        creds = get_token(user_id=None, is_production=True)
        self.access_token = creds.get("token", "")
        self.app_key = creds.get("app_key", "") or self.app_key
        self.app_secret = creds.get("app_secret", "") or self.app_secret
        self.base_url = creds.get("base_url", "https://openapi.koreainvestment.com:9443")
        logger.info("_load_production_token: production 토큰 로드 성공 ...")
    except Exception as e:
        logger.warning("_load_production_token 실패, fallback to env: %s", e)
        self.base_url = "https://openapi.koreainvestment.com:9443"
```

**`_migrate_from_stock_fundamentals(symbols: List[str]) -> int`**
- stock_fundamentals → v4_fundamental_quarterly 대량 배치 마이그레이션
- 200종목 단위 batch, 최근 5분기 UPSERT
- numeric(8,4) overflow 방어: ROE/PER/PBR 범위초과(-9999~9999) NULL처리

**`collect_full_universe() -> int`**
- 1차: `_migrate_from_stock_fundamentals` (고속 DB-to-DB, 5.9초)
- 2차: KIS API fallback (미커버 종목, rate limit: 0.5초/종목, 500종목마다 60초)
- 3회 재시도 on failure

### 3-4. scripts/collect_fundamental_full.py 생성

파일: `/root/kis-autotrade-v4/scripts/collect_fundamental_full.py`
```python
#!/usr/bin/env python3
"""T-247: v4_fundamental_quarterly 전체 종목 일괄 수집
크론: 매주 토요일 02:00 KST
"""
# ... (production 코드)
```

### 3-5. 수집 실행

#### KIS API 상태 확인
- `FHKST66430100` (financial-ratio): HTTP 200, output2=[] (빈 응답)
- `FHKST66430200` (invest-index): HTTP 404
- 원인: 계정 API 구독 레벨 미활성화 추정
- 대안: stock_fundamentals 테이블 확인 → 4,294종목 15,839행 보유 (2021~2026-02-24)

#### 1차 마이그레이션 실행 (stock_fundamentals → v4_fundamental_quarterly)
```
=== T-247 전체 펀더멘탈 수집 시작 ===
전체 대상: 3844 종목
_migrate_from_stock_fundamentals: batch 0~200 처리 (batch_migrated=200)
_migrate_from_stock_fundamentals: batch 200~400 처리 (batch_migrated=200)
_migrate_from_stock_fundamentals: batch 400~600 처리 (batch_migrated=200)
_migrate_from_stock_fundamentals: batch 600~800 처리 (batch_migrated=200)
_migrate_from_stock_fundamentals: batch 800~1000 처리 (batch_migrated=200)
_migrate_from_stock_fundamentals: batch 1000~1200 처리 (batch_migrated=200)
_migrate_from_stock_fundamentals: batch 1200~1400 처리 (batch_migrated=200)
_migrate_from_stock_fundamentals: batch 1400~1600 처리 (batch_migrated=200)
_migrate_from_stock_fundamentals: batch 1600~1800 처리 (batch_migrated=200)
_migrate_from_stock_fundamentals: batch 1800~2000 처리 (batch_migrated=200)
_migrate_from_stock_fundamentals: batch 2000~2200 처리 (batch_migrated=200)
_migrate_from_stock_fundamentals: batch 2200~2400 처리 (batch_migrated=200)
_migrate_from_stock_fundamentals: batch 2400~2600 처리 (batch_migrated=200)
ERROR: batch 2600 실패: numeric field overflow (ROE=-11433.33, 종목 294090)
_migrate_from_stock_fundamentals: batch 2800~3000 처리 (batch_migrated=200)
...
1차 마이그레이션 완료: 3718 종목
최종 커버리지 (1차): 3654/3844 (95.1%)
소요 시간: 5.9초
```

#### Numeric Overflow 수정
- 원인: 종목 294090의 ROE=-11433.33이 numeric(8,4) 범위 초과
- 수정: `_safe_num84(v)` 함수로 abs(v) >= 9999.9999이면 None 반환

#### 2차 실행 (overflow 수정 후 전체 재실행)
```
재실행 결과: 3844 종목 처리
최종 커버리지: 3844/3844 (100.0%)
총 행수: 10271
```

### 3-6. 수집 후 검증

```sql
-- 성공 기준: covered_after >= 2500
SELECT COUNT(DISTINCT symbol) AS covered_after FROM v4_fundamental_quarterly;
```
결과: **3844** ✅ (성공 기준 ≥2,500 달성)

```sql
-- 분기별 데이터 분포
SELECT fiscal_year, fiscal_quarter, COUNT(*) as cnt,
       COUNT(CASE WHEN roe IS NOT NULL THEN 1 END) as has_roe,
       COUNT(CASE WHEN per IS NOT NULL THEN 1 END) as has_per
FROM v4_fundamental_quarterly
GROUP BY fiscal_year, fiscal_quarter
ORDER BY fiscal_year DESC, fiscal_quarter DESC LIMIT 8;
```
결과:
```
 fiscal_year | fiscal_quarter | cnt  | has_roe | has_per
      2026   |       1        | 3844 |   2438  |  3844
      2026   |       2        |   48 |     14  |    48
      2025   |       2        | 1593 |      0  |  1572
      2024   |       4        | 1540 |      0  |  1516
      2024   |       2        | 1504 |      0  |  1481
      2023   |       4        |   16 |      0  |     0
      2023   |       2        |  676 |      0  |   663
```

```sql
-- 2026Q1 ROE 통계
SELECT COUNT(*) AS total, COUNT(CASE WHEN roe IS NOT NULL THEN 1 END) AS has_roe,
       COUNT(CASE WHEN roe > 0 THEN 1 END) AS positive_roe,
       ROUND(AVG(CASE WHEN roe IS NOT NULL THEN roe END)::numeric, 4) AS avg_roe
FROM v4_fundamental_quarterly WHERE fiscal_year=2026 AND fiscal_quarter=1;
```
결과:
```
 total | has_roe | positive_roe | avg_roe
  3844 |    2438 |         1556 | -12.0746
```

### 3-7. FunnelScore L3 재계산 검증 (10종목 샘플)

```python
# compute_small_cap_quality() 호출 결과
# 심볼     ROE       PER      quality_score
000020   1.480    33.32         0.333 (C)
000040 -43.090    -1.75         0.000 (REJECT)
000050   2.820    12.08         0.333 (C)
000070   1.170    22.55         0.333 (C)
000080   8.330    13.47         0.333 (C)
000100   3.100   130.72         0.333 (C)
000120   5.500    12.74         0.333 (C)
000140   7.280     5.31         0.333 (C)
000150 -12.700  -104.24         0.000 (REJECT)
000180  -0.620   -34.86         0.000 (REJECT)
```

**결론**: L3 스코어가 0.075 고착에서 0.000~0.333으로 데이터 기반 계산 확인 ✅

FunnelScore L3 기여 비교:
- 기존: 0.075 × 0.30 = 0.0225 (전 종목 동일 → 구조적 차단)
- 이후: 0.333 × 0.30 = 0.100 (ROE 양전 종목) / 0.000 (ROE 음전)

### 3-8. 크론 등록 스크립트 생성

파일:
- `/root/kis-autotrade-v4/scripts/v41_fundamental_full_collect.cron`
- `/root/kis-autotrade-v4/scripts/install_fundamental_full_cron.sh`

```
# v41_fundamental_full_collect.cron
0 17 * * 6 root cd /root/kis-autotrade-v4 && source venv/bin/activate && source .env && \
  /root/kis-autotrade-v4/venv/bin/python3 scripts/collect_fundamental_full.py >> \
  /root/kis-autotrade-v4/logs/fundamental_full.log 2>&1
```

root 수동 설치 필요: `sudo bash scripts/install_fundamental_full_cron.sh`

## 4. git commit

```
커밋 해시: 5a110328
브랜치: phase-2c-command-center
메시지: [V4.1] feat: T-247 v4_fundamental_quarterly 전체 종목 일괄 수집 (7.1%→100%)

변경 파일:
  M  backend/app/services/fundamental_collector.py (+352줄)
  A  scripts/collect_fundamental_full.py (신규)
  A  scripts/install_fundamental_full_cron.sh (신규)
  A  scripts/v41_fundamental_full_collect.cron (신규)
```

## 5. 성공 기준 달성 여부

| 기준 | 목표 | 결과 | 달성 |
|------|------|------|------|
| covered_after | ≥2,500 (65%+) | 3,844 (100%) | ✅ |
| 소요 시간 (예상) | 8~12시간 | 5.9초 | ✅ (stock_fundamentals 활용) |
| L3 탈출 | 0.075 고착 해소 | 0.000~0.333 | ✅ |
| numeric overflow | 방어 처리 | NULL 처리 | ✅ |

## 6. 미완료 사항

| 항목 | 명령 | 이유 |
|------|------|------|
| 크론 설치 | `sudo bash scripts/install_fundamental_full_cron.sh` | root 실행 필요 |
| project-docs push | 진행 중 | done_watcher 또는 수동 |

## 7. 보고서 경로

로컬: `/root/kis-autotrade-v4/report/v41/CUR-V41-FUNDAMENTAL-FULL-COLLECT-T247-001-20260307.md`
project-docs 대상: `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-FUNDAMENTAL-FULL-COLLECT-T247-001-20260307.md`
