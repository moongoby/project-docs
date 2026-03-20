---
project: AADS
task_id: AADS-JUDGE-PARSE-FIX
completed_at: 2026-03-20 18:30 KST
status: completed
---

# AADS Judge Agent JSON 파싱 수정 보고서

**작업 ID**: AADS-JUDGE-PARSE-FIX
**날짜**: 2026-03-20
**배경**: "AI 검수 응답을 파싱할 수 없습니다. 수동 확인이 필요합니다" 반복 피드백 수정

---

[인계 확인]
직전 완료: DESK1-VOL-CORRECTION (2026-03-20)
현재 단계: Phase 2 운영
CEO 지시 적용: D-001 (서비스 재시작 금지 — KIS/GO100 한정, AADS는 별도)
strategy_cards: 기존 유지
open_positions: N/A

---

## 1. 문제 원인 분석

### 증상
- "AI 검수 응답을 파싱할 수 없습니다. 수동 확인이 필요합니다" 피드백이 반복적으로 발생
- 2026-03-19 ~ 2026-03-20 여러 Claude Code 세션에 queue-operation으로 전달됨

### 근본 원인

`/root/aads-server/app/agents/judge_agent.py`의 JSON 파싱 로직 오류:

**수정 전 (greedy regex — 문제)**:
```python
json_match = re.search(r'\{[\s\S]*\}', content)
if json_match:
    verdict_dict = json.loads(json_match.group())
```

**문제점**:
1. `\{[\s\S]*\}` greedy 매칭이 중첩된 JSON 객체에서 오파싱 발생
2. LLM 응답이 `` ```json ... ``` `` markdown code block으로 감싸진 경우 처리 불가
3. gemini-3.1-pro-preview 모델이 불안정/미존재로 파싱 실패 유발

---

## 2. 수정 내용

### 2.1 judge_agent.py — JSON 파싱 강화

**수정 후 (depth-tracking + markdown block 처리)**:
```python
text = content.strip()
# 1. markdown code block 우선 추출
code_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
if code_match:
    text = code_match.group(1).strip()
# 2. depth-tracking으로 JSON 객체 추출 (greedy 매칭 오류 방지)
start = text.find('{')
if start >= 0:
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{': depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                verdict_dict = json.loads(text[start:i + 1])
                break
```

### 2.2 model_router.py — Judge 모델 변경

| 항목 | 이전 | 이후 |
|------|------|------|
| primary 모델 | gemini-3.1-pro-preview | gemini-2.5-flash |
| 입력 비용 | $2.00/M | $0.30/M |
| 출력 비용 | $12.00/M | $2.50/M |
| 사유 | 미존재/불안정 | 안정적, 비용 절감 |

---

## 3. 배포 내용

### 3.1 로컬 커밋 (server-211, /root/aads-server)
- 커밋: `e1f3fcd` — fix: Judge Agent JSON 파싱 강화 + 모델 변경
- 파일: `app/agents/judge_agent.py`, `app/services/model_router.py`

### 3.2 server-68 배포
- SCP 배포: `judge_agent.py`, `model_router.py` → `/root/aads/aads-server/app/`
- 볼륨 마운트: `/root/aads/aads-server/app → /app/app` (자동 반영)
- `docker restart aads-server` 완료
- 재시작 후 상태: `Up 24 seconds (healthy)` ✅

---

## 4. 검증

| 항목 | 결과 |
|------|------|
| aads-api RUNNING | ✅ supervisord success: aads-api entered RUNNING state |
| aads-server healthy | ✅ Up (healthy) 확인 |
| mcp-filesystem/git/memory | ✅ 모두 RUNNING 상태 |

---

## 5. 예상 효과

Judge Agent가 LLM 응답을 정상적으로 파싱하여:
- "AI 검수 응답을 파싱할 수 없습니다" 오류 발생 중단
- JSON parse fallback ("conditional_pass, 수동 확인 필요") 대신 실제 판정 반환
- gemini-2.5-flash로 안정적이고 저렴한 Judge 실행

---

HANDOVER.md 업데이트 완료: e1f3fcd
