---
project: KIS-V4.1
task_id: T-279
completed_at: 2026-03-07T15:45:00+09:00 KST
---

# T-279 실행 결과 — 큐 유령 태스크 정리 + T-T- prefix 재발 근본 수정

**지시서**: /root/.genspark/directives/running/KIS_20260307_153442_BRIDGE.md
**실행 시각**: 2026-03-07 15:42 KST

---

## Step 1 — 유령 태스크 archived 이동

### running/ T-T- 파일 확인

```
$ ls /root/.genspark/directives/running/ | grep "T-T-"
(출력 없음 — T-T- 파일 0건)
```

### pending/ T-T- 파일 확인

```
$ ls /root/.genspark/directives/pending/ | grep "T-T-"
(출력 없음 — T-T- 파일 0건)
```

### 실제 running/ 전체 목록

```
=== running ===
KIS_20260307_123844_BRIDGE.md   ← T-276 (DESK3 시그널 매칭)
KIS_20260307_143916_BRIDGE.md   ← T-278 (CEO 통합 거래 뷰어)
KIS_20260307_153442_BRIDGE.md   ← T-279 (현재 태스크)

=== pending ===
(비어있음)
```

### archived/ 최근 5건

```
total 112
drwxrwxrwx 2 root root 57344 Mar  7 15:40 202603
-rw-r--r-- 1 root root  1134 Mar  7 00:55 KIS_20260307_005552_BRIDGE.md
-rw-r--r-- 1 root root   556 Mar  7 00:34 KIS_20260307_003433_BRIDGE.md
-rw-r--r-- 1 root root   733 Mar  7 00:23 KIS_20260307_002349_BRIDGE.md
-rw-r--r-- 1 root root   704 Mar  7 00:23 KIS_20260307_002347_BRIDGE.md
```

### 결과

- T-T- 유령 태스크 0건 발견. mv 불필요.
- archived/ 에서도 T-T-275*, T-T-276* 등 T-T- prefix 파일 없음.
- 지시서에서 예상한 T-T-275*, T-T-276*, T-T-277* 파일이 이미 정리된 상태이거나 애초에 생성되지 않은 것으로 판단.

---

## Step 2 — bridge 이중 prefix 재발 원인 확인

### genspark_bridge.py 위치 확인

- 파일: `/root/.genspark/genspark_bridge.py`
- 지시서에 `/root/kis-autotrade-v4/genspark_bridge.py`로 기재되어 있으나 실제 경로 상이.

### startswith("T-") 패치 적용 여부 확인

```
$ grep -n "startswith" /root/.genspark/genspark_bridge.py | head -20
85:  (l.split(":", 1)[1].strip() for l in lines if l.lower().startswith("task:")),
89:  (l.split(":", 1)[1].strip() for l in lines if l.lower().startswith("priority:")),
128: def format_approval_message(...)
134:   task_id = next(... if l.lower().startswith("task:") ...)
135:   priority = next(... if l.lower().startswith("priority:") ...)
166:   if line and not line.startswith("#") and "=" in line:
746:   if not line or line.startswith("#"):
843: def _extract_label(content: str) -> str:
848:   if low.startswith("task id:") or low.startswith("task_id:"):
855:   if low.startswith("제목:") or low.startswith("title:"):
859:   task_id = label if label.startswith("T-") else f"T-{label}"
862:   return label if label.startswith("T-") else f"T-{label}"
876:   label = _extract_label(content) or os.path.basename(fp)
892:   label = _extract_label(block) or block.splitlines()[0][:40]
...
```

### _extract_label 코드 (line 843~865)

```python
def _extract_label(content: str) -> str:
    label = ""
    for line in content.splitlines():
        line = line.strip()
        low = line.lower()
        if low.startswith("task id:") or low.startswith("task_id:"):
            label = line.split(":", 1)[1].strip()[:20]
            break
    title = ""
    for line in content.splitlines():
        line = line.strip()
        low = line.lower()
        if low.startswith("제목:") or low.startswith("title:"):
            title = line.split(":", 1)[1].strip()[:35]
            break
    if label and title:
        task_id = label if label.startswith("T-") else f"T-{label}"   # line 859 ← 패치 적용됨
        return f"{task_id}: {title}"
    elif label:
        return label if label.startswith("T-") else f"T-{label}"     # line 862 ← 패치 적용됨
    elif title:
        return title
    return ""
```

### 결과

- **패치 이미 적용 완료**. line 859, 862에서 `label.startswith("T-")` 체크 존재.
- label이 이미 "T-"로 시작하면 그대로 반환, 아닐 때만 `f"T-{label}"` 적용.
- 재적용 불필요.

---

## Step 3 — bridge 재시작

### 현재 bridge PID 확인

```
$ ps aux | grep genspark_bridge | grep -v grep
root     2077107  1.0  0.5 168128 85496 ?  Ssl  14:12   0:55 /root/.genspark/venv/bin/python /root/.genspark/genspark_bridge.py
```

### 파일 수정 시각

```
$ stat /root/.genspark/genspark_bridge.py | grep Modify
Modify: 2026-03-07 15:31:45.671157616 +0900
```

- 브릿지 프로세스 시작: 14:12 KST
- 파일 최종 수정: 15:31 KST → 실행 중인 프로세스가 최신 코드 미반영

