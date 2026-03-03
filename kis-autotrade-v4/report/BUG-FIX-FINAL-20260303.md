# 실매매 로직 최종 오류 점검 및 수정 보고서

**작업일**: 2026-03-03 (2차 검토)
**범위**: 전체 실매매 스크립트 심층 코드 리뷰

---

## 발견된 버그 목록 (2차 검토)

### 🔴 치명적 (CRITICAL)

| # | 파일 | 위치 | 버그 | 수정 |
|---|------|------|------|------|
| 1 | `unified_trading_scheduler.py:318` | NXT 실행부 | `NXT_USER_ID=6` → moongoby@gmail.com **(VTS 모의계좌)** → NXT 실주문 불가 | `"6"` → **`"15"`** (moongoby@naver.com, 실계좌) |
| 2 | `nxt_real_service_auto_trade.py:332` | 종목필터 | NXT 오후 시작 `16:00` — 실제 NXT는 `16:40` 시작 | `dt_time(16, 0)` → **`dt_time(16, 40)`** |
| 3 | `nxt_real_service_auto_trade.py:680` | 주문 실행부 | 동일 — NXT 오후 시작 `16:00` | `dt_time(16, 0)` → **`dt_time(16, 40)`** |
| 4 | `realtime_signal_generator_fixed.py` | 중복체크 | EXPIRED/EXECUTED 신호도 2분 중복으로 판정 → 정상 신호 차단 | `AND status IN ('PENDING','EXECUTED')` 추가 |
| 5 | `trading_signals` DB | — | PENDING 신호 **20,798건** 적체 (최대 1개월 전) → 오래된 신호로 매매 실행 가능 | 전체 EXPIRED 처리 + 자동만료 로직 추가 |

### 🟡 HIGH

| # | 파일 | 위치 | 버그 | 수정 |
|---|------|------|------|------|
| 6 | `nxt_real_service_auto_trade.py:27` | 최상단 | `sys.path.insert(0, '/home/root/webapp/backend')` — 경로 오류 | `/root/webapp/backend`로 수정 |
| 7 | `nxt_real_service_auto_trade.py:39` | 설정부 | `ENABLE_REAL_ORDER = True` 하드코딩 — 테스트 모드 불가 | 환경변수 `NXT_ENABLE_REAL_ORDER` 지원 추가 |

---

## 수정 상세

### Bug 1: NXT_USER_ID 오설정 (치명적)

```python
# 수정 전 (unified_trading_scheduler.py:318)
env.setdefault("NXT_USER_ID", "6")   # moongoby@gmail.com = VTS 모의계좌

# 수정 후
env.setdefault("NXT_USER_ID", "15")  # moongoby@naver.com = 실계좌 74032243
```

**영향**: NXT 실주문이 VTS 계좌로 시도 → 인증 실패 또는 VTS API 호출 → 실주문 0건

### Bug 2+3: NXT 시간대 오설정

```python
# 수정 전 (2곳)
(dt_time(16, 0) <= now_t <= dt_time(20, 0))   # 16:00 오류

# 수정 후
(dt_time(16, 40) <= now_t <= dt_time(20, 0))  # 16:40 정확
```

**영향**: 16:00~16:39 정규장 종료 후 NXT 미개장 시간에 NXT 주문 시도 → APBK 오류

### Bug 4: 중복 신호 체크 로직

```sql
-- 수정 전
AND detected_at >= NOW() - INTERVAL '2 minutes'  -- status 필터 없음

-- 수정 후
AND status IN ('PENDING', 'EXECUTED')
AND detected_at >= NOW() - INTERVAL '2 minutes'
```

### Bug 5: 신호 자동만료

```python
# realtime_signal_generator_fixed.py 진입부에 추가
expired = db.execute(text("""
    UPDATE trading_signals SET status='EXPIRED', updated_at=NOW()
    WHERE status='PENDING' AND detected_at < NOW() - INTERVAL '10 minutes'
"""))
```

즉시 조치: 20,798건 stale PENDING → EXPIRED 처리 완료

---

## 검증 통과 항목 (이상 없음)

| 항목 | 결과 |
|------|------|
| SQLite datetime('now') SQL 내 사용 | ✅ 없음 (Python strftime은 정상) |
| PRAGMA 사용 | ✅ 없음 |
| is_active = 1 / auto_trading_enabled = 1 | ✅ 없음 |
| execute_with_retry 함수 존재 | ✅ 정상 (lines 81-93) |
| fetch_recent_signals PENDING 필터 | ✅ 정상 (status='PENDING') |
| 청산 스크립트 boolean 이슈 | ✅ 없음 |
| V4.1 DRY_RUN=false 적용 | ✅ 확인 |
| stale PENDING 신호 | ✅ 0건 (20,798건 처리) |
| account_snapshots 동기화 | ✅ 5분 크론 동작 중 |

---

## 최종 상태

| 컴포넌트 | 상태 |
|---------|------|
| kis-trading-engine.service | ✅ active (NXT_USER_ID=15 적용) |
| kis-v41-scheduler.service | ✅ active (DRY_RUN=false) |
| 신호 생성기 | ✅ 정상 (만료로직 포함) |
| NXT 자동매매 | ✅ 실계좌 user_id=15, 시간대 16:40 정확 |
| 자동매매 (정규장) | ✅ 정상 |
| account_snapshots | ✅ 5분 갱신 |
