# v1.2.0 project-docs 동기화 실행 순서

SSH: `ssh -p 7916 -i ~/.ssh/id_ed25519_newtalk root@114.207.244.86`

---

## 1단계: sync 스크립트 수정 (서버)

```bash
cd /data/project-docs/scripts
cp sync_newtalk_v2_api.sh "sync_newtalk_v2_api.sh.bak.$(date +%Y%m%d_%H%M%S)"
# 그 다음: project-docs 저장소에서 git pull 하여 수정된 sync_newtalk_v2_api.sh 반영
cd /data/project-docs && git pull origin master
```

(민감정보 검사: `token` 단독 → `password\s*=`, `secret\s*=`, `api_key\s*=`, `access_token\s*=`, `bearer [a-z0-9]` 패턴으로 변경됨)

---

## 2단계: 서버 docs 업데이트 (v1.2.0)

**2-A** 로컬에서 서버로 문서 복사 (로컬 터미널에서 실행):

```bash
cd /root/project-docs/newtalk-v2-api
scp -P 7916 -i ~/.ssh/id_ed25519_newtalk CONTEXT.md CHANGELOG.md root@114.207.244.86:/tmp/
scp -P 7916 -i ~/.ssh/id_ed25519_newtalk handover/HANDOVER.md root@114.207.244.86:/tmp/
```

**2-B** 서버에서 복사 및 V2 Git 푸시:

```bash
DOCS=/srv/newtalk-v2/docs
cp /tmp/CONTEXT.md "$DOCS/"
cp /tmp/CHANGELOG.md "$DOCS/"
cp /tmp/HANDOVER.md "$DOCS/handover/"

cd /srv/newtalk-v2
git add docs/CONTEXT.md docs/CHANGELOG.md docs/handover/HANDOVER.md
git commit -m "[DOCS] v1.2.0 반영 — CONTEXT, CHANGELOG, HANDOVER 업데이트"
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin feature/R2-FRONT-001-setup
```

---

## 3단계: project-docs 동기화 (서버)

```bash
bash /data/project-docs/scripts/sync_newtalk_v2_api.sh
```

실패 시 수동 동기화:

```bash
cp /srv/newtalk-v2/docs/CONTEXT.md /data/project-docs/newtalk-v2-api/
cp /srv/newtalk-v2/.cursorrules /data/project-docs/newtalk-v2-api/cursorrules.md
cp /srv/newtalk-v2/docs/CHANGELOG.md /data/project-docs/newtalk-v2-api/
cp /srv/newtalk-v2/docs/handover/HANDOVER.md /data/project-docs/newtalk-v2-api/handover/
grep -rIiE "(password\s*=|secret\s*=|api_key\s*=|access_token\s*=)" /data/project-docs/newtalk-v2-api/ || true
cd /data/project-docs && git add -A && git commit -m "[sync] newtalk-v2-api v1.2.0 동기화 — DEPLOY 완료 반영"
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin master
```

---

## 4단계: 검증

```bash
curl -s "https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/CONTEXT.md" | grep "1.2.0"
curl -s "https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/CHANGELOG.md" | grep "1.2.0"
curl -s "https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/handover/HANDOVER.md" | grep "870c007"
```

세 개 모두 결과가 있으면 성공.

---

## 5단계: review 폴더 정리 (서버)

```bash
cd /data/project-docs/newtalk-v2-api/review
rm -f R2-FRONT-001_*.ts R2-FRONT-001_*.php REVIEW_REQUEST.md
ls -la

cd /data/project-docs
git add -A
git commit -m "[review] R2-FRONT-001 검수 완료 — review 폴더 정리"
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin master
```

---

완료 후: **"v1.2.0 동기화 완료. 확인해라."**
