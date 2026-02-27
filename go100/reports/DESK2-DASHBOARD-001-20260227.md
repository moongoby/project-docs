# DESK2-DASHBOARD-001 — DESK2 모니터링 대시보드

**일시:** 2026-02-27  
**작업 ID:** DESK2-DASHBOARD-001 (P1)  
**목적:** DESK2 실시간 모니터링용 정적 대시보드 및 데이터 파이프라인 구축

---

## 1. 요약

- **frontend/static:** `desk2-live.html`, `desk2-live.js`, `desk2-live.css` 신규 생성.
- **데이터 소스:** main.py 수정 없이, `v4_desk2_*` 테이블에서 직접 조회하는 **정적 JSON** 방식.
- **생성 스크립트:** `scripts/desk2_live_data_gen.py` — 배포 시 `DESK2_STATIC_OUT`에 `desk2-live-data.json` 출력.
- **배포:** `bash scripts/deploy_static.sh` 실행 시 desk2-live 파일 복사 + live 데이터 JSON 생성.

---

## 2. 표시 항목 및 데이터 매핑

| 표시 항목 | 데이터 소스 | 주요 필드 |
|-----------|-------------|-----------|
| 오늘의 후보 10종목 | v4_desk2_candidates (target_date=오늘, score_rank 순 상위 10) | 스코어, 순위, 뉴스 수(f1_news_count), 종가위치(f4_close_pos) |
| 실시간 신호 현황 | v4_desk2_signals (signal_date=오늘) | 유형(stock_type), 신호명(signal_name), 시각(signal_time), 가격(signal_price), 상태(status) |
| 보유 포지션 | v4_desk2_trades (exit_time IS NULL) | 진입가, 현재가(—), 수익률(—), 스톱/목표(metadata.stop_loss, metadata.target_price) |
| 오늘 청산 거래 | v4_desk2_trades (trade_date=오늘, exit_time IS NOT NULL) | PnL(net_pnl / net_pnl_pct), 청산사유(exit_reason) |
| 일별 누적 PnL 차트 | v4_desk2_daily_summary → 누적 합산 | trade_date, cumulative_pnl |

- **현재가/수익률:** DB에 실시간 시세가 없어 보유 포지션 영역은 "—" 표시. 추후 실시간 시세 연동 시 확장 가능.

---

## 3. 생성/수정 파일

### 3.1 프론트엔드 (frontend/static)

| 파일 | 설명 |
|------|------|
| desk2-live.html | 대시보드 페이지: 후보 테이블, 신호 테이블, 보유 포지션, 오늘 청산, 일별 누적 PnL 차트 |
| js/desk2-live.js | 데이터 로드(/desk2-live-data.json), 테이블/차트 렌더링, 새로고침 |
| css/desk2-live.css | 다크 테마, 테이블·카드·차트 영역 스타일 |

### 3.2 데이터 생성 스크립트

| 파일 | 설명 |
|------|------|
| scripts/desk2_live_data_gen.py | v4_desk2_candidates, v4_desk2_signals, v4_desk2_trades, v4_desk2_daily_summary 조회 후 `{DESK2_STATIC_OUT}/desk2-live-data.json` 생성 |

### 3.3 배포 스크립트

| 파일 | 변경 내용 |
|------|-----------|
| scripts/deploy_static.sh | desk2-live.html, js/desk2-live.js, css/desk2-live.css 백업/복사 추가; 배포 후 `desk2_live_data_gen.py` 실행하여 desk2-live-data.json 생성; 검증 메시지 추가 |

---

## 4. 데이터 스키마 (desk2-live-data.json)

```json
{
  "generated_at": "ISO8601",
  "target_date": "YYYY-MM-DD",
  "candidates": [
    { "stock_code", "stock_name", "score", "score_rank", "news_count", "close_pos" }
  ],
  "signals": [
    { "stock_code", "stock_type", "signal_name", "signal_time", "signal_price", "status" }
  ],
  "positions": [
    { "id", "trade_date", "stock_code", "signal_name", "entry_time", "entry_price", "quantity", "stop_loss", "target_price" }
  ],
  "closed_today": [
    { "id", "stock_code", "signal_name", "entry_time", "entry_price", "exit_time", "exit_price", "exit_reason", "net_pnl", "net_pnl_pct" }
  ],
  "daily_pnl": [
    { "trade_date", "net_pnl", "cumulative_pnl" }
  ]
}
```

---

## 5. 배포 및 검증

### 5.1 배포

```bash
cd /root/kis-autotrade-v4
bash scripts/deploy_static.sh
```

- 소스: `/root/kis-autotrade-v4/frontend/static`
- 대상: `/var/www/trading.newtalk.kr`
- 배포 후 `desk2_static_data_gen.py`(기존) + `desk2_live_data_gen.py`(신규) 순서 실행.

### 5.2 검증

```bash
# 페이지
curl -s -o /dev/null -w '%{http_code}' https://trading41.newtalk.kr/desk2-live.html

# JSON
curl -s https://trading41.newtalk.kr/desk2-live-data.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('Candidates:', len(d.get('candidates',[])), 'Signals:', len(d.get('signals',[])), 'Positions:', len(d.get('positions',[])))"
```

### 5.3 데이터 갱신

- 배포 시마다 `deploy_static.sh`가 한 번 생성.
- 실시간 갱신이 필요하면 cron으로 주기 실행 예시:

```bash
# 예: 5분마다
*/5 * * * * cd /root/kis-autotrade-v4 && source .venv/bin/activate && DESK2_STATIC_OUT=/var/www/trading.newtalk.kr python3 scripts/desk2_live_data_gen.py
```

---

## 6. project-docs 푸시

본 보고서를 project-docs로 복사 후 푸시:

```bash
cp /root/kis-autotrade-v4/report/v41/DESK2-DASHBOARD-001-20260227.md /root/project-docs/go100/reports/
cd /root/project-docs && git add go100/reports/DESK2-DASHBOARD-001-20260227.md && git commit -m "DESK2-DASHBOARD-001: 모니터링 대시보드 보고서" && git push
```

(실행 환경에서 project-docs 원격 및 권한 확인 후 수행.)

---

## 7. 결론

- DESK2 실시간 모니터링용 정적 대시보드(desk2-live.html)와 정적 JSON 데이터(desk2-live-data.json) 파이프라인을 구축했으며, main.py 수정 없이 배포 스크립트와 별도 스크립트만으로 동작한다.
- 보유 포지션의 현재가/수익률은 추후 실시간 시세 연동 시 확장 가능하다.
