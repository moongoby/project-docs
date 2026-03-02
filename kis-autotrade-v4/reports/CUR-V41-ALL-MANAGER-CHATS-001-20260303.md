# CUR-V41-ALL-MANAGER-CHATS-001 — 6프로젝트 매니저 대화창 + bridge.py 확장

**작업 ID**: CUR-V41-ALL-MANAGER-CHATS-001  
**날짜**: 2026-03-03  
**담당**: Cursor AI  
**우선순위**: P1  

---

## 1. 목표

- Genspark AI 채팅 + Claude Opus 4.6 모델로 4개 프로젝트 매니저 대화창 신규 생성
- `/root/.genspark/.env` 업데이트 (4개 URL + SSH 환경변수)
- `genspark_bridge.py` PROJECTS 섹션 6개 프로젝트로 확장
- `genspark-bridge` 서비스 재시작 및 6개 동시 폴링 확인

---

## 2. 완료 사항

### 2-1. Genspark 대화창 생성 (4개)

| 프로젝트 | 대화창 이름 | Genspark URL ID | 모델 | 초기화 |
|----------|------------|-----------------|------|--------|
| AADS | [AADS] 프로젝트 매니저 | `3d86d6f3-09a7-41b2-b91b-762a55512458` | Claude Opus 4.6 | 맥락 파악 완료 |
| SF | [SF] ShortFlow 프로젝트 매니저 | `1107f4e7-344d-48c5-820e-0b34b561b4e3` | Claude Opus 4.6 | 맥락 파악 완료 |
| NAS | [NAS] NAS Image 프로젝트 매니저 | `8112e93a-189f-4e8c-bf7b-fc27bea8f431` | Claude Opus 4.6 | 맥락 파악 완료 |
| NTV2 | [NTV2] NewTalk V2 프로젝트 매니저 | `668a994f-e12a-45e4-99cd-e6e29e7ef238` | Claude Opus 4.6 | 맥락 파악 완료 |

각 대화창 초기화 메시지 포함:
- 역할 정의 (CURSOR-{TAG} / CEO 메시지 구분)
- 프로젝트 문서 GitHub URL (HANDOVER.md, SECURITY_RULES.md, DOCUMENT-NAMING-CONVENTION.md)
- 보안 스캔 패턴 (`211.188.*`, `genspark_dev@`, `kill.switch`)
- `>>>DIRECTIVE_START / >>>DIRECTIVE_END` 블록 프로토콜

### 2-2. .env 업데이트

경로: `/root/.genspark/.env`

추가 항목:
- `GENSPARK_CHAT_AADS`, `GENSPARK_CHAT_SF`, `GENSPARK_CHAT_NAS`, `GENSPARK_CHAT_NTV2` — 각 대화창 URL
- `SSH_CMD_AADS`, `SSH_CMD_SF`, `SSH_CMD_NAS`, `SSH_CMD_NTV2` — SSH 접속 명령 (환경변수로 관리, IP/포트 하드코딩 금지)

### 2-3. bridge.py PROJECTS 6개 확장

경로: `/root/.genspark/genspark_bridge.py`

- `_load_project_config()` 함수 리팩터링: `env_vars` dict 파싱 → `_get(key, default)` 헬퍼로 통일
- 기존 2개(KIS, GO100) → 6개(KIS, GO100, AADS, SF, NAS, NTV2) 확장
- 각 프로젝트 필드: `chat_url`, `services`, `tag`, `whitelist`, `cursor_prefix`, `ssh`
- SSH 접속 정보: `os.getenv` 경유 로드 (하드코딩 금지 준수)

### 2-4. 서비스 재시작 + 폴링 확인

```
systemctl restart genspark-bridge
→ active (running) 확인
→ 로그: 활성 프로젝트: ['KIS', 'GO100', 'AADS', 'SF', 'NAS', 'NTV2']
```

6개 프로젝트 동시 폴링 시작 확인 (2026-03-02 15:37:30 KST)

---

## 3. 보안 준수 사항

- SSH 접속 정보(IP, 포트, 사용자)는 보고서 및 project-docs에 노출 금지 — 환경변수로만 관리
- `.genspark/.env`는 `.gitignore` 적용 (git 커밋 대상 외)
- 대화창 URL ID만 공개 저장소에 기록 (인증 없이 접근 불가)

---

## 4. 검증 결과

| 항목 | 결과 |
|------|------|
| AADS 대화창 생성 | PASS (맥락 파악 완료) |
| SF 대화창 생성 | PASS (맥락 파악 완료, HANDOVER 크롤링 성공) |
| NAS 대화창 생성 | PASS (맥락 파악 완료, P4 현황 파악) |
| NTV2 대화창 생성 | PASS (맥락 파악 완료, R0~R4 현황 파악) |
| .env URL 등록 | PASS (4개 URL + 4개 SSH_CMD) |
| bridge.py 6개 확장 | PASS (환경변수 기반 동적 로드) |
| 서비스 재시작 | PASS (active running) |
| 6개 폴링 확인 | PASS (로그 확인: 6개 활성) |

---

## 5. 참고 — 6프로젝트 매니저 체계

| 프로젝트 | 태그 | 서비스 | SSH |
|----------|------|--------|-----|
| KIS | KIS | kis-v41-api, kis-v41-monitor, kis-v41-scheduler | 환경변수 |
| GO100 | GO100 | go100 | 환경변수 |
| AADS | AADS | (없음) | `$SSH_CMD_AADS` |
| SF | SF | (없음) | `$SSH_CMD_SF` |
| NAS | NAS | (없음) | `$SSH_CMD_NAS` |
| NTV2 | NTV2 | (없음) | `$SSH_CMD_NTV2` |

---

**HTTP**: 200  
**보안 스캔**: 0건 (SSH 정보 마스킹 완료)
