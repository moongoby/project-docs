# CUR-V41-GENSPARK-BRIDGE-STEALTH-001: Genspark 브릿지 Cloudflare 차단 우회 보고서

| 항목 | 내용 |
|------|------|
| 문서 ID | CUR-V41-GENSPARK-BRIDGE-STEALTH-001 |
| 작성일 | 2026-03-02 |
| 프로젝트 | KIS AutoTrade V4.1 |
| 대상 | CEO 통합지휘소 |

---

## 1. 작업 요약

Genspark 브릿지 V1의 Cloudflare 봇 차단 문제를 해결하기 위해 두 가지 방법을 순서대로 시도함.
- 1단계: playwright-stealth (headless) → 세션 인증 실패 (httpOnly 쿠키 미지원)
- 2단계: headed + Xvfb 가상 디스플레이 → **PASS** (13523자 읽기 + 메시지 전송 성공)

---

## 2. 시도 순서 및 결과

| 시도 | 방식 | 결과 | 비고 |
|------|------|------|------|
| 1 | playwright-stealth + headless | FAIL | Cloudflare 통과하나 httpOnly 쿠키 없어 세션 만료 |
| 2 | playwright-stealth + headed + Xvfb | **PASS** | 로그인 후 session.json 저장, 대화창 접속+메시지 전송 성공 |

---

## 3. 구현 상세

### 추가된 기능
- `playwright-stealth 2.0.2` 설치 및 `Stealth().apply_stealth_async(page)` 적용
- `--disable-blink-features=AutomationControlled` 브라우저 args 추가
- `--test-once` 플래그: 1회 폴링 후 종료 (통합 테스트용)
- `genspark_bridge.py`: headless=False + Xvfb 전환
- `/etc/systemd/system/genspark-bridge.service`: ExecStart에 xvfb-run 추가
- `BRIDGE-DESIGN-V1.md`: V1.1 업데이트 (최종 채택 방식 기록)

### 로그인 세션 관리
- 최초 1회: `login.genspark.ai` 직접 접속 → 이메일+비밀번호 자동 입력 → session.json 저장
- 세션 갱신 스크립트: `/tmp/direct_login.py`
- session.json 위치: `/root/.genspark/session.json`

### 통합 테스트 결과
- 로그: `/root/.genspark/logs/integration_test_002.log`
- **결과: PASS** (exit code 0)
  - 대화창 접속 성공: 13523자 읽기
  - 테스트 메시지 `[CURSOR-KIS] headed+Xvfb 테스트 PASS` 전송 완료

---

## 4. systemd 서비스 설정

```ini
ExecStart=/usr/bin/xvfb-run --auto-servernum --server-args="-screen 0 1280x720x24" \
  /root/.genspark/venv/bin/python genspark_bridge.py
```

`systemctl start genspark-bridge` 는 CEO 통합 테스트 확인 후 수동 시작.

---

## 5. 다음 작업

1. CEO가 테스트 결과 확인 후 `systemctl start genspark-bridge` 실행 승인
2. 주기적 session.json 갱신 자동화 (세션 만료 시 자동 재로그인 로직 강화)

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-GENSPARK-BRIDGE-STEALTH-001-20260302.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-GENSPARK-BRIDGE-STEALTH-001-20260302.md
- 커밋: (push 후 갱신)
- HTTP 확인: (push 후 갱신)
- HANDOVER 업데이트: 완료

*Cursor — Genspark 브릿지 Cloudflare 차단 우회 (headed+Xvfb PASS)*
