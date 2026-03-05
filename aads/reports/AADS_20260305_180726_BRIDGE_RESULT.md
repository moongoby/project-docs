---
project: AADS
task_id: T-078
completed_at: 2026-03-05T18:10:02+09:00
---

# T-078 실행 결과: classify_project 본문기반 분류 + 파일명 프리픽스 보완

## 지시 파일

파일: `/root/.genspark/directives/running/AADS_20260305_180726_BRIDGE.md`

> **참고**: 지시 파일이 26번째 줄에서 잘려 있었음 (파일 크기 1100 바이트, 내용 불완전).
> GO100 키워드 이후 ShortFlow, NewTalk, NAS, AADS 키워드 목록이 누락됨.
> 기존 `_classify_project` 함수 및 PROJECTS_META 컨텍스트를 참고하여 합리적으로 보완함.

---

## [백업] 실행 결과

```
cp /root/aads/aads-server/app/api/project_dashboard.py \
   /root/aads/aads-server/app/api/project_dashboard.py.bak.T078
```

출력: `백업 완료`

백업 파일 생성 위치: `/root/aads/aads-server/app/api/project_dashboard.py.bak.T078`

---

## [작업내용] 실행 결과

### 대상 파일

`/root/aads/aads-server/app/api/project_dashboard.py`

---

### 변경 1: `_classify_project` 함수 완전 교체 (Line 684)

#### 교체 전 (기존 코드)

```python
def _classify_project(content: str) -> str:
    """보고서/지시서 내용에서 프로젝트 자동 분류 (T-074: 정확도 개선 - AADS 1순위)"""
    content_lower = content.lower()
    # 1순위: AADS 자체 작업 (가장 먼저 체크)
    aads_keywords = ['aads', 'dashboard', 'ceo chat', 'ceo 채팅', '대시보드', 'handover',
                     'tasks 페이지', 'task-history', 'project_dashboard',
                     'cost', '비용', '분석', 'remote', '원격', 'bridge', '브릿지',
                     'memory', 'context api', '계층 메모리', '모델 분기', '실행 엔진']
    if any(kw in content_lower for kw in aads_keywords):
        return 'AADS'
    # 2순위: 프로젝트별 (정확 매칭)
    if any(kw in content_lower for kw in ['kis-autotrade', 'kis_autotrade', '주식', 'autotrade', '백억이']):
        return 'KIS'
    if any(kw in content_lower for kw in ['shortflow', '쇼츠', 'shorts', '템빨', 'youtube short']):
        return 'ShortFlow'
    if any(kw in content_lower for kw in ['newtalk', '뉴톡', 'newtalk_v2']):
        return 'NewTalk'
    if any(kw in content_lower for kw in ['nasync', 'nas동기화']):
        return 'NAS'
    if any(kw in content_lower for kw in ['go100', 'go_100']):
        return 'GO100'
    # 기본값
    return 'AADS'
```

#### 교체 후 (새 코드)

```python
def _classify_project(filename: str, content: str) -> str:
    """파일명 프리픽스 + 보고서 본문 키워드로 프로젝트 자동 분류 (T-078)

    1단계: 파일명 프리픽스 (AADS_ 제외) — KIS_, GO100_, SF_, NT_
    2단계: 보고서 본문 키워드 탐색
    """
    # 1단계: 파일명 프리픽스 (AADS_ 는 제외하여 본문 분류로 진행)
    fname = filename.upper()
    if fname.startswith("KIS_"):
        return "KIS"
    if fname.startswith("GO100_"):
        return "GO100"
    if fname.startswith("SF_"):
        return "ShortFlow"
    if fname.startswith("NT_"):
        return "NewTalk"

    # 2단계: 본문 키워드 탐색
    content_lower = content.lower()

    # KIS
    kis_keywords = ['kis', 'kis-autotrade', 'kis_autotrade', '자동매매', 'desk',
                    '한국투자', '매수', '매도', '백억이', 'autotrade', 'fractal']
    if any(kw in content_lower for kw in kis_keywords):
        return "KIS"

    # GO100
    go100_keywords = ['go100', 'go_100', '단기목표', '100일']
    if any(kw in content_lower for kw in go100_keywords):
        return "GO100"

    # ShortFlow
    sf_keywords = ['shortflow', '쇼츠', 'shorts', '템빨', 'youtube short']
    if any(kw in content_lower for kw in sf_keywords):
        return "ShortFlow"

    # NewTalk
    nt_keywords = ['newtalk', '뉴톡', 'newtalk_v2']
    if any(kw in content_lower for kw in nt_keywords):
        return "NewTalk"

    # NAS
    nas_keywords = ['nasync', 'nas동기화', 'nas 동기화']
    if any(kw in content_lower for kw in nas_keywords):
        return "NAS"

    # 기본값: AADS
    return "AADS"
```

