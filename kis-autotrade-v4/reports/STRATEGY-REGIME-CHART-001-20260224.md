# STRATEGY-REGIME-CHART-001 — 레짐별 백테스트 차트 시각화 (2026-02-24)

## 작업 ID
- **CUR-STRATEGY-REGIME-BT-VIZ-001** PART C (프론트엔드 차트 시각화)
- KST: 2026-02-24

---

## 1. 프론트엔드 차트 기존 현황

- **차트 라이브러리**: recharts ^3.7.0, lightweight-charts ^5.1.0
- **기존 차트 컴포넌트**: ExitReasonChart(백테스트), StockChart(lightweight-charts), PortfolioChart(go100), AssetPieChart, PerformanceChart, ProfitBarChart
- **백테스트 페이지**: `/backtest` — 전략 카드 선택, 실행(v4/GO100), 결과 요약·청산사유·거래내역 (레짐 분석 없음)
- **백엔드 API**: `/api/v4/backtest/sessions`, sessions/{id}, daily, trades, desk-summary, run, compare 등 (레짐 분석 전용 엔드포인트 없음 → 신규 5개 추가)

상세: `/tmp/chart_status.md` 참고.

---

## 2. 신규 API 5개 엔드포인트 스펙

| 메서드 | 경로 | query | 설명 |
|--------|------|-------|------|
| GET | `/api/v4/backtest/regime-analysis` | card_id?, desk_id?, regime?, session_id? | v4_backtest_regime_analysis 조회, 필터 |
| GET | `/api/v4/backtest/regime-matrix` | session_id? | 전략×레짐 피벗 (bull/neutral/bear/crisis) |
| GET | `/api/v4/backtest/equity-curve` | session_id, card_id | v4_backtest_daily 일별 누적 수익 + regime_at_entry |
| GET | `/api/v4/backtest/regime-timeline` | market_type=KOSPI\|KOSDAQ | v4_market_regime_daily JOIN index_daily → 날짜, 레짐, 지수 close |
| GET | `/api/v4/backtest/regime-comparison` | card_id | 해당 카드 레짐별 성과 비교 (바 차트용) |

- 테이블/데이터 없을 시: 빈 배열 또는 `daily: []` 등으로 응답 (에러 없음).

---

## 3. 차트 5종 구현 내역

| 차트 | 컴포넌트 | 설명 |
|------|----------|------|
| 1 | `RegimeTimelineChart` | X: 날짜, Y: 지수 라인, 배경: 레짐별 ReferenceArea(BULL/NEUTRAL/BEAR/CRISIS), KOSPI/KOSDAQ 토글 |
| 2 | `EquityCurveChart` | X: 날짜, Y: 누적 수익률(%), 전략 라인 + 벤치마크 점선, 레짐 배경 |
| 3 | `RegimePerformanceBarChart` | 그룹: BULL/NEUTRAL/BEAR/CRISIS, 바: 승률/PF/알파/샤프, ReferenceLine·합격=녹색/불합격=빨강 |
| 4 | `StrategyRegimeHeatmap` | X: 레짐, Y: 전략 카드, 셀: 알파 그라데이션 + 승률/PF 텍스트, DESK별 구분 |
| 5 | `DeskRadarChart` | 5축(승률, PF, 알파, 샤프, MDD역수), buildRadarData 헬퍼 제공 |

- 경로: `frontend/src/components/backtest-analysis/`

---

## 4. 백테스트 분석 페이지

- **경로**: `frontend/src/app/(protected)/backtest/analysis/page.tsx`
- **URL**: `/backtest/analysis` (접속 URL: https://trading41.newtalk.kr/backtest/analysis)
- **구성**:
  - 상단 필터: DESK, 전략 카드, 레짐, 세션(에쿼티), KOSPI/KOSDAQ(타임라인)
  - Row 1: 레짐 타임라인 (전체 너비)
  - Row 2: 에쿼티 커브 (좌) + 레짐별 성과 바 (우)
  - Row 3: 전략×레짐 히트맵 (좌) + DESK 레이더 (우)
  - 하단: v4_backtest_regime_analysis 상세 테이블 (최대 100행)

---

## 5. 빌드 & 배포 결과

- **빌드**: `npm run build` 성공 (exit code 0)
- **라우트**: `/backtest/analysis` 정상 등록 (First Load JS 280 kB)
- **네비게이션**: 사이드바에 "레짐별 분석" 링크 추가 (`/backtest/analysis`)
- **프론트엔드 재시작**: 규칙에 따라 자동 재시작 없음. 배포 시 `sudo systemctl restart go100-frontend` 또는 동일 서비스 재시작 후 반영.

---

## 6. 수정/추가 파일 목록

**백엔드**
- `backend/app/models/backtest_analysis.py` — BacktestRegimeAnalysis ORM (신규)
- `backend/app/api/v4_backtest_analysis.py` — 5개 엔드포인트 (신규)
- `backend/app/main.py` — bt_analysis_router 등록 (prefix `/api/v4/backtest`)

**프론트엔드**
- `frontend/src/lib/api/backtest-analysis.ts` — API 클라이언트 (신규)
- `frontend/src/components/backtest-analysis/RegimeTimelineChart.tsx` (신규)
- `frontend/src/components/backtest-analysis/EquityCurveChart.tsx` (신규)
- `frontend/src/components/backtest-analysis/RegimePerformanceBarChart.tsx` (신규)
- `frontend/src/components/backtest-analysis/StrategyRegimeHeatmap.tsx` (신규)
- `frontend/src/components/backtest-analysis/DeskRadarChart.tsx` (신규)
- `frontend/src/app/(protected)/backtest/analysis/page.tsx` (신규)
- `frontend/src/components/layout/Sidebar.tsx` — "레짐별 분석" 메뉴 추가

---

## 7. 접속 URL

- **레짐별 분석**: https://trading41.newtalk.kr/backtest/analysis

---

## 8. 비고

- **DB**: `v4_backtest_regime_analysis` 테이블 및 데이터는 Cursor 1 PART B 완료 후 채워짐. 현재는 API가 빈 배열/메시지로 응답해도 차트는 빈 상태로 정상 표시.
- **API 키**: `/api/v4/*` 는 X-Internal-API-Key 미들웨어 적용. 프론트는 기존 apiClient(Bearer 등) 사용; 백엔드 프록시/헤더 설정에 따라 동작.
- **main.py**: GO100 공유 파일 — 라우터 include만 추가, 기존 로직 변경 없음.
