# BT-SIDEBAR-FIX-001 백테스트 메뉴 표시 수정 보고서
**작성일:** 2026-02-25
**우선순위:** P0

## 1. 문제
CEO 관리자 대시보드(admin.html#godmode) 사이드바에 "백테스트 분석" 메뉴 미표시

## 2. 원인
**CASE A:** CEO 접속 URL(trading41.newtalk.kr/admin.html#godmode)은 Next.js 앱이 아닌 **별도 정적 HTML 기반 관리자 페이지**이다. 해당 admin.html의 좌측 사이드바(Management 섹션)에 백테스트 관련 메뉴 항목이 없었음. Next.js의 백테스트 분석/차트 페이지는 go100.newtalk.kr에서 서빙됨.

## 3. 수정 내용
- **변경 파일:** `/var/www/trading.newtalk.kr/admin.html`
- **변경 내용:**
  - Management 섹션 내 "전략 설정" 아래에 다음 두 메뉴 항목 추가:
    1. **백테스트 분석** — `https://go100.newtalk.kr/admin/backtest` (새 탭, V4 뱃지)
    2. **백테스트 차트** — `https://go100.newtalk.kr/admin/backtest/charts` (새 탭)
  - 기존 메뉴 패턴(`admin-nav-item`, Font Awesome 아이콘) 동일 적용. 외부 링크이므로 `target="_blank"` 및 `rel="noopener noreferrer"` 사용.

## 4. 브라우저 검증 결과
| 항목 | 결과 |
|------|------|
| 사이드바 메뉴 표시 | O (배포 HTML에 "백테스트 분석", "백테스트 차트" 포함 확인) |
| 클릭 시 페이지 이동 | O (링크가 go100.newtalk.kr/admin/backtest·charts로 설정됨, 307 리다이렉트 정상) |
| 세션 목록 로드 | 로그인 필요 (CEO 계정으로 로그인 후 확인) |
| 차트 렌더링 | 로그인 필요 (CEO 계정으로 로그인 후 확인) |

※ 로그인 없이 접속 시 admin.html이 login.html로 리다이렉트되므로, 로그인 후 좌측 사이드바에 "백테스트 분석", "백테스트 차트"가 표시되는지 CEO 측에서 최종 확인 필요.

## 5. CEO 접속 방법
- **관리자 대시보드 URL:** https://trading41.newtalk.kr/admin.html#godmode
- **메뉴 위치:** 좌측 사이드바 > Management 섹션 > "전략 설정" 바로 아래
- **백테스트 분석:** 클릭 시 새 탭에서 https://go100.newtalk.kr/admin/backtest 열림
- **백테스트 차트:** 클릭 시 새 탭에서 https://go100.newtalk.kr/admin/backtest/charts 열림
