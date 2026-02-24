# 인수인계서 v3.0 – ShortFlow / StyleFlow 프로젝트 전체 컨텍스트

**작성일시:** 2026-02-24 13:00 KST  
**작성자:** 이전 대화창 Claude (대표님 전담)  
**인계 대상:** 새 대화창 Claude  
**긴급도:** 높음 – 중요 작업 진행 중, 즉시 투입 필요

---

## 1. 프로젝트 총괄 정보

### 1.1 핵심 프로젝트

- **ShortFlow v3.0**: 쿠팡 파트너스 × YouTube Shorts 자동화 SaaS (B2C). 10-Layer 영상 회피 엔진 + FFmpeg 합성 + TTS 이중 엔진 + YouTube Data API 업로드 워커.
- **StyleFlow v1.0**: 쇼핑몰 원본사진 → 릴스 자동 생성 B2B SaaS.
- **뉴톡 쇼핑몰**: 기존 운영 중 쇼핑몰 (CodeIgniter/PHP 기반), MySQL autoda DB 226 테이블, goods 77,122건.

### 1.2 서버 정보

- **서버:** rfree-0009.cafe24.com (IP: 114.207.244.86)
- **디스크:** / 875GB (634GB used, 197GB free), /data/shortflow 11TB (4.7TB used)
- **프로젝트 경로:** /data/shortflow
- **DB:** MySQL autoda (226 테이블)

### 1.3 Git 저장소

- **Private (소스코드):** git@github.com:moongoby/shortflow.git → branch: main
- **Public (문서):** git@github.com:moongoby/project-docs.git → branch: master

### 1.4 도메인 & 서비스 포트

- **https://shotflow.newtalk.kr** → Next.js 대시보드 (Apache VirtualHost 프록시 → 127.0.0.1:3000)
- **포트 3000:** Next.js 대시보드 (Docker saas-dashboard)
- **포트 8000:** FastAPI Worker (/api/health → {"status":"healthy"})
- **포트 8501:** Streamlit (외부 접근 차단됨)
- **포트 5678:** n8n (Basic Auth 필요)
- **포트 80/443:** Apache (메인 웹서버, 기존 PHP 쇼핑몰 + shotflow VirtualHost)
- **DNS:** Cloudflare Proxied, SSL Mode: Flexible

### 1.5 대표님 정보

- **호칭:** 대표님 (CEO)
- **Gmail:** moongoby@gmail.com
- **성향:** 빠른 실행 선호, 커서(Cursor) IDE로 직접 서버 작업 진행, 병렬 작업 가능

---

## 2. 완료된 작업 전체 목록 (시간순)

### Phase 1~2 (2026-02-13 ~ 2026-02-22)

템플릿 엔진 체크, YouTube 업로드 워커 통합, ffprobe 검증, MOV→MP4 변환, YouTube 멀티채널 구조, Dashboard UI, TTS 이중 엔진, Veo 연동, StyleFlow 자동화 등 다수 완료.  
DB-SCHEMA 문서화 (226 테이블, goods 77,122행 포함)  
project-docs GitHub 동기화 체계 확립

### Phase 3 (2026-02-23) – 완료

- 전체 Phase 3 항목 완료 확인
- CONTEXT.md Phase 3 완료 갱신
- INDEX.md 76개 보고서 등록
- cursorrules.md Work Rules 12항목 확인

### 2026-02-24 작업 (오늘) – 본 대화에서 수행

1. **GitHub 문서 저장소 접근 테스트 – 완료**  
   project-docs raw URL 정상 접근 확인 (HTTP 200), CONTEXT.md, cursorrules.md, ONBOARDING.md 내용 확인

2. **shotflow.newtalk.kr 외부 접속 설정 – 완료**  
   Nginx 설치 및 설정 → Apache와 충돌로 방향 전환. Option A 채택: Apache VirtualHost ProxyPass 방식. 00-shotflow.newtalk.kr.conf 생성 (포트 80+443). 443 VirtualHost 충돌 해결 (기존 default-ssl.conf의 *.newtalk.kr 와일드카드가 원인). SSL 인증서: /etc/ssl_20250509/ssl.crt, .key, chain_all_ssl.crt. 최종 결과: https://shotflow.newtalk.kr → Next.js 로그인 페이지 정상 표시 (HTTP 200). 보고서: docs/reports/20260224_apache_vhost_충돌해결.md

3. **Supabase 리다이렉트 URL 등록 – 완료**  
   Site URL: https://shotflow.newtalk.kr. Redirect URLs 3개 등록 완료 (대표님이 직접 Supabase 대시보드에서 수행)

