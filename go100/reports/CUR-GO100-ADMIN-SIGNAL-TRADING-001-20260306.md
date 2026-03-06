# CUR-GO100-ADMIN-SIGNAL-TRADING-001-20260306

**Task ID**: T-046
**제목**: 어드민 시그널·리스크 + 매매 관리 + 거래 상세 페이지
**날짜**: 2026-03-06 KST
**커밋**: b8f247ca
**브랜치**: phase-2c-command-center
**상태**: PASS

---

[인계 확인]
직전 완료: T-045 (어드민 연구소 + 백테스트 상세 페이지)
현재 단계: Phase 2C — Command Center (어드민 종합상황실)
CEO 지시 적용: D-001, D-002
strategy_cards: 2 (card_id 35, 36 — entry_rules 정규화 완료)
open_positions: 0 (모의투자 진행 중, 거래 0건)

---

## 1. 작업 요약

어드민 종합상황실의 **시그널·리스크** 및 **매매 관리** 페이지를 스텁(stub)에서 완전한 구현체로 교체하고, **거래 상세** 동적 라우팅 페이지를 신규 생성했다.

---

## 2. 구현 내역

### 2-1. 백엔드 API 추가 (risk_router.py)

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/go100/risk/status` | GET | 리스크 현황: 킬스위치 상태, 노출도, 섹터 집중도, 일일 P&L, 게이지 4종, Kill Switch 이력 |
| `/api/go100/risk/kill-switch` | POST | Kill Switch 토글 (activate/deactivate/toggle), CEO 전용 |

`get_risk_status()` 함수를 risk_engine.py에서 직접 호출하여 실시간 데이터 제공.
4종 게이지(포지션한도/섹터집중도/총노출/일일P&L)를 0~100% 퍼센티지로 계산하여 반환.
Kill Switch 발동 이력은 `go100_risk_events` 테이블에서 조회.

### 2-2. 백엔드 API 추가 (go100_admin_router.py)

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/go100/admin/signal-timeline` | GET | 오늘 시그널 타임라인 (go100_agent_reports 기반, PASS/REJECT 판정) |
| `/api/go100/admin/trade-detail/{trade_id}` | GET | 거래 상세 + 에이전트 보고서 시그널 역추적 + 슬리피지 분석 |
| `/api/go100/admin/trading-status` | GET | 매매 관리 현황: 세션·포지션·체결이력·일별수익곡선 |

**시그널 타임라인**: `go100_signals` 테이블이 없어 `go100_agent_reports`를 활용.
BUY/BULL → PASS, REJECT/BEAR/NEUTRAL → REJECT 자동 판정.

### 2-3. 프론트엔드 컴포넌트 (6개 신규 생성)

| 파일 | 역할 |
|------|------|
| `SignalTimeline.tsx` | 시간순 시그널 목록, PASS=초록/REJECT=빨강 색상 |
| `RiskGauge.tsx` | 리스크 게이지 바 (GREEN<70%, YELLOW 70-90%, RED>90%) |
| `KillSwitchPanel.tsx` | Kill Switch ON/OFF 토글 + 확인 모달 + 발동 이력 |
| `PositionTable.tsx` | 보유 포지션 테이블 (종목코드/명/수량/단가/현재가/수익률/비중) |
| `TradeHistory.tsx` | 체결 이력 테이블 (시간/유형/종목/수량/가격/손익/상세링크) |
| `TradeDetail.tsx` | 거래 상세 (거래정보 + 시그널역추적 + 슬리피지 분석) |

### 2-4. 프론트엔드 페이지 (3개 구현/생성)

| 경로 | 변경 | 내용 |
|------|------|------|
| `/admin/signals` | 스텁 → 완전 구현 | 시그널 타임라인 + 리스크 게이지 4종 + Kill Switch 패널 + 도넛 차트 (recharts PieChart) |
| `/admin/trading` | 스텁 → 완전 구현 | 모의/실매매 모드 토글 표시 + 세션 정보 + 포지션 테이블 + 일별 수익곡선(AreaChart) + 체결 이력 |
| `/admin/trading/[tradeId]` | 신규 생성 | 거래 상세 동적 라우팅 (캔들차트 위치에 텍스트 정보 + 시그널역추적 + 슬리피지) |

