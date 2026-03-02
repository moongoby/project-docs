# INDEX.md project-docs 동기화 + sync 스크립트 수정

**작성일시:** 2026-02-23 18:12 KST  
**작업 유형:** 설정 변경 / 문서화  
**상태:** 완료  
**관련 파일:** `/data/project-docs/scripts/sync_shortflow.sh`, `project-docs/shortflow/INDEX.md`

---

## 1. 작업 개요

- **목적:** project-docs 저장소에 shortflow `INDEX.md`를 shortflow 루트(`shortflow/INDEX.md`)로 동기화하고, 동기화 스크립트에 해당 복사 로직을 추가.
- **서버:** [SERVER-HOSTNAME]  
- **프로젝트:** /data/shortflow  
- **GitHub (public):** git@github.com:moongoby/project-docs.git (master)

## 2. 변경 사항

### 2.1 sync_shortflow.sh 수정 (diff)

**백업 경로:** `/data/shortflow/backups/20260223_175805/sync_shortflow.sh.bak`

```diff
--- backups/.../sync_shortflow.sh.bak
+++ /data/project-docs/scripts/sync_shortflow.sh
@@ -11,6 +11,10 @@
 # cursorrules
 cp /data/shortflow/.cursorrules ${DST}/cursorrules.md 2>/dev/null
 
+# INDEX.md 동기화 (shortflow 루트)
+cp /data/shortflow/docs/reports/INDEX.md ${DST}/INDEX.md 2>/dev/null || true
+cp /data/shortflow/reports/INDEX.md ${DST}/INDEX.md 2>/dev/null || true
+
 # 인계서 (최신 3개)
 mkdir -p ${DST}/handover
 ls -t ${SRC}/handover/2*.md 2>/dev/null | head -3 | while read f; do cp "$f" ${DST}/handover/; done
```

- **추가 내용:** shortflow 루트에 `INDEX.md`를 복사하는 2줄 추가. `docs/reports/INDEX.md` 우선, 없으면 `reports/INDEX.md`로 덮어쓰기.

### 2.2 INDEX.md 행 수

| 위치 | 행 수 (wc -l) |
|------|----------------|
| /data/shortflow/reports/INDEX.md | 85 |
| /data/project-docs/shortflow/INDEX.md | 84 |

(동기화 후 project-docs 쪽은 84행, 원본 85행과 동일 내용 기준.)

## 3. project-docs 커밋 및 push

- **커밋 해시:** `1792157`
- **커밋 메시지:** `[sync] shortflow: INDEX.md 동기화 + sync_shortflow.sh 수정`
- **push 결과:** 성공  
  - `3bfb599..1792157  master -> master`

## 4. 검증

### 4.1 raw URL HTTP 200 확인

- **URL:** https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/INDEX.md  
- **결과:** `HTTP/2 200` (확인 시각: push 후 약 90초 경과)

### 4.2 project-docs 최근 커밋 (확인 시점)

```
1792157 [sync] shortflow: INDEX.md 동기화 + sync_shortflow.sh 수정
3bfb599 docs: KIS API 문서 push — xlsx/pdf/md (20260223)
bd9e758 docs: CUR-GO100-INVEST-AMOUNT-FIX-001 투자금/비중 주문반영 보고
```

## 5. 주의사항 / 후속 작업

- 이후 `bash /data/project-docs/scripts/sync_shortflow.sh` 실행 시 `shortflow/INDEX.md`가 자동 갱신됨.
- 보고서 GitHub(raw) 위치:  
  https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/reports/20260223_index_sync_수정.md  
  (Step 7 동기화 후 접근 가능)
