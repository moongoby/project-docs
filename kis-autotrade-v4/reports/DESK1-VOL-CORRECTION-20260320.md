# DESK1 volume_ratio 보정 구현 보고서

**Task ID**: DESK1-VOL-CORRECTION
**날짜**: 2026-03-20
**파일**: `scripts/run_desk1_scanner.py`

[인계 확인]
직전 완료: DESK1-GRIDSEARCH-OPT
현재 단계: Phase 2C
CEO 지시 적용: DESK1 스캐너 개선

---

## 1. 문제 정의

WS tick 수집 대상이 35종목에 불과하여 `current_volume`(tick SUM)이 실제 거래량 대비 극히 낮음.

- 예시: 008600 — price_chg=14.07%, vol_ratio=0.00 → surge=False
- `IntradaySurgeDetector.detect_surge()`는 `price_ok AND volume_ok` 모두 만족해야 `surge=True`
- `VOLUME_SURGE_RATIO=1.0` 조건 충족 불가 → 실제 급등 종목 미감지

---

## 2. 구현 목표

- [x] WS tick volume 부족 시 KIS REST API `acml_vol`으로 보정
- [x] REST API 실패/0 반환 시 price_change 단독 1차 통과 (confidence 감산)
- [x] rate limit 준수 (0.12초 간격 = 초당 최대 8.3회)

---

## 3. 구현 내용

### 추가 함수

#### `_get_kis_access_token() -> Optional[str]`
- `POST https://openapivts.koreainvestment.com:29443/oauth2/tokenP`
- `KIS_VIRTUAL_APP_KEY / KIS_VIRTUAL_APP_SECRET` 환경변수 사용
- 세션 내 메모리 캐시: `_kis_token_cache` (만료 60초 전 재발급)

#### `_fetch_kis_acml_vol(stock_code, access_token) -> int`
- `GET /uapi/domestic-stock/v1/quotations/inquire-price` (FHKST01010100)
- `output.acml_vol` 파싱
- 실패/rt_cd!="0" → 0 반환 (fail-safe)
- `_last_rest_call_ts` 전역 변수로 0.12초 간격 보장

### `scan_desk1()` 변경 사항

1. **토큰 사전 발급**: rows 처리 전 `access_token = _get_kis_access_token()`
2. **volume 보정 루프**: `current_volume < prev_day_volume * 0.02` 이면 REST API 조회
   - `api_vol > current_volume` 인 경우만 교체 (더 낮은 값으로 덮어쓰지 않음)
   - `volume_corrected` 플래그 저장 (로그 집계용)
3. **price-only 폴백**: `scan_universe()` 이후, 미감지 종목 중
   - `price_change_pct >= PRICE_SURGE_PCT(5%)` 이고
   - `volume_ratio < VOLUME_SURGE_RATIO(1.0)` 인 종목
   - → confidence 40(base) + 가산점, 최대 70으로 results에 추가
4. **재정렬**: price-only 추가 후 `confidence` 내림차순, 상위 10개 슬라이스

---

## 4. 검증 체크리스트

- [x] **구현 목표**: KIS REST API acml_vol 보정 + price-only 폴백 2단계 로직 구현
- [x] **검증 방법**: `python3 -c "import ast; ast.parse(open('/root/scripts/run_desk1_scanner.py').read()); print('OK')"`
- [x] **완료 기준**: syntax OK, 로직 흐름 이상 없음
- [x] **실패 기준**: price_chg 5%+ 종목이 vol_ratio 0.00이어도 price-only 모드에서 confidence 40~70으로 결과에 포함되지 않으면 실패
- [x] **서비스 재시작**: 스크립트 파일 수정 — 크론 실행 시 자동 반영 (재시작 불필요)
- [x] **에러 로그 0건**: 구문 오류 없음 확인

---

## 5. 동작 흐름 요약

```
tick rows 조회
  ↓
KIS 토큰 발급 (캐시)
  ↓
각 종목: current_volume < prev_vol * 2% ?
  → YES: REST API acml_vol 조회 → 교체
  → NO: tick 거래량 그대로 사용
  ↓
scan_universe() → 표준 급등 감지 (price_ok AND vol_ok)
  ↓
미감지 종목 중 price_chg >= 5% 이면 price-only 추가 (conf 40~70)
  ↓
confidence 내림차순 TOP 10 → DB 저장
```

---

## 5b. 실제 단위 테스트 결과 (2026-03-20 재검증)

```
테스트 1 PASS: acml_vol=1234567  (rt_cd=0 정상 응답)
테스트 2 PASS: rt_cd!=0 → 0     (오류 응답 안전 처리)
테스트 3 PASS: HTTP 500 → 0     (서버 오류 안전 처리)
테스트 4 PASS: 예외 → 0         (타임아웃 등 예외 안전 처리)
모든 단위 테스트 통과
```

통합 시뮬레이션 (008600 & 012345):
```
스캔 대상: 2종목 (volume 보정: 1종목)
008600: price_chg=14.10% vol_ratio=1.67 surge=True conf=96 kill_zone=True  ← REST API 보정
012345: price_chg=5.00%  vol_ratio=0.00 surge=False (표준 경로)
price-only fallback 012345: price_chg=5.00% vol_ratio=0.00 conf=55 (volume 부족)
DESK1 스캔 완료: 2건 감지, 2건 신규 저장
```

---

## 6. 주의사항

- 모의투자 API는 일부 종목 acml_vol=0 반환 가능 → price-only 폴백이 안전망 역할
- price-only confidence 최대 70으로 cap → `generate_scalping_signal()`에서 confidence<60 시 SKIP 처리됨 → 신호 생성은 confidence 60~70인 경우만
- WS tick 수집 종목 확대 시 volume_corrected 건수 감소 → 보정 효과 자연 감소
