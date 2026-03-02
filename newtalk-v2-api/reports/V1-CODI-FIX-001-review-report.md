# V1 코디 등록 버그 수정 소스 검수 보고서

**검수일시**: 2026-02-24
**검수자**: Claude Code
**검수 대상**: 116 서버 ([SERVER-IP]) - /home/danharoo/www/application/controllers/products.php
**백업 파일**: products.php.bak.20260224

---

## 1. 검수 개요

### 목적
V1 코디 등록 시 발생하는 2가지 버그 수정 사항 검수
- **버그1**: 변수명 오류 (`$code` → `$goodsCode`)
- **버그2**: 중복 코디 상품 등록 방지 로직 누락

### 검수 방법
- 읽기 전용 검수 (수정 금지)
- diff 비교, 코드 리뷰, PHP 문법 검사

---

## 2. Diff 분석 결과

### 2.1 전체 변경 사항 요약

총 **4개 지점** 수정됨:

| 라인 번호 | 변경 유형 | 설명 |
|----------|----------|------|
| 2645 | 버그2 수정 | 중복 체크 로직 추가 (상품 등록 시) |
| 3039 | 버그1 수정 | `$code` → `$goodsCode` 변수명 수정 |
| 3045 | 버그2 수정 | 중복 체크 로직 추가 (상품 수정 시) |
| 5034 | 버그1 수정 | `$code` → `$goodsCode` 변수명 수정 |

### 2.2 Diff 상세 내용

```diff
# 2645줄 - 버그2 수정 (상품 등록 시)
2645c2645,2651
<                     $CoordiGoodsCodes .= $CoordiGoodsCodes ? ','.$data['GoodsCode'] : $data['GoodsCode'];
---
>                     $existCodes = array_map('strtolower', array_filter(explode(',', $CoordiGoodsCodes)));
>
>                     if(!in_array(strtolower($data['GoodsCode']), $existCodes)) {
>
>                         $CoordiGoodsCodes .= $CoordiGoodsCodes ? ','.$data['GoodsCode'] : $data['GoodsCode'];
>
>                     }

# 3033줄 → 3039줄 - 버그1 수정 (변수명 오류)
3033c3039
<                     $key = array_search(strtolower($code), $CoordiGoodsCodesArr);
---
>                     $key = array_search(strtolower($goodsCode), $CoordiGoodsCodesArr);

# 3039줄 → 3045줄 - 버그2 수정 (상품 수정 시)
3039c3045,3051
<                         $CoordiGoodsCodes .= $CoordiGoodsCodes ? ','.$data['GoodsCode'] : $data['GoodsCode'];
---
>                         $existCodes = array_map('strtolower', array_filter(explode(',', $CoordiGoodsCodes)));
>
>                         if(!in_array(strtolower($data['GoodsCode']), $existCodes)) {
>
>                             $CoordiGoodsCodes .= $CoordiGoodsCodes ? ','.$data['GoodsCode'] : $data['GoodsCode'];
>
>                         }

# 5022줄 → 5034줄 - 버그1 수정 (변수명 오류)
5022c5034
<             $key = array_search(strtolower($code), $CoordiGoodsCodesArr);
---
>             $key = array_search(strtolower($goodsCode), $CoordiGoodsCodesArr);
```

---

## 3. 수정 지점 코드 상세 검수

### 3.1 버그1 수정 지점 1 (3039줄)

**위치**: products.php:3039
**수정 내용**: `$code` → `$goodsCode` 변수명 수정

```php
// 수정 전
$key = array_search(strtolower($code), $CoordiGoodsCodesArr);

// 수정 후
$key = array_search(strtolower($goodsCode), $CoordiGoodsCodesArr);
```

**검수 결과**: ✅ **정상**
- 변수명이 정확히 수정됨
- 상위 코드에서 `$goodsCode` 변수가 존재하고 올바른 값 참조

---

### 3.2 버그1 수정 지점 2 (5034줄)

**위치**: products.php:5034
**함수**: `goods_code_check_process()` - 삭제 로직

**수정 내용**: `$code` → `$goodsCode` 변수명 수정

```php
// 수정 전
$key = array_search(strtolower($code), $CoordiGoodsCodesArr);

// 수정 후
$key = array_search(strtolower($goodsCode), $CoordiGoodsCodesArr);
```

**검수 결과**: ✅ **정상**
- POST 입력 변수 `$goodsCode`를 정확히 참조
- 삭제 로직이 정상 작동함

---

### 3.3 버그2 수정 지점 1 (2645줄)

**위치**: products.php:2645
**수정 내용**: 중복 코디 상품 등록 방지 로직 추가

