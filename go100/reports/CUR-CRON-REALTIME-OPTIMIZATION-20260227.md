# CUR-CRON-REALTIME-OPTIMIZATION — 크론 실시간 최적화 수집 전환

- **작성일**: 2026-02-27
- **작업자**: Claude Opus 4.6
- **상태**: 완료

---

## 1. 배경 및 원칙

**원칙**: 데이터 확정 즉시 수집. V4.1 수집 완료 직후 GO100 후처리. 중복 제거. 지연 제로.

기존 크론은 보수적 시각(18:00~19:30)에 데이터를 수집하여 최대 4시간의 불필요한 지연이 있었음.
데이터 소스별 확정 시각을 분석하여 가능한 한 빠르게 수집하도록 전환.

## 2. 블록 0-2: 현황 조사

### 크론 전수 조사
- 기존 활성 엔트리: 45개
- 고아 주석(비활성 설명 라인): ~30줄
- 백업: `/tmp/crontab_backup_pre_redesign_20260227_000932.txt`

### V4.1 수집 소스별 특성

| 스크립트 | 데이터 소스 | 소요시간 | 상태 |
|---------|-----------|---------|------|
| collect_index_daily.sh | pykrx (KRX) | ~3초 | OK (교체 완료) |
| collect_vkospi_alt.py | DATA_GO_KR | ~1초 | OK |
| collect_ohlcv_daily.py | KIS API | 미측정 | OK |
| collect_market_investor.py | KIS API | ~2초 | OK |
| collect_stock_universe.py | KIS API | 미측정 | OK |
| collect_financials.py | KIS API | N/A | **403 에러 (AppKey 무효)** |

### 데이터 확정 시각
- **pykrx**: 장 마감 ~5분 후 (15:35~)
- **DATA_GO_KR**: T-1일 데이터, 시간 무관
- **KIS API**: 장 마감 ~30분 후 (16:00~)
- **Kiwoom**: 기존 16:20~16:50 유지 (이미 최적)

## 3. 블록 3+5+6: 크론 전체 재설계 + 시각 최적화

### 시간 변경 요약 (8개 항목)

| 항목 | 기존 | 최적화 | 단축 | 근거 |
|------|------|--------|------|------|
| index_daily (pykrx) | 18:30 | **15:45** | -2h45m | pykrx 15:35 확정 |
| vkospi_alt (DATA_GO_KR) | 18:30 | **15:50** | -2h40m | T-1일, 즉시 가능 |
| vkospi_regime_sync | 18:40 | **15:55** | -2h45m | VKOSPI 수집 직후 |
| ohlcv_daily (KIS) | 18:00 | **16:00** | -2h | KIS 16:00 확정 |
| market_investor (KIS) | 18:40 | **16:15** | -2h25m | KIS 16:00 확정 |
| stock_universe (KIS) | 19:00 | **16:25** | -2h35m | KIS 16:00 확정 |
| financials (KIS) | 19:30 | **17:30** | -2h | 403 에러 지속 |
| dart_collection | 19:30(월) | **17:30(월)** | -2h | 의존성 없음 |

### 최적화 타임라인 (평일)

```
15:30  장 마감
15:40  [E] 장마감 리포트 + WS 중지
15:45  [E] index_daily (pykrx) ←←← 2h45m 단축
15:50  [E] VKOSPI (DATA_GO_KR) ←←← 2h40m 단축
15:55  [E] VKOSPI 레짐 동기화 ←←← 2h45m 단축
16:00  [F] ohlcv_daily + 분봉 배치 ←←← 2h 단축
16:10  [F] 페이퍼 트레이딩
16:15  [F] market_investor ←←← 2h25m 단축
16:20  [F] Kiwoom 토큰 갱신
16:25  [F] stock_universe ←←← 2h35m 단축
16:30  [F] 프로그램매매 (Kiwoom)
16:35  [F] 체결강도 일별 (Kiwoom)
16:40  [F] 호가창 통계 (GO100)
16:45  [F] 신용잔고/공매도
16:50  [F] 투자자 수급 + 체결 통계
17:00  [G] 테마 수집 + 야간 갭 MV
17:10  [G] 뉴스/공시
17:30  [G] 재무제표 + DART ←←← 2h 단축
      ↑ 모든 수집 17:30 완료 (기존 19:30)
```

**총 단축**: 최대 수집 완료 시각 19:30 → 17:30 (2시간 단축)

### 크론 구조 변경
- 섹션별 주석으로 논리적 그루핑: [A]~[H]
- 고아 주석 30여 줄 제거 → 가독성 향상
- `data_miner.py --refresh-tokens` 라인에서 잘못된 `root` 키워드 제거

## 4. 블록 4: 후처리 스크립트 최적화

### 신규 생성: lib_collect.sh
- 경로: `scripts/go100/lib_collect.sh`
- 제공 함수:
  - `wait_for_table <table> <col> <date> [max_wait] [interval]` — 의존 테이블 데이터 도착 대기
  - `report_elapsed <start_ts> <label>` — 실행 시간 측정
  - `run_with_retry <max> <delay> <cmd...>` — 재시도 실행
  - `today_kst` / `today_kst_dash` — KST 날짜 유틸

### 스크립트 업데이트

| 스크립트 | 변경 내용 |
|---------|----------|
| run_overnight_gap_refresh.sh | ohlcv_daily 의존성 체크 + 소요시간 리포트 |
| run_vkospi_regime_sync.sh | 시각 주석 업데이트 + 소요시간 리포트 |
| run_daily_index_collect.sh | lib_collect 연동 + 소요시간 리포트 |
| collect_index_daily.sh | lib_collect 연동 + 소요시간 리포트 |

## 5. 검증 결과

### 크론 엔트리 대조
- 기존 활성 엔트리: 45개
- 최적화 활성 엔트리: 45개 (**누락 없음**)
- 스크립트 36개 전수 대조: 전체 [OK]

### lib_collect.sh 기능 테스트
- `today_kst`: 20260227 ✓
- `wait_for_table("ohlcv_daily", "date", "20260226")`: rows=3839, 즉시 반환 ✓
- `report_elapsed`: 정확한 초 단위 측정 ✓

### 크론 문법 검증
- `crontab -n` (dry-run): 문법 정상 ✓

## 6. 알려진 이슈

| 이슈 | 상태 | 비고 |
|------|------|------|
| collect_financials.py 403 에러 | **미해결** | KIS AppKey 무효 — 외부 조치 필요 |
| v4_market_regime_daily 02-23 정체 | 알려진 제약 | regime_detector 실행 필요 (V4.1 스케줄러 담당) |
| ohlcv_daily 크론 로그 비어있음 | 관찰 필요 | 16:00으로 이동 후 다음 영업일 확인 |

## 7. 파일 변경 목록

### 신규 생성
- `scripts/go100/lib_collect.sh` — 공통 라이브러리

### 수정
- `scripts/go100/run_overnight_gap_refresh.sh` — 의존성 체크 추가
- `scripts/go100/run_vkospi_regime_sync.sh` — 시각 업데이트
- `scripts/go100/run_daily_index_collect.sh` — lib_collect 연동
- `scripts/collect_index_daily.sh` — lib_collect 연동

### 크론탭
- 적용 완료: 45개 활성 엔트리
- 백업: `/tmp/crontab_backup_pre_redesign_20260227_000932.txt`
