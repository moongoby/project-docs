# 레포 / 문서 레포 푸시 경로 보고

**일시**: 2026-02-26 KST

---

## 1. V2 메인 레포 (newtalk-v2-api)

| 항목 | 값 |
|------|-----|
| **로컬 경로** | `/srv/newtalk-v2` |
| **원격** | `origin` (main) |
| **최신 커밋 SHA** | `f6c0bec` |
| **푸시 결과** | Everything up-to-date |

```
cd /srv/newtalk-v2
git push origin main
```

---

## 2. 문서 레포 (project-docs)

| 항목 | 값 |
|------|-----|
| **로컬 경로** | `/srv/newtalk-v2/project-docs-repo` |
| **원격** | `origin` (master) |
| **최신 커밋 SHA** | `21349ac` (pull 반영 후 원격 기준) |
| **푸시 결과** | pull 후 up-to-date |

```
cd /srv/newtalk-v2/project-docs-repo
git pull origin master --rebase
git push origin master
```

---

## 3. 요약

| 레포 | 경로 | 브랜치 | SHA (7자리) |
|------|------|--------|-------------|
| V2 메인 | `/srv/newtalk-v2` | main | **f6c0bec** |
| 문서 | `/srv/newtalk-v2/project-docs-repo` | master | **21349ac** |

---

## 4. 참고

- V2 메인: R4-API-007(드롭십/반품/풀필먼트) 코드는 커밋 `1b555ad`에 포함됨.
- 문서 레포: 원격에 shortflow 등 다른 프로젝트 보고서가 추가된 뒤 pull 반영됨. R4-API-007 보고서는 `newtalk-v2-api/reports/R4-API-007-report.md` 에 있음.
