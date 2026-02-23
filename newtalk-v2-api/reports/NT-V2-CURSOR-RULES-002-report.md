# NT-V2-CURSOR-RULES-002 완료 보고서
# .cursorrules DB 접속 방법 업데이트

**문서번호:** NT-V2-CURSOR-RULES-002  
**작성일:** 2026-02-21  
**대상:** Cursor AI

---

## 1. 작업 개요
- **목적:** `.cursorrules` 섹션 2(DB 접속)를 새 내용으로 교체.
- **변경 요약:** V1 DB 비밀번호 확인 경로 명시 (① `www` 경로 접속 성공 확인됨, ② `pigup` 경로 참고용), V1 DB 접속 순서 및 `unset DBPW` 안내 추가.

---

## 2. 실행 결과

### 2.1 백업
- **명령:** 서버에서 기존 `.cursorrules` 존재 시 `cp ... .cursorrules.bak.(날짜시간)` 실행.
- **결과:** 백업 명령 정상 실행 (기존 파일 존재 시 백업 생성).

### 2.2 .cursorrules 반영
- **방법:** 워크스페이스에 전체 규칙 파일 작성 후 `scp`로 서버 `/srv/newtalk-v2/.cursorrules`에 업로드.
- **결과:** 업로드 성공.

### 2.3 파일 확인
- **상단 40줄:** 섹션 1·2 포함, 지시서와 동일.
- **줄 수:** `wc -l` → **129줄** (`/srv/newtalk-v2/.cursorrules`).

### 2.4 Git 커밋 (서버)
- **저장소:** `/srv/newtalk-v2`
- **브랜치:** `feature/R0-TASK-002-db-design`
- **커밋:** `[R0-002] chore: .cursorrules DB 접속 방법 업데이트 (V1 경로 확정)`
- **결과:** `1 file changed, 15 insertions(+), 9 deletions(-)` — 커밋 해시 `eba1420`.

---

## 3. 섹션 2 반영 내용 (요약)
- V1 DB: `mysql -u pigupuser -p'<비밀번호>' -h 127.0.0.1 -P 3306 autoda` (읽기 전용).
- 비밀번호 확인: ① `/home/danharoo/www/application/config/database.php` (접속 성공), ② `/home/danharoo/pigup/application/config/database.php` (참고용).
- V2 DB: `mysql -u newtalk_v2_user -p'<비밀번호>' -h 127.0.0.1 -P 3307 newtalk_v2`, 비밀번호는 `.env.docker` 참조.
- V1 접속 순서 4단계 및 작업 후 `unset DBPW` 안내 반영.

---

## 4. 결론
- `.cursorrules` 섹션 2 교체 완료.
- 서버 백업 후 반영, 확인, Git 커밋까지 완료.
- **=== .cursorrules 업데이트 완료 ===**
