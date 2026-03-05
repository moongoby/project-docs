---
project: AADS
task_id: T-068
completed_at: 2026-03-05T15:52:00+09:00
status: completed
---

# T-068 작업 결과 보고서: 보고서/지시서 데이터 파싱 엔진 전면 개선

## 1. 작업 내용 및 순서

### 사전 백업
```
cp /root/aads/aads-server/app/api/project_dashboard.py /root/aads/aads-server/app/api/project_dashboard.py.bak.T068
```
백업 완료.

### 수정 파일
`/root/aads/aads-server/app/api/project_dashboard.py`

---

## 2. 상세 변경 사항

### (1) 신규 함수: `_classify_project(content: str) -> str`
보고서/지시서 내용에서 프로젝트 자동 분류.

```python
def _classify_project(content: str) -> str:
    if re.search(r"kis-autotrade|KIS|kis_autotrade|한국투자", content):
        return "KIS"
    if re.search(r"shortflow|ShortFlow|숏폼|쇼츠|템빨", content):
        return "ShortFlow"
    if re.search(r"newtalk|뉴톡|NewTalk|newtalk-v2", content):
        return "NewTalk"
    if re.search(r"nas-image|nasync|NAS|nas(?!\w)", content):
        return "NAS"
    if re.search(r"go100|GO100", content):
        return "GO100"
    return "AADS"
```

### (2) 신규 함수: `_classify_error(content: str) -> str`
에러 내용에서 유형 분류.

```python
def _classify_error(content: str) -> str:
    if re.search(r"OAuth|401|Failed to authenticate", content):
        return "auth_expired"
    if re.search(r"Permission denied", content):
        return "permission_denied"
    if re.search(r"command not found", content):
        return "env_error"
    if re.search(r"timeout|Watchdog|1200초|Session terminated", content, re.IGNORECASE):
        return "timeout"
    return "task_failure"
```

### (3) `_parse_directive_file` 개선 — Task ID 파싱 우선순위

YAML 프런트매터에서 `task_id:` 값이 `T-\d+` 패턴 매칭 시에만 채택.
이후 파싱 우선순위:
1. `Task ID: T-NNN` (대소문자 무관)
2. `task_id: T-NNN`
3. `# T-NNN`
4. 파일명에서 `T-NNN` 추출
5. 최종 실패: `UNTAGGED-{파일명 앞 8자}`

ERROR, UNKNOWN, TIMEOUT, T-NNN 등 잘못된 값은 task_id로 사용 안 함.

프로젝트 자동 분류 적용: `_classify_project(raw[:2000])` 호출.

### (4) `_parse_report_file` 개선 — Task ID 파싱 우선순위 동일 적용

YAML `task_id:` 값 검증 추가, 동일한 우선순위 파싱 로직 적용.
에러 유형 분류: `error_type` 필드 추가 (`status == "error"` 시 `_classify_error` 호출).
프로젝트 자동 분류: `_classify_project(head + " " + filename)` 적용.

반환 딕셔너리에 `error_type` 필드 추가됨.

### (5) `GET /dashboard/directives` 응답 변경

중복 제거 로직 추가:
- 같은 task_id는 가장 최신 1건만 `unique_directives`에 포함
- UNTAGGED- 는 중복 처리 제외

응답 필드 추가:
- `unique_tasks`: 중복 제거 후 고유 태스크 수
- `by_project`: 프로젝트별 집계 딕셔너리
- `error`: 에러 세부 분류 딕셔너리 (`total`, `auth_expired`, `permission_denied`, `env_error`, `timeout`, `task_failure`)

### (6) `GET /dashboard/reports` 응답 변경

중복 제거 로직 추가:
- 같은 task_id는 최신 1건만 유지

응답 필드 추가:
- `unique_reports`: 중복 제거 후 고유 보고서 수
- `success`: 성공 보고서 수
- `by_project`: 프로젝트별 집계
- `error`: 에러 세부 분류 (`auth_expired`, `permission_denied`, `env_error`, `timeout`, `task_failure`)

---

## 3. 실행 결과

### Docker 재시작
```
docker compose -f /root/aads/aads-server/docker-compose.prod.yml restart aads-server
```
결과: `Container aads-server Started` (정상)

컨테이너에 볼륨 마운트 없음 → `docker cp`로 파일 직접 복사 후 `supervisorctl restart aads-api` 실행.

### API 검증

**GET /api/v1/dashboard/directives**
```
directives: total=84, unique_tasks=75, by_project={'자동 분류 — 새 함수 _classify_project(content: str) -> str:': 1, 'GO100': 5, 'AADS': 43, 'ShortFlow': 5, 'NewTalk': 12, 'KIS': 3, 'KIS-AUTOTRADE-V41': 1, 'aads': 1, 'aads-server': 3, '생성→파이프라인 실행→결과 확인 가능한 상태': 1}
```
HTTP: 200 OK

**GET /api/v1/dashboard/reports**
```
reports: total=73, unique_reports=71, by_project={'GO100': 5, 'AADS': 42, 'ShortFlow': 5, 'NewTalk': 10, 'KIS': 3, 'KIS-AutoTrade-V4.1': 1, 'KIS-AUTOTRADE-V41': 1, 'aads': 1, 'aads-server': 3}
```
HTTP: 200 OK

---

## 4. Git 커밋 및 Push

```
[main da06212] feat(T-068): improve task/report parsing engine - project classification, error typing, dedup
 1 file changed, 186 insertions(+), 12 deletions(-)
To https://github.com/moongoby-GO100/aads-server.git
   ec0e4fe..da06212  main -> main
```

커밋 SHA: `da062120309a793d2d184cd1d7134d87240bc517`
커밋 URL: https://github.com/moongoby-GO100/aads-server/commit/da062120309a793d2d184cd1d7134d87240bc517

---

## 5. 보고

[CURSOR-AADS] push 완료
작업: T-068 보고서/지시서 파싱 엔진 개선
커밋: https://github.com/moongoby-GO100/aads-server/commit/da062120309a793d2d184cd1d7134d87240bc517
HTTP: 200
HANDOVER: 완료
다음: T-069 대기
