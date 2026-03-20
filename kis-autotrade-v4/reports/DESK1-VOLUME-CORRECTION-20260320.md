# DESK1 IntradaySurgeDetector volume_ratio 보정 보고서

**작업일**: 2026-03-20
**태스크**: DESK1 volume_ratio WS tick → KIS REST API acml_vol 보정
**파일**: `scripts/run_desk1_scanner.py`

---

## 검증 체크리스트

### 구현 목표
WS tick 수집 35종목 한계로 `current_volume`이 과소 집계되는 문제를 해소하기 위해,
`volume_ratio < 5%`인 종목에 한해 KIS REST API `inquire-price`의 `acml_vol`(당일 누적거래량)로 보정.

### 구현 내용
`scripts/run_desk1_scanner.py`에 다음 추가:

1. **`_get_kis_access_token()`** — KIS 모의투자 OAuth2 토큰 발급/캐싱 (메모리 + `/tmp/kis_token_cache_desk1.json` 파일 캐시, 20시간 유효)
2. **`_fetch_kis_acml_vol(ticker)`** — `FHKST01010100` TR 호출 → `output.acml_vol` + `output.stck_prpr` 반환
3. **보정 로직** (`scan_desk1()` 내):
   - DB 조회 후 `vol_ratio_ws = current_volume / prev_day_volume < 0.05` 이면 `needs_volume_fix` 목록에 추가
   - REST API로 `acml_vol` 조회 → `acml_vol > current_volume` 이면 `entry["current_volume"]` 덮어씀
   - API 현재가(`stck_prpr`)도 유효하면 함께 보정
   - `time.sleep(0.11)` — ~9 req/sec, KIS rate limit(초당 10회) 준수
4. **price-only fallback** (커밋 `294583d0` 추가):
   - `scan_universe()` 이후 `vol_ratio < 1.0` + `price_chg >= 5%` 종목을 2차 포함
   - 모의투자 acml_vol=0 반환 시에도 가격 급등 종목 감지 보장
   - confidence 상한 **65** (volume 확인 종목과 구분), 킬존 보너스 +10 포함
   - 008600 사례: `price_chg=14.07% vol_ratio=0.00` → `surge=False` 문제 해결

### 변경 파일
| 파일 | 변경 유형 |
|------|-----------|
| `scripts/run_desk1_scanner.py` | 수정 (line 10-124 추가, line 189-237 보정 로직 추가) |

---

### 검증 방법

**문법 검사**
```bash
python3 -c "import ast; ast.parse(open('scripts/run_desk1_scanner.py').read()); print('syntax OK')"
```
→ 결과: `syntax OK`

**함수 존재 확인**
```python
src = open('scripts/run_desk1_scanner.py').read()
# _get_kis_access_token: OK
# _fetch_kis_acml_vol: OK
# _VOLUME_CORRECTION_THRESHOLD: OK
# needs_volume_fix: OK
# acml_vol: OK
```

**KIS REST API 직접 테스트** (환경변수 설정 후)
```bash
python3 -c "
import sys; sys.path.insert(0,'scripts')
# 환경변수 설정 필요: KIS_VIRTUAL_APP_KEY, KIS_VIRTUAL_APP_SECRET
from run_desk1_scanner import _fetch_kis_acml_vol
vol, price = _fetch_kis_acml_vol('008600')
print(f'008600: acml_vol={vol}, price={price}')
"
```

**장중 실행 로그 기대 패턴 (케이스 1: REST API 성공)**
```
스캔 대상: 35종목 (거래량 보정 필요: 30종목)
[VOL_FIX] KIS REST API로 거래량 보정 시작
[VOL_FIX] 008600: WS=125 → API acml_vol=1523400 (×12187.2배)
[VOL_FIX] 보정 완료: 28/30종목
급등감지 008600: price_chg=14.07% vol_ratio=1.52 surge=True conf=75
```

**장중 실행 로그 기대 패턴 (케이스 2: REST API acml_vol=0 → price-only fallback)**
```
[VOL_FIX] 보정 완료: 0/30종목
급등감지 008600: price_chg=14.07% vol_ratio=0.00 surge=False conf=0
[PRICE_ONLY] 008600: price_chg=14.07% vol_ratio=0.00 → conf=57 (거래량 미측정)
DESK1 스캔 완료: 1건 감지, 1건 신규 저장
```

### 완료 기준
- **케이스 1**: `[VOL_FIX] 보정 완료: N/M종목` + `surge=True` 감지
- **케이스 2 (모의투자 acml_vol=0)**: `[PRICE_ONLY]` 로그로 가격 급등 종목 감지
- 둘 중 하나 이상 달성 시 완료

