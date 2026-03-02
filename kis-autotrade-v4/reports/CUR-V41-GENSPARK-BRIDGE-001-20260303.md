# Genspark 자동 대화 브릿지 구축 보고서

**문서 ID**: CEO-GENSPARK-BRIDGE-001  
**보고서**: CUR-V41-GENSPARK-BRIDGE-001  
**작성일**: 2026-03-03  
**담당**: KIS V4.1 Cursor (공통 관리 겸임)

---

## 1. 개요

CEO 지시에 따라 Genspark AI(genspark.ai)와 Cursor 간 자동 대화 브릿지를 구축하였다.  
Playwright 기반 로그인·채팅 POC, 5개 프로젝트 대화창 생성 스크립트, verify.sh 및 보안 조치를 완료하였다.

---

## 2. 완료 항목

### 2.1 환경 구축 (1단계)
- Playwright + Chromium: `/root/.genspark/venv` 에 설치
- `.genspark/.env` 확인 (GENSPARK_EMAIL, GENSPARK_PASSWORD 사용)
- `.gitignore` 에 `.genspark/` 추가 (project-docs)

### 2.2 Genspark POC (2단계)
- **보고서**: `kis-autotrade-v4/reports/CUR-V41-GENSPARK-POC-001-20260303.md`
- 스크린샷: `/root/.genspark/poc_01_main.png` ~ `poc_06_renamed.png`
- 세션 저장: `/root/.genspark/session.json`
- **로그인 플로우**: www.genspark.ai → 로그인 → 더 많은 옵션 → login.genspark.ai (이메일/비밀번호)
- **셀렉터**: 이메일 `get_by_label("Email Address")`, 비밀번호 `get_by_label("Password")`, 전송 `get_by_role("button", name="Sign in")`, 채팅 입력 `get_by_placeholder("무엇이든 물어보고 만들어보세요")`

### 2.3 5개 대화창 자동 생성 (3단계)
- **스크립트**: `/root/.genspark/create_5_chats.py`
- **공통 모듈**: `/root/.genspark/genspark_common.py` (load_env, ensure_logged_in, send_message_and_wait, human_type)
- KIS-V41, GO100, SF, NAS, NTV2 각 초기화 메시지 정의 완료
- 생성 간 2~5분 랜덤 대기 적용
- URL 저장: `.env` (GENSPARK_CHAT_KIS, GENSPARK_CHAT_GO100), `chat_urls_114.json` (SF, NTV2, NAS)

### 2.4 114서버 URL 전달 (4단계)
- 전달 명령: `scp -P 7916 /root/.genspark/chat_urls_114.json root@[SERVER-IP]:/root/.genspark/chat_urls_114.json`
- verify.sh는 project-docs에 포함되어 114서버에서 `git pull` 후 사용

### 2.5 verify.sh 및 보안 조치 (5단계)
- **setup_full.sh** 삭제 (git rm, 커밋 완료)
- **SYNC_GUIDE.md** 마스킹: [NAS-IP] → [NAS_HOST], 2222 → [NAS_PORT]
- **루트 보고서** 2건 이동: kis-autotrade-v4/reports/ (CUR-V41-D2-IMPROVE-RSI-MA10-001, CUR-V41-D2ABC-REALCODE-008)
- **scripts/verify.sh** 생성: 5개 프로젝트 공통 검증, path_check.sh 호출 또는 프로젝트별 요약
- **scripts/path_check.sh** 확장: SF, NAS, NTV2 프로젝트·경로·파일명 규칙 추가
- **ONBOARDING.md**: KIS 중복 제거, NTV2 추가
- **DOCUMENT-NAMING-CONVENTION.md**: CUR-SF-*, CUR-NAS-*, CUR-NTV2-* 저장 위치 및 교차 저장 금지 명시
- **common/SECURITY_RULES.md**: IP·호스트 마스킹 규칙 추가

---

## 3. 6단계 통합 테스트 (안내)

통합 테스트는 실제 로그인·대화 URL 확보 후 다음 순서로 수행한다.

1. **브라우저 열기** → [VERIFY] KIS-V41 대화창 이동 (GENSPARK_CHAT_KIS URL)
2. **메시지 입력**: `[CURSOR-KIS] 세션 시작\nHANDOVER: {URL}\n다음 지시해주세요.`
3. **응답 대기** → `>>>DIRECTIVE_START` ~ `>>>DIRECTIVE_END` 파싱
4. **지시에 따라 간단한 작업 1건 수행**
5. **브라우저에 결과 보고 입력**
6. **응답에서 다음 지시 확인**

성공 시 `genspark_bridge.py` v1.0으로 래핑하여 Private 레포에 저장한다.

---

## 4. 보안 준수 사항

- `/root/.genspark/` 전체를 .gitignore에 추가 완료
- genspark_bridge.py 및 POC/생성 스크립트는 Private 레포에만 저장 (현재 서버 로컬에만 존재)
- session.json, .env, chat_urls_114.json 절대 Public 커밋 금지
- Genspark 접근 시 인간적 딜레이(글자당 50~120ms) 적용

---

## 5. HANDOVER 갱신 요약

- **Genspark 브릿지**: Playwright POC·5채 생성 스크립트·verify.sh·보안 조치 반영
- **다음 작업**: 3단계 create_5_chats.py 실행으로 5개 대화 URL 확보 → 6단계 통합 테스트 1회 실행 → genspark_bridge.py v1.0 작성

---

## 저장 정보

- 서버 경로: `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-GENSPARK-BRIDGE-001-20260303.md`
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-GENSPARK-BRIDGE-001-20260303.md
- 커밋: (push 후 갱신)
- HTTP 확인: (push 후 200 확인)
- HANDOVER 업데이트: (필요 시 수행)