```php
// 수정 전
$CoordiGoodsCodes .= $CoordiGoodsCodes ? ','.$data['GoodsCode'] : $data['GoodsCode'];

// 수정 후
$existCodes = array_map('strtolower', array_filter(explode(',', $CoordiGoodsCodes)));

if(!in_array(strtolower($data['GoodsCode']), $existCodes)) {
    $CoordiGoodsCodes .= $CoordiGoodsCodes ? ','.$data['GoodsCode'] : $data['GoodsCode'];
}
```

**검수 결과**: ✅ **정상**
- 대소문자 구분 없이 중복 체크 (`strtolower`)
- 빈 문자열 필터링 (`array_filter`)
- 중복 시 등록하지 않음

---

### 3.4 버그2 수정 지점 2 (3045줄)

**위치**: products.php:3045
**수정 내용**: 중복 코디 상품 등록 방지 로직 추가 (수정 시)

```php
// 수정 후
$existCodes = array_map('strtolower', array_filter(explode(',', $CoordiGoodsCodes)));

if(!in_array(strtolower($data['GoodsCode']), $existCodes)) {
    $CoordiGoodsCodes .= $CoordiGoodsCodes ? ','.$data['GoodsCode'] : $data['GoodsCode'];
}
```

**검수 결과**: ✅ **정상**
- 2645줄과 동일한 로직 적용 (일관성 유지)
- 상품 수정 시에도 중복 방지 적용됨

---

## 4. PHP 문법 검사 결과

```bash
$ php -l /home/danharoo/www/application/controllers/products.php
No syntax errors detected in /home/danharoo/www/application/controllers/products.php
```

**검수 결과**: ✅ **문법 오류 없음**

---

## 5. goods_code_check_process() 함수 분석

### 5.1 함수 위치
- **시작**: products.php:4958
- **종료**: products.php:5058 (약 100줄)

### 5.2 함수 로직 흐름

```
1. POST 입력값 검증 ($gb, $goodsCode, $coordinateCode)
   ↓
2. 코디 상품코드 존재 확인 (coordinateCode)
   ↓
3. goods_detail 조회 → $CoordiGoodsId, $CoordiGoodsCodes
   ↓
4-A. 추가(A): 중복 체크 → 추가 → UPDATE
4-D. 삭제(D): array_search → array_splice → UPDATE
```

### 5.3 주요 로직 검수

| 구분 | 코드 위치 | 검수 결과 |
|------|----------|----------|
| 입력값 검증 | 4963-4967 | ✅ 정상 (빈 값 체크) |
| 코디 상품 존재 확인 | 4972-4979 | ✅ 정상 |
| 중복 체크 (추가) | 5003-5012 | ✅ 정상 (대소문자 무시) |
| 삭제 로직 | 5028-5034 | ✅ **버그1 수정 완료** |

---

## 6. 추가 검수 항목 (보안 & 잠재적 이슈)

### 6.1 ⚠️ SQL 인젝션 취약점

**심각도**: 🔴 **HIGH**

#### 문제 코드 (products.php:4972)
```php
$sql = "SELECT count(id) as cnt FROM goods WHERE LOWER(GoodsCode) = '".strtolower($coordinateCode)."'";
$query = $this->db->query($sql);
```

#### 문제 코드 (products.php:4983-4990)
```php
$sql = "SELECT
            GS.id, GSD.CoordiGoodsCodes
            FROM
                goods AS		GS LEFT OUTER JOIN
                goods_detail	As GSD ON GS.id = GSD.goods_id
            WHERE
                GS.GoodsCode='{$coordinateCode}'
";
$query = $this->db->query($sql);
```

**문제점**:
- `$coordinateCode`가 POST 입력값이지만 **직접 SQL에 삽입**됨
- CodeIgniter의 Query Builder나 Prepared Statement 미사용
- SQL 인젝션 공격 가능

**권장 수정 방안**:
```php
// 방법1: Query Builder 사용
$this->db->where('LOWER(GoodsCode)', strtolower($coordinateCode));
$query = $this->db->get('goods');

// 방법2: Prepared Statement
$sql = "SELECT count(id) as cnt FROM goods WHERE LOWER(GoodsCode) = ?";
$query = $this->db->query($sql, array(strtolower($coordinateCode)));
```

---

### 6.2 ⚠️ CoordiGoodsCodes 컬럼 길이 제한

**심각도**: 🟡 **MEDIUM**

**예상 문제**:
- `CoordiGoodsCodes`가 varchar(100)일 가능성 (확인 불가)
- 코디 상품코드가 많아지면 **데이터 잘림 발생** 가능
- 예: 상품코드 10자 × 15개 = 150자 (콤마 포함) → 100자 초과

