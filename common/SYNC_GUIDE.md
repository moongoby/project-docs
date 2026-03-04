# 문서 동기화 가이드
> 각 프로젝트 서버 → project-docs Public 저장소 동기화 방법

## 동기화 대상
- CONTEXT.md
- cursorrules (원본 .cursorrules → 사본 cursorrules.md)
- 최신 인계서 3개
- 보고서

## 동기화 스크립트 작성 규칙

### 로컬 서버 (114서버 등 git 직접 접근 가능)
```bash
#!/bin/bash
SRC="/프로젝트/docs"
DST="/data/project-docs/[폴더명]"
cp ${SRC}/CONTEXT.md ${DST}/
cp /프로젝트/.cursorrules ${DST}/cursorrules.md
ls -t ${SRC}/handover/2*.md 2>/dev/null | head -3 | while read f; do cp "$f" ${DST}/handover/; done
cd /data/project-docs && git add -A
git diff --cached --quiet || { git commit -m "[sync] [폴더명] $(date +%Y%m%d_%H%M)"; git push origin master; }
```

### 원격 서버 (NAS 등 SSH 접근)
```bash
#!/bin/bash
NAS_HOST="[NAS_HOST]"
NAS_PORT="[NAS_PORT]"
NAS_SRC="/프로젝트경로/docs"
DST="/data/project-docs/[폴더명]"
scp -P ${NAS_PORT} ${NAS_HOST}:${NAS_SRC}/CONTEXT.md ${DST}/
scp -P ${NAS_PORT} ${NAS_HOST}:/프로젝트경로/.cursorrules ${DST}/cursorrules.md
cd /data/project-docs && git add -A
git diff --cached --quiet || { git commit -m "[sync] [폴더명] $(date +%Y%m%d_%H%M)"; git push origin master; }
```

## 동기화 실행 시점
- CONTEXT.md 변경 시
- cursorrules 변경 시
- 대화 종료 시 (인계서 작성 후)
- 보고서 발행 시

## 등록된 동기화 스크립트
| 프로젝트 | 서버 | 스크립트 |
|----------|------|----------|
| ShortFlow | 114서버 | /data/project-docs/scripts/sync_shortflow.sh |
| GO100 | GO100서버 | /root/project-docs/scripts/sync_go100.sh |
| NAS Image | 114서버(원격) | /data/project-docs/scripts/sync_nas_image.sh |
