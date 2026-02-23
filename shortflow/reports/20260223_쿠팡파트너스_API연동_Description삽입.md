# 쿠팡 파트너스 API 연동 + Description 자동 삽입

**작성일시:** 2026-02-23 18:50 KST  
**작업 유형:** 신규 개발  
**상태:** 완료  
**관련 파일:** `engine/coupang_partners.py`, `scripts/upload_worker.py`, `.env.example`, `.gitignore`

---

## 1. 작업 개요

- 쿠팡 파트너스 Open API 클라이언트 모듈(`engine/coupang_partners.py`) 신규 개발
- `upload_worker.py`의 YouTube 업로드 메타데이터 중 Description에 상품명·파트너스 링크(또는 fallback 문구) 자동 삽입
- API 키 미발급 상태에서도 동작하도록 fallback 처리, 키 발급 후 `.env` 설정만으로 즉시 활성화

## 2. 변경 사항

### 2.1 engine/coupang_partners.py 주요 메서드

| 메서드 | 설명 |
|--------|------|
| `is_available()` | API 사용 가능 여부 (COUPANG_API_ENABLED + ACCESS_KEY + SECRET_KEY) |
| `_generate_hmac(method, url)` | CEA HMAC-SHA256 인증 헤더 생성 (signed-date: GMT %y%m%dT%H%M%SZ) |
| `generate_deeplink(coupang_urls)` | 쿠팡 URL → 파트너스 딥링크 변환 (POST /v1/deeplink) |
| `search_products(keyword, limit)` | 키워드 검색 (GET, 6시간 파일 캐시) |
| `get_best_products(category_id, limit)` | 카테고리 베스트 (GET, 6시간 파일 캐시) |
| `build_description(product_name, partner_link)` | YouTube Description 텍스트 생성 (링크 없으면 fallback 문구) |

### 2.2 HMAC 서명 로직

- path / query 분리 후 메시지: `signed-date + method + path + query_string`
- GMT 기반 signed-date: `strftime('%y%m%d', gmtime()) + 'T' + strftime('%H%M%S', gmtime()) + 'Z'`
- HMAC-SHA256(secret_key, msg) → hexdigest
- 헤더: `CEA algorithm=HmacSHA256, access-key=..., signed-date=..., signature=...`

### 2.3 API 호출 제한 대응

- 검색/베스트: 1시간 10회 제한 → `/data/shortflow/cache/coupang_{key}.json` 파일 캐시, 유효기간 6시간
- 딥링크 생성: 별도 제한 있음 → 과다 호출 시 24시간 정지 가능, 캐싱으로 검색 호출 최소화

### 2.4 Fallback Description 전문

```
{product_name} 리뷰 & 추천

▶ 구매 링크: 상품 검색: 쿠팡에서 '{product_name}' 검색

#쿠팡파트너스 #ShortFlow #패션추천

이 포스팅은 쿠팡 파트너스 활동의 일환으로,
이에 따른 일정액의 수수료를 제공받습니다.
```

### 2.5 upload_worker.py 수정 요약

- `_get_product_name_for_file(file_path)`: DB `get_product_by_code(stem)` 시도 → 실패 시 stem을 상품명으로 사용
- `_build_description_with_coupang(product_name)`: `CoupangPartnersClient` 사용  
  - available 시: `search_products` → 첫 상품 URL → `generate_deeplink` → `build_description(name, shortenUrl)`  
  - unavailable 시: `build_description(name)` 만 호출 (fallback)
- `build_metadata(file_path)`: title = 상품명, description = 위에서 생성한 텍스트, 기존 하드코딩 제거
- dry-run 시 description 프리뷰 로그 추가

### 2.6 .env.example 추가 항목

```env
# === 쿠팡 파트너스 API ===
COUPANG_ACCESS_KEY=
COUPANG_SECRET_KEY=
COUPANG_PARTNER_ID=
COUPANG_API_ENABLED=false
```

### 2.7 캐시 및 .gitignore

- `mkdir -p /data/shortflow/cache`
- `.gitignore`에 `cache/` 추가

## 3. 테스트 결과

### 3.1 모듈 import 및 fallback

```text
API available: False
Fallback description:
린넨 퍼프 셔링 BL 리뷰 & 추천
▶ 구매 링크: 상품 검색: 쿠팡에서 '린넨 퍼프 셔링 BL' 검색
#쿠팡파트너스 #ShortFlow #패션추천
이 포스팅은 쿠팡 파트너스 활동의 일환으로, ...
```

### 3.2 build_metadata Description

- 가상 경로 `/data/styleflow/output/sample_린넨퍼프.mp4`로 `build_metadata` 호출
- `description`에 `쿠팡파트너스` 문구 포함 확인
- 에러 없음

### 3.3 dry-run

- 서버에서 `YOUTUBE_CHANNELS_JSON` 및 후보 MP4 존재 시, dry-run 시 description 프리뷰 로그 출력

## 4. Git 커밋 및 push

- **shortflow:** `engine/coupang_partners.py`, `scripts/upload_worker.py`, `.env.example`, `.gitignore` 변경은 이미 main 브랜치에 반영된 상태로 확인됨.  
  보고서 파일 `docs/reports/20260223_쿠팡파트너스_API연동_Description삽입.md`는 서버(rfree-0009)에서 아래로 추가 커밋 권장:
  ```bash
  cd /data/shortflow
  git add docs/reports/20260223_쿠팡파트너스_API연동_Description삽입.md
  git commit -m "[docs] 쿠팡 파트너스 API 연동 + Description 삽입 보고서"
  git push origin main
  ```
- **project-docs:** 동기화는 Step 7 참고. 보고서 복사 후 project-docs 저장소에 커밋·push.

## 5. 보고서 GitHub 위치

https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/reports/20260223_쿠팡파트너스_API연동_Description삽입.md

## 6. 주의사항 / 후속 작업

- API 키 발급: partners.coupang.com → API 관리 → 키 발급 후 `.env`에 `COUPANG_ACCESS_KEY`, `COUPANG_SECRET_KEY`, `COUPANG_PARTNER_ID`, `COUPANG_API_ENABLED=true` 설정
- 승인 조건: 누적 수익 약 10만원 이상 또는 활발한 채널 운영, 1~3 영업일 소요
- API 미승인 상태에서도 시스템은 fallback Description으로 정상 동작
