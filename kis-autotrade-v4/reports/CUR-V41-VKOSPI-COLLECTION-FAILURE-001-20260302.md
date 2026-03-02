# CUR-V41-VKOSPI-COLLECTION-FAILURE-001 — 공공데이터 API 수집 미완료 원인 조사
> 작성일: 2026-03-02 | 담당: Claude Code Sonnet 4.6 | 레포: kis-autotrade-v4

---

[인계 확인]
직전 완료: CUR-V41-ADDL-INVESTIGATION-002
현재 단계: VKOSPI 공공데이터 수집 장애 조사
CEO 지시 적용: D-001(단순사고 금지), D-002(보고서 push 필수)
strategy_cards: 60개
open_positions: 14개

---

## 1. 결론 요약

> **공공데이터 API 자체는 정상 (24시간 서비스 중)**
> **원인: API 데이터 게재 T+1~T+2 영업일 지연 + 수집 스크립트 end_date 설계 결함 + 레짐 동기화 컬럼 오버플로 오류**

---

## 2. 현황 확인

### DB 수집 상태

```sql
SELECT COUNT(*), MAX(date), MIN(date) FROM v4_vkospi_daily;
-- count=1510, MAX=20260226, MIN=20200102
```

| 항목 | 값 |
|------|-----|
| 총 수집 건수 | 1,510건 |
| 최신 수집일 | **2026-02-26 (목)** |
| 오늘 날짜 | 2026-03-02 (월) |
| 누락 거래일 | **2026-02-27 (금)** — 1일 누락 |

### 최근 수집 이력 (created_at 기준)

| VKOSPI 날짜 | DB 저장 시각 | 지연 |
|-------------|-------------|------|
| 20260220 (목) | 2026-02-23 18:30 (월) | **T+2 영업일** |
| 20260223 (월) | 2026-02-25 18:30 (수) | **T+2 영업일** |
| 20260224 (화) | 2026-02-26 18:30 (목) | **T+2 영업일** |
| 20260225 (수) | 2026-02-27 09:50 (금) | **T+2 영업일** |
| 20260226 (목) | 2026-02-27 09:50 (금) | **T+1 영업일** |
| **20260227 (금)** | **미수집** | — |

→ **API는 VKOSPI 데이터를 T+1~T+2 영업일 후 게재**

---

## 3. 원인 분석

### 원인 1: 공공데이터 API 데이터 게재 지연 [핵심]

**직접 API 호출로 확인**:
```
GET apis.data.go.kr/.../getDerivationProductMarketIndex
  beginBasDt=20260224, endBasDt=20260302, idxNm=코스피 200 변동성지수
  → totalCount: 5 (20260220~20260226만 반환, 20260227 미포함)
```

```
GET ... beginBasDt=20260227, endBasDt=20260227 (전체 지수)
  → totalCount: 0   ← Feb 27 데이터 존재하지 않음 (Mar 2 오전 현재)
```

**결론**: 공공데이터포털 `GetMarketIndexInfoService`는 24시간 접근 가능하지만, **금융위원회 데이터 자체는 T+1~T+2 영업일 후 게재**됨. Feb 27(금) 데이터는 Mar 3(화) 크론에서 처음 수집 가능 전망.

---

### 원인 2: 수집 스크립트 `end_date = yesterday` 설계 결함 [구조적]

**크론 설정** (`crontab -l`):
```
50 15 * * 1-5   collect_vkospi_alt.py --days 5
```

**스크립트 코드** (`collect_vkospi_alt.py`):
```python
elif args.days > 0:
    start_d = kst - timedelta(days=args.days)
    start_date = start_d.strftime("%Y%m%d")
    end_date = yesterday           # ← 항상 어제까지만 요청
```

**주요 문제점**:

| 크론 실행일 | end_date | 수집 범위 | 누락 |
|------------|----------|-----------|------|
| 2026-02-27 (금) 15:50 | 2026-02-26 (목) | 2/22~2/26 | Feb 27 본인 날 수집 불가 |
| 2026-02-28 (토) | 크론 없음 (1-5만 실행) | — | — |
| 2026-03-01 (일) | 크론 없음 | — | — |
| 2026-03-02 (월) 15:50 | 2026-03-01 (일) | 2/25~3/1 | Feb 27 포함되나 API가 미게재 |
| 2026-03-03 (화) 15:50 | 2026-03-02 (월) | 2/26~3/2 | **Feb 27 비로소 수집 가능** |

→ **금요일 데이터는 화요일 크론에서야 수집 가능** (T+2 영업일 설계)

---

### 원인 3: 레짐 동기화 `numeric field overflow` 오류 [2차 장애]

**오류 로그** (`/var/log/go100/regime_vkospi_sync.log`, 2026-02-27 15:55):
```
sync_vkospi_to_regime error: numeric field overflow
DETAIL: A field with precision 5, scale 2 must round to an absolute value less than 10^3.
강화 레짐: MILD_TREND_UP_EXTREME_VOL (VKOSPI=2885.49, tag=EXTREME)
```

