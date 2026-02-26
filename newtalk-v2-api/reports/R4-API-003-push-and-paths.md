# R4-API-003 레포·문서 레포 푸시 및 경로 보고

**작성일시:** 2026-02-26 KST  
**비고:** Cursor 워크스페이스(`/root/newtalk-v2`)는 **git 저장소가 아님** — 실제 푸시는 서버(`/srv/newtalk-v2`)에서 수행.

---

## 1. 레포 정리

| 구분 | 레포 (clone URL) | 웹 URL |
|------|------------------|--------|
| **코드 레포 (V2 API)** | `git@github.com:moongoby/newtalk-v2-api-.git` | https://github.com/moongoby/newtalk-v2-api- |
| **문서 레포 (project-docs)** | `git@github.com:moongoby/project-docs.git` | https://github.com/moongoby/project-docs |

※ 코드 레포 이름 끝 **하이픈(`-`) 주의**

---

## 2. 서버에서 푸시 절차 (참고)

### 2.1 코드 레포 (newtalk-v2-api-)
```bash
cd /srv/newtalk-v2
git status
git add -A
git commit -m "[R4-API-003] AI 맞춤 피드 + 추천 엔진 — user_interests/product_scores/trend_snapshots, RecommendationService, TrendService, 7 EP (v3.3.0)"
git push origin main   # 또는 해당 브랜치
```

### 2.2 문서 레포 (project-docs)
```bash
# project-docs 클론 경로: /srv/newtalk-v2/project-docs-repo 또는 /root/project-docs-repo
cd /srv/newtalk-v2/project-docs-repo   # 또는 /root/project-docs-repo
git pull origin master

DEST=newtalk-v2-api/reports
mkdir -p "$DEST"
cp /srv/newtalk-v2/docs/reports/*.md "$DEST/" 2>/dev/null || true
# R4-API-003 보고서 포함 확인
ls -la "$DEST/R4-API-003-report.md"

git add newtalk-v2-api/
git status
git commit -m "[DOCS] R4-API-003 보고서 추가 (AI 맞춤 피드 + 추천 엔진)"
git push origin master
```

---

## 3. 경로 요약

### 3.1 코드 레포 (푸시 후)
- **저장소:** https://github.com/moongoby/newtalk-v2-api-
- **로컬(서버):** `/srv/newtalk-v2` (git root)
- **보고서 로컬 경로:** `/srv/newtalk-v2/docs/reports/R4-API-003-report.md`

### 3.2 문서 레포 (project-docs 푸시 후)
- **저장소:** https://github.com/moongoby/project-docs
- **newtalk-v2 문서 루트:** `newtalk-v2-api/` (master 기준)
- **R4-API-003 보고서 (project-docs 내):** `newtalk-v2-api/reports/R4-API-003-report.md`

**Public URL (푸시 후):**
- **Blob:** https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/reports/R4-API-003-report.md
- **Raw:** https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/reports/R4-API-003-report.md

---

## 4. Cursor 워크스페이스 상태

- **경로:** `/root/newtalk-v2` (또는 워크스페이스 루트)
- **Git:** 없음 (`fatal: not a git repository`) → **이 경로에서는 push 불가**
- **R4-API-003 보고서 파일:** `/root/newtalk-v2/docs/reports/R4-API-003-report.md` (작성 완료)
- 서버와 동기화된 뒤 서버에서 위 2.1·2.2 절차로 푸시하면 됨.
