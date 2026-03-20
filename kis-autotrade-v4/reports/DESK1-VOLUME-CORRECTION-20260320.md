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

## 핵심 설계 결정

| 항목 | 결정 | 이유 |
|------|------|------|
| 보정 임계값 | 5% (`_VOLUME_CORRECTION_THRESHOLD = 0.05`) | WS 35종목 한계상 대부분이 5% 미만으로 나타남 |
| API 호출 속도 | `sleep(0.11)` (~9 req/sec) | KIS 모의투자 rate limit 초당 10회 준수 |
| 토큰 캐시 | 메모리 + 파일(`/tmp/kis_token_cache_desk1.json`) | 3분 크론 재실행마다 토큰 재발급 방지 |
| `acml_vol` 조건 | `acml_vol > current_volume` 일 때만 덮어씀 | 모의투자에서 acml_vol=0 반환 시 데이터 훼손 방지 |
| price-only fallback | confidence 상한 65, volume 확인 종목은 50+α | 거래량 미측정 종목과 실제 거래량 증가 종목 구분 |
| 구현 분리 | REST 보정(1차) → price-only(2차) 독립 처리 | 어느 경로로든 가격 급등 종목 누락 방지 |

---

## 코드 레포 커밋 체크포인트
- [x] 코드 레포 커밋 완료 (kis-autotrade-v4)
  - `0e91a973` feat(desk1): KIS REST API로 volume_ratio 보정 추가
  - `294583d0` feat(desk1): price-only fallback 추가 — 거래량 미측정 시 가격 급등 단독 통과
- [ ] project-docs 보고서 push 완료
