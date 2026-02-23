# R1-TASK-004 보고서: 사입 대시보드 API (대표님 전용)

**문서번호**: R1-TASK-004  
**작성일**: 2026-02-22  
**브랜치**: feature/R1-TASK-004-dashboard  

---

## 1. 개요

사입 대시보드 API 6개 엔드포인트 구현 (admin 전용).  
Controller·라우트·시더(선택) 작성 완료. **서버(/srv/newtalk-v2) 반영 후 아래 2~5절을 실제 실행 결과로 채워 넣을 것.**

---

## 2. 생성·수정된 파일 목록

| 구분 | 경로 |
|------|------|
| 신규 | `app/Models/WholesaleProfile.php` |
| 신규 | `app/Http/Controllers/Api/PurchasingDashboardController.php` |
| 신규 | `database/seeders/DashboardTestSeeder.php` |
| 수정 | `routes/api.php` (dashboard/purchasing 라우트 추가) |

---

## 3. route:list 결과

**실행 위치**: `/srv/newtalk-v2`  
**실행 명령**:  
`docker compose --env-file .env.docker exec app php artisan route:clear && php artisan route:list --path=api/dashboard`

```
(서버에서 실행 후 위 명령 출력 결과를 아래에 붙여넣기)
```

---

## 4. curl 테스트 결과

**사전**: admin 토큰 획득 (R1-TASK-001 로그인 API 사용)

```bash
TOKEN=$(curl -s -X POST "http://127.0.0.1:8080/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@newtalk.kr","password":"[REDACTED]"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('token') or d.get('data',{}).get('token',''))")
```

| # | 항목 | 명령 | 기대 | 결과 (서버 실행 후 기입) |
|---|------|------|------|--------------------------|
| 6-1 | summary | `curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8080/api/dashboard/purchasing/summary"` | 200, purchase_orders/this_month/pending_actions | |
| 6-2a | suppliers | `curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8080/api/dashboard/purchasing/suppliers"` | 200, 배열 | |
| 6-2b | suppliers 90d | `curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8080/api/dashboard/purchasing/suppliers?period=90d&sort=order_count"` | 200 | |
| 6-3a | trend | `curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8080/api/dashboard/purchasing/trend"` | 200, labels/datasets | |
| 6-3b | trend 90d | `curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8080/api/dashboard/purchasing/trend?period=90d"` | 200 | |
| 6-4a | recent-orders | `curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8080/api/dashboard/purchasing/recent-orders"` | 200 | |
| 6-4b | recent-orders limit=5 | `curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8080/api/dashboard/purchasing/recent-orders?limit=5"` | 200, 최대 5건 | |
| 6-5 | recent-inbounds | `curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8080/api/dashboard/purchasing/recent-inbounds"` | 200 | |
| 6-6 | alerts | `curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8080/api/dashboard/purchasing/alerts"` | 200, overdue_orders/long_pending/high_defective | |
| 6-7a | 권한 purchaser | purchaser 토큰으로 summary | 403 | |
| 6-7b | 권한 md | md 토큰으로 summary | 403 | |
| 6-7c | 권한 retail | retail 토큰으로 summary | 403 | |
| 6-8 | V1 보호 | `curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86` | 200 | |

---

## 5. Git 커밋 및 푸시

**실행 위치**: `/srv/newtalk-v2`

```bash
git checkout develop && git pull origin develop
git checkout -b feature/R1-TASK-004-dashboard
git add -A
git diff --cached | grep -iE "(password|secret|key|token)" | head -5   # 비어 있어야 함
env -i HOME="$HOME" PATH="/usr/bin:/bin" git commit -m "[R1-004] 사입 대시보드 API - summary, suppliers, trend, alerts"
git push origin feature/R1-TASK-004-dashboard
git log --oneline -1
```

| 항목 | 결과 (실행 후 기입) |
|------|---------------------|
| 커밋 SHA | |
| 푸시 결과 | |

---

## 6. 서버 배포·테스트 순서 (실행용)

1. 워크스페이스가 `/srv/newtalk-v2`가 아니면:  
   `rsync -av --exclude='.git' --exclude='vendor' /root/newtalk-v2/ /srv/newtalk-v2/`
2. `cd /srv/newtalk-v2 && docker compose --env-file .env.docker exec app php artisan route:clear`
3. `php artisan route:list --path=api/dashboard` → 6개 엔드포인트 확인
4. (선택) `php artisan db:seed --class=DashboardTestSeeder`
5. 위 4절 curl 테스트 전 항목 실행 후 표에 결과 기입
6. 5절 Git 명령 실행 후 SHA·푸시 결과 기입

---

## 7. 이슈·특이사항

- **WholesaleProfile**: 시더/발주에서 참조되나 모델 파일이 없어 `app/Models/WholesaleProfile.php` 신규 생성함.
- **suppliers 응답**: `company_name`은 DB에 없어 `shop_name`과 동일 값으로 반환.
- **인증 API**: 로그인 엔드포인트는 R1-TASK-001에서 정의. 해당 경로가 없으면 토큰 획득 단계를 환경에 맞게 조정할 것.

---

## 8. 완료 체크리스트

- [x] PurchasingDashboardController 생성 (메서드 6개)
- [x] routes/api.php에 6개 엔드포인트 등록
- [ ] route:list에서 dashboard/purchasing/* 확인 (서버 실행 후)
- [ ] curl 테스트 전 항목 통과 (서버 실행 후)
- [ ] 기존 라우트(인증/상품/발주·입고) 정상 동작 확인
- [ ] V1 정상 확인 (200)
- [ ] Git 푸시 완료
- [x] 보고서 작성
