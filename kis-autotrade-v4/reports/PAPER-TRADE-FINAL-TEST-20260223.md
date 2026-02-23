# PAPER-TRADE-FINAL-TEST 결과 보고서

- **작업 ID**: PAPER-TRADE-FINAL-TEST
- **일시**: 2026-02-23 15:30+ KST (장마감 후)
- **서버**: root@211.188.51.113
- **브랜치**: phase-2c-command-center
- **우선순위**: P0

---

## 절대 규칙 준수

| 항목 | 준수 |
|------|------|
| strategy_cards ALTER/DROP/DELETE | ✅ 없음 |
| v4_positions 직접 수정 | ✅ 없음 (OPEN 5건 유지: 49, 51, 53, 55, 61) |
| .env/.bak 커밋 | ✅ 없음 |
| 모의계좌(openapivts)만 사용 | ✅ CONFIG_ID=1(5016***), openapivts |
| kis-v41-monitor, kis-v41-scheduler 재시작 | ✅ 금지 준수 |
| 보고서 시크릿 마스킹 | ✅ 적용 |

---

## Phase A — API 재시작

| 단계 | 결과 |
|------|------|
| systemctl restart kis-v41-api | ✅ 완료 |
| systemctl status kis-v41-api | ✅ active (running) |
| curl localhost:8003/health | ✅ status=ok, database=connected, redis=connected |

---

## Phase B — 잔고 확인

| 항목 | 결과 |
|------|------|
| 스크립트 | `CONFIG_ID=1 python3 scripts/diagnose_balance_config3.py` |
| 예수금(d2_deposit) | **466,347,229원** (기대치와 일치) |
| 보유 종목 수 | **7종목** (기대치와 일치) |
| API 로그 | openapivts 잔고 조회 HTTP 200 OK 확인 |

---

## Phase C — DESK3 매매 사이클

| 항목 | 결과 |
|------|------|
| 요청 | `POST /api/v4/trading/desk3/cycle?dry_run=false` (X-Internal-API-Key: ***) |
| HTTP 응답 | **200 OK** |
| 응답 body | ok=true, dry_run=false, picks=5, signals=5(BUY), orders=[] |

**로그 요약**

- DESK3 장전 분석: CLASS-D 5종목(지누스, 아가방컴퍼니, 화승인더, 비비안, 경인전자), CLASS-K 75종목.
- **PRE_ORDER_CHECK**: 5건 모두 매수 거부 — **가용=0, 사유=잔액 부족**. (필요 금액은 7.8M~9.7M 수준.)
- **원인**: 사이클 중 `[V4] 토큰 재발급 config_id=1 모의` 후 **재시도 3회 초과** 로그 다수. 토큰 갱신 실패로 잔고 조회 시 가용금이 0으로 인식된 것으로 추정.
- 주문 전송: 로그에 `order-cash` POST openapivts 200 OK 1건 기록됨(기존 플로우 또는 재시도로 추정). 본 사이클에서 생성된 신규 주문은 0건.

**성공 기준 대비**

- PRE_ORDER_CHECK usable > 0: ❌ (가용=0)
- v4_order_requests 신규 행: ❌ 0건
- v4_positions 신규 OPEN: ❌ 0건
- openapivts 주문 200 OK: ⚠️ 1건 로그 있으나 본 회차 신규 매수 주문과 직접 대응되지 않음

---

## Phase D — 결과 확인

| 쿼리 | 결과 |
|------|------|
| v4_positions 최근 10건 | id 61(360140, desk4) ~ 52(003530, desk2) 조회됨 |
| v4_order_requests (최근 15분) | **0건** (신규 없음) |
| strategy_cards COUNT | **65** |
| v4_positions WHERE status='OPEN' | **5건** (id: 49, 51, 53, 55, 61) |

**OPEN 포지션 목록 (무결성 유지)**

| id | ticker | desk_id |
|----|--------|--------|
| 49 | 221800 | 1 |
| 51 | 001510 | 2 |
| 53 | 001290 | 2 |
| 55 | 373110 | 3 |
| 61 | 360140 | 4 |

---

## Phase E — 보고서 발행

- 보고서 경로: `/root/kis-autotrade-v4/report/v41/PAPER-TRADE-FINAL-TEST-20260223.md`
- 발행: `bash /root/project-docs/scripts/publish_report.sh PAPER-TRADE-FINAL-TEST`
- 동기화: `bash /root/project-docs/scripts/sync_kis.sh`

---

## Phase F — 완료 요약

| 항목 | 값 |
|------|-----|
| DB 무결성 | strategy_cards=**65**, v4_positions OPEN=**5** |
| 매매 사이클 | HTTP 200·신호 5건 생성, **실제 주문 0건** (PRE_ORDER 가용=0 거부) |
| 신규 주문/포지션 | 0건 / 0건 |
| Git URL | https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/PAPER-TRADE-FINAL-TEST-20260223.md |

**권장 후속**

1. **토큰 재발급**: config_id=1 모의 계좌 토큰 재발급 3회 초과 원인 조사(API 제한, 인증 정보 유효성, 네트워크 등).
2. **PRE_ORDER 가용금**: 사이클 내 잔고 조회가 토큰 실패로 0원으로 나오는 구간 수정 또는 재시도/폴백 정책 검토.
3. **재테스트**: 토큰/잔고 경로 정상화 후 동일 절차로 DESK3 사이클 재실행 권장.

---

*PAPER-TRADE-FINAL-TEST 실행 구간 반영. 시크릿 마스킹 적용.*