---

### 변경 2: `_parse_directive_file` 내 호출부 업데이트 (Line 835)

#### 변경 전

```python
    # 프로젝트 자동 분류 (project가 기본값이면 내용으로 분류)
    if project == "AADS":
        project = _classify_project(raw[:2000])
```

#### 변경 후

```python
    # 프로젝트 자동 분류 (project가 기본값이면 내용으로 분류)
    if project == "AADS":
        project = _classify_project(filename, raw[:2000])
```

---

### 변경 3: `_parse_report_file` 내 호출부 업데이트 (Line 939)

#### 변경 전

```python
    # 프로젝트 자동 분류 (project가 기본값이면 내용+제목으로 분류)
    if project == "AADS":
        project = _classify_project(head + " " + filename)
```

#### 변경 후

```python
    # 프로젝트 자동 분류 (project가 기본값이면 내용+파일명으로 분류)
    if project == "AADS":
        project = _classify_project(filename, head)
```

---

## 검증: grep 결과

```
$ grep -n "_classify_project" /root/aads/aads-server/app/api/project_dashboard.py

684:def _classify_project(filename: str, content: str) -> str:
835:        project = _classify_project(filename, raw[:2000])
939:        project = _classify_project(filename, head)
```

모든 호출부가 새 시그니처 `_classify_project(filename, content)` 로 업데이트됨. 누락 없음.

---

## 변경 요약

| 항목 | 내용 |
|------|------|
| 대상 파일 | `/root/aads/aads-server/app/api/project_dashboard.py` |
| 백업 파일 | `/root/aads/aads-server/app/api/project_dashboard.py.bak.T078` |
| 변경 함수 | `_classify_project` |
| 시그니처 변경 | `(content: str)` → `(filename: str, content: str)` |
| 1단계 추가 | 파일명 프리픽스: KIS_, GO100_, SF_, NT_ (AADS_ 제외) |
| 2단계 KIS | 'kis', 'kis-autotrade', 'kis_autotrade', '자동매매', 'desk', '한국투자', '매수', '매도', '백억이', 'autotrade', 'fractal' |
| 2단계 GO100 | 'go100', 'go_100', '단기목표', '100일' |
| 2단계 ShortFlow | 'shortflow', '쇼츠', 'shorts', '템빨', 'youtube short' |
| 2단계 NewTalk | 'newtalk', '뉴톡', 'newtalk_v2' |
| 2단계 NAS | 'nasync', 'nas동기화', 'nas 동기화' |
| 기본값 | AADS |
| 호출부 업데이트 | 2곳 (_parse_directive_file, _parse_report_file) |
| 근본 문제 해결 | AADS_* 파일명 때문에 모든 파일이 AADS로 분류되던 문제 해결 |

---

## 비고

지시 파일 `/root/.genspark/directives/running/AADS_20260305_180726_BRIDGE.md` 이 26번째 줄, GO100 키워드 목록 도중에 잘려 있어 (`'100일<span class="cursor">█</span>`) GO100 이후 키워드 목록이 누락됨. 기존 코드와 프로젝트 컨텍스트를 참고하여 ShortFlow, NewTalk, NAS 키워드를 보완함.
