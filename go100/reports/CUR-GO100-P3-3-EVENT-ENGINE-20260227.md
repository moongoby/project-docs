# CUR-GO100-P3-3 — 이벤트 엔진 + ISS-011/012/013

**일시:** 2026-02-27  
**작업 ID:** CUR-GO100-P3-3 (P3-3)  
**목적:** GO100 이벤트 엔진(어닝·공시 연동) 구축 및 잔여 이슈 ISS-011/012/013 해결

---

## 1. 요약

- **파트 A:** 이벤트 엔진 — DB 테이블 `go100_events`, 수집 스크립트(KRX/DART), 시그널 엔진, Agent 도구 `get_events`/`get_event_impact` 추가.
- **파트 B:** ISS-011 `/go100/chat` 리다이렉트, ISS-012 ChatWidget `user_id` 동적 처리(GET /api/go100/me), ISS-013 백테스트 재시도 API `POST /api/go100/backtest/{run_id}/retry` 및 프론트 경로 반영.

---

## 2. 파트 A: 이벤트 엔진

### 2.1 DB 마이그레이션

| 파일 | 설명 |
|------|------|
| `backend/migrations/037_go100_events.sql` | `go100_events` 테이블 생성 (event_id, ticker, event_type, event_date, title, content, source, impact_score, related_strategy_ids, raw_data). 인덱스: ticker+event_date, event_type, event_date. |

### 2.2 이벤트 수집기

| 파일 | 설명 |
|------|------|
| `scripts/go100/collect_events.py` | KRX 공시 페이지 크롤링(requests+BeautifulSoup), DART Open API(환경변수 `DART_API_KEY` 또는 `OPENDART_API_KEY` 있으면 사용). 수집 결과 `go100_events` UPSERT. `impact_score`는 단순 휴리스틱(이벤트 유형/제목 기반 -5~+5). |
| `scripts/go100/run_collect_events.sh` | 크론 실행용 래퍼. 평일 08:30 권장. |

**크론 등록 예시:**
```bash
30 8 * * 1-5 /root/kis-autotrade-v4/scripts/go100/run_collect_events.sh >> /var/log/go100/events.log 2>&1
```

### 2.3 이벤트 시그널 엔진

| 파일 | 설명 |
|------|------|
| `backend/app/services/go100/event_signal_engine.py` | `get_upcoming_events(days=7, ticker=None)`: 향후 N일 이벤트 조회. `get_event_impact(ticker)`: 종목별 이벤트 이력 + 이벤트 전후 주가 반응 요약. `process_events()`: 당일 생성 이벤트 → 전략카드 매칭 → 시그널 요약 반환. |

### 2.4 Agent 도구

| 도구 | 설명 |
|------|------|
| `get_events(ticker=None, days=7)` | 이벤트(어닝/공시) 조회. `agent_tools.py`에 정의, `tool_executors.py`에서 `event_signal_engine.get_upcoming_events` 호출. |
| `get_event_impact(ticker)` | 이벤트 영향도 분석. `event_signal_engine.get_event_impact` 호출. |

---

## 3. 파트 B: 잔여 이슈

### 3.1 ISS-011: /go100/chat 리다이렉트

| 파일 | 변경 내용 |
|------|-----------|
| `frontend/next.config.mjs` | `redirects()` 추가: `/go100/chat/` → `/go100/chat` (trailing slash 정규화). 기존 `(protected)/go100/chat/page.tsx`는 ChatWidget fullscreen 렌더 유지. |

### 3.2 ISS-012: ChatWidget user_id 동적 처리

| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/routers/go100/me_router.py` | 신규. `GET /api/go100/me` → `get_current_user` + `get_effective_uid` → `{ "user_id": number }`. |
| `backend/app/main.py` | `go100_me_router` 등록, prefix `/api/go100`. |
| `frontend/src/go100/api/go100Api.ts` | `getEffectiveUserId()` 추가. |
| `frontend/src/go100/components/ChatWidget.tsx` | `effectiveUserId` state 추가. 토큰 있으나 `user` 없을 때 `getEffectiveUserId()` 호출 후 `resolvedUserId = userId ?? effectiveUserId`로 채팅/보고서 건수 사용. 위젯 표시 조건: `user || effectiveUserId != null || hasToken()`. |

### 3.3 ISS-013: 백테스트 재시도 API

| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/routers/go100/backtest_router.py` | `POST /{run_id}/retry` 추가(지시서 경로). 기존 `POST /retry/{run_id}` 유지(레거시). 공통 로직 `_do_retry()`로 통합. |
| `frontend/src/go100/api/go100Api.ts` | `retryBacktest(runId)` 호출 경로를 `BASE/backtest/${runId}/retry`로 변경. |

---

## 4. 테스트

- **이벤트 수집:** `cd /root/kis-autotrade-v4 && PYTHONPATH=/root/kis-autotrade-v4 venv/bin/python3 scripts/go100/collect_events.py --dry-run` → 수집 건수 확인. (테이블 적용 후) `GO100_EVENTS_SEED=1` 로 실행 시 더미 1건 INSERT 가능.
- **Agent Chat:** "삼성전자 최근 이벤트 알려줘" → `get_events(ticker="삼성전자")` / `get_event_impact("삼성전자")` 호출 확인.
- **/go100/chat:** `curl -I http://localhost:3000/go100/chat` → 200 및 채팅 페이지 응답. `/go100/chat/` → 307/308로 `/go100/chat` 리다이렉트.
- **ChatWidget:** 로그인 후 스토어에 user 미동기 상태에서도 토큰 있으면 GET /api/go100/me로 effective user_id 사용해 채팅 가능.
- **재시도 API:** `curl -X POST -H "Authorization: Bearer <token>" http://localhost:8002/api/go100/backtest/<run_id>/retry` → `new_run_id`, `original_run_id`, `status: running` 확인.

---

## 5. 체크리스트

- [x] 코드 레포 반영 (kis-autotrade-v4)
- [ ] project-docs 보고서 push (본 문서)
- [ ] DB 마이그레이션 037 적용: `psql -h localhost -U kis_admin -d kisautotrade -f backend/migrations/037_go100_events.sql`
- [ ] 크론 등록 (필요 시)

---

## 6. 참고

- 이벤트 `impact_score` LLM 자동 판정은 수집 스크립트에서 생략(선택 사양). 필요 시 별도 배치에서 `event_signal_engine` 또는 LLM 호출로 갱신 가능.
- DART API 키 없으면 DART 수집은 skip, KRX만 시도.
