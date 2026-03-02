# Apache VirtualHost 충돌 해결 보고서 (shotflow.newtalk.kr)

**작성일시:** 2026-02-24 KST  
**작업 유형:** 버그 수정 / 설정 변경  
**상태:** 완료  
**서버:** [SERVER-HOSTNAME] ([SERVER-IP])  
**프로젝트:** /data/shortflow  
**도메인:** shotflow.newtalk.kr  

---

## 1. 문제

https://shotflow.newtalk.kr 접속 시 기존 쇼핑몰(shop.newtalk.kr)이 응답(HTTP 302 → /main).  
오리진 내부 `Host: shotflow.newtalk.kr` 테스트는 200 정상.

---

## 2. 진단 결과 (Step 0 출력)

### Step 0-1: Apache VirtualHost 매칭 순서

```
VirtualHost configuration:
*:80                   is a NameVirtualHost
         default server shotflow.newtalk.kr (/etc/apache2/sites-enabled/00-shotflow.newtalk.kr.conf:10)
         port 80 namevhost shotflow.newtalk.kr (/etc/apache2/sites-enabled/00-shotflow.newtalk.kr.conf:10)
         port 80 namevhost [SERVER-IP] (/etc/apache2/sites-enabled/000-default.conf:1)
         port 80 namevhost wp.newtalk.kr (/etc/apache2/sites-enabled/000-default.conf:61)
                 alias wp.newtalk.kr
         port 80 namevhost html.newtalk.kr (/etc/apache2/sites-enabled/000-default.conf:79)
                 alias html.newtalk.kr
         port 80 namevhost newtalk.kr (/etc/apache2/sites-enabled/000-default.conf:114)
                 alias www.newtalk.kr
                 wild alias *.newtalk.kr
*:443                  is a NameVirtualHost
         default server newtalk.kr (/etc/apache2/sites-enabled/default-ssl.conf:19)
         port 443 namevhost newtalk.kr (/etc/apache2/sites-enabled/default-ssl.conf:19)
                 wild alias *.newtalk.kr
         port 443 namevhost ddg.kr (/etc/apache2/sites-enabled/default-ssl.conf:168)
                 wild alias *.ddg.kr
```

### Step 0-2: sites-enabled 파일 목록

```
total 28
drwxrwxr-x 2 root root 4096 Feb 24 09:20 .
lrwxrwxrwx 1 root root   35 Dec 31  2021 000-default.conf.bak_gd_20260213 -> ...
-rw-r--r-- 1 root root 5275 Feb 13 13:17 000-default.conf
lrwxrwxrwx 1 root root   46 Feb 24 09:20 00-shotflow.newtalk.kr.conf -> ../sites-available/00-shotflow.newtalk.kr.conf
-rw-r--r-- 1 root root 8762 Feb 13 13:17 default-ssl.conf
```

### Step 0-3: 오리진 직접 테스트 (Host 헤더)

```
HTTP 200
```

### Step 0-4: 공인IP 직접 테스트 (Cloudflare 우회)

```
HTTP 200
```

### Step 0-5: default VirtualHost 확인

- `000-default.conf`: ServerName [SERVER-IP], wp.newtalk.kr, html.newtalk.kr, newtalk.kr + ServerAlias www.newtalk.kr `*.newtalk.kr` (포트 80).
- `default-ssl.conf`: ServerName newtalk.kr, ServerAlias `*.newtalk.kr` (포트 443), DocumentRoot /home/danharoo/www.

### Step 0-6: 모든 VirtualHost에서 newtalk 검색

```
/etc/apache2/sites-enabled/default-ssl.conf:21:		ServerName newtalk.kr
/etc/apache2/sites-enabled/default-ssl.conf:22:		ServerAlias *.newtalk.kr
...
/etc/apache2/sites-enabled/000-default.conf:126:	ServerName newtalk.kr
/etc/apache2/sites-enabled/000-default.conf:127:	ServerAlias www.newtalk.kr *.newtalk.kr
```

### Step 0-7: shotflow VirtualHost (수정 전)

- `00-shotflow.newtalk.kr.conf`에는 **포트 80** VirtualHost만 존재. **포트 443용 VirtualHost 없음.**

---

## 3. 원인

**포트 443에 shotflow 전용 VirtualHost가 없음.**

- 포트 80: `00-shotflow.newtalk.kr.conf`에 `ServerName shotflow.newtalk.kr`이 있어 정상 매칭.
- 포트 443: `default-ssl.conf`만 있고, 여기 `ServerAlias *.newtalk.kr`이 **모든** `*.newtalk.kr` HTTPS 요청(shotflow.newtalk.kr 포함)을 쇼핑몰 DocumentRoot(/home/danharoo/www)로 처리.
- 외부에서 https://shotflow.newtalk.kr 접속 시 Cloudflare가 오리진 443으로 전달 → default-ssl의 newtalk.kr vhost에 매칭되어 쇼핑몰 응답(302 → /main) 발생.

지시서의 Case A(80 default)가 아닌 **443 쪽 default/wildcard 매칭** 문제.

---

## 4. 해결 조치

1. **백업**  
   - `/data/shortflow/backups/20260224_103946_vhost_fix/`에 sites-available, sites-enabled, `vhosts_before_fix.txt` 저장.

2. **shotflow 443 VirtualHost 추가**  
   - `deploy/apache-shotflow.newtalk.kr.conf`에 `<VirtualHost *:443>` 블록 추가.
   - `ServerName shotflow.newtalk.kr`, 기존 newtalk.kr SSL 인증서 경로 사용  
     (`/etc/ssl_20250509/ssl.crt`, `.key`, `chain_all_ssl.crt`, `chain_ssl.crt`).
   - 프록시: `ProxyPass / http://127.0.0.1:3000/`, WebSocket·`/_next/static`·`/api/health` 동일 유지.
   - 해당 파일을 `/etc/apache2/sites-available/00-shotflow.newtalk.kr.conf`에 복사·반영.

3. **로드 순서**  
   - `00-shotflow.newtalk.kr.conf`가 `default-ssl.conf`보다 먼저 로드되므로, 443에서도 `shotflow.newtalk.kr`이 `*.newtalk.kr`보다 우선 매칭됨.

4. **검증**  
   - `sudo apache2ctl configtest` → Syntax OK  
   - `sudo systemctl reload apache2`  
   - `apache2ctl -S`에서 443 default server가 shotflow.newtalk.kr로 변경된 것 확인.

---

## 5. 검증 결과

| 테스트 | 결과 |
|--------|------|
| apache2ctl configtest | Syntax OK |
| curl 127.0.0.1 Host:shotflow /login | HTTP 200 |
| curl [SERVER-IP] Host:shotflow /login | HTTP 200 |
| curl https://shotflow.newtalk.kr/ | HTTP 307 (→ 로그인 등 정상 리다이렉트) |
| curl https://shotflow.newtalk.kr/login | HTTP 200 |
| 로그인 페이지 내용 | "뉴톡 V2 로그인", "로그인" 등 포함 (Next.js 대시보드) |

---

## 6. 커밋 정보

- shortflow: `bfea905` (fix: Apache vhost shotflow 443 proxy)
- project-docs: `1ca5b99` (docs: shortflow Apache VirtualHost conflict report)

---

## 7. 보고서 GitHub 위치

- shortflow: `docs/reports/20260224_apache_vhost_충돌해결.md`
- project-docs: https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/reports/20260224_apache_vhost_충돌해결.md
