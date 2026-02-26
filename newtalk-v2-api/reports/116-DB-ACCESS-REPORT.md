# 116서버 MySQL 접속 정보 확인 보고서

**작성일시:** 2026-02-25 KST (화요일)  
**목적:** NAS에서 116서버 DB 폴링을 위한 접속 정보 파악  
**준수:** 비밀번호 등 민감정보는 보고서에 포함하지 않음(실제 값은 대표님께 별도 전달)

---

## 1. DB 호스트·포트·계정 요약

| 항목 | 값 |
|------|-----|
| **DB 호스트** | `114.207.244.86` (외부 호스트, localhost 아님) |
| **DB명** | `autoda` |
| **포트** | `3306` |
| **사용자명** | `pigupuser` |
| **비밀번호** | 확인됨 |

- 설정 파일: `server116/application/config/database.php` (CodeIgniter 기본 DB 설정)
- 활성 연결 그룹: `$active_group = 'default'` → 위 값 적용

---

## 2. 외부 접속 가능 여부

- **현재:** 116 PHP 앱은 `114.207.244.86:3306` MySQL에 접속하도록 설정되어 있음.
- **NAS(183.96.69.193)에서 접속:**  
  MySQL 서버(114.207.244.86) 또는 방화벽에서 **NAS 공인 IP 183.96.69.193**에 대해 3306 포트 원격 접속을 허용해야 함.  
  cafe24 등 호스팅 사용 시, 관리자에서 해당 IP 원격 접속 허용 설정 필요.
- **접속 테스트 예시 (NAS SSH에서):**
  ```bash
  mysql -h 114.207.244.86 -P 3306 -u pigupuser -p autoda -e "SELECT 1;"
  ```
  비밀번호는 대표님께 전달된 값 입력.

---

## 3. contents_msg 테이블 구조 요약

- **역할:** 촬영(컨텐츠) 마스터. 한 건당 촬영 일정 1건.
- **코드 참조:** `Content.php`(shooting_registe_post), `Shooting_m.php`, `Common_m.php`, `Root.php`(settlement_shooting_expenses) 등.

**추정 컬럼 (코드 기준, CREATE TABLE 미비교):**

| 컬럼 | 용도 |
|------|------|
| id | PK, 촬영 ID |
| ShootingDate | 촬영일 |
| ShootingTime | 촬영 시간대 |
| BrandName, MDName | 브랜드·MD명 |
| ModelName, PhotoName, StyleName, PlaceName | 모델/촬영기사/스타일/장소 (ID 또는 복수 ID) |
| ParticipantCnt, MoveHow, Etc | 참여인원, 이동방법, 기타 |
| ShootingTimeTotal, Item1~3, ItemTotal | 촬영시간합, 항목별 비용 등 |
| EtcCost1, EtcCost2, PlaceCost | 기타/장소 비용 |
| CodyCnt | 코디 수 |
| PlaceCost, Created | 장소비, 생성일시 |
| Brand_ShootingTimeTotal, Brand_ShotsCnt, Brand_ItemTotal | 브랜드별 집계 |
| ModelCost_total, PhotoCost_total, StyleCost_total, PlaceCost_total | 비용 합계 |
| status | 정산 상태 (예: 정산대기, E2 등) |

- `cody_msg.shooting_id`가 `contents_msg.id`를 참조.

---

## 4. cody_msg 테이블 구조 요약

- **역할:** 코디 단위. 한 촬영(contents_msg 1건)에 여러 코디(cody_msg 다건).
- **코드 참조:** `Content.php`, `Common_m.php` 등.

**추정 컬럼 (코드 기준):**

| 컬럼 | 용도 |
|------|------|
| id | PK |
| codyCode | 코디 고유 코드 |
| shooting_id | FK → contents_msg.id |
| codyName | 코디 폴더명(경로 형식) |
| Model_shooting_complete_date | 모델 촬영 완료일 |
| codyNumber | 코디 순번 |
| mdMemo | MD 메모 |
| created | 생성일시 |

- 연관: `cody_product_msg`(codyCode, shooting_id), `codyImg_msg`(codyCode, shootingComplete) 등.

---

## 5. 폴더생성 요청용 테이블 존재 여부

- **별도 “폴더생성 요청” 전용 테이블은 없음.**
- 촬영·코디 정보는 **contents_msg + cody_msg**로 관리됨.
- 폴더 경로는 코드에서 조합:
  - 예: `Content.php` — `$codyFolder = shootingDate_model_place/`, 코디/상품 폴더명은 `codyName` 등으로 구성.
  - 실제 파일 경로: `/home/newpigup3/www/data/files/shooting/{cody_id}/` (116 서버 로컬).

NAS에서 “폴더생성”을 하려면 **contents_msg / cody_msg (및 필요 시 cody_product_msg)**를 폴링해 촬영·코디 정보를 읽고, 그에 맞춰 NAS 쪽 폴더를 생성하는 방식이 필요함.  
폴더생성 요청만 저장하는 **신규 테이블**이 필요하면 별도 설계·마이그레이션 필요.

---

## 6. 기타 DB 설정 (참고)

- **Oracle 연결:** `database.php` 내 `oracle`, `oracle_cgi`, `oracle_hanjin` 등 별도 그룹 존재.  
  NAS 폴링 대상은 **MySQL default(autoda)**만 해당.
- **보안 권고:**  
  DB 비밀번호가 `application/config/database.php`에 평문으로 있음.  
  `.env` 또는 환경변수로 이전하고, `database.php`는 환경변수만 참조하도록 변경 권장.  
  `.env`·credentials는 Git 커밋 금지.

---

## 7. 요약 체크리스트

| 항목 | 결과 |
|------|------|
| DB 호스트 | 114.207.244.86 (외부) |
| DB명 | autoda |
| 포트 | 3306 |
| 외부 접속 | NAS IP 허용 시 가능 (설정 필요 여부는 인프라 확인) |
| contents_msg | 촬영 마스터 테이블, 구조 위와 같음 |
| cody_msg | 코디 테이블, shooting_id로 contents_msg와 연결 |
| 폴더생성 전용 테이블 | 없음 (기존 테이블로 폴링 후 NAS에서 폴더 생성 가능) |
