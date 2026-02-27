# GO100 프로젝트 컨텍스트 (Claude PM용)
> 최종 갱신: 2026-02-28  
> 인계서: HANDOVER-20260228-V7.md

## 1. 프로젝트 개요
- **GO100 (백억이)**: 증권사급 AI 투자 에이전트 (조건검색 + 자동매매 + 자율 전략 진화)
- **코드**: /root/kis-autotrade-v4 (모노리포, V4.1과 경계 분리)
- **문서**: /root/project-docs → github.com/moongoby/project-docs (public)
- **도메인**: go100.newtalk.kr
- **스택**: FastAPI(8002), Next.js(3000), PostgreSQL(16), Redis, Nginx

## 2. 서버 환경
- 프로젝트: /root/kis-autotrade-v4
- 브랜치: phase-2c-command-center
- DB: kisautotrade / kis_admin / localhost:5432
- PYTHONPATH: /root/kis-autotrade-v4/backend
- 가상환경: source /root/kis-autotrade-v4/venv/bin/activate

## 3. 작업 큐 (v7 기준)
| 순위 | 작업 | 상태 |
|------|------|------|
| P0 | Agent Mode 활성화, 크론 검증, 무결성 모니터 | ✅ 완료 |
| P1 | E2E 풀테스트, Cron 이슈, 시드 백테스트, Freshness 경고 | ✅ 완료 |
| P2 | 세션/에피소드 메모리, 경험 DB, 시그널 성과, 모닝 브리핑 | 🔧 진행 중 |
| P3 | 전략 진화 엔진, 호가창 백테스트, 이벤트 엔진 | 예정 |
| P4 | 갭 캘리브레이터, 30일 모의투자 | 예정 |
| P5 | 자기리뷰, 포트폴리오 최적화, 실투자 | 예정 |

## 4. 서비스 현황
| 서비스 | 포트 | 상태 |
|--------|------|------|
| go100 (FastAPI) | 8002 | active (nginx) |
| Next.js (GO100) | 3000 | active |
| Redis | 6379 | active |
| PostgreSQL | 5432 | active |

## 5. 진행률
- **전체**: 38% (천재 100% 기준)
- P1 완료 반영: Agent E2E 21/21, Cron Known Issue 3건 해결, 시드 백테스트, Freshness 경고

## 6. 필수 읽기 (세션 시작 시)
1. /root/kis-autotrade-v4/.cursorrules
2. /root/kis-autotrade-v4/CLAUDE.md
3. go100/HANDOVER-20260228-V7.md
4. go100/ARCHITECTURE.md, DB_SCHEMA.md

## 7. 규칙 요약
- 커밋 prefix: [GO100], [V4.1], [SHARED]
- GO100 작업 시 V4.1 파일 수정 금지
- 보고서 저장: /root/project-docs/go100/reports/ → git push
