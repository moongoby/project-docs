# CUR-GO100-BRIDGE-BUG-FIX-001 — genspark_bridge.py 메시지 잘림 버그 수정 보고서

| 항목 | 내용 |
|------|------|
| 지시 ID | CEO 긴급 점검 지시 (2026-03-02) |
| 보고 ID | CUR-GO100-BRIDGE-BUG-FIX-001-20260302 |
| 작성일 | 2026-03-02 |
| 작성자 | Cursor AI Agent (GO100 전담) |
| 상태 | ✅ 완료 |

---

## [인계 확인]
직전 완료: CUR-GO100-BRIDGE-EXPAND-001
현재 단계: Phase 4 AI 고도화 대기 + 브릿지 긴급 수정
CEO 지시 적용: D-006 (서비스 경계), PATH-001, REPORT-001
strategy_cards: 확인 불필요
open_positions: 0 (모의투자 URL 사용)

---

## 1. 요약

genspark_bridge.py가 GO100 대화창으로 전송하는 메시지가 `[CURSOR-GO100] CEO 승인 대기 — /`
(28자) 로 잘려서 2회 반복 전송되는 버그를 수정했다.

총 3종의 버그를 식별하고 수정했으며, 세션 시작 보고를 백억이 총괄매니저에게 정상 전송 완료했다.

---

## 2. 버그 분석

### Bug 1: 시스템 프롬프트 false positive (잘림 원인)

**현상:** 파싱 결과 지시 내용이 `/` (1자)만 추출됨

**원인:** `parse_directive()` 함수가 `>>>DIRECTIVE_START / >>>DIRECTIVE_END` 패턴을 정규식으로 파싱할 때, GO100 초기화 시스템 프롬프트 안의 예시 문구를 실제 지시로 오탐

```
시스템 프롬프트 내 문구:
"지시 응답은 >>>DIRECTIVE_START / >>>DIRECTIVE_END 블록으로 감싼다"
→ 정규식 매칭: content = " / " → strip() = "/" → len=1
```

기존 코드는 `len(content) < 20` 필터로 차단해야 하나, 다른 DIRECTIVE 블록 내용과 합쳐져
20자를 초과하는 잘못된 content가 생성되는 경우 필터를 통과함.

**수정:** 줄바꿈(`\n`) 포함 여부 추가 검증
```python
# 수정 전
if len(content) < 20:
    return None

# 수정 후
if len(content) < 20 or "\n" not in content:
    return None
```

### Bug 2: 피드백 루프 (2회 반복 전송 원인)

**현상:** 잘린 메시지 → AI가 DIRECTIVE로 재요청 → 브릿지가 재감지 → 반복

**원인:** `last_directive_hash` 는 동일 지시 재처리를 막지만, AI가 응답으로 새로운 DIRECTIVE 블록을 생성하면 hash가 달라져 재처리됨

**수정:** CEO 승인 대기 전송 후 **30분 쿨다운** 적용
```python
# 추가된 코드
last_ceo_approval_sent: dict[str, datetime.datetime | None] = {k: None for k in active_projects}
CEO_APPROVAL_COOLDOWN_SEC = 1800  # 30분

# 쿨다운 기간 내 재전송 차단
now_dt = datetime.datetime.now(KST)
last_sent = last_ceo_approval_sent[proj_key]
if last_sent is not None:
    elapsed = (now_dt - last_sent).total_seconds()
    if elapsed < CEO_APPROVAL_COOLDOWN_SEC:
        logger.debug("[%s] CEO 승인 대기 쿨다운 중 (%.0f초 남음) — 스킵", ...)
        continue
```

### Bug 3: React 호환 메시지 전송 (잘림 원인)

**현상:** `ta.fill(message)` + `Enter` 시 메시지가 `/` 이후로 잘려서 제출됨

**원인:** `fill()` 이나 `nativeInputValueSetter` 방식은 Genspark의 React 제어 컴포넌트 내부 상태를 갱신하지 못해, React가 아는 값(빈 값 또는 이전 값)이 제출됨

**수정:** `pressSequentially()` 방식으로 교체 (실제 키보드 타이핑 시뮬레이션)
```python
# 수정 전
await ta.fill(message)
await asyncio.sleep(0.5)
await page.keyboard.press("Enter")

# 수정 후
await ta.click()
await ta.press("Control+a")
await ta.press("Delete")
await asyncio.sleep(0.2)
await ta.press_sequentially(message, delay=15)
await asyncio.sleep(0.5)
await ta.press("Enter")
```

---

## 3. 서비스 상태 보고

| 항목 | 값 | 판정 |
|------|-----|------|
| go100 서비스 | active (running), 2026-03-01 12:09 기동 | ✅ 정상 |
| go100_risk_rules | 3행 | ✅ 정상 |
| go100_risk_events | 3행 | ✅ 정상 |
| go100_live_orders | 4행 | ✅ 정상 |
| GO100 테이블 수 | 65개 | ✅ 정상 |

---

## 4. .env 영향도 분석

| 항목 | 값 | GO100 영향 |
|------|-----|-----------|
| KIS_BASE_URL | https://openapivts.koreainvestment.com:29443 | **영향 없음** (모의투자 URL) |
| KIS_APP_KEY | 설정됨 | 영향 없음 |
| KIS_APP_SECRET | 설정됨 | 영향 없음 |
| .env 최종 수정 | 2026-03-02 13:31 | V4.1 세션에서 수정, GO100 서비스 재시작 없음 |

KIS_BASE_URL이 모의투자 URL(`openapivts`)로 설정되어 있으므로 GO100 KIS 주문 게이트웨이는
실주문 위험 없음.

---

## 5. 세션 시작 보고 전송 결과

백억이 총괄매니저 대화창 URL: https://www.genspark.ai/agents?id=167071cf-c8b5-476a-8953-6168dd6c910c

| 항목 | 결과 |
|------|------|
| 메시지 전송 | ✅ 성공 |
| AI 수신 확인 | ✅ "[CURSOR-GO100] 세션 시작 보고 수신 확인" |
| 다음 지시 | "미제출 보고서 (P6-EXTRA-VERIFY, P7-1 QA) 처리" |

---

## 6. 파일 변경 목록

| 파일 | 변경 내용 |
|------|----------|
| `/root/.genspark/genspark_bridge.py` | parse_directive 줄바꿈 필터 추가, CEO 승인 대기 30분 쿨다운, _send_chat_message pressSequentially 방식 교체 |

**V4.1 파일 변경 없음** (GO100 전담 규칙 준수)

---

## 7. 미제출 보고서 현황

| 항목 | 상태 | 우선순위 |
|------|------|----------|
| CUR-GO100-P6-EXTRA-VERIFY-20260227.md | 미제출 | 즉시 |
| CUR-GO100-P7-1-FULL-QA-20260227.md | 미제출 | 즉시 |

→ 백억이 총괄매니저 지시 후 처리 예정

---

## 저장 정보
- 서버 경로: /root/project-docs/go100/reports/CUR-GO100-BRIDGE-BUG-FIX-001-20260302.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-BRIDGE-BUG-FIX-001-20260302.md
- 커밋: https://github.com/moongoby/project-docs/commit/01520a7
- HTTP 확인: 200 ✅
- HANDOVER 업데이트: 완료
