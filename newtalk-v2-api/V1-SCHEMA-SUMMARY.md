# 뉴톡 V1 — DB 스키마 요약 (autoda)

- **추출일**: 2026-02-24 KST
- **DB명**: autoda
- **총 테이블 수**: (서버에서 `SHOW TABLES` 실행 후 반영)
- V1 DB는 **읽기 전용**. 스키마 참조·V2 마이그레이션 목적.
- 민감정보 없음 확인 완료.

---

## 전체 테이블 목록

서버에서 아래 명령으로 채움:

```bash
mysql -u pigupuser -p -h 127.0.0.1 -P 3306 autoda -N -e "SHOW TABLES;"
```

| # | 테이블명 |
|---|----------|
| (서버 실행 후 위 출력을 행 단위로 나열) |

---

## 핵심 테이블 구조 (V2 마이그레이션 참조)

아래 핵심 테이블은 서버에서 `DESCRIBE <테이블>`, `SELECT COUNT(*)` 실행 후 구조·행 수를 반영한다.

### Member
- 용도: 회원(소매/도매/관리자 등). V2 users 마이그레이션 소스.
- 서버: `DESCRIBE Member;` / `SELECT COUNT(*) FROM Member;`

### GoodsInfo
- 용도: 상품 마스터. V2 products 연동.
- 서버: `DESCRIBE GoodsInfo;` / `SELECT COUNT(*) FROM GoodsInfo;`

### WholesaleCompany
- 용도: 도매사 정보.
- 서버: `DESCRIBE WholesaleCompany;`

### OrderInfo / OrderDetail
- 용도: 주문·주문 상세.
- 서버: `DESCRIBE OrderInfo;`, `DESCRIBE OrderDetail;`

### GoodsCategory
- 용도: 상품 카테고리.
- 서버: `DESCRIBE GoodsCategory;`

### 기타 핵심 키워드
- 테이블명 패턴: `goods|product|member|user|order|coordi|codi|categ|brand|cart|wish|stock|barcode|company|shop|pay|delivery|coupon|point|review|board|config|admin` 등으로 식별 가능.

---

## 참고
- V1 DB 비밀번호: `/home/danharoo/www/application/config/database.php` 참조 (커밋·문서에 기입 금지)
- 전체 DDL: 서버 `docs/scripts/extract-v1-schema.sh` 또는 수동 `SHOW CREATE TABLE`
- V2 스키마: `docs/DB-SCHEMA.md` (52테이블)
