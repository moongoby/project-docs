# TASK: 키움 토큰 갱신 크론 07:00 KST 조정 + 키움 수집 크론 크론탭 등록

**작업 완료일**: 2026-05-04  
**HANDOVER 버전**: v11.28+

---

## 작업 개요

키움증권 API 토큰 갱신 시간을 NXT 시장 개시 시간(08:00 KST)에 맞춰 07:00 KST로 앞당기고, 키움 OHLCV/분봉/수급 수집 크론을 크론탭에 등록.

---

## 수정 내용

### 1. 키움 토큰 갱신 크론 정리

**변경 전:**
```
40 8 * * 1-5  /root/kis-autotrade-v4/scripts/cron/refresh_kiwoom_tokens.sh
40 8 * * 1-5  /root/kis-autotrade-v4/scripts/cron/refresh_kiwoom_tokens.sh >> /var/log/go100/kiwoom_token_refresh.log 2>&1
50 7 * * 1-5  /root/kis-autotrade-v4/venv/bin/python /root/kis-autotrade-v4/scripts/refresh_kiwoom_tokens.py >> /root/kis-autotrade-v4/logs/kiwoom_token_refresh.log 2>&1
20 16 * * 1-5  /root/kis-autotrade-v4/scripts/cron/refresh_kiwoom_tokens.sh
```

**변경 후:**
```
0 7 * * 1-5  /root/kis-autotrade-v4/scripts/cron/refresh_kiwoom_tokens.sh >> /var/log/go100/kiwoom_token_refresh.log 2>&1
20 16 * * 1-5  /root/kis-autotrade-v4/scripts/cron/refresh_kiwoom_tokens.sh
```

**변경 사항:**
- 08:40 (40 8) 중복 2개 제거
- 07:50 (50 7)의 Python 스크립트 제거
- 통합 엔트리: **0 7** (07:00 KST 장 시작 1시간 전)
- 로깅 추가: /var/log/go100/kiwoom_token_refresh.log
- 장 후 갱신: **20 16** 유지 (16:20 KST)

### 2. 키움 데이터 수집 크론 등록 (신규)

```
# 키움 일봉 수집 (장 마감 후 16:30)
30 16 * * 1-5  /root/kis-autotrade-v4/scripts/cron/collect_kiwoom_ohlcv.sh >> /var/log/go100/collect_kiwoom_ohlcv.log 2>&1

# 키움 분봉 수집 (장 마감 후 16:40)
40 16 * * 1-5  /root/kis-autotrade-v4/scripts/cron/collect_kiwoom_minute.sh >> /var/log/go100/collect_kiwoom_minute.log 2>&1

# 키움 수급 수집 (장 마감 후 17:00)
0 17 * * 1-5  /root/kis-autotrade-v4/scripts/cron/collect_kiwoom_supply.sh >> /var/log/go100/collect_kiwoom_supply.log 2>&1
```

### 3. 로그 디렉토리 확인

`/var/log/go100/` 디렉토리 존재 확인 ✓

---

## 검증

### 최종 crontab 확인

**키움 토큰 갱신:**
```bash
$ crontab -l | grep "refresh_kiwoom_tokens"
0 7 * * 1-5  /root/kis-autotrade-v4/scripts/cron/refresh_kiwoom_tokens.sh >> /var/log/go100/kiwoom_token_refresh.log 2>&1
20 16 * * 1-5  /root/kis-autotrade-v4/scripts/cron/refresh_kiwoom_tokens.sh
```

**키움 데이터 수집:**
```bash
$ crontab -l | grep "collect_kiwoom"
30 16 * * 1-5  /root/kis-autotrade-v4/scripts/cron/collect_kiwoom_ohlcv.sh >> /var/log/go100/collect_kiwoom_ohlcv.log 2>&1
40 16 * * 1-5  /root/kis-autotrade-v4/scripts/cron/collect_kiwoom_minute.sh >> /var/log/go100/collect_kiwoom_minute.log 2>&1
0 17 * * 1-5  /root/kis-autotrade-v4/scripts/cron/collect_kiwoom_supply.sh >> /var/log/go100/collect_kiwoom_supply.log 2>&1
```

### 체크리스트

- [x] 기존 중복 크론 정리 (08:40 2개 → 제거)
- [x] 토큰 갱신 시간 통합 (50 7 + 40 8 → 0 7)
- [x] 07:00 KST 토큰 갱신 설정 (NXT 08:00 개시 1시간 전)
- [x] 16:20 장 후 갱신 유지
- [x] 키움 OHLCV 수집 16:30 등록
- [x] 키움 분봉 수집 16:40 등록
- [x] 키움 수급 수집 17:00 등록
- [x] /var/log/go100/ 디렉토리 존재 확인
- [x] crontab 설치 완료

---

## 타임라인

| 시간 | 작업 | 상태 |
|------|------|------|
| 07:00 KST | 키움 토큰 갱신 (장 시작 1시간 전) | ✓ 등록 |
| 16:20 KST | 키움 토큰 갱신 (장 후) | ✓ 유지 |
| 16:30 KST | 키움 OHLCV(일봉) 수집 | ✓ 신규 |
| 16:40 KST | 키움 분봉 수집 | ✓ 신규 |
| 17:00 KST | 키움 수급 수집 | ✓ 신규 |

---

## 저장 정보

- **서버 경로**: /root/project-docs/kis-autotrade-v4/reports/KIS-KIWOOM-CRON-SETUP-20260504.md
- **GitHub**: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/KIS-KIWOOM-CRON-SETUP-20260504.md
- **HTTP 확인**: (아래에서 확인)
- **HANDOVER 업데이트**: (다음 단계)
