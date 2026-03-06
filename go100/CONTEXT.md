# GO100 프로젝트 컨텍스트 (Claude PM용)
> 최종 갱신: 2026-03-06 (T-038 HANDOVER v15.3 반영 — Commander 대시보드 + 페이지 45개)
> 인계서: HANDOVER.md v15.3

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
- **환경**: DART API 발급·설정 완료 (.env DART_API_KEY/OPENDART_API_KEY). Telegram 설정 완료 (GO100_TELEGRAM_BOT_TOKEN, GO100_TELEGRAM_CHAT_ID). 모닝 브리핑 자동 발송 가능.

## 3. 작업 큐 (v15.3 기준, 2026-03-06)
| 순위 | 작업 | 상태 |
|------|------|------|
| P0 | Agent Mode 활성화, 크론 검증, 무결성 모니터 | ✅ 완료 |
| P1 | E2E 풀테스트, Cron 이슈, 시드 백테스트, Freshness 경고 | ✅ 완료 |
| P2 | 세션/에피소드 메모리, 경험 DB, 모닝 브리핑 (Telegram 설정 완료) | ✅ 완료 |
| P3 | 전략 진화·호가창 백테스트·이벤트 엔진·전략 편집(P3-R1)·지표 20개(P3-R2) | ✅ 완료 |
| P4 | 갭 캘리브레이터(P4-2), 메모리(P4-1), 30일 모의투자(P4-3), AI Feature V3 | ✅ 완료 |
| P5 | 자기리뷰(P5-1), Telegram+섹터(P5-2), 포트폴리오 최적화(P5-3), 개인화(P5-4) | ✅ 완료 |
| P6 | 리스크+킬스위치(P6-1), KIS API 실주문 게이트웨이(P6-2) | ✅ 완료 |
| P7 | P7-1 QA 완료, SaaS 버그수정(T-028), SEO(T-029/T-020), 에러모니터링(T-031) | ✅ 완료 |
| P8 | entry_rules 포맷 수정(T-033), 모의투자 거래 발생 확인(T-034 재실행) | 🔥 즉시 필요 |
| P9 | 30일 모의투자 1사이클 완주 (session_id=2, ~03-29) | 🔧 진행 중 |
| P10 | V3 모델 CEO 승인 후 실전 투입 | ⏳ CEO 대기 |
| SaaS | 결제(T-021), 마켓플레이스, 최종 QA, 라이브 런칭 | 📋 설계 완료 |

## 4. 서비스 현황
| 서비스 | 포트 | 상태 |
|--------|------|------|
| go100 (FastAPI) | 8002 | active (nginx) |
| Next.js (GO100) | 3000 | active |
| Redis | 6379 | active |
| PostgreSQL | 5432 | active |

## 5. 진행률
- **전체**: 98%+ (천재 100% 기준)
- E2E 23/23 PASS, Agent Tool **57개**, Screening Filters 35+, Gap 데이터 108,574건
- DB 마이그레이션 035~065 (064 v4_users terms, 065 go100_error_log)
- **페이지**: 45개 전수 LIVE (T-029에서 34→44, T-036/T-037 Commander 대시보드 추가로 45 확인)
- **크론**: 활성 약 60라인 (closing_report cron 포함 — T-030 완료)
- **SaaS**: 회원가입(T-028 완료), SEO(T-020/T-029 완료), 에러모니터링(T-031 완료)
- **토글UI**: accounts·settings 실매매/모의 토글 연동 완료(T-157, 커밋 fc398d2d)
- **Commander 대시보드**: go100.newtalk.kr/go100/commander (T-036/T-037 완료)
- **⚠️ 잔여이슈**: entry_rules 포맷 불일치 (card_id=35,36) — T-033 수정 필요

## 6. 필수 읽기 (세션 시작 시)
1. /root/kis-autotrade-v4/.cursorrules
2. /root/kis-autotrade-v4/CLAUDE.md
3. go100/HANDOVER.md v15.3
4. go100/ARCHITECTURE.md, DB_SCHEMA.md

## 7. 규칙 요약
- 커밋 prefix: [GO100], [V4.1], [SHARED]
- GO100 작업 시 V4.1 파일 수정 금지
- 보고서 저장: /root/project-docs/go100/reports/ → git push

## 8. 지시서 작성규칙

```
[지시서 예시 형식]
Task ID: T-NNN
제목: (한글 제목)
서버: 211 (go100)
우선순위: P0-CRITICAL / P1-HIGH / P2-NORMAL
예상 시간: N분
예상 비용: $0
의존성: (없음 또는 선행 Task ID)

(작업 내용 상세 기술)
[예시 끝]
```

- 타임스탬프: KST 기준 (UTC 금지)
- 작업 완료 후 HANDOVER.md 반드시 갱신
- git commit + push 필수
