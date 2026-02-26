# 디스크 추가 + PostgreSQL DB 이전 확인 보고서

- **일자**: 2026-02-26
- **작업**: 대표님이 200GB 디스크 추가 장착 및 DB 이전 완료 → 확인 검증

---

## 1. 디스크 구성

| 디바이스 | 크기 | 파일시스템 | 마운트 | 용도 | 사용량 |
|----------|------|-----------|--------|------|--------|
| `/dev/vda2` | 100G | ext4 | `/` | OS + 애플리케이션 | **65G / 99G (69%)** |
| `/dev/vdb1` | 200G | ext4 | `/data` | **PostgreSQL DB (신규)** | **14G / 196G (8%)** |

- fstab 등록: `UUID=85c0fff9-f3ba-46d0-bdf1-9587527711aa /data ext4 defaults,noatime 0 2`
- 재부팅 시 자동 마운트 보장됨

---

## 2. PostgreSQL 데이터 디렉토리 이전 확인

| 항목 | 값 |
|------|-----|
| PG 버전 | 16 |
| data_directory | **`/data/postgresql/16/main`** |
| config_file | `/etc/postgresql/16/main/postgresql.conf` (기존 위치) |
| 이전 경로 `/var/lib/postgresql/` | **삭제됨** (정리 완료) |
| postgresql.conf 42행 | `data_directory = '/data/postgresql/16/main'` |

---

## 3. 서비스 상태

| 서비스 | 상태 | 비고 |
|--------|------|------|
| `postgresql@16-main` | **active (running)** | PID 4150151, 메모리 812MB |
| 백엔드 (port 8002) | **정상** | `{"status":"ok","database":"connected","redis":"connected"}` |
| 프론트엔드 (port 3000) | **정상** | HTTP 307 (정상 리다이렉트) |

---

## 4. DB 무결성 점검

| 항목 | 결과 |
|------|------|
| DB 크기 | **14 GB** |
| 테이블 수 | **207개** |
| 활성 종목 (stock_universe) | 3,844개 |
| 뉴스 (go100_news_items) | 288,787건 |
| 분봉 데이터 쿼리 테스트 | 정상 응답 |

### 주요 테이블 크기 (Top 10)

| 테이블 | 크기 |
|--------|------|
| v4_ohlcv_minute_2026_01 | 1,153 MB |
| v4_ohlcv_minute_2025_12 | 1,086 MB |
| v4_ohlcv_minute_2025_07 | 945 MB |
| v4_ohlcv_minute_2025_09 | 935 MB |
| v4_ohlcv_minute_2025_11 | 911 MB |
| ohlcv_1m_history | 893 MB |
| v4_ohlcv_minute_2025_04 | 860 MB |
| v4_ohlcv_minute_2025_08 | 824 MB |
| v4_ohlcv_minute_2025_03 | 806 MB |
| v4_ohlcv_minute_2026_02 | 806 MB |

---

## 5. 용량 이점

| 비교 | 이전 (vda) | 이후 (vdb) |
|------|-----------|-----------|
| DB 전용 디스크 크기 | 99G (OS와 공유) | **196G (전용)** |
| DB 사용 후 여유 | ~30G (위험) | **172G (여유)** |
| noatime 옵션 | 미적용 | **적용** (I/O 최적화) |

기존 `/` 파티션에서 14GB DB가 분리되어 OS 디스크 여유분도 확보됨.

---

## 6. 결론

모든 항목 **정상 확인**. 디스크 추가 + DB 이전이 깔끔하게 완료된 상태입니다.

- fstab 영구 마운트 설정됨
- PG data_directory가 `/data/postgresql/16/main`으로 올바르게 변경됨
- 구 경로 `/var/lib/postgresql/` 정리 완료
- 전체 서비스 (PG, 백엔드, 프론트엔드) 정상 가동 중
- 신규 디스크 여유: **172GB** (현 DB 14GB 대비 충분)

---

*Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>*
