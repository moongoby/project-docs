# CUR-GO100-FULL-UNLEASH-001-20260309

[인계 확인]
직전 완료: T-046 (어드민 시그널·리스크+매매 관리+거래 상세)
현재 단계: Phase 8 (30일 모의투자 진행 중)
CEO 지시 적용: D-001, D-002, D-003, D-004, D-005, D-006, D-007

---

## 작업 개요

**Task ID**: T-050
**제목**: 백억이 능력 전면 개방 — Agent Loop 무제한 + V3 활성화 + 모의계좌 실매매 연동 + 환각 방지 시스템
**완료일**: 2026-03-09 KST
**커밋**: 4e7d5d8d
**브랜치**: phase-2c-command-center

---

## 작업 1: Agent Loop 전면 개방

### 변경 전/후

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| MAX_ROUNDS | 5 (하드코딩) | 20 (env: GO100_AGENT_MAX_ROUNDS) |
| MAX_TOOLS_PER_ROUND | 3 (하드코딩) | 10 (env: GO100_AGENT_MAX_TOOLS_PER_ROUND) |

### 수정 파일
- `backend/app/services/go100/ai/agent_core.py` (라인 25-26)
- `.env`: GO100_AGENT_MAX_ROUNDS=20, GO100_AGENT_MAX_TOOLS_PER_ROUND=10, GO100_AGENT_UNLIMITED_MODE=true

### 검증
```
grep "MAX_ROUNDS|MAX_TOOLS|UNLIMITED" .env
GO100_AGENT_MAX_ROUNDS=20
GO100_AGENT_MAX_TOOLS_PER_ROUND=10
GO100_AGENT_UNLIMITED_MODE=true
```

---

## 작업 2: V3 모델 활성화 확인

### 상태 확인 결과
- `data/go100/models/v3/go100_brain_v3_train_result.json`: `active: True` (이미 활성화됨)
- BrainPredictorV3 로드 테스트:
  - `is_active: True`
  - `models_loaded: True`
  - `is_available: True`
  - features: 30개 (V3 피처 세트)
  - AUC: 0.5656 (통합), Q2공격형 0.6092

### 참고
metadata.json 파일들은 root:root 소유로 claudebot이 직접 수정 불가 (권한 제약). 그러나 `brain_predictor_v3.py`가 참조하는 `train_result.json`이 `active: True`로 이미 설정되어 있어 V3 예측기가 정상 동작함.

---

## 작업 3: 모의계좌 실매매 전면 개방 + 실계좌 잠금

### .env 추가 설정

```
GO100_PAPER_TRADING_ENABLED=true
GO100_PAPER_TRADING_UNLIMITED=true      # 세션 수 제한 없음
GO100_LIVE_TRADING_ENABLED=false        # 실계좌 잠금 유지
GO100_LIVE_TRADING_REQUIRES_CEO=true    # 실계좌는 CEO 승인 필요
```

---

## 작업 4: 멀티에이전트 토론 전면 개방

### 변경 사항

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| 토론 라운드 | 3 (하드코딩) | 5 (GO100_DEBATE_ROUNDS 환경변수) |
| DRAW 처리 | DRAW로 종결 | DRAW 2회 이상 시 총사령관 강제 판정 |
| 병렬화 | asyncio.gather (유지) | 각 라운드 Bull/Bear 병렬 실행 유지 |

### 수정 파일
- `backend/app/services/go100/agents/debate.py`
  - `run_debate()` 함수: N라운드 동적 루프로 재작성
  - `num_rounds` 파라미터 추가 (None이면 환경변수 사용)
  - 강제 판정 로직: `draw_count >= 2` 시 confidence 기반 판정
  - 반환값에 `commander_override`, `draw_count`, `total_rounds` 추가

---

## 작업 5: 메모리·개인화 자동 로드

### 구현 위치
- `backend/app/services/go100/ai/agent_core.py` - `run_agent()` 함수 시작 부분

### 동작
1. `get_my_memory` 도구 자동 호출 → 최근 5건 메모리 조회
2. `get_my_preferences` 도구 자동 호출 → 사용자 선호도 조회
3. 결과를 system_prompt_extra에 주입하여 LLM에 컨텍스트 제공
4. 오류 시 예외 없이 건너뜀 (안전한 폴백)

---

## 작업 6: 환각 방지 시스템 구축

### 신규 파일: `backend/app/services/go100/ai/hallucination_guard.py`

```python
class HallucinationGuard:
    # 1층: verify_trade_facts()     - 종목코드/가격/거래시간 검증
    # 2층: double_check_numbers()   - LLM 주장 vs DB 실데이터 비교
    # 3층: paper_trade_first()      - 실계좌 전 모의투자 선행 확인
    # 4층: post_trade_review()      - 24h 후 근거 vs 결과 대조
    # 5층: learn_from_hallucination() - 환각 패턴 메모리 저장
    # 통계: get_hallucination_stats() - 7일/30일 환각 통계
```

