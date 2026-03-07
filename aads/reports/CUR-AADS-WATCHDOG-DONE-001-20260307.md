# AADS Watchdog — Done 미처리 200건 초과 조치 보고

**작성일**: 2026-03-07 KST  
**항목**: Done 미처리 203건(200건 초과) 확인·조치·재발방지

---

## 1. 확인 결과

| 항목 | 내용 |
|------|------|
| **근거** | `genspark_bridge.py` build_unified_status_report() — `done(미처리): {done_n}건` |
| **임계값** | WORKFLOW-PIPELINE.md: done 큐 200건 초과 시 경고 |
| **조사 시점** | directives/done/ 내 .md 파일 수: **208건** |
| **구성** | *_RESULT.md 86건 + 그 외 .md **122건** |

**원인**: `done_watcher.sh`는 `*_RESULT.md` 패턴만 처리해 archived로 이동함.  
비-RESULT .md(보고서·패치·CUR-* 등)는 done에만 쌓이고 archived로 넘어가지 않아 미처리 건수가 200을 초과함.

---

## 2. 조치 내용

### 2.1 즉시 조치 (일괄 이동)

- **대상**: done/ 내 `*_RESULT.md`가 **아닌** 모든 .md 파일
- **처리**: 수정일 기준 월별 폴더(`archived/YYYYMM/`)로 이동
- **결과**: **123건** 이동 완료

### 2.2 이동 후 건수

| 위치 | 조치 전 | 조치 후 |
|------|---------|---------|
| directives/done/ | 208건 | **86건** |
| 임계값 대비 | 200건 초과 | **200건 미만** |

### 2.3 재발 방지 (done_watcher.sh v2.2)

- **추가 함수**: `archive_non_result_done()`  
  - 매 사이클마다 done/ 내 비-RESULT .md를 월별 archived로 이동
- **호출 위치**: `while true` 루프 진입 직후  
  - RESULT 파일 처리 전에 비-RESULT 정리 수행
- **효과**: done/에는 *_RESULT.md만 남기고, done(미처리) 건수가 200을 넘지 않도록 유지

---

## 3. 요약

| 구분 | 결과 |
|------|------|
| 확인 | Done 미처리 208건(203건 보고 기준), 200건 초과 원인: 비-RESULT .md 미이동 |
| 조치 | 비-RESULT .md 123건 → archived 월별 폴더 이동, done 86건으로 감소 |
| 재발방지 | done_watcher.sh에 `archive_non_result_done()` 추가, 매 사이클 비-RESULT 정리 |

**현재 상태**: done(미처리) **86건** — 임계값(200건) 이하 유지 중.
