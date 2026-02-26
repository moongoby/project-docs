# CHART-HEALTH-CHECK-001 — 백테스트 분석 차트 페이지 접속 확인

**작업ID:** CHART-HEALTH-CHECK-001  
**작업명:** 백테스트 분석 차트 페이지 접속 확인  
**일시:** 2026-02-24 KST  
**우선순위:** 병렬 (읽기 전용 확인, 서비스 재시작 금지)

---

## 1. 사전 필수 읽기

| 파일 | 결과 |
|------|------|
| `/root/kis-autotrade-v4/.cursor/rules/kis-v41-rules.md` | ✅ 읽음 |
| `/root/kis-autotrade-v4/.cursor/rules/211-common.md` | ⚠️ 해당 경로에 파일 없음 (HANDOVER에서 참조만 존재) |

---

## 2. 서비스 상태

| 서비스 | 상태 | 비고 |
|--------|------|------|
| **go100** | ✅ active (running) | 127.0.0.1:8002, uvicorn workers 2, 메모리 ~333MB |
| **go100-frontend** | ✅ active (running) | localhost:3000, Next.js 14.2.35, 메모리 ~95MB |

- 재시작 없이 확인만 수행함.

---

## 3. 엔드포인트 헬스체크 (HTTP 상태코드)

| 대상 | URL | HTTP 코드 |
|------|-----|-----------|
| 백엔드 health | http://localhost:8002/health | **200** |
| 프론트엔드 | http://localhost:3000 | **200** |
| 백테스트 분석 페이지 | http://localhost:3000/backtest/analysis | **200** |
| 배포 URL | https://trading41.newtalk.kr | **200** |
| 배포 분석 페이지 | https://trading41.newtalk.kr/backtest/analysis | **200** |

모든 엔드포인트 정상 응답.

---

## 4. 백테스트 분석 API 응답

### 4.1 regime-matrix

- **URL:** `GET /api/v4/backtest/analysis/regime-matrix`
- **헤더:** `X-Internal-API-Key` 사용
- **응답:** `{"matrix":[]}`
- **해석:** API는 정상 동작. 매트릭스 데이터는 빈 배열(백테스트 결과 기반 집계 데이터 미존재 또는 별도 조건 필요).

### 4.2 regime-timeline (KOSPI)

- **URL:** `GET /api/v4/backtest/analysis/regime-timeline?market_type=KOSPI`
- **헤더:** `X-Internal-API-Key` 사용
- **응답:** 정상. `market_type`, `timeline` 배열 존재.
- **데이터 요약:**
  - 날짜별 레짐(regime), regime_score, index_close 포함.
  - 레짐 값: MILD_TREND_UP/DOWN, STRONG_TREND_UP/DOWN, SIDEWAYS 등.
  - 2025-01-02 ~ 2026-02-23 구간 데이터 있음.
- **참고:** 2025-12-03 ~ 2026-02-13 구간 일부에서 `index_close: 0` 존재 (지수 종가 미수집/결측 구간으로 추정, 기존 CEO 결정 대기 항목 “index_daily OHLC=0 재수집”과 연관 가능).

---

## 5. 이상 사항

| 구분 | 내용 | 조치 |
|------|------|------|
| 규칙 파일 | `211-common.md` 해당 경로 없음 | 참조만 유지, 필요 시 경로/생성 여부 확인 |
| regime-matrix | `matrix` 빈 배열 | API 정상, 데이터 채우기는 백테스트/집계 작업 후 검토 |
| regime-timeline | 일부 구간 `index_close: 0` | 이미 정책 대기 중인 index_daily 재수집과 연관 가능, 별도 조치는 CEO 승인 후 |

---

## 6. 결론

- **접속 및 헬스:** 백테스트 분석 차트 페이지(로컬/배포) 및 백엔드·프론트엔드 엔드포인트 모두 **정상 (200)**.
- **API:** regime-matrix·regime-timeline 엔드포인트 **동작 정상**. timeline 데이터 유효, matrix는 현재 빈 배열.
- **조치:** 서비스 재시작 없음. 이상 발견 사항은 보고만 하며, 조치는 CEO 승인 후 진행.

---

*보고서 작성: 2026-02-24 KST*
