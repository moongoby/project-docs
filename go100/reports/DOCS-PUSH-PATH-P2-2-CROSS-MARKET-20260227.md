# 푸시 후 브라우저 확인 경로 (P2-2 Cross-Market 반영)

**일시:** 2026-02-27  
**대상:** 코드 레포(go100), 문서 레포(project-docs) 푸시 완료 — 브라우저에서 확인할 경로 정리

---

## 1. 코드 레포 (kis-autotrade-v4 → go100)

| 항목 | 브라우저 경로 |
|------|----------------|
| 리포지토리 | https://github.com/moongoby/go100 |
| 브랜치 (현재) | https://github.com/moongoby/go100/tree/phase-2c-command-center |
| P2-2 마이그레이션 | https://github.com/moongoby/go100/blob/phase-2c-command-center/backend/migrations/034_go100_cross_market_signals.sql |
| P2-2 수집 스크립트 | https://github.com/moongoby/go100/blob/phase-2c-command-center/scripts/go100/collect_cross_market_signals.py |
| P2-2 실행 스크립트 | https://github.com/moongoby/go100/blob/phase-2c-command-center/scripts/go100/run_cross_market_signals.sh |
| 도구 연동 (tool_executors) | https://github.com/moongoby/go100/blob/phase-2c-command-center/backend/app/services/go100/ai/tool_executors.py |
| 도구 정의 (agent_tools) | https://github.com/moongoby/go100/blob/phase-2c-command-center/backend/app/services/go100/ai/agent_tools.py |

- **푸시 상태:** `origin/phase-2c-command-center` 기준 최신 반영됨 (Everything up-to-date).

---

## 2. 문서 레포 (project-docs)

| 항목 | 브라우저 경로 |
|------|----------------|
| 리포지토리 | https://github.com/moongoby/project-docs |
| master 브랜치 | https://github.com/moongoby/project-docs/tree/master |
| P2-2 보고서 | https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-P2-2-CROSS-MARKET-SIGNALS-20260227.md |
| GO100 보고서 목록 | https://github.com/moongoby/project-docs/tree/master/go100/reports |

- **푸시 상태:** master 기준 working tree clean.

---

## 3. 요약

- **코드 레포:** `phase-2c-command-center` 브랜치에 P2-2 Cross-Market Signal 수집기(테이블, 수집/실행 스크립트, get_cross_market_signals 연동) 반영 후 푸시 완료. 위 URL로 브라우저에서 바로 확인 가능.
- **문서 레포:** `CUR-GO100-P2-2-CROSS-MARKET-SIGNALS-20260227.md` 포함하여 푸시 완료. 위 보고서 링크로 내용 확인 가능.
