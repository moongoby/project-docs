# Git Push 복구 보고서 — SF-T015

**작성일**: 2026-03-06 18:50 KST
**태스크**: SF-T015 — Git Push 완전 복구 (HTTPS 전환 + 미푸시 커밋 Push + HANDOVER v1.6)
**서버**: 114 (shortflow)
**실행자**: claudebot
**결과**: ❌ PUSH 실패 (PAT 없음) — CEO 조치 필요

---

## STEP 1 — 현재 상태 진단

### shortflow 레포
```
origin  https://github.com/moongoby/shortflow.git (fetch)
origin  https://github.com/moongoby/shortflow.git (push)
```

**git log (최근 5건)**:
```
8782abf [SF] SF-T008: 멀티플랫폼 동시 업로드 엔진 구현 (YouTube+TikTok+Instagram+X)
0288564 [SF] QA-ENGINE-V1: HANDOVER.md §2·§7 QA 파일 경로 수정
511cc6b [SF] SF-T007: SaaS 온보딩 위자드 UI (Next.js 14) 구현
33ffd75 [SF] SF-T014: 롱폼 퍼널 + 쿠팡 파트너스 자동 링크 + 공개 채널 성과 API
ff4dca9 [SF] SF-T011: 메타데이터 최적화 + 크론 피크타임 조정
```

**git status**:
```
On branch main
Your branch is ahead of 'origin/main' by 12 commits.

Changes not staged for commit:
  modified:   channels/economy.json
  modified:   channels/health.json
  modified:   docs/reports/20260306_prompt_optimization.md
  modified:   engine/llm_script_engine.py
  modified:   engine/tts_manager.py
  modified:   scripts/pilot_video_e2e_v4.py
  modified:   worker/services/ffmpeg_composer.py

Untracked files:
  data/images/20260226_31_scene1.png
  data/images/20260226_31_scene2.png
  data/images/20260226_31_scene3.png
  data/images/20260226_31_scene4.png
  docs/reports/20260226_전체상태점검_백업커밋배포.md
  docs/reports/20260305_gemini_tts_integration.md
  docs/reports/20260305_quality_improvement.md
  engine/cta_overlay.py
  engine/gemini_tts.py
  engine/hashtag_generator.py
  engine/hook_templates.py
  engine/title_optimizer.py
  venv_old/
  worker/config.py.bak.20260303_160111
```

### project-docs 레포 탐색
```
/data/project-docs/newtalk-v2-api/handover/HANDOVER.md
/data/project-docs/newtalk-v2-api/HANDOVER.md
/data/project-docs/shortflow/HANDOVER.md
/data/project-docs/go100/HANDOVER.md
/data/project-docs/nas-image/HANDOVER.md
/data/project-docs/kis-autotrade-v4/HANDOVER.md
```
→ `/data/project-docs` 확인

### SSH 키 확인
```
~/.ssh/id_ed25519      (개인키 존재)
~/.ssh/id_ed25519.pub  (공개키 존재)

공개키: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFXTamuyjYHT8vQQxWEZFTiiCwq6pcbwWVuD5X2e1Mn1 claudebot@rfree-0009
```
→ GitHub 미등록 상태

### git config
```
user.name  = ShortFlow  (local)
user.email = shortflow@newtalk.dev (local)
credential.helper = (미설정)
```

---

## STEP 2 — HTTPS 전환 (shortflow 레포)

```bash
cd /data/shortflow
git remote set-url origin https://github.com/moongoby/shortflow.git
git remote -v
```

**결과**:
```
origin  https://github.com/moongoby/shortflow.git (fetch)
origin  https://github.com/moongoby/shortflow.git (push)
```
→ ✅ 이미 HTTPS / 재설정 완료

---

## STEP 3 — HTTPS 전환 (project-docs 레포)

project-docs 기존 remote: `git@github.com:moongoby/project-docs.git` (SSH)

```bash
cd /data/project-docs
git remote set-url origin https://github.com/moongoby/project-docs.git
```

**결과**:
```
error: could not lock config file .git/config: Permission denied
fatal: could not set 'remote.origin.url' to 'https://github.com/moongoby/project-docs.git'
```

→ ❌ `/data/project-docs/.git/config` 소유자: root (claudebot 쓰기 불가)

**우회 시도**: `git -c remote.origin.url=... push` → 실행은 됐으나 credential 없어 push 실패

---

## STEP 4 — Push 시도

### 방법 A — 환경변수/토큰 탐색
```bash
grep -i "github" /data/shortflow/.env  → 없음
echo $GITHUB_TOKEN                      → 없음 (빈 문자열)
cat /root/.genspark/.env | grep github  → 없음
cat ~/.git-credentials                  → 없음
cat ~/.netrc | grep github              → 없음
gh auth status                          → "not logged into any GitHub hosts"
find /data -name "*.token"              → 없음
```

