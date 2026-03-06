---
project: AADS
task_id: AADS_20260306_193739_BRIDGE
completed_at: 2026-03-06T19:51:27 KST
---

# AADS_20260306_193739_BRIDGE 실행 결과

## 실행 개요

- **지시서 파일**: `/root/.genspark/directives/pending/AADS_20260306_193739_BRIDGE.md`
- **파일 크기**: 96줄
- **실행 일시**: 2026-03-06T19:51:27 KST
- **실행 환경**: /root/aads (서버 68 Claude Code)

---

## 지시서 원문 전체 내용

```
/END %%% 형식의 관계 미정의

기획서는 FLOW의 산출물 형식({PROJECT}-FIND-{SEQ}, {PROJECT}-LAYOUT-{SEQ} 등)을 정의하지만, 이것이 기존 지시서 형식(%%% DIRECTIVE_START/END %%%)과 어떻게 결합되는지 명시하지 않습니다. FIND 단계의 연구 지시를 브릿지를 통해 자동 실행하려면 DIRECTIVE 블록 안에 FLOW 메타데이터(flow_stage: FIND, parent: NTV2-LAYOUT-001)를 포함하는 형식이 필요합니다.

권고: DIRECTIVE 블록 상단에 flow_stage, parent, gate_condition 필드를 추가하는 확장 형식을 정의하세요. 브릿지가 이를 파싱하여 directive_lifecycle 테이블에 기록하면, 교차검증 엔진이 FLOW 단계 준수 여부도 검증할 수 있습니다.

4. 종합 의견

기획서의 핵심 가치인 "지식의 구조화·분리·공유"는 현재 AADS가 250건 이상 태스크를 처리하면서 축적한 경험이 휘발되는 문제를 근본적으로 해결합니다. 특히 Wrap up 강제화와 교훈 공유 허브는 903건 오탐 사태 같은 검증 생략 문제의 재발을 방지하는 구조적 장치입니다.

위 충돌 6건과 보완 4건을 반영하여 기획서를 수정하면, CEO-DIRECTIVES와의 정합성이 확보되고 기존 자동화 파이프라인을 깨뜨리지 않으면서 점진적으로 적용할 수 있습니다. 수정 후 AADS 프로젝트부터 파일럿 적용하여 검증하고, 성공 확인 후 나머지 프로젝트로 확장하는 것을 권고합니다.

수정된 기획서 작성을 지시하시겠습니까, 아니면 현재 기획서를 기반으로 충돌 사항을 반영한 지시서를 바로 발행하시겠습니까?

현행 시스템의 실제 URL 구조를 확인했습니다. 매우 중요한 발견입니다.

각 매니저의 `required_docs`가 이미 프로젝트별로 분리된 GitHub 리포지토리를 참조하고 있습니다:
- AADS: `moongoby-GO100/aads-docs/main/`
- KIS: `moongoby/project-docs/master/kis-autotrade-v4/`
- GO100: `moongoby/project-docs/master/go100/`
- NTV2: `moongoby/project-docs/master/newtalk-v2-api/`
- SF: `moongoby/project-docs/master/shortflow/`
- NAS: `moongoby/project-docs/master/nas-image/`

이 구조를 기반으로 수정 기획서를 작성합니다.

---

# PLN-AADS-001 v2: AADS 업무 흐름 문서화 체계 구축 (수정본)

**문서 ID**: PLN-AADS-001 v2
**작성일**: 2026-03-06
**v1 대비 변경**: 교차검토 13건(충돌 6, 리스크 3, 보완 4) 전량 반영
**실행 대상**: AADS 매니저 (서버 68 Claude Code)
**예상 비용**: $9~15 (Phase 1~4 합산)
**예상 기간**: 6일 (AADS 파일럿 3일 + 확장 3일)

---

## 1부. 배경과 목적

### 1-1. 해결할 문제 4가지

**문서 비대화**: HANDOVER.md 22,000토큰. Claude Code 권장 200줄 대비 초과. 세션마다 컨텍스트 낭비.

**검증 생략**: T-038/039 배포 후 검증 미실시 → Watchdog 오탐 903건 → 디스크 94%→100%. 5분 모니터링이면 방지 가능했음.

**지식 휘발**: CEO-Claude 대화에서 도출된 의사결정(GenSpark 웹훅 불가 → ACK+재전송 채택, AADS 자체 에이전트 전환 → 월 $55로 보류)이 대화 종료 시 소멸.

**프로젝트 간 교훈 단절**: KIS 토큰 만료 에러 9건의 해결 패턴을 NTV2 매니저가 모름. 6개 프로젝트(AADS 235, KIS 237, GO100 155, SF 71, NTV2 45, NAS 10건)가 서로의 실패에서 학습 불가.

### 1-2. 목표

HANDOVER.md 3,000토큰 이내 축소. 모든 작업에 검증 의무화(우선순위별 수준 차등). 의사결정·교훈을 구조화 저장 및 프로젝트 간 공유. 기존 자동화 파이프라인(`claude_exec.sh`, `auto_trigger.sh`, `genspark_bridge.py`, 교차검증)을 깨뜨리지 않고 점진 적용.

### 1-3. 연구 기반

PMBOK/PRINCE2/Agile/CRISP-DM/Double Diamond 비교, Claude Code 공식 메모리 문서, PhotoStructure TPP(6개월 실전 검증), ProductTalk 3계층 메모리, SkillsBench 연구(큐레이팅 지식 → AI 성능 16%p 향상), stormy.ai 1인 CEO+AI 사례.

---

## 2부. FLOW 프레임워크

### 2-1. 4단계 정의

**F — Find (발견)**: 시장분석, 자료분석, 연구. 산출물: `{PROJECT}-FIND-{SEQ}_{제목}.md`. 게이트: CEO "충분한가?" 판단.

**L — Lay out (설계)**: 기획서, 아키텍처, 기술설계. 산출물: `{PROJECT}-LAYOUT-{SEQ}_{제목}.md`. 핵심: **기각된 대안과 이유** 필수 기록. 게이트: CEO 승인.

**O — Operate (실행)**: 작업지시서, 코드 작업. 산출물: 기존 `{PROJECT}-{SEQ}` 넘버링 유지. 상단에 `parent` 필드 추가. DIRECTIVE 블록에 `flow_stage`, `parent`, `gate_condition` 필드 확장.

**W — Wrap up (마무리)**: 검증, 회고, 교훈 등록. 산출물: `{PROJECT}-WRAP-{SEQ}_{제목}.md`.

### 2-2. Wrap up 의무화 수준 (충돌 5 반영)

모든 작업에 동일 수준의 Wrap up을 강제하면 처리 속도가 저하되므로, 우선순위별로 차등 적용합니다.

**P0-CRITICAL / P1-HIGH**: Wrap up 필수. `auto_trigger.sh`에서 WRAP 결과 파일 미존재 시 다음 pending 작업 진입 차단. 검증 체크리스트 전항목 수행.

**P2-NORMAL (예상 소요 15분 초과)**: Wrap up 필수이나 간소화 가능. 최소 "5분 Watchdog 모니터링 + 엔드포인트 HTTP 200 확인"은 반드시 수행.

**P2-NORMAL (예상 소요 15분 이하) / P3-LOW**: `claude_exec.sh` 완료 단계에서 자동으로 5분 대기 + health-check API 호출. 결과를 1줄 로그로 기록. 별도 WRAP 파일 불필요. 단, health-check 실패 시 WRAP 파일 자동 생성 + CEO 알림.

### 2-3. DIRECTIVE 블록 확장 (보완 4 반영)

기존 `%%% DIRECTIVE_START/END %%%` 형식에 FLOW 메타데이터를 추가합니다.

```
%%% DIRECTIVE_START %%%
project: NTV2
task_id: NTV2-040
flow_stage: operate
parent: NTV2-LAYOUT-001
gate_condition: wrap_required
priority: P1-HIGH
...
%%%
```

---

## 실행 결과 및 분석

### 파일 상태 분석

- **파일 총 라인 수**: 96줄
- **파일 시작**: `/END %%% 형식의 관계 미정의` — DIRECTIVE_END 블록과 FLOW 관계 미정의 이슈를 논의하는 내용으로 시작
- **파일 내용**: PLN-AADS-001 v2 기획서 (수정본) 일부 포함
- **파일 상태**: **불완전 (중간에 잘림)** — 2-3절 DIRECTIVE 블록 확장 예시 도중 `%%%`에서 종료됨

### 지시서 성격 분류

이 파일은 명시적 실행 명령(코드 작성, 파일 생성, 서비스 재시작 등)을 포함하지 않는 **기획/분석 문서**입니다. 구체적으로:

1. **FLOW 프레임워크 정의** (Find → Lay out → Operate → Wrap up 4단계)
2. **Wrap up 의무화 수준** (우선순위별 차등 적용 기준)
3. **DIRECTIVE 블록 확장 형식** (flow_stage, parent, gate_condition 필드 추가)
4. **프로젝트별 GitHub 리포지토리 URL 구조 확인**

### 실행 가능 항목 검토 결과

| 항목 | 상태 | 비고 |
|------|------|------|
| FLOW 프레임워크 정의 | 문서 내 기술됨 | 별도 실행 불필요 (기획 내용) |
| Wrap up 의무화 수준 정의 | 문서 내 기술됨 | 별도 실행 불필요 (기획 내용) |
| DIRECTIVE 블록 확장 형식 | 문서 내 기술됨, 파일 잘림 | 완전한 정의 미포함 |
| PLN-AADS-001 v2 전체 기획서 | 불완전 포함 | 1부·2부 일부만 존재 |
| 명시적 실행 명령 | **없음** | 기획 문서로 분류 |

### 결론

이 BRIDGE 파일은 PLN-AADS-001 v2 기획서의 일부를 포함하고 있으나:
1. 파일이 96줄에서 잘려 있어 완전하지 않습니다
2. 명시적 실행 지시(태스크, 코드 작업, 파일 생성 등)가 없습니다
3. FLOW 프레임워크와 DIRECTIVE 블록 확장을 제안하는 기획/분석 내용입니다

**조치**: 파일 내용을 원문 그대로 기록하고, 현재 상태(파일 잘림, 실행 가능 명령 없음)를 보고합니다. CEO 또는 상위 시스템의 추가 지시가 필요합니다.

---

## 작업 디렉토리 현황 (/root/aads)

```
AADS_20260305_080000_KIS_T039_HOURLY_CRON.md
AADS_20260305_080001_KIS_T040_WF_STEP1_RETEST.md
AADS_20260305_080002_KIS_T041_DESK1_LIVE_PREP.md
AADS_20260306_T039_MULTI_SERVER_WATCHDOG.md
aads.conf.bak
aads.conf.current
aads.conf.new
aads-core/
aads-dashboard/
aads-docs/
aads-server/
backups/
claude_exec.sh
containerd-fifo
conversations_standalone.py
logs/
memory_standalone.py
node_modules_global/
pipeline_monitor.sh
__pycache__/
scripts/
test_sample.png
```

---

*이 결과 파일은 AADS_20260306_193739_BRIDGE.md 지시서의 원문 전체와 실행 분석을 원문 그대로 포함합니다.*
