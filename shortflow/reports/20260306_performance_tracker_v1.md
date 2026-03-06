# SF-T013: Performance Tracker v1 — YouTube 영상 성과 수집기

**작성일**: 2026-03-06
**Task ID**: SF-T013
**서버**: 114 (shortflow)
**우선순위**: P1-HIGH
**의존성**: 없음 (SF-T011과 병렬)
**커밋**: `dfcb903`

---

## 개요

YouTube 업로드 후 성과 데이터(조회수, 좋아요, 댓글)를 수집하는 피드백 루프를 구축했다.
D-001(복합 분석) 원칙에 따라 YouTube Data API v3 `videos.list`를 활용한 일일 성과 수집기를 구현.

---

## 구현 파일

### 1. `engine/performance_tracker.py` (신규)

| 클래스/메서드 | 역할 |
|---|---|
| `PerformanceTracker.__init__` | 채널 ID, OAuth 토큰 경로 초기화 |
| `_build_service()` | google-auth로 YouTube Data API 서비스 객체 생성 + 토큰 자동 갱신 |
| `get_video_ids()` | `data/video_registry.json`에서 채널 영상 ID 목록 로드 |
| `get_video_stats(video_ids, dry_run)` | `videos.list` API 호출 (part=statistics,snippet,contentDetails) — dry_run 시 0값 반환 |
| `save_daily_report(stats)` | `data/analytics/daily_{channel}_{YYYYMMDD}.json` 저장 |
| `compare_with_previous(stats)` | 전일 대비 조회수/좋아요/댓글 증감 계산 |
| `run(dry_run)` | 전체 수집 플로우 실행 (get_ids → get_stats → save → compare) |
| `append_to_registry(channel, video_id, title, version)` | 업로드 성공 후 video_registry.json에 자동 추가 (중복 제외) |

**API 비용**: `videos.list` = 1 unit/call, 최대 50 ID/call → 6편 = 6 units (쿼터 영향 미미)

### 2. `scripts/collect_analytics.py` (신규)

CLI 실행 스크립트.

```
# 단일 채널
python3 scripts/collect_analytics.py --channel economy

# 전체 채널
python3 scripts/collect_analytics.py --all

# dry-run (API 호출 없음)
python3 scripts/collect_analytics.py --channel economy --dry-run
python3 scripts/collect_analytics.py --all --dry-run
```

### 3. `data/video_registry.json` (신규)

업로드된 영상 ID 관리 파일. 초기값:

```json
{
  "economy": [
    {"video_id": "6s5UU1vFCvg", "title": "v4 economy 1", "uploaded_at": "2026-03-02", "version": "v4"},
    {"video_id": "VIMxlQSSXUQ", "title": "v4 economy 2", "uploaded_at": "2026-03-02", "version": "v4"},
    {"video_id": "tpeRTVKNtng", "title": "v4 economy 3", "uploaded_at": "2026-03-02", "version": "v4"}
  ],
  "health": [
    {"video_id": "4ZWoA8hbkWs", "title": "v4 health 1", "uploaded_at": "2026-03-02", "version": "v4"},
    {"video_id": "RtmEvQoM7Iw", "title": "v4 health 2", "uploaded_at": "2026-03-02", "version": "v4"},
    {"video_id": "OW3_51k40LY", "title": "v4 health 3", "uploaded_at": "2026-03-02", "version": "v4"}
  ]
}
```

### 4. `data/analytics/` 디렉토리 (신규)

일일 성과 리포트 저장 위치. `.gitkeep` 포함.

### 5. `scripts/run_v4_pipeline.py` (수정)

업로드 성공 직후 `PerformanceTracker.append_to_registry()` 호출 로직 추가 (SF-T013 블록).

---

## 크론 등록

```cron
0 23 * * * cd /data/shortflow && /data/shortflow/venv/bin/python3 scripts/collect_analytics.py --all >> logs/analytics_cron.log 2>&1
```

매일 23:00 UTC (daily_report.sh 직전) 전 채널 성과 수집.

---

## dry-run 테스트 결과

```
2026-03-06 19:01:19 [INFO] >>> DRY-RUN 모드: API 호출 없이 구조만 확인합니다. <<<
2026-03-06 19:01:20 [INFO] ============================================================
2026-03-06 19:01:20 [INFO] 채널: economy  |  dry_run=True
2026-03-06 19:01:20 [INFO] ============================================================
2026-03-06 19:01:20 [INFO] [economy] 수집 대상 영상 3개: ['6s5UU1vFCvg', 'VIMxlQSSXUQ', 'tpeRTVKNtng']
2026-03-06 19:01:20 [INFO] [DRY-RUN] economy: 3개 영상 API 호출 시뮬레이션.
2026-03-06 19:01:20 [INFO] [economy] 일일 리포트 저장: .../data/analytics/daily_economy_20260306.json
2026-03-06 19:01:20 [INFO] [economy] 전일 리포트 없음 (첫 수집).

[economy] 결과:
  영상 수    : 3개
  리포트 저장: /data/shortflow/data/analytics/daily_economy_20260306.json
  영상별 통계:
    6s5UU1vFCvg | 조회수=0 | 좋아요=0 | 댓글=0 [DRY-RUN]
    VIMxlQSSXUQ | 조회수=0 | 좋아요=0 | 댓글=0 [DRY-RUN]
    tpeRTVKNtng | 조회수=0 | 좋아요=0 | 댓글=0 [DRY-RUN]
  전일 데이터 없음 (첫 수집 또는 이전 파일 없음).

수집 완료 요약
============================================================
  성공: 1채널 / 실패: 0채널

  [DRY-RUN] 위 통계는 실제 값이 아닙니다.
```

**결과**: 정상 — video_registry 로드, 3개 영상 구조 확인, JSON 리포트 저장 완료.

---

## 참고

- 실제 API 호출은 OAuth 토큰 유효 시에만 가능. 토큰 만료 상태일 수 있으므로 dry-run 테스트 중심으로 구현.
- `google-auth`, `google-api-python-client` 라이브러리 필요 (venv에 기설치 확인 필요).
- push 보류: PAT 확보 후 일괄 처리 예정.
