# CUR-GO100-CHART-IMPROVE-001 — GO100 차트 전면 개선 보고서

> 작성일시: 2026-02-25 KST
> 커밋: `4cee5e72` (feat/CUR-GO100-DATA-ENGINE-INTEGRATION)
> 선행 커밋: `8cad0a38` (페이지 오디트 — stock_name + store 구독)

---

## 1. 배경

GO100 프론트엔드 페이지 오디트(9개 페이지) 완료 후, 차트 반영 현황을 전수 조사한 결과 5개 영역에서 차트 미구현 또는 개선이 필요함을 확인.

### 1-1. 조사 결과 요약

| 페이지 | 기존 상태 | 문제 |
|--------|----------|------|
| 전략 상세 (`/go100/strategies/[id]`) | 차트 없음 | `equity_curve`, `trade_log` 데이터 있으나 시각화 안 됨 |
| 대시보드 (`/go100`) | 차트 없음 | KPI 숫자만 표시, 추이 파악 불가 |
| 백테스트 (`/backtest`) | CSS div 막대 그래프 | 축/라벨/툴팁 없음, 데이터 포맷 불일치 |
| 실매매 (`/go100/live-trading/[id]`) | 포지션 테이블 없음 | API 있으나 UI에 포지션 미표시 |
| 포지션 테이블 (`PositionTable`) | 종목명 텍스트만 | 클릭 시 종목 차트 연결 없음 |

포트폴리오/모의거래 상세 페이지는 `PortfolioChart.tsx`로 3종 차트(자산추이, 일일수익률, 누적수익률) 이미 구현됨.

---

## 2. 구현 내용

### [A] 전략 상세 — Equity Curve + 승패 분포 차트

**파일**: `frontend/src/app/(protected)/go100/strategies/[id]/page.tsx`
**변경량**: +100줄

- **Equity Curve (LineChart)**: 마지막 백테스트 결과의 `equity_curve` 데이터를 파싱하여 recharts `LineChart` 렌더링
  - 포맷: `[{date: "YYYY-MM-DD", equity: number}, ...]`
  - 날짜 X축 + 원화 Y축 + 툴팁
- **승/패 분포 (PieChart)**: `profit_trades` / `loss_trades` 데이터로 도넛 차트
  - 초록(수익) / 빨강(손실) 색상
  - 중앙에 총 거래 수 + 승률 텍스트 표시
- 데이터 없으면 차트 섹션 자체 비표시 (조건부 렌더링)

### [B] 대시보드 — 미니 자산추이 차트

**파일**: `frontend/src/go100/components/DashboardContent.tsx`
**변경량**: +69줄

- 첫 번째 페이퍼 포트폴리오의 스냅샷 최근 30일을 `AreaChart`로 표시
- `getPaperPortfolios()` → `getPaperSnapshots(id)` 순차 호출
- 그라데이션 채우기(파란색), 날짜 축, 원화 툴팁
- KPI 메트릭과 일일 브리핑 사이에 배치
- 데이터 없으면 숨김 처리

### [C] 백테스트 — CSS 막대 → recharts AreaChart

**파일**: `frontend/src/app/(protected)/backtest/page.tsx`
**변경량**: +67줄, -42줄

- **GO100 백테스트**: `equity_curve` 파싱 개선
  - `{date, equity}[]` 형식 감지하여 날짜 라벨 추출
  - `number[]` 형식도 호환 유지
  - CSS `EquityCurveBar` → recharts `AreaChart` (amber 그라데이션)
  - 시작금/최종금 텍스트 하단 표시
- **V4 백테스트**: 동일하게 `EquityCurveBar` → recharts `AreaChart` 전환
- 양쪽 모두 X축(날짜/인덱스), Y축(원화 포맷), 툴팁 추가

### [D] 실매매 — 포지션 테이블 + Tabs UI

**파일**: `frontend/src/go100/components/LiveTradingDetailContent.tsx`
**변경량**: 리팩토링 (+141줄, -99줄)

