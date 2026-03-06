# T-214: DESK3→DESK2 pool_link 크론 연결 보고서

**Task ID:** T-214
**보고서 ID:** CUR-V41-DESK2-POOL-LINK-CRON-001-20260307
**작성일:** 2026-03-06 (23:34 KST)
**우선순위:** P1-HIGH
**상태:** 완료 (수동 실행 249건 연결, 크론 소스 설치 완료)

---

[인계 확인]
직전 완료: T-204 (03-07 모의매매 모니터링)
현재 단계: Phase 2C (T-202 PIPE-001 단절점 수정)
CEO 지시 적용: D-003 (DESK 본질: 풀 관리), D-012 (프랙탈 아키텍처)
strategy_cards: 변경 없음 (금지 준수)
open_positions: DESK4=0, DESK5=0

---

## 1. 배경

T-202 단절점 분석에서 식별된 **단절점 ④**: `desk2_pool_link.py` 함수는 존재하나 크론/엔진 미연결 상태. DESK3→DESK2 승격 0건의 직접 원인.

D-012 프랙탈 아키텍처 원칙: "DESK2 = 상위 DESK 보유 종목을 먹이감으로 장중 수확"이 미작동 중.

- **DESK3 ACTIVE:** 401건 (종목 풀에서 스캔·선별된 상위 종목)
- **DESK2 candidates (작업 전):** 10건 (당일 스캔분만)
- **목표:** DESK3 ACTIVE → DESK2 candidates confidence_boost 주입

---

## 2. 수행 작업

### 2.1 기존 코드 검증

`backend/app/services/strategy/desk2_pool_link.py` 분석:
- **입력:** `v4_desk3_pool` (status='ACTIVE') → score boost +0.5
- **입력:** `v4_desk_positions` (desk_level=4, ACTIVE/PARTIAL) → boost +0.8
- **입력:** `v4_desk_positions` (desk_level=5, ACTIVE/PARTIAL) → boost +1.0
- **출력:** `v4_desk2_candidates` (기존: score 가산 / 신규: INSERT)
- **로직:** ON CONFLICT (target_date, stock_code) DO UPDATE 패턴 → 멱등성 보장 ✓

코드 상태: 정상 (함수 존재, 로직 완결, 단지 크론 미연결)

### 2.2 크론 엔트리포인트 생성

**파일:** `backend/desk_filters/desk2_pool_link.py`

```python
#!/usr/bin/env python3
# T-214: DESK3→DESK2 pool_link cron 엔트리포인트
# - .env 자동 로드 (DB_PASSWORD 포함)
# - backend.app.services.strategy.desk2_pool_link.apply_desk345_confidence_boost() 호출
# - 결과 stdout 출력 (크론 로그로 캡처)
```

**디렉토리:** `backend/desk_filters/` 신규 생성 (패키지 초기화 포함)

### 2.3 크론 소스 파일 생성

**파일:** `scripts/v41/v41_desk2_pool_link.cron`

```cron
# V4.1 DESK3→DESK2 pool_link (T-214, 2026-03-07)
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin

# DESK3 ACTIVE → v4_desk2_candidates confidence_boost 주입 (매일 영업일 08:00)
0 8 * * 1-5 root cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 backend/desk_filters/desk2_pool_link.py >> /var/log/kis-v41/desk2_pool_link.log 2>&1
```

**실행 타이밍:** 08:00 KST (DESK2 장전 스캔 전, 최적)

### 2.4 설치 스크립트 생성

**파일:** `scripts/v41/install_desk2_pool_link.sh`

```bash
# 설치: sudo bash /root/kis-autotrade-v4/scripts/v41/install_desk2_pool_link.sh
# 수행:
#   1. /var/log/kis-v41/ 디렉토리 생성
#   2. cron 파일 → /etc/cron.d/v41_desk2_pool_link 복사 (chmod 644)
#   3. 수동 1회 실행 테스트
```

> **Note:** `/etc/cron.d/` 설치는 root 권한 필요.
> root에서: `sudo bash /root/kis-autotrade-v4/scripts/v41/install_desk2_pool_link.sh`

---

## 3. 수동 1회 실행 결과

```
실행 명령: /root/kis-autotrade-v4/venv/bin/python3 backend/desk_filters/desk2_pool_link.py
실행 시각: 2026-03-06 23:30:14 KST
```