### 실패 기준
- `[KIS_REST] APP_KEY/SECRET 환경변수 없음` 계속 출력 → `.env` 확인 필요
- `needs_volume_fix`도 0, `price_only_results`도 0 → tick 데이터 자체가 없는 경우
- syntax 오류 → 배포 불가

### 서비스 재시작 확인
- 이 스크립트는 `cron`으로 실행되므로 별도 서비스 재시작 불필요
- 다음 크론 주기(*/3 9-14 * * 1-5)에 자동 반영

### 에러 로그 확인
```bash
# 다음 크론 실행 후
journalctl -u cron --since "5 minutes ago" | grep desk1
```

---

## 추가 수정 (2026-03-20 — 커밋 `1e362c52`)

### 발견된 버그 2건

**버그 1: 임계값 0.05 과소 설정**
- WS vol_ratio가 0.0792인 종목(475150, 가격+11.15%)이 보정 대상에서 제외
- 0.0792 > 0.05라서 REST API 호출 스킵 → 실제 acml_vol(8,522,609) 조회 못 함
- 수정: `_VOLUME_CORRECTION_THRESHOLD = 0.05` → `0.95` (surge 임계 1.0 미만 전체 보정)

**버그 2: prev_day_volume=0 케이스 누락 (008600 사례)**
- DB에서 전일 거래량이 0으로 기록된 경우 `vol_ratio_ws = ws_volume / max(0, 1) = 36625`
- 36625 >= 0.95라서 REST 보정 대상 제외
- detect_surge()에서는 `prev_day_volume <= 0 → volume_ratio = 0.0 → surge=False`
- price-only fallback에서도 `vol_ratio(36625) >= 1.0 → continue` → 완전 누락
- 수정 1: 보정 조건에 `or int(prev_day_volume) == 0` 추가
- 수정 2: price-only fallback에 `stock["prev_day_volume"] > 0` 가드 추가

### 수정 후 검증 (실시간 API 테스트)

```
종목코드    WS거래량    전일거래량    WS비율    보정대상  REST_acml_vol  REST가격  price_chg
002780    5,230,457  66,076,371   0.0792      Y    59,668,737    1,210    +20.59% → ratio=0.903
008600       36,625           0  36625.00      Y  조회필요(모의투자)    -      +14.07%
475150    1,162,129  14,628,900   0.0794      Y     8,522,609   61,400    +11.15% → ratio=0.5826
089150      576,156   5,917,914   0.0974      Y      0(모의투자)    -       +7.36%
261780    1,471,770  30,802,101   0.0478      Y      0(모의투자)    -       +6.61%
```

- KIS REST API 토큰 발급: 200 OK ✅
- acml_vol 조회 (008600): `acml_vol=172442`, `stck_prpr=2820` ✅
- 002780: WS 5.2M → REST 59.7M (×11.4배), ratio=0.0792→0.903
- 475150: WS 1.2M → REST 8.5M (×7.3배), ratio=0.0794→0.5826

---

## 핵심 설계 결정

| 항목 | 결정 | 이유 |
|------|------|------|
| 보정 임계값 | **0.95** (`_VOLUME_CORRECTION_THRESHOLD`) | WS 35종목은 실질적으로 모든 종목이 surge 임계(1.0) 미달, 전부 보정 필요 |
| prev_day_volume=0 | `or int(prev_day_volume) == 0` 추가 | 전일 거래량 미수집 시 WS ratio 인위 상승 방지 (008600 사례) |
| price-only 가드 | `stock["prev_day_volume"] > 0 and vol_ratio >= 1.0` | prev=0 인 경우 vol_ratio 36625로 폴백 스킵되던 버그 해결 |
| API 호출 속도 | `sleep(0.11)` (~9 req/sec) | KIS 모의투자 rate limit 초당 10회 준수 |
| 토큰 캐시 | 메모리 + 파일(`/tmp/kis_token_cache_desk1.json`) | 3분 크론 재실행마다 토큰 재발급 방지 |
| `acml_vol` 조건 | `acml_vol > current_volume` 일 때만 덮어씀 | 모의투자에서 acml_vol=0 반환 시 데이터 훼손 방지 |
| price-only fallback | confidence 상한 65, volume 확인 종목은 50+α | 거래량 미측정 종목과 실제 거래량 증가 종목 구분 |

---

## 코드 레포 커밋 체크포인트
- [x] 코드 레포 커밋 완료 (kis-autotrade-v4)
  - `0e91a973` feat(desk1): KIS REST API로 volume_ratio 보정 추가
  - `294583d0` feat(desk1): price-only fallback 추가 — 거래량 미측정 시 가격 급등 단독 통과
  - `3a432889` fix: desk1_scanner SQL 수정
  - `1e362c52` fix(desk1): 임계값 0.95 상향 + prev_day_volume=0 버그 2건 수정
- [ ] project-docs 보고서 push 완료