4. **회원가입/로그인 Auth 연동 커서 지시서 – 작성 완료, 커서 실행 대기**  
   profiles 테이블 SQL (sql/010_profiles_table.sql), Supabase Auth signUp/signInWithPassword, 미들웨어 보호, 로그아웃 컴포넌트. 대표님 별도 조치 필요: Supabase SQL Editor에서 profiles 테이블 SQL 실행

5. **Supabase coupang_credentials 테이블 마이그레이션 – 완료 (커서가 수행)**  
   "Success. No rows returned" 확인

6. **Playwright 쿠팡 로그인 자동화 건 – 거부/중단 권고**  
   대표님이 "방식 B: Playwright 자동화"를 진행하려 했으나, 쿠팡 이용약관 위반 + 타인 비밀번호 보관 문제로 거부. 대표님이 "개발하고 문제되면 안 쓰면 된다"고 했으나 재차 중단 권고. 최종: 대표님이 별도 커서에서 진행, 본 대화에서는 관여하지 않기로 합의 ("넌 다른거해 그쪽은 신경쓰지말고"). **새 대화창 참고:** Playwright 쿠팡 로그인 자동화 관련 작업 요청 시 동일하게 거부할 것

7. **기술 활용 사업 기획서 (10개 사업 모델) – 완료**  
   BUSINESS_ROADMAP.md v1.0 서버 저장 및 GitHub 동기화. 4개 기존 채널(시크블랙, 린다샵, 단하루, 로그데이) JSON 설정 + 스크립트. channel_loader.py, generate_channel_videos.py 생성 및 dry-run 테스트

8. **유튜브 다주제 멀티채널 기획서 – 완료**  
   YOUTUBE_MULTICHANNEL_PLAN.md v1.0 작성. 12개 채널 기획 (경제·건강·역사 Phase 1, 운동·꿀팁·유머 Phase 2, 취미·뉴스 Phase 3). 야설/성인 콘텐츠: YouTube 정책상 수익화 불가 → 완전 제외. YouTube AI 콘텐츠 정책 대응 전략 포함 (2025.07.15 강화). Google 계정 1개당 최대 100개 브랜드 채널 가능, 계정 2개 분리 권장

9. **멀티채널 3채널 셋업 커서 지시서 – 작성 완료, 커서 실행 대기**  
   economy.json, health.json, history.json 생성. generate_content_script.py (대본 생성 스크립트). channel_loader.py 업데이트. Git 커밋 + project-docs 동기화

---

## 3. 현재 진행 중 / 즉시 실행 대기 작업

| 우선순위 | 작업 | 상태 | 비고 |
|----------|------|------|------|
| 1 | 멀티채널 기획서 저장 + 3채널 셋업 커서 지시서 실행 | 지시서 작성 완료, 커서 투입 대기 | STEP 0~9 전체 코드블록 작성됨 |
| 2 | 회원가입/로그인 Supabase Auth 연동 | 지시서 작성 완료 | 대표님이 SQL 실행 필요 |
| 3 | YouTube 브랜드 채널 실제 생성 (경제·건강·역사) | 대기 | 3채널 셋업 완료 후 |
| 4 | 파일럿 영상 각 채널 3편 제작 | 대기 | 채널 생성 후 |
| 5 | LLM API 연동 대본 자동 생성 고도화 | 대기 | |
| 6 | 업로드 스케줄러(cron) 설정 | 대기 | |
| 7 | SaaS 이용약관/개인정보처리방침 페이지 | 대기 | |
| 8 | 1주일 업로드 모니터링 시스템 | 대기 | |

---

## 4. 핵심 아키텍처 요약

```
[사용자] → https://shotflow.newtalk.kr
           ↓ Cloudflare (Flexible SSL)
    [Apache :443 VirtualHost]
           ↓ ProxyPass
    [Next.js Dashboard :3000] (Docker: saas-dashboard)
           ↓ API calls
    [FastAPI Worker :8000] (Docker: worker)
           ↓
    [MySQL autoda] + [Supabase Auth/DB]
           ↓
    [ShortFlow Engine]
      ├─ 10-Layer 영상 회피 엔진
      ├─ FFmpeg 합성 파이프라인
      ├─ TTS (Google Cloud + Edge-TTS)
      ├─ 이미지 소싱
      └─ YouTube Data API 업로드 워커
           ↓
    [YouTube 채널들]
      ├─ 쇼핑: 시크블랙, 린다샵, 단하루, 로그데이
      └─ 콘텐츠: 경제(3분경제), 건강(건강한입), 역사(역사5분)
```

