---
project: KIS
task_id: CUR-V41-DESK-FRONTEND-ARCH-001
completed_at: 2026-03-03 13:55 KST
directive_file: KIS_20260303_134825_BRIDGE.md
status: PARTIAL_COMPLETE
---

# CUR-V41-DESK-FRONTEND-ARCH-001 실행 결과

## 실행 요약

| 항목 | 내용 |
|------|------|
| 태스크 | DESK 프론트엔드 아키텍처 기획기술문서 v1.0 |
| 담당 | Claude Sonnet 4.6 (claudebot) |
| 완료 시각 | 2026-03-03 13:55 KST |
| 상태 | PARTIAL — 문서 작성 완료 / project-docs/design/ 배포는 root 수동 필요 |

---

## 지시서 이슈: 파일 절단

지시서 파일이 **16줄(621바이트)에서 절단**됨. 헤리독 내용(문서 본문)이 모두 유실. 원인: HTML `<span class="cursor">` 태그 포함 → 웹 UI 복사 시 불완전 전송.

**대응**: 기존 아키텍처 문서 4건 분석 → 문서 내용 재구성:
- DESK-FRACTAL-ARCHITECTURE-v3.0-20260301.md
- DESK2-DESIGN-SPEC-v3.0-20260228.md
- SYSTEM-ARCHITECTURE-FLOWCHART-v1.0-20260301.md
- CTE-DESK-COMPARE-ARCHITECTURE-v1.0-20260301.md

---

## 완료된 작업

### ✅ 작업1: 문서 작성 완료
- **위치**: `/tmp/DESK-FRONTEND-ARCHITECTURE-v1.0-20260303.md`
- **크기**: 약 10,500 바이트

### ⚠️ 작업2: project-docs/design/ 배포 — root 수동 필요
- **이유**: claudebot은 /root/project-docs/ 쓰기 권한 없음
- **설치 스크립트**: `/tmp/install_desk_frontend_arch.sh`
- **실행 명령**:
  ```bash
  sudo bash /tmp/install_desk_frontend_arch.sh
  ```

---

## 문서 내용 (전문)

아래는 작성된 DESK-FRONTEND-ARCHITECTURE-v1.0 전문. done_watcher가 project-docs/reports/에 복사하면 내용이 보존됨.

---

# DESK 프론트엔드 아키텍처 기획기술문서 v1.0

**문서 ID**: DESK-FRONTEND-ARCHITECTURE-v1.0
**작성일**: 2026-03-03
**작성자**: Claude Sonnet 4.6 (CUR-V41-DESK-FRONTEND-ARCH-001)
**승인자**: CEO 확정 대기
**연관 문서**: DESK-FRACTAL-ARCHITECTURE-v3.0, DESK2-DESIGN-SPEC-v3.0, SYSTEM-ARCHITECTURE-FLOWCHART-v1.0

### 1장. 화면 구조 Overview

주요 라우트:
- `/desk` — DESK Command Center (DESK1~5 통합 모니터링) [P1]
- `/desk/desk2` — DESK2 실행 패널 (장중 진입·청산 실시간) [P1]
- `/desk/desk3` — DESK3 풀 관리 (단기풀 50~100종목) [P2]
- `/desk/desk4` — DESK4 풀 관리 (중기풀 20~30종목) [P3]
- `/desk/desk5` — DESK5 풀 관리 (장기풀 10~20종목) [P3]
- `/desk/capital` — 자본배분 패널 (Stage 1/2/3) [P2]
- `/desk/pools` — 풀 플로우 시각화 (Sankey) [P2]

### 2장. DESK2 실행 패널 (P1 최우선)

핵심 구성요소:
- 현재 포지션 테이블 (종목, 진입가, 현재가, 수익률, 전략, 청산 버튼)
- 감시 중 종목 (DESK3 풀 수신, Birth 감지 표시)
- 컨디션 레이어 현황 (C1~C7 ON/OFF 상태)
- Birth Point 실시간 감지 위젯 (팝업 알림 포함)
- 6-Layer 전략 매핑 매트릭스 (C1~C7 × D2/D4/D5/D6/D7/S1)

### 3장. DESK3 풀 관리 패널 (P2)

- 풀 현황 테이블: 종목, 스코어, 입풀일, 체류일수, L3/X9 지표, 뉴스 건수
- 5-Layer 스코어 분해 (Layer 1~5 상세)
- 필터: 섹터, 스코어순, 상태별
- 수동 조작: 추가, 퇴출, DESK4 강등

### 4장. 실시간 데이터 연동

WebSocket 이벤트:
- `desk2.birth` — Birth 감지 (실시간)
- `desk2.position` — 포지션 현황 (5초)
- `desk2.signal` — 컨디션 감지 (실시간)
- `desk3.pool` — 풀 갱신 (15분)
- `market.state` — BULL/FLAT/BEAR (1분)

REST API:
- GET `/api/desk/pools` — 전체 DESK 풀 현황
- GET `/api/desk/desk2/positions` — DESK2 포지션
- GET/POST/DELETE `/api/desk/desk3/pool` — 풀 CRUD
- POST `/api/desk/desk2/manual-entry` — 수동 진입
- POST `/api/desk/desk2/manual-exit` — 수동 청산

### 5장. 컴포넌트 구조

```
src/app/(protected)/desk/
├── page.tsx                    # Command Center
├── desk2/page.tsx             # DESK2 실행 패널
├── desk3/page.tsx             # DESK3 풀 관리
├── capital/page.tsx           # 자본배분

src/components/desk/
├── DeskOverviewCard.tsx
├── DeskPoolTable.tsx
├── ScoreBreakdown.tsx
├── BirthAlertWidget.tsx
├── PositionPanel.tsx
├── ConditionMatrix.tsx
├── CapitalAllocation.tsx
└── RealtimeOrderLog.tsx
```

### 6장. 구현 로드맵

| Phase | 화면 | 선결 조건 |
|-------|------|----------|
| Phase 0 | DESK2 실행 패널 기초 | DESK2 백엔드 완성 |
| Phase 1 | DESK Command Center | v4_desk3_pool 등 DB |
| Phase 2 | DESK3 풀 관리 | 스코어링 엔진 |
| Phase 3 | DESK4/5 풀 관리 | DESK4/5 엔진 |
| Phase 4 | 자본배분 패널 | Kelly 모듈 |
| Phase 5 | DESK1 스캘핑 | DESK1 엔진 |

---

## 조치 요청

**root가 수동 실행해야 할 명령**:
```bash
bash /tmp/install_desk_frontend_arch.sh
```

이 스크립트가 실행되면:
1. `/tmp/DESK-FRONTEND-ARCHITECTURE-v1.0-20260303.md` → `/root/project-docs/kis-autotrade-v4/design/`
2. git add + commit + push → GitHub 자동 반영

---

## 체크포인트

- [x] 코드/문서 작성 완료 (/tmp/DESK-FRONTEND-ARCHITECTURE-v1.0-20260303.md)
- [x] RESULT.md → done_watcher → project-docs/reports/ push (이 파일)
- [ ] project-docs/design/ 배포: root가 `/tmp/install_desk_frontend_arch.sh` 실행 필요

## 수동 완료 필요 사항

**대표님 확인 요청**: 지시서 파일(KIS_20260303_134825_BRIDGE.md)이 16줄에서 절단되어 원본 문서 내용이 유실되었습니다. 위에 재구성한 DESK-FRONTEND-ARCHITECTURE v1.0 내용을 검토하시고, 수정이 필요하면 알려주세요. 또한 root 권한으로 `/tmp/install_desk_frontend_arch.sh` 실행이 필요합니다.
