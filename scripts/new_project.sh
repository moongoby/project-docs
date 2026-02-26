#!/bin/bash
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "사용법: bash scripts/new_project.sh [폴더명] [프로젝트 설명]"
  echo "예시: bash scripts/new_project.sh my-app '내 앱 프로젝트'"
  exit 1
fi

FOLDER=$1
DESC=$2
BASE="/data/project-docs"

echo "=== ${FOLDER} 프로젝트 문서 구조 생성 ==="

mkdir -p ${BASE}/${FOLDER}/handover
mkdir -p ${BASE}/${FOLDER}/reports

cp ${BASE}/common/CONTEXT_TEMPLATE.md ${BASE}/${FOLDER}/CONTEXT.md
cp ${BASE}/common/CURSORRULES_TEMPLATE.md ${BASE}/${FOLDER}/cursorrules.md
cp ${BASE}/common/HANDOVER_TEMPLATE.md ${BASE}/${FOLDER}/handover/
cp ${BASE}/common/REPORT_TEMPLATE.md ${BASE}/${FOLDER}/reports/

echo "=== README.md에 행 추가 ==="
echo "| ${FOLDER} | ${DESC} | (서버미정) | [CONTEXT](./${FOLDER}/CONTEXT.md) | Rules |" >> ${BASE}/README.md

echo "=== Git 커밋 & push ==="
cd ${BASE}
git add -A
git commit -m "[init] ${FOLDER} 프로젝트 문서 구조 생성" || true
git push origin master || true

echo ""
echo "✅ 완료!"
echo "CONTEXT URL: https://raw.githubusercontent.com/moongoby/project-docs/master/${FOLDER}/CONTEXT.md"
echo "Rules URL: https://raw.githubusercontent.com/moongoby/project-docs/master/${FOLDER}/cursorrules.md"
echo ""
echo "다음 단계: CONTEXT.md와 cursorrules.md 내용을 프로젝트에 맞게 수정하세요."
