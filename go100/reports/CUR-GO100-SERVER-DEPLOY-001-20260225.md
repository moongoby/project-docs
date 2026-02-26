# CUR-GO100-SERVER-DEPLOY-001 — 서버 배포 + E2E 테스트 보고서

**작성:** 2026-02-25 KST  
**작업 ID:** CUR-GO100-SERVER-DEPLOY-001  
**우선순위:** P0

---

## 1. 배포 결과

| 단계 | 결과 | 비고 |
|------|------|------|
| 백업 | ✅ 완료 | `/root/backup/server-deploy-20260225-105201` (services-go100, routers-go100, frontend-go100, frontend-next-prev, go100_tables.sql) |
| git pull | ✅ 완료 | phase-2c-command-center, Already up to date |
| DB 마이그레이션 | ✅ 완료 | `params_hash` VARCHAR(12) 추가 (postgres 소유 테이블이라 sudo -u postgres psql로 실행) |
| 프론트 빌드 | ✅ 완료 | tsc exit 0, npm run build 성공 |
| go100 재시작 | ✅ 완료 | active |
| go100-frontend 재시작 | ✅ 완료 | active |
| 헬스체크 | ✅ 완료 | GET /health → status ok, database/redis connected, version 4.1.0 |

**참고:** DB 접속은 `-h 127.0.0.1` 사용 (Peer 인증 회피). 헬스체크는 `/health` 사용 (`/api/go100/health` 미존재).

---

## 2. E2E 테스트 결과

| 항목 | 결과 |
|------|------|
| 1턴 status | 401 (Not authenticated) — 인증 필수 동작 정상 |
| 1턴 scenarios | 미실행 (토큰 미획득) |
| 1턴 required_cagr | 미실행 |
| 2턴 goal_id | 미실행 |
| 2턴 created_cards | 미실행 |
| DB go100_goals | 0건 (현재 목표 없음) |
| DB strategy_cards | 4건 (RETIRED 제외), 카드#20 등 IDEA 활성 |
| DB backtest_runs | 4건, `params_hash` 컬럼 존재·값 NULL, id 기준 최근 4건 조회 정상 |

**토큰:** 세션 테이블 유효 토큰 없음, v1 로그인(이메일/비밀번호 불일치), v4 로그인(Internal server error).  
**권장:** 대표님이 **go100.newtalk.kr** 접속 후 로그인 → 백억이 채팅에서 **"5천만원으로 3년 안에 3억 만들고 싶어"** 입력 → 시나리오 선택(예: "공격적")까지 직접 E2E 테스트.

---

## 3. 성능 측정

| 카드 | HTTP | 소요 | 비고 |
|------|------|------|------|
| #14 (1개월) | 401 | 50ms | 인증 필요, 로그인 후 5~8초 목표 |
| #20 (1개월) | 401 | 51ms | 동일 |

인증 후 실제 백테스트 실행 시 응답 시간은 대표님 테스트 또는 추후 토큰 확보 후 재측정 권장.

---

## 4. 규칙 준수

- kis-v41-* 재시작: **없음** (kis-v41-backend inactive, 미가동)
- 실계좌 사용: **없음**
- 백업: **완료**
- go100_ 접두어 파일/테이블만 수정
- 서비스 재시작: **go100, go100-frontend만** 수행
- 헬스체크: **통과** (/health)
- 보고서: `/root/project-docs/go100/reports/CUR-GO100-SERVER-DEPLOY-001-20260225.md` 저장

---

## 5. 대표님 테스트 안내

1. **go100.newtalk.kr** 접속 후 로그인  
2. **백억이** 채팅에서 메시지 입력: **"5천만원으로 3년 안에 3억 만들고 싶어"**  
3. 시나리오(보수적/균형/공격적 등) 선택  
4. 목표·전략 카드 생성 및 백테스트 플로우 확인  

서버 배포·DB 마이그레이션·서비스 재시작은 완료되었으며, API 인증(401) 및 헬스·DB·프론트 응답은 정상입니다.
