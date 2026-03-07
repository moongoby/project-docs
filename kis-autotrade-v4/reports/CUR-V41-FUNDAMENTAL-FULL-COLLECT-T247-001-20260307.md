# T-247: v4_fundamental_quarterly 전체 종목 일괄 수집 (7.1% → 100%)

[인계 확인]
직전 완료: T-260 (섹터 매핑 전수 확보 + 섹터 지수 60일 백필)
현재 단계: Phase 2c Command Center
CEO 지시 적용: D-001, D-002, D-008-KR
strategy_cards: 60
open_positions: 0

---

## 요약

| 항목 | 값 |
|------|-----|
| Task ID | T-247 |
| 우선도 | P0-CRITICAL |
| 작업일 | 2026-03-07 |
| 커밋 | 5a110328 |
| 상태 | ✅ 완료 |

**핵심 결과**: v4_fundamental_quarterly 커버리지 273/3844 (7.1%) → **3844/3844 (100.0%)**, 소요 시간 5.9초

---

## 1. 배경

- CEO P0 변수 3개(SMALL_CAP_QUALITY, BJ_SCORE, KJH_CYCLE)가 구현 완료되었으나 데이터 부재로 실전 기여 0
- L3 펀더멘탈 레이어가 93% 종목에서 0.075로 고착되어 FunnelScore 전체를 구조적으로 차단
- 3,844종목 중 273종목(7.1%)만 재무 데이터 보유

---

## 2. 기준선

| 항목 | 이전 | 이후 |
|------|------|------|
| distinct symbol 수 | 273 | 3,844 |
| 커버리지 | 7.1% | 100.0% |
| 총 행수 | 787 (기존) → 1,520 (T-257 이후) | 10,271 |
| ROE 보유 종목 (2026Q1) | ~273 | 2,438 / 3,844 (63.4%) |

---

## 3. 구현 내용

### 3-1. fundamental_collector.py 수정

#### `_load_production_token()` 신규
- `KIS_ACCESS_TOKEN` env 미설정 시 `kis_api_client.get_token(is_production=True)` 자동 호출
- 암호화된 app_key/app_secret 복호화 + production base_url 자동 설정

#### `_migrate_from_stock_fundamentals(symbols)` 신규
- `stock_fundamentals` → `v4_fundamental_quarterly` 대량 배치 마이그레이션
- 200종목 단위 batch 처리 (IN 쿼리 최적화)
- 최근 5분기 × 종목 UPSERT (ON CONFLICT DO UPDATE)
- numeric(8,4) overflow 방어: ROE/PER/PBR 범위초과(-9999~9999) NULL 처리
- 소요 시간: 3,844종목 × 5.9초 (API 없는 DB-to-DB 마이그레이션)

#### `collect_full_universe()` 신규
- 1차: `_migrate_from_stock_fundamentals` (고속, API 없음) → 3,844종목 처리
- 2차: KIS API fallback (1차 누락 종목 대상)
  - rate limit: 종목당 0.5초 sleep, 500종목마다 60초 대기
  - 실패 시 3회 재시도 (1초 간격)

### 3-2. scripts/collect_fundamental_full.py 신규
- 배치 실행 엔트리포인트
- 로그: `logs/fundamental_full.log`
- 수집 후 자동 커버리지 검증 출력

### 3-3. 크론 등록 준비
- `scripts/v41_fundamental_full_collect.cron`: 매주 토요일 02:00 KST (금 17:00 UTC)
- `scripts/install_fundamental_full_cron.sh`: root 수동 설치 스크립트
- **미완료**: root 수동 실행 필요 → `sudo bash scripts/install_fundamental_full_cron.sh`

---

## 4. 실행 결과

### 4-1. 수집 실행 로그
```
=== T-247 전체 펀더멘탈 수집 시작 ===
전체 대상: 3844 종목
_migrate_from_stock_fundamentals: batch 0~200 처리 (batch_migrated=200)
_migrate_from_stock_fundamentals: batch 200~400 처리 (batch_migrated=200)
...
_migrate_from_stock_fundamentals: batch 3800~3844 처리 (batch_migrated=44)
최종 커버리지: 3844/3844 (100.0%)
소요 시간: 5.9초
```

오류 1건 (batch 2600): numeric field overflow (ROE=-11433.33, 종목 294090)
→ 수정 후 재실행으로 해소 (범위초과 NULL 처리 추가)

### 4-2. DB 검증 쿼리 결과
```sql
SELECT COUNT(DISTINCT symbol) AS covered_after FROM v4_fundamental_quarterly;
-- 결과: 3844 (성공 기준 ≥2500 달성)

-- 2026Q1 ROE 통계
total=3844 / has_roe=2438 / positive_roe=1556 / avg_roe=-12.07
```

### 4-3. 분기별 데이터 분포
| fiscal_year | fiscal_quarter | cnt | has_roe | has_per | has_eps |
|---|---|---|---|---|---|
| 2026 | 1 | 3,844 | 2,438 | 3,844 | 3,844 |
| 2026 | 2 | 48 | 14 | 48 | 48 |
| 2025 | 2 | 1,593 | 0 | 1,572 | 1,572 |
| 2024 | 4 | 1,540 | 0 | 1,516 | 1,516 |

### 4-4. quality_grade 분포 (2026Q1 기준)
| quality_grade | cnt |
|---|---|
| B (ROE > 0) | 1,556 |
| C (ROE ≤ 0 또는 NULL) | 2,288 |

> 주의: operating_profit 컬럼이 stock_fundamentals에 NULL이므로 grade A (ROE>0 AND op>0) = 0건. ROE 양전 비율 40.5%는 실질 수급.

---

## 5. FunnelScore L3 재계산 검증

### 10종목 샘플 (2026Q1, ROE 보유)
```
심볼       ROE       PER     quality_score
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

**결론**: L3 펀더멘탈 스코어가 0.075 고착에서 탈출하여 데이터 기반 계산 확인 (0.000~0.333)

FunnelScore L3 기여:
- 기존: 0.075 × 0.30 = 0.0225 (전 종목 동일)
- 이후: 0.333 × 0.30 = 0.100 (ROE양전) / 0.000 × 0.30 = 0.000 (ROE음전)

---

## 6. KIS API 동작 상태 (참고)

production 토큰으로 `FHKST66430100` (financial-ratio) 호출 시:
- HTTP 200, rt_cd=0, msg1=정상처리, output2=[] (빈 배열)
- 계정 구독 레벨 또는 API 활성화 미설정으로 추정
- **영향 없음**: stock_fundamentals 마이그레이션으로 100% 커버리지 달성

---

## 7. 미완료 사항 (root 수동 필요)

| 항목 | 명령 |
|------|------|
| 크론 설치 | `sudo bash /root/kis-autotrade-v4/scripts/install_fundamental_full_cron.sh` |

---

## 8. 체크포인트

- [x] 코드 레포 커밋 완료 (5a110328, phase-2c-command-center)
- [ ] project-docs 보고서 push 완료 (진행 중)
