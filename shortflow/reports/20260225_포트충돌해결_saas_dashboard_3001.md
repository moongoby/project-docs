# saas-dashboard 포트 충돌 해결 보고서 (3000→3001)

**작성일시:** 2026-02-25 11:53 KST
**작업 유형:** 인프라 / 버그 수정 / 배포
**상태:** 완료
**서버:** [SERVER-HOSTNAME] ([SERVER-IP])
**프로젝트:** /data/shortflow

## 1. 문제
- 포트 3000을 newtalk-v2-frontend(기존 쇼핑몰)가 점유
- shortflow-saas-dashboard 컨테이너가 기동 불가
- https://shotflow.newtalk.kr 요청이 쇼핑몰로 전달
- /terms, /privacy가 쇼핑몰 미들웨어에 의해 /login 리다이렉트

## 2. 원인
- docker-compose.yml에서 saas-dashboard가 호스트 포트 3000 사용
- 동일 서버에 newtalk-v2-frontend가 포트 3000을 이미 점유
- 포트 충돌로 saas-dashboard 컨테이너 미기동

## 3. 해결
- docker-compose.yml: saas-dashboard 호스트 포트 3000→3001 변경
- Apache VirtualHost: shotflow.newtalk.kr ProxyPass 127.0.0.1:3000→3001
- Docker no-cache 재빌드 + 재기동
- Apache 리로드

## 4. 변경 파일

| 파일 | 변경 내용 |
|------|----------|
| docker-compose.yml | saas-dashboard ports "3000:3000" → "3001:3000" |
| /etc/apache2/sites-available/00-shotflow.newtalk.kr.conf | ProxyPass 127.0.0.1:3000 → 3001 |

## 5. 포트 구성 (변경 후)

| 포트 | 서비스 | 비고 |
|------|--------|------|
| 3000 | newtalk-v2-frontend | 기존 쇼핑몰 (변경 없음) |
| 3001 | shortflow-saas-dashboard | ShortFlow SaaS 대시보드 |
| 8000 | FastAPI Worker | API |
| 8501 | Streamlit | 내부 모니터링 |
| 5678 | n8n | 워크플로우 |

## 6. 검증 결과

### localhost:3001 (saas-dashboard 직접)
| 경로 | HTTP |
|------|------|
| /login | 200 |
| /register | 200 |
| /terms | 200 |
| /privacy | 200 |

### 외부 (https://shotflow.newtalk.kr)
| 경로 | HTTP |
|------|------|
| /login | 200 |
| /register | 200 |
| /terms | 200 |
| /privacy | 200 |

### 기존 서비스 영향 없음
| 서비스 | 결과 |
|--------|------|
| newtalk.kr (쇼핑몰) | 정상 |
| localhost:3000 | 정상 |

## 7. 백업
- 경로: /data/shortflow/backups/20260225_120000_port_fix/
- docker-compose.yml.bak, 00-shotflow.newtalk.kr.conf.bak

## 8. 보고서 GitHub 위치
- shortflow: docs/reports/20260225_포트충돌해결_saas_dashboard_3001.md
- project-docs: https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/reports/20260225_포트충돌해결_saas_dashboard_3001.md
