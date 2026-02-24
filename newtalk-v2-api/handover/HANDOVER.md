# 뉴톡 V2 인수인계서
- 버전: 2.0.0
- 최종수정: 2026-02-24 12:45 KST
- 작성: AI Agent

---

## 1. 완료된 작업

| 작업 ID | 내용 | 버전 | 날짜 |
|---------|------|------|------|
| R0 | Laravel 12 + Docker 환경, 38 migration, RBAC | v0.1.0 | 2026-02-21 |
| R1-TASK-001 | Sanctum 인증 + RBAC | v1.0.0 | 2026-02-22 |
| R1-TASK-002 | 상품 CRUD API | v1.0.0 | 2026-02-22 |
| R1-TASK-003 | 발주/입고/바코드 API | v1.0.0 | 2026-02-22 |
| R1-TASK-004 | 대시보드 API | v1.0.0 | 2026-02-22 |
| R1-TASK-005 | V1→V2 마이그레이션 | v1.0.0 | 2026-02-22 |
| R2-FRONT-001 | Next.js 16 프로젝트 셋업 | v1.1.0 | 2026-02-23 |
| R2-FRONT-001-DEPLOY | 프론트엔드 Docker 배포, Rate Limiting | v1.2.0 | 2026-02-23 |
| R2-API-001 | SNS 소셜 엔진 API | v1.3.0 | 2026-02-23 |
| R2-FRONT-002 | 홈 피드 UI | v1.4.0 | 2026-02-23 |
| R2-FIX-001 | 피드백 수정 (역할체크, SQL인젝션, 위시리스트) | v1.4.1 | 2026-02-24 |
| R2-FRONT-003 | 상품 상세 UI | v1.5.0 | 2026-02-24 |
| R2-API-002 | 브랜드 페이지 API | v1.6.0 | 2026-02-24 |
| R2-FRONT-004 | 브랜드 페이지 UI | v1.6.0 | 2026-02-24 |
| V1-CODI-FIX-001 | V1 코디등록 버그 수정 (products.php) | - | 2026-02-24 |

## 2. V1-CODI-FIX-001 수정 상세

| 항목 | 내용 |
|------|------|
| 서버 | 116 (114.207.244.86) |
| 파일 | /home/danharoo/www/application/controllers/products.php |
| 백업 | products.php.bak.20260224 |
| 버그1 | 삭제 시 $code→$goodsCode (3039줄, 5034줄) |
| 버그2 | 등록 시 중복체크 추가 (2645줄, 3045줄) |
| PHP 문법 | No syntax errors |
| Health Check | HTTP 200 |
| 롤백 | cp products.php.bak.20260224 products.php && service phpX.X-fpm reload |

## 3. 미해결 항목

| 항목 | 심각도 | 설명 |
|------|--------|------|
| CONTEXT.md "(미푸시)" 3건 | HIGH | R2-FRONT-003, R2-API-002, R2-FRONT-004 SHA 미교체 |
| CHANGELOG.md "(미푸시)" 2건 | HIGH | SHA 미교체 + v1.6.1 섹션 없음 |
| R2-FIX-002 보고서 | HIGH | 미작성 |
| HANDOVER.md 플레이스홀더 | MEDIUM | 커밋 SHA 미기록 |
| V1-SCHEMA-SUMMARY.md | MEDIUM | 261B (거의 빈 파일) |
| review 폴더 | LOW | 3개 파일 잔존 (.gitkeep만 남겨야 함) |
| SQL 인젝션 (V1 코디함수) | 별도판단 | V2 전환 시 해소 또는 별도 패치 |
| CoordiGoodsCodes varchar(100) | 별도판단 | 코디 10개 이상 시 잘림 가능 |

## 4. 다음 작업 큐

| 순서 | 작업 ID | 내용 |
|------|---------|------|
| 1 | R2-FRONT-005 | 관리자 구매 대시보드 상세 |
| 2 | R2-FRONT-006 | 도매 콘텐츠 업로드 |
| 3 | R2-API-003 | AI 콘텐츠 처리 API |
| 4 | R2-API-004 | Cafe24 API 연동 |

## 5. 서버 정보

| 항목 | 값 |
|------|-----|
| SSH | ssh -p 7916 -i ~/.ssh/id_ed25519_newtalk root@114.207.244.86 |
| V2 작업디렉토리 | /srv/newtalk-v2/ |
| Docker | docker compose --env-file .env.docker |
| V2 API | http://114.207.244.86:8080 |
| V2 Frontend | http://114.207.244.86:3000 |
| V1 | http://114.207.244.86 (수정금지) |
| V2 Git | git@github.com:moongoby/newtalk-v2-api-.git |
| 문서 Git | git@github.com:moongoby/project-docs.git |
| 문서 로컬 | /data/project-docs |
| SSH key | /root/.ssh/id_ed25519_newtalk |

## 6. DB 접속

| 구분 | 명령 |
|------|------|
| V1 (읽기전용) | mysql -u pigupuser -p'sbxhr3376*' -h 127.0.0.1 -P 3306 autoda |
| V2 (읽기쓰기) | mysql -u newtalk_v2_user -p(비밀번호 .env.docker 참조) -h 127.0.0.1 -P 3307 newtalk_v2 |

## 7. 작업규칙

- V1 소스/DB 수정 금지 (대표님 승인 없이)
- 수정 전 백업: .bak.YYYYMMDD_HHMMSS
- 커밋 prefix: [R{라운드}-{TASK}] 또는 [DOCS]
- 보고서: /srv/newtalk-v2/docs/reports/{TASK-ID}-report.md
- git commit 시 --trailer 옵션 사용 금지 (git 버전 낮음), -m 또는 -F 사용
- 한국시간(KST) 기준

## 8. 문서 GitHub push 절차

1. cp 보고서 /data/project-docs/newtalk-v2-api/reports/
2. cd /data/project-docs
3. git add newtalk-v2-api/
4. git commit -m "docs: {TASK-ID} 보고서 push ({YYYYMMDD})"
5. git push origin master (실패 시 3회 재시도)
6. git log --oneline -1
7. 위치: https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/reports/{파일명}

## 9. 주요 URL

| 구분 | URL |
|------|-----|
| V2 소스 | https://github.com/moongoby/newtalk-v2-api- |
| 문서 레포 | https://github.com/moongoby/project-docs |
| 보고서 | https://github.com/moongoby/project-docs/tree/master/newtalk-v2-api/reports |
| 인계서 | https://github.com/moongoby/project-docs/blob/master/newtalk-v2-api/handover/HANDOVER.md |

## 10. 테스트 계정

| 역할 | 이메일 |
|------|--------|
| 관리자 | admin@newtalk.kr |
| MD | md@newtalk.kr |
| 구매담당 | purchaser@newtalk.kr |
| 도매 | wholesale@newtalk.kr |
| 소매 | retail@newtalk.kr |
| 외주 | outsource@newtalk.kr |

---
*인계서 작성: 2026-02-24 12:45 KST*
