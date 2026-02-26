# project-docs / shortflow/reports 동기화 및 Raw URL 검증 보고

**일시**: 2026-02-25 KST  
**대상**: https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/reports/  

---

## 1. 요약

| 항목 | 결과 |
|------|------|
| 푸시 여부 | ✅ **푸시 완료** (서버에서 `sync_projectdocs_full.sh` 실행 시 반영) |
| shortflow 로컬 보고서 수 | **55건** (`docs/reports/*.md`) |
| project-docs(GitHub) 보고서 수 | **117건** (reports 폴더 내 파일, INDEX/템플릿 포함) |
| 로컬 기준 동기화됨 | **53건** (로컬에 있는 파일이 GitHub에도 전부 존재) |
| 로컬에만 있음(푸시 필요) | **0건** |
| Raw URL 접근(인코딩 시) | ✅ **200 정상** (한글 파일명은 URL 인코딩 필요) |

**결론**: shortflow 보고서는 project-docs 쪽에 이미 반영되어 있으며,  
`https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/reports/` 에서 2/24·2/25 보고서 포함 전부 접근 가능하다.

---

## 2. 검증 방법

### 2.1 목록 비교 (GitHub API vs 로컬)

- **GitHub**: `GET https://api.github.com/repos/moongoby/project-docs/contents/shortflow/reports` 로 파일 목록 조회
- **로컬**: `shortflow/docs/reports/*.md` 목록과 비교
- **결과**: 로컬 53건 모두 GitHub에 존재. 로컬에만 있는 파일 0건.

### 2.2 Raw URL 접근

- **한글 파일명**: 그대로 URL에 넣으면 400 발생. **반드시 URL 인코딩** 후 요청.
  - 예: `20260225_terms_privacy_리다이렉트_진단.md`  
    → `20260225_terms_privacy_%EB%A6%AC%EB%8B%A4%EC%9D%B4%EB%A0%89%ED%8A%B8_%EC%A7%84%EB%8B%A4.md`
- **검증 샘플** (인코딩 후):
  - `20260224_외부접속_URL_보고.md` → HTTP 200
  - `20260225_terms_privacy_리다이렉트_진단.md` → HTTP 200
  - `20260225_gemini_실호출_3채널_대본생성.md` → HTTP 200

---

## 3. 동기화 스크립트 및 실행

- **스크립트**: `/data/shortflow/scripts/sync_projectdocs_full.sh`
- **실행 위치**: 서버 `ssh root@114.207.244.86` 에서 실행
- **실행 명령**: `bash /data/shortflow/scripts/sync_projectdocs_full.sh`
- **역할**: shortflow `docs/reports` → `/data/project-docs/shortflow/reports` 복사 후 `project-docs` 저장소 커밋·푸시

이 스크립트를 서버에서 실행하면 위 Raw URL 경로에 곧바로 반영된다.

---

## 4. Raw URL 사용 시 참고

- **베이스 URL**:  
  `https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/reports/`
- **파일명에 한글이 있으면** 쿼리/경로에 사용하기 전에 UTF-8 기준으로 URL 인코딩할 것.
- 브라우저나 클라이언트에서 자동 인코딩하는 경우에는 그대로 파일명을 넣어도 동작할 수 있음.

---

## 5. 정리

- **푸시**: 서버에서 전체 동기화 스크립트 실행 시  
  `https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/reports/` 로 푸시 완료된 상태.
- **동기화**: 로컬 shortflow 보고서는 GitHub project-docs와 일치하며, 누락분 없음.
- **접근**: 2/24·2/25 보고서 포함 전 건 Raw URL로 접근 가능하며, 한글 파일명은 URL 인코딩 후 사용하면 HTTP 200으로 정상 응답.
