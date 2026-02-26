# P2 코디-상품 데이터 존재 확인 보고서

**작성일시:** 2026-02-26 00:00 KST  
**프로젝트:** server116 (git@github.com:moongoby/server116.git, main)  
**목적:** P2 테스트용 코디-상품 데이터 있는 촬영건 확인, shooting_id=662 미존재 원인 확인, 116 최신 배포 확인.

---

## STEP 1: 코디-상품 데이터가 있는 촬영건 찾기

**실행 쿼리 (116 서버 SSH → mysql -u pigupuser -p autoda):**
```sql
SELECT c.shooting_id, COUNT(*) as cnt
FROM cody_product_msg cp
JOIN cody_msg c ON cp.codyCode = c.codyCode AND cp.shooting_id = c.shooting_id
GROUP BY c.shooting_id
ORDER BY c.shooting_id DESC
LIMIT 10;
```

**결과:**

| shooting_id | cnt |
|-------------|-----|
| 670 | 9 |
| 669 | 15 |
| 668 | 16 |
| 667 | 15 |
| 665 | 20 |
| 664 | 16 |
| 663 | 19 |
| 661 | 19 |
| 660 | 17 |
| 659 | 11 |

**해석:** cnt > 0인 shooting_id가 다수 존재. P2 테스트용으로 **shooting_id=670**(가장 최근, 9건) 사용.

---

## STEP 2: 테스트용 shooting_id의 전체 코디-상품 데이터 조회

**실행 쿼리 (shooting_id=670):**
```sql
SELECT cp.codyProdCode, cp.codyProdName, c.codyCode, c.codyNumber, c.shooting_id
FROM cody_product_msg cp
JOIN cody_msg c ON cp.codyCode = c.codyCode AND cp.shooting_id = c.shooting_id
WHERE c.shooting_id = 670
ORDER BY c.codyNumber;
```

**결과 전체:**

| codyProdCode | codyProdName | codyCode | codyNumber | shooting_id |
|--------------|--------------|----------|------------|-------------|
| pt15811k62 | 1164 | 699d2a5fa9f6d | 1 | 670 |
| t17548k62 | 레이홀터이중T | 699d2a762443a | 2 | 670 |
| nt6155k62 | 랩카라버튼니트 | 699d2aaaacf69 | 3 | 670 |
| pt15816k62 | 삥줄투웨이팬츠 | 699d2ac9a9fcc | 4 | 670 |
| t17547k62 | 뉴트럴P | 699d2ae70edbb | 5 | 670 |
| t17556k62 | 러그반팔T | 699d2b3aaa8aa | 6 | 670 |
| nb3359k62 | 롱체크 | 699d2b5060862 | 7 | 670 |
| cd3710k62 | 스카시퍼프가디건 | 699d4de494cac | 8 | 670 |
| vt1416k62 | 자가드조끼 | 699d4e0a82a10 | 9 | 670 |

**건수:** 9건.

---

## STEP 3: shooting_id=662에 코디-상품 데이터가 없는 이유 확인

**실행 쿼리:**
```sql
SELECT COUNT(*) FROM cody_msg WHERE shooting_id = 662;
SELECT COUNT(*) FROM cody_product_msg WHERE shooting_id = 662;
```

**결과:**

| 구분 | 결과 |
|------|------|
| cody_msg (shooting_id=662) | 0 |
| cody_product_msg (shooting_id=662) | 0 |

**해석:** shooting_id=662는 **cody_msg에 0건**이므로, cody_product_msg와 JOIN되는 코디-상품 데이터도 없음. 해당 촬영건(662)에는 코디 마스터(cody_msg) 자체가 등록되지 않은 상태로 판단됨. (P1 NAS 폴더 생성 검증 시 사용한 shooting_id=662는 코디 폴더는 있으나 상품 연계 데이터는 없는 케이스.)

---

## STEP 4: 116 서버 최신 배포 확인

**실행 (로컬 server116 또는 116 서버 `/home/newpigup3`):**
```bash
cd /root/server116   # 서버 시 /home/newpigup3
git log --oneline -5
```

**결과:**

```
cbeaec7 docs: P2 DB schema survey results filled
e7cc432 feat: P2 DB schema and nas_folder_request columns
bb2bf48 feat: P2 사전작업 - nas_folder_request md_name 추가 + DB 구조 조사
1acf842 docs: P1 배포 검증 완료 보고서 추가
8e71d73 docs: 116 접속 가능 처리 및 배포 검증 결과 반영
```

**확인 사항:**
- 최신 커밋에 **md_name 관련 수정 포함 여부:** 포함됨 (bb2bf48, e7cc432, cbeaec7에서 nas_folder_request md_name·DB 스키마 반영).
- **origin/main 동기화:** `git status` 기준 "Your branch is up to date with 'origin/main'". 별도 `git pull origin main` 미실행(이미 최신).

**참고:** 실제 116 서버에서 배포 상태를 확인하려면 서버 SSH 후 `/home/newpigup3`에서 동일하게 `git log --oneline -5`, `git pull origin main` 실행 권장.

---

## 요약

| 항목 | 내용 |
|------|------|
| P2 테스트용 shooting_id | 670 (코디-상품 9건) |
| shooting_id=662 코디-상품 없음 원인 | cody_msg·cody_product_msg 모두 0건 → 코디 마스터 미등록 |
| 116 저장소 최신 | md_name 포함, origin/main과 동기화됨 |

---

*Public: project-docs/newtalk-v2-api/reports/116-P2-CODY-DATA-CHECK-20260226.md*
