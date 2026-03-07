#!/bin/bash
# CEO Chat 모델 선택 UI를 버튼 → 드롭다운으로 반영 후 대시보드 재빌드·재기동
# 68서버에서 실행: bash /root/project-docs/aads/scripts/deploy_ceo_chat_dropdown.sh
# 전제: /root/aads/aads-dashboard, /root/aads/aads-server 존재, docker compose 사용

set -e
PATCH="/root/project-docs/aads/patches/ModelSelector_ceo_chat_dropdown.tsx"
TARGET="/root/aads/aads-dashboard/src/components/chat/ModelSelector.tsx"
COMPOSE_DIR="/root/aads/aads-server"

if [ ! -f "$PATCH" ]; then
  echo "ERROR: 패치 파일 없음: $PATCH (project-docs 먼저 pull)"
  exit 1
fi
if [ ! -d "$(dirname "$TARGET")" ]; then
  echo "ERROR: 대상 경로 없음: $(dirname "$TARGET")"
  exit 1
fi

cp "$PATCH" "$TARGET"
echo "[OK] $TARGET 반영됨 (드롭다운)"

if [ -d "$COMPOSE_DIR" ]; then
  cd "$COMPOSE_DIR"
  docker compose -f docker-compose.prod.yml build aads-dashboard --no-cache
  docker compose -f docker-compose.prod.yml up -d aads-dashboard
  echo "[OK] aads-dashboard 재기동 완료. https://aads.newtalk.kr/ceo-chat 에서 확인하세요."
else
  echo "WARN: $COMPOSE_DIR 없음. 수동으로 aads-dashboard 빌드·재기동 필요."
fi