### execute_buy / execute_sell 연동
- 두 함수 모두 호출 전 `verify_trade_facts()` 자동 실행
- 종목코드 오류/가격 이상치 → `status: "blocked_hallucination"` 반환하여 매매 차단
- 시간 외 주문 → soft-block (경고 로깅만, 매매는 진행)

### DB 확장 (go100_error_log)

```sql
ALTER TABLE go100_error_log ADD COLUMN IF NOT EXISTS error_type varchar(100);
ALTER TABLE go100_error_log ADD COLUMN IF NOT EXISTS error_category varchar(50) DEFAULT 'SYSTEM';
ALTER TABLE go100_error_log ADD COLUMN IF NOT EXISTS auto_resolved boolean DEFAULT false;
ALTER TABLE go100_error_log ADD COLUMN IF NOT EXISTS resolution_detail jsonb;
```

**실행 결과**: 4개 컬럼 추가 완료 (총 11개 컬럼)

### 환각 일일 리뷰 크론

- 스크립트: `scripts/go100/hallucination_daily_review.py`
- 크론 템플릿: `scripts/go100/go100_hallucination_review.cron`
- 크론 내용: `0 0 * * 1-5 root` (평일 09:00 KST = UTC 00:00)
- 로그: `/var/log/go100/hallucination_review.log`
- **※ /etc/cron.d 설치는 root 실행 필요** (claudebot sudo cp 권한 없음)
  - 설치 명령: `sudo cp scripts/go100/go100_hallucination_review.cron /etc/cron.d/go100_hallucination_review`

---

## 작업 7: 검증 결과

| 항목 | 결과 |
|------|------|
| Agent Loop MAX_ROUNDS=20 | ✅ .env 확인 |
| Agent Loop MAX_TOOLS_PER_ROUND=10 | ✅ .env 확인 |
| V3 모델 is_available | ✅ True |
| PAPER_TRADING_ENABLED=true | ✅ .env 확인 |
| LIVE_TRADING_ENABLED=false | ✅ .env 확인 |
| HallucinationGuard import | ✅ Guard OK |
| verify_trade_facts 단위테스트 | ✅ PASS (정상 종목 통과, 비정상 차단) |
| paper_trade_first 단위테스트 | ✅ PASS (모의투자 경로 안내) |
| go100_error_log error_category 컬럼 | ✅ 존재 확인 |
| go100 서비스 재시작 | ✅ active |
| go100-frontend 서비스 재시작 | ✅ active |
| 크론 /etc/cron.d 등록 | ⚠️ root 실행 필요 (템플릿 준비됨) |

---

## 성공 기준 달성 현황

| 성공 기준 | 달성 여부 |
|-----------|----------|
| Agent Loop MAX_ROUNDS=20, MAX_TOOLS_PER_ROUND=10 확인 | ✅ |
| V3 모델 import 성공, AUC 0.5656 모델 로드 확인 | ✅ (is_available=True) |
| 모의투자 PAPER_TRADING_ENABLED=true, LIVE_TRADING_ENABLED=false | ✅ |
| 환각 방지 HallucinationGuard import 성공 | ✅ |
| verify_trade_facts 단위테스트 PASS | ✅ |
| go100_error_log에 error_category 컬럼 존재 | ✅ |
| 크론 /etc/cron.d/go100_hallucination_review 등록 | ⚠️ root 실행 필요 |
| 서비스 재시작 후 go100, go100-frontend 모두 active | ✅ |

---

## 미완료 항목 (후속 조치 필요)

1. **크론 설치**: root 권한으로 아래 명령 실행 필요
   ```bash
   sudo cp /root/kis-autotrade-v4/scripts/go100/go100_hallucination_review.cron /etc/cron.d/go100_hallucination_review
   sudo chmod 644 /etc/cron.d/go100_hallucination_review
   ```

2. **V3 메타데이터 파일 active=True 업데이트**: root 권한으로 activate_v3_model.py 실행 필요
   ```bash
   python3 scripts/go100/activate_v3_model.py --confirm
   ```
   (단, train_result.json은 이미 active=True로 실매매 예측은 정상 작동)

---

## 커밋 정보

- 커밋 해시: 4e7d5d8d
- 변경 파일: 6개 (780 insertions, 79 deletions)
- 신규 파일: hallucination_guard.py, hallucination_daily_review.py, go100_hallucination_review.cron

---

## 저장 정보
- 서버 경로: /root/project-docs/go100/reports/CUR-GO100-FULL-UNLEASH-001-20260309.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-FULL-UNLEASH-001-20260309.md
- 커밋: (project-docs push 후 기재)
- HTTP 확인: 미확인 (push 후 확인)
- HANDOVER 업데이트: 완료 예정
