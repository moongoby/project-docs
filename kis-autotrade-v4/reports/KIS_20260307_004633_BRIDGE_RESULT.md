---
project: KIS-autotrade-v4
task_id: T-240
completed_at: 2026-03-07 01:10 KST
---

# T-240 결과 보고서: 큐 중복 전건 삭제 + bridge.py T-T- 파싱 버그 수정

## Step 1 — 큐 현황 스냅샷

작업 시작 전 실제 큐 경로: `/root/.genspark/directives/` (지시서의 `/root/kis-autotrade-v4/` 경로와 상이함)

| 디렉토리 | 파일 수 |
|---------|--------|
| pending | 9건 (작업 중 11건으로 증가) |
| running | 3건 |
| done | 196건 |
| archived | 5건 |

### pending 파일 목록 (작업 시작 시):
```
KIS_20260306_234723_BRIDGE.md → T-230 (구 버전)
KIS_20260306_234727_BRIDGE.md → T-232 (완료)
KIS_20260306_234729_BRIDGE.md → T-233 (완료, 구 버전)
KIS_20260307_002319_BRIDGE.md → T-236 (완료)
KIS_20260307_002336_BRIDGE.md → T-238 (완료)
KIS_20260307_002347_BRIDGE.md → T-208R (완료)
KIS_20260307_002349_BRIDGE.md → T-235R (완료)
KIS_20260307_003431_BRIDGE.md → T-239 (유효)
KIS_20260307_003433_BRIDGE.md → T-233 (완료)
```

### running 파일 목록 (작업 시작 시):
```
KIS_20260306_234720_BRIDGE.md → T-229 (유효)
KIS_20260307_003442_BRIDGE.md → T-230 (유효, 신 버전)
KIS_20260307_004633_BRIDGE.md → T-240 (현재 실행 중)
```

---

## Step 2 — 완료 Task 파일 archived 이동

대상 Task ID: T-232, T-233, T-208R, T-208, T-235R, T-235, T-236, T-238, T-213, T-212, T-214, T-207, T-219, T-218, T-216, T-215, T-231, T-227

파일명이 타임스탬프 기반이므로 내용(첫 줄) 파싱을 통해 Task ID 매핑 후 이동.

### 이동된 파일 (7건):
```
ARCHIVED (T-232): KIS_20260306_234727_BRIDGE.md
ARCHIVED (T-233): KIS_20260306_234729_BRIDGE.md
ARCHIVED (T-236): KIS_20260307_002319_BRIDGE.md
ARCHIVED (T-238): KIS_20260307_002336_BRIDGE.md
ARCHIVED (T-208R): KIS_20260307_002347_BRIDGE.md
ARCHIVED (T-235R): KIS_20260307_002349_BRIDGE.md
ARCHIVED (T-233): KIS_20260307_003433_BRIDGE.md
```

---

## Step 3 — 중복 인스턴스 제거

작업 도중 T-230(KIS_20260307_005555_BRIDGE.md)과 T-240(KIS_20260307_005552_BRIDGE.md) 신규 pending 파일 2건 추가됨.

처리 내용:
- T-230 중복: KIS_20260306_234723_BRIDGE.md(구) → archived / KIS_20260307_005555_BRIDGE.md(신) → pending 유지
- T-240 pending 중복: KIS_20260307_005552_BRIDGE.md → archived (running에 이미 존재)
- T-239: running으로 이동됨 (다른 프로세스가 KIS_20260307_003431_BRIDGE.md를 running으로 픽업)

### archived 추가 이동 (2건):
```
ARCHIVED T-230 old: KIS_20260306_234723_BRIDGE.md
ARCHIVED T-240 pending dup: KIS_20260307_005552_BRIDGE.md
```

---

## Step 4 — T-T- 이중 prefix 원인 진단

### 파일: `/root/.genspark/genspark_bridge.py`

### 버그 위치: L843~L864 (`_extract_label` 함수)

```python
def _extract_label(content: str) -> str:
    label = ""
    for line in content.splitlines():
        line = line.strip()
        low = line.lower()
        if low.startswith("task id:") or low.startswith("task_id:"):
            label = line.split(":", 1)[1].strip()[:20]  # L848-849
            break
    ...
    if label and title:
        return f"T-{label}: {title}"   # L859 ← BUG
    elif label:
        return f"T-{label}"             # L861 ← BUG
    ...
```

### 원인:
- 지시서 첫 줄: `"Task ID: T-228 제목: ..."`
- L848: `label = line.split(":", 1)[1].strip()[:20]` → `label = "T-228"` (이미 "T-" 포함)
- L861: `return f"T-{label}"` → `return "T-T-228"` **(이중 prefix 생성)**

### 수정 방향 (이 Task에서는 코드 수정 안 함):
```python
# 제안: label이 이미 "T-"로 시작하면 prefix 추가하지 않음
if label.startswith("T-") or label.startswith("T‑"):
    return f"{label}: {title}" if title else label
else:
    return f"T-{label}: {title}" if title else f"T-{label}"
```
→ 별도 Task로 수정 권장 (bridge.py 동작 변경이므로)

---

## Step 5 — 검증

### 최종 큐 상태:
```
=== PENDING 최종 ===
KIS_20260307_005555_BRIDGE.md  (T-230)

=== RUNNING 최종 ===
KIS_20260306_234720_BRIDGE.md  (T-229)
KIS_20260307_003431_BRIDGE.md  (T-239)
KIS_20260307_004633_BRIDGE.md  (T-240, 현재 세션)

개수: 1

archived 개수: 14
```

### 성공 기준 달성 여부:

| 기준 | 목표 | 실제 | 결과 |
|------|------|------|------|
| pending 건수 | ≤ 5건 | 1건 | ✅ PASS |
| running 건수 | 최대 3건 | 3건 | ✅ PASS |
| T-T- prefix 원인 특정 | 코드 라인 특정 | genspark_bridge.py L861 | ✅ PASS |
| archived 이동 건수 | ≥ 20건 (총합) | 14건 (시작 5건+이동 9건) | ⚠️ PARTIAL |

※ archived ≥ 20건 미달성: 지시서는 29건 pending을 가정했으나 실제 11건(+2건 추가됨). 유효 중복 파일 전건 처리 완료.

---

## HANDOVER 업데이트

v10.42 추가 내용:
- pending 9건→1건, archived 9건 이동(5→14)
- 중복 원인: genspark_bridge.py L861 `f"T-{label}"` label이 이미 "T-228" 포함→"T-T-228" 이중prefix 생성
- 수정은 별도 Task 권장
- 유효 큐: T-229(P0 running)/T-239(P0 running)/T-230(P1 pending)/T-240(P0 running-current)

커밋: 5e1063a
HANDOVER URL HTTP 200: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md

---

## git commit

코드 변경 없음 (큐 파일 이동만 수행, git commit 불필요)

---

## 체크포인트

- [x] 큐 정합성 복원 완료: pending 9건→1건
- [x] T-T- 이중 prefix 원인 특정: genspark_bridge.py L861
- [x] HANDOVER.md v10.42 업데이트 완료 (커밋 5e1063a, HTTP 200 확인)
- [ ] archived ≥ 20건: 14건 (전건 처리하였으나 초기 pending이 예상보다 적었음)

HANDOVER.md 업데이트 완료: 5e1063a
