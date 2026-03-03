# CUR-V41-DIRECTIVE-AUTOMATION-001-20260302

[인계 확인]
직전 완료: CUR-V41-ALL-MANAGER-CHATS-001
현재 단계: Bridge 자동화 인프라
CEO 지시 적용: D-001, D-002
strategy_cards: 60
open_positions: 14

---

## 작업 개요

- **Task ID**: CUR-V41-DIRECTIVE-AUTOMATION-001
- **Priority**: P0
- **작업일**: 2026-03-02 KST
- **목적**: bridge.py Directive 자동 감지·저장·완료 중계 체계 구축

---

## 구현 내역

### Step 1 — 디렉토리 생성 ✅
```
/root/.genspark/directives/
├── pending/    # bridge가 감지한 Directive 저장
├── running/    # run_pending.sh로 이동하여 실행 중
├── done/       # Cursor가 완료 후 이동
└── archived/   # bridge가 done 처리 후 YYYYMM/ 이동
```

### Step 2 — bridge.py: Directive 감지 → pending 저장 ✅

신규 함수:
- `_parse_directive_meta(body)` — Task ID / Priority 파싱
- `_compute_content_hash(body)` — sha256 해시 계산
- `_is_duplicate_directive(hash)` — pending/running/done 전체 중복 검사
- `save_directive_to_pending(body, project, source_chat)` — 프런트매터 포함 파일 저장

파일 형식:
```markdown
---
project: KIS
task_id: TEST-DIRECTIVE-001
priority: P3
detected_at: 2026-03-02T19:44:00+09:00
source_chat: https://www.genspark.ai/agents?id=77de652f-...
content_hash: <sha256>
---
(Directive 본문)
```

폴링 루프에서 DIRECTIVE 감지 즉시:
1. `save_directive_to_pending()` 호출
2. 중복이 아닐 경우 텔레그램 발송: `[KIS] 새 Directive 감지 — {Task ID} (pending 저장 완료)`

### Step 3 — bridge.py: done 폴더 감시 → 결과 중계 ✅

신규 함수:
- `process_done_directives(page, projects_cfg, processed_done_files)` — done/ 새 파일 목록 반환
- `archive_done_file(filepath)` — done 파일 → archived/{YYYYMM}/ 이동

메인 폴링 루프에 10초 간격 done 감시 추가:
1. 해당 프로젝트 매니저 대화창에 결과 전송
2. CEO 통합지휘소에 요약 전송
3. 텔레그램 발송: `[KIS] 작업 완료 — {Task ID}`
4. archived/{YYYYMM}/ 로 이동

### Step 4 — run_pending.sh 생성 ✅

경로: `/root/.genspark/run_pending.sh`

```bash
bash run_pending.sh           # 전체 pending 목록 표시
bash run_pending.sh KIS       # KIS pending → running 이동 + 내용 출력
bash run_pending.sh GO100     # GO100 pending → running 이동 + 내용 출력
```

### Step 5 — 정기 보고에 pending 현황 포함 ✅

`build_unified_status_report()` 하단에 추가:
```
[Directive 현황]
  pending: N건
  running: N건
  최근 완료: {Task ID} (HH:MM KST)
```

### Step 6 — KST 타임스탬프 전면 적용 ✅ (추가 지시)

| 대상 | 변경 내용 |
|------|-----------|
| logging formatter | `%(asctime)s KST` + `converter = _kst_time` (명시적 KST 강제) |
| `_get_latest_commit()` | GitHub UTC → `utc_dt.astimezone(KST)` 변환 후 `HH:MM KST` 표시 |
| `run_pending.sh` | `export TZ="Asia/Seoul"` 선언 + date 출력에 `KST` 레이블 |
| `save_directive_to_pending()` | `datetime.now(KST).isoformat()` → `+09:00` 포함 ISO 8601 |

로그 출력 예시:
```
2026-03-02 19:47:53,240 KST [INFO] 활성 프로젝트: ['KIS', 'GO100', ...]
```

---

## 테스트 결과

### 단위 테스트 5/5 PASS
| 테스트 | 결과 |
|--------|------|
| 메타 파싱 (Task ID / Priority) | ✅ PASS |
| sha256 해시 일관성 | ✅ PASS |
| pending 파일 저장 | ✅ PASS |
| 중복 감지 | ✅ PASS |
| run_pending.sh 출력 확인 | ✅ PASS |

### bridge.py 문법 검증
```
✅ 문법 검증 PASS
✅ UTC 노출 없음
```

### 서비스 재시작
```
genspark-bridge.service: active
로그: 2026-03-02 19:47:53,240 KST [INFO] 활성 프로젝트: ['KIS', 'GO100', 'AADS', 'SF', 'NAS', 'NTV2']
```

### run_pending.sh 동작 확인
```bash
$ bash run_pending.sh
=== 대기 중인 Directive ===
▶ KIS_20260302_194400.md
  project: KIS / task_id: TEST-DIRECTIVE-001 / priority: P3

$ bash run_pending.sh KIS
==========================================
실행 중: KIS_20260302_194400.md  [2026-03-02 19:43:00 KST]
==========================================
(내용 출력 후 pending → running 이동)
```

---

## 파일 목록

| 파일 | 유형 | 설명 |
|------|------|------|
| `/root/.genspark/genspark_bridge.py` | 수정 | Directive 자동화 + KST 전면 적용 |
| `/root/.genspark/run_pending.sh` | 신규 | pending 조회 및 running 이동 스크립트 |
| `/root/.genspark/directives/pending/` | 신규 디렉토리 | 감지된 Directive 대기 |
| `/root/.genspark/directives/running/` | 신규 디렉토리 | 실행 중인 Directive |
| `/root/.genspark/directives/done/` | 신규 디렉토리 | 완료된 Directive |
| `/root/.genspark/directives/archived/` | 신규 디렉토리 | 아카이브 |

> ⚠️ .genspark/ 파일은 project-docs에 커밋하지 않음 (보안 규칙)

---

## 체크포인트
- [x] 코드 수정 완료 (genspark_bridge.py + run_pending.sh)
- [ ] project-docs 보고서 push 완료 (진행 중)

HANDOVER.md 업데이트 완료: 50bd69a
