# DOCS-ARCH-001 보완: project-docs 동기화 누락 수정

**작성일:** 2026-02-25 KST  
**문제:** DOCS-ARCH-001 보고서, NT-V2-ARCHITECTURE.md, CHANGELOG.md v2.2.0/v2.3.0이 project-docs에 반영되지 않음 (GitHub 404)

---

## 해결 방법

서버에서 **한 번에 실행**하는 스크립트를 사용합니다.

### 1. 서버 접속

```bash
ssh -p 7916 -i ~/.ssh/id_ed25519_newtalk root@114.207.244.86
```

### 2. 스크립트 실행

(스크립트가 이미 서버 `/srv/newtalk-v2`에 있다고 가정)

```bash
bash /srv/newtalk-v2/docs/scripts/DOCS-ARCH-001-remediation-sync.sh
```

로컬에서 서버로 스크립트만 복사해서 쓸 경우:

```bash
# 로컬에서
scp -P 7916 -i ~/.ssh/id_ed25519_newtalk \
  /root/newtalk-v2/docs/scripts/DOCS-ARCH-001-remediation-sync.sh \
  root@114.207.244.86:/tmp/

# 서버에서 (project-docs 경로가 /root/project-docs-repo인 경우)
bash /tmp/DOCS-ARCH-001-remediation-sync.sh
```

**주의:** 스크립트는 **`/root/project-docs-repo`**를 기준으로 동작합니다. 서버에서 project-docs가 다른 경로에 있으면 스크립트 내 `cd /root/project-docs-repo`를 해당 경로로 수정한 뒤 실행하세요.

---

## 스크립트가 하는 일

| 단계 | 내용 |
|------|------|
| 1 | 서버 파일 확인: `NT-V2-ARCHITECTURE.md`, `DOCS-ARCH-001-report.md` |
| 2 | `project-docs-repo` pull → `newtalk-v2-api/` 하위에 architecture, planning, reports, handover 복사, CHANGELOG/CONTEXT/HANDOVER/.cursorrules 복사 |
| 3 | CHANGELOG에 `[2.2.0]`, `[2.3.0]` 존재 여부 확인 |
| 4 | 민감 정보 검사 후 커밋·푸시 |
| 5 | 60초 대기 후 raw GitHub URL HTTP 200 검증 (재시도 1회) |
| 6 | `/data/project-docs/scripts/sync_newtalk_v2_api.sh`에 architecture/planning 포함 여부 확인 |
| 7 | 완료 시각·SHA·검증 URL 출력 |

---

## 검증 URL (성공 시 200)

- https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/architecture/NT-V2-ARCHITECTURE.md  
- https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/reports/DOCS-ARCH-001-report.md  
- https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/CHANGELOG.md  

---

## 전제 조건

- 서버에 `/srv/newtalk-v2/docs`가 최신 상태 (또는 DOCS-ARCH-001 지시서 실행 완료)
- `/root/project-docs-repo`가 클론되어 있고 `origin master` 푸시 권한 있음
- CHANGELOG.md에 v2.2.0, v2.3.0 항목이 이미 반영된 원본 사용

---

## 관련 파일

- **실행 스크립트:** `docs/scripts/DOCS-ARCH-001-remediation-sync.sh`  
- **기존 런북:** `docs/scripts/DOCS-ARCH-001-runbook.sh` (아키텍처 갱신 + `/data/project-docs` 수동 복사)
