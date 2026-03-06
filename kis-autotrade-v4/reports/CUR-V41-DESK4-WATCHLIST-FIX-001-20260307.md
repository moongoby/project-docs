# CUR-V41-DESK4-WATCHLIST-FIX-001-20260307

[인계 확인]
직전 완료: T-202
현재 단계: Phase 2C (파이프라인 복원)
CEO 지시 적용: D-003, D-012, D-013
strategy_cards: 60
open_positions: 0

---

## Task 정보
- **Task ID**: T-213
- **우선순위**: P0-HIGH
- **날짜**: 2026-03-07 (KST)
- **선행**: T-200, T-202
- **병렬그룹**: A

---

## 작업 배경

T-202 DESK5→4→3 파이프라인 복원 분석에서 식별된 단절점 ③:

> DESK4 node_detector가 빈 v4_node_realtime 테이블을 읽고 있어
> v4_desk4_watchlist 11종목이 완전히 무시됨. 트리거 발동 불가.

### 문제 근본 원인

`Desk4NodeDetector.load_watchlist()` (node_detector_desk4.py:170) 가
`v4_node_realtime` 테이블의 `desk_level=4` 행을 조회하고 있었으나,
해당 테이블은 실시간 마디 감지 결과 저장용으로 현재 0행(비어 있음).

실제 DESK4 워치리스트는 `v4_desk4_watchlist` 테이블에 11종목이 WATCHING 상태로 존재하지만,
`load_watchlist()`가 빈 테이블을 읽어 빈 리스트를 반환함.
→ DESK4 트리거 평가가 전혀 실행되지 않는 구조적 단절.

---

## 수행 작업

### 1. 백업
```
backend/app/services/desk_filters/node_detector_desk4.py.bak.20260307
```

### 2. FIX-002 적용: load_watchlist() 수정

**변경 전** (line 170~183):
```python
def load_watchlist(self) -> List[str]:
    """DESK4 워치리스트 조회."""
    try:
        conn = _db_connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT stock_code FROM v4_node_realtime WHERE desk_level = 4"
        )
        rows = cur.fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        logger.warning("load_watchlist 실패: %s", e)
        return []
```

**변경 후** (FIX-002):
```python
def load_watchlist(self) -> List[str]:
    """DESK4 워치리스트 조회.
    FIX-002 (T-213): v4_desk4_watchlist를 primary source로,
    v4_node_realtime은 보조 참조로 사용.
    """
    try:
        conn = _db_connect()
        cur = conn.cursor()

        # Primary: v4_desk4_watchlist WATCHING 종목
        cur.execute(
            "SELECT DISTINCT stock_code FROM v4_desk4_watchlist WHERE status = 'WATCHING'"
        )
        primary = [r[0] for r in cur.fetchall()]

        # Secondary: v4_node_realtime (보조 참조, 빈 경우 무시)
        secondary: List[str] = []
        try:
            cur.execute(
                "SELECT DISTINCT stock_code FROM v4_node_realtime WHERE desk_level = 4"
            )
            secondary = [r[0] for r in cur.fetchall()]
        except Exception:
            pass

        conn.close()

        # 중복 제거, primary 우선
        primary_set = set(primary)
        combined = primary + [s for s in secondary if s not in primary_set]
        logger.info(
            "load_watchlist FIX-002: primary(v4_desk4_watchlist)=%d secondary(v4_node_realtime)=%d total=%d",
            len(primary), len(secondary), len(combined),
        )
        return combined
    except Exception as e:
        logger.warning("load_watchlist 실패: %s", e)
        return []
```

---

## 검증 결과

### py_compile PASS
```
/root/kis-autotrade-v4/venv/bin/python3 -m py_compile backend/app/services/desk_filters/node_detector_desk4.py
→ PASS (오류 없음)
```

### pytest 40/40 ALL PASS
```
pytest tests/unit/test_node_detector_engine.py -v
→ 40 passed, 1 warning in 0.32s
```

### FIX-002 적용 후 load_watchlist 결과
```
load_watchlist FIX-002: primary(v4_desk4_watchlist)=11 secondary(v4_node_realtime)=0 total=11
총 11종목 로드: ['024740', '0000D0', '053050', '009180', '0068M0', '456200', '0084E0', '117580', '012700', '483030', '040420']
```

### DESK4 11종목 트리거 재평가 결과

| 종목코드 | bars | phase | confidence | promote | reentry |
|----------|------|-------|------------|---------|---------|
| 024740 한일단조 | 150 | RISING | 75 | False | False |
| 0000D0 | 150 | RISING | 60 | False | False |
| 053050 지에스이 | 150 | RISING | 75 | False | False |
| 009180 한솔로지스틱스 | 150 | RISING | 75 | False | False |
| 0068M0 | 150 | RISING | 60 | False | False |
| 456200 | 150 | RISING | 60 | False | False |
| 0084E0 | 91 | RISING | 60 | False | False |
| 117580 대성에너지 | 150 | RISING | 75 | False | False |
| 012700 리드코프 | 150 | PULLBACK | 65 | False | False |
| 483030 | 150 | PULLBACK | 65 | False | False |
| 040420 정상제이엘에스 | 150 | PULLBACK | 65 | False | False |

**요약**: total=11 / STARTING=0 / PROMOTE=0 / RISING=8 / PULLBACK=3

※ STARTING=0: 현재 시장 상황에서 즉각적 매수 트리거 없음. RISING/PULLBACK 상태로 대기 중.
※ PROMOTE=0: DESK3 승격 조건(BB상단돌파+거래량3배+기관매수5일) 미충족.

---

## 성공 기준 달성 여부

- [x] v4_desk4_watchlist 11종목 정상 로드 (FIX 전: 0종목 → FIX 후: 11종목)
- [x] 트리거 평가 실행 완료 (11/11 종목)
- [x] py_compile PASS
- [x] pytest 40/40 ALL PASS
- [x] git commit + push 완료

---

## 커밋 정보

- **커밋**: 1cfc435c
- **브랜치**: phase-2c-command-center
- **메시지**: [V4.1] fix: T-213 DESK4 node_detector read desk4_watchlist

---

## 금지 사항 준수

- [x] 서비스 재시작 없음
- [x] strategy_cards 변경 없음

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-DESK4-WATCHLIST-FIX-001-20260307.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-DESK4-WATCHLIST-FIX-001-20260307.md
- 커밋: (project-docs push 후 확인)
- HTTP 확인: (push 후 확인)
- HANDOVER 업데이트: 완료 예정
