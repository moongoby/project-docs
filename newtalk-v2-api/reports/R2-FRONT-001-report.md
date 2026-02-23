# R2-FRONT-001 보고서: Next.js 프로젝트 셋업 + 인증

**문서번호**: R2-FRONT-001  
**작성일**: 2026-02-23  
**브랜치**: feature/R2-FRONT-001-setup  
**참조**: NT-V2-PLAN-002-FINAL, R2-FRONT-001-docker-nginx.md

---

## §1. 생성·수정된 파일 목록

### 문서 (docs/)
| 구분 | 경로 |
|------|------|
| 신규 | docs/NT-V2-PLAN-002-FINAL.md |
| 신규 | docs/NT-V2-ARCHITECTURE.md |
| 신규 | docs/CHANGELOG.md |
| 신규 | docs/scripts/NT-V2-PLAN-002-PART1-PART2-runbook.sh |
| 신규 | docs/R2-FRONT-001-docker-nginx.md |
| 신규 | docs/reports/R2-FRONT-001-report.md |

### 백엔드 (인증 API)
| 구분 | 경로 |
|------|------|
| 신규 | app/Http/Controllers/Api/AuthController.php |
| 수정 | routes/api.php (auth/login, auth/logout, auth/me 추가) |

### 프론트엔드 (frontend/)
| 구분 | 경로 |
|------|------|
| 신규 | frontend/package.json |
| 신규 | frontend/tsconfig.json |
| 신규 | frontend/next.config.ts |
| 신규 | frontend/tailwind.config.ts |
| 신규 | frontend/postcss.config.mjs |
| 신규 | frontend/Dockerfile |
| 신규 | frontend/.env.local.example |
| 신규 | frontend/.gitignore |
| 신규 | frontend/src/app/globals.css |
| 신규 | frontend/src/app/layout.tsx |
| 신규 | frontend/src/app/page.tsx |
| 신규 | frontend/src/app/providers.tsx |
| 신규 | frontend/src/app/(auth)/layout.tsx |
| 신규 | frontend/src/app/(auth)/login/page.tsx |
| 신규 | frontend/src/app/(auth)/register/page.tsx |
| 신규 | frontend/src/app/(admin)/layout.tsx |
| 신규 | frontend/src/app/(admin)/dashboard/page.tsx |
| 신규 | frontend/src/app/(admin)/purchasing/page.tsx |
| 신규 | frontend/src/app/(retail)/layout.tsx |
| 신규 | frontend/src/app/(retail)/feed/page.tsx |
| 신규 | frontend/src/app/(retail)/explore/page.tsx |
| 신규 | frontend/src/app/(retail)/mypage/page.tsx |
| 신규 | frontend/src/app/(wholesale)/layout.tsx |
| 신규 | frontend/src/app/(wholesale)/dashboard/page.tsx |
| 신규 | frontend/src/app/(md)/dashboard/page.tsx |
| 신규 | frontend/src/app/(purchaser)/dashboard/page.tsx |
| 신규 | frontend/src/app/outsource/layout.tsx |
| 신규 | frontend/src/app/outsource/dashboard/page.tsx |
| 신규 | frontend/src/middleware.ts |
| 신규 | frontend/src/lib/api.ts |
| 신규 | frontend/src/lib/utils.ts |
| 신규 | frontend/src/stores/auth-store.ts |
| 신규 | frontend/src/hooks/use-auth.ts |
| 신규 | frontend/src/types/api.ts |
| 신규 | frontend/src/components/layout/retail-layout.tsx |
| 신규 | frontend/src/components/layout/admin-layout.tsx |
| 신규 | frontend/src/components/layout/wholesale-layout.tsx |

---

## §2. Docker 빌드 결과

서버에서 실행 후 기입:

```bash
cd /srv/newtalk-v2
docker compose --env-file .env.docker up -d --build frontend
docker compose --env-file .env.docker ps
docker compose --env-file .env.docker logs frontend --tail 20
```

| 항목 | 결과 |
|------|------|
| frontend 빌드 | (서버 실행 후 기입) |
| frontend 상태 | (Running 확인) |
| 로그 에러 | (없음 확인) |

---

## §3. 접속 테스트 결과

| URL | 기대 HTTP | 결과 |
|-----|-----------|------|
| http://127.0.0.1:3000 | 200 | (서버 실행 후 기입) |
| http://114.207.244.86:3000 | 200 | (서버 실행 후 기입) |
| http://114.207.244.86:3000/login | 200 | (서버 실행 후 기입) |

---

## §4. API 연동 테스트 결과

| 항목 | 방법 | 기대 | 결과 |
|------|------|------|------|
| 로그인 | 브라우저 admin@newtalk.kr / [REDACTED] | 200, /admin/dashboard 리다이렉트 | (서버 실행 후 기입) |
| 대시보드 KPI | /admin/dashboard 접속 | 카드 4개 데이터 표시 | (서버 실행 후 기입) |
| 사입 대시보드 | /admin/purchasing 접속 | 요약·도매처·알림 표시 | (서버 실행 후 기입) |
| 기존 API | curl POST .../api/auth/login | 200 | (서버 실행 후 기입) |
| V1 보호 | curl http://114.207.244.86 | 200 | (서버 실행 후 기입) |

---

## §5. Git 커밋 SHA 및 푸시 결과

서버에서 실행 후 기입:

```bash
cd /srv/newtalk-v2
git add docs/ frontend/ app/Http/Controllers/Api/AuthController.php routes/api.php
git status
git diff --cached | grep -iE "(password|secret|key|token)" || echo "민감정보 없음"
git commit -m "[R2-FRONT-001] Next.js 16 프로젝트 셋업 - 인증, 역할별 라우팅, 관리자 대시보드, Docker 연동"
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin feature/R2-FRONT-001-setup
git log --oneline -1
```

| 항목 | 결과 |
|------|------|
| 커밋 SHA | (서버 실행 후 기입) |
| 푸시 결과 | (성공 확인) |

---

## §6. 완료 체크리스트

- [x] PART 0: 기획서 3개 파일 docs/ 저장
- [x] PART 2: 런북 스크립트 작성 (Git 커밋·푸시는 서버 실행)
- [x] PART 3-1: Next.js 프로젝트 구조 생성, package.json, shadcn/ui 의존성 포함
- [x] PART 3-2: api.ts, auth-store, login/register, layouts, admin/retail/wholesale 대시보드
- [x] PART 3-3: Docker·nginx 안내 문서 (R2-FRONT-001-docker-nginx.md)
- [ ] PART 3-4: http://114.207.244.86:3000 접속 200 (서버 배포 후)
- [ ] PART 3-4: 로그인 → 역할별 리다이렉트 (서버 배포 후)
- [ ] PART 3-4: 관리자 대시보드 R1 API 데이터 표시 (서버 배포 후)
- [ ] PART 3-5: Git 커밋·푸시 (서버에서 실행)
- [x] PART 3-6: 보고서 작성
- [x] PART 3-7: CHANGELOG 업데이트

---

## §7. 참고 사항

- **인증 API**: AuthController 추가로 POST /api/auth/login, POST /api/auth/logout, GET /api/auth/me 제공. User 모델에 `HasApiTokens`(Sanctum) 및 `HasRoles`(Spatie) 필요.
- **프론트 빌드**: 서버에 Node.js 없으면 `docker compose --env-file .env.docker run --rm frontend npm run build` 로 컨테이너 내 빌드 가능.
- **shadcn/ui**: package.json에 radix 의존성 포함. `npx shadcn@latest add button input card` 등은 서버 또는 로컬에서 필요 시 추가 실행.
