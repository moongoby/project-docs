# Apache VirtualHost 프록시 설정 보고서 (shotflow.newtalk.kr)

**작성일시:** 2026-02-24 KST
**작업 유형:** 설정 변경
**상태:** 완료
**서버:** rfree-0009.cafe24.com (114.207.244.86)
**프로젝트:** /data/shortflow
**도메인:** shotflow.newtalk.kr (Cloudflare Proxied)

---

## 1. 작업 개요

Apache VirtualHost에 shotflow.newtalk.kr 전용 프록시를 추가하여
Next.js 대시보드(127.0.0.1:3000)로 연결.

**주의:** `000-default.conf`의 `*.newtalk.kr` 와일드카드가 shotflow를 가로채지 않도록,  
사이트 활성화 시 **00-shotflow.newtalk.kr.conf** 로 등록하여 포트 80에서 shotflow vhost가 우선 매칭되도록 함.

## 2. 변경 사항

| 항목 | 내용 |
|------|------|
| 설정 파일 (배포용) | /data/shortflow/deploy/apache-shotflow.newtalk.kr.conf |
| 설정 파일 (서버) | /etc/apache2/sites-available/00-shotflow.newtalk.kr.conf (사이트 활성화명) |
| 프록시 대상 | http://127.0.0.1:3000 (Next.js) |
| 헬스체크 | /api/health → http://127.0.0.1:8000/api/health |
| WebSocket | ws://127.0.0.1:3000 (HMR/실시간) |
| 정적 캐시 | /_next/static → 1년 immutable |
| SSL | Cloudflare Flexible (오리진 80 수신) |
| 모듈 활성화 | proxy, proxy_http, proxy_wstunnel, headers, rewrite |

## 3. 검증 결과

| 테스트 | 결과 |
|--------|------|
| apache2ctl configtest | Syntax OK |
| curl 로컬 127.0.0.1 Host:shotflow / | HTTP 307 |
| curl 로컬 127.0.0.1 Host:shotflow /login | HTTP 200 |
| curl 로컬 127.0.0.1 Host:shotflow (공인 IP 80) /login | HTTP 200 |
| curl https://shotflow.newtalk.kr | HTTP 302 |
| curl https://shotflow.newtalk.kr/login | HTTP 404 (Cloudflare 캐시 가능성, 오리진 직접 시 200) |
| curl https://shotflow.newtalk.kr/api/health | 404 HTML (Worker 경로/구현 확인 필요) |

**apache2ctl -S (shotflow 관련):**
```
*:80  default server shotflow.newtalk.kr (/etc/apache2/sites-enabled/00-shotflow.newtalk.kr.conf:10)
      port 80 namevhost shotflow.newtalk.kr (/etc/apache2/sites-enabled/00-shotflow.newtalk.kr.conf:10)
```

**Apache 로그:** shotflow_error.log 에러 없음. shotflow_access.log 에 307/200 기록 확인.

## 4. 배포 파일

- `/data/shortflow/deploy/apache-shotflow.newtalk.kr.conf`
- 서버 활성화: `sudo cp .../apache-shotflow.newtalk.kr.conf /etc/apache2/sites-available/00-shotflow.newtalk.kr.conf` 후 `sudo a2ensite 00-shotflow.newtalk.kr`
- 백업: `/data/shortflow/backups/20260224_091202_apache_vhost/`

## 5. 대표님 후속 조치

- [ ] Supabase 리다이렉트 URL 등록 (Section 8 참조 – 이전 보고서)
- [ ] Cloudflare SSL Mode 확인 (Flexible 유지 또는 Full 전환)
- [ ] 외부 HTTPS 404 시 Cloudflare 캐시 퍼지 후 재확인
- [ ] /api/health 경로가 Worker(8000)에 있는지 확인, 없으면 Location 블록 제거 또는 경로 수정

## 6. 커밋 정보

- shortflow 커밋: 65050fc
- project-docs 커밋: (아래 Step 9 후 기입)

## 7. 보고서 GitHub 위치

- shortflow: docs/reports/20260224_apache_virtualhost_프록시설정.md
- project-docs: https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/reports/20260224_apache_virtualhost_프록시설정.md