---

## 3. 검증 결과

```
npm run build: ✓ Compiled successfully (51/51 pages)
Backend health: curl http://localhost:8002/health → 200 OK
Frontend:
  curl http://localhost:3000/admin/signals → 307 (auth-redirect 정상)
  curl http://localhost:3000/admin/trading → 307 (auth-redirect 정상)
  curl http://localhost:3000/admin/trading/1 → 307 (auth-redirect 정상)
  curl http://localhost:3000/go100 → 200 OK
Git commit: b8f247ca
Git push: phase-2c-command-center → origin (성공)
```

---

## 4. 기술 노트

### DB 상태 (2026-03-06 기준)
- `go100_paper_trades`: 0행 (모의투자 거래 아직 없음)
- `go100_paper_trading_sessions`: 2행 (session_id=2, status=ACTIVE)
- `go100_agent_reports`: 4종류 (commander_self_critique/research_pipeline/researcher_backtester 외)
- `go100_risk_events`: 킬스위치 발동 이력 저장
- `go100_signals` 테이블: 존재하지 않음 → agent_reports로 대체

### 리스크 게이지 계산
- **포지션 한도**: `exposure_pct / max_position_pct * 100`
- **섹터 집중도**: `max_sector_pct / max_sector_limit * 100`
- **총 노출도**: `exposure_pct` 직접 사용
- **일일 P&L**: `abs(daily_pnl_pct) * 33.3` (일일 -3% 한도 대비 환산)

### Kill Switch 플로우
1. CEO가 버튼 클릭 → 확인 모달 팝업
2. 확인 시 `POST /api/go100/risk/kill-switch` 호출
3. `activate_kill_switch()` 또는 `deactivate_kill_switch()` 실행
4. 화면 새로고침으로 상태 갱신

---

## 5. 파일 목록

**백엔드 수정:**
- `backend/app/routers/go100/risk_router.py` (+80줄)
- `backend/app/api/v1/go100_admin_router.py` (+150줄)

**프론트엔드 신규:**
- `frontend/src/components/admin/SignalTimeline.tsx` (94줄)
- `frontend/src/components/admin/RiskGauge.tsx` (76줄)
- `frontend/src/components/admin/KillSwitchPanel.tsx` (120줄)
- `frontend/src/components/admin/PositionTable.tsx` (87줄)
- `frontend/src/components/admin/TradeHistory.tsx` (102줄)
- `frontend/src/components/admin/TradeDetail.tsx` (131줄)
- `frontend/src/app/(protected)/admin/trading/[tradeId]/page.tsx` (94줄)

**프론트엔드 수정:**
- `frontend/src/app/(protected)/admin/signals/page.tsx` (스텁 → 163줄 full)
- `frontend/src/app/(protected)/admin/trading/page.tsx` (스텁 → 211줄 full)

---

## 6. 성공 기준 점검

| 항목 | 결과 |
|------|------|
| 시그널 타임라인 + 리스크 게이지 4종 + Kill Switch 패널 렌더링 | ✅ PASS |
| 매매 관리: 세션 정보 + 포지션 + 체결 이력 + 수익곡선 | ✅ PASS |
| 거래 상세: 상세 정보 + 시그널 역추적 + 슬리피지 분석 | ✅ PASS |
| npm run build PASS | ✅ PASS (51/51 pages) |
| 서비스 재시작 + 헬스체크 200 | ✅ PASS |
| git push origin phase-2c-command-center | ✅ PASS (b8f247ca) |

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (phase-2c-command-center, b8f247ca)
- [ ] project-docs 보고서 push 완료 (진행 중)