- `getPortfolioPositions(portfolioId)` API 호출 추가
- `Tabs` UI 도입: 포지션 탭 + 조정 내역 탭
- `PositionTable` 컴포넌트 재사용
- "보유 종목" MetricCard 추가
- 기존 조정(Reconciliation) 내역은 두 번째 탭으로 이동

### [E] 종목 차트 — PositionTable → StockDetailModal 연결

**파일**: `frontend/src/go100/components/PositionTable.tsx`
**변경량**: 리팩토링 (+85줄, -45줄)

- 종목명을 `<button>`으로 변경 (hover 시 파란색 + 밑줄)
- 클릭 시 `StockDetailModal` 오픈 (stock_code, stock_name 전달)
- `StockDetailModal`은 이미 완전 구현됨:
  - Lightweight Charts 캔들스틱 (일봉/분봉)
  - 호가창 (5초 갱신)
  - 펀더멘털 (PER, PBR, EPS 등)
  - 체결강도 바
  - 투자자별 매매동향

---

## 3. 빌드 이슈 및 해결

### recharts Tooltip formatter 타입 에러 (3건)

**문제**: recharts의 `Formatter` 타입이 `value` 파라미터에 `undefined`를 포함
```
Type '(value: number) => ...' is not assignable to type 'Formatter<number, ...>'
  Type 'number | undefined' is not assignable to type 'number'
```

**해결**: 명시적 타입 어노테이션 제거, `Number(value)` 래핑으로 런타임 안전성 확보
```tsx
// before
formatter={(value: number) => [`${value.toLocaleString()}원`, "자산"]}
// after
formatter={(value) => [`${Number(value).toLocaleString()}원`, "자산"]}
```

**적용 파일**: `backtest/page.tsx` (2건), `strategies/[id]/page.tsx` (1건), `DashboardContent.tsx` (1건)

---

## 4. 변경 파일 목록

| # | 파일 | 변경 | 줄수 |
|---|------|------|------|
| 1 | `frontend/src/app/(protected)/go100/strategies/[id]/page.tsx` | 수정 | +100 |
| 2 | `frontend/src/go100/components/DashboardContent.tsx` | 수정 | +69 |
| 3 | `frontend/src/app/(protected)/backtest/page.tsx` | 수정 | +67 -42 |
| 4 | `frontend/src/go100/components/LiveTradingDetailContent.tsx` | 수정 | +141 -99 |
| 5 | `frontend/src/go100/components/PositionTable.tsx` | 수정 | +85 -45 |
| **합계** | | | **+363 -99** |

---

## 5. 차트 라이브러리 현황

| 라이브러리 | 용도 | 페이지 |
|-----------|------|--------|
| **recharts** | 자산추이, 수익률, 에쿼티 커브, 승패 분포 | 대시보드, 포트폴리오, 모의거래, 백테스트, 전략 상세 |
| **lightweight-charts** (TradingView) | 캔들스틱, 호가, 체결강도 | StockDetailModal (모든 포지션에서 접근 가능) |

---

## 6. 미구현 사항 (P3 — 백엔드 변경 필요)

| 항목 | 이유 | 필요한 작업 |
|------|------|-----------|
| 실매매 자산추이 차트 | 백엔드에 스냅샷 엔드포인트 없음 | `GET /api/go100/live-trading/{id}/snapshots` 구현 + 스케줄러 |
| 누적수익률 KOSPI 벤치마크 | 벤치마크 데이터 미연동 | KOSPI 지수 데이터 수집 + 비교 로직 |

---

## 7. 검증

- [x] `npx next build` — 성공
- [x] `systemctl restart go100-frontend` — 정상
- [x] `systemctl restart go100` — 정상
- [x] Git 커밋: `4cee5e72`
- [x] Git 푸시: `feat/CUR-GO100-DATA-ENGINE-INTEGRATION`
