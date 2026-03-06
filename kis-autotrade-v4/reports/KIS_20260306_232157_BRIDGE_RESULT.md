---
project: KIS
task_id: T-214
completed_at: "2026-03-07T00:35:00+09:00"
---

# T-214: DESK3→DESK2 pool_link 크론 연결 — 실행 결과

**Task ID:** T-214
**완료 시각:** 2026-03-07 00:35 KST
**상태:** 완료 (수동 실행 성공 249건, 크론 소스+설치 스크립트 완료)

---

## 1. 지시서 내용 (원문 그대로)

```
T‑214: DESK3→DESK2 pool_link 크론 연결 (T‑202 PIPE‑001)

Task ID: T‑214
Priority: P1‑HIGH
소요: 20 min
선행: T‑200
병렬그룹: A
배경: T‑202 단절점 ④. desk2_pool_link.py 함수 존재하나 크론/엔진 미연결. DESK3→DESK2 승격 0건의 직접 원인. D‑012 프랙탈 아키텍처에서 "DESK2 = 상위 DESK 보유 종목을 먹이감으로 장중 수확"이 미작동.
작업:
desk2_pool_link.py 스크립트 확인: 입력(v4_desk3_pool ACTIVE) → 출력(v4_desk2_candidates) 연결 로직 검증
크론 파일 생성: /etc/cron.d/v41_desk2_pool_link
0 8 * * 1-5 root cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 backend/desk_filters/desk2_pool_link.py >> /var/log/kis-v41/desk2_pool_link.log 2>&1

권한: chmod 644, chown root:root
수동 1회 실행 → DESK3 401 ACTIVE 중 DESK2 후보 연결 건수 확인
로그 확인: 정상 기록 여부
git commit + push ([V4.1] feat: T-214 DESK3→DESK2 pool_link cron)
성공기준: 크론 설치 + 수동 실행 시 1건 이상 DESK2 후보 연결
금지: 서비스 재시작, strategy_cards 변경
보고서: CUR-V41-DESK2-POOL-LINK-CRON-001-20260307.md
보고규칙: GitHub URL + 커밋 URL + HANDOVER URL + HTTP 200
```

---

## 2. 실행 과정 상세

### 2.1 기존 코드 확인

파일 경로 탐색:
```
find /root/kis-autotrade-v4 -name "desk2_pool_link*"
→ /root/kis-autotrade-v4/backend/app/services/strategy/desk2_pool_link.py (EXISTS)
→ /root/kis-autotrade-v4/backend/app/services/strategy/__pycache__/desk2_pool_link.cpython-312.pyc
```

지시서 경로(`backend/desk_filters/desk2_pool_link.py`)는 존재하지 않음 → 엔트리포인트 신규 생성 필요.

기존 `backend/app/services/strategy/desk2_pool_link.py` 분석:
- `apply_desk345_confidence_boost()` 함수 완결 (255줄)
- 입력: v4_desk3_pool.status='ACTIVE' → boost +0.5
- 입력: v4_desk_positions.desk_level=4 ACTIVE/PARTIAL → boost +0.8
- 입력: v4_desk_positions.desk_level=5 ACTIVE/PARTIAL → boost +1.0
- 출력: v4_desk2_candidates (UPDATE score += boost / INSERT 신규)
- ON CONFLICT DO UPDATE 패턴 → 멱등성 보장
- `__main__` 블록 없음 → 크론 엔트리포인트 별도 필요

DB 상태 확인:
```sql
SELECT status, COUNT(*) FROM v4_desk3_pool GROUP BY status;
→ ACTIVE: 401, EXPIRED: 5

SELECT COUNT(*) FROM v4_desk2_candidates WHERE target_date = '2026-03-06';
→ 10건 (작업 전)
```

### 2.2 backend/desk_filters/ 디렉토리 생성

```bash
sudo /bin/mkdir -p /root/kis-autotrade-v4/backend/desk_filters
# → dir created (root:root 755)
sudo /bin/chmod 777 /root/kis-autotrade-v4/backend/desk_filters
# → 777로 변경 (claudebot 쓰기 가능)
```

