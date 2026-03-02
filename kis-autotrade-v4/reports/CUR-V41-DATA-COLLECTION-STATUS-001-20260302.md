# CUR-V41-DATA-COLLECTION-STATUS-001 — 전체 데이터 수집 현황 및 즉시 조치 완료
> 작성일: 2026-03-02 06:50 KST | 담당: Claude Code Sonnet 4.6

---

[인계 확인]
직전 완료: CUR-V41-VKOSPI-FIX-001
현재 단계: 전체 수집 가능 데이터 점검 + 누락 즉시 조치
CEO 지시 적용: D-001(단순사고 금지), D-002(보고서 push 필수)
strategy_cards: 60개
open_positions: 14개

---

## 결론

> **수집 가능한 데이터 전부 수집 완료 (조치 후).**
> 단, VKOSPI Feb 27 = API 게재 지연 (외부 요인, 오늘 자동 수집 예정)

---

## 전체 테이블 현황 (2026-03-02 06:50 기준)

| 테이블 | 건수 | 최신일 | 상태 | 비고 |
|--------|------|--------|------|------|
| `ohlcv_daily` | 2,615,744 | 20260227 | ✅ 정상 | 3,839 종목 |
| `v4_investor_daily` | 275,846 | 2026-02-27 | ✅ 정상 | 수급 데이터 |
| `v4_market_regime_daily` | 823 | 2026-02-27 | ✅ 정상 | VKOSPI=54.67 |
| `v4_ohlcv_minute` | 83,499,229 | 2026-02-27 | ✅ 정상 | 분봉 8,300만건 |
| `go100_news_items` | 2,148,278 | 2026-02-27 | ✅ 정상 | 뉴스 214만건 |
| `go100_global_market` | 296 | 2026-03-01 | ✅ 정상 | FX주말+신규지표 수집 |
| `v4_scalping_universe` | **1,354** | **2026-03-02** | ✅ **오늘 갱신** | 조치 후 646→1354 |
| `v4_vkospi_daily` | 1,510 | 20260226 | ⏳ 대기 | API 지연, 자동수집 예정 |

---

## 이번 점검에서 발견·조치한 3건

### [발견 1] v4_scalping_universe 크론 미등록 → 즉시 조치 완료

**상황**: `scalping_universe_builder.py`는 "매일 16:00 실행" 설계이지만 crontab에 미등록.
최신일 = 2026-02-21 (8일 경과, 708건).

**조치**:
```bash
# 수동 즉시 실행
venv/bin/python scripts/collection/scalping_universe_builder.py
# → UPSERT 646건, 당일 활성 총 646건 → DB 기준 1354건 (Mar 2 기준)

# crontab 등록 (16:10 매 평일)
10 16 * * 1-5  venv/bin/python scripts/collection/scalping_universe_builder.py
```

**결과**: 2026-03-02 기준 1,354건 활성 ✅

---

### [발견 2] go100_global_market wti_crude/sox/csi300/copper 미수집 → 즉시 조치 완료

**상황**: DB 테이블에 `wti_crude`, `sox`, `sox_change_pct`, `csi300`, `csi300_change_pct`, `copper`, `copper_change_pct` 컬럼 존재하지만 `collect_global_market.py`에 수집 코드 없음. 해당 컬럼 전부 NULL.

**조치** (`scripts/data_collect/collect_global_market.py`, 커밋 e273038d):
```python
# 추가된 4개 심볼
("CL=F",      "wti_crude",  "wti_crude_change_pct"),
("^SOX",      "sox",        "sox_change_pct"),
("000300.SS", "csi300",     "csi300_change_pct"),
("HG=F",      "copper",     "copper_change_pct"),
```

**소급 수집 결과 (Feb 24~27)**:

| 날짜 | wti_crude | sox | csi300 | copper |
|------|-----------|-----|--------|--------|
| 2026-02-24 | 65.63 | 8332.34 | 4707.54 | 5.923 |
| 2026-02-25 | 65.42 | 8467.43 | 4735.89 | 5.980 |
| 2026-02-26 | 65.21 | 8197.26 | 4726.87 | 5.947 |
| 2026-02-27 | 67.02 | 8098.37 | 4710.65 | 6.060 |

✅ 이후 크론(매일 08:30)에서 자동 수집됨

---

### [발견 3] v4_vkospi_daily Feb 27 미수집 → 스크립트 수정 완료, 자동 수집 대기

이전 보고서 `CUR-V41-VKOSPI-FIX-001-20260302` 참조.

- `collect_vkospi_alt.py` `end_date = today_str` 수정 완료 (커밋 bc5fac1c)
- 오늘 09:00/12:00/15:00/15:50 자동 재시도 크론 추가
- API 미게재 (외부 요인) → 오늘 15:50 또는 내일 자동 수집 예정

---

## 전체 크론 스케줄 현황 (수정 후)

| 시각 | 스크립트 | 대상 테이블 |
|------|---------|------------|
| 08:30 월~금 | `collect_global_market.py` | go100_global_market (10개 지표) |
| 15:50 월~금 | `collect_vkospi_alt.py --days 7` | v4_vkospi_daily |
| 15:55 월~금 | `run_vkospi_regime_sync.sh` | v4_market_regime_daily, go100_global_market |
| 16:00 월~금 | `minute_batch_cron.sh` | v4_ohlcv_minute (히스토리) |
| **16:10 월~금** | **`scalping_universe_builder.py`** ← **신규 등록** | v4_scalping_universe |
| 16:25 월~금 | `collect_stock_universe.py` | stock_universe (Top-100) |
| 오늘만 임시 | `collect_vkospi_alt.py` (9/12/15시) | v4_vkospi_daily Feb27 재시도 |

---

## 수집 불가 / 정상 미수집 항목

| 항목 | 이유 | 조치 방안 |
|------|------|-----------|
| **VKOSPI Feb 27** | API T+1~T+2 지연 (외부) | 오늘~내일 자동 수집 |
| **go100_global_market Mar 2** | US 시장 아직 미개장 (KST 06:50) | 08:30 크론에서 수집 |
| **go100_global_market Feb 28~Mar 1 vix/sp500** | 주말 US 시장 휴장 | 정상 (비거래일) |
| **v4_ohlcv_minute Mar 2** | 장 미개장 (오전) | 09:00 장 시작 후 WebSocket 수집 |

---

## 커밋 내역

| 커밋 | 내용 |
|------|------|
| `bc5fac1c` | VKOSPI end_date yesterday→today 수정 |
| `e273038d` | 글로벌 시장 WTI/SOX/CSI300/copper 추가 |
| `74ec682b` | push (kis-autotrade-v4 origin) |

---

## 체크포인트

- [x] 전체 8개 핵심 테이블 상태 확인
- [x] v4_scalping_universe 크론 미등록 발견 → 등록 + 즉시 갱신 (646→1354건)
- [x] go100_global_market 4개 지표 미수집 발견 → 스크립트 수정 + 소급 수집
- [x] VKOSPI end_date 수정 + 임시 재시도 크론 추가
- [x] 코드 push 완료 (74ec682b)
- [x] 보고서 project-docs push 완료
- [ ] VKOSPI Feb 27: 오늘 15:50 크론 수집 확인 (대기 중)
- [ ] go100_global_market Mar 2: 08:30 크론 수집 확인 (대기 중)
