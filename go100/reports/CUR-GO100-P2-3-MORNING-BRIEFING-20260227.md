# [GO100] P2-3: 자동 모닝 브리핑 생성 시스템 — 구현 보고

**문서 ID**: CUR-GO100-P2-3-MORNING-BRIEFING-20260227  
**작성일**: 2026-02-27  
**목표**: 매일 08:50 자동으로 전일 시장 요약 + 크로스마켓 시그널 + 오늘 관심 종목 브리핑 생성

---

## 1. 요약

| 항목 | 내용 |
|------|------|
| **1단계** | `backend/app/services/go100/report/morning_briefing.py` 신규 구현 — 전일 시장·크로스마켓 시그널 수집, Gemini Flash 요약, 텔레그램 발송, go100_reports 저장 |
| **2단계** | `scripts/go100/run_morning_briefing.sh` 수정 및 크론 등록 가이드 (08:50 월~금) |
| **3단계** | 브리핑 저장은 `go100_reports` 테이블 `report_type='daily_morning'` 로 동일 유지 |
| **4단계** | 채팅 "오늘 브리핑 보여줘" 시 최신 브리핑 반환 — C2SC `report_check` 핸들러 및 에이전트 도구 `get_latest_report` 수정 |

---

## 2. 구현 상세

### 2.1 브리핑 생성 서비스 (`morning_briefing.py`)

**경로**: `backend/app/services/go100/report/morning_briefing.py`

**역할**
- **전일 시장 데이터**: `index_daily` 최근 거래일, `v4_market_regime_daily` (KOSPI) 최근 1일
- **크로스마켓 시그널**: `go100_cross_market_signals` 최근 28건
- **글로벌 시장**(선택): `go100_global_market` 최근 1일 (USD/KRW, VIX, S&P, 나스닥, 다우 등)
- **LLM 요약**: Gemini Flash (`GO100_MORNING_BRIEFING_MODEL` 또는 `gemini-2.0-flash`)로 5~8문장 요약 생성
- **텔레그램 발송**: `GO100_TELEGRAM_BOT_TOKEN`, `GO100_TELEGRAM_CHAT_ID` 사용, 기존 `alert_sender.send_telegram` 재사용
- **저장**: `go100_reports`에 `report_type='daily_morning'`, `user_id`는 ACTIVE 목표 사용자 또는 `GO100_ALERT_USER_ID`(기본 1)

**엔트리포인트**
- `run_morning_briefing(user_ids: Optional[List[int]] = None)` — 비동기 1회 실행
- `if __name__ == "__main__"`: `main()` — 크론/쉘에서 직접 실행 시 프로젝트 루트 추가 후 `asyncio.run(run_morning_briefing())` 호출

**환경 변수**
- `GOOGLE_AI_API_KEY` 또는 `GEMINI_API_KEY`: Gemini 요약용
- `GO100_MORNING_BRIEFING_MODEL`: (선택) 기본 `gemini-2.0-flash`
- `GO100_TELEGRAM_BOT_TOKEN`, `GO100_TELEGRAM_CHAT_ID`: 텔레그램 발송
- `GO100_ALERT_USER_ID`: 보고서 저장 기본 user_id (기본 1)

### 2.2 크론 스크립트 및 등록

**스크립트**: `scripts/go100/run_morning_briefing.sh`

- 프로젝트 루트로 이동, 가상환경 활성화(.venv 또는 venv), `run_morning_briefing` 모듈 실행
- 로그: 표준출력/표준에러를 크론에서 리다이렉트하여 저장

**크론 등록 예시**
```bash
# 매일 08:50 (월~금) 모닝 브리핑
50 8 * * 1-5 /root/kis-autotrade-v4/scripts/go100/run_morning_briefing.sh >> /var/log/go100/morning_briefing.log 2>&1
```

- `/var/log/go100/` 디렉터리 및 권한은 배포 환경에 맞게 사전 생성 필요

### 2.3 go100_reports 저장

- 기존 `proactive_reporter.save_report` 사용
- `report_type='daily_morning'`, `title` 예: `모닝 브리핑 — 2026-02-27(목)`, `priority='normal'`
- 저장 대상: `go100_goals`에서 `status='ACTIVE'`인 `user_id` 목록; 없으면 `GO100_ALERT_USER_ID` 1건

### 2.4 채팅에서 "오늘 브리핑 보여줘" 반환

**C2SC 경로 (인텐트 report_check)**
- `_handle_report_check(message, user_id, db)` 시그니처로 변경
- 메시지에 "브리핑" + ("보여줘" 또는 "오늘") 포함 시: 해당 `user_id`의 최신 `report_type='daily_morning'` 1건 조회 후 본문(`content`) 반환
- 없으면: "아직 오늘 모닝 브리핑이 생성되지 않았어요. 매일 08:50에 자동으로 생성돼요." 안내
- 그 외: 기존처럼 미읽은 보고서 목록 반환

**에이전트 도구 (get_latest_report)**
- `tool_executors.get_latest_report(report_type="morning")` 호출 시 DB에는 `daily_morning`으로 저장되므로, `report_type` 매핑 추가:
  - `morning` → `daily_morning`, `closing` → `daily_close`, `weekly` → `weekly`, `event` → `event_alert`
- "오늘 브리핑 보여줘" 등으로 에이전트가 `get_latest_report("morning")` 호출 시 최신 모닝 브리핑 내용 반환

---

## 3. 파일 변경 목록

| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/services/go100/report/__init__.py` | 신규 — `run_morning_briefing` export |
| `backend/app/services/go100/report/morning_briefing.py` | 신규 — 수집·LLM·텔레그램·저장 로직 |
| `scripts/go100/run_morning_briefing.sh` | 수정 — 새 모듈 호출, 로그 경로 주석에 명시 |
| `backend/app/services/go100/ai/tool_executors.py` | `get_latest_report`: report_type 매핑 추가 |
| `backend/app/routers/go100/ai_router.py` | `_handle_report_check`에 message 인자 추가, "브리핑 보여줘/오늘" 시 최신 daily_morning 본문 반환; `intent_type == "report_check"` 분기 추가 |

---

## 4. 확인 사항

- **크론**: 위 한 줄을 crontab에 등록 후 08:50(월~금) 실행 및 `morning_briefing.log` 확인
- **텔레그램**: `GO100_TELEGRAM_*` 설정 시 브리핑 본문 수신 여부 확인
- **채팅**: "오늘 브리핑 보여줘", "브리핑 보여줘" 입력 시 최신 모닝 브리핑 내용이 표시되는지 확인 (C2SC 및 에이전트 모드 모두)
- **DB**: `go100_reports`에서 `report_type='daily_morning'` 최신 1건 존재 여부 확인

---

## 5. 참고

- 기존 `proactive_reporter.generate_morning_briefing`는 사용자별 포트폴리오·레짐 권고 등 개인화 브리핑용으로 유지. P2-3 모닝 브리핑은 **공통 시장 데이터 + 크로스마켓 시그널 + LLM 요약**을 매일 08:50에 1회 생성·발송·저장하는 흐름으로 분리됨.
- `daily_reports.py --type morning`은 기존 proactive 모닝 브리핑(사용자별)을 사용하는 크론용이며, 08:50 자동화는 `run_morning_briefing.sh`(새 서비스) 사용을 권장.