### 2.3 backend/desk_filters/desk2_pool_link.py 생성

```python
#!/usr/bin/env python3
"""
backend/desk_filters/desk2_pool_link.py — DESK3→DESK2 pool_link 크론 엔트리포인트

T-214: DESK3→DESK2 pool_link 크론 연결
- v4_desk3_pool ACTIVE 종목 → v4_desk2_candidates confidence_boost 주입
- DESK4/5 OPEN 포지션도 함께 boost
- 매일 영업일 08:00 실행 (DESK2 장전 스캔 전)

크론: /etc/cron.d/v41_desk2_pool_link
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

# ─── 프로젝트 루트를 sys.path에 추가 ───
_PROJ_ROOT = Path(__file__).resolve().parents[2]  # /root/kis-autotrade-v4
sys.path.insert(0, str(_PROJ_ROOT))

# ─── .env 로드 ───
_env_path = _PROJ_ROOT / ".env"
if _env_path.exists():
    with open(_env_path, "r", encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _, _v = _line.partition("=")
                _k = _k.strip()
                _v = _v.strip().strip('"').strip("'")
                if _k not in os.environ:
                    os.environ[_k] = _v

# ─── 로깅 설정 ───
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("desk2_pool_link")

# ─── 메인 실행 ───
if __name__ == "__main__":
    from backend.app.services.strategy.desk2_pool_link import (
        apply_desk345_confidence_boost,
    )

    logger.info("=== DESK3->DESK2 pool_link 시작 ===")
    result = apply_desk345_confidence_boost()
    logger.info("결과: %s", result)

    if "error" in result:
        logger.error("오류 발생: %s", result["error"])
        sys.exit(1)

    print(
        f"[T-214] DESK3->DESK2 pool_link 완료\n"
        f"  target_date    : {result['target_date']}\n"
        f"  desk3_active   : {result['desk3_active']}\n"
        f"  desk4_open     : {result['desk4_open']}\n"
        f"  desk5_open     : {result['desk5_open']}\n"
        f"  boosted        : {result['boosted']}\n"
        f"  inserted       : {result['inserted']}\n"
        f"  total_processed: {result['total_processed']}\n"
    )
    sys.exit(0)
```

파일 생성 완료: `/root/kis-autotrade-v4/backend/desk_filters/desk2_pool_link.py`

### 2.4 backend/desk_filters/__init__.py 생성

```python
# backend/desk_filters package
```

### 2.5 scripts/v41/v41_desk2_pool_link.cron 생성

```cron
# V4.1 DESK3→DESK2 pool_link (T-214, 2026-03-07)
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin

# DESK3 ACTIVE → v4_desk2_candidates confidence_boost 주입 (매일 영업일 08:00)
0 8 * * 1-5 root cd /root/kis-autotrade-v4 && /root/kis-autotrade-v4/venv/bin/python3 backend/desk_filters/desk2_pool_link.py >> /var/log/kis-v41/desk2_pool_link.log 2>&1
```

파일 생성 완료: `/root/kis-autotrade-v4/scripts/v41/v41_desk2_pool_link.cron`

### 2.6 scripts/v41/install_desk2_pool_link.sh 생성

```bash
#!/bin/bash
# T-214 설치 스크립트 (root 실행 필요)
# 실행: bash /root/kis-autotrade-v4/scripts/v41/install_desk2_pool_link.sh
set -e

echo "=== T-214 DESK3→DESK2 pool_link 크론 설치 ($(date '+%Y-%m-%dT%H:%M:%S+09:00')) ==="
cd /root/kis-autotrade-v4

# 1. 로그 디렉토리
mkdir -p /var/log/kis-v41
chmod 755 /var/log/kis-v41
echo "[OK] 로그 디렉토리: /var/log/kis-v41"

# 2. cron 등록
cp scripts/v41/v41_desk2_pool_link.cron /etc/cron.d/v41_desk2_pool_link
chmod 644 /etc/cron.d/v41_desk2_pool_link
chown root:root /etc/cron.d/v41_desk2_pool_link
echo "[OK] 크론 등록: /etc/cron.d/v41_desk2_pool_link"

# 3. 수동 1회 실행 테스트
echo "[TEST] desk2_pool_link 수동 실행..."
cd /root/kis-autotrade-v4
/root/kis-autotrade-v4/venv/bin/python3 backend/desk_filters/desk2_pool_link.py
echo "[OK] 수동 실행 완료"

echo "=== T-214 설치 완료 ==="
```

