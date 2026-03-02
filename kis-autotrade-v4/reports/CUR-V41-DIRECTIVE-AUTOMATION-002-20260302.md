# CUR-V41-DIRECTIVE-AUTOMATION-002-20260302

[인계 확인]
직전 완료: CUR-V41-DIRECTIVE-AUTOMATION-001
현재 단계: Bridge 자동화 인프라 — 추가 지시 반영
CEO 지시 적용: D-001, D-002
strategy_cards: 60
open_positions: 14

---

## 작업 개요

- **Task ID**: CUR-V41-DIRECTIVE-AUTOMATION-002
- **Priority**: P0
- **작업일**: 2026-03-02 KST
- **목적**: Directive 자동화 추가 지시 5건 일괄 반영

---

## 추가 1 — KST 타임스탬프 전면 적용

### 적용 범위

| 파일 | 변경 내용 |
|------|-----------|
| `genspark_bridge.py` | logging formatter에 `_kst_time` converter 적용 → `%(asctime)s KST` |
| `genspark_bridge.py` | `_get_latest_commit()` — GitHub UTC ISO 8601 → `astimezone(KST)` → `HH:MM KST` |
| `genspark_bridge.py` | `save_directive_to_pending()` — `datetime.now(KST).isoformat()` (+09:00 포함) |
| `run_pending.sh` | `export TZ="Asia/Seoul"` + `date` 출력에 `KST` 레이블 |
| `write_done.py` (신규) | `datetime.now(KST)` 기반, 파일명/프런트매터 전부 KST |
| `telegram_report.py` | datetime 미사용 — KST 적용 불필요 확인 |

### 검증
```
✅ UTC 잔여 없음 (grep 0건)
✅ KST 레이블: 13건 (bridge.py 내)
로그 출력: 2026-03-02 19:53:05,238 KST [INFO] 활성 프로젝트: [...]
```

---

## 추가 2 — 정기 보고 30분 주기 + 형식 개선

### 변경 전/후

**이전:**
```
KIS: {svc} | 최근커밋: {SHA} | 미완료작업 없음
GO100: 최근커밋: {SHA} | 미완료작업 없음
```

**이후:**
```
[통합현황] 2026-03-02 19:52 KST
KIS: {svc} | 최근커밋: abc1234 (2026-03-02 19:48 KST) | pending: 0건
GO100: 최근커밋: abc1234 (...) | pending: 0건
AADS: 최근커밋: abc1234 (...) | pending: 0건
SF: 최근커밋: abc1234 (...) | pending: 0건
NAS: 최근커밋: abc1234 (...) | pending: 0건
NTV2: 최근커밋: abc1234 (...) | pending: 0건
running: 1건 | done(미처리): 2건
```

### 신규 함수
- `_count_pending_for_project(project_tag)` — `PENDING_DIR/{tag}_*.md` 파일 수 반환
- `build_unified_status_report()` 전면 개선 (프로젝트별 pending 카운트 포함)
- `PERIODIC_REPORT_HOURS_KST` 잔여 없음 확인 ✅ (30분 기반만 존재)

---

## 추가 3 — done 파일 작성 스크립트

### 파일: `/root/.genspark/write_done.py`

**사용법:**
```bash
python3 /root/.genspark/write_done.py \
  --project KIS \
  --task-id CUR-V41-EXAMPLE-001 \
  --commit 50bd69a \
  --http 200 \
  --security-scan 0건 \
  --path-check PASS \
  --summary "작업 1줄 요약" \
  --report-url "https://github.com/moongoby/project-docs/blob/master/..."
```

**생성 파일 위치:**
```
/root/.genspark/directives/done/{PROJECT}_{YYYYMMDD}_{HHMMSS}_KST.md
```

**생성 파일 형식:**
```markdown
---
project: KIS
task_id: CUR-V41-EXAMPLE-001
completed_at: 2026-03-02 19:52:50 KST
commit: 50bd69a
http: 200
security_scan: 0건
path_check: PASS
---
[CURSOR-KIS] 2026-03-02 19:52 KST 작업 완료
작업: 작업 1줄 요약
커밋: 50bd69a
보고서: https://github.com/moongoby/...
```

**테스트 결과:**
```
✅ done 파일 생성: /root/.genspark/directives/done/KIS_20260302_195250_KST.md
✅ 파일명 형식: {PROJECT}_{YYYYMMDD}_{HHMMSS}_KST.md
✅ 프런트매터 형식 PASS
bridge.py가 10초 내 감지 → 매니저 대화창 + CEO 지휘소 자동 중계
```

---

## 추가 4 — .cursorrules 섹션 9-10 추가

`/root/kis-autotrade-v4/.cursorrules`에 섹션 9-10 추가:

```
9-10. Directive 자동화 (2026-03-02 추가)
- bridge.py가 매니저 대화창에서 >>>DIRECTIVE_START 감지 → pending/ 자동 저장
- Cursor 실행: bash /root/.genspark/run_pending.sh {PROJECT}
- 파일 이동 순서: pending/ → running/ → done/
- done 파일 생성: python3 /root/.genspark/write_done.py ...
- bridge.py 10초 내 감지 → 매니저+CEO+텔레그램 자동 중계
- 모든 타임스탬프는 KST (UTC 금지)
```

---

## 추가 5 — CEO-COMMAND-CENTER.md 섹션 9 추가

`/root/project-docs/shared/CEO-COMMAND-CENTER.md`에 섹션 9 신규 추가:
- 전체 흐름 다이어그램 (CEO 승인 → bridge 감지 → pending → running → done → 자동 중계)
- 폴더 구조 설명
- 스크립트 명령어 테이블
- 타임스탬프 규칙 (KST 강제, UTC 금지)

---

## 테스트 결과 요약

| 항목 | 결과 |
|------|------|
| bridge.py 문법 검증 | ✅ PASS |
| UTC 잔여 검사 | ✅ 0건 |
| KST 레이블 확인 | ✅ 13건 |
| write_done.py 실행 | ✅ PASS |
| done 파일 형식 | ✅ PASS |
| 통합현황 보고 형식 | ✅ PASS |
| genspark-bridge 재시작 | ✅ active |
| 로그 KST 표시 | ✅ `2026-03-02 19:53:05,238 KST` |

---

## 파일 목록

| 파일 | 유형 | 설명 |
|------|------|------|
| `/root/.genspark/genspark_bridge.py` | 수정 | KST 전면 적용 + 정기보고 형식 개선 + pending 현황 |
| `/root/.genspark/write_done.py` | 신규 | done 파일 생성 스크립트 |
| `/root/kis-autotrade-v4/.cursorrules` | 수정 | 섹션 9-10 추가 |
| `/root/project-docs/shared/CEO-COMMAND-CENTER.md` | 수정 | 섹션 9 Directive 자동화 추가 |

> ⚠️ .genspark/ 파일은 project-docs에 커밋하지 않음 (보안 규칙)

---

## 체크포인트
- [x] 코드 수정 완료
- [ ] project-docs 보고서 push 완료 (진행 중)

HANDOVER.md 업데이트 완료: {커밋해시 — push 후 기재}
