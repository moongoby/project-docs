# CUR-NASIMG-DB-CONN-001-20260225

**제목:** P1 선행 — NAS → 114서버(116 DB) MySQL 접속 테스트  
**작성일시:** 2026-02-25 KST  
**작업 유형:** DB-CONN (P1 선행 조건 확인)  
**목적:** NAS에서 116서버 DB(114.207.244.86:3306) 폴링 가능 여부 확인

---

## 1. 테스트 개요

- **대상:** 114.207.244.86 (116서버 MySQL)
- **포트:** 3306
- **실행 위치:** NAS (SSH: `ssh -p 2222 newtalk@192.168.30.23`)
- **실행 스크립트:** `scripts/nas_mysql_114_connection_test.sh`
- **비밀번호 출처:** server116/application/config/database.php (보고서/커밋에 절대 포함 금지)

---

## 2. 테스트 결과 (실행 후 기입)

### 2.1 STEP 1: 3306 포트 연결

| 항목 | 결과 |
|------|------|
| nc 또는 /dev/tcp | (예: 포트 열림 / 포트 닫힘 / 타임아웃) |
| 비고 | (에러 메시지가 있으면 요약만, 접속 문자열/비밀번호 제외) |

### 2.2 STEP 2: Docker 컨테이너 내 클라이언트/라이브러리

| 항목 | 존재 여부 |
|------|-----------|
| mysql (CLI) | (있음/없음) |
| pymysql | (있음/없음) |
| mysqlclient | (있음/없음) |
| mysql-connector | (있음/없음) |

### 2.3 STEP 3: TCP 소켓 테스트

| 항목 | 결과 |
|------|------|
| TCP 연결 | (성공/실패) |
| MySQL 서버 응답 | (처음 50바이트 요약 또는 N/A) |

### 2.4 STEP 4: MySQL 로그인 및 SELECT 1

| 항목 | 결과 |
|------|------|
| 접속 | (성공/실패) |
| SELECT 1 결과 | (성공 시 1 출력 여부) |
| 실패 시 에러 | (connection refused / timeout / access denied 등, 메시지 요약만) |

---

## 3. 결론 및 다음 조치

- **폴링 가능 여부:** (가능/불가능/추가 설정 필요)
- **필요 시 조치:** (방화벽 개방, Docker에 pymysql 추가, 116 DB 원격 접속 허용 등)

---

## 4. 참고

- GitHub Private: https://github.com/moongoby/newtalk-image-auto
- GitHub Public docs: https://github.com/moongoby/project-docs
- Public 보고서: https://github.com/moongoby/project-docs/blob/master/nas-image/reports/CUR-NASIMG-DB-CONN-001-20260225.md
- project-docs 동기화: 완료
- Private 최종 커밋: 572a35b [P1] NAS->114 MySQL 접속 테스트 스크립트 및 DB-CONN 보고서 추가 (2026-02-25 KST)
