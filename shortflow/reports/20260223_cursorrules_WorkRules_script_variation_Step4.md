# 작업 보고서: .cursorrules Work Rules 추가 + script_variation Step 4

**작성일시:** 2026-02-23
**작업 유형:** 설정 변경 / 신규 개발
**상태:** 완료
**관련 파일:**
- `/data/shortflow/.cursorrules` (Work Rules 섹션 추가)
- `/data/shortflow/engine/script_variation.py` (ScriptPhrasesResult, get_phrases_result, signature)
- `/data/shortflow/engine/anti_inauthentic.py` (Layer 2 연동, suggest_script, suggested_script)
- `/data/shortflow/engine/__init__.py` (주석 갱신)

---

## 1. 작업 개요

- **.cursorrules:** 지시된 Work Rules(백업·보고서·Git·.gitignore·배포·디스크·작업 흐름)를 기존 내용 하단에 추가함. 기존 프로젝트 컨텍스트는 삭제하지 않고 유지함.
- **Step 4 script_variation:** Layer 2 스크립트 변주 엔진을 오케스트레이터에 연동하고, 서명(signature) 및 제안 API를 추가하여 재생성 시 스크립트 아키타입·문구까지 함께 제안하도록 함.

## 2. 변경 사항

### 2.1 .cursorrules

- 파일 끝에 `---` 및 `## Work Rules (필수 준수)` 섹션 추가.
- 하위 7개 규칙: (1) 백업 규칙, (2) 보고서 규칙, (3) Git 커밋 규칙, (4) .gitignore 규칙, (5) 배포/실행 규칙, (6) 디스크 주의사항, (7) 작업 흐름 요약.

### 2.2 engine/script_variation.py

- `ScriptPhrasesResult` dataclass 추가: `archetype`, `intro`/`body`/`outro` 리스트, `chosen_intro`/`chosen_body`/`chosen_outro`, `to_dict()`, `signature()`.
- `get_phrases_result(archetype=None, recent_archetypes=None)` 추가: 아키타입 선택 후 인트로/본문/아웃트로 각 1문장 무작위 선택해 `ScriptPhrasesResult` 반환.
- `get_script_signature_only(recent_archetypes=None)` 추가: 서명만 반환하는 편의 메서드.

### 2.3 engine/anti_inauthentic.py

- `ScriptVariation`, `ScriptPhrasesResult` import 및 엔진 `__init__`에서 `self._script = ScriptVariation(logger=...)` 등록.
- `AntiInauthenticInput`에 `recent_script_archetypes: List[str]` 필드 추가 (Layer 2 제외용).
- `AntiInauthenticResult`에 `suggested_script: Optional[Dict[str, Any]]` 추가; `to_dict()`에 반영.
- `evaluate()`: `action == "regenerate"`일 때 `_script.get_phrases_result(recent_archetypes=input_data.recent_script_archetypes)` 호출 후 `suggested_script` 설정.
- `suggest_script(exclude_archetypes=None) -> ScriptPhrasesResult` 메서드 추가.

### 2.4 engine/__init__.py

- 주석에 `script_variation` 포함하도록 갱신.

## 3. 테스트 결과

- 다음 명령으로 import 및 연동 확인:
  ```bash
  cd /data/shortflow
  python3 -c "
  from engine.script_variation import ScriptVariation, ScriptPhrasesResult, ARCHETYPES
  from engine.anti_inauthentic import AntiInauthenticEngine, AntiInauthenticInput, AntiInauthenticResult
  sv = ScriptVariation()
  r = sv.get_phrases_result(recent_archetypes=[])
  print('ScriptVariation OK, archetype=%s signature=%s' % (r.archetype, r.signature()))
  eng = AntiInauthenticEngine()
  res = eng.evaluate(AntiInauthenticInput(layout_signature='x', recent_layouts=['x']*5, recent_scripts=['same']*5))
  print('AntiInauthenticEngine evaluate OK, action=%s score=%s' % (res.action, res.originality_score))
  if res.suggested_script:
      print('suggested_script keys:', list(res.suggested_script.keys()))
  s = eng.suggest_script(exclude_archetypes=[])
  print('suggest_script OK, archetype=%s' % s.archetype)
  print('All imports and flows OK.')
  "
  ```
- 결과: `ScriptVariation OK`, `AntiInauthenticEngine evaluate OK`, `suggested_script keys` 출력, `suggest_script OK`, `All imports and flows OK.` 정상 출력.

## 4. 주의사항 / 후속 작업

- Work Rules의 보고서 경로는 지시문 기준으로 `docs/reports/`로 명시되어 있음. 기존 워크스페이스 규칙은 `reports/`를 사용하므로, 팀 정책에 따라 통일 여부 검토 권장.
- 파이프라인 워커에서 `recent_script_archetypes`를 DB 또는 이력에서 채워 넣어 `evaluate()`에 전달하면, 재생성 시 스크립트 변주가 더 정확히 적용됨.
- Layer 3~6, 8~10(voice_variation, bgm_variation, metadata_variation, upload_pattern, narrative_injection, structural_variation, cross_video_checker)은 추후 Sprint에서 연동 예정.
