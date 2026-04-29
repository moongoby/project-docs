# GO100-P0-PIPELINE-FIX 보고서
> 작성일: 2026-04-29 | 우선순위: P0 | 작업자: Claude Sonnet 4.6

---

## [인계 확인]
직전 완료: GO100-V5-P2-8  
현재 단계: P0 긴급 조치 (실매매 파이프라인 복구)  
CEO 지시 적용: D-001(보고서 push), D-002(작업 전 인계 확인), R-AUTH, R-KEY  

---

## 1. 작업 개요

CEO 지시: 실매매 파이프라인 전체 검수 후 즉시 조치.  
2026-04-29 KST 기준 진단에서 확인된 장애 4건을 복구.

---

## 2. 장애 진단 → 원인 → 조치 요약

### 2-1. 급등주/분봉 수집 — IndexError: tuple index out of range

| 항목 | 내용 |
|------|------|
| 증상 | `*/3 9-15` 마다 IndexError, 수집 중단 |
| 로그 | `/var/log/collect_minute_topmovers.log` line 70: `cur.execute(...)` |
| 원인 | SQL 주석 `-- 1순위: 등락률 2%+` 내 `%+`를 psycopg2가 parameter placeholder로 오파싱 → tuple index 초과 |
| 조치 | SQL 주석에서 `%` 제거, LIKE 패턴(`KODEX%%` 등)을 `%s` 파라미터로 분리 |
| 파일 | `backend/scripts/collect_minute_topmovers.py` |
| 검증 | venv python dry-run: 5건 반환, IndexError 없음 확인 |
| 상태 | ✅ 즉시 복구. 장중 ohlcv_minute 수집 15:30 확인 |

**Before (버그):**
```python
cur.execute("""
    ...
    AND u.stock_name NOT LIKE 'KODEX%%'   -- %% → literal % (OK)
    ...
    -- 1순위: 등락률 2%+ 중 거래대금 상위   -- %+ → psycopg2 placeholder 오파싱!
    ...
    LIMIT %s
""", (n, n, n))  # tuple 3개지만 psycopg2는 4개 필요 → IndexError
```

**After (수정):**
```python
cur.execute("""
    ...
    AND u.stock_name NOT LIKE %s  -- 파라미터로 분리
    ...
    LIMIT %s
""", ('KODEX%', 'TIGER%', 'ACE%', '%스팩%', '%정리%', '%관리%', n, n, n))
```

---

### 2-2. 스캘핑 유니버스 — 경로 오류 (절대경로 미지정)

| 항목 | 내용 |
|------|------|
| 증상 | `can't open file '/root/scripts/collection/scalping_universe_builder.py'` |
| 원인 | crontab: `venv/bin/python scripts/collection/...` — `cd` 없이 상대경로, CWD=/root |
| 조치 | `scripts/cron/run_scalping_universe.sh` 래퍼 생성 (cd+.env+PYTHONPATH), crontab 즉시 변경 |
| crontab 변경 | `venv/bin/python scripts/...` → `scripts/cron/run_scalping_universe.sh` |
| 상태 | ✅ crontab 즉시 적용. 다음 영업일 16:10부터 정상 실행 예정 |

**crontab 변경 전:**
```
10 16 * * 1-5  /root/kis-autotrade-v4/venv/bin/python scripts/collection/scalping_universe_builder.py >> .../scalping_universe.log 2>&1
```

**crontab 변경 후:**
```
10 16 * * 1-5  /root/kis-autotrade-v4/scripts/cron/run_scalping_universe.sh
```

---

### 2-3. 조건검색 수집 — no_condition_list 반복 스킵

| 항목 | 내용 |
|------|------|
| 증상 | `{'skipped': 'no_condition_list'}` 매 5분마다 반복 |
| 원인 | Kiwoom 조건검색 수집기가 `v4_condition_search` DB에서 조건식 목록을 읽는데, 테이블이 비어있어 항상 빈 리스트 반환 |
| 조치 | `collect_condition_search.sh` → `run_kis_condition_search_collect()` 교체. KIS psearch-title API로 조건식 목록 직접 조회 |
| 부가 | API cron(401) 제거. `requests.post('/api/go100/conditions/collect')` — JWT 없는 호출 삭제 |
| 상태 | ⚠ 코드 교체 완료. KIS 계정에 `hts_id` 미설정 시 skip 예상 — `kis_configs.hts_id` 입력 필요 |

