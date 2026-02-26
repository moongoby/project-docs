# autoda DB goods_detail 조회 (GoodsCode 기준) 보고서

**작성일시:** 2026-02-26 KST  
**DB:** autoda  
**목적:** GoodsCode로 상품명·상세 이미지 URL(GoodsEtc60~64) 조회 방법 정리

---

## 1. 테이블 구조 요약

| 테이블 | GoodsCode | GoodsName | GoodsEtc60~64 | 연동 키 |
|--------|-----------|-----------|---------------|--------|
| **goods** | ✅ varchar(20) | ✅ varchar(50) | ❌ | id (PK) |
| **goods_detail** | ❌ | ❌ | ✅ varchar(100) | goods_id → goods.id |

- `goods_detail`에는 **GoodsCode, GoodsName 컬럼이 없음**. `goods_id`(int)로만 `goods`와 연결됨.
- GoodsCode 기준 조회 시 **반드시 `goods`와 JOIN** 해야 함.

---

## 2. 올바른 쿼리

```sql
SELECT g.GoodsCode, g.GoodsName, d.GoodsEtc60, d.GoodsEtc61, d.GoodsEtc62, d.GoodsEtc63, d.GoodsEtc64
FROM goods g
JOIN goods_detail d ON g.id = d.goods_id
WHERE g.GoodsCode IN ('bl5889k62','bl5894k62','nb3362k62','t17538k62','t17529k62');
```

**잘못된 예 (에러 발생):**

```sql
-- ERROR 1054: Unknown column 'GoodsCode' in 'field list'
SELECT GoodsCode, GoodsName, GoodsEtc60, GoodsEtc61, GoodsEtc62, GoodsEtc63, GoodsEtc64
FROM goods_detail
WHERE GoodsCode IN (...);
```

---

## 3. 실행 결과 (2026-02-26)

| GoodsCode | GoodsName | GoodsEtc60~64 |
|-----------|-----------|---------------|
| bl5889k62 | BL5889K62-케세라 리본 브이넥 레이스 크롭 블라우스 | 600px 이미지 URL 5개 (DO Spaces CDN) |
| bl5894k62 | BL5894K62-차레린 프릴 넥라인 핀턱 블라우 | 동일 패턴 |
| nb3362k62 | NB3362K62-일버투 오버핏 스트라이프 컬러 셔츠 | 동일 패턴 |
| t17529k62 | T17529K62-캘리온 러브미 프린팅 오버핏 맨투맨 | 동일 패턴 |
| t17538k62 | T17538K62-하벨로 하트 레터링 오버핏 반팔 티셔츠 | 동일 패턴 |

- **5건** 모두 조회됨.
- GoodsEtc60~64: `https://newtalk.nyc3.cdn.digitaloceanspaces.com/img/202602/{GoodsCode}-600_1.jpg` 등 600px 썸네일 URL.

---

## 4. 실행 예시 (CLI)

```bash
mysql -u pigupuser -p'autoda비밀번호' autoda -e "
SELECT g.GoodsCode, g.GoodsName, d.GoodsEtc60, d.GoodsEtc61, d.GoodsEtc62, d.GoodsEtc63, d.GoodsEtc64
FROM goods g
JOIN goods_detail d ON g.id = d.goods_id
WHERE g.GoodsCode IN ('bl5889k62','bl5894k62','nb3362k62','t17538k62','t17529k62');
"
```

---

## 5. 참고

- **goods_detail** 주요 컬럼: `gd_id`, `goods_id`, `GoodsOptVal`, `Description`, `GoodsEtc60`~`GoodsEtc74`, `GoodsSortImg1`~`4`, `CoordiGoodsCodes` 등.
- 이미지 URL은 DO Spaces CDN 경로 사용 (`newtalk.nyc3.cdn.digitaloceanspaces.com`).