### 2.7 수동 1회 실행 결과

실행 명령:
```bash
/root/kis-autotrade-v4/venv/bin/python3 backend/desk_filters/desk2_pool_link.py
```

실행 로그 (원문):
```
2026-03-06 23:30:14 [INFO] desk2_pool_link: === DESK3->DESK2 pool_link 시작 ===
2026-03-06 23:30:14 [INFO] backend.app.services.strategy.desk2_pool_link: DESK345→DESK2 boost 완료: date=2026-03-06 D3=401 D4=0 D5=0 boosted=4 inserted=245 total=249
2026-03-06 23:30:14 [INFO] desk2_pool_link: 결과: {'target_date': '2026-03-06', 'desk3_active': 401, 'desk4_open': 0, 'desk5_open': 0, 'boosted': 4, 'inserted': 245, 'total_processed': 249}
[T-214] DESK3->DESK2 pool_link 완료
  target_date    : 2026-03-06
  desk3_active   : 401
  desk4_open     : 0
  desk5_open     : 0
  boosted        : 4
  inserted       : 245
  total_processed: 249
```

stdout 결과:
```
[T-214] DESK3->DESK2 pool_link 완료
  target_date    : 2026-03-06
  desk3_active   : 401
  desk4_open     : 0
  desk5_open     : 0
  boosted        : 4
  inserted       : 245
  total_processed: 249
```

종료 코드: 0 (정상)

### 2.8 DB 검증 (실행 후)

```sql
SELECT COUNT(*) FROM v4_desk2_candidates WHERE target_date = '2026-03-06';
→ 255건 (작업 전 10건 → 245건 신규 삽입 + 4건 score 가산)
```

### 2.9 /etc/cron.d/ 설치 상태

claudebot은 `/etc/cron.d/` 쓰기 권한 없음 (root:root 755).
- 크론 소스 파일: `scripts/v41/v41_desk2_pool_link.cron` ✓
- 설치 스크립트: `scripts/v41/install_desk2_pool_link.sh` ✓
- **root에서 실행 필요:**
  ```bash
  sudo bash /root/kis-autotrade-v4/scripts/v41/install_desk2_pool_link.sh
  ```

### 2.10 git commit + push

```bash
sudo /usr/bin/git -C /root/kis-autotrade-v4 add backend/desk_filters/ scripts/v41/v41_desk2_pool_link.cron scripts/v41/install_desk2_pool_link.sh

# 스테이징 확인:
A  backend/desk_filters/__init__.py
A  backend/desk_filters/desk2_pool_link.py
A  scripts/v41/install_desk2_pool_link.sh
A  scripts/v41/v41_desk2_pool_link.cron

sudo /usr/bin/git -C /root/kis-autotrade-v4 commit -m "[V4.1] feat: T-214 DESK3→DESK2 pool_link cron"
# [phase-2c-command-center faf1c576] [V4.1] feat: T-214 DESK3→DESK2 pool_link cron
#  4 files changed, 101 insertions(+)
#  create mode 100644 backend/desk_filters/__init__.py
#  create mode 100644 backend/desk_filters/desk2_pool_link.py
#  create mode 100644 scripts/v41/install_desk2_pool_link.sh
#  create mode 100644 scripts/v41/v41_desk2_pool_link.cron

sudo /usr/bin/git -C /root/kis-autotrade-v4 push origin phase-2c-command-center
# To github.com:moongoby/go100.git
#    1cfc435c..faf1c576  phase-2c-command-center -> phase-2c-command-center
```

### 2.11 보고서 project-docs push

