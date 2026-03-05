# V1-HOTFIX-001 Report
**작업일**: 2026-03-04
**서버**: rfree-009
**V1 소스**: /home/danharoo/www
**작업자**: NTV2 V1 핫픽스 에이전트

---

## 목적

V1(CodeIgniter) 상품 이미지 관리 기능 두 가지 개선:
1. 이미지 정렬 뷰에서 브라우저 이미지 캐시 버스팅 보장
2. 이미지 정렬 저장 시 `goods_detail.GoodsEtc73` 호스팅 경로 즉시 반영

---

## Step 1 — 사전 조사 결과

| 파일 | 역할 |
|---|---|
| `application/controllers/products.php` | 이미지 정렬 컨트롤러 (주 수정 대상) |
| `application/views/products/goods_img_sorting_test1.php` | 이미지 정렬 뷰 |
| `application/models/goods_m.php` | 상품 모델 |
| `application/controllers/goods_api.php` | API 컨트롤러 (GoodsEtc73 참조) |

**관련 함수:**
- `goods_img_sorting_test1()` — 이미지 정렬 페이지 렌더링 (line 8598)
- `goods_img_sorting_save1()` — 이미지 정렬 저장 (line 8855, **수정 대상**)
- `goods_img_sorting_save2()` — MO 이미지 저장 (line 8895)

---

## Step 2 — 캐시 버스팅

**결과: 이미 적용됨 (기존 코드에 존재)**

`goods_img_sorting_test1.php` 뷰 내 `$img_src` 생성 로직:
```php
$img_src = $img_url.$img_name.'?v='.time();
```

4개 sortable 영역(sortable1~4) 모두 동일 패턴으로 `?v=타임스탬프` 이미 포함.
추가 수정 불필요.

---

## Step 3 — GoodsEtc73 호스팅 경로 즉시 반영

**수정 파일**: `application/controllers/products.php`
**수정 위치**: `goods_img_sorting_save1()` 함수 내, 기존 `$this->db->update('goods_detail', $goods_data)` 직후

### 추가된 코드

```php
// =================================================================
// GoodsEtc73 호스팅 경로 즉시 반영 (2026-03-04)
// =================================================================
$hosting_path = 'https://newtalk.kr/data/files/goods/goodscode/img/' . $data['GoodsCode'] . '/';
$this->db->where('goods_id', $GoodsId);
$this->db->update('goods_detail', array('GoodsEtc73' => $hosting_path));
// =================================================================
```

**경로 기준**: `user_goodscode_img_url` config = `/data/files/goods/goodscode/img/`
**도메인**: `https://newtalk.kr`
**결과**: 이미지 정렬 저장 시 `goods_detail.GoodsEtc73`이 자동으로 newtalk.kr 경로로 갱신됨.

---

## Step 4 — 백업

```
cp /home/danharoo/www/application/controllers/products.php \
   /home/danharoo/www/application/controllers/products.php.bak.20260304
```

백업 파일 생성 확인 완료.

---

## Step 5 — 검증

| 검증 항목 | 결과 |
|---|---|
| PHP 문법 검사 (`php -l`) | `No syntax errors detected` |
| `curl http://localhost/` | HTTP 200 (서버 정상) |
| `curl http://localhost/products/goods_img_sorting_test1` | HTTP 307 (미로그인 리다이렉트 — 정상) |

---

## 주의사항

- DO Spaces 전송 로직 (`digitaloceanApi()`) 미수정
- `goods_img_sorting_save2()` 미수정 (MO 이미지 전용, GoodsEtc73 해당 없음)
- GoodsEtc73이 기존에 다른 값으로 설정된 상품은 저장 시 newtalk.kr 경로로 덮어씌워짐 (의도된 동작)

---

## 변경 파일 목록

| 파일 | 변경 내용 |
|---|---|
| `application/controllers/products.php` | `goods_img_sorting_save1()` GoodsEtc73 UPDATE 추가 |
| `application/controllers/products.php.bak.20260304` | 수정 전 백업 (신규 생성) |