**권장 조치**:
```sql
-- varchar(100) → varchar(500) 또는 TEXT로 변경
ALTER TABLE goods_detail MODIFY COLUMN CoordiGoodsCodes TEXT;
```

**또는 정규화**:
- `coordi_goods_mapping` 테이블 생성하여 1:N 관계로 분리
- 데이터 무결성 향상, 검색 성능 개선

---

### 6.3 ⚠️ $CoordiGoodsId NULL 체크 누락

**심각도**: 🟢 **LOW**

**문제 코드 (products.php:4994-4995)**:
```php
$row = $query->row();
$CoordiGoodsId = $row->id;
```

**문제점**:
- `$row`가 null일 경우 `$row->id`에서 **에러 발생** 가능
- `$CoordiGoodsId`가 null이면 UPDATE가 **전체 레코드**에 적용될 위험

**권장 수정**:
```php
$row = $query->row();
if(!$row || !$row->id) {
    echo '{"info":{"success":false, "text":"코디 상품 정보를 찾을 수 없습니다!"}}';
    exit;
}
$CoordiGoodsId = $row->id;
```

---

### 6.4 ✅ 중복 체크 로직 검증

**검수 결과**: ✅ **정상**

**로직**:
```php
$existCodes = array_map('strtolower', array_filter(explode(',', $CoordiGoodsCodes)));

if(!in_array(strtolower($data['GoodsCode']), $existCodes)) {
    $CoordiGoodsCodes .= $CoordiGoodsCodes ? ','.$data['GoodsCode'] : $data['GoodsCode'];
}
```

**장점**:
- `array_filter`: 빈 문자열 제거
- `strtolower`: 대소문자 무시 중복 체크
- `in_array`: 정확한 중복 검사

**문제 없음**: 정상 작동

---

## 7. 종합 검수 결과

### 7.1 버그 수정 검수 결과

| 버그 번호 | 내용 | 수정 지점 | 검수 결과 |
|----------|------|----------|----------|
| 버그1 | 변수명 오류 (`$code` → `$goodsCode`) | 3039, 5034 | ✅ **수정 완료** |
| 버그2 | 중복 등록 방지 로직 누락 | 2645, 3045 | ✅ **수정 완료** |

### 7.2 보안 취약점 발견

| 취약점 | 심각도 | 상태 | 권장 조치 |
|--------|--------|------|----------|
| SQL 인젝션 | 🔴 HIGH | ⚠️ **미수정** | Query Builder 또는 Prepared Statement 사용 |
| CoordiGoodsCodes 길이 제한 | 🟡 MEDIUM | ⚠️ **미확인** | 컬럼 길이 확인 및 증가 또는 정규화 |
| NULL 체크 누락 | 🟢 LOW | ⚠️ **미수정** | `$row` null 체크 추가 |

---

## 8. 최종 결론

### 8.1 검수 통과 여부

**✅ 조건부 통과**

- **버그 수정 완료**: 버그1, 버그2 모두 정상 수정됨
- **PHP 문법**: 오류 없음
- **로직 정합성**: 정상 작동
- **보안 이슈**: 3개 취약점 발견 (별도 수정 필요)

### 8.2 권장 사항

#### 즉시 조치 필요
1. **SQL 인젝션 수정** (HIGH)
   - `$coordinateCode` 변수를 Prepared Statement로 처리

#### 확인 후 조치
2. **CoordiGoodsCodes 컬럼 길이 확인** (MEDIUM)
   - 현재 길이가 100자 이하인지 확인
   - 부족 시 TEXT로 변경 또는 정규화

#### 선택 사항
3. **NULL 체크 추가** (LOW)
   - `$row` 존재 여부 확인 로직 추가

---

## 9. 검수 환경

- **서버**: 116 서버 ([SERVER-IP]:7916)
- **파일 경로**: /home/danharoo/www/application/controllers/products.php
- **백업 파일**: products.php.bak.20260224
- **PHP 버전**: 확인 필요
- **CodeIgniter 버전**: 확인 필요

---

## 10. 검수자 의견

버그 수정은 정확하게 완료되었으나, **SQL 인젝션 취약점**이 발견되었습니다.
운영 환경에서는 **보안 패치 우선 적용**을 권장합니다.

특히 `goods_code_check_process()` 함수는 사용자 입력값(`$coordinateCode`, `$goodsCode`)을 직접 SQL에 삽입하고 있어, **악의적인 SQL 구문 주입이 가능**합니다.

현재 수정 사항은 **기능 버그 해결**에는 문제없으나, **보안 강화**를 위해 추가 조치가 필요합니다.

---

**검수 완료일**: 2026-02-24
**검수자**: Claude Code (AI Assistant)
**다음 단계**: 보안 패치 적용 후 재검수
