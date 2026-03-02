#!/bin/bash
# done_watcher.sh v2.0
# RESULT.md 감지 → project-docs 복사 → git push → GitHub URL → chat_messages → 텔레그램 → archived
export TZ="Asia/Seoul"

DONE_DIR="/root/.genspark/directives/done"
ARCHIVED_DIR="/root/.genspark/directives/archived"
CHAT_MSG_DIR="/root/.genspark/directives/chat_messages"
PROJECT_DOCS="/root/project-docs"
LOG="/root/.genspark/logs/done_watcher.log"
SEEN_FILE="/root/.genspark/logs/done_seen.txt"

GH_OWNER="moongoby"
GH_REPO="project-docs"
GH_BRANCH="master"

mkdir -p "$ARCHIVED_DIR" "$CHAT_MSG_DIR" "$(dirname "$LOG")"
touch "$SEEN_FILE"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S KST')] $1" | tee -a "$LOG"; }

# ── 프로젝트 → reports 경로 매핑 ─────────────────────────────────────────
get_reports_dir() {
    case "$1" in
        KIS)   echo "$PROJECT_DOCS/kis-autotrade-v4/reports" ;;
        GO100) echo "$PROJECT_DOCS/go100/reports" ;;
        AADS)  echo "$PROJECT_DOCS/aads/reports" ;;
        SF)    echo "$PROJECT_DOCS/shortflow/reports" ;;
        NAS)   echo "$PROJECT_DOCS/nas-image/reports" ;;
        NTV2)  echo "$PROJECT_DOCS/newtalk-v2-api/reports" ;;
        *)     echo "" ;;
    esac
}

# ── 프로젝트 → GitHub 경로 매핑 ──────────────────────────────────────────
get_gh_path() {
    case "$1" in
        KIS)   echo "kis-autotrade-v4/reports" ;;
        GO100) echo "go100/reports" ;;
        AADS)  echo "aads/reports" ;;
        SF)    echo "shortflow/reports" ;;
        NAS)   echo "nas-image/reports" ;;
        NTV2)  echo "newtalk-v2-api/reports" ;;
        *)     echo "" ;;
    esac
}

# ── 텔레그램 직접 발송 (GitHub URL 포함) ──────────────────────────────────
send_telegram() {
    local text="$1"
    source /root/.genspark/.env 2>/dev/null
    source /root/kis-autotrade-v4/.env 2>/dev/null
    local TOKEN="${TELEGRAM_BOT_TOKEN:-$GO100_TELEGRAM_BOT_TOKEN}"
    local CHAT_ID="${TELEGRAM_CHAT_ID:-$GO100_TELEGRAM_CHAT_ID}"
    [ -z "$TOKEN" ] || [ -z "$CHAT_ID" ] && { log "[WARN] 텔레그램 토큰 없음"; return 1; }
    # 4096자 제한
    text="${text:0:4000}"
    curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
        -d chat_id="$CHAT_ID" \
        --data-urlencode "text=$text" \
        -d parse_mode="Markdown" > /dev/null 2>&1
}

log "done_watcher v2.0 시작"

while true; do
    for file in "$DONE_DIR"/*_RESULT.md; do
        [ -f "$file" ] || continue
        fname=$(basename "$file")

        # 중복 처리 방지
        grep -qF "$fname" "$SEEN_FILE" && continue
        log "▶ 새 완료 파일 감지: $fname"

        # ── 1) 프로젝트명 추출 (파일명 첫 '_' 앞 단어) ──────────────────
        PROJECT=$(echo "$fname" | cut -d'_' -f1)
        TASK_ID=$(echo "$fname" | sed 's/_RESULT\.md$//')
        COMPLETED_AT=$(date '+%Y-%m-%d %H:%M')
        log "  프로젝트: $PROJECT | 태스크: $TASK_ID"

        # ── 2) reports 폴더로 복사 ────────────────────────────────────────
        REPORTS_DIR=$(get_reports_dir "$PROJECT")
        GH_PATH=$(get_gh_path "$PROJECT")
        GH_URL=""

        if [ -n "$REPORTS_DIR" ] && [ -n "$GH_PATH" ]; then
            mkdir -p "$REPORTS_DIR"
            cp "$file" "$REPORTS_DIR/$fname"
            log "  reports 복사: $REPORTS_DIR/$fname"

            # ── 3) git add + commit + push ────────────────────────────────
            cd "$PROJECT_DOCS" || { log "[ERROR] project-docs 디렉토리 없음"; continue; }
            # git author 보장 (root 환경에서 auto-detect 실패 방지)
            git config user.name "Cursor AutoBot" 2>/dev/null
            git config user.email "cursor@kis-autotrade.local" 2>/dev/null
            git add . >> "$LOG" 2>&1
            git commit -m "[DONE] $fname — 자동 완료 보고서" >> "$LOG" 2>&1 && \
            git push >> "$LOG" 2>&1 && \
            log "  git push 완료" || log "  [WARN] git push 실패 — 수동 push 필요"

            # ── 4) GitHub raw URL 생성 ────────────────────────────────────
            GH_URL="https://raw.githubusercontent.com/${GH_OWNER}/${GH_REPO}/${GH_BRANCH}/${GH_PATH}/${fname}"
            log "  GitHub URL: $GH_URL"
        else
            log "  [WARN] 프로젝트 '$PROJECT' 매핑 없음 — reports 복사 스킵"
        fi

        # ── 5) 매니저 대화창 메시지 파일 생성 ────────────────────────────
        SUMMARY=$(head -20 "$file" | sed 's/```//g')
        MSG_FILE="$CHAT_MSG_DIR/${PROJECT}_$(date '+%Y%m%d_%H%M%S').txt"

        cat > "$MSG_FILE" << CHATEOF
✅ 작업 완료: ${TASK_ID}
프로젝트: ${PROJECT}
완료 시각: ${COMPLETED_AT} KST

📄 결과 보고서:
${GH_URL:-"(GitHub push 미완료 — 로컬: $REPORTS_DIR/$fname)"}

요약:
${SUMMARY}
CHATEOF
        log "  chat_messages 파일 생성: $(basename "$MSG_FILE")"

        # ── 6) 텔레그램 발송 (GitHub URL 포함) ───────────────────────────
        TG_MSG="✅ *작업 완료 보고*
━━━━━━━━━━━━━━━━━━━━
📅 ${COMPLETED_AT} KST
📁 프로젝트: ${PROJECT}
📄 ${fname}
━━━━━━━━━━━━━━━━━━━━
🔗 GitHub: ${GH_URL:-없음}
━━━━━━━━━━━━━━━━━━━━
${SUMMARY}"
        send_telegram "$TG_MSG" && log "  텔레그램 발송 완료" || log "  [WARN] 텔레그램 발송 실패"

        # ── 7) archived/ 이동 ─────────────────────────────────────────────
        MONTH=$(date '+%Y%m')
        mkdir -p "$ARCHIVED_DIR/$MONTH"
        mv "$file" "$ARCHIVED_DIR/$MONTH/$fname"
        echo "$fname" >> "$SEEN_FILE"
        log "  archived 이동 완료 → $ARCHIVED_DIR/$MONTH/$fname"
        log "▶ 처리 완료: $fname"
    done

    sleep 10
done
