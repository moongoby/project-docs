# T-256 완료 보고서: admin.html #data-collection UI 전면 구축

**Task ID**: T-256
**완료일**: 2026-03-07
**작업자**: claudebot (Claude Sonnet 4.6)
**브랜치**: phase-2c-command-center
**커밋**: aa782077

---

## [인계 확인]

직전 완료: T-257 (데이터 정합성 자동 점검)
현재 단계: Phase 2C — Command Center
CEO 지시 적용: D-001 (보고서 push), D-002 (HANDOVER.md 업데이트)
strategy_cards: N/A
open_positions: N/A

---

## 1. 작업 개요

admin.html의 `#data-collection` 탭에 11개 섹션(A~K) UI를 전면 구축하였다.
기존 더미 기반의 분봉 수집 현황 UI를 제거하고, `/api/v4/data-collection/*` 실 API를 호출하는 완전한 데이터 수집 대시보드로 교체하였다.

---

## 2. 변경 파일 목록

| 파일 | 변경 유형 | 설명 |
|------|-----------|------|
| `frontend/static/admin.html` | 수정 | #section-data-collection 내용 교체 (11섹션 루트 + 헤더) |
| `frontend/static/js/data-collection.js` | 신규 (T-257 커밋) | 섹션 A~K 렌더링 JS 모듈 (803줄) |
| `backend/app/routers/v4_data_collection.py` | 확장 | 13개 API 엔드포인트 추가 (892줄 추가) |

---

## 3. 섹션 A~K 구현 상세

### 섹션 A: 수집 현황 대시보드 (Summary)
- API: `GET /api/v4/data-collection/summary`
- Health Score 가중평균 계산 (매크로×1.5 + 섹터×1.0 + 펀더멘탈×1.0 + 수급×1.2 + 분봉×1.5 + 일봉×1.3)
- 카테고리별 카드: status badge (OK/WARNING/ERROR), 커버리지%, 최신일, 이슈 목록

### 섹션 B: 매크로 데이터 (Macro)
- API: `GET /api/v4/data-collection/macro`
- 테이블: `v4_macro_daily` (730행)
- 10개 컬럼별 Non-Null/NULL 수, 최신값, 이상치 여부
- VIX 누락 시 빨간 경고 배너 표시

### 섹션 C: 업종 분류 (Sector)
- API: `GET /api/v4/data-collection/sector`
- 테이블: `v4_sector_mapping` (3,844행, 매핑 162개/미매핑 3,682개)
- 업종별 텍스트 바 차트 (상위 15개)
- 미매핑 샘플 20개 표시

### 섹션 D: 펀더멘탈 (Fundamental)
- API: `GET /api/v4/data-collection/fundamental`
- 테이블: `v4_fundamental_quarterly` (1,520행)
- 커버리지 게이지, 분기별 매트릭스, Grade 분포, 필드별 완성도

### 섹션 E: 수급 데이터 (Investor)
- API: `GET /api/v4/data-collection/investor`
- 테이블: `v4_investor_daily` (2,584,110행)
- Dual Flow 적격 종목 수, 5개 필드 완성도 바 차트

### 섹션 F: 분봉 수집 (Minute)
- API: `GET /api/v4/data-collection/minute`
- 테이블: `v4_ohlcv_minute` (127,549,211행, 16개 파티션)
- 파티션별 행수/용량, collector 상태, 최근 30일 바 차트

### 섹션 G: 일봉 OHLCV
- API: `GET /api/v4/data-collection/ohlcv-daily`
- 테이블: `ohlcv_daily` (2,627,338행)
- 전체 통계, 날짜 범위, 오늘 미수집 종목 리스트

### 섹션 H: FunnelScore 진단
- API: `GET /api/v4/data-collection/funnel-score`
- L0(매크로 40%) / L1(섹터 10%) / L2(수급 20%) / L3(펀더멘탈 30%) 레이어별 바 차트
- 임계값: 35점 (T-163), Fail-Open 뱃지

### 섹션 I: 크론 & 서비스 상태
- API: `GET /api/v4/data-collection/cron-status`, `/services`
- systemd 6개 서비스: go100, go100-frontend, kis-v41-api, postgresql, redis-server, nginx
- 크론 파일 목록 (scripts/go100/), 권장 미설치 경고

### 섹션 J: DB 통계
- API: `GET /api/v4/data-collection/db-stats`
- DB 크기, 테이블 수, Top10 테이블 크기 바 차트

### 섹션 K: 알림 & 모의매매
- API: `GET /api/v4/data-collection/alerts-summary`, `/mock-trades`
- Critical/Warning/Info 게이지, 전략별 요약 테이블, FunnelScore 분포 히스토그램

---

## 4. JS 모듈 구조 (data-collection.js)

```
DataCollection = {
  toggle(id)           // 섹션 접기/펼치기
  loadAll()            // 전체 섹션 병렬 로드
  startAutoRefresh()   // 60초 자동 갱신
  stopAutoRefresh()
  refresh()            // 수동 새로고침
}
```

- 탭 클릭 시 자동 초기화
- URL hash `#data-collection` 직접 접근 시도 지원
- API 실패 시 개별 섹션에 에러 메시지 + 빨간 토스트

---

## 5. 테스트 결과

| 테스트 ID | 내용 | 결과 |
|-----------|------|------|
| UI-01 | #data-collection 탭 존재 확인 | ✅ PASS |
| UI-02 | /summary API 호출 확인 | ✅ PASS (API 200) |
| UI-03 | 섹션 펼침/접힘 동작 | ✅ PASS |
| UI-04 | API 실패 시 "데이터 로드 실패" 메시지 | ✅ PASS |
| UI-05 | 60초 자동 갱신 로직 | ✅ PASS |
| SVC-01 | go100 서비스 재시작 후 200 | ✅ PASS |

---

## 6. 백업

```
/root/backup/admin_html_20260307.bak
```

---

## 7. 완료 기준 체크

- [x] admin.html #data-collection 탭에서 11개 섹션 모두 렌더링
- [x] 각 섹션 API 엔드포인트 구현 완료 (13개)
- [x] 서비스 재시작 후 health check 200
- [x] 코드 push 완료 (커밋 aa782077)

---

## 8. 체크포인트

- [x] 코드 레포 커밋 완료 (aa782077, phase-2c-command-center)
- [ ] project-docs 보고서 push 완료 (진행 중)
