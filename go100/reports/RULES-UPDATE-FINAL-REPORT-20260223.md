# RULES-UPDATE 최종 보고서 (2026-02-23)

## 작업 개요
- **작업명**: RULES-UPDATE
- **목적**: CLAUDE.md와 kis-v41-rules.md를 현행 CONTEXT.md(V1.0, 2026-02-23) 및 실제 DB/규칙과 일치시키기
- **대상 파일**: `/root/kis-autotrade-v4/CLAUDE.md`, `/root/kis-autotrade-v4/.cursor/rules/kis-v41-rules.md`

---

## 사전 확인 결과
| 항목 | 결과 |
|------|------|
| strategy_cards | **62건** |
| v4_positions OPEN | **5건** |
| 디스크 (/) | 54% 사용 (45G 가용) |
| 백업 | `/root/backups/rules_update_20260223/` (CLAUDE.md.bak, kis-v41-rules.md.bak) |

---

## CLAUDE.md 수정 6건

| # | 수정 내용 | 상태 |
|---|-----------|------|
| 1 | strategy_cards 기준값 59 → **62건** (작업 전/후 필수, 컴플라이언스 체크리스트) | 완료 |
| 2 | 컴플라이언스 체크리스트 `strategy_cards 62건` | 완료 |
| 3 | 절대 규칙 4번: "폐기: UPDATE 허용" → "변경: strategy_cards UPDATE는 **CEO 승인 후에만** 허용" | 완료 |
| 4 | strategy_cards 문구: ALTER/DROP/DELETE 금지 **(UPDATE는 CEO 승인 후에만)** | 완료 |
| 5 | STRAT-TUNE: "58→36 live 카드" → "**62개 중** 36 live 카드" | 완료 |
| 6 | 최근 완료 작업 이력 10건 추가 (BT-ENGINE-UPGRADE, REGIME-BACKFILL, DESK-RECOMMEND, DASH-FIX-VERIFY, OVERLAP-GUARD, REGIME-STRATEGY-CROSS, DESK1-DATA-VERIFY, KIS-DOCS-FULL-SETUP, REPORT-PIPELINE-SETUP, CURSOR-RULES-PUBLISH) | 완료 |
| 7 | 알려진 이슈: BT-ENGINE-UPGRADE(16컬럼), REGIME-BACKFILL(59행), OVERLAP-GUARD(CEO 정책 대기) 추가 | 완료 |

---

## kis-v41-rules.md 수정 4건

| # | 수정 내용 | 상태 |
|---|-----------|------|
| 1 | 작업 절차 5번: "systemctl restart kis-webapp-api → health 확인" → "서비스 재시작은 **CEO 승인 후에만** (절대 규칙 3번 준수)" | 완료 |
| 2 | v4_backtest_trades: 2026-02-23 **16개 컬럼** 추가 스키마 설명 (entry_datetime, exit_datetime, entry_price, exit_price, mfe_pct, mae_pct, mfe_price, mae_price, regime_at_entry, indicator_snapshot, slippage_pct, commission, sector, strategy_name, entry_volume, entry_spread_pct) | 완료 |
| 3 | **보고서 배포** 섹션 추가: report/ 저장, publish_report.sh, sync_kis.sh, Public 보고서 보안(API키·계좌번호·비밀번호·토큰 금지) | 완료 |
| 4 | DB명 kisautotrade 확인 (변경 없음) | 확인 |

---

## 컴플라이언스 체크리스트
| 항목 | 결과 |
|------|------|
| .env/.bak 커밋 여부 | 미포함 |
| strategy_cards | 62건 유지 |
| v4_positions OPEN | 5건 (변경 없음) |
| DB 스키마 변경 | 없음 |
| 서비스 재시작 | 없음 (절대 규칙 3번 준수) |
| V4.1 파일 수정 | CLAUDE.md, kis-v41-rules.md 문서만 |

---

## Git / 배포
- **Private (kis-autotrade-v4)**  
  - 커밋: `a1ad56a9` — `rules: CLAUDE.md + kis-v41-rules.md 현행 동기화 — strategy_cards 62건, BT엔진 업그레이드, 보고서 배포 규칙 반영`
- **Public (project-docs)**  
  - sync_kis.sh 실행 후 `git pull --rebase origin master` + `git push origin master` 완료 (커밋 28c0f2e)
  - CLAUDE.md: project-docs `kis-autotrade-v4/rules/CLAUDE.md`에 62건 반영됨
  - kis-v41-rules.md: sync 시 **민감정보 필터**로 Public 미배포 (설계상 SKIP — "비밀번호" 등 문구 포함)

---

## 미수정 — CEO 결정 필요
- **GO100 컨텍스트 분리 여부**  
  - 현재 CLAUDE.md의 50%+ 가 GO100 관련  
  - A: GO100 섹션 전체 제거 (별도 CLAUDE-GO100.md)  
  - B: 현행 유지  

---

## 백업 경로
- `/root/backups/rules_update_20260223/CLAUDE.md.bak`
- `/root/backups/rules_update_20260223/kis-v41-rules.md.bak`

---

*보고서 생성: 2026-02-23 | RULES-UPDATE*