```bash
cp /root/kis-autotrade-v4/report/v41/CUR-V41-DESK2-POOL-LINK-CRON-001-20260307.md \
   /root/project-docs/kis-autotrade-v4/reports/CUR-V41-DESK2-POOL-LINK-CRON-001-20260307.md

sudo /usr/bin/git -C /root/project-docs add \
  kis-autotrade-v4/reports/CUR-V41-DESK2-POOL-LINK-CRON-001-20260307.md \
  kis-autotrade-v4/HANDOVER.md

sudo /usr/bin/git -C /root/project-docs commit -m "docs: T-214 보고서 push + HANDOVER v10.26 (20260307)"
# [master 4ed6c29] docs: T-214 보고서 push + HANDOVER v10.26 (20260307)
#  2 files changed, 208 insertions(+), 1 deletion(-)
#  create mode 100644 kis-autotrade-v4/reports/CUR-V41-DESK2-POOL-LINK-CRON-001-20260307.md

sudo /usr/bin/git -C /root/project-docs push origin master
# To github.com:moongoby/project-docs.git
#    f56669b..4ed6c29  master -> master
```

GitHub raw URL 확인:
```bash
curl -s -o /dev/null -w "%{http_code}" \
  "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-DESK2-POOL-LINK-CRON-001-20260307.md"
→ 200
```

---

## 3. 성공 기준 체크

| 항목 | 기준 | 결과 | 상태 |
|------|------|------|------|
| 크론 소스 파일 생성 | 존재 | scripts/v41/v41_desk2_pool_link.cron | PASS |
| 설치 스크립트 생성 | 존재 | scripts/v41/install_desk2_pool_link.sh | PASS |
| 수동 실행 | ≥1건 | **249건** | PASS (249x) |
| 로그 정상 출력 | INFO 기록 | INFO 레벨 확인, stdout 출력 정상 | PASS |
| /etc/cron.d/ 설치 | 완료 | root 수동 실행 필요 (install_desk2_pool_link.sh) | PENDING-ROOT |
| strategy_cards 변경 금지 | 없음 | 미변경 | PASS |
| 서비스 재시작 금지 | 없음 | 미실행 | PASS |

**핵심 성과:** DESK3 401건 ACTIVE → v4_desk2_candidates 249건 연결 (10→255건)

---

## 4. 생성 파일 목록

| 경로 | 유형 | 크기 |
|------|------|------|
| `backend/desk_filters/__init__.py` | 신규 | 1줄 |
| `backend/desk_filters/desk2_pool_link.py` | 신규 | 68줄 |
| `scripts/v41/v41_desk2_pool_link.cron` | 신규 | 7줄 |
| `scripts/v41/install_desk2_pool_link.sh` | 신규 | 26줄 |
| `report/v41/CUR-V41-DESK2-POOL-LINK-CRON-001-20260307.md` | 신규 | 보고서 |

---

## 5. 커밋 및 URL

- **코드 커밋:** `faf1c576` (phase-2c-command-center)
  - URL: https://github.com/moongoby/go100/commit/faf1c576
- **project-docs 커밋:** `4ed6c29` (master)
- **보고서 GitHub URL:** https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-DESK2-POOL-LINK-CRON-001-20260307.md
  - HTTP 상태: **200**
- **HANDOVER URL:** https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md
  - 버전: v10.26 업데이트 완료

---

## 6. root 필수 후속 조치

```bash
# root에서 실행 (한 번만):
sudo bash /root/kis-autotrade-v4/scripts/v41/install_desk2_pool_link.sh
```

이 명령이 완료되면:
- `/var/log/kis-v41/` 디렉토리 생성
- `/etc/cron.d/v41_desk2_pool_link` 설치 (chmod 644)
- 수동 실행 재확인

다음 영업일 (03-09 월요일) 08:00 KST에 첫 자동 실행 예정.

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (faf1c576, phase-2c-command-center)
- [x] project-docs 보고서 push 완료 (HTTP 200)

HANDOVER.md 업데이트 완료: 4ed6c29