**주의사항:** `kis_configs` 테이블에서 `is_active=true` 계정의 `hts_id` 필드에 HTS ID 입력이 필요합니다. CEO 확인 필요.

---

### 2-4. 에러 로깅 장치 보강

| 항목 | 내용 |
|------|------|
| 신규 | `backend/app/services/go100/pipeline_error_logger.py` |
| 기능 | `log_pipeline_error(pipeline, job_name, exc)` → go100_error_log INSERT |
| 기능 | `log_pipeline_success(pipeline, job_name, message)` → heartbeat 기록 |
| DB 확장 | `go100_pipeline_log_extend.sql` — pipeline/job_name/component 컬럼 추가 |
| 뷰 | `go100_pipeline_health_view` — 파이프라인별 최근 상태 요약 |
| 검증 | `log_pipeline_success('test', 'go100_p0_verify')` → DB 기록 True 확인 |

---

## 3. 헬스체크 결과 (2026-04-29 15:18 KST)

| 파이프라인 | 상태 | 최신 데이터 | 비고 |
|-----------|------|------------|------|
| v4_ohlcv_minute (topmovers) | ✅ 정상 | 2026-04-29 15:30 | IndexError 수정 후 수집 확인 |
| v4_scalping_universe | ⚠ 미갱신 | 2026-03-02 (58일) | crontab 수정 완료, 내일 16:10 실행 예정 |
| v4_scalping_signals | ⚠ 0건 | NULL | scalping_universe 갱신 후 신호 발생 예정 |
| v4_condition_search | ⚠ 없음 | NULL | KIS collector 교체 완료, hts_id 입력 필요 |
| stock_price_snapshot | ✅ 정상 | 3572종목 (오늘) | realtime tick 정상 |
| FastAPI /health | ✅ HTTP 200 | — | 정상 |

---

## 4. 변경 파일 목록

| 파일 | 유형 | 변경 내용 |
|------|------|-----------|
| `backend/scripts/collect_minute_topmovers.py` | 수정 | IndexError 수정 (LIKE 파라미터화, 주석 %제거) + error logger 통합 |
| `scripts/cron/collect_condition_search.sh` | 수정 | Kiwoom→KIS collector 교체, API cron 삭제 |
| `backend/app/services/go100/pipeline_error_logger.py` | 신규 | 공통 파이프라인 에러 로거 |
| `scripts/cron/run_scalping_universe.sh` | 신규 | 절대경로+.env wrapper |
| `scripts/ops/go100_pipeline_health.sh` | 신규 | CLI 헬스체크 스크립트 |
| `migrations/go100_pipeline_log_extend.sql` | 신규 | go100_error_log 확장 + health_view |

**커밋**: `c5060a1a` — `fix(go100): repair realtime trading data collectors and error logging`

---

## 5. crontab 변경사항 (즉시 적용 완료)

```diff
- 10 16 * * 1-5  /root/kis-autotrade-v4/venv/bin/python scripts/collection/scalping_universe_builder.py >> .../scalping_universe.log 2>&1
+ 10 16 * * 1-5  /root/kis-autotrade-v4/scripts/cron/run_scalping_universe.sh

- */5 9-15 * * 1-5 cd /root/kis-autotrade-v4 && ... /venv/bin/python -c "import requests; r=requests.post('http://localhost:8002/api/go100/conditions/collect'...)"
  (삭제 — JWT 없는 401 cron)
```

---

## 6. 남은 리스크 및 CEO 확인 필요 사항

1. **v4_scalping_universe 갱신**: 다음 영업일(2026-04-30) 16:10까지 최신 갱신 불가. crontab은 수정됨.
2. **v4_scalping_signals 신호 없음**: scalping_universe가 갱신되면 신호 발생 예정. 현재는 빈 상태.
3. **KIS 조건검색 hts_id 미설정**: `kis_configs` 테이블에서 `is_active=true` 계정의 `hts_id` 입력이 필요. 입력 전까지 `skipped: hts_id_not_set` 반환.
4. **v4_condition_search 과거 데이터 없음**: 새 KIS collector 첫 실행 후 데이터 누적 시작. 오늘 중 수집 예정.

---

## 7. 체크포인트

- [x] 코드 레포 커밋 완료 (커밋 c5060a1a)
- [ ] project-docs 보고서 push 완료

HANDOVER.md 업데이트 완료: (project-docs push 후 확인 예정)
