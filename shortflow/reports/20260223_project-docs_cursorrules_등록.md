# project-docs cursorrules 등록 및 동기화 스크립트·README 정비

**작성일시:** 2026-02-23 09:05  
**작업 유형:** 설정 변경  
**상태:** 완료  
**관련 파일:** `/data/project-docs/shortflow/cursorrules.md`, `scripts/sync_shortflow.sh`, `README.md`

---

## 1. 작업 개요

- Step 7: shortflow `.cursorrules`를 project-docs Public 저장소에 `cursorrules.md`로 복사 후 커밋·push
- Step 8: 동기화 스크립트 `sync_shortflow.sh`에 cursorrules 동기화 라인 추가, push 브랜치를 `master`로 통일
- Step 9: README.md를 문서 허브용으로 갱신(프로젝트 표, CONTEXT/Cursor Rules 링크, Claude 사용법, cursorrules 검토 요청 안내)
- Step 10: 최종 커밋·push
- Step 11: 전체 구조 및 Git 로그 확인

## 2. 변경 사항

- **shortflow/cursorrules.md**  
  - `/data/shortflow/.cursorrules` 복사본 등록(검토용)
- **scripts/sync_shortflow.sh**  
  - `cp /data/shortflow/.cursorrules ${DST}/cursorrules.md` 추가  
  - `git push origin main` → `git push origin master`로 수정
- **README.md**  
  - 프로젝트 표에 shortflow/go100, 서버, CONTEXT, Cursor Rules 링크 반영  
  - Claude 새 대화 시작법(raw URL), 보고서 확인 요청, Cursor Rules 검토 요청 예시 문구 추가  
  - 규칙에 cursorrules 검토용 사본 관리 명시

## 3. 테스트 결과

- `find /data/project-docs -name "*.md" -o -name "*.sh"`로 구조 확인 완료
- `shortflow/cursorrules.md` 존재 및 sync 스크립트 실행 권한(`chmod +x`) 적용 확인
- `git push origin master` 성공(6c48c17 등 반영)

## 4. 주의사항 / 후속 작업

- **go100**  
  - `/root/kis-autotrade-v4/.cursorrules` 없음 → `go100/cursorrules.md`는 미생성. 추후 go100용 규칙 생성 시 동일 방식으로 복사·등록 필요.
- **Git 커밋**  
  - 현재 셸 환경에서 한글/괄호 포함 메시지 사용 시 `unknown option 'trailer'` 오류 발생. `env -i` 등으로 환경을 정리하거나 영문 메시지로 커밋하면 정상 동작.
- cursorrules 검토는 아래 raw URL로 확인 가능:  
  `https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/cursorrules.md`
