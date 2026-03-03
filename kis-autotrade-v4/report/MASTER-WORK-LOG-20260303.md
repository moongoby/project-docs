# 2026-03-03 전체 작업 종합 마스터 로그

**작성일**: 2026-03-03
**담당**: Claude (Sonnet 4.6)
**작업 시간**: 14:00 ~ 20:00 KST

---

## 0. 오늘 작업 요약

| 분류 | 건수 | 주요 내용 |
|------|------|---------|
| 버그 수정 | 20건 | PRAGMA, boolean, datetime, TR_ID, rate limit, NXT 시간대 등 |
| 신규 구현 | 3건 | account_snapshots 동기화, DESK2 통합, NXT 통합 |
| 설정 변경 | 2건 | V4.1 DRY_RUN=false, V4_CONFIG_ID=2 |
| 테스트 | 1건 | NXT 실계좌 1주 매수/매도 체결 확인 |

---

## 1. 거래 엔진 수정 (오전)

### 1.1 PRAGMA / boolean 오류 수정
| 파일 | 수정 내용 |
|------|----------|
| `webapp/backend/realtime_signal_generator_fixed.py` | `PRAGMA busy_timeout=30000` 제거 |
| `webapp/backend/realtime_general_market_auto_trade.py` | `PRAGMA busy_timeout=30000` 제거 |
| 양 파일 | `is_active = 1` → `= true` (PostgreSQL boolean) |
| 양 파일 | `auto_trading_enabled = 1` → `= true` |

### 1.2 AppKey 복호화 수정
- 양 파일: `decrypt_value(kis_config.app_key)` 추가 (이전: 암호화된 Fernet 문자열 그대로 KIS 전송)

### 1.3 타임아웃 확장
- `unified_trading_scheduler.py:161`: `timeout=60` → `timeout=240`

---

## 2. Rank API / 신호 생성 수정 (오후)

### 2.1 Rank API 치명적 버그 수정
| 파일 | 항목 | 수정 |
|------|------|------|
| `webapp/backend/data_miner.py` | TR_ID `FHKST03010100`(일봉) → `FHPST01710000`(거래량순위) | ✅ |
| `webapp/backend/data_miner.py` | 필수 파라미터 `FID_INPUT_DATE_1: ""` 추가 | ✅ |
| `webapp/backend/data_miner.py` | `ImprovedKISAPIClient` 호환 (`_get_headers` 분기) | ✅ |
| `webapp/backend/app/services/strategy/dynamic_stock_scanner.py` | `KISAuth` 생성 시 `decrypt_value()` 누락 수정 | ✅ |
| `webapp/backend/app/services/strategy/dynamic_stock_scanner.py` | `is_production=True` 실계좌 우선 선택 | ✅ |
| `webapp/backend/app/services/strategy/dynamic_stock_scanner.py` | `_enrich_gainers()` 0.15초 딜레이 (EGW00201 방지) | ✅ |
| `webapp/backend/app/services/kis/improved_client.py` | VTS 3/초, 실전 8/초 rate limit 최적화 | ✅ |
| `webapp/backend/app/services/kis/improved_client.py` | `get_current_price` retry 명시값 제거 (fast-fail 기본값) | ✅ |
| `webapp/backend/realtime_signal_generator_fixed.py` | `datetime('now')` SQLite → `NOW() - INTERVAL '2 minutes'` | ✅ |
| `webapp/backend/realtime_signal_generator_fixed.py` | VTS 사용자 skip (use_fallback=False, rank API 미지원) | ✅ |
| `webapp/backend/realtime_signal_generator_fixed.py` | 실계좌 fallback 허용 (`use_fallback=is_production`) | ✅ |

### 2.2 신호 자동 만료 로직 추가
- `realtime_signal_generator_fixed.py` 진입부: 10분 이상 PENDING → EXPIRED 자동 처리
- DB 즉시 조치: 20,798건 stale PENDING → EXPIRED 처리 완료

### 2.3 신호 중복 체크 수정
- `_should_skip_duplicate_signal()`: `AND status IN ('PENDING', 'EXECUTED')` 추가 (EXPIRED 신호로 정상 신호 차단 방지)

---

## 3. KIS 주문 성공 판정 버그 수정

**파일**: `webapp/backend/app/services/kis/client.py`

```python
# 수정 전: rt_cd='1'만 실패 처리
if result.get("rt_cd") == "1":
    return {"success": False, ...}

# 수정 후: rt_cd != '0' 전부 실패 처리
rt_cd = result.get("rt_cd", "")
if rt_cd != "0":
    return {"success": False, "rt_cd": rt_cd, ...}
```

**영향**: NXT 불가 종목(rt_cd='7') 등 업무 오류가 `success=True`로 잘못 반환되던 버그 수정

---

## 4. NXT 자동매매 수정

| 파일 | 수정 내용 |
|------|----------|
| `webapp/backend/unified_trading_scheduler.py:318` | `NXT_USER_ID="6"(VTS)` → `"15"(실계좌)` — 치명적 버그 수정 |
| `webapp/backend/nxt_real_service_auto_trade.py:27` | `sys.path '/home/root/...'` → `'/root/...'` |
| `webapp/backend/nxt_real_service_auto_trade.py:332` | NXT 오후 시작 `16:00` → `16:40` (2곳) |
| `webapp/backend/nxt_real_service_auto_trade.py:39` | `ENABLE_REAL_ORDER = True` → 환경변수 `NXT_ENABLE_REAL_ORDER` 지원 |
| `webapp/backend/nxt_real_service_auto_trade.py:92` | `is_active = 1` → `is_active = true` |

