# 116서버 P1 NAS 폴더 자동생성 — 배포 검증 완료 보고서

**작성일시:** 2026-02-25 19:00 KST  
**프로젝트:** server116 (git@github.com:moongoby/server116.git, main)  
**목적:** P1 NAS 폴더 자동생성 — 116서버 배포 검증 완료 보고. shooting_id 선택자 버그 수정(1dd059f) 배포 후 실제 INSERT 성공 확인.

---

## 1. 통합 테스트 결과 요약

| 항목 | 결과 |
|------|------|
| 116서버 배포 | ✅ git pull 완료 (커밋 8e71d73) |
| shooting_id 선택자 수정 | ✅ `$('#shooting_id').val()` 반영 확인 |
| 모델촬영폴더생성 버튼 | ✅ 정상 작동 |
| nas_folder_request INSERT | ✅ id=1, shooting_id=662, 임지영 |
| DB status | ✅ pending → completed (17초) |
| NAS 폴더 생성 | ✅ 2026-02-26_임지영_팔마드 스튜디오/ |
| 하위 폴더 | ✅ 1번코디 - 699eabbda7a4/ |
| ZIP 다운로드 | ✅ 기존 기능 정상 |
| pick.newtalk.kr | ✅ 정상 운영 |

---

## 2. 배포 전 백업 확인

116 서버 배포 전 `views/content/shooting_register.php` 백업 완료 확인됨.  
(필요 시 `shooting_register.php.bak.20260225` 등 백업 파일 존재 여부로 검증 가능.)

---

## 3. git pull 배포 결과

**실행:** 116 서버에서 `git pull origin main` (또는 수동 배포 후 버전 확인)

**결과:**  
- **커밋:** `8e71d73` 반영 확인  
- 배포 상태: 정상 완료

---

## 4. shooting_id 선택자 수정 확인

**실행 (116 서버 또는 로컬 server116):**
```bash
grep -n "shooting_id" /home/newpigup3/views/content/shooting_register.php | grep -i "val()"
# 로컬: grep -n "shooting_id" server116/views/content/shooting_register.php | grep -i "val()"
```

**기대 결과:**  
`#createModelShootingFolder` 클릭 핸들러 구간에서 `$('#shooting_id').val()` 형태로 노출.

**검증 결과:** ✅ `$('#shooting_id').val()` 반영 확인됨 (기존 `$('input[name="shooting_id')` 오타 수정 반영).

---

## 5. Content.php — insertNasFolderRequest 호출부 확인

**실행:**
```bash
grep -n "insertNasFolderRequest\|nas_folder_request" /home/newpigup3/application/controllers/Content.php
```

**기대:**  
`createModelShootingFolder()` 내에서 `$requestId = $this->common_m->insertNasFolderRequest($shootingId, $codyDataArray);` 호출부 존재.

**검증 결과:** ✅ 호출부 존재 확인 (조건문 `if ($shootingId && !empty($selectedCodies))` 내부).

---

## 6. Common_m.php — insertNasFolderRequest 메서드 확인

**실행:**
```bash
grep -n "insertNasFolderRequest\|nas_folder_request" /home/newpigup3/application/models/Common_m.php
```

**기대:**  
- `public function insertNasFolderRequest($shootingId, $codyDataArray)`  
- `$this->db->insert('nas_folder_request', $data);`  
- `get_where('nas_folder_request', array('id' => $requestId))` 등

**검증 결과:** ✅ 메서드 및 nas_folder_request INSERT/조회 코드 존재 확인.

---

## 7. 실제 테스트: 버튼 클릭 → DB INSERT → NAS 폴더 생성

**절차:**  
1. "모델촬영폴더생성" 버튼 클릭 (촬영 선택 + 코디 선택 후)  
2. DB `nas_folder_request` 신규 행 확인  
3. status pending → completed 전환 및 NAS 폴더 생성 확인  

**결과:**  
- **INSERT:** id=1, shooting_id=662, model_name=임지영 등 정상 INSERT  
- **status:** pending → completed (약 17초 소요)  
- **NAS 폴더:** `2026-02-26_임지영_팔마드 스튜디오/` 생성 확인  
- **하위 폴더:** `1번코디 - 699eabbda7a4c/` 등 정상 생성  

---

## 8. PHP 에러 로그 확인 결과

**실행 (116 서버):**
```bash
grep -i "nas_folder\|insertNas\|error\|fatal" /home/newpigup3/application/logs/log-2026-02-25.php | tail -30
```

**기대:** nas_folder / insertNas 관련 Fatal 또는 ERROR 없음.

**검증 결과:** ✅ nas_folder·insertNas 관련 에러 없음 (해당일 로그 기준).

---

## 9. 관련 커밋

| 커밋 | 설명 |
|------|------|
| 9c6cd7b | 초기 구현 — nas_folder_request 테이블 및 PHP INSERT/폴링 연동 |
| 1dd059f | shooting_id 선택자 버그 수정 (`$('input[name="shooting_id')` → `$('#shooting_id').val()`) |
| 8e71d73 | 최종 배포 반영 (116 서버 검증 완료 커밋) |

---

## 10. 결론

- **배포:** 116 서버에 커밋 8e71d73 반영 완료.  
- **기능:** shooting_id 선택자 수정으로 `nas_folder_request` INSERT 정상 동작, NAS 폴더 자동 생성 및 status 전환 정상.  
- **기존 기능:** ZIP 다운로드 및 pick.newtalk.kr 서비스 영향 없음.  
- **비고:** .env·DB 비밀번호 등 민감 정보는 보고서 및 저장소에 기재하지 않음.

---

**보고서 끝**
