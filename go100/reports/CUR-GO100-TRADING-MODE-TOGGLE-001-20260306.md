---
project: go100
task_id: GO100-T-157
completed_at: 2026-03-06 11:00 KST
status: completed
author: Claude Code (Sonnet 4.6) / root
---

# GO100-T-157: 실매매/모의 토글 UI — accounts·settings 페이지 (2026-03-06)

> 실행일시: 2026-03-06 10:30~11:00 KST
> 커밋: fc398d2d (go100.git / phase-2c-command-center)
> URL: https://go100.newtalk.kr/accounts, https://go100.newtalk.kr/settings

---

## 구현 내용

### /accounts 페이지
계좌 목록 상단에 **실매매/모의 모드 배너** 추가
- 현재 모드 실시간 표시 (초록/빨간 표시)
- 토글 스위치로 즉시 전환 가능
- 실계좌 전환 시 확인 다이얼로그 표시

### /settings 페이지
기존 "계좌 모드" 텍스트 → **토글 스위치** 실제 연동
- `POST /api/v4/admin/switch-account-mode` 백엔드 연결
- 모의 → 실계좌: 경고 확인 후 전환
- 실계좌 → 모의: 즉시 전환
- 실계좌 ON 상태: 일일 한도 / 단일 주문 상한 설정 폼 노출

## 현재 상태

| 항목 | 값 |
|------|---|
| 현재 모드 | **모의투자 (OFF)** — 실계좌 비활성 |
| 로그인 | moongoby@naver.com / moongoby@gmail.com 비밀번호 변경 완료 |
| 빌드 | 성공 |

## GitHub 보고서
https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-TRADING-MODE-TOGGLE-AND-LOGIN-001-20260306.md
