# CUR-GO100-DAILY-OPS-20260224 일일 운영/개선 보고서

**일시:** 2026-02-24 KST
**작업자:** Claude Opus 4.6
**브랜치:** phase-2c-command-center

---

## 1. 데이터 수집 매트릭스 UI 개선

### 변경 파일
- `frontend/src/components/admin/DataCollectionTab.tsx`

### 변경 내용
| 항목 | Before | After |
|------|--------|-------|
| 매트릭스 셀 | 아이콘 (●, ◐, ✕, —, ○) | 실제 수집 건수 (숫자, 상태별 색상) |
| 당일 증가분 | 없음 | `오늘 N건 (+delta)` TrendingUp 아이콘 |
| 범례 | 아이콘 범례 5종 | 숫자 색상 범례 4종 |

### 기술 상세
- `CellStatus` 컴포넌트 → `cellColor()` 함수로 교체
- `useRef<Record<string, number>>`로 이전 `today_count` 저장
- `useEffect`에서 30초 refetch마다 delta 계산, `useState`로 관리
- 커밋: `7d3b2f1d`

---

## 2. 분봉수집기 장중 수집 불가 버그 수정

### 문제
- `_get_trading_dates()`가 `ohlcv_daily` 테이블에서 이미 존재하는 날짜만 반환
- 오늘(장중) 날짜가 DB에 아직 없으므로 수집 대상에서 제외됨
- 페이지네이션 시 다른 날짜 데이터가 섞여 무한루프 발생

### 변경 파일
- `backend/app/services/data_pipeline/collector_minute.py`

### 수정 내용

#### (1) 장중 오늘 날짜 자동 추가
```python
kst = timezone(timedelta(hours=9))
now = datetime.now(kst)
today_str = now.strftime("%Y%m%d")
if now.weekday() < 5 and 9 <= now.hour < 16 and today_str not in dates:
    dates.append(today_str)
```

#### (2) 페이지네이션 무한루프 방지
- 대상 날짜 레코드만 필터링하여 `last_time` 계산
- `target_records_in_page`가 비면 즉시 break
- `fid_hour` 변동 없으면 break (동일 시간 반복 방지)

#### (3) `--oldest-first` 옵션 추가
- 과거 일자 우선 수집 (백필용)

### 수집 결과
| 날짜 | 종목수 | 건수 |
|------|--------|------|
| 2026-02-24 (오늘) | 493 | 79,726 |
| 2026-02-23 (어제) | 500 | 188,511 |
| **합계** | — | **266,433** |

- API 호출: 2,930건, 에러: 25건 (서버 disconnect, 무시 가능)
- 소요 시간: ~9분 (페이지네이션 수정 후 ~70배 속도 개선)
- 커밋: `09d9a80f`

---

## 3. 프론트엔드 장애 복구

### 문제
- `.next` 빌드 디렉토리가 삭제되어 프론트엔드 서비스 시작 실패
- `Error: Could not find a production build in the '.next' directory`

### 조치
- `npm run build` 재실행 → `systemctl restart go100-frontend`
- HTTP 200 정상 복구 확인

---

## 4. GO100 백테스트 전략 연동 분석 및 조치

### 분석 대상
- `/backtest` 페이지 전략 드롭다운
- `/strategy-cards` 페이지 GO100 카드 노출
- 종목추천 로직 (universe_filter, entry_rules, exit_rules)

### 코드 흐름 확인
```
[전략카드 페이지] → 상세모달 "백테스트 실행" 버튼
  → /backtest?go100_card_id={id}
  → 드롭다운 자동 선택
  → /api/go100/backtest/run (universe_filter로 종목 자동 선정)
```

### 발견된 문제
| GO100 카드 | 이름 | 종목추천 로직 | is_active | 문제 |
|---|---|---|---|---|
| #13 | 분봉 스캘핑 고변동 대형주 | 완비 | **false** | 주요 전략 비활성 |
| #14 | 대형 우량주 수급 데일리 | 완비 | **false** | 주요 전략 비활성 |
| #15 | 섹터모멘텀 외국인수급 스윙 | 완비 | true | 정상 |
| #17 | E2E_TEST_FIX002 | 없음 | **true** | 테스트카드 노출 |
| #18 | --- | 없음 | **true** | 더미카드 노출 |
| #20 | 상한가 모멘텀 눌림목 | 부분 (텍스트) | true | — |

### 조치
```sql
-- 주요 전략 활성화
UPDATE go100_strategy_cards SET is_active = true WHERE go100_card_id IN (13, 14);
-- 테스트/더미 카드 비활성화
UPDATE go100_strategy_cards SET is_active = false WHERE go100_card_id IN (17, 18);
```

### 조치 후 활성 GO100 전략 (4개)
| 순서 | 카드 | 전략명 | universe_filter | entry_rules | exit_rules |
|------|------|--------|-----------------|-------------|------------|
| 1 | #13 | 분봉 스캘핑 고변동 대형주 | OK | OK | OK |
| 2 | #14 | 대형 우량주 수급 데일리 | OK | OK | OK |
| 3 | #15 | 섹터모멘텀 외국인수급 스윙 | OK | OK | OK |
| 0 | #20 | 상한가 모멘텀 눌림목 재상승 | — | OK | OK |

---

## 커밋 이력

| 커밋 | 메시지 |
|------|--------|
| `7d3b2f1d` | feat: 데이터 수집 매트릭스 아이콘→숫자 변경 + 당일 증가분 표시 |
| `09d9a80f` | fix: 분봉수집기 장중 오늘 날짜 미포함 + 페이지네이션 무한루프 수정 |

## 서비스 상태
- go100 (백엔드): active ✅
- go100-frontend: active ✅
- kis-v41-minute-collector: active (백필 진행 중) ✅
