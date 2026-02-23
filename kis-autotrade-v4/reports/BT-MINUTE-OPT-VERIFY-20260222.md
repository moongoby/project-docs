# BT-MINUTE-OPT-VERIFY 결과 보고 (2026-02-22)

## 사전 확인 (통과)
- strategy_cards: 59
- v4_positions OPEN: 5
- kis-v41-api / monitor / scheduler: active
- 디스크 /: 41% 사용, 56G 여유

## STEP 1: 백테스트 결과 파일
- 분봉 최적화 전용 CSV/리포트: **없음**. 결과는 DB 세션만 존재.
- backtest_results/, results/ 디렉터리 없음.

## STEP 2: DB 세션 결과
- **62** [DB] V2_BT-MIN-DESK2-2M (2025-12-15~2026-02-19): **RUNNING** (미완료)
- **61** [DB] V2_BT-TUNE-DESK2-3M (2025-11-20~2026-02-19): COMPLETED → ROI **+7.48%**, 승률 41.55%, MDD 7.38%, 거래 503건
- **60** [DB] V2_BT-TUNE-DESK3-3M (2025-11-20~2026-02-19): COMPLETED → ROI **+32.23%** (기존 26.92% 대비 상회), 승률/MDD는 summary 미적재

분봉 진입 최적화 전용 완료 세션 없음.

## STEP 3: 로그
- bt_desk3bt_20260221_074243.log: 일봉 시그널 DESK3 백테스트(session_id=38), 분봉 최적화 아님.

## STEP 4: 분봉 데이터
- 행수: 19,179,194
- 범위: 2025-02-18 ~ 2026-02-19

## STEP 5: Git
- 911075f9 DESK2-MINUTE-BT, ab44d85a minute backtest engine, 5516fb64 CUR-BT-OPTIMIZE 등.

## 보고 양식 요약
- 결과 파일 존재: **N**
- DESK2 분봉 ROI: 전용 완료 없음 (TUNE 61: +7.48%)
- DESK3 분봉 ROI: 전용 완료 없음 (TUNE 60: +32.23%, 기존 26.92% 대비 개선)
- 승률: DESK2 41.55%, DESK3 미기재
- MDD: DESK2 7.38%, DESK3 미기재
- 분봉 데이터: 2025-02-18 ~ 2026-02-19, 19,179,194행
- strategy_cards: 59, v4_positions OPEN: 5
- 이슈: 분봉 최적화 전용 완료 결과 없음. 세션 62 RUNNING.

읽기 전용 검증 완료. DB/파일/backtest 수정 없음.
