# R0-TASK-001 작업 완료 보고서

**문서번호:** NT-V2-R0-TASK-001  
**작업일:** 2026-02-21  
**대상:** 뉴톡 V2 — Laravel 12 프로젝트 초기 생성 및 Docker Compose 구성  

---

## 1. 작업 요약

- **Laravel 12** 프로젝트 초기 생성 완료 (v12.11.2)
- **Docker Compose** 개발 환경 구성 완료
  - PHP 8.3-FPM (커스텀 Dockerfile)
  - MySQL 8.0 (호스트 포트 3307)
  - Redis 7-alpine (호스트 포트 6380)
  - Nginx 1.25-alpine (호스트 포트 8080)
- V1 시스템(80/443/3306)과 포트 충돌 없음 확인
- 4개 컨테이너 정상 기동, Laravel welcome 페이지 200 응답, DB/Redis 연결 정상

---

## 2. 사전 확인 결과 (섹션 3)

| 항목 | 결과 |
|------|------|
| 서버 | rfree-0009.cafe24.com (Ubuntu 20.04.6 LTS) |
| Docker | 28.1.1 |
| Docker Compose | v2.35.1 |
| Git | 2.25.1 |
| PHP (V1) | 8.0.14 (수정 없음) |
| 디스크 /srv | 195GB 여유 |
| V1 포트 | 80, 443 (Apache), 3306 (mariadbd) 사용 중 |
| V2 포트 | 8080 (Nginx), 3307 (MySQL), 6380 (Redis) 사용 |

---

## 3. 컨테이너 상태

| 컨테이너 | 이미지 | 포트 | 상태 |
|----------|--------|------|------|
| newtalk-v2-app | newtalk-v2-app (php:8.3-fpm custom) | 9000 (internal) | Up |
| newtalk-v2-nginx | nginx:1.25-alpine | 8080→80 | Up |
| newtalk-v2-db | mysql:8.0 | 3307→3306 | Up (healthy) |
| newtalk-v2-redis | redis:7-alpine | 6380→6379 | Up |

---

## 4. 접속 정보

| 용도 | 접속 방법 |
|------|-----------|
| V2 웹 | http://114.207.244.86:8080 |
| V2 DB | `mysql -h 127.0.0.1 -P 3307 -u newtalk_v2_user -p newtalk_v2` |
| V1 메인 | http://114.207.244.86 (영향 없음, 200 확인) |
| V1 어드민 | http://114.207.244.87 (본 서버(86)에서 curl 시 연결 실패 — 별도 호스트일 수 있음) |

- DB 비밀번호 등 민감 정보는 `.env.docker` 및 `src/.env`에만 있으며, Git에 커밋되지 않음.

---

## 5. 확인 결과 (섹션 7)

- [x] 4개 컨테이너 정상 기동
- [x] Laravel welcome 페이지 200 응답
- [x] DB 연결 정상 (`migrate:status` 및 호스트에서 MySQL 접속 성공)
- [x] Redis 연결 정상 (cache store redis put 테스트 성공)
- [x] V1 메인(86) 사이트 정상 동작
- [x] 포트 충돌 없음 (80/443/3306=V1, 8080/3307/6380=V2)
- [ ] GitHub 푸시 — 원격 저장소 `newtalk-admin/newtalk-v2-api` 생성 후 `git remote add origin` 및 `git push -u origin main` 필요

---

## 6. 생성된 파일 목록 (구조)

```
/srv/newtalk-v2/
├── docker/
│   ├── nginx/default.conf
│   ├── php/Dockerfile
│   └── mysql/my.cnf
├── src/                    # Laravel 12 프로젝트 루트
│   ├── app/, bootstrap/, config/, database/, public/, resources/, routes/, storage/, tests/
│   ├── .env.example, .gitignore, artisan, composer.json, composer.lock, package.json, phpunit.xml, vite.config.js
│   └── (Laravel 기본 파일들, .env는 Git 미포함)
├── docker-compose.yml
├── .env.docker             # Git 미포함
├── .gitignore
├── README.md
├── backups/
├── docs/reports/
│   └── R0-TASK-001-report.md
└── (commit_msg.txt — 커밋용, 삭제 가능)
```

---

## 7. 이슈/특이사항

1. **Composer create-project 퍼미션**  
   - `./src` 볼륨이 root 소유라, 기본 사용자(www-data)로는 쓰기 실패.  
   - `--user root`로 `composer create-project` 실행 후 `chown -R www-data:www-data /var/www` 적용하여 해결.

2. **Git commit "unknown option trailer"**  
   - 일반 셸에서 `git commit -m "..."` 시 `trailer` 관련 오류 발생.  
   - `env -i HOME="$HOME" PATH="/usr/bin:/bin" git commit -m "..."` 로 최소 환경에서 커밋하여 성공. (전역 훅/alias 가능성 있음.)

3. **V1-B(114.207.244.87)**  
   - 본 서버(86)에서 `curl` 시 응답 없음(000). 별도 호스트이거나 방화벽/네트워크 제한일 수 있음. V1 메인(86)은 정상.

---

## 8. 다음 작업

- **R0-TASK-002:** V1 DB(autoda) 스키마 분석 및 V2 마이그레이션 설계
- GitHub에서 `newtalk-admin/newtalk-v2-api` 저장소 생성 후:
  - `git remote add origin git@github.com:newtalk-admin/newtalk-v2-api.git`
  - `git push -u origin main`
  - `git checkout -b develop && git push -u origin develop`
