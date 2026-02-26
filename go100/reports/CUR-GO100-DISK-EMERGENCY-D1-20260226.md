# CUR-GO100-DISK-EMERGENCY-D1

## 디스크 긴급 대응

**날짜**: 2026-02-26
**상태**: 완료

---

## 작업 요약

디스크 사용률 88% → 87%로 정리 수행. 7일 초과 백업 없음, legacy 테이블 삭제 및 자동 정리 크론 등록 완료.

## 수행 내역

### 1. 7일 초과 백업 삭제
- 삭제 전: /root/backup 약 33GB
- 삭제 대상: 7일 초과 백업 없음 (dry-run 결과 0건)
- 삭제 후: 33GB 유지

### 2. _legacy_ 테이블 삭제
- 삭제 전: 약 653MB (2개 테이블)
  - _legacy_ohlcv_1m_history_20260220: 361MB
  - _legacy_market_data_min_20260220: 292MB
- 삭제 후: DROP CASCADE 실행, vacuumdb --all --analyze 수행

### 3. 자동 정리 크론 등록
- 매일 04:00: 7일 초과 백업 자동 삭제
- 매주 일 03:30: systemd 저널 3일 유지
- 매주 일 03:45: npm 캐시 정리

### 4. /tmp 정리
- 7일 초과 임시파일 삭제 수행

## 결과
- 정리 전: 88% (83GB/99GB)
- 정리 후: 87% (82GB/99GB)
- 회수 용량: 약 1GB (legacy 테이블 DROP + VACUUM)

---

*Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>*
