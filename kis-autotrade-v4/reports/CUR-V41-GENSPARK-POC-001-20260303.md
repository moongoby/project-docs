# Genspark Playwright POC 결과 보고서

**문서 ID**: CEO-GENSPARK-BRIDGE-001  
**보고서 번호**: CUR-V41-GENSPARK-POC-001  
**작성일**: 2026-03-03  
**작성**: KIS V4.1 Cursor

---

## 1. 개요

Genspark 자동 대화 브릿지 구축을 위한 Playwright POC를 수행하였다.  
환경 구축(venv + Playwright Chromium) 후 6단계 접근·스크린샷·셀렉터 수집을 진행하였고,  
브라우저 수동 확인으로 로그인 플로우 및 AI 채팅 입력 셀렉터를 보완하였다.

---

## 2. 환경 구축 결과

| 항목 | 결과 |
|------|------|
| Playwright 설치 | `/root/.genspark/venv` 내 설치 완료 |
| Chromium | `playwright install chromium` 완료 |
| `.genspark/.env` | 존재 확인 (GENSPARK_EMAIL, GENSPARK_PASSWORD 사용) |
| POC 스크립트 | `/root/.genspark/genspark_poc.py` |

---

## 3. 각 단계 성공/실패

| 단계 | 내용 | 결과 | 비고 |
|------|------|------|------|
| 01 | https://www.genspark.ai/ 접근 | **성공** | poc_01_main.png 저장 |
| 02 | 로그인 페이지 이동 | **부분 성공** | 메인에서 "로그인" 클릭 → 모달 → "더 많은 옵션" 시 외부 도메인(login.genspark.ai) 이동 |
| 03 | .env 기반 자동 로그인 | **성공** | session.json 저장, poc_03_loggedin.png |
| 04 | AI Chat 페이지 이동 | **성공** | wait_until=load 로 타임아웃 완화 후 재실행으로 성공, poc_04_chat.png |
| 05 | 새 대화 생성 + 첫 메시지 전송·응답 대기 | **부분 성공** | 스크린샷 저장. 셀렉터는 브라우저 스냅샷으로 추후 확정 |
| 06 | 대화명 변경 시도 | **시도 완료** | poc_06_renamed.png 저장. UI에 따라 편집 버튼 추가 탐색 필요 |

---

## 4. DOM 셀렉터 목록

### 4.1 Genspark 로그인 폼 (login.genspark.ai)

로그인은 **www.genspark.ai** 메인에서 **로그인** 클릭 → **더 많은 옵션** 클릭 시 **login.genspark.ai** 로 리다이렉트된다.

| 용도 | 셀렉터 (Playwright 권장) |
|------|---------------------------|
| 이메일 입력 | `page.get_by_label("Email Address")` 또는 `page.locator('input[placeholder*="Email" i]')` |
| 비밀번호 입력 | `page.get_by_label("Password")` 또는 `page.locator('input[type="password"]')` |
| 로그인 버튼 | `page.get_by_role("button", name="Sign in")` |

**메인 페이지에서 로그인 유도**

- 로그인 링크: `page.get_by_role("link", name="로그인")` 또는 텍스트 "로그인" 포함 요소 클릭
- 더 많은 옵션: `page.get_by_role("button", name="더 많은 옵션")` (모달 내)

### 4.2 AI Chat 메시지 입력

| 용도 | 셀렉터 |
|------|--------|
| 메시지 input | `page.get_by_placeholder("무엇이든 물어보고 만들어보세요")` 또는 `page.get_by_role("textbox", name="무엇이든 물어보고 만들어보세요")` |

(한국어 로케일 기준. 영문이면 "Ask anything..." 유사 placeholder 사용 가능.)

### 4.3 전송 버튼

- 전송 버튼이 별도로 보이면: `page.get_by_role("button", name="전송")` 또는 `button[type="submit"]`  
- POC 시에는 **Enter 키**로 전송 가능한 구조로 확인.

### 4.4 응답 메시지 컨테이너

- SPA 구조로 클래스명이 동적일 수 있음.  
- 권장: `page.locator('[class*="message"]').last` 또는 `[class*="assistant"]`, `[class*="response"]` 등으로 후보 탐색 후, **6초간 텍스트 변화 없음**으로 응답 완료 판정 (현 POC 로직 유지).

### 4.5 새 대화 시작

- 메인에서 **New** 버튼: `page.get_by_role("button", name="New")` 또는 해당 영역 클릭 시 채팅 입력창이 노출되는 플로우로 확인.

### 4.6 대화명 변경

- 대화 목록/사이드바에서 해당 대화 항목 클릭 후 **편집/이름변경** UI 탐색 필요.  
- POC에서는 `button[aria-label*="edit" i]`, `[class*="rename"]` 등 시도. 실제 서비스에서 노출되는 편집 버튼/메뉴에 맞춰 셀렉터 확정 권장.

---

## 5. 대화 URL 패턴

- POC 시 채팅 진행 후 **page.url** 로 수집.  
- Genspark SPA 특성상 대화별 고유 path/query 가 있을 경우 해당 패턴을 추출해 재접근용 URL로 사용 가능.  
- (실제 값은 세션·환경에 따라 상이하므로 여기서는 패턴만 명시.)

---

## 6. 스크린샷 저장 위치

| 파일 | 설명 |
|------|------|
| `/root/.genspark/poc_01_main.png` | 메인 페이지 |
| `/root/.genspark/poc_02_login.png` | 로그인 유도 후 화면 |
| `/root/.genspark/poc_03_loggedin.png` | 로그인 완료 후 |
| `/root/.genspark/poc_04_chat.png` | AI Chat 화면 |
| `/root/.genspark/poc_05_response.png` | 메시지 전송·응답 후 |
| `/root/.genspark/poc_06_renamed.png` | 대화명 변경 시도 후 |

---

## 7. 결론 및 다음 단계

- **로그인**: login.genspark.ai 이메일/비밀번호 폼 셀렉터 확정. 세션 저장(session.json)으로 재로그인 최소화 가능.
- **채팅**: 메인 페이지 텍스트박스("무엇이든 물어보고 만들어보세요")로 메시지 입력·전송 가능. 응답 완료는 6초 안정화 기준 유지.
- **3단계**: 위 셀렉터를 반영한 스크립트로 5개 대화창 자동 생성 및 URL 저장 진행 예정.
- **보안**: `/root/.genspark/` 전체 .gitignore 유지, session.json·.env·chat_urls 미커밋 원칙 준수.

---

## 저장 정보

- 서버 경로: `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-GENSPARK-POC-001-20260303.md`
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-GENSPARK-POC-001-20260303.md
- 커밋: (push 후 갱신)
- HTTP 확인: (push 후 200 확인)
- HANDOVER 업데이트: (필요 시 수행)
