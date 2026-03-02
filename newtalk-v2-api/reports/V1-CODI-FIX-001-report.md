# V1-CODI-FIX-001 코디등록 버그 수정 완료 보고서

- **작업일시**: 2026-02-24
- **대상 서버**: 116 서버 ([SERVER-IP], SSH port 7916)
- **대표님 승인**: 완료 (V1 운영서버 소스 수정)

---

## 1. 수정 대상

| 항목 | 내용 |
|------|------|
| 파일 | `/home/danharoo/www/application/controllers/products.php` |
| 백업 경로 | `/home/danharoo/www/application/controllers/products.php.bak.20260224` |

---

## 2. 수정 내역

### 버그1: 삭제 처리 시 변수명 오류

- **원인**: `array_search(strtolower($code), $CoordiGoodsCodesArr)` 에서 `$code` 가 해당 스코프에 없음. 삭제 처리 구간에서는 `$goodsCode` 사용이 맞음.
- **조치**: `$code` → `$goodsCode` 로 변경 (2곳: 삭제 처리·코디 반영 구간).

### 버그2: 등록 시 중복 체크 없음

- **원인**: 코디 상품코드 추가 시 기존 문자열에 그대로 이어붙여 동일 상품코드가 중복 등록될 수 있음.
- **조치**: 기존 `CoordiGoodsCodes` 를 소문자 배열로 파싱한 뒤 `in_array(strtolower($data['GoodsCode']), $existCodes)` 로 중복 시 추가하지 않도록 수정 (2곳: 약 2644줄·3032줄 부근).

---

## 3. 수정 전 코드 (백업 기준)

### 버그1 (삭제 처리)

```php
3033:                    $key = array_search(strtolower($code), $CoordiGoodsCodesArr);
5022:            $key = array_search(strtolower($code), $CoordiGoodsCodesArr);
```

### 버그2 (등록 구간 2642~2652)

```php
                    $CoordiGoodsCodes = $row->CoordiGoodsCodes;

                    // 없는 상품코드이면 추가
                    $CoordiGoodsCodes .= $CoordiGoodsCodes ? ','.$data['GoodsCode'] : $data['GoodsCode'];

                    $update_data = array(
```

### 버그2 (등록 구간 3034~3044)

```php
                    // 해당 코드가 없으면 코디상품에 해당 상품코드 반영
                    if($key === false)
                    {
                        // 없는 상품코드이면 추가
                        $CoordiGoodsCodes .= $CoordiGoodsCodes ? ','.$data['GoodsCode'] : $data['GoodsCode'];

                        $update_data = array(
```

---

## 4. 수정 후 코드 (현재 서버)

### 버그1 (삭제 처리)

```php
3039:                    $key = array_search(strtolower($goodsCode), $CoordiGoodsCodesArr);
5034:            $key = array_search(strtolower($goodsCode), $CoordiGoodsCodesArr);
```

### 버그2 (등록 구간 2642~2654)

```php
                    $CoordiGoodsCodes = $row->CoordiGoodsCodes;

                    // 없는 상품코드이면 추가
                    $existCodes = array_map('strtolower', array_filter(explode(',', $CoordiGoodsCodes)));

                    if(!in_array(strtolower($data['GoodsCode']), $existCodes)) {

                        $CoordiGoodsCodes .= $CoordiGoodsCodes ? ','.$data['GoodsCode'] : $data['GoodsCode'];

                    }

                    $update_data = array(
```

### 버그2 (등록 구간 3042~3054)

```php
                    if($key === false)
                    {
                        // 없는 상품코드이면 추가
                        $existCodes = array_map('strtolower', array_filter(explode(',', $CoordiGoodsCodes)));

                        if(!in_array(strtolower($data['GoodsCode']), $existCodes)) {

                            $CoordiGoodsCodes .= $CoordiGoodsCodes ? ','.$data['GoodsCode'] : $data['GoodsCode'];

                        }

                        $update_data = array(
```

---

## 5. 적용 단계 요약

| 단계 | 내용 | 결과 |
|------|------|------|
| 1 | 백업 `products.php.bak.20260224` 생성 | 완료 |
| 2 | 버그1 sed 치환 (`$code` → `$goodsCode`) | 완료 |
| 3 | 버그1 확인 grep | 3039, 5034줄 `$goodsCode` 확인 |
| 4 | 버그2 perl 치환 (1줄→3줄, 2곳) | 2645·3045 부근 적용 |
| 5 | 버그2 확인 grep | `existCodes` / `CoordiGoodsCodes .=` 2곳 확인 |
| 6 | PHP-FPM reload | 완료 |
| 7 | V1 Health Check | **200** |

---

## 6. Health Check 결과

```text
$ curl -s -o /dev/null -w '%{http_code}' http://[SERVER-IP]
200
```

- **결과**: HTTP 200 정상.

---

## 7. 롤백 방법

문제 발생 시 서버에서:

```bash
cp -p /home/danharoo/www/application/controllers/products.php.bak.20260224 /home/danharoo/www/application/controllers/products.php
service php7.4-fpm reload   # 또는 해당 PHP-FPM 버전
```

---

*보고서 작성: 2026-02-24 | V1-CODI-FIX-001 수정 완료*
