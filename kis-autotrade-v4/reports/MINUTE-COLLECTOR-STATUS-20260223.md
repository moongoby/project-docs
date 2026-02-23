# MINUTE-COLLECTOR-STATUS 진단 보고서
> 날짜: 2026-02-23
> 작업자: Cursor (읽기 전용 진단, 코드/DB/서비스 변경 없음)

## 서비스 상태
| 서비스 | 상태 | 비고 |
|--------|------|------|
| kis-v41-api | active | |
| kis-v41-monitor | active | |
| kis-v41-scheduler | active | |
| kis-v41-minute-collector | activating | 실패 후 재시작 루프 가능 (journalctl 참고) |
| kis-v41-orderbook-collector | inactive | |

## systemd 유닛 파일
- **kis-v41-minute-collector**: 존재. WorkingDirectory=/root/kis-autotrade-v4, ExecStart=venv/bin/python -m backend.app.services.data_pipeline.collector_minute, Restart=on-failure, RestartSec=60
- **kis-v41-orderbook-collector**: 존재. ExecStart=venv/bin/python scripts/collection/orderbook_collector.py, Restart=on-failure, RestartSec=10 (등록만, 월요일 장전 시작 예정)

## crontab (분봉/호가 관련)
- `0 16 * * 1-5` /root/kis-autotrade-v4/scripts/minute_batch_cron.sh
- `0 2 * * 6` /root/kis-autotrade-v4/scripts/minute_batch_cron.sh  
(실시간 수집기는 systemd 유닛, crontab은 배치용)

## 수집기 소스 코드
| 파일 | 존재 | 비고 |
|------|------|------|
| backend/app/services/data_pipeline/collector_minute.py | 있음 | 25845 bytes, FHKST03010230 분봉 수집 |
| scripts/collection/orderbook_collector.py | 있음 | 10843 bytes, FHKST01010200 호가 수집 |

## 분봉 데이터 (v4_ohlcv_minute)
- **최신 일시**: 2026-02-19 16:00 (trade_date + trade_time)
- **총 행수**: 35,029,032 (문서 기대치 ~19,468,781 대비 증가)
- **종목 수**: 547 (DISTINCT stock_code)
- **종목별 최신 샘플**: 365330 2026-02-19 16:00, 000100/000120/000150/000250 2026-02-19 15:32 등

## 스캘핑 유니버스
- **건수**: 708건
- **샘플**: 496080, 020150(롯데에너지머티리얼즈), 047050(포스코인터내셔널), 091160, 442580 등 (is_active=t)

## 호가 테이블
- orderbook_snapshots
- v4_orderbook_realtime

## 레짐 (v4_market_regime_daily, 최신 5일)
| date       | regime       | regime_score |
|------------|--------------|--------------|
| 2026-02-13 | MILD_TREND_UP| 75.00        |
| 2026-02-12 | MILD_TREND_UP| 75.00        |
| 2026-02-11 | SIDEWAYS     | 41.00        |
| 2026-02-10 | SIDEWAYS     | 42.00        |
| 2026-02-09 | SIDEWAYS     | 42.00        |

## 분봉 수집기 로그 (최근 오류)
- **에러**: `asyncpg.exceptions.UndefinedFunctionError: operator does not exist: boolean = integer` (HINT: explicit type casts 필요)
- **발생 위치**: collector_minute.py `_get_target_stocks()` 내부 SQL (라인 427 근처), `conn.fetch(...)` 호출 시
- **결과**: Main process exited, status=1/FAILURE → Restart=on-failure로 재시작 반복 가능성

## API 로그
- journalctl -u kis-v41-api --since "1 hour ago" 기준: **최근 에러 없음**

## 디스크
- **/root**: 99G 중 51G 사용, 44G 가용, **55% 사용**

---

## DB 무결성 (사전 확인)
| 항목 | 결과 | 기대 |
|------|------|------|
| strategy_cards | 62 | 62 |
| v4_positions OPEN | 5 | 5 |

---

## CEO 승인 필요 사항
- **분봉 수집기 활성화**: `systemctl start kis-v41-minute-collector`  
  → **주의**: 현재 `boolean = integer` 쿼리 오류로 기동 시 실패함. 쿼리 수정(타입 캐스트) 후 활성화 권장.
- **호가 수집기 활성화**: `systemctl start kis-v41-orderbook-collector`
- **활성화 시점**: 월요일 08:50 권장 (코드 수정 없이 호가는 가능; 분봉은 오류 수정 후)

---

## 요약
- 핵심 서비스(api, monitor, scheduler) 정상. DB 무결성 충족.
- 분봉 수집기는 유닛 등록·소스 존재하나, **DB 쿼리 타입 오류**로 기동 실패 중(재시작 루프 가능).
- 호가 수집기는 유닛·소스·테이블 준비됨, inactive 상태 유지(CEO 승인 후 월요일 장전 활성화).
- 보고서 발행: `bash /root/project-docs/scripts/publish_report.sh MINUTE-COLLECTOR-STATUS`  
- 보고서 URL: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/MINUTE-COLLECTOR-STATUS-20260223.md
