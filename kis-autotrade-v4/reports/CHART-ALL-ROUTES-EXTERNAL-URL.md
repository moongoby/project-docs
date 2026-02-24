# 차트 관련 사용자 접근 가능 경로 — 외부 URL 정리

- **문서 ID**: CHART-ALL-ROUTES-EXTERNAL-URL
- **작성일**: 2026-02-24
- **기준**: 프론트엔드 앱 라우트 및 차트 컴포넌트 사용처

---

## 1. 기본 설정

| 항목 | 값 |
|------|-----|
| **도메인(예시)** | `https://go100.newtalk.kr` (실배포 시 해당 도메인으로 치환) |
| **인증** | 아래 경로는 모두 `(protected)` 레이아웃 아래 있어 **로그인 필요** (미인증 시 로그인 페이지로 리다이렉트) |
| **경로 구분** | 차트 전용 페이지 / 차트 포함 페이지 / 차트 진입 가능 페이지로 구분 |

---

## 2. 차트 전용 페이지 (URL로 종목 차트 직접 접근)

| 순번 | 외부 URL (경로) | 설명 | 비고 |
|------|------------------|------|------|
| 1 | `https://go100.newtalk.kr/stock/{종목코드}` | 종목별 차트 전용 페이지 (StockDetailModal = 일봉/분봉/수급 등) | 북마크·공유용. 예: `/stock/005930` |

**예시**
- `https://go100.newtalk.kr/stock/005930`
- `https://go100.newtalk.kr/stock/000660`

---

## 3. 차트가 포함된 페이지 (페이지 본문에 차트 컴포넌트 노출)

| 순번 | 외부 URL (경로) | 페이지 내 차트 | 비고 |
|------|------------------|----------------|------|
| 1 | `https://go100.newtalk.kr/dashboard` | 보유 종목·시장 순위·수급·최근 거래 등에서 **종목 클릭 시** StockDetailModal(StockChart) | 대시보드 메인 |
| 2 | `https://go100.newtalk.kr/portfolio` | **AssetPieChart**(자산 비중 파이), **ProfitBarChart**(수익/손실 바); 보유 종목 클릭 시 StockDetailModal | 포트폴리오 분석 |
| 3 | `https://go100.newtalk.kr/backtest` | **ExitReasonChart**(청산 사유); 백테스트 결과에서 종목 클릭 시 StockDetailModal | 백테스트 결과 |
| 4 | `https://go100.newtalk.kr/go100/paper-trading/{id}` | **PortfolioChart**(페이퍼 자산·수익 곡선); 포지션/거래내역에서 종목 클릭 시 StockDetailModal | 페이퍼 트레이딩 상세. id=포트폴리오 ID |
| 5 | `https://go100.newtalk.kr/go100/live-trading/{id}` | (현재 상세 페이지에 PortfolioChart/종목 차트 진입 UI 없음 — 추후 동일 패턴 추가 시 차트 경로 됨) | 실거래 상세. id=포트폴리오 ID |

---

## 4. 차트 진입만 가능한 페이지 (클릭/행동으로 StockDetailModal 또는 /stock/[code] 진입)

아래 페이지에서는 **테이블/카드에서 종목 클릭** 시 종목 상세(StockChart)로 진입합니다.  
해당 페이지 URL은 위 「차트가 포함된 페이지」와 동일하므로, **차트 진입 경로**만 요약합니다.

| 순번 | 외부 URL (경로) | 차트 진입 행동 |
|------|------------------|----------------|
| 1 | `https://go100.newtalk.kr/dashboard` | 보유 종목 TOP5 종목명 클릭, 시장 순위 종목 행 클릭, 수급 요약 종목 클릭, 최근 거래 종목명 클릭 → StockDetailModal |
| 2 | `https://go100.newtalk.kr/portfolio` | 보유 종목 테이블에서 종목명/코드 클릭 → StockDetailModal |
| 3 | `https://go100.newtalk.kr/go100/paper-trading/{id}` | 포지션 탭/거래내역 탭에서 종목 행 클릭 → StockDetailModal |
| 4 | `https://go100.newtalk.kr/backtest` | 백테스트 결과 매매 내역에서 종목 코드 클릭 → StockDetailModal |

---

## 5. 전체 차트 관련 경로 요약 (외부 URL만 나열)

아래는 **사용자가 접근 가능한 차트 관련 외부 URL**을 경로만 정리한 목록입니다.  
(도메인은 `https://go100.newtalk.kr` 기준)

```
# 차트 전용 (직접 접근)
/stock/{종목코드}
  예: /stock/005930, /stock/000660

# 대시보드 (차트 진입 + 모달)
/dashboard

# 포트폴리오 (페이지 내 파이/바 차트 + 종목 클릭 시 모달)
/portfolio

# 백테스트 (청산 사유 차트 + 종목 클릭 시 모달)
/backtest

# GO100 페이퍼 트레이딩 (자산 곡선 차트 + 종목 클릭 시 모달)
/go100/paper-trading
/go100/paper-trading/{id}

# GO100 실거래 (추후 차트·종목 진입 추가 시 동일 패턴)
/go100/live-trading
/go100/live-trading/{id}
```

---

## 6. 참고 — 차트 미사용 페이지 (라우트만 참고용)

아래는 **차트 컴포넌트/진입이 없는** 사용자 페이지입니다.  
차트 경로 정리와 구분을 위해 참고로 기재합니다.

| 외부 URL (경로) | 비고 |
|------------------|------|
| `https://go100.newtalk.kr/go100` | GO100 대시보드 (PortfolioChart는 페이퍼/라이브 상세에 있음) |
| `https://go100.newtalk.kr/go100/strategies` | 전략 목록 |
| `https://go100.newtalk.kr/go100/strategies/{id}` | 전략 상세 |
| `https://go100.newtalk.kr/go100/chat` | AI 대화 |
| `https://go100.newtalk.kr/go100/store` | 스토어 |
| `https://go100.newtalk.kr/go100/settings` | GO100 설정 |
| `https://go100.newtalk.kr/trade` | 거래 |
| `https://go100.newtalk.kr/strategy-cards` | 전략 카드 |
| `https://go100.newtalk.kr/accounts` | 계좌 |
| `https://go100.newtalk.kr/reports` | 리포트 |
| `https://go100.newtalk.kr/notifications` | 알림 |
| `https://go100.newtalk.kr/settings` | 설정 |
| `https://go100.newtalk.kr/monitoring` | 모니터링 |
| `https://go100.newtalk.kr/admin` | 관리자 |
| `https://go100.newtalk.kr/llm` | LLM |

---

## 7. 도메인 치환 시 참고

실제 서비스 도메인이 다를 경우 아래만 치환하면 됩니다.

- **개발**: `http://localhost:3000` 등
- **스테이징/운영**: `https://go100.newtalk.kr` 또는 실제 도메인

예) 운영이 `https://app.example.com` 이면  
차트 전용 페이지: `https://app.example.com/stock/005930`

이 문서는 **모든 차트 경로를 사용자가 접근 가능한 외부 URL 형태로 정리한 보고서**입니다.
