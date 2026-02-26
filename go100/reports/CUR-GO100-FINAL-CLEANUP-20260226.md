# GO100 마무리 작업 종합 보고 — 2026-02-26 최종

**작성일**: 2026-02-26  
**작업 범위**: 프로파일·usage_logs·DART·오버나이트 갭 MV·호가/틱 일간 집계 크론

---

## 1. 작업 1/5: go100_user_profile 스키마 수정 + 대표님 프로파일 INSERT

| 항목 | 결과 |
|------|------|
| 기존 구조 | `go100_user_profile`이 **뷰**(→ `go100_user_profiles` 참조)로 존재 |
| 조치 | 뷰 DROP 후 동일 이름으로 **테이블** 생성(요청 스키마) |
| 대표님 프로파일 | user_id=2, aggressive, swing, preferred_sectors 포함 AI, notes 반영 |

**확인 쿼리 결과**
```
 user_id | risk_tolerance | preferred_style |           preferred_sectors           | max_drawdown_tolerance | notes
---------+----------------+-----------------+---------------------------------------+------------------------+--------------------------------------------------
       2 | aggressive     | swing           | ["반도체", "자동차", "2차전지", "AI"] |                     15 | CEO — 수익이 나면 비용은 질문 없다. 정확도 우선.
```

**참고**: 앱에서 기존 `go100_user_profiles`(복수형) 테이블을 사용하는 코드는 그대로 두었음. 신규 테이블 `go100_user_profile`(단수)는 프로파일 확장/대표님 전용으로 사용 가능.

---

## 2. 작업 2/5: usage_logs 실제 검증

| 항목 | 결과 |
|------|------|
| go100_usage_logs 건수 | 0건 (채팅 발생 시 증가) |
| 테이블 스키마 | log_id, user_id, session_id, intent, message_preview, response_length, latency_ms, llm_model, llm_tokens_in/out, is_error, error_type, created_at |
| usage_logger | `backend.app.services.go100.ai.usage_logger.log_chat_usage` import 성공 |
| _log_usage 호출 | `ai_router.py` 내 **43개** 지점 (온보딩·help·전략·목표·종목·포트폴리오·라이브·스크리닝·백테스트·레짐·리밸런스·페이퍼 등) |

**프론트 채팅 후 확인**
```bash
sudo -u postgres psql -d kisautotrade -c "SELECT count(*) FROM go100_usage_logs;"
```

---

## 3. 작업 3/5: DART 정기 갱신 크론 등록

| 항목 | 결과 |
|------|------|
| 스크립트 | `/tmp/collect_dart_financials.py` → `scripts/data_collect/collect_dart_financials.py` 이동 완료 |
| 래퍼 | `scripts/go100/run_dart_collection.sh` 생성 (.env 로드 후 수집 스크립트 또는 인라인 폴백 실행) |
| cron | `30 19 * * 1` — 매주 **월요일 19:30** |
| 로그 | `/var/log/go100/dart.log` |

---

## 4. 작업 4/5: go100_overnight_gap MV REFRESH 크론

| 항목 | 결과 |
|------|------|
| 스크립트 | `scripts/go100/run_overnight_gap_refresh.sh` (sudo -u postgres psql로 MV REFRESH) |
| cron | `0 17 * * 1-5` — **평일 17:00** |
| 로그 | `/var/log/go100/overnight_gap.log` |

**참고**: MV `go100_overnight_gap` 존재 확인됨. REFRESH는 장 마감 후 실행되도록 17:00에 설정.

---

## 5. 작업 5/5: 호가/틱 일간 집계 크론 등록

| 항목 | 결과 |
|------|------|
| 호가 집계 | `scripts/go100/run_orderbook_daily_stats.sh` — `v4_orderbook_realtime`(captured_at 기준) → `go100_orderbook_daily_stats` |
| 틱 집계 | `scripts/go100/run_tick_daily_stats.sh` — `v4_tick_data`(tick_time 기준) → `go100_tick_daily_stats` |
| DB 연결 | .env 로드 및 PGPASSWORD/DB_USER 반영 (cron에서 비밀번호 인증 대응) |
| cron | 호가 `40 16 * * 1-5`, 틱 `50 16 * * 1-5` |
| 로그 | `/var/log/go100/orderbook_stats.log`, `/var/log/go100/tick_stats.log` |

**스키마 정합성**: 실제 테이블 컬럼명(예: `ask_price_1`, `bid_qty_1`, `captured_at`)에 맞춰 집계 쿼리 작성됨.

---

## 6. 크론 타임라인 (일간·월~금 기준)

| 시각 | 작업 |
|------|------|
| */5 | 헬스 모니터 |
| 07:00 | 크로스마켓 시그널 수집 |
| 08:50 | 모닝 브리핑 + KRX WS 시작 |
| 15:35 | (장 마감) |
| 15:40 | 장마감 리포트 + KRX WS 정지 |
| 16:10 | 페이퍼 트레이딩 |
| 16:40 | **호가 일간 집계** |
| 16:50 | **틱 일간 집계** |
| 17:00 | **오버나이트 갭 MV REFRESH** |
| 19:30 | **DART 재무 갱신 (월)** |
| 토 09:00 | 주간 보고 |

---

## 7. 서비스·디스크 상태

| 서비스 | 상태 |
|--------|------|
| go100 | active |
| go100-ws-nxt | active |
| go100-frontend | active |
| postgresql | active |

| 경로 | 사용량 |
|------|--------|
| /data | 15G / 196G (8%) |
| / | 65G / 99G (69%) |

---

## 8. 스킵/에러 정리

- **작업 1**: 완료 (뷰 → 테이블 전환 후 대표님 프로파일 INSERT)
- **작업 2**: 완료 (usage_logs 스키마·로거·43개 호출 지점 확인)
- **작업 3**: 완료 (DART 스크립트 이동·래퍼·cron 등록)
- **작업 4**: 완료 (오버나이트 갭 스크립트·cron 등록)
- **작업 5**: 완료 (호가/틱 스크립트·cron 등록, .env 기반 DB 연결 적용)

직접 실행 시 호가/틱 스크립트는 `PGPASSWORD`(또는 .env의 `DB_PASSWORD`)가 필요. cron에서는 `run_*_stats.sh`가 `.env`를 로드하므로 동일 서버에서 .env가 있으면 정상 동작.

---

## 9. go100 관련 cron 건수

- **총 go100 cron**: 19건 (신규 4건 포함)
- 신규: DART(월 19:30), 오버나이트 갭(평일 17:00), 호가 집계(평일 16:40), 틱 집계(평일 16:50)

---

**보고 끝.**
