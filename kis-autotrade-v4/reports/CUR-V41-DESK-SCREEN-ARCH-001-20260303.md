---
task_id: CUR-V41-DESK-SCREEN-ARCH-001
project: KIS
date: 2026-03-03
author: Cursor Claude
status: completed
---

# CUR-V41-DESK-SCREEN-ARCH-001 — DESK 시스템 화면 아키텍처 설계문서 저장

> 작업일: 2026-03-03 KST  
> 완료: 2026-03-03 14:xx KST

---

## 작업 내용

CEO 지시 DESK SYSTEM SCREEN ARCHITECTURE 문서를 V4 프로젝트에 100% 누락 없이 저장.

## 저장 위치

```
/root/kis-autotrade-v4/docs/design/DESK-SCREEN-ARCHITECTURE-20260303.md
```

## 저장 내용 (5개 화면 + 아키텍처 + 로드맵)

| 섹션 | 설명 |
|------|------|
| ① DESK Command Center | `/desk-command.html` — CEO 5개 DESK 지휘 화면 |
| ② DESK Stock Universe | `/desk-universe.html` — 종목 중심 차트 + 수급 |
| ③ DESK Performance | `/desk-perf.html` — 실적·통계·리밸런싱 |
| ④ DESK2 Live | `/desk2-live.html` — 장중 실시간 모니터링 (개선) |
| ⑤ Stock Detail Popup | 모달 — 종목 전체 생애 뷰 |
| 데이터 흐름 | PostgreSQL → FastAPI:8003 → Nginx static |
| 신규 테이블 | `v4_desk_positions`, `v4_desk_missed_opportunities` |
| 구현 로드맵 | Phase 1~3 (이번주~그 다음주) |

## 커밋

- 저장소: `moongoby/go100` (kis-autotrade-v4 모노레포)
- 브랜치: `phase-2c-command-center`
- 커밋 SHA: `185f80a2`
- 파일 크기: 374줄 (원문 100% 보존)

## 구현 우선순위 (Phase 1 — 이번주)

- DESK2 Live API 6개 구현
- Lightweight Charts v5 연동
- 3패널 레이아웃 + 30초 자동 리프레시