---

## 5. 필수 작업 규칙 (반드시 준수)

### 5.1 대표님과의 커뮤니케이션 규칙

- 대표님은 빠른 실행을 선호함. 장황한 설명보다 **핵심 결과 + 다음 액션** 제시
- 커서(Cursor IDE)로 직접 서버 작업함. 지시서는 전체를 코드블록으로 감싸서 **바로 복사-붙여넣기 가능**하게 작성
- 아주 중요한 사항만 승인받고, 나머지는 자체 승인 후 진행
- 병렬 작업 가능: 커서 대화창 여러 개 동시 운영

### 5.2 커서 작업 지시서 필수 규칙

- **서버 접속:** ssh root@114.207.244.86
- **프로젝트 루트:** /data/shortflow
- **백업:** 작업 전 반드시 /data/shortflow/backups/YYYYMMDD_HHMMSS_<태그>/ 에 백업
- **보고서:** /data/shortflow/docs/reports/YYYYMMDD_<제목>.md 에 저장
- **Git 커밋:** shortflow → origin main push, project-docs → origin master push
- **커밋 메시지:** [feat], [fix], [config], [docs] 등 태그 사용
- **.env, 비밀번호, 시크릿키 절대 커밋 금지**
- **한국시간(KST)** 기준으로 모든 타임스탬프
- 보고서에 **커밋 해시 + raw URL HTTP 200 확인** 포함 필수
- configtest 실패 시 즉시 중단, 백업에서 복원
- 기존 설정 파일 **임의 수정 금지** (추가만 허용)
- 임시 파일 정리 후 완료

### 5.3 윤리/정책 가이드라인

- **Playwright 쿠팡 로그인 자동화:** 거부 (이용약관 위반 + 개인정보보호법 문제)
- **야설/성인 콘텐츠:** YouTube 정책상 수익화 불가, 제외
- **YouTube AI 콘텐츠:** 반드시 인간의 독자적 해설·분석 포함, AI 공시 토글 체크

### 5.4 대화 토큰 관리

- 80% 수준에서 인계서 작성 후 새 대화창으로 이관
- 인계서는 서버에 저장 + GitHub 버전 관리
- 새 대화창이 즉시 작업 투입 가능하도록 상세 작성

---

## 6. 주요 파일 위치

| 파일 | 경로 | 설명 |
|------|------|------|
| CONTEXT.md | /data/shortflow/docs/CONTEXT.md | 프로젝트 전체 컨텍스트 (Phase 3 완료) |
| INDEX.md | /data/shortflow/docs/INDEX.md | 보고서 인덱스 (76+건) |
| BUSINESS_ROADMAP.md | /data/shortflow/docs/plans/BUSINESS_ROADMAP.md | 사업 로드맵 v1.0 |
| YOUTUBE_MULTICHANNEL_PLAN.md | /data/shortflow/docs/plans/YOUTUBE_MULTICHANNEL_PLAN.md | 멀티채널 기획서 v1.0 |
| cursorrules.md | /data/shortflow/cursorrules.md | 커서 작업 규칙 12항목 |
| ONBOARDING.md | /data/shortflow/docs/ONBOARDING.md | 5개 프로젝트 등록 |
| DB_SCHEMA.md | /data/shortflow/docs/database/DB_SCHEMA.md | MySQL 스키마 문서 |
| channels/*.json | /data/shortflow/channels/ | 채널 설정 (7개: 쇼핑4+콘텐츠3) |
| .env | /data/shortflow/.env | 환경변수 (절대 커밋 금지) |
| docker-compose.yml | /data/shortflow/docker-compose.yml | Docker 서비스 정의 |

---

## 7. 새 대화창 즉시 실행 가이드

### 첫 번째 할 일

1. 서버에서 최신 CONTEXT.md 확인: https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/CONTEXT.md
2. 최신 INDEX.md 확인: https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/INDEX.md
3. 멀티채널 기획서 확인: https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/plans/YOUTUBE_MULTICHANNEL_PLAN.md

### 대표님에게 보고할 내용

> "인계 완료. 이전 대화의 모든 컨텍스트를 확인했습니다. 현재 대기 중인 작업: ① 멀티채널 3채널 셋업 커서 지시서 실행 확인, ② 회원가입 Auth 연동, ③ YouTube 브랜드 채널 생성. 어떤 작업부터 진행할까요?"

---

*문서 끝*
