# CUR-GO100-DAILY-BRIEFING-CRON-001 보고서

**작성일**: 2026-02-25 16:00 KST
**우선순위**: P2
**상태**: **완료**

---

## 1. 목표

매일 08:30 KST 일일 시장 브리핑 자동 생성. 시장 레짐, 상승/하락 TOP, 섹터 동향, AI 코멘터리 포함. 대시보드에 브리핑 카드 표시.

## 2. 변경 내역

### 2.1 Database

```sql
CREATE TABLE go100_daily_briefings (
    id SERIAL PRIMARY KEY,
    briefing_date DATE NOT NULL UNIQUE,
    market_summary TEXT,
    top_movers JSONB DEFAULT '[]',
    sector_highlights JSONB DEFAULT '[]',
    regime_info JSONB DEFAULT '{}',
    ai_commentary TEXT,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    source VARCHAR(50) DEFAULT 'gemini_flash'
);
```

### 2.2 Backend

| 파일 | 변경 |
|------|------|
| `backend/app/services/go100/briefing/__init__.py` | **신규** — 패키지 초기화 |
| `backend/app/services/go100/briefing/daily_briefing_service.py` | **신규** — 시장 데이터 수집, AI 코멘터리 생성, DB 저장 |
| `backend/app/services/go100/briefing/briefing_scheduler.py` | **신규** — 08:30 KST asyncio 스케줄러 (주말 스킵) |
| `backend/app/routers/go100/briefing_router.py` | **신규** — GET /latest, POST /generate API |
| `backend/app/main.py` | 브리핑 스케줄러 등록 + briefing_router include |

### 2.3 Frontend

| 파일 | 변경 |
|------|------|
| `frontend/src/go100/components/DailyBriefingCard.tsx` | **신규** — 대시보드 시장 브리핑 카드 |
| `frontend/src/go100/components/DashboardContent.tsx` | DailyBriefingCard 추가 |
| `frontend/src/go100/api/go100Api.ts` | `getLatestBriefing()` API 함수 추가 |

## 3. 브리핑 생성 플로우

```
08:30 KST (briefing_scheduler_loop)
   │
   ├─ _collect_market_data()
   │    ├─ v4_market_regime_daily → 레짐/점수/VKOSPI
   │    ├─ index_daily → KOSPI/KOSDAQ 종가
   │    ├─ ohlcv_daily → 상승/하락 TOP 5
   │    └─ v4_sector_daily → 섹터 상위 5개
   │
   ├─ _build_market_summary() → 텍스트 요약
   │
   ├─ _generate_ai_commentary()
   │    └─ LLMGateway(CS=Gemini Flash) → 3~5문장 브리핑
   │
   └─ INSERT go100_daily_briefings (ON CONFLICT UPDATE)
```

## 4. API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/go100/briefing/latest` | 최신 브리핑 조회 |
| POST | `/api/go100/briefing/generate` | 수동 브리핑 생성 |

## 5. 검증 결과

| 항목 | 결과 |
|------|------|
| POST /generate | ✅ 브리핑 생성 성공 (market_summary + top_movers + sectors) |
| GET /latest | ✅ 생성된 브리핑 조회 성공 |
| AI Commentary | ✅ Gemini Flash 코멘터리 생성 (RequestType.CS 사용) |
| DB 저장 | ✅ go100_daily_briefings 테이블에 UPSERT 성공 |
| Frontend 빌드 | ✅ npx next build 성공 |
| 대시보드 카드 | ✅ DailyBriefingCard 표시 |

## 보고 요약

- **구현**: DB 테이블 + 브리핑 서비스 + 08:30 KST 스케줄러 + API + 대시보드 카드
- **데이터 소스**: v4_market_regime_daily, index_daily, ohlcv_daily, v4_sector_daily
- **AI**: Gemini Flash (CS route) 코멘터리 자동 생성
- **스케줄**: 평일 08:30 KST 자동 실행, 주말 스킵
- **빌드**: 프론트엔드 빌드 성공, 서비스 재시작 완료