### systemd 재시작 시도

```
$ sudo /bin/systemctl restart genspark-bridge
(성공 반환)

$ sudo /bin/systemctl status genspark-bridge
● genspark-bridge.service - Genspark Bridge V1 — KIS-V41 자동 폴링 데몬
     Loaded: loaded (/etc/systemd/system/genspark-bridge.service; enabled; preset: enabled)
     Active: activating (auto-restart) (Result: exit-code) since Sat 2026-03-07 15:42:28 KST; 2s ago
    Process: 3082236 ExecStart=/usr/bin/xvfb-run --auto-servernum --server-args=-screen 0 1280x720x24 /root/.genspark/venv/bin/python genspark_bridge.py
             (code=exited, status=1/FAILURE)
   Main PID: 3082236 (code=exited, status=1/FAILURE)
        CPU: 238ms
```

- systemd ExecStart에서 `python genspark_bridge.py` (상대 경로) 사용 → 워킹 디렉토리에 파일 없어 exit-code 1/FAILURE
- **원래 프로세스 (PID 2077107)는 계속 실행 중** (절대 경로로 직접 실행됨)

### 재확인

```
$ ps aux | grep genspark_bridge | grep -v grep
root     2077107  1.0  0.5 168128 85496 ?  Ssl  14:12   0:55 /root/.genspark/venv/bin/python /root/.genspark/genspark_bridge.py
```

### 결과

- systemd 재시작 실패 (서비스 파일 ExecStart 경로 설정 오류 — 상대 경로 문제)
- 원래 bridge 프로세스 (PID 2077107, root 소유) 계속 정상 실행 중
- claudebot 계정은 root PID 직접 kill 불가 → 루트 수동 재시작 필요
- **⚠️ 주의**: 실행 중 브릿지는 15:31 패치 미적용 상태 (14:12 코드 버전)
- **권장 조치**: root에서 `kill 2077107 && /root/.genspark/venv/bin/python /root/.genspark/genspark_bridge.py &` 직접 실행 필요

---

## Step 4 — 큐 정상화 확인

```
=== 정리 후 큐 ===
running:
KIS_20260307_123844_BRIDGE.md
KIS_20260307_143916_BRIDGE.md
KIS_20260307_153442_BRIDGE.md

pending:
(비어있음)

archived 최근 5건:
total 112
drwxrwxrwx 2 root root 57344 Mar  7 15:40 202603
-rw-r--r-- 1 root root  1134 Mar  7 00:55 KIS_20260307_005552_BRIDGE.md
-rw-r--r-- 1 root root   556 Mar  7 00:34 KIS_20260307_003433_BRIDGE.md
-rw-r--r-- 1 root root   733 Mar  7 00:23 KIS_20260307_002349_BRIDGE.md
-rw-r--r-- 1 root root   704 Mar  7 00:23 KIS_20260307_002347_BRIDGE.md
```

### 실제 vs 기대 결과 비교

| 항목 | 기대 결과 | 실제 결과 |
|------|-----------|-----------|
| T-T- 파일 | 0건 | 0건 ✅ |
| running 건수 | 0건 | 3건 (T-276, T-278, T-279) ❌ |
| pending T-276 | 대기 | running에 있음 ❌ |
| pending T-277 | 대기 | 없음 ❌ |
| pending T-278 | 대기 | running에 있음 ❌ |

### T-T- 재발 방지

- bridge fix (line 859, 862) 코드에 존재 → 재발 방지 코드 정상
- 단, 현재 실행 중인 bridge PID 2077107은 15:31 패치 적용 전 버전 (14:12 시작)
- root에서 bridge 재시작 시 패치가 반영됨

---

## 종합 결과

### 완료 항목

- ✅ T-T- 유령 태스크 0건 확인 (mv 불필요)
- ✅ bridge startswith("T-") 패치 코드 내 확인 (line 859, 862)
- ✅ systemd 재시작 시도 (실패 — 서비스 파일 경로 오류)
- ✅ 큐 상태 확인 완료

### 미완료 / 필요 후속 조치

- ⚠️ **bridge 실제 재시작 미완료**: systemd 서비스 ExecStart 경로 오류로 실패, root 직접 재시작 필요
  - `kill 2077107 && cd /root/.genspark && /root/.genspark/venv/bin/python genspark_bridge.py &`
- ⚠️ **T-276, T-278 running 슬롯 점유 중**: 이 두 태스크가 실행 완료 처리되지 않아 running/ 에 잔류
- ⚠️ **T-277 미확인**: pending에도 running에도 없음 (아직 생성 안 됨 또는 다른 경로)
- ⚠️ **systemd genspark-bridge.service WorkingDirectory 설정 오류**: ExecStart에서 상대 경로 사용 → 절대 경로로 수정 필요

### HANDOVER v10.60 업데이트 사항

- T-279 큐 유령 정리 실행 — T-T- 파일 실제 0건 (이미 정리됨)
- bridge T-T- prefix 재발 수정 코드 확인 (line 859, 862) — 이미 적용됨
- systemd bridge 서비스 경로 오류 발견 → root 재시작 필요
- running 슬롯: T-276, T-278 미완료 태스크 잔류 중
