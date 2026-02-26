# 최근 3개월 분봉 우선 수집 적용 보고

**작성일**: 2026-02-24

## 1. 요청

- **요청**: 최근 3개월 분봉 우선 수집

## 2. 적용 내용

### 2.1 분봉 수집기 코드 변경

**파일**: `backend/app/services/data_pipeline/collector_minute.py`

- **`run()` 인자 추가**: `oldest_first: bool = False`
  - `True`이면 거래일 목록을 **과거 → 최근** 순으로 정렬하여, 가장 오래된 일자부터 전 종목 수집 후 다음 일자로 진행.
- **CLI 옵션 추가**: `--oldest-first`
  - 예: `python -m backend.app.services.data_pipeline.collector_minute --days 66 --oldest-first`

### 2.2 systemd 서비스 오버라이드

**경로**: `/etc/systemd/system/kis-v41-minute-collector.service.d/override.conf`

- **변경 전**: `collector_minute` (기본 240거래일, 최신일 우선)
- **변경 후**: `collector_minute --days 66 --oldest-first`
  - **66거래일**: 약 3개월 분량만 대상
  - **과거우선**: 3개월 전 일자부터 채운 뒤 최근으로 진행

### 2.3 서비스 재시작

- `systemctl daemon-reload` 후 `systemctl restart kis-v41-minute-collector` 실행
- 상태: **active (running)**

## 3. 동작 확인 (로그)

```
실전계좌: 2개, 종목: 500개, 거래일: 66일, 과거우선: True
수집 순서: 과거 일자 우선 (최근 66거래일 백필)
대상 종목: 500개, 거래일: 66일
```

- 수집 순서: **과거 일자 우선**으로 최근 66거래일 백필 진행 중.

## 4. 참고

- **기본 동작 복원**: 오버라이드 삭제 후 `systemctl daemon-reload && systemctl restart kis-v41-minute-collector` 하면 기존처럼 240일·최신일 우선으로 동작.
- **수동 실행 예** (3개월 과거우선):  
  `cd /root/kis-autotrade-v4 && .venv/bin/python -m backend.app.services.data_pipeline.collector_minute --days 66 --oldest-first`