---

## 5. NXT 실계좌 1주 매매 테스트 결과

**계좌**: 74032243 (moongoby@naver.com, is_production=True)
**세션**: NXT 오후 (16:40~20:00), 2026-03-03 17:04~17:06 KST

| 구분 | 종목 | 수량 | 가격 | 주문번호 | 결과 |
|------|------|------|------|---------|------|
| 매수 | 316140 우리금융지주 | 1주 | 35,300원 | 0047766100 | ✅ 체결 |
| 매도 | 316140 우리금융지주 | 1주 | 35,300원 | 0047776200 | ✅ 체결 |

**API**: `TTTC0012U` (실전 매수) + `EXCG_ID_DVSN_CD=NXT` 정상 동작 확인

---

## 6. account_snapshots 실시간 동기화 신규 구현

**신규 파일**: `webapp/backend/scripts/sync_account_snapshots.py`

**기능**: KIS API (TTTC8434R/VTTC8434R)로 모든 활성 사용자 잔고 조회 → `account_snapshots` 테이블 저장

**크론 등록**: `*/5 8-20 * * 1-5` (5분 주기, 장중+NXT 세션 전체)

**오늘 실행 결과**:
| user_id | 계좌 | is_production | 총자산 | 예수금 |
|---------|------|--------------|--------|--------|
| 6 | 50160697 (VTS) | false | 498,351,156원 | 451,909,651원 |
| 18 | 50160711 (VTS) | false | 499,172,213원 | 492,132,067원 |
| 27 | 74032243 (실) | true | 592,417원 | 506,078원 |
| 15 | 74032243 (실) | true | 592,417원 | 506,078원 |
| 28 | 50160404 (VTS) | false | ❌ AppKey 오류 | — |

**시퀀스 리셋**: `account_snapshots_id_seq` → `MAX(id)+1` 적용 (중복 키 오류 해결)

---

## 7. V4.1 실계좌 전환

**파일**: `/root/kis-autotrade-v4/.env`

| 항목 | 이전 | 이후 |
|------|------|------|
| DRY_RUN | `true` | **`false`** |
| V4_CONFIG_ID | `3` (VTS 50160711) | **`2`** (실계좌 74032243) |
| TRADING_CONFIG_ID | `3` | **`2`** |

**서비스 재시작**: `kis-v41-scheduler.service` 17:33 KST 재시작 (새 설정 적용)

---

## 8. DESK2 통합 엔진 구현

자세한 내용은 [DESK2-IMPL-COMPLETE-20260303.md](./DESK2-IMPL-COMPLETE-20260303.md) 참조.

### 요약
| 항목 | 내용 |
|------|------|
| DB URL 버그 | `desk2_realtime_signal.py` + `desk2_prescoring.py` URL 파싱 수정 |
| 통합 엔진 연동 | `desk2_auto_trader.py`: `dry_run/mode` 파라미터 추가 |
| 스케줄러 등록 | `desk2_execute` 09:03 5분, `desk2_monitor_exits` 09:05 5분 |
| 리스크 관리 | 일손실 -3% / 연속 3패 중단 실시간 체크 |
| C6/C7 신호 | 전일 상한가 +0.30, 5일 신고가 +0.15 보너스 |
| 진행률 | 62% → **87%** |

---

## 9. 현재 서비스 상태 (20:00 KST 기준)

| 서비스 | 상태 | 비고 |
|--------|------|------|
| `kis-trading-engine.service` | ✅ active | NXT_USER_ID=15 적용 |
| `kis-v41-scheduler.service` | ✅ active | DRY_RUN=false, desk2_execute 등록 |
| `kis-v41-api.service` | ✅ active | Port 8003 |
| `kis-webapp-api.service` | ✅ active | Port 8001 |
| `go100.service` | ✅ active | Port 8002 |
| `account_snapshots 크론` | ✅ 등록 | 5분 주기 |

---

## 10. 내일(2026-03-04) 확인 사항

- [ ] 09:00 신호 생성기 정상 완료 (240s 이내, VTS skip)
- [ ] 09:03 DESK2 자동매매 스케줄러 실행 확인
- [ ] 실계좌(74032243) 실주문 발생 여부 (autotrade_positions/v4_desk2_trades)
- [ ] account_snapshots 5분 갱신 확인
- [ ] V4.1 전략카드 실주문 발송 (DRY_RUN=false 첫 실거래)
- [ ] NXT 세션 (08:00~08:50) 정상 실행 여부

---

*이 문서는 2026-03-03 전체 작업의 마스터 로그입니다.*
*개별 상세 보고서 링크: FIX-TRADING-ENGINE, STATUS-REPORT, FIX-SIGNAL-ENGINE, FIX-RANK-API, REALTRADING-FULL-STATUS, BUG-FIX-FINAL, DESK2-IMPL-COMPLETE*
