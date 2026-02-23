#!/bin/bash
# 서버(114)에서 실행: project-docs 동기화 보정 + v1.2.0 반영
# 사용법: scp 이 스크립트와 수정된 docs를 서버로 복사 후, 서버에서 bash run_v120_sync_on_server.sh
# 또는: 서버에 SSH 접속 후 1~5단계를 순서대로 수동 실행

set -e
export GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no"

echo "=== 1단계: sync 스크립트 백업 및 적용 ==="
cd /data/project-docs/scripts
cp -a sync_newtalk_v2_api.sh "sync_newtalk_v2_api.sh.bak.$(date +%Y%m%d_%H%M%S)"
# (수정된 sync 스크립트는 로컬 project-docs에서 pull 또는 수동 복사 필요)
echo "백업 완료. sync_newtalk_v2_api.sh 내용을 민감정보 검사 패턴 반영 버전으로 교체한 뒤 2단계 진행."

echo ""
echo "=== 2단계: 서버 docs 업데이트 (v1.2.0) ==="
DOCS="/srv/newtalk-v2/docs"
# CONTEXT.md, CHANGELOG.md, handover/HANDOVER.md 는 로컬 project-docs/newtalk-v2-api/ 에서
# 서버 /srv/newtalk-v2/docs/ 로 복사해야 함. 예:
#   scp CONTEXT.md CHANGELOG.md root@114.207.244.86:/tmp/
#   scp handover/HANDOVER.md root@114.207.244.86:/tmp/
#   ssh ... "cp /tmp/CONTEXT.md /srv/newtalk-v2/docs/ && cp /tmp/CHANGELOG.md /srv/newtalk-v2/docs/ && cp /tmp/HANDOVER.md /srv/newtalk-v2/docs/handover/"
if [ -f /tmp/CONTEXT.md ]; then cp /tmp/CONTEXT.md "$DOCS/"; fi
if [ -f /tmp/CHANGELOG.md ]; then cp /tmp/CHANGELOG.md "$DOCS/"; fi
if [ -f /tmp/HANDOVER.md ]; then mkdir -p "$DOCS/handover" && cp /tmp/HANDOVER.md "$DOCS/handover/"; fi

cd /srv/newtalk-v2
git add docs/CONTEXT.md docs/CHANGELOG.md docs/handover/HANDOVER.md
if ! git diff --cached --quiet; then
  git commit -m "[DOCS] v1.2.0 반영 — CONTEXT, CHANGELOG, HANDOVER 업데이트"
  $GIT_SSH_COMMAND git push origin feature/R2-FRONT-001-setup
  echo "✅ newtalk-v2 푸시 완료"
fi

echo ""
echo "=== 3단계: project-docs 동기화 ==="
bash /data/project-docs/scripts/sync_newtalk_v2_api.sh

echo ""
echo "=== 4단계: 검증 ==="
curl -sf "https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/CONTEXT.md" | grep -q "1.2.0" && echo "✅ CONTEXT 1.2.0 OK" || echo "❌ CONTEXT 실패"
curl -sf "https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/CHANGELOG.md" | grep -q "1.2.0" && echo "✅ CHANGELOG 1.2.0 OK" || echo "❌ CHANGELOG 실패"
curl -sf "https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/handover/HANDOVER.md" | grep -q "870c007" && echo "✅ HANDOVER 870c007 OK" || echo "❌ HANDOVER 실패"

echo ""
echo "=== 5단계: review 폴더 정리 ==="
cd /data/project-docs/newtalk-v2-api/review
rm -f R2-FRONT-001_*.ts R2-FRONT-001_*.php REVIEW_REQUEST.md
ls -la

cd /data/project-docs
git add -A
if ! git diff --cached --quiet; then
  git commit -m "[review] R2-FRONT-001 검수 완료 — review 폴더 정리"
  $GIT_SSH_COMMAND git push origin master
  echo "✅ project-docs 푸시 완료"
fi

echo ""
echo "v1.2.0 동기화 완료. 확인해라."
