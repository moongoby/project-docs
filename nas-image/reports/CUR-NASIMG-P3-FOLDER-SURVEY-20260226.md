# CUR-NASIMG-P3-FOLDER-SURVEY-20260226

**제목:** P3 A컷 선별 설계 — NAS 원본 폴더 사진 수량 조사  
**작성일시:** 2026-02-26 (목) 19:40 KST  
**작업 유형:** P3-FOLDER-SURVEY  
**프로젝트:** https://github.com/moongoby/newtalk-image-auto (main)  
**서버:** NAS [NAS-IP]:[NAS-SSH-PORT], 사용자 newtalk

---

## 1. 목적

P3 A컷 선별 설계를 위해 테스트 대상 코디 폴더별 사진 수량 파악.

- **대상 1:** 시크블랙 0220지윤  
  `/volume1/★제품사진/●모델컷_시크블랙/★26년도 모델컷 원본/2026.2월/0220지윤/`
- **대상 2:** 리엘라 0213 백소예  
  `/volume1/★제품사진/●모델컷_리엘라/2026년도/2월/0213 백소예/`

---

## 2. 코디별 사진 수량

### 2.1 시크블랙 0220지윤

| 코디 | 사진 수(장) |
|------|-------------|
| *(조사 후 기입)* | |

**코디당 사진 수 범위:** 최소 — 장, 최대 — 장, 평균 — 장 *(조사 후 기입)*

### 2.2 리엘라 0213 백소예

| 코디 | 사진 수(장) |
|------|-------------|
| *(조사 후 기입)* | |

**코디당 사진 수 범위:** 최소 — 장, 최대 — 장, 평균 — 장 *(조사 후 기입)*

---

## 3. 파일 확장자 분포

| 대상 | 확장자 | 수량 | 비고 |
|------|--------|------|------|
| 시크블랙 0220지윤 | *(조사 후 기입, 예: HEIC, JPG, PNG)* | | |
| 리엘라 0213 백소예 | *(조사 후 기입)* | | |

---

## 4. 조사 실행 방법

NAS SSH 접속 후 아래 중 한 가지로 실행한다.

```bash
# 방법 A: 스크립트 파이프 (로컬에서)
# Get-Content scripts\nas_p3_folder_survey.sh -Raw | ssh -p 2222 newtalk@[NAS-IP] "bash -s"

# 방법 B: NAS 저장소에서 직접 실행 (repo 최신 pull 후)
ssh -p 2222 newtalk@[NAS-IP]
cd /volume1/뉴톡/newtalk-image-auto
bash scripts/nas_p3_folder_survey.sh
```

실행 출력 전체를 복사하여 아래 **5. 조사 원본 출력** 섹션에 붙여넣고, 위 표(2.1, 2.2, 3)를 채운다.

---

## 5. 조사 원본 출력

*(NAS에서 `scripts/nas_p3_folder_survey.sh` 실행 결과를 아래에 붙여넣기)*

```
(출력 붙여넣기)
```

---

## 6. 참고

- **Private 보고서:** `docs/reports/CUR-NASIMG-P3-FOLDER-SURVEY-20260226.md`
- **Public 보고서:** `project-docs/nas-image/reports/CUR-NASIMG-P3-FOLDER-SURVEY-20260226.md` (동기화 스크립트로 반영)
- **조사 스크립트:** `scripts/nas_p3_folder_survey.sh` — 읽기 전용, 파일 수정/삭제 금지.