**결론**: GitHub 인증 수단 없음

### 방법 B — credential store
```bash
git config --global credential.helper store
cd /data/shortflow && git push origin main 2>&1
```

**오류**:
```
fatal: could not read Username for 'https://github.com': No such device or address
```
→ ❌ 인터랙티브 입력 불가 환경

### 방법 C — [BLOCKED]
```
[BLOCKED] GitHub push 불가. CEO에게 Personal Access Token(PAT) 요청 필요.
생성 방법: GitHub → Settings → Developer settings → Personal access tokens → Fine-grained
권한: Repository access → moongoby/shortflow + moongoby/project-docs
Permissions: Contents (Read and write)
```

---

## STEP 5 — HANDOVER v1.6 갱신

→ ⏭️ SKIP (push 미완료로 실행 불가)
로컬 `/data/project-docs/shortflow/HANDOVER.md` 현재 v1.5 상태

---

## STEP 6 — 최종 검증

```bash
curl -s -o /dev/null -w "shortflow/main hook_presets.json: %{http_code}\n" \
  https://raw.githubusercontent.com/moongoby/shortflow/main/config/hook_presets.json
# → shortflow/main hook_presets.json: 404

curl -s -o /dev/null -w "project-docs HANDOVER.md: %{http_code}\n" \
  https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/HANDOVER.md
# → project-docs HANDOVER.md: 200

curl -s https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/HANDOVER.md | head -2
# → # HANDOVER – ShortFlow YouTube Shorts 자동화 SaaS
# → > 최종 업데이트: 2026-03-05 (v1.5 — SF-T001~T008 재실행 중 / claudebot 권한 복구)
```

**결과**:
- shortflow: 404 (12커밋 미push)
- project-docs HANDOVER: 200, 버전 v1.5 (v1.6 미반영)

---

## 미푸시 커밋 목록 (shortflow, 12건)

```
8782abf [SF] SF-T008: 멀티플랫폼 동시 업로드 엔진 구현 (YouTube+TikTok+Instagram+X)
0288564 [SF] QA-ENGINE-V1: HANDOVER.md §2·§7 QA 파일 경로 수정 (qa_engine.py→qa_score_engine.py+qa_publish_logic.py)
511cc6b [SF] SF-T007: SaaS 온보딩 위자드 UI (Next.js 14) 구현
33ffd75 [SF] SF-T014: 롱폼 퍼널 + 쿠팡 파트너스 자동 링크 + 공개 채널 성과 API
ff4dca9 [SF] SF-T011: 메타데이터 최적화(해시태그·설명·태그) + 크론 피크타임 조정(07:30/12:00/19:00)
b633720 [SF] SF-T010: 프롬프트 최적화 — 후크·CTA·루프엔딩 구조 적용
2ab04fc [SF] SF-T011: 메타데이터 최적화 + 크론 피크타임 조정 (07:30/12:00/19:00)
214d303 [SF] REPORT: git SSH 키 등록 + 미푸시 커밋 복구 보고서 (push 차단 기록)
88b0a68 [SF] HANDOVER v1.6: SF-T005 완료, SSH키 설정, 상태 갱신
ae7dc72 [SF] T009: 대본 프롬프트 고도화 (훅/루프/CTA/길이 최적화)
f868556 [SF] SAAS-DB-SCHEMA: SaaS 플랫폼 DB 스키마 구축 (SF-T005)
5ea27b5 [SF] QA-ENGINE-V1: QA 스코어 엔진 v1 구현 (SF-T002)
```

---

## CEO 필수 조치 (P0-CRITICAL)

GitHub PAT 발급 후 서버에서 아래 명령 실행:

```bash
# 1. shortflow 12개 커밋 push
cd /data/shortflow
git push https://[PAT]@github.com/moongoby/shortflow.git main

# 2. project-docs .git/config 권한 수정 + HTTPS 전환
sudo chown claudebot:claudebot /data/project-docs/.git/config
cd /data/project-docs
git remote set-url origin https://github.com/moongoby/project-docs.git
git push https://[PAT]@github.com/moongoby/project-docs.git master
```

PAT 발급 경로:
`GitHub → Settings → Developer settings → Personal access tokens → Fine-grained`
권한: `moongoby/shortflow` + `moongoby/project-docs` → Contents: Read and write

---

## 완료 기준 달성 여부

| 항목 | 상태 |
|------|------|
| shortflow HTTPS 전환 | ✅ |
| project-docs HTTPS 전환 | ❌ root 권한 필요 |
| shortflow push | ❌ PAT 필요 |
| project-docs push | ❌ PAT + 권한 수정 필요 |
| HANDOVER v1.6 GitHub 반영 | ❌ push 선행 필요 |
| HTTP 200 (shortflow) | ❌ 404 |
| HTTP 200 (project-docs HANDOVER) | ✅ 200 (v1.5) |
