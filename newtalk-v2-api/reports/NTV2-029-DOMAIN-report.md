# NTV2-029 도메인 연결 보고서
**작성일**: 2026-03-06 KST

## 결과
| URL | HTTP 코드 |
|---|---|
| https://v2.newtalk.kr | 307 (Next.js → /login 리다이렉트, 정상) |
| https://v2.newtalk.kr/api/health | 200 {"status":"ok","services":{"database":"ok","redis":"ok"}} |
| http://114.207.244.86 (V1) | 200 (무변경) |
| http://114.207.244.86:3000 (직접) | 307 (Next.js 정상) |
| http://114.207.244.86:8080/api/health (직접) | 200 {"status":"ok"} |

## 주요 발견사항
- 서버는 systemd nginx(비활성)가 아닌 **Apache2**가 포트 80/443을 처리하고 있음
- Nginx 설정(`/etc/nginx/sites-available/v2.newtalk.kr`)도 생성했으나 미사용
- Apache2 VirtualHost로 프록시 구성 완료
  - `/api/` → `http://127.0.0.1:8080` (newtalk-v2-nginx Docker 컨테이너 → Laravel)
  - `/app/` → `http://127.0.0.1:6001` (Reverb WebSocket)
  - `/_next/static/` → `http://127.0.0.1:3000` (Next.js 정적)
  - `/` → `http://127.0.0.1:3000` (Next.js 프론트엔드)
- `00-v2.newtalk.kr.conf` 접두사 사용: `default-ssl.conf`의 `*.newtalk.kr` 와일드카드보다 우선 매칭
- SSL: `/etc/ssl_20250509/ssl.crt` (와일드카드 `*.newtalk.kr`)

## 생성된 파일
- `/etc/nginx/sites-available/v2.newtalk.kr` (nginx 설정 — 미사용, 참고용)
- `/etc/nginx/sites-enabled/v2.newtalk.kr` (심링크)
- `/etc/apache2/sites-available/00-v2.newtalk.kr.conf` (실제 사용)
- `/etc/apache2/sites-enabled/00-v2.newtalk.kr.conf` (심링크)