**분석**:
- `v4_market_regime_daily` 또는 `go100_global_market`의 VKOSPI 컬럼 타입: `NUMERIC(5,2)` (최대 999.99)
- `sync_vkospi_to_regime()`이 VKOSPI 2885.49를 반환 → **단위 오류** (원래 VKOSPI는 10~80 범위)
- 실제 Feb 26 VKOSPI = 54.67 (정상 범위)이나, 동기화 함수가 다른 컬럼/단위를 읽는 듯
- 결과: **레짐 동기화 실패 → `v4_market_regime_daily` VKOSPI 미반영**

---

## 4. 대안 소스 조사 결과

| 소스 | 테스트 결과 | 비고 |
|------|------------|------|
| `공공데이터포털` | T+1~T+2 지연 | 현재 사용 중 |
| `pykrx` | 실패 (`지수명` 오류) | VKOSPI 코드 미확정 |
| `FinanceDataReader` | 실패 (Yahoo 404) | VKOSPI 미지원 |
| `KRX 직접` | 미테스트 | OpenDart/KRX 검토 필요 |

---

## 5. 해결 방안

### [즉시 조치] 누락 데이터 수동 수집

Feb 27 데이터가 API에 게재되면 (예상: Mar 3 화요일) 수동 수집:
```bash
cd /root/kis-autotrade-v4
venv/bin/python scripts/collect_vkospi_alt.py --days 10
```
또는 특정 기간:
```bash
venv/bin/python scripts/collect_vkospi.py --start 20260227 --end 20260302
```

### [단기 개선] 크론 end_date 수정

`collect_vkospi_alt.py` 코드에서 `end_date = yesterday` → `end_date = today`로 변경:

```python
elif args.days > 0:
    start_d = kst - timedelta(days=args.days)
    start_date = start_d.strftime("%Y%m%d")
    end_date = today_str   # ← yesterday → today_str 변경
```

단, API 게재 T+1 지연으로 인해 오늘 데이터는 어차피 없음. 효과는 **T+0 게재 시 즉시 수집** 가능해짐.

### [단기 개선] 크론 --days 범위 확대 또는 월요일 전용 크론 추가

```cron
# 월요일은 --days 10 (금-일 누락 보완)
50 15 * * 1   cd /root/kis-autotrade-v4 && venv/bin/python scripts/collect_vkospi_alt.py --days 10
50 15 * * 2-5 cd /root/kis-autotrade-v4 && venv/bin/python scripts/collect_vkospi_alt.py --days 5
```

### [중기] 레짐 동기화 컬럼 오류 수정

`sync_vkospi_to_regime()` 함수의 VKOSPI 값 단위 오류 조사 후 수정:
1. `backend/app/services/go100/ai/regime_enhanced.py` 에서 `sync_vkospi_to_regime()` 코드 확인
2. VKOSPI 필드 값 2885.49 → 정상값 54.67로 되려면 어디서 단위 변환 오류 발생했는지 추적
3. `NUMERIC(5,2)` → `NUMERIC(7,2)` 컬럼 타입 변경 (ALTER TABLE) 또는 값 정규화

---

## 6. 임팩트 분석

| 영향 항목 | 현황 | 리스크 |
|----------|------|--------|
| v4_vkospi_daily 데이터 | Feb 27 1일 누락 | CTE CS 계산 시 최신 변동성 레짐 미반영 |
| v4_market_regime_daily VKOSPI | 동기화 실패 | VKOSPI 기반 CS 배수 오계산 가능 |
| 레짐 판정 | EXTREME 판정 (VKOSPI=2885.49) | 잘못된 극단값으로 리스크 과대 판정 |
| GO100 AI 모델 입력 | `v4_market_regime_daily` 사용 | 레짐 오류 → AI 스코어 오염 가능 |

---

## 7. 체크포인트

- [x] 공공데이터 API 직접 호출 확인 → API 정상, 데이터 T+1~T+2 지연
- [x] Feb 27 (금) 미수집 원인 확인 → API 미게재 + end_date=yesterday 설계
- [x] 크론 로그 분석 → 설계대로 동작, API 지연이 근본 원인
- [x] 대안 소스 테스트 → pykrx/FDR 모두 실패
- [x] 레짐 동기화 오류 확인 → numeric overflow (VKOSPI=2885.49 단위 오류)
- [ ] Feb 27 데이터 수동 수집 (API 게재 후, 예상 Mar 3)
- [ ] `sync_vkospi_to_regime()` 단위 오류 수정
- [ ] 크론 --days 범위 또는 end_date 설계 개선

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-VKOSPI-COLLECTION-FAILURE-001-20260302.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-VKOSPI-COLLECTION-FAILURE-001-20260302.md
- 커밋: (push 후 기재)
