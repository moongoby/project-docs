# V1-PATH-CHECK-001: V1 이미지 경로 구조 조사 보고서

**문서번호**: V1-PATH-CHECK-001  
**작성일시**: 2026-03-02 21:30 KST  
**목적**: V1-FIX-001 Phase 2 실행 전 newtalk.kr/img/ 실서버 경로 구조 및 DO Spaces URL 패턴 사전 조사  
**규칙**: V1 소스·DB 수정 없음 (읽기 전용 조사)  

---

## 1. 조사 환경

| 항목 | 값 |
|------|-----|
| 서버 | rfree-0009.cafe24.com (114.207.244.86) |
| V1 DB | MySQL (autoda, :3306) |
| V1 소스 경로 | /home/danharoo/www/ |
| DO Spaces 목적 URL | https://newtalk.nyc3.cdn.digitaloceanspaces.com |
| 교체 대상 URL | https://newtalk.kr |
| 조사 기준 | 2026-03-02 |

---

## 2. newtalk.kr/img/ 서버 경로 현황

### 2-1. /home/danharoo/www/img/ 디렉토리

```
총 파일: 1개 (spin.svg)
연도별 디렉토리: 없음 (2024, 2025 없음)
```

**결론**: `/home/danharoo/www/img/` 경로가 사실상 비어 있음.  
DO Spaces에서 이미지를 서빙 중이며, 로컬 서버에 `img/YYYYMM/` 구조가 존재하지 않음.

### 2-2. 실제 이미지 로컬 저장 경로

V1 config.php에서 확인한 경로:
```
user_goodscode_img_dir = /home/danharoo/www/data/files/goods/goodscode/img/
user_goodscode_img_url = /data/files/goods/goodscode/img/
```

`/home/danharoo/www/data/files/goods/goodscode/img/` → 77,637개 항목 존재  
구조: 상품코드별 디렉토리 (예: acc010/, pt1860-600_1/ 등)  
**연도별(YYYYMM) 구조 없음** — DO Spaces와 경로 구조 상이

### 2-3. DO Spaces 이미지 경로 패턴 (V1-FIX-001 보고서 기반)

```
업로드 로직: digitaloceanApi() → $d = "img/".date("Ym")."/"
DO Spaces URL: https://newtalk.nyc3.cdn.digitaloceanspaces.com/img/YYYYMM/파일명
```

예상 치환 후: `https://newtalk.kr/img/YYYYMM/파일명`

---

## 3. V1 DB 이미지 URL 현황 (읽기 전용 조회)

### 3-1. goods_detail.GoodsEtc60 (oceanPath — 서빙 URL)

| URL 타입 | 건수 | 비율 |
|----------|------|------|
| newtalk.kr | 50,920 | 66.0% |
| other (DO Spaces 또는 기타) | 25,007 | 32.4% |
| empty | 1,264 | 1.6% |
| **합계** | **77,191** | |

### 3-2. goods_detail.GoodsEtc73 (설명 HTML — DO URL 포함 가능)

| URL 타입 | 건수 | 비율 |
|----------|------|------|
| newtalk.kr | 46,185 | 59.8% |
| other | 21,477 | 27.8% |
| empty | 9,529 | 12.3% |
| **합계** | **77,191** | |

### 3-3. goods.GoodsImage (대표 이미지)

| URL 타입 | 건수 | 비율 |
|----------|------|------|
| other (단순 파일명 패턴) | 75,361 | 97.6% |
| empty | 1,824 | 2.4% |

`goods.GoodsImage`는 단순 파일명 패턴 (예: `pt1860-600_1.jpg`) — 경로 없이 파일명만 저장됨.

---

## 4. 핵심 발견 및 CEO 확인 필요 사항

### 4-1. 중요 발견

1. **newtalk.kr/img/ 로컬 경로 없음**  
   `/home/danharoo/www/img/` 하위에 연도별 디렉토리 없음.  
   DO Spaces URL을 newtalk.kr로 치환 시 이미지가 404가 될 수 있음.

2. **이미 66% 치환 완료 추정**  
   `GoodsEtc60` 기준 50,920건(66%)이 이미 newtalk.kr URL로 변환되어 있음.  
   나머지 25,007건(32%)이 치환 대상으로 추정.

3. **경로 구조 불일치**  
   - DO Spaces: `img/YYYYMM/파일명`  
   - 로컬 서버: `data/files/goods/goodscode/img/상품코드/파일명`  
   경로 구조가 다르므로 단순 도메인 치환이 불가능할 수 있음.

### 4-2. CEO 확인 필요 사항

| 항목 | 질문 |
|------|------|
| 이미지 서빙 방식 | newtalk.kr/img/ 경로로 nginx 프록시 설정이 되어 있나요? 또는 DO Spaces에서 직접 서빙 중인가요? |
| 66% 기치환 확인 | 이미 newtalk.kr로 치환된 50,920건의 이미지가 실제 서빙되고 있나요? |
| Phase 2 범위 | 나머지 25,007건에 대해 UPDATE 작업을 진행해야 하나요? |
| 이미지 복사 필요 여부 | DO Spaces 이미지를 서버로 복사해야 하는지, 아니면 redirect 설정으로 충분한지요? |

---

## 5. 결론 및 권고

### 현재 상황
- **66%는 이미 치환 완료** — V1-FIX-001 Phase 1~2가 일부 적용된 것으로 보임
- **34%는 아직 DO Spaces 또는 로컬 파일명** — 추가 조사 필요
- **newtalk.kr/img/ 로컬 경로 없음** — Phase 2 실행 전 서빙 방식 확인 필수

### 권고
V1-FIX-001 Phase 2 (UPDATE) 실행 전에 CEO가 다음을 확인해야 합니다:
1. newtalk.kr/img/YYYYMM/ 경로가 실제 서빙되는지 (nginx 설정 확인)
2. 현재 newtalk.kr URL 이미지가 정상 표시되는지 (브라우저 확인)
3. 25,007건 "other"의 실제 URL 패턴 (직접 샘플 조회)

---

## 6. 참고 파일

- V1-FIX-001 보고서: `/srv/newtalk-v2/docs/reports/V1-FIX-001-report.md`
- V1 config: `/home/danharoo/www/application/config/config.php`
- 이미지 로컬 경로: `/home/danharoo/www/data/files/goods/goodscode/img/`

---
완료일시: 2026-03-02 21:30 KST