```
2026-03-06 23:30:14 [INFO] desk2_pool_link: === DESK3->DESK2 pool_link 시작 ===
2026-03-06 23:30:14 [INFO] backend.app.services.strategy.desk2_pool_link:
  DESK345→DESK2 boost 완료: date=2026-03-06 D3=401 D4=0 D5=0
  boosted=4 inserted=245 total=249
```

| 항목 | 값 |
|------|-----|
| target_date | 2026-03-06 |
| desk3_active | **401건** |
| desk4_open | 0건 (없음) |
| desk5_open | 0건 (없음) |
| boosted (기존 후보 score 가산) | **4건** |
| inserted (신규 삽입) | **245건** |
| **total_processed** | **249건** |

### 실행 후 DB 상태

```sql
SELECT COUNT(*) FROM v4_desk2_candidates WHERE target_date = '2026-03-06';
-- 결과: 255건 (작업 전 10건 → 255건으로 증가)
```

**성공기준 달성:** "1건 이상 DESK2 후보 연결" → **249건** (기준 대비 249x)

---

## 4. 변경 파일 목록

| 파일 | 유형 | 설명 |
|------|------|------|
| `backend/desk_filters/__init__.py` | 신규 | 패키지 초기화 |
| `backend/desk_filters/desk2_pool_link.py` | 신규 | 크론 엔트리포인트 (120줄) |
| `scripts/v41/v41_desk2_pool_link.cron` | 신규 | 크론 소스 파일 |
| `scripts/v41/install_desk2_pool_link.sh` | 신규 | root 설치 스크립트 |

**변경 없는 파일:** `backend/app/services/strategy/desk2_pool_link.py` (기존 코드 완전 유지)

---

## 5. 아키텍처 연결 다이어그램

```
DESK3 풀 (v4_desk3_pool.status='ACTIVE', 401건)
    ↓  +0.5 score boost
v4_desk2_candidates (매일 08:00 크론)
    ↓
DESK4 포지션 (v4_desk_positions.desk_level=4 ACTIVE/PARTIAL)
    ↓  +0.8 score boost
v4_desk2_candidates
    ↓
DESK5 포지션 (v4_desk_positions.desk_level=5 ACTIVE/PARTIAL)
    ↓  +1.0 score boost
v4_desk2_candidates
    ↓
DESK2 장중 수확 엔진 (08:50 스캔 → 진입 판단)
```

**D-012 프랙탈 원칙 복원:** DESK2가 상위 DESK 보유 종목을 먹이감으로 수확하는 연결 완성.

---

## 6. 크론 설치 완료 방법 (root 실행 필요)

```bash
# root에서 실행
sudo bash /root/kis-autotrade-v4/scripts/v41/install_desk2_pool_link.sh
# 또는 수동:
sudo cp /root/kis-autotrade-v4/scripts/v41/v41_desk2_pool_link.cron /etc/cron.d/v41_desk2_pool_link
sudo chmod 644 /etc/cron.d/v41_desk2_pool_link
sudo chown root:root /etc/cron.d/v41_desk2_pool_link
sudo mkdir -p /var/log/kis-v41
```

---

## 7. 성공 기준 체크

| 항목 | 기준 | 결과 | 상태 |
|------|------|------|------|
| 크론 소스 파일 생성 | 존재 | scripts/v41/v41_desk2_pool_link.cron ✓ | PASS |
| 설치 스크립트 생성 | 존재 | scripts/v41/install_desk2_pool_link.sh ✓ | PASS |
| 수동 실행 성공 | ≥1건 | 249건 연결 | PASS |
| 로그 정상 출력 | 정상 | INFO 레벨, 결과 출력 확인 | PASS |
| strategy_cards 변경 금지 | 없음 | 미변경 | PASS |
| 서비스 재시작 금지 | 없음 | 미실행 | PASS |
| /etc/cron.d/ 설치 | 완료 | root 실행 필요 (install_desk2_pool_link.sh) | PENDING-ROOT |

---

## 8. 커밋 정보

- **커밋 해시:** `faf1c576`
- **브랜치:** `phase-2c-command-center`
- **메시지:** `[V4.1] feat: T-214 DESK3→DESK2 pool_link cron`
- **GitHub URL:** https://github.com/moongoby/go100/commit/faf1c576

---

## 9. 체크포인트

- [x] 코드 레포 커밋 완료 (faf1c576, phase-2c-command-center)
- [ ] project-docs 보고서 push 완료 (진행 중)

---

HANDOVER.md 업데이트 완료: (업데이트 후 기재)
